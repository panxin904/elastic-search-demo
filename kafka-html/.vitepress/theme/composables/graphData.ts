// Kafka 知识图谱数据 - 60+ 节点 + 关系边
export interface GraphNode {
  id: string
  name: string
  category: string
  value: number
  link: string
}

export interface GraphLink {
  source: string
  target: string
}

export interface GraphData {
  nodes: GraphNode[]
  links: GraphLink[]
}

export const graphData: GraphData = {
  "nodes": [
    // ============== 01 入门 ==============
    { "id": "intro",          "name": "Kafka 是什么",          "category": "basics",       "value": 10, "link": "/01-basics/intro" },
    { "id": "install",        "name": "安装部署",                "category": "basics",       "value": 9,  "link": "/01-basics/install" },
    { "id": "concepts",       "name": "核心概念",                "category": "basics",       "value": 10, "link": "/01-basics/concepts" },
    { "id": "topic-part",     "name": "Topic & Partition",       "category": "basics",       "value": 9,  "link": "/01-basics/topic-partition" },
    { "id": "msg-model",      "name": "消息模型",                "category": "basics",       "value": 8,  "link": "/01-basics/message-model" },

    // ============== 02 架构原理 ==============
    { "id": "arch-ov",        "name": "整体架构",                "category": "architecture", "value": 10, "link": "/02-architecture/overview" },
    { "id": "controller",     "name": "Controller 控制器",       "category": "architecture", "value": 9,  "link": "/02-architecture/controller" },
    { "id": "replica",        "name": "分区副本机制",            "category": "architecture", "value": 10, "link": "/02-architecture/replica" },
    { "id": "election",       "name": "Leader 选举",             "category": "architecture", "value": 10, "link": "/02-architecture/leader-election" },
    { "id": "log-storage",    "name": "日志存储",                "category": "architecture", "value": 9,  "link": "/02-architecture/log-storage" },
    { "id": "zero-copy",      "name": "零拷贝原理",              "category": "architecture", "value": 8,  "link": "/02-architecture/zero-copy" },
    { "id": "controller-evo", "name": "控制器演进",              "category": "architecture", "value": 7,  "link": "/02-architecture/controller-evolution" },

    // ============== 03 命令行 ==============
    { "id": "cli-ov",         "name": "常用命令总览",            "category": "cli",          "value": 8,  "link": "/03-cli/overview" },
    { "id": "cli-topic",      "name": "Topic 管理",              "category": "cli",          "value": 9,  "link": "/03-cli/topic" },
    { "id": "cli-prod-cons",  "name": "生产消费调试",            "category": "cli",          "value": 8,  "link": "/03-cli/produce-consume" },
    { "id": "cli-cg",         "name": "消费者组",                "category": "cli",          "value": 8,  "link": "/03-cli/consumer-group" },

    // ============== 04 生产者 ==============
    { "id": "prod-principle", "name": "生产者原理",              "category": "producer",     "value": 9,  "link": "/04-producer/principle" },
    { "id": "send-flow",      "name": "消息发送流程",            "category": "producer",     "value": 9,  "link": "/04-producer/send-flow" },
    { "id": "idempotent",     "name": "幂等性",                  "category": "producer",     "value": 10, "link": "/04-producer/idempotent" },
    { "id": "transaction",    "name": "事务",                    "category": "producer",     "value": 10, "link": "/04-producer/transaction" },
    { "id": "order",          "name": "顺序保证",                "category": "producer",     "value": 9,  "link": "/04-producer/order" },
    { "id": "prod-tuning",    "name": "性能调优",                "category": "producer",     "value": 8,  "link": "/04-producer/tuning" },

    // ============== 05 消费者 ==============
    { "id": "cons-principle", "name": "消费者原理",              "category": "consumer",     "value": 9,  "link": "/05-consumer/principle" },
    { "id": "cons-group",     "name": "消费者组",                "category": "consumer",     "value": 10, "link": "/05-consumer/group" },
    { "id": "offset",         "name": "偏移量提交",              "category": "consumer",     "value": 10, "link": "/05-consumer/offset" },
    { "id": "rebalance",      "name": "再平衡",                  "category": "consumer",     "value": 9,  "link": "/05-consumer/rebalance" },
    { "id": "manual-commit",  "name": "手动提交",                "category": "consumer",     "value": 8,  "link": "/05-consumer/manual-commit" },
    { "id": "multi-thread",   "name": "多线程消费",              "category": "consumer",     "value": 8,  "link": "/05-consumer/multi-thread" },

    // ============== 06 Java SDK ==============
    { "id": "prod-api",       "name": "Producer API",            "category": "jdk",          "value": 9,  "link": "/06-jdk/producer-api" },
    { "id": "cons-api",       "name": "Consumer API",            "category": "jdk",          "value": 9,  "link": "/06-jdk/consumer-api" },
    { "id": "admin-client",   "name": "AdminClient",             "category": "jdk",          "value": 8,  "link": "/06-jdk/admin-client" },
    { "id": "serialization",  "name": "序列化反序列化",          "category": "jdk",          "value": 8,  "link": "/06-jdk/serialization" },
    { "id": "partitioner",    "name": "自定义分区器",            "category": "jdk",          "value": 7,  "link": "/06-jdk/partitioner" },
    { "id": "exception",      "name": "异常处理",                "category": "jdk",          "value": 8,  "link": "/06-jdk/exception" },

    // ============== 07 Spring ==============
    { "id": "spring-intro",   "name": "Spring Kafka 入门",       "category": "spring",       "value": 9,  "link": "/07-spring/intro" },
    { "id": "spring-tpl",     "name": "KafkaTemplate",           "category": "spring",       "value": 9,  "link": "/07-spring/kafka-template" },
    { "id": "spring-listener","name": "@KafkaListener",          "category": "spring",       "value": 10, "link": "/07-spring/listener" },
    { "id": "spring-tx",      "name": "Spring 事务",             "category": "spring",       "value": 8,  "link": "/07-spring/transaction" },
    { "id": "spring-boot",    "name": "Spring Boot 集成",        "category": "spring",       "value": 9,  "link": "/07-spring/spring-boot" },

    // ============== 08 企业实战 ==============
    { "id": "ent-idem",       "name": "消息幂等性",              "category": "enterprise",   "value": 10, "link": "/08-enterprise/idempotent" },
    { "id": "ent-order",      "name": "顺序消费",                "category": "enterprise",   "value": 9,  "link": "/08-enterprise/order-consume" },
    { "id": "ent-delay",      "name": "延迟消息",                "category": "enterprise",   "value": 9,  "link": "/08-enterprise/delay" },
    { "id": "ent-dlq",        "name": "死信队列",                "category": "enterprise",   "value": 8,  "link": "/08-enterprise/dead-letter" },
    { "id": "ent-backlog",    "name": "消息积压",                "category": "enterprise",   "value": 9,  "link": "/08-enterprise/backlog" },
    { "id": "ent-connect",    "name": "Kafka Connect",           "category": "enterprise",   "value": 7,  "link": "/08-enterprise/connect" },
    { "id": "ent-streams",    "name": "Kafka Streams",           "category": "enterprise",   "value": 8,  "link": "/08-enterprise/streams" },
    { "id": "ent-mon",        "name": "监控告警",                "category": "enterprise",   "value": 9,  "link": "/08-enterprise/monitoring" },
    { "id": "ent-env",        "name": "多环境隔离",              "category": "enterprise",   "value": 7,  "link": "/08-enterprise/multi-env" },
    { "id": "ent-cluster",    "name": "集群部署",                "category": "enterprise",   "value": 8,  "link": "/08-enterprise/cluster" },

    // ============== 09 运维 ==============
    { "id": "ops-capacity",   "name": "集群规划",                "category": "ops",          "value": 8,  "link": "/09-ops/capacity" },
    { "id": "ops-bench",      "name": "性能压测",                "category": "ops",          "value": 8,  "link": "/09-ops/benchmark" },
    { "id": "ops-jvm",        "name": "JVM 调优",                "category": "ops",          "value": 8,  "link": "/09-ops/jvm" },
    { "id": "ops-log",        "name": "日志清理",                "category": "ops",          "value": 7,  "link": "/09-ops/log-cleanup" },
    { "id": "ops-metrics",    "name": "监控指标",                "category": "ops",          "value": 8,  "link": "/09-ops/metrics" },
    { "id": "ops-dr",         "name": "故障恢复",                "category": "ops",          "value": 8,  "link": "/09-ops/disaster-recovery" },

    // ============== 10 面试 ==============
    { "id": "iv-basic",       "name": "高频面试题（上）",         "category": "interview",    "value": 9,  "link": "/10-interview/basic" },
    { "id": "iv-advanced",    "name": "高频面试题（下）",         "category": "interview",    "value": 9,  "link": "/10-interview/advanced" },
    { "id": "iv-replica",     "name": "副本同步机制",             "category": "interview",    "value": 10, "link": "/10-interview/replica-sync" },
    { "id": "iv-loss",        "name": "消息丢失解决方案",         "category": "interview",    "value": 10, "link": "/10-interview/message-loss" },
    { "id": "iv-compare",     "name": "Kafka vs RocketMQ",       "category": "interview",    "value": 9,  "link": "/10-interview/kafka-vs-rocketmq" },
    { "id": "iv-election",    "name": "Leader 选举机制",          "category": "interview",    "value": 9,  "link": "/10-interview/election" },
    { "id": "iv-eos",         "name": "Exactly Once 实现",        "category": "interview",    "value": 10, "link": "/10-interview/exactly-once" },
    { "id": "iv-fast",        "name": "Kafka 为什么快",           "category": "interview",    "value": 10, "link": "/10-interview/why-fast" }
  ],
  "links": [
    // ====== 01 入门关联 ======
    { "source": "intro",      "target": "install" },
    { "source": "intro",      "target": "concepts" },
    { "source": "concepts",   "target": "topic-part" },
    { "source": "topic-part", "target": "msg-model" },

    // ====== 02 架构原理关联 ======
    { "source": "arch-ov",    "target": "controller" },
    { "source": "arch-ov",    "target": "replica" },
    { "source": "replica",    "target": "election" },
    { "source": "controller", "target": "controller-evo" },
    { "source": "replica",    "target": "log-storage" },
    { "source": "log-storage","target": "zero-copy" },
    { "source": "arch-ov",    "target": "zero-copy" },

    // ====== 03 命令行关联 ======
    { "source": "cli-ov",     "target": "cli-topic" },
    { "source": "cli-ov",     "target": "cli-prod-cons" },
    { "source": "cli-ov",     "target": "cli-cg" },

    // ====== 04 生产者关联 ======
    { "source": "prod-principle", "target": "send-flow" },
    { "source": "send-flow",      "target": "idempotent" },
    { "source": "idempotent",     "target": "transaction" },
    { "source": "send-flow",      "target": "order" },
    { "source": "transaction",    "target": "prod-tuning" },

    // ====== 05 消费者关联 ======
    { "source": "cons-principle", "target": "cons-group" },
    { "source": "cons-group",     "target": "offset" },
    { "source": "cons-group",     "target": "rebalance" },
    { "source": "offset",         "target": "manual-commit" },
    { "source": "manual-commit",  "target": "multi-thread" },

    // ====== 06 Java SDK 关联 ======
    { "source": "prod-api",    "target": "cons-api" },
    { "source": "prod-api",    "target": "serialization" },
    { "source": "prod-api",    "target": "partitioner" },
    { "source": "cons-api",    "target": "exception" },
    { "source": "prod-api",    "target": "admin-client" },

    // ====== 07 Spring 集成关联 ======
    { "source": "spring-intro",   "target": "spring-tpl" },
    { "source": "spring-tpl",     "target": "spring-listener" },
    { "source": "spring-listener","target": "spring-tx" },
    { "source": "spring-tx",      "target": "spring-boot" },

    // ====== 08 企业实战关联 ======
    { "source": "ent-idem",    "target": "idempotent" },
    { "source": "ent-order",   "target": "order" },
    { "source": "ent-delay",   "target": "msg-model" },
    { "source": "ent-dlq",     "target": "cons-api" },
    { "source": "ent-backlog", "target": "cons-group" },
    { "source": "ent-connect", "target": "admin-client" },
    { "source": "ent-streams", "target": "send-flow" },
    { "source": "ent-mon",     "target": "ops-metrics" },
    { "source": "ent-cluster", "target": "ops-capacity" },

    // ====== 09 运维关联 ======
    { "source": "ops-capacity","target": "ops-bench" },
    { "source": "ops-bench",   "target": "ops-jvm" },
    { "source": "ops-jvm",     "target": "ops-log" },
    { "source": "ops-log",     "target": "ops-metrics" },
    { "source": "ops-metrics", "target": "ops-dr" },

    // ====== 10 面试关联 ======
    { "source": "iv-basic",    "target": "iv-advanced" },
    { "source": "iv-replica",  "target": "replica" },
    { "source": "iv-loss",     "target": "idempotent" },
    { "source": "iv-loss",     "target": "offset" },
    { "source": "iv-compare",  "target": "msg-model" },
    { "source": "iv-election", "target": "election" },
    { "source": "iv-eos",      "target": "transaction" },
    { "source": "iv-eos",      "target": "idempotent" },
    { "source": "iv-fast",     "target": "zero-copy" },

    // ====== 跨域关联 ======
    { "source": "intro",       "target": "arch-ov" },
    { "source": "cli-topic",   "target": "topic-part" },
    { "source": "prod-api",    "target": "spring-tpl" },
    { "source": "cons-api",    "target": "spring-listener" },
    { "source": "ent-cluster", "target": "arch-ov" }
  ]
}
