export type KnowledgeBaseStatus =
  | 'draft'
  | 'validating'
  | 'validated'
  | 'indexing'
  | 'ready'
  | 'failed';

export type WorkflowNodeType =
  | 'source_pdf'
  | 'source_docx'
  | 'source_csv'
  | 'source_website'
  | 'source_database'
  | 'source_api'
  | 'extract_text'
  | 'clean_text'
  | 'chunk'
  | 'metadata'
  | 'embedding'
  | 'reranking'
  | 'vector_database'
  | 'knowledge_base'
  | 'rag'
  | 'agent';

export interface WorkflowNode {
  id: string;
  type: WorkflowNodeType;
  label: string;
  config?: Record<string, unknown>;
  position?: { x: number; y: number };
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
  language?: string;
  custom?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface DocumentInput {
  id?: string;
  content: string;
  metadata?: Record<string, unknown>;
}

export interface KnowledgeBaseRecord {
  id: string;
  name: string;
  description?: string | null;
  metadata: MetadataInput;
  workflow: WorkflowDefinition;
  chunks: ChunkRecord[];
  validation?: ValidationResult;
  status: KnowledgeBaseStatus;
  createdAt?: string;
  updatedAt?: string;
}

export interface KnowledgeBaseInput {
  name: string;
  description?: string;
  metadata?: Record<string, unknown>;
  workflow?: Partial<WorkflowDefinition>;
}

export interface ChunkRecord {
  id: string;
  content: string;
  metadata: Record<string, unknown>;
  embedding: number[];
  sourceDocumentId: string;
  sourceNodeIds: string[];
}

export interface ValidationResult {
  valid: boolean;
  issues: Array<{
    severity: 'error' | 'warning';
    message: string;
    nodeId?: string;
  }>;
  checkedAt: string;
}

export interface ComponentDefinition {
  type: WorkflowNodeType;
  label: string;
  category: 'Sources' | 'Processing' | 'Metadata' | 'Storage' | 'AI';
  description: string;
  defaultConfig: Record<string, unknown>;
}

export interface RunResponse {
  id: string;
  status: KnowledgeBaseStatus;
  documentCount: number;
  chunkCount: number;
  embeddingDimension: number;
  validation: ValidationResult;
  updatedAt: string;
}

export interface SearchResult {
  chunk: ChunkRecord;
  score: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
}

export interface RetrieveResponse extends SearchResponse {
  answer: string;
  sources: SearchResult[];
}

export interface StatusResponse {
  id: string;
  name: string;
  status: KnowledgeBaseStatus;
  workflow: { nodes: number; edges: number };
  index: { documents: number; chunks: number; embeddingDimension: number };
  validation?: ValidationResult;
  updatedAt: string;
}

export interface WorkspaceState {
  apiBase: string;
  selectedKnowledgeBaseId?: string;
  metadata: MetadataInput;
  workflow: WorkflowDefinition;
  documents: string;
}
