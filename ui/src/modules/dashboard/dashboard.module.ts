import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { DashboardController } from './dashboard.controller';
import { DashboardService } from './dashboard.service';
import { RawSale } from '../entities/raw-sale.entity';
import { StagingSale } from '../entities/staging-sale.entity';
import { MartSale } from '../entities/mart-sale.entity';

@Module({
  imports: [TypeOrmModule.forFeature([RawSale, StagingSale, MartSale])],
  controllers: [DashboardController],
  providers: [DashboardService],
  exports: [DashboardService],
})
export class DashboardModule {}