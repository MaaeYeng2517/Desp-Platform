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
exports.IcebergService = void 0;
const common_1 = require("@nestjs/common");
const config_1 = require("@nestjs/config");
const minio_service_1 = require("./minio.service");
const child_process_1 = require("child_process");
const util_1 = require("util");
const execAsync = (0, util_1.promisify)(child_process_1.exec);
let IcebergService = class IcebergService {
    constructor(configService, minioService) {
        this.configService = configService;
        this.minioService = minioService;
        this.warehousePath = this.configService.get('ICEBERG_WAREHOUSE') || 's3a://data-lake/warehouse';
        this.catalogName = this.configService.get('ICEBERG_CATALOG') || 'hadoop';
        this.sparkSubmitPath = this.configService.get('SPARK_SUBMIT') || 'spark-submit';
    }
    async runSparkSQL(sql, configs = {}) {
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
    async createTable(tableName, schema, namespace = 'default', partitionBy = [], properties = {}) {
        const fullName = `${namespace}.${tableName}`;
        const fields = schema.fields.map(f => `${f.name} ${f.type}${f.required ? ' NOT NULL' : ''}${f.doc ? ` COMMENT '${f.doc}'` : ''}`).join(', ');
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
    async createTableFromSelect(tableName, selectQuery, namespace = 'default', partitionBy = [], properties = {}) {
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
    async dropTable(tableName, namespace = 'default') {
        const sql = `DROP TABLE IF EXISTS ${namespace}.${tableName}`;
        await this.runSparkSQL(sql);
    }
    async listTables(namespace = 'default') {
        const sql = `SHOW TABLES IN ${namespace}`;
        const output = await this.runSparkSQL(sql);
        return output.split('\n')
            .map(line => line.trim())
            .filter(line => line && !line.startsWith('tableName') && !line.startsWith('---'));
    }
    async describeTable(tableName, namespace = 'default') {
        const sql = `DESCRIBE TABLE EXTENDED ${namespace}.${tableName}`;
        return this.runSparkSQL(sql);
    }
    async getTableSchema(tableName, namespace = 'default') {
        const sql = `DESCRIBE TABLE ${namespace}.${tableName}`;
        const output = await this.runSparkSQL(sql);
        return this.parseSchema(output);
    }
    parseSchema(output) {
        const lines = output.split('\n').filter(l => l.trim());
        const fields = lines.map((line, idx) => {
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
    async insertInto(tableName, data, namespace = 'default', overwrite = false) {
        if (data.length === 0)
            return;
        const columns = Object.keys(data[0]);
        const values = data.map(row => `(${columns.map(c => {
            const val = row[c];
            if (val === null || val === undefined)
                return 'NULL';
            if (typeof val === 'string')
                return `'${val.replace(/'/g, "''")}'`;
            if (val instanceof Date)
                return `'${val.toISOString()}'`;
            return String(val);
        }).join(', ')})`).join(', ');
        const sql = `
      ${overwrite ? 'INSERT OVERWRITE' : 'INSERT INTO'} ${namespace}.${tableName}
      (${columns.join(', ')})
      VALUES ${values}
    `;
        await this.runSparkSQL(sql);
    }
    async query(sql) {
        const output = await this.runSparkSQL(sql);
        return this.parseQueryResult(output);
    }
    parseQueryResult(output) {
        const lines = output.split('\n').filter(l => l.trim() && !l.startsWith('---'));
        if (lines.length < 2)
            return [];
        const headers = lines[0].split('|').map(h => h.trim());
        return lines.slice(1).map(line => {
            const values = line.split('|').map(v => v.trim());
            const row = {};
            headers.forEach((h, i) => { row[h] = values[i]; });
            return row;
        });
    }
    async getSnapshots(tableName, namespace = 'default') {
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
    async getSnapshot(tableName, snapshotId, namespace = 'default') {
        const sql = `SELECT * FROM ${namespace}.${tableName}.snapshots WHERE snapshot_id = ${snapshotId}`;
        const results = await this.query(sql);
        if (results.length === 0)
            throw new Error(`Snapshot ${snapshotId} not found`);
        const r = results[0];
        return {
            snapshotId: parseInt(r.snapshot_id, 10),
            timestamp: parseInt(r.committed_at, 10),
            operation: r.operation,
            summary: r.summary ? JSON.parse(r.summary) : {},
            manifestList: r.manifest_list,
        };
    }
    async rollbackToSnapshot(tableName, snapshotId, namespace = 'default') {
        const sql = `CALL spark_catalog.system.rollback_to_snapshot('${namespace}.${tableName}', ${snapshotId})`;
        await this.runSparkSQL(sql);
    }
    async expireSnapshots(tableName, namespace = 'default', olderThan = '7d', retainLast = 1) {
        const sql = `
      CALL spark_catalog.system.expire_snapshots(
        table => '${namespace}.${tableName}',
        older_than => TIMESTAMP '${new Date(Date.now() - this.parseDuration(olderThan)).toISOString()}',
        retain_last => ${retainLast}
      )
    `;
        await this.runSparkSQL(sql);
    }
    async rewriteDataFiles(tableName, namespace = 'default', strategy = 'binpack', options = {}) {
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
    async rewriteManifests(tableName, namespace = 'default') {
        const sql = `
      CALL spark_catalog.system.rewrite_manifests('${namespace}.${tableName}')
    `;
        await this.runSparkSQL(sql);
    }
    async removeOrphanFiles(tableName, namespace = 'default', olderThan = '3d') {
        const sql = `
      CALL spark_catalog.system.remove_orphan_files(
        table => '${namespace}.${tableName}',
        older_than => TIMESTAMP '${new Date(Date.now() - this.parseDuration(olderThan)).toISOString()}'
      )
    `;
        await this.runSparkSQL(sql);
    }
    async migrateFromParquet(sourcePath, tableName, namespace = 'default', schema, partitionBy = []) {
        const sql = `
      CREATE TABLE ${namespace}.${tableName}
      USING iceberg
      ${partitionBy.length > 0 ? `PARTITIONED BY (${partitionBy.join(', ')})` : ''}
      LOCATION '${sourcePath}'
    `;
        await this.runSparkSQL(sql);
    }
    async migrateFromPostgres(jdbcUrl, tableName, targetTable, namespace = 'default', partitionBy = []) {
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
    parseDuration(duration) {
        const match = duration.match(/^(\d+)([dhms])$/);
        if (!match)
            return 7 * 24 * 60 * 60 * 1000;
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
    async listWarehouseObjects(prefix = '') {
        const bucket = this.warehousePath.replace('s3a://', '').split('/')[0];
        const prefixPath = this.warehousePath.replace(`s3a://${bucket}/`, '') + prefix;
        return this.minioService.listObjects(bucket, prefixPath, true);
    }
    async getTableLocation(tableName, namespace = 'default') {
        const desc = await this.describeTable(tableName, namespace);
        const lines = desc.split('\n');
        const locationLine = lines.find(l => l.includes('Location:'));
        return locationLine ? locationLine.split('Location:')[1].trim() : '';
    }
};
exports.IcebergService = IcebergService;
exports.IcebergService = IcebergService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [config_1.ConfigService,
        minio_service_1.MinioService])
], IcebergService);
//# sourceMappingURL=iceberg.service.js.map