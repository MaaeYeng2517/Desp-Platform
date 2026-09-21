import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  Query,
  ParseIntPipe,
  DefaultValuePipe,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiQuery, ApiBody } from '@nestjs/swagger';
import { PipelineService } from './pipeline.service';
import { AirflowService, DagRun } from './airflow.service';
import { KafkaService, ProduceMessage, KafkaTopic } from './kafka.service';
import { SparkService, SparkJob, SparkConfig } from './spark.service';
import { DockerService, DockerComposeProject } from './docker.service';

@ApiTags('Pipeline Management')
@Controller('pipeline')
export class PipelineController {
  constructor(
    private readonly pipelineService: PipelineService,
    private readonly airflowService: AirflowService,
    private readonly kafkaService: KafkaService,
    private readonly sparkService: SparkService,
    private readonly dockerService: DockerService,
  ) {}

  // Docker Compose endpoints
  @Get('docker/projects')
  @ApiOperation({ summary: 'List all Docker Compose projects' })
  async getDockerProjects(): Promise<DockerComposeProject[]> {
    return this.dockerService.getProjects();
  }

  @Get('docker/projects/:projectName')
  @ApiOperation({ summary: 'Get Docker Compose project status' })
  async getDockerProject(@Param('projectName') projectName: string) {
    return this.dockerService.getProjectStatus(projectName);
  }

  @Post('docker/projects/:projectName/start')
  @ApiOperation({ summary: 'Start Docker Compose project' })
  async startDockerProject(@Param('projectName') projectName: string) {
    return this.dockerService.startProject(projectName);
  }

  @Post('docker/projects/:projectName/stop')
  @ApiOperation({ summary: 'Stop Docker Compose project' })
  async stopDockerProject(@Param('projectName') projectName: string) {
    return this.dockerService.stopProject(projectName);
  }

  @Post('docker/projects/:projectName/restart')
  @ApiOperation({ summary: 'Restart Docker Compose project' })
  async restartDockerProject(@Param('projectName') projectName: string) {
    return this.dockerService.restartProject(projectName);
  }

  @Get('docker/containers')
  @ApiOperation({ summary: 'List all Docker containers' })
  async getAllContainers() {
    return this.dockerService.getAllContainers();
  }

  @Get('docker/containers/:containerId/logs')
  @ApiOperation({ summary: 'Get container logs' })
  @ApiQuery({ name: 'tail', required: false, type: Number })
  async getContainerLogs(
    @Param('containerId') containerId: string,
    @Query('tail', new DefaultValuePipe(100), ParseIntPipe) tail: number,
  ) {
    return { logs: await this.dockerService.getContainerLogs(containerId, tail) };
  }

  // Airflow endpoints
  @Get('airflow/health')
  @ApiOperation({ summary: 'Check Airflow health' })
  async getAirflowHealth() {
    return this.airflowService.getHealth();
  }

  @Get('airflow/dags')
  @ApiOperation({ summary: 'List all Airflow DAGs' })
  async getAirflowDags() {
    return this.airflowService.getDags();
  }

  @Get('airflow/dags/:dagId')
  @ApiOperation({ summary: 'Get Airflow DAG details' })
  async getAirflowDag(@Param('dagId') dagId: string) {
    return this.airflowService.getDag(dagId);
  }

  @Get('airflow/dags/:dagId/runs')
  @ApiOperation({ summary: 'Get DAG runs' })
  @ApiQuery({ name: 'limit', required: false, type: Number })
  async getDagRuns(
    @Param('dagId') dagId: string,
    @Query('limit', new DefaultValuePipe(10), ParseIntPipe) limit: number,
  ) {
    return this.airflowService.getDagRuns(dagId, limit);
  }

