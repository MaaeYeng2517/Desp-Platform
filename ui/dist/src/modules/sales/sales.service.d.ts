import { Repository } from 'typeorm';
import { RawSale } from '../entities/raw-sale.entity';
import { StagingSale } from '../entities/staging-sale.entity';
import { MartSale } from '../entities/mart-sale.entity';
import { MinioService, MinioObject, PresignedUrlOptions } from './minio.service';
import { IcebergService, IcebergTable } from './iceberg.service';
export declare class SalesService {
    private rawSaleRepo;
    private stagingSaleRepo;
    private martSaleRepo;
    private minioService;
    private icebergService;
    constructor(rawSaleRepo: Repository<RawSale>, stagingSaleRepo: Repository<StagingSale>, martSaleRepo: Repository<MartSale>, minioService: MinioService, icebergService: IcebergService);
    getRawSales(page?: number, limit?: number, filters?: Record<string, any>): Promise<{
        data: RawSale[];
        total: number;
        page: number;
        limit: number;
    }>;
    getStagingSales(page?: number, limit?: number, filters?: Record<string, any>): Promise<{
        data: StagingSale[];
        total: number;
        page: number;
        limit: number;
    }>;
    getMartSales(page?: number, limit?: number, filters?: Record<string, any>): Promise<{
        data: MartSale[];
        total: number;
        page: number;
        limit: number;
    }>;
    getDailyRevenue(startDate?: string, endDate?: string): Promise<any[]>;
    getProductPerformance(limit?: number): Promise<any[]>;
    getCustomerPerformance(limit?: number): Promise<any[]>;
    listDataLakeObjects(prefix?: string): Promise<MinioObject[]>;
    uploadToDataLake(objectName: string, filePath: string, metaData?: Record<string, string>): Promise<string>;
    downloadFromDataLake(objectName: string, filePath: string): Promise<void>;
    getPresignedUrl(objectName: string, options?: PresignedUrlOptions): Promise<string>;
    createIcebergTable(table: IcebergTable): Promise<void>;
    listIcebergTables(namespace?: string): Promise<string[]>;
    queryIceberg(sql: string): Promise<any[]>;
    getIcebergSnapshots(tableName: string, namespace?: string): Promise<import("./iceberg.service").IcebergSnapshot[]>;
    rollbackIceberg(tableName: string, snapshotId: number, namespace?: string): Promise<void>;
    maintainIceberg(tableName: string, namespace?: string): Promise<void>;
    getDataLineage(): Promise<{
        raw: {
            count: number;
            description: string;
        };
        staging: {
            count: number;
            description: string;
        };
        mart: {
            count: number;
            description: string;
        };
        flow: string;
    }>;
}
