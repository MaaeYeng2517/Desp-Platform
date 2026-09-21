import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { QualityController } from './quality.controller';
import { QualityService } from './quality.service';
import { MartSale } from '../entities/mart-sale.entity';
import { StagingSale } from '../entities/staging-sale.entity';
import { RawSale } from '../entities/raw-sale.entity';

@Module({
  imports: [TypeOrmModule.forFeature([MartSale, StagingSale, RawSale])],
  controllers: [QualityController],
  providers: [QualityService],
  exports: [QualityService],
})
export class QualityModule {}