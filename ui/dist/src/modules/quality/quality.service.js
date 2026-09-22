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
exports.QualityService = void 0;
const common_1 = require("@nestjs/common");
const typeorm_1 = require("@nestjs/typeorm");
const typeorm_2 = require("typeorm");
const mart_sale_entity_1 = require("../entities/mart-sale.entity");
const staging_sale_entity_1 = require("../entities/staging-sale.entity");
const raw_sale_entity_1 = require("../entities/raw-sale.entity");
let QualityService = class QualityService {
    constructor(martSaleRepo, stagingSaleRepo, rawSaleRepo) {
        this.martSaleRepo = martSaleRepo;
        this.stagingSaleRepo = stagingSaleRepo;
        this.rawSaleRepo = rawSaleRepo;
        this.checks = [
            {
                name: 'duplicate_transaction',
                description: 'Check for duplicate transaction IDs in mart layer',
                query: `
        SELECT COUNT(*)
        FROM (
          SELECT transaction_id
          FROM mart.sales
          GROUP BY transaction_id
          HAVING COUNT(*) > 1
        ) x
      `,
                threshold: 0,
                severity: 'error',
            },
            {
                name: 'invalid_quantity',
                description: 'Check for invalid quantity values (<= 0)',
                query: `
        SELECT COUNT(*) FROM mart.sales WHERE quantity <= 0
      `,
                threshold: 0,
                severity: 'error',
            },
            {
                name: 'invalid_price',
                description: 'Check for negative unit prices',
                query: `
        SELECT COUNT(*) FROM mart.sales WHERE unit_price < 0
      `,
                threshold: 0,
                severity: 'error',
            },
            {
                name: 'null_customer',
                description: 'Check for null customer IDs',
                query: `
        SELECT COUNT(*) FROM mart.sales WHERE customer_id IS NULL
      `,
                threshold: 0,
                severity: 'warning',
            },
            {
                name: 'null_product',
                description: 'Check for null product IDs',
                query: `
        SELECT COUNT(*) FROM mart.sales WHERE product_id IS NULL
      `,
                threshold: 0,
                severity: 'warning',
            },
            {
                name: 'negative_total_amount',
                description: 'Check for negative total amounts',
                query: `
        SELECT COUNT(*) FROM mart.sales WHERE total_amount < 0
      `,
                threshold: 0,
                severity: 'error',
            },
            {
                name: 'raw_staging_row_count_match',
                description: 'Verify row count matches between raw and staging',
                query: `
        SELECT 
          (SELECT COUNT(*) FROM raw.sales) as raw_count,
          (SELECT COUNT(*) FROM staging.sales) as staging_count
      `,
                threshold: 0,
                severity: 'warning',
            },
            {
                name: 'staging_mart_row_count_match',
                description: 'Verify row count matches between staging and mart',
                query: `
        SELECT 
          (SELECT COUNT(*) FROM staging.sales) as staging_count,
          (SELECT COUNT(*) FROM mart.sales) as mart_count
      `,
                threshold: 0,
                severity: 'warning',
            },
            {
                name: 'future_dates',
                description: 'Check for future transaction dates',
                query: `
        SELECT COUNT(*) FROM mart.sales WHERE transaction_date > CURRENT_DATE
      `,
                threshold: 0,
                severity: 'warning',
            },
            {
                name: 'zero_amount_transactions',
                description: 'Check for transactions with zero amount',
                query: `
        SELECT COUNT(*) FROM mart.sales WHERE total_amount = 0
      `,
                threshold: 0,
                severity: 'info',
            },
        ];
    }
    async runAllChecks() {
        const results = [];
        for (const check of this.checks) {
            try {
                const result = await this.runCheck(check);
                results.push(result);
            }
            catch (error) {
                results.push({
                    check,
                    value: -1,
                    passed: false,
                    timestamp: new Date(),
                    details: { error: error.message },
                });
            }
        }
        return results;
    }
    async runCheck(check) {
        const result = await this.martSaleRepo.manager.query(check.query);
        let value;
        if (check.name.includes('row_count_match')) {
            const row = result[0];
            value = Math.abs((row.raw_count || row.staging_count) - (row.staging_count || row.mart_count));
        }
        else {
            value = parseInt(result[0]?.count || result[0]?.['?column?'] || '0', 10);
        }
        const passed = value <= check.threshold;
        return {
            check,
            value,
            passed,
            timestamp: new Date(),
            details: result,
        };
    }
    async runChecksByLayer() {
        const results = await this.runAllChecks();
        const byLayer = {
            raw: [],
            staging: [],
            mart: [],
            cross_layer: [],
        };
        for (const result of results) {
            if (result.check.name.includes('raw_staging') || result.check.name.includes('staging_mart')) {
                byLayer.cross_layer.push(result);
            }
            else if (result.check.name.includes('raw')) {
                byLayer.raw.push(result);
            }
            else if (result.check.name.includes('staging')) {
                byLayer.staging.push(result);
            }
            else {
                byLayer.mart.push(result);
            }
        }
        return byLayer;
    }
    async getSummary() {
        const results = await this.runAllChecks();
        const byLayer = await this.runChecksByLayer();
        const layerSummary = {};
        for (const [layer, checks] of Object.entries(byLayer)) {
            layerSummary[layer] = {
                passed: checks.filter(c => c.passed).length,
                failed: checks.filter(c => !c.passed).length,
            };
        }
        return {
            total: results.length,
            passed: results.filter(r => r.passed).length,
            failed: results.filter(r => !r.passed).length,
            warnings: results.filter(r => !r.passed && r.check.severity === 'warning').length,
            errors: results.filter(r => !r.passed && r.check.severity === 'error').length,
            byLayer: layerSummary,
        };
    }
    getChecks() {
        return this.checks;
    }
    addCustomCheck(check) {
        this.checks.push(check);
    }
    removeCheck(name) {
        this.checks = this.checks.filter(c => c.name !== name);
    }
};
exports.QualityService = QualityService;
exports.QualityService = QualityService = __decorate([
    (0, common_1.Injectable)(),
    __param(0, (0, typeorm_1.InjectRepository)(mart_sale_entity_1.MartSale)),
    __param(1, (0, typeorm_1.InjectRepository)(staging_sale_entity_1.StagingSale)),
    __param(2, (0, typeorm_1.InjectRepository)(raw_sale_entity_1.RawSale)),
    __metadata("design:paramtypes", [typeorm_2.Repository,
        typeorm_2.Repository,
        typeorm_2.Repository])
], QualityService);
//# sourceMappingURL=quality.service.js.map