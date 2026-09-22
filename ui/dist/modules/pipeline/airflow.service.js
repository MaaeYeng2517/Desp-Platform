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
exports.AirflowService = void 0;
const common_1 = require("@nestjs/common");
const config_1 = require("@nestjs/config");
const axios_1 = require("@nestjs/axios");
const rxjs_1 = require("rxjs");
let AirflowService = class AirflowService {
    constructor(configService, httpService) {
        this.configService = configService;
        this.httpService = httpService;
        this.baseUrl = this.configService.get('airflowUrl') || 'http://localhost:8080';
        this.auth = {
            username: this.configService.get('airflowUser') || 'airflow',
            password: this.configService.get('airflowPassword') || 'airflow',
        };
    }
    async request(method, endpoint, data) {
        try {
            const response = await (0, rxjs_1.firstValueFrom)(this.httpService.request({
                method,
                url: `${this.baseUrl}/api/v1${endpoint}`,
                data,
                auth: this.auth,
                headers: {
                    'Content-Type': 'application/json',
                },
            }));
            return response.data;
        }
        catch (error) {
            const axiosError = error;
            throw new Error(`Airflow API error: ${axiosError.response?.data || axiosError.message}`);
        }
    }
    async getDags() {
        const response = await this.request('GET', '/dags');
        return response.dags;
    }
    async getDag(dagId) {
        return this.request('GET', `/dags/${dagId}`);
    }
    async triggerDag(dagId, conf) {
        return this.request('POST', `/dags/${dagId}/dagRuns`, { conf });
    }
    async getDagRuns(dagId, limit = 10) {
        const response = await this.request('GET', `/dags/${dagId}/dagRuns?limit=${limit}&order_by=-execution_date`);
        return response.dag_runs;
    }
    async getDagRun(dagId, runId) {
        return this.request('GET', `/dags/${dagId}/dagRuns/${runId}`);
    }
    async getTaskInstances(dagId, runId) {
        const response = await this.request('GET', `/dags/${dagId}/dagRuns/${runId}/taskInstances`);
        return response.task_instances;
    }
    async pauseDag(dagId) {
        await this.request('PATCH', `/dags/${dagId}`, { is_paused: true });
    }
    async unpauseDag(dagId) {
        await this.request('PATCH', `/dags/${dagId}`, { is_paused: false });
    }
    async clearTaskInstances(dagId, runId, taskIds) {
        await this.request('POST', `/dags/${dagId}/dagRuns/${runId}/clearTaskInstances`, {
            task_ids: taskIds,
            dry_run: false,
        });
    }
    async getDagDetails(dagId) {
        const response = await this.request('GET', `/dags/${dagId}/details`);
        return response;
    }
    async getHealth() {
        return this.request('GET', '/health');
    }
};
exports.AirflowService = AirflowService;
exports.AirflowService = AirflowService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [config_1.ConfigService,
        axios_1.HttpService])
], AirflowService);
//# sourceMappingURL=airflow.service.js.map