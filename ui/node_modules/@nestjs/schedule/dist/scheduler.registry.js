var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var SchedulerRegistry_1;
import { Injectable, Logger } from '@nestjs/common';
import { DUPLICATE_SCHEDULER, NO_SCHEDULER_FOUND } from './schedule.messages.js';
let SchedulerRegistry = SchedulerRegistry_1 = class SchedulerRegistry {
    logger = new Logger(SchedulerRegistry_1.name);
    cronJobs = new Map();
    timeouts = new Map();
    intervals = new Map();
    doesExist(type, name) {
        switch (type) {
            case 'cron':
                return this.cronJobs.has(name);
            case 'interval':
                return this.intervals.has(name);
            case 'timeout':
                return this.timeouts.has(name);
            default:
                return false;
        }
    }
    getCronJob(name) {
        const ref = this.cronJobs.get(name);
        if (!ref) {
            throw new Error(NO_SCHEDULER_FOUND('Cron Job', name));
        }
        return ref;
    }
    getInterval(name) {
        const ref = this.intervals.get(name);
        if (typeof ref === 'undefined') {
            throw new Error(NO_SCHEDULER_FOUND('Interval', name));
        }
        return ref;
    }
    getTimeout(name) {
        const ref = this.timeouts.get(name);
        if (typeof ref === 'undefined') {
            throw new Error(NO_SCHEDULER_FOUND('Timeout', name));
        }
        return ref;
    }
    addCronJob(name, job) {
        const ref = this.cronJobs.get(name);
        if (ref) {
            throw new Error(DUPLICATE_SCHEDULER('Cron Job', name));
        }
        job.fireOnTick = this.wrapFunctionInTryCatchBlocks(job.fireOnTick, job);
        this.cronJobs.set(name, job);
    }
    addInterval(name, intervalId) {
        const ref = this.intervals.get(name);
        if (ref) {
            throw new Error(DUPLICATE_SCHEDULER('Interval', name));
        }
        this.intervals.set(name, intervalId);
    }
    addTimeout(name, timeoutId) {
        const ref = this.timeouts.get(name);
        if (ref) {
            throw new Error(DUPLICATE_SCHEDULER('Timeout', name));
        }
        this.timeouts.set(name, timeoutId);
    }
    getCronJobs() {
        return this.cronJobs;
    }
    deleteCronJob(name) {
        const cronJob = this.getCronJob(name);
        cronJob.stop();
        this.cronJobs.delete(name);
    }
    getIntervals() {
        return [...this.intervals.keys()];
    }
    deleteInterval(name) {
        const interval = this.getInterval(name);
        clearInterval(interval);
        this.intervals.delete(name);
    }
    getTimeouts() {
        return [...this.timeouts.keys()];
    }
    deleteTimeout(name) {
        const timeout = this.getTimeout(name);
        clearTimeout(timeout);
        this.timeouts.delete(name);
    }
    wrapFunctionInTryCatchBlocks(methodRef, instance) {
        return async (...args) => {
            try {
                await methodRef.call(instance, ...args);
            }
            catch (error) {
                this.logger.error(error);
            }
        };
    }
};
SchedulerRegistry = SchedulerRegistry_1 = __decorate([
    Injectable()
], SchedulerRegistry);
export { SchedulerRegistry };
