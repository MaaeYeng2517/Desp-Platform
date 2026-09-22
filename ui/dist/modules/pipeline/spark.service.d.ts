import { ConfigService } from '@nestjs/config';
export interface SparkJob {
    id: string;
    name: string;
    appResource: string;
    mainClass?: string;
    arguments?: string[];
    sparkConf?: Record<string, string>;
    status: 'pending' | 'running' | 'completed' | 'failed';
    submitTime?: Date;
    completionTime?: Date;
    driverLogUrl?: string;
}
export interface SparkConfig {
    master: string;
    deployMode: 'cluster' | 'client';
    executorMemory: string;
    executorCores: number;
    numExecutors: number;
    driverMemory: string;
}
export declare class SparkService {
    private configService;
    private sparkMaster;
    private defaultConfig;
    private jobs;
    constructor(configService: ConfigService);
    submitJob(job: Omit<SparkJob, 'id' | 'status' | 'submitTime'>): Promise<SparkJob>;
    private buildSparkSubmitArgs;
    getJobStatus(jobId: string): Promise<SparkJob | null>;
    listJobs(): Promise<SparkJob[]>;
    killJob(jobId: string): Promise<boolean>;
    getSparkMasterUI(): Promise<string>;
    getApplications(): Promise<any[]>;
    getDefaultConfig(): SparkConfig;
    updateConfig(config: Partial<SparkConfig>): void;
}
