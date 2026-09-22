"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const core_1 = require("@nestjs/core");
const common_1 = require("@nestjs/common");
const swagger_1 = require("@nestjs/swagger");
const path_1 = require("path");
const app_module_1 = require("./app.module");
async function bootstrap() {
    const app = await core_1.NestFactory.create(app_module_1.AppModule);
    app.enableCors({
        origin: true,
        credentials: true,
    });
    const publicPath = (0, path_1.join)(__dirname, '..', 'public');
    app.useStaticAssets(publicPath);
    app.use('/', (_req, res) => {
        res.sendFile((0, path_1.join)(publicPath, 'index.html'));
    });
    app.use('/studio', (_req, res) => {
        res.sendFile((0, path_1.join)(publicPath, 'index.html'));
    });
    app.useGlobalPipes(new common_1.ValidationPipe({
        whitelist: true,
        transform: true,
        forbidNonWhitelisted: true,
    }));
    app.setGlobalPrefix('api');
    const config = new swagger_1.DocumentBuilder()
        .setTitle('Knowledge Base Studio API')
        .setDescription('Visual knowledge pipeline, metadata, vector search, and RAG API')
        .setVersion('1.0')
        .addBearerAuth()
        .build();
    const document = swagger_1.SwaggerModule.createDocument(app, config);
    swagger_1.SwaggerModule.setup('docs', app, document);
    const port = process.env.PORT || 3000;
    await app.listen(port);
    console.log(`Application running on port ${port}`);
    console.log(`Swagger docs available at http://localhost:${port}/docs`);
}
bootstrap();
//# sourceMappingURL=main.js.map