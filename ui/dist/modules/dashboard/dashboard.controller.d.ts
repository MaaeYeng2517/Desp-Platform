import { DashboardService } from './dashboard.service';
export declare class DashboardController {
    private readonly dashboardService;
    constructor(dashboardService: DashboardService);
    getOverview(): Promise<{
        counts: {
            raw: number;
            staging: number;
            mart: number;
        };
        latestRaw: import("../../entities/raw-sale.entity").RawSale[];
        revenueByDate: any[];
    }>;
    getRawSales(page: number, limit: number): Promise<{
        data: import("../../entities/raw-sale.entity").RawSale[];
        total: number;
        page: number;
        limit: number;
    }>;
    getStagingSales(page: number, limit: number): Promise<{
        data: import("../../entities/staging-sale.entity").StagingSale[];
        total: number;
        page: number;
        limit: number;
    }>;
    getMartSales(page: number, limit: number): Promise<{
        data: import("../../entities/mart-sale.entity").MartSale[];
        total: number;
        page: number;
        limit: number;
    }>;
}
