import { OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
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
export declare class DockerService implements OnModuleInit {
    private configService;
    private composeProjects;
    constructor(configService: ConfigService);
    onModuleInit(): Promise<void>;
    discoverProjects(): Promise<DockerComposeProject[]>;
    getContainersForProject(projectDir: string): Promise<DockerContainer[]>;
    getAllContainers(): Promise<DockerContainer[]>;
    startProject(projectName: string): Promise<{
        success: boolean;
        output: string;
    }>;
    stopProject(projectName: string): Promise<{
        success: boolean;
        output: string;
    }>;
    restartProject(projectName: string): Promise<{
        success: boolean;
        output: string;
    }>;
    getContainerLogs(containerId: string, tail?: number): Promise<string>;
    getProjects(): Promise<DockerComposeProject[]>;
    getProjectStatus(projectName: string): Promise<DockerComposeProject | null>;
}
