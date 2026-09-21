import { applyDecorators, SetMetadata } from '@nestjs/common';
import { SchedulerType } from '../enums/scheduler-type.enum.js';
import { SCHEDULER_NAME, SCHEDULER_TYPE, SCHEDULE_TIMEOUT_OPTIONS, } from '../schedule.constants.js';
/**
 * Schedules a timeout (`setTimeout`).
 *
 * @publicApi
 */
export function Timeout(nameOrTimeout, timeout) {
    const [name, timeoutValue] = typeof nameOrTimeout === 'string'
        ? [nameOrTimeout, timeout]
        : [undefined, nameOrTimeout];
    return applyDecorators(SetMetadata(SCHEDULE_TIMEOUT_OPTIONS, { timeout: timeoutValue }), SetMetadata(SCHEDULER_NAME, name), SetMetadata(SCHEDULER_TYPE, SchedulerType.TIMEOUT));
}
