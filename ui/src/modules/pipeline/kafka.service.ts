import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Kafka, Producer, Consumer, EachMessagePayload, KafkaConfig } from 'kafkajs';

export interface KafkaTopic {
  name: string;
  partitions: number;
  replicationFactor: number;
}

export interface ProduceMessage {
  topic: string;
  messages: Array<{
    key?: string;
    value: string;
    headers?: Record<string, string>;
  }>;
}

@Injectable()
export class KafkaService implements OnModuleInit, OnModuleDestroy {
  private kafka: Kafka;
  private producer: Producer;
  private consumers: Map<string, Consumer> = new Map();

  constructor(private configService: ConfigService) {
    const kafkaConfig: KafkaConfig = {
      clientId: this.configService.get('KAFKA_CLIENT_ID') || 'data-platform',
      brokers: (this.configService.get('KAFKA_BROKERS') || 'localhost:9092').split(','),
      retry: {
        initialRetryTime: 100,
        retries: 8,
      },
    };

    this.kafka = new Kafka(kafkaConfig);
    this.producer = this.kafka.producer();
  }

  async onModuleInit() {
    await this.producer.connect();
  }

  async onModuleDestroy() {
    await this.producer.disconnect();
    for (const consumer of this.consumers.values()) {
      await consumer.disconnect();
    }
  }

  async createTopic(topic: KafkaTopic): Promise<void> {
    const admin = this.kafka.admin();
    await admin.connect();
    await admin.createTopics({
      topics: [{
        topic: topic.name,
        numPartitions: topic.partitions,
        replicationFactor: topic.replicationFactor,
      }],
      waitForLeaders: true,
    });
    await admin.disconnect();
  }

  async listTopics(): Promise<string[]> {
    const admin = this.kafka.admin();
    await admin.connect();
    const topics = await admin.listTopics();
    await admin.disconnect();
    return topics;
  }

  async produce(message: ProduceMessage): Promise<void> {
    await this.producer.send({
      topic: message.topic,
      messages: message.messages.map(m => ({
        key: m.key,
        value: m.value,
        headers: m.headers,
      })),
    });
  }

  async produceBatch(messages: ProduceMessage[]): Promise<void> {
    for (const message of messages) {
      await this.produce(message);
    }
  }

  async consume(
    topic: string,
    groupId: string,
    handler: (payload: EachMessagePayload) => Promise<void>,
    options: { fromBeginning?: boolean } = {}
  ): Promise<void> {
    const consumer = this.kafka.consumer({ groupId });
    await consumer.connect();
    await consumer.subscribe({ topic, fromBeginning: options.fromBeginning || false });
    
    await consumer.run({
      eachMessage: async (payload) => {
        await handler(payload);
      },
    });

    this.consumers.set(`${topic}-${groupId}`, consumer);
  }

  async getConsumerLag(groupId: string, topic: string): Promise<number> {
    const admin = this.kafka.admin();
    await admin.connect();
    const lag = await admin.fetchTopicOffsets(topic);
    await admin.disconnect();
    return lag.reduce((acc, partition) => acc + (Number(partition.high) - Number(partition.low)), 0);
  }

  async getClusterInfo(): Promise<{ brokers: any[]; controller: any }> {
    const admin = this.kafka.admin();
    await admin.connect();
    const brokers = await admin.describeCluster();
    await admin.disconnect();
    return brokers;
  }

  getProducer(): Producer {
    return this.producer;
  }

  getKafka(): Kafka {
    return this.kafka;
  }
}