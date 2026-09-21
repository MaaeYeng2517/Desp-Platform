export const databaseConfig = () => ({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '15432', 10),
  username: process.env.DB_USER || 'dataeng',
  password: process.env.DB_PASSWORD || 'dataeng',
  name: process.env.DB_NAME || 'datawarehouse',
  synchronize: process.env.DB_SYNCHRONIZE === 'true',
  logging: process.env.DB_LOGGING === 'true',
});