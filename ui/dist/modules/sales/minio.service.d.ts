import { OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Client } from 'minio';
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
export declare class MinioService implements OnModuleInit {
    private configService;
    private client;
    private defaultBucket;
    constructor(configService: ConfigService);
    onModuleInit(): Promise<void>;
    private ensureDefaultBucket;
    listBuckets(): Promise<MinioBucket[]>;
    createBucket(bucketName: string, region?: string): Promise<void>;
    deleteBucket(bucketName: string): Promise<void>;
    bucketExists(bucketName: string): Promise<boolean>;
    listObjects(bucketName: string, prefix?: string, recursive?: boolean): Promise<MinioObject[]>;
    getObject(bucketName: string, objectName: string): Promise<Readable>;
    getObjectStat(bucketName: string, objectName: string): Promise<import("minio").BucketItemStat>;
    putObject(bucketName: string, objectName: string, stream: Readable | Buffer, size: number, metaData?: Record<string, string>): Promise<string>;
    uploadFile(bucketName: string, objectName: string, filePath: string, metaData?: Record<string, string>): Promise<string>;
    downloadFile(bucketName: string, objectName: string, filePath: string): Promise<void>;
    deleteObject(bucketName: string, objectName: string): Promise<void>;
    deleteObjects(bucketName: string, objectNames: string[]): Promise<void>;
    copyObject(sourceBucket: string, sourceObject: string, destBucket: string, destObject: string): Promise<void>;
    presignedGetObject(bucketName: string, objectName: string, expiry?: number): Promise<string>;
    presignedPutObject(bucketName: string, objectName: string, expiry?: number): Promise<string>;
    presignedUrl(bucketName: string, objectName: string, options?: PresignedUrlOptions): Promise<string>;
    setBucketPolicy(bucketName: string, policy: 'public' | 'private' | 'readonly'): Promise<void>;
    getBucketPolicy(bucketName: string): Promise<string>;
    healthCheck(): Promise<boolean>;
    getClient(): Client;
}
