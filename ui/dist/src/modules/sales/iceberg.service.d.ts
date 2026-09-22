import { ConfigService } from '@nestjs/config';
import { MinioService } from './minio.service';
export interface IcebergTable {
    name: string;
    namespace: string;
    location: string;
    format: 'parquet' | 'orc' | 'avro';
    schema: IcebergSchema;
    properties: Record<string, string>;
    snapshotId?: number;
    schemaId?: number;
}
export interface IcebergSchema {
    fields: IcebergField[];
    schemaId: number;
}
export interface IcebergField {
    id: number;
    name: string;
    type: string;
    required: boolean;
    doc?: string;
}
export interface IcebergSnapshot {
    snapshotId: number;
    timestamp: number;
    operation: 'append' | 'replace' | 'overwrite' | 'delete';
    summary: Record<string, string>;
    manifestList: string;
}
export declare class IcebergService {
    private configService;
    private minioService;
    private warehousePath;
    private catalogName;
    private sparkSubmitPath;
    constructor(configService: ConfigService, minioService: MinioService);
    private runSparkSQL;
    createTable(tableName: string, schema: IcebergSchema, namespace?: string, partitionBy?: string[], properties?: Record<string, string>): Promise<void>;
    createTableFromSelect(tableName: string, selectQuery: string, namespace?: string, partitionBy?: string[], properties?: Record<string, string>): Promise<void>;
    dropTable(tableName: string, namespace?: string): Promise<void>;
    listTables(namespace?: string): Promise<string[]>;
    describeTable(tableName: string, namespace?: string): Promise<any>;
    getTableSchema(tableName: string, namespace?: string): Promise<IcebergSchema>;
    private parseSchema;
    insertInto(tableName: string, data: Record<string, any>[], namespace?: string, overwrite?: boolean): Promise<void>;
    query(sql: string): Promise<any[]>;
    private parseQueryResult;
    getSnapshots(tableName: string, namespace?: string): Promise<IcebergSnapshot[]>;
    getSnapshot(tableName: string, snapshotId: number, namespace?: string): Promise<IcebergSnapshot>;
    rollbackToSnapshot(tableName: string, snapshotId: number, namespace?: string): Promise<void>;
    expireSnapshots(tableName: string, namespace?: string, olderThan?: string, retainLast?: number): Promise<void>;
    rewriteDataFiles(tableName: string, namespace?: string, strategy?: string, options?: Record<string, string>): Promise<void>;
    rewriteManifests(tableName: string, namespace?: string): Promise<void>;
    removeOrphanFiles(tableName: string, namespace?: string, olderThan?: string): Promise<void>;
    migrateFromParquet(sourcePath: string, tableName: string, namespace?: string, schema?: IcebergSchema, partitionBy?: string[]): Promise<void>;
    migrateFromPostgres(jdbcUrl: string, tableName: string, targetTable: string, namespace?: string, partitionBy?: string[]): Promise<void>;
    private parseDuration;
    listWarehouseObjects(prefix?: string): Promise<any[]>;
    getTableLocation(tableName: string, namespace?: string): Promise<string>;
}
