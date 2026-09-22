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
exports.DockerService = void 0;
const common_1 = require("@nestjs/common");
const config_1 = require("@nestjs/config");
const child_process_1 = require("child_process");
const util_1 = require("util");
const execAsync = (0, util_1.promisify)(child_process_1.exec);
let DockerService = class DockerService {
    constructor(configService) {
        this.configService = configService;
        this.composeProjects = new Map();
    }
    async onModuleInit() {
        await this.discoverProjects();
    }
    async discoverProjects() {
        const projects = [];
        const workspaceRoot = this.configService.get('WORKSPACE_ROOT') || process.cwd();
        try {
            const { stdout } = await execAsync(`find ${workspaceRoot} -name "docker-compose*.yml" -o -name "docker-compose*.yaml" 2>/dev/null | head -20`);
            const files = stdout.trim().split('\n').filter(f => f);
            const projectMap = new Map();
            for (const file of files) {
                const dir = file.substring(0, file.lastIndexOf('/'));
                if (!projectMap.has(dir)) {
                    projectMap.set(dir, []);
                }
                projectMap.get(dir).push(file);
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
        }
        catch (error) {
            console.error('Error discovering docker projects:', error);
        }
        for (const project of projects) {
            this.composeProjects.set(project.name, project);
        }
        return projects;
    }
    async getContainersForProject(projectDir) {
        try {
            const { stdout } = await execAsync(`cd ${projectDir} && docker compose ps --format json 2>/dev/null || docker-compose ps --format json 2>/dev/null`);
            if (!stdout.trim())
                return [];
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
                }
                catch {
                    return null;
                }
            }).filter(Boolean);
        }
        catch {
            return [];
        }
    }
    async getAllContainers() {
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
                }
                catch {
                    return null;
                }
            }).filter(Boolean);
        }
        catch {
            return [];
        }
    }
    async startProject(projectName) {
        const project = this.composeProjects.get(projectName);
        if (!project) {
            return { success: false, output: 'Project not found' };
        }
        try {
            const dir = project.configFiles[0].substring(0, project.configFiles[0].lastIndexOf('/'));
            const { stdout, stderr } = await execAsync(`cd ${dir} && docker compose up -d 2>&1`, { timeout: 120000 });
            await this.discoverProjects();
            return { success: true, output: stdout + stderr };
        }
        catch (error) {
            return { success: false, output: error.message || error.stdout || error.stderr };
        }
    }
    async stopProject(projectName) {
        const project = this.composeProjects.get(projectName);
        if (!project) {
            return { success: false, output: 'Project not found' };
        }
        try {
            const dir = project.configFiles[0].substring(0, project.configFiles[0].lastIndexOf('/'));
            const { stdout, stderr } = await execAsync(`cd ${dir} && docker compose down 2>&1`, { timeout: 60000 });
            await this.discoverProjects();
            return { success: true, output: stdout + stderr };
        }
        catch (error) {
            return { success: false, output: error.message || error.stdout || error.stderr };
        }
    }
    async restartProject(projectName) {
        await this.stopProject(projectName);
        return this.startProject(projectName);
    }
    async getContainerLogs(containerId, tail = 100) {
        try {
            const { stdout } = await execAsync(`docker logs --tail ${tail} ${containerId} 2>&1`);
            return stdout;
        }
        catch (error) {
            return error.message;
        }
    }
    async getProjects() {
        return Array.from(this.composeProjects.values());
    }
    async getProjectStatus(projectName) {
        return this.composeProjects.get(projectName) || null;
    }
};
exports.DockerService = DockerService;
exports.DockerService = DockerService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [config_1.ConfigService])
], DockerService);
//# sourceMappingURL=docker.service.js.map