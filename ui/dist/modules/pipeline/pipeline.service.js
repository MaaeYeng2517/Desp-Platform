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
exports.PipelineService = void 0;
const common_1 = require("@nestjs/common");
const schedule_1 = require("@nestjs/schedule");
const airflow_service_1 = require("./airflow.service");
const docker_service_1 = require("./docker.service");
let PipelineService = class PipelineService {
    constructor(airflowService, dockerService) {
        this.airflowService = airflowService;
        this.dockerService = dockerService;
    }
    async monitorPipelines() {
        try {
            const health = await this.airflowService.getHealth();
            if (health.metadatabase?.status !== 'healthy' || health.scheduler?.status !== 'healthy') {
                console.warn('Airflow health check failed:', health);
            }
        }
        catch (error) {
            console.error('Pipeline monitoring error:', error);
        }
    }
    async getPipelineOverview() {
        try {
            const [airflowHealth, dockerProjects] = await Promise.all([
                this.airflowService.getHealth().catch(() => null),
                this.dockerService.getProjects().catch(() => []),
            ]);
            const dagRuns = await this.airflowService.getDags().catch(() => []);
            return {
                airflow: {
                    healthy: airflowHealth?.metadatabase?.status === 'healthy' &&
                        airflowHealth?.scheduler?.status === 'healthy',
                    health: airflowHealth,
                    activeDags: dagRuns.filter(d => d.is_active && !d.is_paused).length,
                    totalDags: dagRuns.length,
                },
                docker: {
                    projects: dockerProjects.length,
                    running: dockerProjects.filter(p => p.status === 'running').length,
                    stopped: dockerProjects.filter(p => p.status === 'stopped').length,
                    partial: dockerProjects.filter(p => p.status === 'partial').length,
                },
            };
        }
        catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            return { error: message };
        }
    }
    async triggerPipeline(dagId, conf) {
        return this.airflowService.triggerDag(dagId, conf);
    }
    async getPipelineStatus(dagId) {
        const [dag, runs] = await Promise.all([
            this.airflowService.getDag(dagId),
            this.airflowService.getDagRuns(dagId, 1),
        ]);
        const latestRun = runs[0];
        let tasks = [];
        if (latestRun) {
            tasks = await this.airflowService.getTaskInstances(dagId, latestRun.run_id);
        }
        return { dag, latestRun, tasks };
    }
};
exports.PipelineService = PipelineService;
__decorate([
    (0, schedule_1.Cron)(schedule_1.CronExpression.EVERY_5_MINUTES),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], PipelineService.prototype, "monitorPipelines", null);
exports.PipelineService = PipelineService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [airflow_service_1.AirflowService,
        docker_service_1.DockerService])
], PipelineService);
//# sourceMappingURL=pipeline.service.js.map