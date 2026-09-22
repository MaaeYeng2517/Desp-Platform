import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { MinioService } from './minio.service';
import { exec, spawn } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

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

@Injectable()
export class IcebergService {
  private warehousePath: string;
  private catalogName: string;
  private sparkSubmitPath: string;

  constructor(
    private configService: ConfigService,
    private minioService: MinioService,
  ) {
    this.warehousePath = this.configService.get('ICEBERG_WAREHOUSE') || 's3a://data-lake/warehouse';
    this.catalogName = this.configService.get('ICEBERG_CATALOG') || 'hadoop';
    this.sparkSubmitPath = this.configService.get('SPARK_SUBMIT') || 'spark-submit';
  }

  // Use Spark SQL to interact with Iceberg tables
  private async runSparkSQL(sql: string, configs: Record<string, string> = {}): Promise<string> {
    const defaultConfigs = {
      'spark.sql.catalog.spark_catalog': 'org.apache.iceberg.spark.SparkSessionCatalog',
      'spark.sql.catalog.spark_catalog.type': 'hadoop',
      'spark.sql.catalog.spark_catalog.warehouse': this.warehousePath,
      'spark.sql.extensions': 'org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions',
      'spark.hadoop.fs.s3a.endpoint': this.configService.get('MINIO_ENDPOINT') || 'http://localhost:9000',
      'spark.hadoop.fs.s3a.access.key': this.configService.get('MINIO_ACCESS_KEY') || 'minio',
      'spark.hadoop.fs.s3a.secret.key': this.configService.get('MINIO_SECRET_KEY') || 'minio123456',
      'spark.hadoop.fs.s3a.path.style.access': 'true',
      'spark.hadoop.fs.s3a.impl': 'org.apache.hadoop.fs.s3a.S3AFileSystem',
    };

    const allConfigs = { ...defaultConfigs, ...configs };
    const confArgs = Object.entries(allConfigs).flatMap(([k, v]) => ['--conf', `${k}=${v}`]);

    const args = [
      ...confArgs,
      '--master', this.configService.get('SPARK_MASTER') || 'local[*]',
      '--sql', sql,
    ];

    const { stdout, stderr } = await execAsync(`${this.sparkSubmitPath} ${args.join(' ')}`, {
      timeout: 300000,
      maxBuffer: 1024 * 1024 * 10,
    });

    if (stderr && !stderr.includes('WARN') && !stderr.includes('INFO')) {
      throw new Error(stderr);
    }

    return stdout;
  }

  // Table operations
  async createTable(
    tableName: string,
    schema: IcebergSchema,
    namespace = 'default',
    partitionBy: string[] = [],
    properties: Record<string, string> = {},
  ): Promise<void> {
    const fullName = `${namespace}.${tableName}`;
    const fields = schema.fields.map(f => 
      `${f.name} ${f.type}${f.required ? ' NOT NULL' : ''}${f.doc ? ` COMMENT '${f.doc}'` : ''}`
    ).join(', ');

    const partitionClause = partitionBy.length > 0 
      ? `PARTITIONED BY (${partitionBy.join(', ')})` 
      : '';

    const props = Object.entries(properties)
      .map(([k, v]) => `'${k}'='${v}'`)
      .join(', ');

    const propClause = props ? `TBLPROPERTIES (${props})` : '';

    const sql = `
      CREATE TABLE ${fullName} (${fields})
      USING iceberg
      ${partitionClause}
      ${propClause}
    `;

    await this.runSparkSQL(sql);
  }

  async createTableFromSelect(
    tableName: string,
    selectQuery: string,
    namespace = 'default',
    partitionBy: string[] = [],
    properties: Record<string, string> = {},
  ): Promise<void> {
    const fullName = `${namespace}.${tableName}`;
    const partitionClause = partitionBy.length > 0 
      ? `PARTITIONED BY (${partitionBy.join(', ')})` 
      : '';

    const props = Object.entries(properties)
      .map(([k, v]) => `'${k}'='${v}'`)
      .join(', ');

    const propClause = props ? `TBLPROPERTIES (${props})` : '';

    const sql = `
      CREATE TABLE ${fullName}
      USING iceberg
      ${partitionClause}
      ${propClause}
      AS ${selectQuery}
    `;

    await this.runSparkSQL(sql);
  }

  async dropTable(tableName: string, namespace = 'default'): Promise<void> {
    const sql = `DROP TABLE IF EXISTS ${namespace}.${tableName}`;
    await this.runSparkSQL(sql);
  }

