import { ConfigService } from '@nestjs/config';
import { HttpService } from '@nestjs/axios';
export interface DagRun {
    dag_id: string;
    run_id: string;
    logical_date: string;
    start_date: string;
    end_date: string | null;
    state: string;
    execution_date: string;
    conf: Record<string, any>;
}
export interface Dag {
    dag_id: string;
    description: string;
    schedule_interval: string;
    is_active: boolean;
    is_paused: boolean;
    last_run: DagRun | null;
    next_run: string | null;
}
export interface TaskInstance {
    dag_id: string;
    task_id: string;
    run_id: string;
    state: string;
    start_date: string | null;
    end_date: string | null;
    duration: number | null;
}
export declare class AirflowService {
    private configService;
    private httpService;
    private baseUrl;
    private auth;
    constructor(configService: ConfigService, httpService: HttpService);
    private request;
    getDags(): Promise<Dag[]>;
    getDag(dagId: string): Promise<Dag>;
    triggerDag(dagId: string, conf?: Record<string, any>): Promise<DagRun>;
    getDagRuns(dagId: string, limit?: number): Promise<DagRun[]>;
    getDagRun(dagId: string, runId: string): Promise<DagRun>;
    getTaskInstances(dagId: string, runId: string): Promise<TaskInstance[]>;
    pauseDag(dagId: string): Promise<void>;
    unpauseDag(dagId: string): Promise<void>;
    clearTaskInstances(dagId: string, runId: string, taskIds?: string[]): Promise<void>;
    getDagDetails(dagId: string): Promise<{
        tasks: any[];
        edges: any[];
    }>;
    getHealth(): Promise<{
        metadatabase: {
            status: string;
        };
        scheduler: {
            status: string;
        };
    }>;
}
