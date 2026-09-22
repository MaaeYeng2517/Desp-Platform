"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.MinioService = void 0;
const common_1 = require("@nestjs/common");
const config_1 = require("@nestjs/config");
const minio_1 = require("minio");
let MinioService = class MinioService {
    constructor(configService) {
        this.configService = configService;
        this.client = new minio_1.Client({
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
    async ensureDefaultBucket() {
        const exists = await this.client.bucketExists(this.defaultBucket);
        if (!exists) {
            await this.client.makeBucket(this.defaultBucket, 'us-east-1');
        }
    }
    async listBuckets() {
        const buckets = await this.client.listBuckets();
        return buckets.map(b => ({
            name: b.name,
            creationDate: b.creationDate,
        }));
    }
    async createBucket(bucketName, region = 'us-east-1') {
        const exists = await this.client.bucketExists(bucketName);
        if (!exists) {
            await this.client.makeBucket(bucketName, region);
        }
    }
    async deleteBucket(bucketName) {
        await this.client.removeBucket(bucketName);
    }
    async bucketExists(bucketName) {
        return this.client.bucketExists(bucketName);
    }
    async listObjects(bucketName, prefix = '', recursive = true) {
        const objects = [];
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
    async getObject(bucketName, objectName) {
        return this.client.getObject(bucketName, objectName);
    }
    async getObjectStat(bucketName, objectName) {
        return this.client.statObject(bucketName, objectName);
    }
    async putObject(bucketName, objectName, stream, size, metaData) {
        const etag = await this.client.putObject(bucketName, objectName, stream, size, metaData);
        return etag.etag;
    }
    async uploadFile(bucketName, objectName, filePath, metaData) {
        const etag = await this.client.fPutObject(bucketName, objectName, filePath, metaData);
        return etag.etag;
    }
    async downloadFile(bucketName, objectName, filePath) {
        await this.client.fGetObject(bucketName, objectName, filePath);
    }
    async deleteObject(bucketName, objectName) {
        await this.client.removeObject(bucketName, objectName);
    }
    async deleteObjects(bucketName, objectNames) {
        await this.client.removeObjects(bucketName, objectNames);
    }
    async copyObject(sourceBucket, sourceObject, destBucket, destObject) {
        await this.client.copyObject(destBucket, destObject, `/${sourceBucket}/${sourceObject}`);
    }
    async presignedGetObject(bucketName, objectName, expiry = 24 * 60 * 60) {
        return this.client.presignedGetObject(bucketName, objectName, expiry);
    }
    async presignedPutObject(bucketName, objectName, expiry = 24 * 60 * 60) {
        return this.client.presignedPutObject(bucketName, objectName, expiry);
    }
    async presignedUrl(bucketName, objectName, options = {}) {
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
                policy.setExpires(new Date(Date.now() + expiry * 1000));
                const { postURL, formData } = await this.client.presignedPostPolicy(policy);
                return JSON.stringify({ url: postURL, formData });
            default:
                throw new Error(`Unsupported method: ${method}`);
        }
    }
    async setBucketPolicy(bucketName, policy) {
        const policyDocument = policy === 'public'
            ? JSON.stringify({ Version: '2012-10-17', Statement: [{ Effect: 'Allow', Principal: '*', Action: ['s3:GetObject'], Resource: [`arn:aws:s3:::${bucketName}/*`] }] })
            : policy === 'readonly'
                ? JSON.stringify({ Version: '2012-10-17', Statement: [{ Effect: 'Allow', Principal: '*', Action: ['s3:GetObject'], Resource: [`arn:aws:s3:::${bucketName}/*`] }] })
                : JSON.stringify({ Version: '2012-10-17', Statement: [] });
        await this.client.setBucketPolicy(bucketName, policyDocument);
    }
    async getBucketPolicy(bucketName) {
        return this.client.getBucketPolicy(bucketName);
    }
    async healthCheck() {
        try {
            await this.client.listBuckets();
            return true;
        }
        catch {
            return false;
        }
    }
    getClient() {
        return this.client;
    }
};
exports.MinioService = MinioService;
exports.MinioService = MinioService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [config_1.ConfigService])
], MinioService);
//# sourceMappingURL=minio.service.js.map