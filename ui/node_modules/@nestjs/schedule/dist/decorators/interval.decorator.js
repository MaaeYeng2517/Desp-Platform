import { applyDecorators, SetMetadata } from '@nestjs/common';
import { SchedulerType } from '../enums/scheduler-type.enum.js';
import { SCHEDULER_NAME, SCHEDULER_TYPE, SCHEDULE_INTERVAL_OPTIONS, } from '../schedule.constants.js';
/**
 * Schedules an interval (`setInterval`).
 *
 * @publicApi
 */
export function Interval(nameOrTimeout, timeout) {
    const [name, intervalTimeout] = typeof nameOrTimeout === 'string'
        ? [nameOrTimeout, timeout]
        : [undefined, nameOrTimeout];
    return applyDecorators(SetMetadata(SCHEDULE_INTERVAL_OPTIONS, { timeout: intervalTimeout }), SetMetadata(SCHEDULER_NAME, name), SetMetadata(SCHEDULER_TYPE, SchedulerType.INTERVAL));
}
