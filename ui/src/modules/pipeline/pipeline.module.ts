import { Module } from '@nestjs/common';
import { PipelineController } from './pipeline.controller';
import { PipelineService } from './pipeline.service';
import { AirflowService } from './airflow.service';
import { KafkaService } from './kafka.service';
import { SparkService } from './spark.service';
import { DockerService } from './docker.service';

@Module({
  controllers: [PipelineController],
  providers: [PipelineService, AirflowService, KafkaService, SparkService, DockerService],
  exports: [PipelineService, AirflowService, KafkaService, SparkService, DockerService],
})
export class PipelineModule {}