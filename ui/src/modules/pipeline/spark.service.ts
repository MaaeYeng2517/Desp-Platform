import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { exec, spawn } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface SparkJob {
  id: string;
  name: string;
  appResource: string;
  mainClass?: string;
  arguments?: string[];
  sparkConf?: Record<string, string>;
  status: 'pending' | 'running' | 'completed' | 'failed';
  submitTime?: Date;
  completionTime?: Date;
  driverLogUrl?: string;
}

export interface SparkConfig {
  master: string;
  deployMode: 'cluster' | 'client';
  executorMemory: string;
  executorCores: number;
  numExecutors: number;
  driverMemory: string;
}

@Injectable()
export class SparkService {
  private sparkMaster: string;
  private defaultConfig: SparkConfig;
  private jobs: Map<string, SparkJob> = new Map();

  constructor(private configService: ConfigService) {
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

  async submitJob(job: Omit<SparkJob, 'id' | 'status' | 'submitTime'>): Promise<SparkJob> {
    const id = `spark-job-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const sparkJob: SparkJob = {
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
      
      const child = spawn('spark-submit', args, {
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
    } catch (error) {
      sparkJob.status = 'failed';
      sparkJob.completionTime = new Date();
      throw error;
    }
  }

  private buildSparkSubmitArgs(job: any, config: SparkConfig): string[] {
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

  async getJobStatus(jobId: string): Promise<SparkJob | null> {
    return this.jobs.get(jobId) || null;
  }

  async listJobs(): Promise<SparkJob[]> {
    return Array.from(this.jobs.values());
  }

  async killJob(jobId: string): Promise<boolean> {
    const job = this.jobs.get(jobId);
    if (!job) return false;

    try {
      // This would need spark-submit --kill or REST API to Spark master
      // For now, we just mark it
      job.status = 'failed';
      job.completionTime = new Date();
      return true;
    } catch {
      return false;
    }
  }

  async getSparkMasterUI(): Promise<string> {
    // Extract web UI URL from master
    const masterHost = this.sparkMaster.replace('spark://', '').split(':')[0];
    return `http://${masterHost}:4040`;
  }

  async getApplications(): Promise<any[]> {
    try {
      const masterHost = this.sparkMaster.replace('spark://', '').split(':')[0];
      const { stdout } = await execAsync(
        `curl -s http://${masterHost}:4040/api/v1/applications`
      );
      return JSON.parse(stdout);
    } catch {
      return [];
    }
  }

  getDefaultConfig(): SparkConfig {
    return { ...this.defaultConfig };
  }

  updateConfig(config: Partial<SparkConfig>): void {
    this.defaultConfig = { ...this.defaultConfig, ...config };
  }
}