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
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.SalesService = void 0;
const common_1 = require("@nestjs/common");
const typeorm_1 = require("@nestjs/typeorm");
const typeorm_2 = require("typeorm");
const raw_sale_entity_1 = require("../entities/raw-sale.entity");
const staging_sale_entity_1 = require("../entities/staging-sale.entity");
const mart_sale_entity_1 = require("../entities/mart-sale.entity");
const minio_service_1 = require("./minio.service");
const iceberg_service_1 = require("./iceberg.service");
let SalesService = class SalesService {
    constructor(rawSaleRepo, stagingSaleRepo, martSaleRepo, minioService, icebergService) {
        this.rawSaleRepo = rawSaleRepo;
        this.stagingSaleRepo = stagingSaleRepo;
        this.martSaleRepo = martSaleRepo;
        this.minioService = minioService;
        this.icebergService = icebergService;
    }
    async getRawSales(page = 1, limit = 20, filters) {
        const qb = this.rawSaleRepo.createQueryBuilder('sale');
        if (filters) {
            if (filters.customerId)
                qb.andWhere('sale.customerId = :customerId', { customerId: filters.customerId });
            if (filters.productId)
                qb.andWhere('sale.productId = :productId', { productId: filters.productId });
            if (filters.startDate)
                qb.andWhere('sale.transactionDate >= :startDate', { startDate: filters.startDate });
            if (filters.endDate)
                qb.andWhere('sale.transactionDate <= :endDate', { endDate: filters.endDate });
        }
        const [data, total] = await qb
            .orderBy('sale.loadedAt', 'DESC')
            .skip((page - 1) * limit)
            .take(limit)
            .getManyAndCount();
        return { data, total, page, limit };
    }
    async getStagingSales(page = 1, limit = 20, filters) {
        const qb = this.stagingSaleRepo.createQueryBuilder('sale');
        if (filters) {
            if (filters.customerId)
                qb.andWhere('sale.customerId = :customerId', { customerId: filters.customerId });
            if (filters.productId)
                qb.andWhere('sale.productId = :productId', { productId: filters.productId });
            if (filters.startDate)
                qb.andWhere('sale.transactionDate >= :startDate', { startDate: filters.startDate });
            if (filters.endDate)
                qb.andWhere('sale.transactionDate <= :endDate', { endDate: filters.endDate });
        }
        const [data, total] = await qb
            .orderBy('sale.transactionDate', 'DESC')
            .skip((page - 1) * limit)
            .take(limit)
            .getManyAndCount();
        return { data, total, page, limit };
    }
    async getMartSales(page = 1, limit = 20, filters) {
        const qb = this.martSaleRepo.createQueryBuilder('sale');
        if (filters) {
            if (filters.customerId)
                qb.andWhere('sale.customerId = :customerId', { customerId: filters.customerId });
            if (filters.productId)
                qb.andWhere('sale.productId = :productId', { productId: filters.productId });
            if (filters.startDate)
                qb.andWhere('sale.transactionDate >= :startDate', { startDate: filters.startDate });
            if (filters.endDate)
                qb.andWhere('sale.transactionDate <= :endDate', { endDate: filters.endDate });
        }
        const [data, total] = await qb
            .orderBy('sale.transactionDate', 'DESC')
            .skip((page - 1) * limit)
            .take(limit)
            .getManyAndCount();
        return { data, total, page, limit };
    }
    async getDailyRevenue(startDate, endDate) {
        const qb = this.martSaleRepo.createQueryBuilder('sale')
            .select('sale.transactionDate', 'date')
            .addSelect('SUM(sale.totalAmount)', 'revenue')
            .addSelect('COUNT(*)', 'transactions')
            .addSelect('SUM(sale.quantity)', 'units')
            .groupBy('sale.transactionDate')
            .orderBy('sale.transactionDate', 'ASC');
        if (startDate)
            qb.andWhere('sale.transactionDate >= :startDate', { startDate });
        if (endDate)
            qb.andWhere('sale.transactionDate <= :endDate', { endDate });
        return qb.getRawMany();
    }
    async getProductPerformance(limit = 10) {
        return this.martSaleRepo.createQueryBuilder('sale')
            .select('sale.productId', 'productId')
            .addSelect('SUM(sale.totalAmount)', 'revenue')
            .addSelect('SUM(sale.quantity)', 'unitsSold')
            .addSelect('COUNT(DISTINCT sale.customerId)', 'uniqueCustomers')
            .groupBy('sale.productId')
            .orderBy('revenue', 'DESC')
            .limit(limit)
            .getRawMany();
    }
    async getCustomerPerformance(limit = 10) {
        return this.martSaleRepo.createQueryBuilder('sale')
            .select('sale.customerId', 'customerId')
            .addSelect('SUM(sale.totalAmount)', 'totalSpent')
            .addSelect('COUNT(*)', 'orderCount')
            .addSelect('AVG(sale.totalAmount)', 'avgOrderValue')
            .groupBy('sale.customerId')
            .orderBy('totalSpent', 'DESC')
            .limit(limit)
            .getRawMany();
    }
    async listDataLakeObjects(prefix = '') {
        return this.minioService.listObjects('data-lake', prefix);
    }
    async uploadToDataLake(objectName, filePath, metaData) {
        return this.minioService.uploadFile('data-lake', objectName, filePath, metaData);
    }
    async downloadFromDataLake(objectName, filePath) {
        return this.minioService.downloadFile('data-lake', objectName, filePath);
    }
    async getPresignedUrl(objectName, options = {}) {
        return this.minioService.presignedUrl('data-lake', objectName, options);
    }
    async createIcebergTable(table) {
        await this.icebergService.createTable(table.name, table.schema, table.namespace, [], table.properties);
    }
    async listIcebergTables(namespace = 'default') {
        return this.icebergService.listTables(namespace);
    }
    async queryIceberg(sql) {
        return this.icebergService.query(sql);
    }
    async getIcebergSnapshots(tableName, namespace = 'default') {
        return this.icebergService.getSnapshots(tableName, namespace);
    }
    async rollbackIceberg(tableName, snapshotId, namespace = 'default') {
        return this.icebergService.rollbackToSnapshot(tableName, snapshotId, namespace);
    }
    async maintainIceberg(tableName, namespace = 'default') {
        await Promise.all([
            this.icebergService.rewriteDataFiles(tableName, namespace),
            this.icebergService.rewriteManifests(tableName, namespace),
            this.icebergService.removeOrphanFiles(tableName, namespace),
        ]);
    }
    async getDataLineage() {
        const [rawCount, stagingCount, martCount] = await Promise.all([
            this.rawSaleRepo.count(),
            this.stagingSaleRepo.count(),
            this.martSaleRepo.count(),
        ]);
        return {
            raw: { count: rawCount, description: 'Raw data from source systems' },
            staging: { count: stagingCount, description: 'Cleaned and validated data' },
            mart: { count: martCount, description: 'Business-ready aggregated data' },
            flow: 'raw -> staging -> mart',
        };
    }
};
exports.SalesService = SalesService;
exports.SalesService = SalesService = __decorate([
    (0, common_1.Injectable)(),
    __param(0, (0, typeorm_1.InjectRepository)(raw_sale_entity_1.RawSale)),
    __param(1, (0, typeorm_1.InjectRepository)(staging_sale_entity_1.StagingSale)),
    __param(2, (0, typeorm_1.InjectRepository)(mart_sale_entity_1.MartSale)),
    __metadata("design:paramtypes", [typeorm_2.Repository,
        typeorm_2.Repository,
        typeorm_2.Repository,
        minio_service_1.MinioService,
        iceberg_service_1.IcebergService])
], SalesService);
//# sourceMappingURL=sales.service.js.map