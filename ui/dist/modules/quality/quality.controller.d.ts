import { QualityService, QualityCheck, QualityResult } from './quality.service';
export declare class QualityController {
    private readonly qualityService;
    constructor(qualityService: QualityService);
    getChecks(): Promise<QualityCheck[]>;
    addCheck(check: QualityCheck): Promise<{
        success: boolean;
    }>;
    removeCheck(name: string): Promise<{
        success: boolean;
    }>;
    runAllChecks(): Promise<QualityResult[]>;
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
    runSingleCheck(name: string): Promise<QualityResult>;
}