  @Post('airflow/dags/:dagId/trigger')
  @ApiOperation({ summary: 'Trigger a DAG run' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        conf: { type: 'object' },
      },
    },
  })
  async triggerDag(
    @Param('dagId') dagId: string,
    @Body() body: { conf?: Record<string, any> },
  ): Promise<DagRun> {
    return this.airflowService.triggerDag(dagId, body.conf);
  }

  @Get('airflow/dags/:dagId/runs/:runId')
  @ApiOperation({ summary: 'Get specific DAG run' })
  async getDagRun(
    @Param('dagId') dagId: string,
    @Param('runId') runId: string,
  ) {
    return this.airflowService.getDagRun(dagId, runId);
  }

  @Get('airflow/dags/:dagId/runs/:runId/tasks')
  @ApiOperation({ summary: 'Get task instances for a DAG run' })
  async getTaskInstances(
    @Param('dagId') dagId: string,
    @Param('runId') runId: string,
  ) {
    return this.airflowService.getTaskInstances(dagId, runId);
  }

  @Post('airflow/dags/:dagId/pause')
  @ApiOperation({ summary: 'Pause a DAG' })
  async pauseDag(@Param('dagId') dagId: string) {
    await this.airflowService.pauseDag(dagId);
    return { success: true };
  }

  @Post('airflow/dags/:dagId/unpause')
  @ApiOperation({ summary: 'Unpause a DAG' })
  async unpauseDag(@Param('dagId') dagId: string) {
    await this.airflowService.unpauseDag(dagId);
    return { success: true };
  }

  @Post('airflow/dags/:dagId/runs/:runId/clear')
  @ApiOperation({ summary: 'Clear task instances for retry' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        task_ids: { type: 'array', items: { type: 'string' } },
      },
    },
  })
  async clearTaskInstances(
    @Param('dagId') dagId: string,
    @Param('runId') runId: string,
    @Body() body: { task_ids?: string[] },
  ) {
    await this.airflowService.clearTaskInstances(dagId, runId, body.task_ids);
    return { success: true };
  }

  @Get('airflow/dags/:dagId/details')
  @ApiOperation({ summary: 'Get DAG structure (tasks and edges)' })
  async getDagDetails(@Param('dagId') dagId: string) {
    return this.airflowService.getDagDetails(dagId);
  }

  // Kafka endpoints
  @Get('kafka/topics')
  @ApiOperation({ summary: 'List Kafka topics' })
  async getKafkaTopics() {
    return this.kafkaService.listTopics();
  }

  @Post('kafka/topics')
  @ApiOperation({ summary: 'Create Kafka topic' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        name: { type: 'string' },
        partitions: { type: 'number', default: 3 },
        replicationFactor: { type: 'number', default: 1 },
      },
      required: ['name'],
    },
  })
  async createKafkaTopic(@Body() topic: KafkaTopic) {
    await this.kafkaService.createTopic(topic);
    return { success: true };
  }

  @Post('kafka/produce')
  @ApiOperation({ summary: 'Produce message to Kafka topic' })
  @ApiBody({
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
  })
  async produceToKafka(@Body() message: ProduceMessage) {
    await this.kafkaService.produce(message);
    return { success: true };
  }

  @Get('kafka/consumer-lag')
  @ApiOperation({ summary: 'Get consumer lag' })
  @ApiQuery({ name: 'groupId', required: true, type: String })
  @ApiQuery({ name: 'topic', required: true, type: String })
  async getConsumerLag(
    @Query('groupId') groupId: string,
    @Query('topic') topic: string,
  ) {
    const lag = await this.kafkaService.getConsumerLag(groupId, topic);
    return { groupId, topic, lag };
  }

  @Get('kafka/cluster')
  @ApiOperation({ summary: 'Get Kafka cluster info' })
  async getClusterInfo() {
    return this.kafkaService.getClusterInfo();
  }

  // Spark endpoints
  @Get('spark/config')
  @ApiOperation({ summary: 'Get Spark default configuration' })
  async getSparkConfig(): Promise<SparkConfig> {
    return this.sparkService.getDefaultConfig();
  }

  @Post('spark/config')
  @ApiOperation({ summary: 'Update Spark default configuration' })
  async updateSparkConfig(@Body() config: Partial<SparkConfig>) {
    this.sparkService.updateConfig(config);
    return { success: true, config: this.sparkService.getDefaultConfig() };
  }

  @Post('spark/jobs')
  @ApiOperation({ summary: 'Submit Spark job' })
  @ApiBody({
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
  })
  async submitSparkJob(@Body() job: Omit<SparkJob, 'id' | 'status' | 'submitTime'>): Promise<SparkJob> {
    return this.sparkService.submitJob(job);
  }

  @Get('spark/jobs')
  @ApiOperation({ summary: 'List Spark jobs' })
  async listSparkJobs() {
    return this.sparkService.listJobs();
  }

  @Get('spark/jobs/:jobId')
  @ApiOperation({ summary: 'Get Spark job status' })
  async getSparkJob(@Param('jobId') jobId: string) {
    return this.sparkService.getJobStatus(jobId);
  }

  @Post('spark/jobs/:jobId/kill')
  @ApiOperation({ summary: 'Kill Spark job' })
  async killSparkJob(@Param('jobId') jobId: string) {
    const success = await this.sparkService.killJob(jobId);
    return { success };
  }

  @Get('spark/applications')
  @ApiOperation({ summary: 'List Spark applications from master UI' })
  async getSparkApplications() {
    return this.sparkService.getApplications();
  }

  @Get('spark/ui')
  @ApiOperation({ summary: 'Get Spark Master UI URL' })
  async getSparkUI() {
    return { url: await this.sparkService.getSparkMasterUI() };
  }
}