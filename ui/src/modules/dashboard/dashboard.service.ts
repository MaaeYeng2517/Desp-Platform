import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { RawSale } from '../../entities/raw-sale.entity';
import { StagingSale } from '../../entities/staging-sale.entity';
import { MartSale } from '../../entities/mart-sale.entity';

@Injectable()
export class DashboardService {
  constructor(
    @InjectRepository(RawSale)
    private rawSaleRepo: Repository<RawSale>,
    @InjectRepository(StagingSale)
    private stagingSaleRepo: Repository<StagingSale>,
    @InjectRepository(MartSale)
    private martSaleRepo: Repository<MartSale>,
  ) {}

  async getOverview() {
    const [rawCount, stagingCount, martCount] = await Promise.all([
      this.rawSaleRepo.count(),
      this.stagingSaleRepo.count(),
      this.martSaleRepo.count(),
    ]);

    const latestRaw = await this.rawSaleRepo.find({
      order: { loadedAt: 'DESC' },
      take: 5,
    });

    const revenueByDate = await this.martSaleRepo
      .createQueryBuilder('sale')
      .select('sale.transaction_date', 'date')
      .addSelect('SUM(sale.total_amount)', 'revenue')
      .addSelect('COUNT(*)', 'transactions')
      .addSelect('SUM(sale.quantity)', 'units')
      .groupBy('sale.transaction_date')
      .orderBy('sale.transaction_date', 'ASC')
      .getRawMany();

    return {
      counts: { raw: rawCount, staging: stagingCount, mart: martCount },
      latestRaw,
      revenueByDate,
    };
  }

  async getRawSales(page = 1, limit = 20) {
    const [data, total] = await this.rawSaleRepo.findAndCount({
      order: { loadedAt: 'DESC' },
      skip: (page - 1) * limit,
      take: limit,
    });
    return { data, total, page, limit };
  }

  async getStagingSales(page = 1, limit = 20) {
    const [data, total] = await this.stagingSaleRepo.findAndCount({
      order: { transactionDate: 'DESC' },
      skip: (page - 1) * limit,
      take: limit,
    });
    return { data, total, page, limit };
  }

  async getMartSales(page = 1, limit = 20) {
    const [data, total] = await this.martSaleRepo.findAndCount({
      order: { transactionDate: 'DESC' },
      skip: (page - 1) * limit,
      take: limit,
    });
    return { data, total, page, limit };
  }
}