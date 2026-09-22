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
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.KnowledgeBaseService = void 0;
const common_1 = require("@nestjs/common");
const typeorm_1 = require("@nestjs/typeorm");
const typeorm_2 = require("typeorm");
const knowledge_base_entity_1 = require("../../entities/knowledge-base.entity");
const componentCatalog = [
    { type: 'source_pdf', label: 'PDF', category: 'Sources', description: 'Load text from PDF files', defaultConfig: { extractLayout: true } },
    { type: 'source_docx', label: 'DOCX', category: 'Sources', description: 'Load text from Word documents', defaultConfig: { includeTables: true } },
    { type: 'source_csv', label: 'CSV', category: 'Sources', description: 'Load rows from a CSV file', defaultConfig: { delimiter: ',' } },
    { type: 'source_website', label: 'Website', category: 'Sources', description: 'Crawl and load web content', defaultConfig: { maxPages: 10 } },
    { type: 'source_database', label: 'Database', category: 'Sources', description: 'Read rows from a database query', defaultConfig: { batchSize: 500 } },
    { type: 'source_api', label: 'API', category: 'Sources', description: 'Ingest JSON from an API endpoint', defaultConfig: { method: 'GET' } },
    { type: 'extract_text', label: 'Extract Text', category: 'Processing', description: 'Extract readable text from source content', defaultConfig: { preserveParagraphs: true } },
    { type: 'clean_text', label: 'Clean Text', category: 'Processing', description: 'Remove noise and normalize text', defaultConfig: { removeExtraWhitespace: true } },
    { type: 'chunk', label: 'Chunk', category: 'Processing', description: 'Split content into retrievable chunks', defaultConfig: { chunkSize: 500, overlap: 50 } },
    { type: 'metadata', label: 'Metadata', category: 'Metadata', description: 'Attach structured metadata to chunks', defaultConfig: { requiredFields: ['source', 'language'] } },
    { type: 'embedding', label: 'Embedding', category: 'Processing', description: 'Create deterministic vector embeddings', defaultConfig: { dimension: 32, model: 'local-hash-v1' } },
    { type: 'reranking', label: 'Reranking', category: 'AI', description: 'Reorder search results by relevance', defaultConfig: { topK: 5 } },
    { type: 'vector_database', label: 'Vector DB', category: 'Storage', description: 'Store and index chunk embeddings', defaultConfig: { index: 'cosine' } },
    { type: 'knowledge_base', label: 'Knowledge Base', category: 'Storage', description: 'Publish an indexed knowledge collection', defaultConfig: { publish: true } },
    { type: 'rag', label: 'RAG', category: 'AI', description: 'Retrieve context for an AI answer', defaultConfig: { topK: 4 } },
    { type: 'agent', label: 'AI Agent', category: 'AI', description: 'Expose the knowledge base to an agent', defaultConfig: { temperature: 0.2 } },
];
const requiredNodeTypes = [
    'chunk',
    'metadata',
    'embedding',
    'vector_database',
    'knowledge_base',
    'rag',
    'agent',
];
const nodeOrder = {
    source_pdf: 0,
    source_docx: 0,
    source_csv: 0,
    source_website: 0,
    source_database: 0,
    source_api: 0,
    extract_text: 10,
    clean_text: 15,
    chunk: 20,
    metadata: 30,
    embedding: 40,
    reranking: 45,
    vector_database: 50,
    knowledge_base: 60,
    rag: 70,
    agent: 80,
};
let KnowledgeBaseService = class KnowledgeBaseService {
    constructor(knowledgeBaseRepo) {
        this.knowledgeBaseRepo = knowledgeBaseRepo;
    }
    getComponentCatalog() {
        return componentCatalog;
    }
    async create(input) {
        const workflow = this.normalizeWorkflow(input.workflow);
        const metadata = this.normalizeMetadata(input.metadata);
        const validation = this.validateWorkflowAndMetadata(workflow, metadata);
        const entity = this.knowledgeBaseRepo.create({
            name: input.name.trim(),
            description: input.description?.trim() || '',
            metadata: metadata,
            workflow: workflow,
            chunks: [],
            validation: validation,
            status: 'draft',
        });
        return this.knowledgeBaseRepo.save(entity);
    }
    async findAll() {
        const entities = await this.knowledgeBaseRepo.find({ order: { updatedAt: 'DESC' } });
        return entities;
    }
    async findOne(id) {
        const entity = await this.knowledgeBaseRepo.findOneBy({ id });
        if (!entity) {
            throw new common_1.NotFoundException(`Knowledge base ${id} not found`);
        }
        return entity;
    }
    async update(id, input) {
        const entity = await this.findOne(id);
        const workflow = input.workflow ? this.normalizeWorkflow(input.workflow) : entity.workflow;
        const metadata = input.metadata ? this.normalizeMetadata(input.metadata) : entity.metadata;
        const validation = this.validateWorkflowAndMetadata(workflow, metadata);
        Object.assign(entity, {
            name: input.name?.trim() || entity.name,
            description: input.description === undefined ? entity.description : input.description.trim(),
            metadata,
            workflow,
            validation,
            status: validation.valid ? 'validated' : 'failed',
        });
        return this.knowledgeBaseRepo.save(entity);
    }
    async remove(id) {
        const entity = await this.findOne(id);
        await this.knowledgeBaseRepo.remove(entity);
    }
    async validate(id) {
        const entity = await this.findOne(id);
        entity.status = 'validating';
        await this.knowledgeBaseRepo.save(entity);
        const workflow = this.normalizeWorkflow(entity.workflow);
        const metadata = this.normalizeMetadata(entity.metadata);
        const validation = this.validateWorkflowAndMetadata(workflow, metadata);
        entity.validation = validation;
        entity.status = validation.valid ? 'validated' : 'failed';
        await this.knowledgeBaseRepo.save(entity);
        return { id: entity.id, validation, status: entity.status };
    }
    async run(id, request) {
        const entity = await this.findOne(id);
        const workflow = this.normalizeWorkflow(entity.workflow);
        const metadata = this.normalizeMetadata(entity.metadata);
        const validation = this.validateWorkflowAndMetadata(workflow, metadata);
        entity.validation = validation;
        if (!validation.valid || !request.documents?.length) {
            entity.status = 'failed';
            await this.knowledgeBaseRepo.save(entity);
            throw new common_1.BadRequestException({
                message: validation.valid ? 'At least one document is required' : 'Workflow validation failed',
                validation,
            });
        }
        entity.status = 'indexing';
        await this.knowledgeBaseRepo.save(entity);
        const chunkConfig = this.getNodeConfig(workflow, 'chunk');
        const embeddingConfig = this.getNodeConfig(workflow, 'embedding');
        const chunkSize = this.positiveInteger(chunkConfig.chunkSize, 500, 10000);
        const overlap = this.positiveInteger(chunkConfig.overlap, 50, chunkSize - 1);
        const dimension = this.positiveInteger(embeddingConfig.dimension, 32, 512);
        const chunks = request.documents.flatMap((document, documentIndex) => this.createChunks(document, documentIndex, workflow, chunkSize, overlap, dimension));
        entity.chunks = chunks;
        entity.status = 'ready';
        await this.knowledgeBaseRepo.save(entity);
        return {
            id: entity.id,
            status: entity.status,
            documentCount: request.documents.length,
            chunkCount: chunks.length,
            embeddingDimension: dimension,
            validation,
            updatedAt: entity.updatedAt,
        };
    }
    async search(id, request) {
        const entity = await this.findOne(id);
        const query = request.query?.trim();
        if (!query) {
            throw new common_1.BadRequestException('Query is required');
        }
        const topK = Math.max(1, Math.min(request.topK || 5, 50));
        const chunks = Array.isArray(entity.chunks) ? entity.chunks : [];
        const queryEmbedding = this.embedText(query, chunks[0]?.embedding.length || 32);
        const results = chunks
            .map((chunk) => ({ chunk, score: this.cosineSimilarity(queryEmbedding, chunk.embedding) }))
            .sort((a, b) => b.score - a.score)
            .slice(0, topK);
        return { query, results };
    }
    async retrieve(id, request) {
        const { query, results } = await this.search(id, request);
        const sources = results.map((result) => ({
            ...result,
            chunk: {
                ...result.chunk,
                content: result.chunk.content.slice(0, 500),
            },
        }));
        const context = sources.map((result) => `- ${result.chunk.content}`).join('\n');
        const prompt = request.systemPrompt?.trim() || 'Answer using only the retrieved knowledge context.';
        const answer = context
            ? `${prompt}\n\nAnswer:\n${context}`
            : `${prompt}\n\nNo matching knowledge chunks were found.`;
        return { query, answer, sources };
    }
    async getStatus(id) {
        const entity = await this.findOne(id);
        const chunks = Array.isArray(entity.chunks) ? entity.chunks : [];
        const workflow = this.normalizeWorkflow(entity.workflow);
        return {
            id: entity.id,
            name: entity.name,
            status: entity.status,
            workflow: {
                nodes: workflow.nodes.length,
                edges: workflow.edges.length,
            },
            index: {
                documents: new Set(chunks.map((chunk) => chunk.sourceDocumentId)).size,
                chunks: chunks.length,
                embeddingDimension: chunks[0]?.embedding.length || 0,
            },
            validation: entity.validation,
            updatedAt: entity.updatedAt,
        };
    }
    async createDemo() {
        const workflow = this.createDefaultWorkflow();
        const entity = await this.create({
            name: 'Product Support Knowledge',
            description: 'Demo knowledge base for retrieval and RAG',
            metadata: {
                title: 'Product Support Knowledge',
                description: 'Support policies, troubleshooting, and product guidance',
                tags: ['support', 'product', 'demo'],
                owner: 'Knowledge Team',
                version: '1.0.0',
                visibility: 'team',
            },
            workflow,
        });
        const result = await this.run(entity.id, {
            documents: [
                {
                    id: 'demo-refunds',
                    content: 'Customers can request a refund within 30 days of purchase. Refunds return to the original payment method within five business days.',
                    metadata: { source: 'refund-policy', language: 'en' },
                },
                {
                    id: 'demo-password',
                    content: 'To reset a password, open the sign in screen, choose forgot password, and follow the email verification link. Contact support if the email does not arrive.',
                    metadata: { source: 'account-help', language: 'en' },
                },
                {
                    id: 'demo-export',
                    content: 'Export reports from the analytics page. Choose CSV for spreadsheets or JSON for API integrations, then confirm the date range before exporting.',
                    metadata: { source: 'analytics-guide', language: 'en' },
                },
            ],
        });
        return result;
    }
    normalizeWorkflow(workflow) {
        if (!workflow || typeof workflow !== 'object') {
            return this.createDefaultWorkflow();
        }
        const nodes = Array.isArray(workflow.nodes)
            ? workflow.nodes.map((node, index) => this.normalizeNode(node, index))
            : this.createDefaultWorkflow().nodes;
        const edges = Array.isArray(workflow.edges)
            ? workflow.edges.map((edge, index) => ({
                id: typeof edge?.id === 'string' && edge.id ? edge.id : `edge-${index + 1}`,
                from: typeof edge?.from === 'string' ? edge.from : '',
                to: typeof edge?.to === 'string' ? edge.to : '',
            }))
            : this.createDefaultWorkflow().edges;
        return { nodes, edges };
    }
    normalizeNode(node, index) {
        if (!node || typeof node !== 'object') {
            return {
                id: `node-${index + 1}`,
                type: 'chunk',
                label: 'Chunk',
                position: { x: 80 + (index % 4) * 220, y: 100 + Math.floor(index / 4) * 140 },
            };
        }
        const candidate = node;
        const type = this.isWorkflowNodeType(candidate.type) ? candidate.type : 'chunk';
        const definition = componentCatalog.find((item) => item.type === type);
        return {
            id: typeof candidate.id === 'string' && candidate.id ? candidate.id : `node-${index + 1}`,
            type,
            label: typeof candidate.label === 'string' && candidate.label ? candidate.label : definition?.label || type,
            config: typeof candidate.config === 'object' && candidate.config ? candidate.config : { ...definition?.defaultConfig },
            position: typeof candidate.position === 'object' && candidate.position
                ? {
                    x: Number(candidate.position.x) || 0,
                    y: Number(candidate.position.y) || 0,
                }
                : { x: 80 + (index % 4) * 220, y: 100 + Math.floor(index / 4) * 140 },
        };
    }
    isWorkflowNodeType(value) {
        return typeof value === 'string' && Object.keys(nodeOrder).includes(value);
    }
    normalizeMetadata(metadata) {
        if (!metadata || typeof metadata !== 'object') {
            return {};
        }
        return {
            ...metadata,
            tags: Array.isArray(metadata.tags) ? metadata.tags.filter((tag) => typeof tag === 'string') : [],
            visibility: ['private', 'team', 'public'].includes(metadata.visibility || '') ? metadata.visibility : 'private',
        };
    }
    validateWorkflowAndMetadata(workflow, metadata) {
        const issues = [];
        const ids = new Set();
        const knownTypes = new Set(Object.keys(nodeOrder));
        for (const node of workflow.nodes) {
            if (!node.id || ids.has(node.id)) {
                issues.push({ severity: 'error', message: `Duplicate or missing node id: ${node.id || 'unknown'}`, nodeId: node.id });
            }
            ids.add(node.id);
            if (!knownTypes.has(node.type)) {
                issues.push({ severity: 'error', message: `Unknown component type: ${node.type}`, nodeId: node.id });
            }
        }
        for (const edge of workflow.edges) {
            if (!ids.has(edge.from) || !ids.has(edge.to)) {
                issues.push({ severity: 'error', message: `Edge ${edge.id} references an unknown node`, nodeId: edge.from || edge.to });
            }
            const from = workflow.nodes.find((node) => node.id === edge.from);
            const to = workflow.nodes.find((node) => node.id === edge.to);
            if (from && to && nodeOrder[to.type] < nodeOrder[from.type]) {
                issues.push({ severity: 'error', message: `Edge ${edge.id} moves backward in the pipeline`, nodeId: edge.id });
            }
        }
        if (this.hasCycle(workflow)) {
            issues.push({ severity: 'error', message: 'Workflow contains a cycle' });
        }
        const sourceCount = workflow.nodes.filter((node) => node.type.startsWith('source_')).length;
        if (sourceCount < 1) {
            issues.push({ severity: 'error', message: 'Add at least one knowledge source' });
        }
        for (const type of requiredNodeTypes) {
            if (!workflow.nodes.some((node) => node.type === type)) {
                issues.push({ severity: 'error', message: `Missing required component: ${this.labelForType(type)}` });
            }
        }
        if (workflow.nodes.length && !this.hasPathToAgent(workflow)) {
            issues.push({ severity: 'error', message: 'Connect the workflow to an AI Agent' });
        }
        if (!metadata || typeof metadata !== 'object' || Array.isArray(metadata)) {
            issues.push({ severity: 'error', message: 'Metadata must be an object' });
        }
        else {
            if (metadata.tags !== undefined && (!Array.isArray(metadata.tags) || metadata.tags.some((tag) => typeof tag !== 'string'))) {
                issues.push({ severity: 'error', message: 'Metadata tags must be an array of strings' });
            }
            if (metadata.visibility !== undefined && !['private', 'team', 'public'].includes(String(metadata.visibility))) {
                issues.push({ severity: 'error', message: 'Metadata visibility must be private, team, or public' });
            }
        }
        if (!workflow.nodes.some((node) => node.type === 'extract_text') && sourceCount) {
            issues.push({ severity: 'warning', message: 'Add Extract Text to make source ingestion explicit' });
        }
        if (!workflow.nodes.some((node) => node.type === 'clean_text')) {
            issues.push({ severity: 'warning', message: 'Add Clean Text to remove noise before chunking' });
        }
        return {
            valid: !issues.some((issue) => issue.severity === 'error'),
            issues,
            checkedAt: new Date().toISOString(),
        };
    }
    hasCycle(workflow) {
        const adjacency = new Map();
        for (const node of workflow.nodes) {
            adjacency.set(node.id, []);
        }
        for (const edge of workflow.edges) {
            adjacency.get(edge.from)?.push(edge.to);
        }
        const visiting = new Set();
        const visited = new Set();
        const visit = (id) => {
            if (visiting.has(id)) {
                return true;
            }
            if (visited.has(id)) {
                return false;
            }
            visiting.add(id);
            for (const next of adjacency.get(id) || []) {
                if (visit(next)) {
                    return true;
                }
            }
            visiting.delete(id);
            visited.add(id);
            return false;
        };
        return workflow.nodes.some((node) => visit(node.id));
    }
    hasPathToAgent(workflow) {
        const adjacency = new Map();
        for (const node of workflow.nodes) {
            adjacency.set(node.id, []);
        }
        for (const edge of workflow.edges) {
            adjacency.get(edge.from)?.push(edge.to);
        }
        const sources = workflow.nodes.filter((node) => node.type.startsWith('source_')).map((node) => node.id);
        const queue = [...sources];
        const seen = new Set();
        while (queue.length) {
            const id = queue.shift();
            if (seen.has(id)) {
                continue;
            }
            seen.add(id);
            if (workflow.nodes.some((node) => node.id === id && node.type === 'agent')) {
                return true;
            }
            queue.push(...(adjacency.get(id) || []));
        }
        return false;
    }
    labelForType(type) {
        return componentCatalog.find((component) => component.type === type)?.label || type;
    }
    getNodeConfig(workflow, type) {
        return workflow.nodes.find((node) => node.type === type)?.config || {};
    }
    positiveInteger(value, fallback, maximum) {
        const parsed = Number(value);
        if (!Number.isFinite(parsed) || parsed < 1) {
            return fallback;
        }
        return Math.min(Math.floor(parsed), maximum);
    }
    createDefaultWorkflow() {
        const definitions = componentCatalog.filter((component) => [
            'source_pdf',
            'extract_text',
            'clean_text',
            'chunk',
            'metadata',
            'embedding',
            'vector_database',
            'knowledge_base',
            'rag',
            'agent',
        ].includes(component.type));
        const nodes = definitions.map((component, index) => ({
            id: `node-${index + 1}`,
            type: component.type,
            label: component.label,
            config: { ...component.defaultConfig },
            position: { x: 60 + index * 180, y: 130 },
        }));
        const edges = nodes.slice(0, -1).map((node, index) => ({
            id: `edge-${index + 1}`,
            from: node.id,
            to: nodes[index + 1].id,
        }));
        return { nodes, edges };
    }
    createChunks(document, documentIndex, workflow, chunkSize, overlap, dimension) {
        const content = typeof document.content === 'string' ? document.content.trim() : '';
        if (!content) {
            return [];
        }
        const sentences = content.match(/[^.!?]+[.!?]*/g)?.map((sentence) => sentence.trim()).filter(Boolean) || [content];
        const current = [];
        const groups = [];
        let currentLength = 0;
        for (const sentence of sentences) {
            if (current.length && currentLength + sentence.length > chunkSize) {
                groups.push(current);
                current.length = 0;
                currentLength = 0;
            }
            current.push(sentence);
            currentLength += sentence.length + 1;
        }
        if (current.length) {
            groups.push(current);
        }
        const sourceNodeIds = workflow.nodes.filter((node) => node.type === 'chunk' || node.type === 'metadata').map((node) => node.id);
        return groups.map((group, index) => {
            const chunkContent = group.join(' ').trim();
            const documentId = document.id || `document-${documentIndex + 1}`;
            return {
                id: `${documentId}-chunk-${index + 1}`,
                content: chunkContent,
                metadata: {
                    ...(document.metadata || {}),
                    documentId,
                    chunkIndex: index + 1,
                    chunkCount: groups.length,
                    sourceNodeIds,
                },
                embedding: this.embedText(chunkContent, dimension),
                sourceDocumentId: documentId,
                sourceNodeIds,
            };
        });
    }
    embedText(text, dimension) {
        const vector = new Array(dimension).fill(0);
        const tokens = text.toLowerCase().match(/[\p{L}\p{N}]+/gu) || [];
        for (const token of tokens) {
            let hash = 2166136261;
            for (let index = 0; index < token.length; index += 1) {
                hash ^= token.charCodeAt(index);
                hash = Math.imul(hash, 16777619);
            }
            const bucket = Math.abs(hash) % dimension;
            vector[bucket] += 1;
        }
        const magnitude = Math.sqrt(vector.reduce((sum, value) => sum + value * value, 0));
        return magnitude ? vector.map((value) => value / magnitude) : vector;
    }
    cosineSimilarity(a, b) {
        if (a.length !== b.length || !a.length) {
            return 0;
        }
        let dot = 0;
        let magnitudeA = 0;
        let magnitudeB = 0;
        for (let index = 0; index < a.length; index += 1) {
            dot += a[index] * b[index];
            magnitudeA += a[index] * a[index];
            magnitudeB += b[index] * b[index];
        }
        if (!magnitudeA || !magnitudeB) {
            return 0;
        }
        return dot / (Math.sqrt(magnitudeA) * Math.sqrt(magnitudeB));
    }
};
exports.KnowledgeBaseService = KnowledgeBaseService;
exports.KnowledgeBaseService = KnowledgeBaseService = __decorate([
    (0, common_1.Injectable)(),
    __param(0, (0, typeorm_1.InjectRepository)(knowledge_base_entity_1.KnowledgeBaseEntity)),
    __metadata("design:paramtypes", [typeorm_2.Repository])
], KnowledgeBaseService);
//# sourceMappingURL=knowledge-base.service.js.map