import { Injectable, OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Client, BucketItem, PolicyType } from 'minio';
import { Readable } from 'stream';

export interface MinioBucket {
  name: string;
  creationDate: Date;
}

export interface MinioObject {
  name: string;
  size: number;
  etag: string;
  lastModified: Date;
  contentType: string;
}

export interface PresignedUrlOptions {
  expiry?: number;
  method?: 'GET' | 'PUT' | 'POST' | 'DELETE';
}

@Injectable()
export class MinioService implements OnModuleInit {
  private client: Client;
  private defaultBucket: string;

  constructor(private configService: ConfigService) {
    this.client = new Client({
      endPoint: this.configService.get('MINIO_ENDPOINT') || 'localhost',
      port: parseInt(this.configService.get('MINIO_PORT') || '9000', 10),
      useSSL: this.configService.get('MINIO_USE_SSL') === 'true',
      accessKey: this.configService.get('MINIO_ACCESS_KEY') || 'minio',
      secretKey: this.configService.get('MINIO_SECRET_KEY') || 'minio123456',
      region: this.configService.get('MINIO_REGION') || 'us-east-1',
    });

    this.defaultBucket = this.configService.get('MINIO_DEFAULT_BUCKET') || 'data-lake';
  }

  async onModuleInit() {
    await this.ensureDefaultBucket();
  }

  private async ensureDefaultBucket(): Promise<void> {
    const exists = await this.client.bucketExists(this.defaultBucket);
    if (!exists) {
      await this.client.makeBucket(this.defaultBucket, 'us-east-1');
      // Set bucket policy for public read if needed
      // await this.client.setBucketPolicy(this.defaultBucket, 'public', PolicyType.READ_ONLY);
    }
  }

  // Bucket operations
  async listBuckets(): Promise<MinioBucket[]> {
    const buckets = await this.client.listBuckets();
    return buckets.map(b => ({
      name: b.name,
      creationDate: b.creationDate,
    }));
  }

  async createBucket(bucketName: string, region = 'us-east-1'): Promise<void> {
    const exists = await this.client.bucketExists(bucketName);
    if (!exists) {
      await this.client.makeBucket(bucketName, region);
    }
  }

  async deleteBucket(bucketName: string): Promise<void> {
    await this.client.removeBucket(bucketName);
  }

  async bucketExists(bucketName: string): Promise<boolean> {
    return this.client.bucketExists(bucketName);
  }

  // Object operations
  async listObjects(
    bucketName: string,
    prefix = '',
    recursive = true,
  ): Promise<MinioObject[]> {
    const objects: MinioObject[] = [];
    const stream = this.client.listObjects(bucketName, prefix, recursive);

    for await (const obj of stream) {
      objects.push({
        name: obj.name || '',
        size: obj.size || 0,
        etag: obj.etag || '',
        lastModified: obj.lastModified || new Date(),
        contentType: obj.metaData?.['content-type'] || 'application/octet-stream',
      });
    }

    return objects;
  }

  async getObject(bucketName: string, objectName: string): Promise<Readable> {
    return this.client.getObject(bucketName, objectName);
  }

  async getObjectStat(bucketName: string, objectName: string) {
    return this.client.statObject(bucketName, objectName);
  }

  async putObject(
    bucketName: string,
    objectName: string,
    stream: Readable | Buffer,
    size: number,
    metaData?: Record<string, string>,
  ): Promise<string> {
    const etag = await this.client.putObject(bucketName, objectName, stream, size, metaData);
    return etag;
  }

  async uploadFile(
    bucketName: string,
    objectName: string,
    filePath: string,
    metaData?: Record<string, string>,
  ): Promise<string> {
    const etag = await this.client.fPutObject(bucketName, objectName, filePath, metaData);
    return etag;
  }

  async downloadFile(
    bucketName: string,
    objectName: string,
    filePath: string,
  ): Promise<void> {
    await this.client.fGetObject(bucketName, objectName, filePath);
  }

  async deleteObject(bucketName: string, objectName: string): Promise<void> {
    await this.client.removeObject(bucketName, objectName);
  }

  async deleteObjects(bucketName: string, objectNames: string[]): Promise<void> {
    await this.client.removeObjects(bucketName, objectNames);
  }

  async copyObject(
    sourceBucket: string,
    sourceObject: string,
    destBucket: string,
    destObject: string,
  ): Promise<void> {
    await this.client.copyObject(
      destBucket,
      destObject,
      `/${sourceBucket}/${sourceObject}`,
    );
  }

  // Presigned URLs
  async presignedGetObject(
    bucketName: string,
    objectName: string,
    expiry = 24 * 60 * 60,
  ): Promise<string> {
    return this.client.presignedGetObject(bucketName, objectName, expiry);
  }

  async presignedPutObject(
    bucketName: string,
    objectName: string,
    expiry = 24 * 60 * 60,
  ): Promise<string> {
    return this.client.presignedPutObject(bucketName, objectName, expiry);
  }

  async presignedUrl(
    bucketName: string,
    objectName: string,
    options: PresignedUrlOptions = {},
  ): Promise<string> {
    const { expiry = 24 * 60 * 60, method = 'GET' } = options;
    switch (method) {
      case 'GET':
        return this.client.presignedGetObject(bucketName, objectName, expiry);
      case 'PUT':
        return this.client.presignedPutObject(bucketName, objectName, expiry);
      case 'POST':
        const policy = this.client.newPostPolicy();
        policy.setBucket(bucketName);
        policy.setKey(objectName);
        policy.setExpires(expiry);
        const { postURL, formData } = await this.client.presignedPostPolicy(policy);
        return JSON.stringify({ url: postURL, formData });
      default:
        throw new Error(`Unsupported method: ${method}`);
    }
  }

  // Bucket policies
  async setBucketPolicy(
    bucketName: string,
    policy: 'public' | 'private' | 'readonly',
  ): Promise<void> {
    const policyType = policy === 'public' ? PolicyType.READ_WRITE : 
                       policy === 'readonly' ? PolicyType.READ_ONLY : 
                       PolicyType.NONE;
    await this.client.setBucketPolicy(bucketName, '', policyType);
  }

  async getBucketPolicy(bucketName: string): Promise<string> {
    return this.client.getBucketPolicy(bucketName);
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      await this.client.listBuckets();
      return true;
    } catch {
      return false;
    }
  }

  getClient(): Client {
    return this.client;
  }
}