  async listTables(namespace = 'default'): Promise<string[]> {
    const sql = `SHOW TABLES IN ${namespace}`;
    const output = await this.runSparkSQL(sql);
    // Parse output to get table names
    return output.split('\n')
      .map(line => line.trim())
      .filter(line => line && !line.startsWith('tableName') && !line.startsWith('---'));
  }

  async describeTable(tableName: string, namespace = 'default'): Promise<any> {
    const sql = `DESCRIBE TABLE EXTENDED ${namespace}.${tableName}`;
    return this.runSparkSQL(sql);
  }

  async getTableSchema(tableName: string, namespace = 'default'): Promise<IcebergSchema> {
    const sql = `DESCRIBE TABLE ${namespace}.${tableName}`;
    const output = await this.runSparkSQL(sql);
    // Parse schema from output
    return this.parseSchema(output);
  }

  private parseSchema(output: string): IcebergSchema {
    // Simple parser for DESCRIBE TABLE output
    const lines = output.split('\n').filter(l => l.trim());
    const fields: IcebergField[] = lines.map((line, idx) => {
      const parts = line.trim().split(/\s+/);
      return {
        id: idx + 1,
        name: parts[0],
        type: parts[1],
        required: parts.includes('NOT'),
        doc: '',
      };
    });
    return { fields, schemaId: 0 };
  }

