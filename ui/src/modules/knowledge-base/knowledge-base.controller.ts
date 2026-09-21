import {
  Body,
  Controller,
  Delete,
  Get,
  HttpCode,
  HttpStatus,
  Param,
  Patch,
  Post,
} from '@nestjs/common';
import { ApiBody, ApiOperation, ApiParam, ApiTags } from '@nestjs/swagger';
import {
  KnowledgeBaseInput,
  KnowledgeBaseService,
  RetrieveKnowledgeBaseRequest,
  RunKnowledgeBaseRequest,
  SearchKnowledgeBaseRequest,
} from './knowledge-base.service';

@ApiTags('Knowledge Base Studio')
@Controller('knowledge-base')
export class KnowledgeBaseController {
  constructor(private readonly knowledgeBaseService: KnowledgeBaseService) {}

  @Get('catalog')
  @ApiOperation({ summary: 'Get draggable workflow components' })
  getCatalog() {
    return this.knowledgeBaseService.getComponentCatalog();
  }

  @Get()
  @ApiOperation({ summary: 'List knowledge bases' })
  list() {
    return this.knowledgeBaseService.findAll();
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Create a knowledge base workflow' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        name: { type: 'string', example: 'Product Support Knowledge' },
        description: { type: 'string', example: 'Support documentation' },
        metadata: { type: 'object' },
        workflow: { type: 'object' },
      },
      required: ['name'],
    },
  })
  create(@Body() input: KnowledgeBaseInput) {
    return this.knowledgeBaseService.create(input);
  }

  @Get(':id')
  @ApiParam({ name: 'id', type: 'string' })
  @ApiOperation({ summary: 'Get a knowledge base' })
  get(@Param('id') id: string) {
    return this.knowledgeBaseService.findOne(id);
  }

  @Patch(':id')
  @ApiParam({ name: 'id', type: 'string' })
  @ApiOperation({ summary: 'Update a knowledge base workflow' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        name: { type: 'string' },
        description: { type: 'string' },
        metadata: { type: 'object' },
        workflow: { type: 'object' },
      },
      required: ['name'],
    },
  })
  update(@Param('id') id: string, @Body() input: Partial<KnowledgeBaseInput>) {
    return this.knowledgeBaseService.update(id, input);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiParam({ name: 'id', type: 'string' })
  @ApiOperation({ summary: 'Delete a knowledge base' })
  remove(@Param('id') id: string) {
    return this.knowledgeBaseService.remove(id);
  }

  @Post(':id/validate')
  @ApiParam({ name: 'id', type: 'string' })
  @ApiOperation({ summary: 'Validate workflow and metadata' })
  validate(@Param('id') id: string) {
    return this.knowledgeBaseService.validate(id);
  }

  @Post(':id/run')
  @ApiParam({ name: 'id', type: 'string' })
  @ApiOperation({ summary: 'Chunk, embed, and index documents' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        documents: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              id: { type: 'string' },
              content: { type: 'string' },
              metadata: { type: 'object' },
            },
            required: ['content'],
          },
        },
      },
      required: ['documents'],
    },
  })
  run(@Param('id') id: string, @Body() request: RunKnowledgeBaseRequest) {
    return this.knowledgeBaseService.run(id, request);
  }

  @Post(':id/search')
  @ApiParam({ name: 'id', type: 'string' })
  @ApiOperation({ summary: 'Search indexed chunks by vector similarity' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        query: { type: 'string' },
        topK: { type: 'number', default: 5 },
      },
      required: ['query'],
    },
  })
  search(@Param('id') id: string, @Body() request: SearchKnowledgeBaseRequest) {
    return this.knowledgeBaseService.search(id, request);
  }

  @Post(':id/retrieve')
  @ApiParam({ name: 'id', type: 'string' })
  @ApiOperation({ summary: 'Retrieve context for a RAG response' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        query: { type: 'string' },
        topK: { type: 'number', default: 4 },
        systemPrompt: { type: 'string' },
      },
      required: ['query'],
    },
  })
  retrieve(@Param('id') id: string, @Body() request: RetrieveKnowledgeBaseRequest) {
    return this.knowledgeBaseService.retrieve(id, request);
  }

  @Get(':id/status')
  @ApiParam({ name: 'id', type: 'string' })
  @ApiOperation({ summary: 'Get workflow and vector index status' })
  status(@Param('id') id: string) {
    return this.knowledgeBaseService.getStatus(id);
  }

  @Post('demo')
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ summary: 'Create and index a demo knowledge base' })
  createDemo() {
    return this.knowledgeBaseService.createDemo();
  }
}
