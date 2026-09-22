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
        latestRaw: RawSale[];
        revenueByDate: any[];
    }>;
    getRawSales(page: number, limit: number): Promise<{
        data: RawSale[];
        total: number;
        page: number;
        limit: number;
    }>;
    getStagingSales(page: number, limit: number): Promise<{
        data: StagingSale[];
        total: number;
        page: number;
        limit: number;
    }>;
    getMartSales(page: number, limit: number): Promise<{
        data: MartSale[];
        total: number;
        page: number;
        limit: number;
    }>;
}
