"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.QualityModule = void 0;
const common_1 = require("@nestjs/common");
const typeorm_1 = require("@nestjs/typeorm");
const quality_controller_1 = require("./quality.controller");
const quality_service_1 = require("./quality.service");
const mart_sale_entity_1 = require("../entities/mart-sale.entity");
const staging_sale_entity_1 = require("../entities/staging-sale.entity");
const raw_sale_entity_1 = require("../entities/raw-sale.entity");
let QualityModule = class QualityModule {
};
exports.QualityModule = QualityModule;
exports.QualityModule = QualityModule = __decorate([
    (0, common_1.Module)({
        imports: [typeorm_1.TypeOrmModule.forFeature([mart_sale_entity_1.MartSale, staging_sale_entity_1.StagingSale, raw_sale_entity_1.RawSale])],
        controllers: [quality_controller_1.QualityController],
        providers: [quality_service_1.QualityService],
        exports: [quality_service_1.QualityService],
    })
], QualityModule);
//# sourceMappingURL=quality.module.js.map