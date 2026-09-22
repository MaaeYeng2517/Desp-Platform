import type { ChunkRecord, MetadataInput, ValidationResult, WorkflowDefinition } from '../modules/knowledge-base/knowledge-base.types';
export declare class KnowledgeBaseEntity {
    id: string;
    name: string;
    description: string | null;
    metadata: MetadataInput;
    workflow: WorkflowDefinition;
    chunks: ChunkRecord[];
    validation: ValidationResult;
    status: 'draft' | 'validating' | 'validated' | 'indexing' | 'ready' | 'failed';
    createdAt: Date;
    updatedAt: Date;
}
