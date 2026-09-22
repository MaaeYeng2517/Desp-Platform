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
exports.StagingSale = void 0;
const typeorm_1 = require("typeorm");
let StagingSale = class StagingSale {
};
exports.StagingSale = StagingSale;
__decorate([
    (0, typeorm_1.PrimaryColumn)({ name: 'transaction_id', length: 50 }),
    __metadata("design:type", String)
], StagingSale.prototype, "transactionId", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'transaction_date', type: 'date' }),
    __metadata("design:type", Date)
], StagingSale.prototype, "transactionDate", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'customer_id', length: 50 }),
    __metadata("design:type", String)
], StagingSale.prototype, "customerId", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'product_id', length: 50 }),
    __metadata("design:type", String)
], StagingSale.prototype, "productId", void 0);
__decorate([
    (0, typeorm_1.Column)({ type: 'int' }),
    __metadata("design:type", Number)
], StagingSale.prototype, "quantity", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'unit_price', type: 'numeric', precision: 12, scale: 2 }),
    __metadata("design:type", Number)
], StagingSale.prototype, "unitPrice", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'total_amount', type: 'numeric', precision: 14, scale: 2 }),
    __metadata("design:type", Number)
], StagingSale.prototype, "totalAmount", void 0);
exports.StagingSale = StagingSale = __decorate([
    (0, typeorm_1.Entity)({ schema: 'staging', name: 'sales' })
], StagingSale);
//# sourceMappingURL=staging-sale.entity.js.map