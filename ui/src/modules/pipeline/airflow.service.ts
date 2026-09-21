import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { AxiosError } from 'axios';

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

@Injectable()
export class AirflowService {
  private baseUrl: string;
  private auth: { username: string; password: string };

  constructor(
    private configService: ConfigService,
    private httpService: HttpService,
  ) {
    this.baseUrl = this.configService.get('airflowUrl') || 'http://localhost:8080';
    this.auth = {
      username: this.configService.get('airflowUser') || 'airflow',
      password: this.configService.get('airflowPassword') || 'airflow',
    };
  }

  private async request<T>(method: string, endpoint: string, data?: any): Promise<T> {
    try {
      const response = await firstValueFrom(
        this.httpService.request<T>({
          method,
          url: `${this.baseUrl}/api/v1${endpoint}`,
          data,
          auth: this.auth,
          headers: {
            'Content-Type': 'application/json',
          },
        })
      );
      return response.data;
    } catch (error) {
      const axiosError = error as AxiosError;
      throw new Error(`Airflow API error: ${axiosError.response?.data || axiosError.message}`);
    }
  }

  async getDags(): Promise<Dag[]> {
    const response = await this.request<{ dags: Dag[] }>('GET', '/dags');
    return response.dags;
  }

  async getDag(dagId: string): Promise<Dag> {
    return this.request<Dag>('GET', `/dags/${dagId}`);
  }

  async triggerDag(dagId: string, conf?: Record<string, any>): Promise<DagRun> {
    return this.request<DagRun>('POST', `/dags/${dagId}/dagRuns`, { conf });
  }

  async getDagRuns(dagId: string, limit = 10): Promise<DagRun[]> {
    const response = await this.request<{ dag_runs: DagRun[] }>(
      'GET',
      `/dags/${dagId}/dagRuns?limit=${limit}&order_by=-execution_date`
    );
    return response.dag_runs;
  }

  async getDagRun(dagId: string, runId: string): Promise<DagRun> {
    return this.request<DagRun>('GET', `/dags/${dagId}/dagRuns/${runId}`);
  }

  async getTaskInstances(dagId: string, runId: string): Promise<TaskInstance[]> {
    const response = await this.request<{ task_instances: TaskInstance[] }>(
      'GET',
      `/dags/${dagId}/dagRuns/${runId}/taskInstances`
    );
    return response.task_instances;
  }

  async pauseDag(dagId: string): Promise<void> {
    await this.request('PATCH', `/dags/${dagId}`, { is_paused: true });
  }

  async unpauseDag(dagId: string): Promise<void> {
    await this.request('PATCH', `/dags/${dagId}`, { is_paused: false });
  }

  async clearTaskInstances(dagId: string, runId: string, taskIds?: string[]): Promise<void> {
    await this.request('POST', `/dags/${dagId}/dagRuns/${runId}/clearTaskInstances`, {
      task_ids: taskIds,
      dry_run: false,
    });
  }

  async getDagDetails(dagId: string): Promise<{ tasks: any[]; edges: any[] }> {
    const response = await this.request<{ tasks: any[]; edges: any[] }>(
      'GET',
      `/dags/${dagId}/details`
    );
    return response;
  }

  async getHealth(): Promise<{ metadatabase: { status: string }; scheduler: { status: string } }> {
    return this.request('GET', '/health');
  }
}