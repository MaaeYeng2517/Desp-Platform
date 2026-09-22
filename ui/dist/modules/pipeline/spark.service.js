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
Object.defineProperty(exports, "__esModule", { value: true });
exports.SparkService = void 0;
const common_1 = require("@nestjs/common");
const config_1 = require("@nestjs/config");
const child_process_1 = require("child_process");
const util_1 = require("util");
const execAsync = (0, util_1.promisify)(child_process_1.exec);
let SparkService = class SparkService {
    constructor(configService) {
        this.configService = configService;
        this.jobs = new Map();
        this.sparkMaster = this.configService.get('SPARK_MASTER') || 'spark://localhost:7077';
        this.defaultConfig = {
            master: this.sparkMaster,
            deployMode: 'client',
            executorMemory: this.configService.get('SPARK_EXECUTOR_MEMORY') || '2g',
            executorCores: parseInt(this.configService.get('SPARK_EXECUTOR_CORES') || '2', 10),
            numExecutors: parseInt(this.configService.get('SPARK_NUM_EXECUTORS') || '2', 10),
            driverMemory: this.configService.get('SPARK_DRIVER_MEMORY') || '1g',
        };
    }
    async submitJob(job) {
        const id = `spark-job-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const sparkJob = {
            ...job,
            id,
            status: 'pending',
            submitTime: new Date(),
        };
        this.jobs.set(id, sparkJob);
        try {
            sparkJob.status = 'running';
            const args = this.buildSparkSubmitArgs(job, this.defaultConfig);
            const command = `spark-submit ${args.join(' ')}`;
            const child = (0, child_process_1.spawn)('spark-submit', args, {
                detached: true,
                stdio: ['ignore', 'pipe', 'pipe'],
            });
            let stdout = '';
            let stderr = '';
            child.stdout?.on('data', (data) => {
                stdout += data.toString();
            });
            child.stderr?.on('data', (data) => {
                stderr += data.toString();
            });
            child.on('close', (code) => {
                sparkJob.status = code === 0 ? 'completed' : 'failed';
                sparkJob.completionTime = new Date();
                console.log(`Spark job ${id} ${sparkJob.status}: ${stdout || stderr}`);
            });
            child.unref();
            return sparkJob;
        }
        catch (error) {
            sparkJob.status = 'failed';
            sparkJob.completionTime = new Date();
            throw error;
        }
    }
    buildSparkSubmitArgs(job, config) {
        const args = [
            '--master', config.master,
            '--deploy-mode', config.deployMode,
            '--executor-memory', config.executorMemory,
            '--executor-cores', config.executorCores.toString(),
            '--num-executors', config.numExecutors.toString(),
            '--driver-memory', config.driverMemory,
        ];
        if (job.mainClass) {
            args.push('--class', job.mainClass);
        }
        if (job.sparkConf) {
            for (const [key, value] of Object.entries(job.sparkConf)) {
                args.push('--conf', `${key}=${value}`);
            }
        }
        args.push(job.appResource);
        if (job.arguments && job.arguments.length > 0) {
            args.push(...job.arguments);
        }
        return args;
    }
    async getJobStatus(jobId) {
        return this.jobs.get(jobId) || null;
    }
    async listJobs() {
        return Array.from(this.jobs.values());
    }
    async killJob(jobId) {
        const job = this.jobs.get(jobId);
        if (!job)
            return false;
        try {
            job.status = 'failed';
            job.completionTime = new Date();
            return true;
        }
        catch {
            return false;
        }
    }
    async getSparkMasterUI() {
        const masterHost = this.sparkMaster.replace('spark://', '').split(':')[0];
        return `http://${masterHost}:4040`;
    }
    async getApplications() {
        try {
            const masterHost = this.sparkMaster.replace('spark://', '').split(':')[0];
            const { stdout } = await execAsync(`curl -s http://${masterHost}:4040/api/v1/applications`);
            return JSON.parse(stdout);
        }
        catch {
            return [];
        }
    }
    getDefaultConfig() {
        return { ...this.defaultConfig };
    }
    updateConfig(config) {
        this.defaultConfig = { ...this.defaultConfig, ...config };
    }
};
exports.SparkService = SparkService;
exports.SparkService = SparkService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [config_1.ConfigService])
], SparkService);
//# sourceMappingURL=spark.service.js.map