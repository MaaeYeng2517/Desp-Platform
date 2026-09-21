import { Injectable, OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { exec, spawn } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface DockerContainer {
  id: string;
  name: string;
  image: string;
  status: string;
  ports: string;
  created: string;
}

export interface DockerComposeProject {
  name: string;
  configFiles: string[];
  containers: DockerContainer[];
  status: 'running' | 'stopped' | 'partial';
}

@Injectable()
export class DockerService implements OnModuleInit {
  private composeProjects: Map<string, DockerComposeProject> = new Map();

  constructor(private configService: ConfigService) {}

  async onModuleInit() {
    await this.discoverProjects();
  }

  async discoverProjects(): Promise<DockerComposeProject[]> {
    const projects: DockerComposeProject[] = [];
    
    // Check for docker-compose files in the workspace
    const workspaceRoot = this.configService.get('WORKSPACE_ROOT') || process.cwd();
    
    try {
      const { stdout } = await execAsync(`find ${workspaceRoot} -name "docker-compose*.yml" -o -name "docker-compose*.yaml" 2>/dev/null | head -20`);
      const files = stdout.trim().split('\n').filter(f => f);
      
      // Group by directory
      const projectMap = new Map<string, string[]>();
      for (const file of files) {
        const dir = file.substring(0, file.lastIndexOf('/'));
        if (!projectMap.has(dir)) {
          projectMap.set(dir, []);
        }
        projectMap.get(dir)!.push(file);
      }

      for (const [dir, configFiles] of projectMap) {
        const containers = await this.getContainersForProject(dir);
        const running = containers.filter(c => c.status.includes('Up')).length;
        const status = running === 0 ? 'stopped' : running === containers.length ? 'running' : 'partial';
        
        projects.push({
          name: dir.split('/').pop() || dir,
          configFiles,
          containers,
          status,
        });
      }
    } catch (error) {
      console.error('Error discovering docker projects:', error);
    }

    for (const project of projects) {
      this.composeProjects.set(project.name, project);
    }

    return projects;
  }

  async getContainersForProject(projectDir: string): Promise<DockerContainer[]> {
    try {
      const { stdout } = await execAsync(
        `cd ${projectDir} && docker compose ps --format json 2>/dev/null || docker-compose ps --format json 2>/dev/null`
      );
      
      if (!stdout.trim()) return [];
      
      const lines = stdout.trim().split('\n');
      return lines.map(line => {
        try {
          const data = JSON.parse(line);
          return {
            id: data.ID || data.Id,
            name: data.Name || data.Service,
            image: data.Image,
            status: data.Status || data.State,
            ports: data.Ports || '',
            created: data.CreatedAt || '',
          };
        } catch {
          return null;
        }
      }).filter(Boolean) as DockerContainer[];
    } catch {
      return [];
    }
  }

  async getAllContainers(): Promise<DockerContainer[]> {
    try {
      const { stdout } = await execAsync('docker ps -a --format json');
      const lines = stdout.trim().split('\n');
      return lines.map(line => {
        try {
          const data = JSON.parse(line);
          return {
            id: data.ID,
            name: data.Names,
            image: data.Image,
            status: data.Status,
            ports: data.Ports,
            created: data.CreatedAt,
          };
        } catch {
          return null;
        }
      }).filter(Boolean) as DockerContainer[];
    } catch {
      return [];
    }
  }

  async startProject(projectName: string): Promise<{ success: boolean; output: string }> {
    const project = this.composeProjects.get(projectName);
    if (!project) {
      return { success: false, output: 'Project not found' };
    }

    try {
      const dir = project.configFiles[0].substring(0, project.configFiles[0].lastIndexOf('/'));
      const { stdout, stderr } = await execAsync(
        `cd ${dir} && docker compose up -d 2>&1`,
        { timeout: 120000 }
      );
      await this.discoverProjects();
      return { success: true, output: stdout + stderr };
    } catch (error: any) {
      return { success: false, output: error.message || error.stdout || error.stderr };
    }
  }

  async stopProject(projectName: string): Promise<{ success: boolean; output: string }> {
    const project = this.composeProjects.get(projectName);
    if (!project) {
      return { success: false, output: 'Project not found' };
    }

    try {
      const dir = project.configFiles[0].substring(0, project.configFiles[0].lastIndexOf('/'));
      const { stdout, stderr } = await execAsync(
        `cd ${dir} && docker compose down 2>&1`,
        { timeout: 60000 }
      );
      await this.discoverProjects();
      return { success: true, output: stdout + stderr };
    } catch (error: any) {
      return { success: false, output: error.message || error.stdout || error.stderr };
    }
  }

  async restartProject(projectName: string): Promise<{ success: boolean; output: string }> {
    await this.stopProject(projectName);
    return this.startProject(projectName);
  }

  async getContainerLogs(containerId: string, tail = 100): Promise<string> {
    try {
      const { stdout } = await execAsync(
        `docker logs --tail ${tail} ${containerId} 2>&1`
      );
      return stdout;
    } catch (error: any) {
      return error.message;
    }
  }

  async getProjects(): Promise<DockerComposeProject[]> {
    return Array.from(this.composeProjects.values());
  }

  async getProjectStatus(projectName: string): Promise<DockerComposeProject | null> {
    return this.composeProjects.get(projectName) || null;
  }
}