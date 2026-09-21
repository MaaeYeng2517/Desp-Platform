import {
  Controller,
  Get,
  Post,
  Body,
  Param,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBody } from '@nestjs/swagger';
import { QualityService, QualityCheck, QualityResult } from './quality.service';

@ApiTags('Data Quality')
@Controller('quality')
export class QualityController {
  constructor(private readonly qualityService: QualityService) {}

  @Get('checks')
  @ApiOperation({ summary: 'Get all defined quality checks' })
  async getChecks(): Promise<QualityCheck[]> {
    return this.qualityService.getChecks();
  }

  @Post('checks')
  @ApiOperation({ summary: 'Add custom quality check' })
  @ApiBody({
    schema: {
      type: 'object',
      properties: {
        name: { type: 'string' },
        description: { type: 'string' },
        query: { type: 'string' },
        threshold: { type: 'number', default: 0 },
        severity: { type: 'string', enum: ['error', 'warning', 'info'], default: 'error' },
      },
      required: ['name', 'description', 'query'],
    },
  })
  async addCheck(@Body() check: QualityCheck): Promise<{ success: boolean }> {
    this.qualityService.addCustomCheck(check);
    return { success: true };
  }

  @Post('checks/:name/remove')
  @ApiOperation({ summary: 'Remove a quality check' })
  async removeCheck(@Param('name') name: string): Promise<{ success: boolean }> {
    this.qualityService.removeCheck(name);
    return { success: true };
  }

  @Get('run')
  @ApiOperation({ summary: 'Run all quality checks' })
  async runAllChecks(): Promise<QualityResult[]> {
    return this.qualityService.runAllChecks();
  }

  @Get('run/by-layer')
  @ApiOperation({ summary: 'Run quality checks grouped by layer' })
  async runChecksByLayer() {
    return this.qualityService.runChecksByLayer();
  }

  @Get('summary')
  @ApiOperation({ summary: 'Get quality check summary' })
  async getSummary() {
    return this.qualityService.getSummary();
  }

  @Get('check/:name')
  @ApiOperation({ summary: 'Run specific quality check' })
  async runSingleCheck(@Param('name') name: string): Promise<QualityResult> {
    const check = this.qualityService.getChecks().find(c => c.name === name);
    if (!check) {
      throw new Error(`Check ${name} not found`);
    }
    return this.qualityService.runCheck(check);
  }
}