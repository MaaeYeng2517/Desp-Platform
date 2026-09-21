import { Injectable } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { AirflowService } from './airflow.service';
import { DockerService } from './docker.service';

@Injectable()
export class PipelineService {
  constructor(
    private readonly airflowService: AirflowService,
    private readonly dockerService: DockerService,
  ) {}

  @Cron(CronExpression.EVERY_5_MINUTES)
  async monitorPipelines() {
    try {
      const health = await this.airflowService.getHealth();
      if (health.metadatabase?.status !== 'healthy' || health.scheduler?.status !== 'healthy') {
        console.warn('Airflow health check failed:', health);
      }
    } catch (error) {
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
    } catch (error) {
      return { error: error.message };
    }
  }

  async triggerPipeline(dagId: string, conf?: Record<string, any>) {
    return this.airflowService.triggerDag(dagId, conf);
  }

  async getPipelineStatus(dagId: string) {
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
}