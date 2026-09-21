import { applyDecorators, SetMetadata } from '@nestjs/common';
import { SchedulerType } from '../enums/scheduler-type.enum.js';
import { SCHEDULE_CRON_OPTIONS, SCHEDULER_NAME, SCHEDULER_TYPE, } from '../schedule.constants.js';
/**
 * Creates a scheduled job.
 * @param cronTime The time to fire off your job. This can be in the form of cron syntax, a JS ```Date``` object or a Luxon ```DateTime``` object.
 * @param options Job execution options.
 *
 * @publicApi
 */
export function Cron(cronTime, options = {}) {
    const name = options?.name;
    return applyDecorators(SetMetadata(SCHEDULE_CRON_OPTIONS, {
        ...options,
        cronTime,
    }), SetMetadata(SCHEDULER_NAME, name), SetMetadata(SCHEDULER_TYPE, SchedulerType.CRON));
}
