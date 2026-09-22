"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.KafkaService = void 0;
const common_1 = require("@nestjs/common");
const config_1 = require("@nestjs/config");
const kafkajs_1 = require("kafkajs");
let KafkaService = class KafkaService {
    constructor(configService) {
        this.configService = configService;
        this.consumers = new Map();
        const kafkaConfig = {
            clientId: this.configService.get('KAFKA_CLIENT_ID') || 'data-platform',
            brokers: (this.configService.get('KAFKA_BROKERS') || 'localhost:9092').split(','),
            retry: {
                initialRetryTime: 100,
                retries: 8,
            },
        };
        this.kafka = new kafkajs_1.Kafka(kafkaConfig);
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
    async createTopic(topic) {
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
    async listTopics() {
        const admin = this.kafka.admin();
        await admin.connect();
        const topics = await admin.listTopics();
        await admin.disconnect();
        return topics;
    }
    async produce(message) {
        await this.producer.send({
            topic: message.topic,
            messages: message.messages.map(m => ({
                key: m.key,
                value: m.value,
                headers: m.headers,
            })),
        });
    }
    async produceBatch(messages) {
        for (const message of messages) {
            await this.produce(message);
        }
    }
    async consume(topic, groupId, handler, options = {}) {
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
    async getConsumerLag(groupId, topic) {
        const admin = this.kafka.admin();
        await admin.connect();
        const lag = await admin.fetchTopicOffsets(topic);
        await admin.disconnect();
        return lag.reduce((acc, partition) => acc + (Number(partition.high) - Number(partition.low)), 0);
    }
    async getClusterInfo() {
        const admin = this.kafka.admin();
        await admin.connect();
        const brokers = await admin.describeCluster();
        await admin.disconnect();
        return brokers;
    }
    getProducer() {
        return this.producer;
    }
    getKafka() {
        return this.kafka;
    }
};
exports.KafkaService = KafkaService;
exports.KafkaService = KafkaService = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [config_1.ConfigService])
], KafkaService);
//# sourceMappingURL=kafka.service.js.map