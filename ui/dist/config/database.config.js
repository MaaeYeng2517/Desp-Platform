"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.databaseConfig = void 0;
const databaseConfig = () => ({
    host: process.env.DB_HOST || 'localhost',
    port: parseInt(process.env.DB_PORT || '15432', 10),
    username: process.env.DB_USER || 'dataeng',
    password: process.env.DB_PASSWORD || 'dataeng',
    name: process.env.DB_NAME || 'datawarehouse',
    synchronize: process.env.DB_SYNCHRONIZE === 'true',
    logging: process.env.DB_LOGGING === 'true',
});
exports.databaseConfig = databaseConfig;
//# sourceMappingURL=database.config.js.map