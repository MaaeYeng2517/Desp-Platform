import { DynamicModule } from '@nestjs/common';
import { ScheduleModuleAsyncOptions, ScheduleModuleOptions } from './interfaces/schedule-module-options.interface.js';
/**
 * @publicApi
 */
export declare class ScheduleModule {
    static forRoot(options?: ScheduleModuleOptions): DynamicModule;
    static forRootAsync(options: ScheduleModuleAsyncOptions): DynamicModule;
    private static createAsyncProviders;
    private static createAsyncOptionsProvider;
}
