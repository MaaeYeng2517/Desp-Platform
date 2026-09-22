import { PipelineService } from './pipeline.service';
import { AirflowService, DagRun } from './airflow.service';
import { KafkaService, ProduceMessage, KafkaTopic } from './kafka.service';
import { SparkService, SparkJob, SparkConfig } from './spark.service';
import { DockerService, DockerComposeProject } from './docker.service';
export declare class PipelineController {
    private readonly pipelineService;
    private readonly airflowService;
    private readonly kafkaService;
    private readonly sparkService;
    private readonly dockerService;
    constructor(pipelineService: PipelineService, airflowService: AirflowService, kafkaService: KafkaService, sparkService: SparkService, dockerService: DockerService);
    getDockerProjects(): Promise<DockerComposeProject[]>;
    getDockerProject(projectName: string): Promise<DockerComposeProject | null>;
    startDockerProject(projectName: string): Promise<{
        success: boolean;
        output: string;
    }>;
    stopDockerProject(projectName: string): Promise<{
        success: boolean;
        output: string;
    }>;
    restartDockerProject(projectName: string): Promise<{
        success: boolean;
        output: string;
    }>;
    getAllContainers(): Promise<import("./docker.service").DockerContainer[]>;
    getContainerLogs(containerId: string, tail: number): Promise<{
        logs: string;
    }>;
    getAirflowHealth(): Promise<{
        metadatabase: {
            status: string;
        };
        scheduler: {
            status: string;
        };
    }>;
    getAirflowDags(): Promise<import("./airflow.service").Dag[]>;
    getAirflowDag(dagId: string): Promise<import("./airflow.service").Dag>;
    getDagRuns(dagId: string, limit: number): Promise<DagRun[]>;
    triggerDag(dagId: string, body: {
        conf?: Record<string, any>;
    }): Promise<DagRun>;
    getDagRun(dagId: string, runId: string): Promise<DagRun>;
    getTaskInstances(dagId: string, runId: string): Promise<import("./airflow.service").TaskInstance[]>;
    pauseDag(dagId: string): Promise<{
        success: boolean;
    }>;
    unpauseDag(dagId: string): Promise<{
        success: boolean;
    }>;
    clearTaskInstances(dagId: string, runId: string, body: {
        task_ids?: string[];
    }): Promise<{
        success: boolean;
    }>;
    getDagDetails(dagId: string): Promise<{
        tasks: any[];
        edges: any[];
    }>;
    getKafkaTopics(): Promise<string[]>;
    createKafkaTopic(topic: KafkaTopic): Promise<{
        success: boolean;
    }>;
    produceToKafka(message: ProduceMessage): Promise<{
        success: boolean;
    }>;
    getConsumerLag(groupId: string, topic: string): Promise<{
        groupId: string;
        topic: string;
        lag: number;
    }>;
    getClusterInfo(): Promise<{
        brokers: any[];
        controller: any;
    }>;
    getSparkConfig(): Promise<SparkConfig>;
    updateSparkConfig(config: Partial<SparkConfig>): Promise<{
        success: boolean;
        config: SparkConfig;
    }>;
    submitSparkJob(job: Omit<SparkJob, 'id' | 'status' | 'submitTime'>): Promise<SparkJob>;
    listSparkJobs(): Promise<SparkJob[]>;
    getSparkJob(jobId: string): Promise<SparkJob | null>;
    killSparkJob(jobId: string): Promise<{
        success: boolean;
    }>;
    getSparkApplications(): Promise<any[]>;
    getSparkUI(): Promise<{
        url: string;
    }>;
}
