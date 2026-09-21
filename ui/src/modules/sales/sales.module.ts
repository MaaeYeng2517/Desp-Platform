import { Module } from '@nestjs/common';
import { SalesController } from './sales.controller';
import { SalesService } from './sales.service';
import { MinioService } from './minio.service';
import { IcebergService } from './iceberg.service';

@Module({
  controllers: [SalesController],
  providers: [SalesService, MinioService, IcebergService],
  exports: [SalesService, MinioService, IcebergService],
})
export class SalesModule {}