var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
import { Injectable, } from '@nestjs/common';
import { CronJob } from 'cron';
import { DUPLICATE_SCHEDULER } from './schedule.messages.js';
import { SchedulerRegistry } from './scheduler.registry.js';
let SchedulerOrchestrator = class SchedulerOrchestrator {
    schedulerRegistry;
    cronJobs = {};
    timeouts = {};
    intervals = {};
    constructor(schedulerRegistry) {
        this.schedulerRegistry = schedulerRegistry;
    }
    onApplicationBootstrap() {
        this.mountTimeouts();
        this.mountIntervals();
        this.mountCron();
    }
    beforeApplicationShutdown() {
        this.clearTimeouts();
        this.clearIntervals();
        this.closeCronJobs();
    }
    mountIntervals() {
        const intervalKeys = Object.keys(this.intervals);
        intervalKeys.forEach((key) => {
            const options = this.intervals[key];
            const intervalRef = setInterval(options.target, options.timeout);
            options.ref = intervalRef;
            this.schedulerRegistry.addInterval(key, intervalRef);
        });
    }
    mountTimeouts() {
        const timeoutKeys = Object.keys(this.timeouts);
        timeoutKeys.forEach((key) => {
            const options = this.timeouts[key];
            const timeoutRef = setTimeout(options.target, options.timeout);
            options.ref = timeoutRef;
            this.schedulerRegistry.addTimeout(key, timeoutRef);
        });
    }
    mountCron() {
        const cronKeys = Object.keys(this.cronJobs);
        cronKeys.forEach((key) => {
            const { options, target } = this.cronJobs[key];
            const cronJob = CronJob.from({
                ...options,
                onTick: target,
                start: !options.disabled && !options.initialDelay,
            });
            this.cronJobs[key].ref = cronJob;
            this.schedulerRegistry.addCronJob(key, cronJob);
            if (options.initialDelay && options.initialDelay > 0 && !options.disabled) {
                this.cronJobs[key].initialDelayRef = setTimeout(() => {
                    // Only start the job if it is still the one registered under this
                    // name: the job may have been deleted while the delay was pending,
                    // and a different job may even have been registered under the same
                    // name afterwards. Starting the captured reference would resurrect
                    // the deleted job and run both jobs in parallel.
                    if (this.schedulerRegistry.doesExist('cron', key) &&
                        this.schedulerRegistry.getCronJob(key) === cronJob) {
                        cronJob.start();
                    }
                }, options.initialDelay);
            }
        });
    }
    clearTimeouts() {
        this.schedulerRegistry
            .getTimeouts()
            .forEach((key) => this.schedulerRegistry.deleteTimeout(key));
    }
    clearIntervals() {
        this.schedulerRegistry
            .getIntervals()
            .forEach((key) => this.schedulerRegistry.deleteInterval(key));
    }
    closeCronJobs() {
        Object.values(this.cronJobs).forEach(({ initialDelayRef }) => {
            if (initialDelayRef !== undefined) {
                clearTimeout(initialDelayRef);
            }
        });
        Array.from(this.schedulerRegistry.getCronJobs().keys()).forEach((key) => this.schedulerRegistry.deleteCronJob(key));
    }
    addTimeout(methodRef, timeout, name = crypto.randomUUID()) {
        if (Object.hasOwn(this.timeouts, name)) {
            throw new Error(DUPLICATE_SCHEDULER('Timeout', name));
        }
        this.timeouts[name] = {
            target: methodRef,
            timeout,
        };
    }
    addInterval(methodRef, timeout, name = crypto.randomUUID()) {
        if (Object.hasOwn(this.intervals, name)) {
            throw new Error(DUPLICATE_SCHEDULER('Interval', name));
        }
        this.intervals[name] = {
            target: methodRef,
            timeout,
        };
    }
    addCron(methodRef, options) {
        const name = options.name || crypto.randomUUID();
        if (Object.hasOwn(this.cronJobs, name)) {
            throw new Error(DUPLICATE_SCHEDULER('Cron Job', name));
        }
        this.cronJobs[name] = {
            target: methodRef,
            options,
        };
    }
};
SchedulerOrchestrator = __decorate([
    Injectable(),
    __metadata("design:paramtypes", [SchedulerRegistry])
], SchedulerOrchestrator);
export { SchedulerOrchestrator };
