import { AirflowService } from './airflow.service';
import { DockerService } from './docker.service';
export declare class PipelineService {
    private readonly airflowService;
    private readonly dockerService;
    constructor(airflowService: AirflowService, dockerService: DockerService);
    monitorPipelines(): Promise<void>;
    getPipelineOverview(): Promise<{
        airflow: {
            healthy: boolean;
            health: {
                metadatabase: {
                    status: string;
                };
                scheduler: {
                    status: string;
                };
            } | null;
            activeDags: number;
            totalDags: number;
        };
        docker: {
            projects: number;
            running: number;
            stopped: number;
            partial: number;
        };
        error?: undefined;
    } | {
        error: string;
        airflow?: undefined;
        docker?: undefined;
    }>;
    triggerPipeline(dagId: string, conf?: Record<string, any>): Promise<import("./airflow.service").DagRun>;
    getPipelineStatus(dagId: string): Promise<{
        dag: import("./airflow.service").Dag;
        latestRun: import("./airflow.service").DagRun;
        tasks: import("./airflow.service").TaskInstance[];
    }>;
}