  // Data operations
  async insertInto(
    tableName: string,
    data: Record<string, any>[],
    namespace = 'default',
    overwrite = false,
  ): Promise<void> {
    if (data.length === 0) return;

    // Create a temporary view and insert
    const columns = Object.keys(data[0]);
    const values = data.map(row => 
      `(${columns.map(c => {
        const val = row[c];
        if (val === null || val === undefined) return 'NULL';
        if (typeof val === 'string') return `'${val.replace(/'/g, "''")}'`;
        if (val instanceof Date) return `'${val.toISOString()}'`;
        return String(val);
      }).join(', ')})`
    ).join(', ');

    const sql = `
      ${overwrite ? 'INSERT OVERWRITE' : 'INSERT INTO'} ${namespace}.${tableName}
      (${columns.join(', ')})
      VALUES ${values}
    `;

    await this.runSparkSQL(sql);
  }

  async query(sql: string): Promise<any[]> {
    const output = await this.runSparkSQL(sql);
    return this.parseQueryResult(output);
  }

  private parseQueryResult(output: string): any[] {
    // Parse Spark SQL output
    const lines = output.split('\n').filter(l => l.trim() && !l.startsWith('---'));
    if (lines.length < 2) return [];
    
    const headers = lines[0].split('|').map(h => h.trim());
    return lines.slice(1).map(line => {
      const values = line.split('|').map(v => v.trim());
      const row: Record<string, any> = {};
      headers.forEach((h, i) => { row[h] = values[i]; });
      return row;
    });
  }

  // Time travel and snapshots
  async getSnapshots(tableName: string, namespace = 'default'): Promise<IcebergSnapshot[]> {
    const sql = `SELECT * FROM ${namespace}.${tableName}.snapshots ORDER BY committed_at DESC`;
    const results = await this.query(sql);
    return results.map(r => ({
      snapshotId: parseInt(r.snapshot_id, 10),
      timestamp: parseInt(r.committed_at, 10),
      operation: r.operation,
      summary: r.summary ? JSON.parse(r.summary) : {},
      manifestList: r.manifest_list,
    }));
  }

  async getSnapshot(tableName: string, snapshotId: number, namespace = 'default'): Promise<IcebergSnapshot> {
    const sql = `SELECT * FROM ${namespace}.${tableName}.snapshots WHERE snapshot_id = ${snapshotId}`;
    const results = await this.query(sql);
    if (results.length === 0) throw new Error(`Snapshot ${snapshotId} not found`);
    
    const r = results[0];
    return {
      snapshotId: parseInt(r.snapshot_id, 10),
      timestamp: parseInt(r.committed_at, 10),
      operation: r.operation,
      summary: r.summary ? JSON.parse(r.summary) : {},
      manifestList: r.manifest_list,
    };
  }

  async rollbackToSnapshot(tableName: string, snapshotId: number, namespace = 'default'): Promise<void> {
    const sql = `CALL spark_catalog.system.rollback_to_snapshot('${namespace}.${tableName}', ${snapshotId})`;
    await this.runSparkSQL(sql);
  }

  async expireSnapshots(
    tableName: string,
    namespace = 'default',
    olderThan: string = '7d',
    retainLast: number = 1,
  ): Promise<void> {
    const sql = `
      CALL spark_catalog.system.expire_snapshots(
        table => '${namespace}.${tableName}',
        older_than => TIMESTAMP '${new Date(Date.now() - this.parseDuration(olderThan)).toISOString()}',
        retain_last => ${retainLast}
      )
    `;
    await this.runSparkSQL(sql);
  }

  // Maintenance
  async rewriteDataFiles(
    tableName: string,
    namespace = 'default',
    strategy = 'binpack',
    options: Record<string, string> = {},
  ): Promise<void> {
    const opts = Object.entries(options)
      .map(([k, v]) => `'${k}'='${v}'`)
      .join(', ');

    const optClause = opts ? `OPTIONS (${opts})` : '';
    
    const sql = `
      CALL spark_catalog.system.rewrite_data_files(
        table => '${namespace}.${tableName}',
        strategy => '${strategy}',
        ${optClause}
      )
    `;
    
    await this.runSparkSQL(sql);
  }

  async rewriteManifests(
    tableName: string,
    namespace = 'default',
  ): Promise<void> {
    const sql = `
      CALL spark_catalog.system.rewrite_manifests('${namespace}.${tableName}')
    `;
    await this.runSparkSQL(sql);
  }

  async removeOrphanFiles(
    tableName: string,
    namespace = 'default',
    olderThan: string = '3d',
  ): Promise<void> {
    const sql = `
      CALL spark_catalog.system.remove_orphan_files(
        table => '${namespace}.${tableName}',
        older_than => TIMESTAMP '${new Date(Date.now() - this.parseDuration(olderThan)).toISOString()}'
      )
    `;
    await this.runSparkSQL(sql);
  }

  // Migration from existing data
  async migrateFromParquet(
    sourcePath: string,
    tableName: string,
    namespace = 'default',
    schema?: IcebergSchema,
    partitionBy: string[] = [],
  ): Promise<void> {
    // Create table from parquet files
    const sql = `
      CREATE TABLE ${namespace}.${tableName}
      USING iceberg
      ${partitionBy.length > 0 ? `PARTITIONED BY (${partitionBy.join(', ')})` : ''}
      LOCATION '${sourcePath}'
    `;
    await this.runSparkSQL(sql);
  }

  async migrateFromPostgres(
    jdbcUrl: string,
    tableName: string,
    targetTable: string,
    namespace = 'default',
    partitionBy: string[] = [],
  ): Promise<void> {
    const sql = `
      CREATE TABLE ${namespace}.${targetTable}
      USING iceberg
      ${partitionBy.length > 0 ? `PARTITIONED BY (${partitionBy.join(', ')})` : ''}
      TBLPROPERTIES ('write.format.default'='parquet')
      AS SELECT * FROM jdbc(
        '${jdbcUrl}',
        '${tableName}',
        'user=postgres',
        'password=postgres'
      )
    `;
    await this.runSparkSQL(sql);
  }

  private parseDuration(duration: string): number {
    const match = duration.match(/^(\d+)([dhms])$/);
    if (!match) return 7 * 24 * 60 * 60 * 1000;
    
    const value = parseInt(match[1], 10);
    const unit = match[2];
    
    switch (unit) {
      case 'd': return value * 24 * 60 * 60 * 1000;
      case 'h': return value * 60 * 60 * 1000;
      case 'm': return value * 60 * 1000;
      case 's': return value * 1000;
      default: return 7 * 24 * 60 * 60 * 1000;
    }
  }

  // Integration with MinIO
  async listWarehouseObjects(prefix = ''): Promise<any[]> {
    const bucket = this.warehousePath.replace('s3a://', '').split('/')[0];
    const prefixPath = this.warehousePath.replace(`s3a://${bucket}/`, '') + prefix;
    return this.minioService.listObjects(bucket, prefixPath, true);
  }

  async getTableLocation(tableName: string, namespace = 'default'): Promise<string> {
    const desc = await this.describeTable(tableName, namespace);
    // Parse location from DESCRIBE output
    const lines = desc.split('\n');
    const locationLine = lines.find((line: string) => line.includes('Location:'));
    return locationLine ? locationLine.split('Location:')[1].trim() : '';
  }
}