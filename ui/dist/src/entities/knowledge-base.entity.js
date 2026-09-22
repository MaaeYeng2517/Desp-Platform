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
exports.KnowledgeBaseEntity = void 0;
const typeorm_1 = require("typeorm");
let KnowledgeBaseEntity = class KnowledgeBaseEntity {
};
exports.KnowledgeBaseEntity = KnowledgeBaseEntity;
__decorate([
    (0, typeorm_1.PrimaryGeneratedColumn)('uuid'),
    __metadata("design:type", String)
], KnowledgeBaseEntity.prototype, "id", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'name', type: 'varchar', length: 200 }),
    __metadata("design:type", String)
], KnowledgeBaseEntity.prototype, "name", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'description', type: 'text', nullable: true }),
    __metadata("design:type", Object)
], KnowledgeBaseEntity.prototype, "description", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'metadata', type: 'jsonb', nullable: true, default: {} }),
    __metadata("design:type", Object)
], KnowledgeBaseEntity.prototype, "metadata", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'workflow', type: 'jsonb', nullable: true, default: [] }),
    __metadata("design:type", Object)
], KnowledgeBaseEntity.prototype, "workflow", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'chunks', type: 'jsonb', nullable: true, default: [] }),
    __metadata("design:type", Array)
], KnowledgeBaseEntity.prototype, "chunks", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'validation', type: 'jsonb', nullable: true, default: {} }),
    __metadata("design:type", Object)
], KnowledgeBaseEntity.prototype, "validation", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'status', type: 'varchar', length: 30, default: 'draft' }),
    __metadata("design:type", String)
], KnowledgeBaseEntity.prototype, "status", void 0);
__decorate([
    (0, typeorm_1.CreateDateColumn)({ name: 'created_at', type: 'timestamptz' }),
    __metadata("design:type", Date)
], KnowledgeBaseEntity.prototype, "createdAt", void 0);
__decorate([
    (0, typeorm_1.UpdateDateColumn)({ name: 'updated_at', type: 'timestamptz' }),
    __metadata("design:type", Date)
], KnowledgeBaseEntity.prototype, "updatedAt", void 0);
exports.KnowledgeBaseEntity = KnowledgeBaseEntity = __decorate([
    (0, typeorm_1.Entity)({ name: 'knowledge_bases' })
], KnowledgeBaseEntity);
//# sourceMappingURL=knowledge-base.entity.js.map