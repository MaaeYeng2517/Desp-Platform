import { KnowledgeBaseInput, KnowledgeBaseService, RetrieveKnowledgeBaseRequest, RunKnowledgeBaseRequest, SearchKnowledgeBaseRequest } from './knowledge-base.service';
export declare class KnowledgeBaseController {
    private readonly knowledgeBaseService;
    constructor(knowledgeBaseService: KnowledgeBaseService);
    getCatalog(): import("./knowledge-base.service").ComponentDefinition[];
    list(): Promise<import("../../entities/knowledge-base.entity").KnowledgeBaseEntity[]>;
    create(input: KnowledgeBaseInput): Promise<import("../../entities/knowledge-base.entity").KnowledgeBaseEntity>;
    get(id: string): Promise<import("../../entities/knowledge-base.entity").KnowledgeBaseEntity>;
    update(id: string, input: Partial<KnowledgeBaseInput>): Promise<import("../../entities/knowledge-base.entity").KnowledgeBaseEntity>;
    remove(id: string): Promise<void>;
    validate(id: string): Promise<{
        id: string;
        validation: import("./knowledge-base.service").ValidationResult;
        status: import("../../entities/knowledge-base.entity").KnowledgeBaseEntity["status"];
    }>;
    run(id: string, request: RunKnowledgeBaseRequest): Promise<import("./knowledge-base.service").PipelineRunResult>;
    search(id: string, request: SearchKnowledgeBaseRequest): Promise<{
        query: string;
        results: import("./knowledge-base.service").SearchResult[];
    }>;
    retrieve(id: string, request: RetrieveKnowledgeBaseRequest): Promise<{
        query: string;
        answer: string;
        sources: import("./knowledge-base.service").SearchResult[];
    }>;
    status(id: string): Promise<Record<string, unknown>>;
    createDemo(): Promise<import("./knowledge-base.service").PipelineRunResult>;
}
