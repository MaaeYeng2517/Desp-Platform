export var SchedulerType;
(function (SchedulerType) {
    SchedulerType[SchedulerType["CRON"] = 1] = "CRON";
    SchedulerType[SchedulerType["TIMEOUT"] = 2] = "TIMEOUT";
    SchedulerType[SchedulerType["INTERVAL"] = 3] = "INTERVAL";
})(SchedulerType || (SchedulerType = {}));
