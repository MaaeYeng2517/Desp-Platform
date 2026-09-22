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
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.DashboardService = void 0;
const common_1 = require("@nestjs/common");
const typeorm_1 = require("@nestjs/typeorm");
const typeorm_2 = require("typeorm");
const raw_sale_entity_1 = require("../../entities/raw-sale.entity");
const staging_sale_entity_1 = require("../../entities/staging-sale.entity");
const mart_sale_entity_1 = require("../../entities/mart-sale.entity");
let DashboardService = class DashboardService {
    constructor(rawSaleRepo, stagingSaleRepo, martSaleRepo) {
        this.rawSaleRepo = rawSaleRepo;
        this.stagingSaleRepo = stagingSaleRepo;
        this.martSaleRepo = martSaleRepo;
    }
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
};
exports.DashboardService = DashboardService;
exports.DashboardService = DashboardService = __decorate([
    (0, common_1.Injectable)(),
    __param(0, (0, typeorm_1.InjectRepository)(raw_sale_entity_1.RawSale)),
    __param(1, (0, typeorm_1.InjectRepository)(staging_sale_entity_1.StagingSale)),
    __param(2, (0, typeorm_1.InjectRepository)(mart_sale_entity_1.MartSale)),
    __metadata("design:paramtypes", [typeorm_2.Repository,
        typeorm_2.Repository,
        typeorm_2.Repository])
], DashboardService);
//# sourceMappingURL=dashboard.service.js.map