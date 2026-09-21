import {
  Column,
  CreateDateColumn,
  Entity,
  PrimaryGeneratedColumn,
  UpdateDateColumn,
} from 'typeorm';
import type {
  ChunkRecord,
  MetadataInput,
  ValidationResult,
  WorkflowDefinition,
} from '../modules/knowledge-base/knowledge-base.types';

@Entity({ name: 'knowledge_bases' })
export class KnowledgeBaseEntity {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  @Column({ name: 'name', type: 'varchar', length: 200 })
  name!: string;

  @Column({ name: 'description', type: 'text', nullable: true })
  description!: string | null;

  @Column({ name: 'metadata', type: 'jsonb', nullable: true, default: {} })
  metadata!: MetadataInput;

  @Column({ name: 'workflow', type: 'jsonb', nullable: true, default: [] })
  workflow!: WorkflowDefinition;

  @Column({ name: 'chunks', type: 'jsonb', nullable: true, default: [] })
  chunks!: ChunkRecord[];

  @Column({ name: 'validation', type: 'jsonb', nullable: true, default: {} })
  validation!: ValidationResult;

  @Column({ name: 'status', type: 'varchar', length: 30, default: 'draft' })
  status!: 'draft' | 'validating' | 'validated' | 'indexing' | 'ready' | 'failed';

  @CreateDateColumn({ name: 'created_at', type: 'timestamptz' })
  createdAt!: Date;

  @UpdateDateColumn({ name: 'updated_at', type: 'timestamptz' })
  updatedAt!: Date;
}
