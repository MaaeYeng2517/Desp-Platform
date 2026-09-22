import { OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Kafka, Producer, EachMessagePayload } from 'kafkajs';
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
export declare class KafkaService implements OnModuleInit, OnModuleDestroy {
    private configService;
    private kafka;
    private producer;
    private consumers;
    constructor(configService: ConfigService);
    onModuleInit(): Promise<void>;
    onModuleDestroy(): Promise<void>;
    createTopic(topic: KafkaTopic): Promise<void>;
    listTopics(): Promise<string[]>;
    produce(message: ProduceMessage): Promise<void>;
    produceBatch(messages: ProduceMessage[]): Promise<void>;
    consume(topic: string, groupId: string, handler: (payload: EachMessagePayload) => Promise<void>, options?: {
        fromBeginning?: boolean;
    }): Promise<void>;
    getConsumerLag(groupId: string, topic: string): Promise<number>;
    getClusterInfo(): Promise<{
        brokers: any[];
        controller: any;
    }>;
    getProducer(): Producer;
    getKafka(): Kafka;
}
