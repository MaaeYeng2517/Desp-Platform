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
exports.KnowledgeBaseController = void 0;
const common_1 = require("@nestjs/common");
const swagger_1 = require("@nestjs/swagger");
const knowledge_base_service_1 = require("./knowledge-base.service");
let KnowledgeBaseController = class KnowledgeBaseController {
    constructor(knowledgeBaseService) {
        this.knowledgeBaseService = knowledgeBaseService;
    }
    getCatalog() {
        return this.knowledgeBaseService.getComponentCatalog();
    }
    list() {
        return this.knowledgeBaseService.findAll();
    }
    create(input) {
        return this.knowledgeBaseService.create(input);
    }
    get(id) {
        return this.knowledgeBaseService.findOne(id);
    }
    update(id, input) {
        return this.knowledgeBaseService.update(id, input);
    }
    remove(id) {
        return this.knowledgeBaseService.remove(id);
    }
    validate(id) {
        return this.knowledgeBaseService.validate(id);
    }
    run(id, request) {
        return this.knowledgeBaseService.run(id, request);
    }
    search(id, request) {
        return this.knowledgeBaseService.search(id, request);
    }
    retrieve(id, request) {
        return this.knowledgeBaseService.retrieve(id, request);
    }
    status(id) {
        return this.knowledgeBaseService.getStatus(id);
    }
    createDemo() {
        return this.knowledgeBaseService.createDemo();
    }
};
exports.KnowledgeBaseController = KnowledgeBaseController;
__decorate([
    (0, common_1.Get)('catalog'),
    (0, swagger_1.ApiOperation)({ summary: 'Get draggable workflow components' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", void 0)
], KnowledgeBaseController.prototype, "getCatalog", null);
__decorate([
    (0, common_1.Get)(),
    (0, swagger_1.ApiOperation)({ summary: 'List knowledge bases' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", void 0)
], KnowledgeBaseController.prototype, "list", null);
__decorate([
    (0, common_1.Post)(),
    (0, common_1.HttpCode)(common_1.HttpStatus.CREATED),
    (0, swagger_1.ApiOperation)({ summary: 'Create a knowledge base workflow' }),
    (0, swagger_1.ApiBody)({
        schema: {
            type: 'object',
            properties: {
                name: { type: 'string', example: 'Product Support Knowledge' },
                description: { type: 'string', example: 'Support documentation' },
                metadata: { type: 'object' },
                workflow: { type: 'object' },
            },
            required: ['name'],
        },
    }),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", void 0)
], KnowledgeBaseController.prototype, "create", null);
__decorate([
    (0, common_1.Get)(':id'),
    (0, swagger_1.ApiParam)({ name: 'id', type: 'string' }),
    (0, swagger_1.ApiOperation)({ summary: 'Get a knowledge base' }),
    __param(0, (0, common_1.Param)('id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", void 0)
], KnowledgeBaseController.prototype, "get", null);
__decorate([
    (0, common_1.Patch)(':id'),
    (0, swagger_1.ApiParam)({ name: 'id', type: 'string' }),
    (0, swagger_1.ApiOperation)({ summary: 'Update a knowledge base workflow' }),
    (0, swagger_1.ApiBody)({
        schema: {
            type: 'object',
            properties: {
                name: { type: 'string' },
                description: { type: 'string' },
                metadata: { type: 'object' },
                workflow: { type: 'object' },
            },
            required: ['name'],
        },
    }),
    __param(0, (0, common_1.Param)('id')),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, Object]),
    __metadata("design:returntype", void 0)
], KnowledgeBaseController.prototype, "update", null);
__decorate([
    (0, common_1.Delete)(':id'),
    (0, common_1.HttpCode)(common_1.HttpStatus.NO_CONTENT),
    (0, swagger_1.ApiParam)({ name: 'id', type: 'string' }),
    (0, swagger_1.ApiOperation)({ summary: 'Delete a knowledge base' }),
    __param(0, (0, common_1.Param)('id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", void 0)
], KnowledgeBaseController.prototype, "remove", null);
__decorate([
    (0, common_1.Post)(':id/validate'),
    (0, swagger_1.ApiParam)({ name: 'id', type: 'string' }),
    (0, swagger_1.ApiOperation)({ summary: 'Validate workflow and metadata' }),
    __param(0, (0, common_1.Param)('id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", void 0)
], KnowledgeBaseController.prototype, "validate", null);
__decorate([
    (0, common_1.Post)(':id/run'),
    (0, swagger_1.ApiParam)({ name: 'id', type: 'string' }),
    (0, swagger_1.ApiOperation)({ summary: 'Chunk, embed, and index documents' }),
    (0, swagger_1.ApiBody)({
        schema: {
            type: 'object',
            properties: {
                documents: {
                    type: 'array',
                    items: {
                        type: 'object',
                        properties: {
                            id: { type: 'string' },
                            content: { type: 'string' },
                            metadata: { type: 'object' },
                        },
                        required: ['content'],
                    },
                },
            },
            required: ['documents'],
        },
    }),
    __param(0, (0, common_1.Param)('id')),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, Object]),
    __metadata("design:returntype", void 0)
], KnowledgeBaseController.prototype, "run", null);
__decorate([
    (0, common_1.Post)(':id/search'),
    (0, swagger_1.ApiParam)({ name: 'id', type: 'string' }),
    (0, swagger_1.ApiOperation)({ summary: 'Search indexed chunks by vector similarity' }),
    (0, swagger_1.ApiBody)({
        schema: {
            type: 'object',
            properties: {
                query: { type: 'string' },
                topK: { type: 'number', default: 5 },
            },
            required: ['query'],
        },
    }),
    __param(0, (0, common_1.Param)('id')),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, Object]),
    __metadata("design:returntype", void 0)
], KnowledgeBaseController.prototype, "search", null);
__decorate([
    (0, common_1.Post)(':id/retrieve'),
    (0, swagger_1.ApiParam)({ name: 'id', type: 'string' }),
    (0, swagger_1.ApiOperation)({ summary: 'Retrieve context for a RAG response' }),
    (0, swagger_1.ApiBody)({
        schema: {
            type: 'object',
            properties: {
                query: { type: 'string' },
                topK: { type: 'number', default: 4 },
                systemPrompt: { type: 'string' },
            },
            required: ['query'],
        },
    }),
    __param(0, (0, common_1.Param)('id')),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, Object]),
    __metadata("design:returntype", void 0)
], KnowledgeBaseController.prototype, "retrieve", null);
__decorate([
    (0, common_1.Get)(':id/status'),
    (0, swagger_1.ApiParam)({ name: 'id', type: 'string' }),
    (0, swagger_1.ApiOperation)({ summary: 'Get workflow and vector index status' }),
    __param(0, (0, common_1.Param)('id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", void 0)
], KnowledgeBaseController.prototype, "status", null);
__decorate([
    (0, common_1.Post)('demo'),
    (0, common_1.HttpCode)(common_1.HttpStatus.CREATED),
    (0, swagger_1.ApiOperation)({ summary: 'Create and index a demo knowledge base' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", void 0)
], KnowledgeBaseController.prototype, "createDemo", null);
exports.KnowledgeBaseController = KnowledgeBaseController = __decorate([
    (0, swagger_1.ApiTags)('Knowledge Base Studio'),
    (0, common_1.Controller)('knowledge-base'),
    __metadata("design:paramtypes", [knowledge_base_service_1.KnowledgeBaseService])
], KnowledgeBaseController);
//# sourceMappingURL=knowledge-base.controller.js.map