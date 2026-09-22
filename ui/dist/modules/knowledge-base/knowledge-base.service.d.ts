import { Repository } from 'typeorm';
import { KnowledgeBaseEntity } from '../../entities/knowledge-base.entity';
export type WorkflowNodeType = 'source_pdf' | 'source_docx' | 'source_csv' | 'source_website' | 'source_database' | 'source_api' | 'extract_text' | 'clean_text' | 'chunk' | 'metadata' | 'embedding' | 'reranking' | 'vector_database' | 'knowledge_base' | 'rag' | 'agent';
export interface WorkflowNode {
    id: string;
    type: WorkflowNodeType;
    label: string;
    config?: Record<string, unknown>;
    position?: {
        x: number;
        y: number;
    };
}
export interface WorkflowEdge {
    id: string;
    from: string;
    to: string;
}
export interface WorkflowDefinition {
    nodes: WorkflowNode[];
    edges: WorkflowEdge[];
}
export interface MetadataInput {
    title?: string;
    description?: string;
    tags?: string[];
    owner?: string;
    version?: string;
    visibility?: 'private' | 'team' | 'public';
    custom?: Record<string, unknown>;
}
export interface DocumentInput {
    id?: string;
    content: string;
    metadata?: Record<string, unknown>;
}
export interface KnowledgeBaseInput {
    name: string;
    description?: string;
    metadata?: MetadataInput;
    workflow?: Partial<WorkflowDefinition>;
}
export interface RunKnowledgeBaseRequest {
    documents: DocumentInput[];
}
export interface SearchKnowledgeBaseRequest {
    query: string;
    topK?: number;
}
export interface RetrieveKnowledgeBaseRequest extends SearchKnowledgeBaseRequest {
    systemPrompt?: string;
}
export interface ChunkRecord {
    id: string;
    content: string;
    metadata: Record<string, unknown>;
    embedding: number[];
    sourceDocumentId: string;
    sourceNodeIds: string[];
}
export interface SearchResult {
    chunk: ChunkRecord;
    score: number;
}
export interface ValidationIssue {
    severity: 'error' | 'warning';
    message: string;
    nodeId?: string;
}
export interface ValidationResult {
    valid: boolean;
    issues: ValidationIssue[];
    checkedAt: string;
}
export interface ComponentDefinition {
    type: WorkflowNodeType;
    label: string;
    category: 'Sources' | 'Processing' | 'Metadata' | 'Storage' | 'AI';
    description: string;
    defaultConfig: Record<string, unknown>;
}
export interface PipelineRunResult {
    id: string;
    status: KnowledgeBaseEntity['status'];
    documentCount: number;
    chunkCount: number;
    embeddingDimension: number;
    validation: ValidationResult;
    updatedAt: Date;
}
export declare class KnowledgeBaseService {
    private readonly knowledgeBaseRepo;
    constructor(knowledgeBaseRepo: Repository<KnowledgeBaseEntity>);
    getComponentCatalog(): ComponentDefinition[];
    create(input: KnowledgeBaseInput): Promise<KnowledgeBaseEntity>;
    findAll(): Promise<KnowledgeBaseEntity[]>;
    findOne(id: string): Promise<KnowledgeBaseEntity>;
    update(id: string, input: Partial<KnowledgeBaseInput>): Promise<KnowledgeBaseEntity>;
    remove(id: string): Promise<void>;
    validate(id: string): Promise<{
        id: string;
        validation: ValidationResult;
        status: KnowledgeBaseEntity['status'];
    }>;
    run(id: string, request: RunKnowledgeBaseRequest): Promise<PipelineRunResult>;
    search(id: string, request: SearchKnowledgeBaseRequest): Promise<{
        query: string;
        results: SearchResult[];
    }>;
    retrieve(id: string, request: RetrieveKnowledgeBaseRequest): Promise<{
        query: string;
        answer: string;
        sources: SearchResult[];
    }>;
    getStatus(id: string): Promise<Record<string, unknown>>;
    createDemo(): Promise<PipelineRunResult>;
    private normalizeWorkflow;
    private normalizeNode;
    private isWorkflowNodeType;
    private normalizeMetadata;
    private validateWorkflowAndMetadata;
    private hasCycle;
    private hasPathToAgent;
    private labelForType;
    private getNodeConfig;
    private positiveInteger;
    private createDefaultWorkflow;
    private createChunks;
    private embedText;
    private cosineSimilarity;
}
