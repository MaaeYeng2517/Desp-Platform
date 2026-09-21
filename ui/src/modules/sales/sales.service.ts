import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { RawSale } from '../entities/raw-sale.entity';
import { StagingSale } from '../entities/staging-sale.entity';
import { MartSale } from '../entities/mart-sale.entity';
import { MinioService, MinioObject, PresignedUrlOptions } from './minio.service';
import { IcebergService, IcebergTable, IcebergSchema } from './iceberg.service';

@Injectable()
export class SalesService {
  constructor(
    @InjectRepository(RawSale)
    private rawSaleRepo: Repository<RawSale>,
    @InjectRepository(StagingSale)
    private stagingSaleRepo: Repository<StagingSale>,
    @InjectRepository(MartSale)
    private martSaleRepo: Repository<MartSale>,
    private minioService: MinioService,
    private icebergService: IcebergService,
  ) {}

  // Raw layer operations
  async getRawSales(page = 1, limit = 20, filters?: Record<string, any>) {
    const qb = this.rawSaleRepo.createQueryBuilder('sale');
    
    if (filters) {
      if (filters.customerId) qb.andWhere('sale.customerId = :customerId', { customerId: filters.customerId });
      if (filters.productId) qb.andWhere('sale.productId = :productId', { productId: filters.productId });
      if (filters.startDate) qb.andWhere('sale.transactionDate >= :startDate', { startDate: filters.startDate });
      if (filters.endDate) qb.andWhere('sale.transactionDate <= :endDate', { endDate: filters.endDate });
    }

    const [data, total] = await qb
      .orderBy('sale.loadedAt', 'DESC')
      .skip((page - 1) * limit)
      .take(limit)
      .getManyAndCount();

    return { data, total, page, limit };
  }

  // Staging layer operations
  async getStagingSales(page = 1, limit = 20, filters?: Record<string, any>) {
    const qb = this.stagingSaleRepo.createQueryBuilder('sale');
    
    if (filters) {
      if (filters.customerId) qb.andWhere('sale.customerId = :customerId', { customerId: filters.customerId });
      if (filters.productId) qb.andWhere('sale.productId = :productId', { productId: filters.productId });
      if (filters.startDate) qb.andWhere('sale.transactionDate >= :startDate', { startDate: filters.startDate });
      if (filters.endDate) qb.andWhere('sale.transactionDate <= :endDate', { endDate: filters.endDate });
    }

    const [data, total] = await qb
      .orderBy('sale.transactionDate', 'DESC')
      .skip((page - 1) * limit)
      .take(limit)
      .getManyAndCount();

    return { data, total, page, limit };
  }

  // Mart layer operations
  async getMartSales(page = 1, limit = 20, filters?: Record<string, any>) {
    const qb = this.martSaleRepo.createQueryBuilder('sale');
    
    if (filters) {
      if (filters.customerId) qb.andWhere('sale.customerId = :customerId', { customerId: filters.customerId });
      if (filters.productId) qb.andWhere('sale.productId = :productId', { productId: filters.productId });
      if (filters.startDate) qb.andWhere('sale.transactionDate >= :startDate', { startDate: filters.startDate });
      if (filters.endDate) qb.andWhere('sale.transactionDate <= :endDate', { endDate: filters.endDate });
    }

    const [data, total] = await qb
      .orderBy('sale.transactionDate', 'DESC')
      .skip((page - 1) * limit)
      .take(limit)
      .getManyAndCount();

    return { data, total, page, limit };
  }

  // Aggregations
  async getDailyRevenue(startDate?: string, endDate?: string) {
    const qb = this.martSaleRepo.createQueryBuilder('sale')
      .select('sale.transactionDate', 'date')
      .addSelect('SUM(sale.totalAmount)', 'revenue')
      .addSelect('COUNT(*)', 'transactions')
      .addSelect('SUM(sale.quantity)', 'units')
      .groupBy('sale.transactionDate')
      .orderBy('sale.transactionDate', 'ASC');

    if (startDate) qb.andWhere('sale.transactionDate >= :startDate', { startDate });
    if (endDate) qb.andWhere('sale.transactionDate <= :endDate', { endDate });

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

  // MinIO operations
  async listDataLakeObjects(prefix = ''): Promise<MinioObject[]> {
    return this.minioService.listObjects('data-lake', prefix);
  }

  async uploadToDataLake(objectName: string, filePath: string, metaData?: Record<string, string>): Promise<string> {
    return this.minioService.uploadFile('data-lake', objectName, filePath, metaData);
  }

  async downloadFromDataLake(objectName: string, filePath: string): Promise<void> {
    return this.minioService.downloadFile('data-lake', objectName, filePath);
  }

  async getPresignedUrl(objectName: string, options: PresignedUrlOptions = {}): Promise<string> {
    return this.minioService.presignedUrl('data-lake', objectName, options);
  }

  // Iceberg operations
  async createIcebergTable(table: IcebergTable): Promise<void> {
    await this.icebergService.createTable(
      table.name,
      table.schema,
      table.namespace,
      [], // partition by - would need to be passed separately
      table.properties,
    );
  }

  async listIcebergTables(namespace = 'default'): Promise<string[]> {
    return this.icebergService.listTables(namespace);
  }

  async queryIceberg(sql: string): Promise<any[]> {
    return this.icebergService.query(sql);
  }

  async getIcebergSnapshots(tableName: string, namespace = 'default') {
    return this.icebergService.getSnapshots(tableName, namespace);
  }

  async rollbackIceberg(tableName: string, snapshotId: number, namespace = 'default') {
    return this.icebergService.rollbackToSnapshot(tableName, snapshotId, namespace);
  }

  async maintainIceberg(tableName: string, namespace = 'default') {
    await Promise.all([
      this.icebergService.rewriteDataFiles(tableName, namespace),
      this.icebergService.rewriteManifests(tableName, namespace),
      this.icebergService.removeOrphanFiles(tableName, namespace),
    ]);
  }

  // Data lineage
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
}