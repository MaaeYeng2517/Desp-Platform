var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
import { Injectable } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { SCHEDULER_NAME, SCHEDULER_TYPE, SCHEDULE_CRON_OPTIONS, SCHEDULE_INTERVAL_OPTIONS, SCHEDULE_TIMEOUT_OPTIONS, } from './schedule.constants.js';
let SchedulerMetadataAccessor = class SchedulerMetadataAccessor {
    reflector;
    constructor(reflector) {
        this.reflector = reflector;
    }
    getSchedulerType(target) {
        return this.getMetadata(SCHEDULER_TYPE, target);
    }
    getSchedulerName(target) {
        return this.getMetadata(SCHEDULER_NAME, target);
    }
    getTimeoutMetadata(target) {
        return this.getMetadata(SCHEDULE_TIMEOUT_OPTIONS, target);
    }
    getIntervalMetadata(target) {
        return this.getMetadata(SCHEDULE_INTERVAL_OPTIONS, target);
    }
    getCronMetadata(target) {
        return this.getMetadata(SCHEDULE_CRON_OPTIONS, target);
    }
    getMetadata(key, target) {
        const isObject = typeof target === 'object'
            ? target !== null
            : typeof target === 'function';
        return isObject ? this.reflector.get(key, target) : undefined;
    }
};
SchedulerMetadataAccessor = __decorate([
    Injectable(),
    __metadata("design:paramtypes", [Reflector])
], SchedulerMetadataAccessor);
export { SchedulerMetadataAccessor };
