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
  custom?: Record<string, unknown>;
  [key: string]: unknown;
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
  status: 'draft' | 'validating' | 'validated' | 'indexing' | 'ready' | 'failed';
  documentCount: number;
  chunkCount: number;
  embeddingDimension: number;
  validation: ValidationResult;
  updatedAt: Date;
}
