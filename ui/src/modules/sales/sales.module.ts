import { Module } from '@nestjs/common';
import { SalesService } from './sales.service';
import { MinioService } from './minio.service';
import { IcebergService } from './iceberg.service';

@Module({
  providers: [SalesService, MinioService, IcebergService],
  exports: [SalesService, MinioService, IcebergService],
})
export class SalesModule {}