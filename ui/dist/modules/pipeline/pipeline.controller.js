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
exports.PipelineController = void 0;
const common_1 = require("@nestjs/common");
const swagger_1 = require("@nestjs/swagger");
const pipeline_service_1 = require("./pipeline.service");
const airflow_service_1 = require("./airflow.service");
const kafka_service_1 = require("./kafka.service");
const spark_service_1 = require("./spark.service");
const docker_service_1 = require("./docker.service");
let PipelineController = class PipelineController {
    constructor(pipelineService, airflowService, kafkaService, sparkService, dockerService) {
        this.pipelineService = pipelineService;
        this.airflowService = airflowService;
        this.kafkaService = kafkaService;
        this.sparkService = sparkService;
        this.dockerService = dockerService;
    }
    async getDockerProjects() {
        return this.dockerService.getProjects();
    }
    async getDockerProject(projectName) {
        return this.dockerService.getProjectStatus(projectName);
    }
    async startDockerProject(projectName) {
        return this.dockerService.startProject(projectName);
    }
    async stopDockerProject(projectName) {
        return this.dockerService.stopProject(projectName);
    }
    async restartDockerProject(projectName) {
        return this.dockerService.restartProject(projectName);
    }
    async getAllContainers() {
        return this.dockerService.getAllContainers();
    }
    async getContainerLogs(containerId, tail) {
        return { logs: await this.dockerService.getContainerLogs(containerId, tail) };
    }
    async getAirflowHealth() {
        return this.airflowService.getHealth();
    }
    async getAirflowDags() {
        return this.airflowService.getDags();
    }
    async getAirflowDag(dagId) {
        return this.airflowService.getDag(dagId);
    }
    async getDagRuns(dagId, limit) {
        return this.airflowService.getDagRuns(dagId, limit);
    }
    async triggerDag(dagId, body) {
        return this.airflowService.triggerDag(dagId, body.conf);
    }
    async getDagRun(dagId, runId) {
        return this.airflowService.getDagRun(dagId, runId);
    }
    async getTaskInstances(dagId, runId) {
        return this.airflowService.getTaskInstances(dagId, runId);
    }
    async pauseDag(dagId) {
        await this.airflowService.pauseDag(dagId);
        return { success: true };
    }
    async unpauseDag(dagId) {
        await this.airflowService.unpauseDag(dagId);
        return { success: true };
    }
    async clearTaskInstances(dagId, runId, body) {
        await this.airflowService.clearTaskInstances(dagId, runId, body.task_ids);
        return { success: true };
    }
    async getDagDetails(dagId) {
        return this.airflowService.getDagDetails(dagId);
    }
    async getKafkaTopics() {
        return this.kafkaService.listTopics();
    }
    async createKafkaTopic(topic) {
        await this.kafkaService.createTopic(topic);
        return { success: true };
    }
    async produceToKafka(message) {
        await this.kafkaService.produce(message);
        return { success: true };
    }
    async getConsumerLag(groupId, topic) {
        const lag = await this.kafkaService.getConsumerLag(groupId, topic);
        return { groupId, topic, lag };
    }
    async getClusterInfo() {
        return this.kafkaService.getClusterInfo();
    }
    async getSparkConfig() {
        return this.sparkService.getDefaultConfig();
    }
    async updateSparkConfig(config) {
        this.sparkService.updateConfig(config);
        return { success: true, config: this.sparkService.getDefaultConfig() };
    }
    async submitSparkJob(job) {
        return this.sparkService.submitJob(job);
    }
    async listSparkJobs() {
        return this.sparkService.listJobs();
    }
    async getSparkJob(jobId) {
        return this.sparkService.getJobStatus(jobId);
    }
    async killSparkJob(jobId) {
        const success = await this.sparkService.killJob(jobId);
        return { success };
    }
    async getSparkApplications() {
        return this.sparkService.getApplications();
    }
    async getSparkUI() {
        return { url: await this.sparkService.getSparkMasterUI() };
    }
};
exports.PipelineController = PipelineController;
__decorate([
    (0, common_1.Get)('docker/projects'),
    (0, swagger_1.ApiOperation)({ summary: 'List all Docker Compose projects' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getDockerProjects", null);
__decorate([
    (0, common_1.Get)('docker/projects/:projectName'),
    (0, swagger_1.ApiOperation)({ summary: 'Get Docker Compose project status' }),
    __param(0, (0, common_1.Param)('projectName')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getDockerProject", null);
__decorate([
    (0, common_1.Post)('docker/projects/:projectName/start'),
    (0, swagger_1.ApiOperation)({ summary: 'Start Docker Compose project' }),
    __param(0, (0, common_1.Param)('projectName')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "startDockerProject", null);
__decorate([
    (0, common_1.Post)('docker/projects/:projectName/stop'),
    (0, swagger_1.ApiOperation)({ summary: 'Stop Docker Compose project' }),
    __param(0, (0, common_1.Param)('projectName')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "stopDockerProject", null);
__decorate([
    (0, common_1.Post)('docker/projects/:projectName/restart'),
    (0, swagger_1.ApiOperation)({ summary: 'Restart Docker Compose project' }),
    __param(0, (0, common_1.Param)('projectName')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "restartDockerProject", null);
__decorate([
    (0, common_1.Get)('docker/containers'),
    (0, swagger_1.ApiOperation)({ summary: 'List all Docker containers' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getAllContainers", null);
__decorate([
    (0, common_1.Get)('docker/containers/:containerId/logs'),
    (0, swagger_1.ApiOperation)({ summary: 'Get container logs' }),
    (0, swagger_1.ApiQuery)({ name: 'tail', required: false, type: Number }),
    __param(0, (0, common_1.Param)('containerId')),
    __param(1, (0, common_1.Query)('tail', new common_1.DefaultValuePipe(100), common_1.ParseIntPipe)),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, Number]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getContainerLogs", null);
__decorate([
    (0, common_1.Get)('airflow/health'),
    (0, swagger_1.ApiOperation)({ summary: 'Check Airflow health' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getAirflowHealth", null);
__decorate([
    (0, common_1.Get)('airflow/dags'),
    (0, swagger_1.ApiOperation)({ summary: 'List all Airflow DAGs' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getAirflowDags", null);
__decorate([
    (0, common_1.Get)('airflow/dags/:dagId'),
    (0, swagger_1.ApiOperation)({ summary: 'Get Airflow DAG details' }),
    __param(0, (0, common_1.Param)('dagId')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getAirflowDag", null);
__decorate([
    (0, common_1.Get)('airflow/dags/:dagId/runs'),
    (0, swagger_1.ApiOperation)({ summary: 'Get DAG runs' }),
    (0, swagger_1.ApiQuery)({ name: 'limit', required: false, type: Number }),
    __param(0, (0, common_1.Param)('dagId')),
    __param(1, (0, common_1.Query)('limit', new common_1.DefaultValuePipe(10), common_1.ParseIntPipe)),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, Number]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getDagRuns", null);
__decorate([
    (0, common_1.Post)('airflow/dags/:dagId/trigger'),
    (0, swagger_1.ApiOperation)({ summary: 'Trigger a DAG run' }),
    (0, swagger_1.ApiBody)({
        schema: {
            type: 'object',
            properties: {
                conf: { type: 'object' },
            },
        },
    }),
    __param(0, (0, common_1.Param)('dagId')),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, Object]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "triggerDag", null);
__decorate([
    (0, common_1.Get)('airflow/dags/:dagId/runs/:runId'),
    (0, swagger_1.ApiOperation)({ summary: 'Get specific DAG run' }),
    __param(0, (0, common_1.Param)('dagId')),
    __param(1, (0, common_1.Param)('runId')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, String]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getDagRun", null);
__decorate([
    (0, common_1.Get)('airflow/dags/:dagId/runs/:runId/tasks'),
    (0, swagger_1.ApiOperation)({ summary: 'Get task instances for a DAG run' }),
    __param(0, (0, common_1.Param)('dagId')),
    __param(1, (0, common_1.Param)('runId')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, String]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getTaskInstances", null);
__decorate([
    (0, common_1.Post)('airflow/dags/:dagId/pause'),
    (0, swagger_1.ApiOperation)({ summary: 'Pause a DAG' }),
    __param(0, (0, common_1.Param)('dagId')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "pauseDag", null);
__decorate([
    (0, common_1.Post)('airflow/dags/:dagId/unpause'),
    (0, swagger_1.ApiOperation)({ summary: 'Unpause a DAG' }),
    __param(0, (0, common_1.Param)('dagId')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "unpauseDag", null);
__decorate([
    (0, common_1.Post)('airflow/dags/:dagId/runs/:runId/clear'),
    (0, swagger_1.ApiOperation)({ summary: 'Clear task instances for retry' }),
    (0, swagger_1.ApiBody)({
        schema: {
            type: 'object',
            properties: {
                task_ids: { type: 'array', items: { type: 'string' } },
            },
        },
    }),
    __param(0, (0, common_1.Param)('dagId')),
    __param(1, (0, common_1.Param)('runId')),
    __param(2, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, String, Object]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "clearTaskInstances", null);
__decorate([
    (0, common_1.Get)('airflow/dags/:dagId/details'),
    (0, swagger_1.ApiOperation)({ summary: 'Get DAG structure (tasks and edges)' }),
    __param(0, (0, common_1.Param)('dagId')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getDagDetails", null);
__decorate([
    (0, common_1.Get)('kafka/topics'),
    (0, swagger_1.ApiOperation)({ summary: 'List Kafka topics' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getKafkaTopics", null);
__decorate([
    (0, common_1.Post)('kafka/topics'),
    (0, swagger_1.ApiOperation)({ summary: 'Create Kafka topic' }),
    (0, swagger_1.ApiBody)({
        schema: {
            type: 'object',
            properties: {
                name: { type: 'string' },
                partitions: { type: 'number', default: 3 },
                replicationFactor: { type: 'number', default: 1 },
            },
            required: ['name'],
        },
    }),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "createKafkaTopic", null);
__decorate([
    (0, common_1.Post)('kafka/produce'),
    (0, swagger_1.ApiOperation)({ summary: 'Produce message to Kafka topic' }),
    (0, swagger_1.ApiBody)({
        schema: {
            type: 'object',
            properties: {
                topic: { type: 'string' },
                messages: {
                    type: 'array',
                    items: {
                        type: 'object',
                        properties: {
                            key: { type: 'string' },
                            value: { type: 'string' },
                            headers: { type: 'object' },
                        },
                        required: ['value'],
                    },
                },
            },
            required: ['topic', 'messages'],
        },
    }),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "produceToKafka", null);
__decorate([
    (0, common_1.Get)('kafka/consumer-lag'),
    (0, swagger_1.ApiOperation)({ summary: 'Get consumer lag' }),
    (0, swagger_1.ApiQuery)({ name: 'groupId', required: true, type: String }),
    (0, swagger_1.ApiQuery)({ name: 'topic', required: true, type: String }),
    __param(0, (0, common_1.Query)('groupId')),
    __param(1, (0, common_1.Query)('topic')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, String]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getConsumerLag", null);
__decorate([
    (0, common_1.Get)('kafka/cluster'),
    (0, swagger_1.ApiOperation)({ summary: 'Get Kafka cluster info' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getClusterInfo", null);
__decorate([
    (0, common_1.Get)('spark/config'),
    (0, swagger_1.ApiOperation)({ summary: 'Get Spark default configuration' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getSparkConfig", null);
__decorate([
    (0, common_1.Post)('spark/config'),
    (0, swagger_1.ApiOperation)({ summary: 'Update Spark default configuration' }),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "updateSparkConfig", null);
__decorate([
    (0, common_1.Post)('spark/jobs'),
    (0, swagger_1.ApiOperation)({ summary: 'Submit Spark job' }),
    (0, swagger_1.ApiBody)({
        schema: {
            type: 'object',
            properties: {
                name: { type: 'string' },
                appResource: { type: 'string' },
                mainClass: { type: 'string' },
                arguments: { type: 'array', items: { type: 'string' } },
                sparkConf: { type: 'object' },
            },
            required: ['name', 'appResource'],
        },
    }),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "submitSparkJob", null);
__decorate([
    (0, common_1.Get)('spark/jobs'),
    (0, swagger_1.ApiOperation)({ summary: 'List Spark jobs' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "listSparkJobs", null);
__decorate([
    (0, common_1.Get)('spark/jobs/:jobId'),
    (0, swagger_1.ApiOperation)({ summary: 'Get Spark job status' }),
    __param(0, (0, common_1.Param)('jobId')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getSparkJob", null);
__decorate([
    (0, common_1.Post)('spark/jobs/:jobId/kill'),
    (0, swagger_1.ApiOperation)({ summary: 'Kill Spark job' }),
    __param(0, (0, common_1.Param)('jobId')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "killSparkJob", null);
__decorate([
    (0, common_1.Get)('spark/applications'),
    (0, swagger_1.ApiOperation)({ summary: 'List Spark applications from master UI' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getSparkApplications", null);
__decorate([
    (0, common_1.Get)('spark/ui'),
    (0, swagger_1.ApiOperation)({ summary: 'Get Spark Master UI URL' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], PipelineController.prototype, "getSparkUI", null);
exports.PipelineController = PipelineController = __decorate([
    (0, swagger_1.ApiTags)('Pipeline Management'),
    (0, common_1.Controller)('pipeline'),
    __metadata("design:paramtypes", [pipeline_service_1.PipelineService,
        airflow_service_1.AirflowService,
        kafka_service_1.KafkaService,
        spark_service_1.SparkService,
        docker_service_1.DockerService])
], PipelineController);
//# sourceMappingURL=pipeline.controller.js.map