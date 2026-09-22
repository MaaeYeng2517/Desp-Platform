"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.appConfig = void 0;
const appConfig = () => ({
    port: parseInt(process.env.PORT || '3000', 10),
    nodeEnv: process.env.NODE_ENV || 'development',
    airflowUrl: process.env.AIRFLOW_URL || 'http://localhost:8080',
    airflowUser: process.env.AIRFLOW_USER || 'airflow',
    airflowPassword: process.env.AIRFLOW_PASSWORD || 'airflow',
});
exports.appConfig = appConfig;
//# sourceMappingURL=app.config.js.map