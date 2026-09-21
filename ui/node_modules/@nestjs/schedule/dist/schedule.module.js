var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var ScheduleModule_1;
import { Module } from '@nestjs/common';
import { DiscoveryModule } from '@nestjs/core';
import { SchedulerMetadataAccessor } from './schedule-metadata.accessor.js';
import { ScheduleExplorer } from './schedule.explorer.js';
import { SchedulerOrchestrator } from './scheduler.orchestrator.js';
import { SchedulerRegistry } from './scheduler.registry.js';
import { SCHEDULE_MODULE_OPTIONS } from './schedule.constants.js';
/**
 * @publicApi
 */
let ScheduleModule = ScheduleModule_1 = class ScheduleModule {
    static forRoot(options) {
        const optionsWithDefaults = {
            cronJobs: true,
            intervals: true,
            timeouts: true,
            ...options,
        };
        return {
            global: true,
            module: ScheduleModule_1,
            providers: [
                ScheduleExplorer,
                SchedulerRegistry,
                {
                    provide: SCHEDULE_MODULE_OPTIONS,
                    useValue: optionsWithDefaults,
                },
            ],
            exports: [SchedulerRegistry],
        };
    }
    static forRootAsync(options) {
        return {
            global: true,
            module: ScheduleModule_1,
            imports: options.imports || [],
            providers: [
                ScheduleExplorer,
                SchedulerRegistry,
                ...this.createAsyncProviders(options),
            ],
            exports: [SchedulerRegistry],
        };
    }
    static createAsyncProviders(options) {
        if (options.useExisting || options.useFactory) {
            return [this.createAsyncOptionsProvider(options)];
        }
        const useClass = options.useClass;
        return [
            this.createAsyncOptionsProvider(options),
            {
                provide: useClass,
                useClass: useClass,
            },
        ];
    }
    static createAsyncOptionsProvider(options) {
        if (options.useFactory) {
            return {
                provide: SCHEDULE_MODULE_OPTIONS,
                useFactory: async (...args) => {
                    const config = await options.useFactory(...args);
                    return {
                        cronJobs: true,
                        intervals: true,
                        timeouts: true,
                        ...config,
                    };
                },
                inject: options.inject || [],
            };
        }
        const inject = [
            (options.useClass ||
                options.useExisting),
        ];
        return {
            provide: SCHEDULE_MODULE_OPTIONS,
            useFactory: async (optionsFactory) => {
                const config = await optionsFactory.createScheduleOptions();
                return {
                    cronJobs: true,
                    intervals: true,
                    timeouts: true,
                    ...config,
                };
            },
            inject,
        };
    }
};
ScheduleModule = ScheduleModule_1 = __decorate([
    Module({
        imports: [DiscoveryModule],
        providers: [SchedulerMetadataAccessor, SchedulerOrchestrator],
    })
], ScheduleModule);
export { ScheduleModule };
