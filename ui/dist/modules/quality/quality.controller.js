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
exports.QualityController = void 0;
const common_1 = require("@nestjs/common");
const swagger_1 = require("@nestjs/swagger");
const quality_service_1 = require("./quality.service");
let QualityController = class QualityController {
    constructor(qualityService) {
        this.qualityService = qualityService;
    }
    async getChecks() {
        return this.qualityService.getChecks();
    }
    async addCheck(check) {
        this.qualityService.addCustomCheck(check);
        return { success: true };
    }
    async removeCheck(name) {
        this.qualityService.removeCheck(name);
        return { success: true };
    }
    async runAllChecks() {
        return this.qualityService.runAllChecks();
    }
    async runChecksByLayer() {
        return this.qualityService.runChecksByLayer();
    }
    async getSummary() {
        return this.qualityService.getSummary();
    }
    async runSingleCheck(name) {
        const check = this.qualityService.getChecks().find(c => c.name === name);
        if (!check) {
            throw new Error(`Check ${name} not found`);
        }
        return this.qualityService.runCheck(check);
    }
};
exports.QualityController = QualityController;
__decorate([
    (0, common_1.Get)('checks'),
    (0, swagger_1.ApiOperation)({ summary: 'Get all defined quality checks' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], QualityController.prototype, "getChecks", null);
__decorate([
    (0, common_1.Post)('checks'),
    (0, swagger_1.ApiOperation)({ summary: 'Add custom quality check' }),
    (0, swagger_1.ApiBody)({
        schema: {
            type: 'object',
            properties: {
                name: { type: 'string' },
                description: { type: 'string' },
                query: { type: 'string' },
                threshold: { type: 'number', default: 0 },
                severity: { type: 'string', enum: ['error', 'warning', 'info'], default: 'error' },
            },
            required: ['name', 'description', 'query'],
        },
    }),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", Promise)
], QualityController.prototype, "addCheck", null);
__decorate([
    (0, common_1.Post)('checks/:name/remove'),
    (0, swagger_1.ApiOperation)({ summary: 'Remove a quality check' }),
    __param(0, (0, common_1.Param)('name')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], QualityController.prototype, "removeCheck", null);
__decorate([
    (0, common_1.Get)('run'),
    (0, swagger_1.ApiOperation)({ summary: 'Run all quality checks' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], QualityController.prototype, "runAllChecks", null);
__decorate([
    (0, common_1.Get)('run/by-layer'),
    (0, swagger_1.ApiOperation)({ summary: 'Run quality checks grouped by layer' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], QualityController.prototype, "runChecksByLayer", null);
__decorate([
    (0, common_1.Get)('summary'),
    (0, swagger_1.ApiOperation)({ summary: 'Get quality check summary' }),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", Promise)
], QualityController.prototype, "getSummary", null);
__decorate([
    (0, common_1.Get)('check/:name'),
    (0, swagger_1.ApiOperation)({ summary: 'Run specific quality check' }),
    __param(0, (0, common_1.Param)('name')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], QualityController.prototype, "runSingleCheck", null);
exports.QualityController = QualityController = __decorate([
    (0, swagger_1.ApiTags)('Data Quality'),
    (0, common_1.Controller)('quality'),
    __metadata("design:paramtypes", [quality_service_1.QualityService])
], QualityController);
//# sourceMappingURL=quality.controller.js.map