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
exports.RawSale = void 0;
const typeorm_1 = require("typeorm");
let RawSale = class RawSale {
};
exports.RawSale = RawSale;
__decorate([
    (0, typeorm_1.PrimaryColumn)({ name: 'transaction_id', length: 50 }),
    __metadata("design:type", String)
], RawSale.prototype, "transactionId", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'transaction_date', type: 'date' }),
    __metadata("design:type", Date)
], RawSale.prototype, "transactionDate", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'customer_id', length: 50 }),
    __metadata("design:type", String)
], RawSale.prototype, "customerId", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'product_id', length: 50 }),
    __metadata("design:type", String)
], RawSale.prototype, "productId", void 0);
__decorate([
    (0, typeorm_1.Column)({ type: 'int' }),
    __metadata("design:type", Number)
], RawSale.prototype, "quantity", void 0);
__decorate([
    (0, typeorm_1.Column)({ name: 'unit_price', type: 'numeric', precision: 12, scale: 2 }),
    __metadata("design:type", Number)
], RawSale.prototype, "unitPrice", void 0);
__decorate([
    (0, typeorm_1.CreateDateColumn)({ name: 'loaded_at' }),
    __metadata("design:type", Date)
], RawSale.prototype, "loadedAt", void 0);
exports.RawSale = RawSale = __decorate([
    (0, typeorm_1.Entity)({ schema: 'raw', name: 'sales' })
], RawSale);
//# sourceMappingURL=raw-sale.entity.js.map