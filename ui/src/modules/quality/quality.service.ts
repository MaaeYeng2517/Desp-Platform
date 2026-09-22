import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { MartSale } from '../../entities/mart-sale.entity';
import { StagingSale } from '../../entities/staging-sale.entity';
import { RawSale } from '../../entities/raw-sale.entity';

export interface QualityCheck {
  name: string;
  description: string;
  query: string;
  threshold: number;
  severity: 'error' | 'warning' | 'info';
}

export interface QualityResult {
  check: QualityCheck;
  value: number;
  passed: boolean;
  timestamp: Date;
  details?: any;
}

@Injectable()
export class QualityService {
  private checks: QualityCheck[] = [
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

  constructor(
    @InjectRepository(MartSale)
    private martSaleRepo: Repository<MartSale>,
    @InjectRepository(StagingSale)
    private stagingSaleRepo: Repository<StagingSale>,
    @InjectRepository(RawSale)
    private rawSaleRepo: Repository<RawSale>,
  ) {}

  async runAllChecks(): Promise<QualityResult[]> {
    const results: QualityResult[] = [];

    for (const check of this.checks) {
      try {
        const result = await this.runCheck(check);
        results.push(result);
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        results.push({
          check,
          value: -1,
          passed: false,
          timestamp: new Date(),
          details: { error: message },
        });
      }
    }

    return results;
  }

  async runCheck(check: QualityCheck): Promise<QualityResult> {
    const result = await this.martSaleRepo.manager.query(check.query);
    let value: number;

    if (check.name.includes('row_count_match')) {
      // Special handling for row count comparison
      const row = result[0];
      value = Math.abs((row.raw_count || row.staging_count) - (row.staging_count || row.mart_count));
    } else {
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

  async runChecksByLayer(): Promise<Record<string, QualityResult[]>> {
    const results = await this.runAllChecks();
    const byLayer: Record<string, QualityResult[]> = {
      raw: [],
      staging: [],
      mart: [],
      cross_layer: [],
    };

    for (const result of results) {
      if (result.check.name.includes('raw_staging') || result.check.name.includes('staging_mart')) {
        byLayer.cross_layer.push(result);
      } else if (result.check.name.includes('raw')) {
        byLayer.raw.push(result);
      } else if (result.check.name.includes('staging')) {
        byLayer.staging.push(result);
      } else {
        byLayer.mart.push(result);
      }
    }

    return byLayer;
  }

  async getSummary(): Promise<{
    total: number;
    passed: number;
    failed: number;
    warnings: number;
    errors: number;
    byLayer: Record<string, { passed: number; failed: number }>;
  }> {
    const results = await this.runAllChecks();
    
    const byLayer = await this.runChecksByLayer();
    const layerSummary: Record<string, { passed: number; failed: number }> = {};
    
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

  getChecks(): QualityCheck[] {
    return this.checks;
  }

  addCustomCheck(check: QualityCheck): void {
    this.checks.push(check);
  }

  removeCheck(name: string): void {
    this.checks = this.checks.filter(c => c.name !== name);
  }
}