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
export declare class QualityService {
    private martSaleRepo;
    private stagingSaleRepo;
    private rawSaleRepo;
    private checks;
    constructor(martSaleRepo: Repository<MartSale>, stagingSaleRepo: Repository<StagingSale>, rawSaleRepo: Repository<RawSale>);
    runAllChecks(): Promise<QualityResult[]>;
    runCheck(check: QualityCheck): Promise<QualityResult>;
    runChecksByLayer(): Promise<Record<string, QualityResult[]>>;
    getSummary(): Promise<{
        total: number;
        passed: number;
        failed: number;
        warnings: number;
        errors: number;
        byLayer: Record<string, {
            passed: number;
            failed: number;
        }>;
    }>;
    getChecks(): QualityCheck[];
    addCustomCheck(check: QualityCheck): void;
    removeCheck(name: string): void;
}
