import { Repository } from 'typeorm';
import { RawSale } from '../entities/raw-sale.entity';
import { StagingSale } from '../entities/staging-sale.entity';
import { MartSale } from '../entities/mart-sale.entity';
export declare class DashboardService {
    private rawSaleRepo;
    private stagingSaleRepo;
    private martSaleRepo;
    constructor(rawSaleRepo: Repository<RawSale>, stagingSaleRepo: Repository<StagingSale>, martSaleRepo: Repository<MartSale>);
    getOverview(): Promise<{
        counts: {
            raw: number;
            staging: number;
            mart: number;
        };
        latestRaw: RawSale[];
        revenueByDate: any[];
    }>;
    getRawSales(page?: number, limit?: number): Promise<{
        data: RawSale[];
        total: number;
        page: number;
        limit: number;
    }>;
    getStagingSales(page?: number, limit?: number): Promise<{
        data: StagingSale[];
        total: number;
        page: number;
        limit: number;
    }>;
    getMartSales(page?: number, limit?: number): Promise<{
        data: MartSale[];
        total: number;
        page: number;
        limit: number;
    }>;
}
