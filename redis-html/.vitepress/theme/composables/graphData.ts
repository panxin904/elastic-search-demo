// Redis 知识图谱数据 - 60+ 节点 + 关系边
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
    // ============== 01 基础入门 ==============
    { "id": "intro",       "name": "Redis 是什么",        "category": "basics",     "value": 10, "link": "/01-basics/intro" },
    { "id": "install",     "name": "安装部署",            "category": "basics",     "value": 9,  "link": "/01-basics/install" },
    { "id": "datatypes",   "name": "5 大基础类型",        "category": "basics",     "value": 10, "link": "/01-basics/datatypes" },
    { "id": "keys",        "name": "Key 通用操作",        "category": "basics",     "value": 7,  "link": "/01-basics/keys" },
    { "id": "expiration",  "name": "过期策略",            "category": "basics",     "value": 8,  "link": "/01-basics/expiration" },

    // ============== 02 数据结构 ==============
    { "id": "sds",         "name": "SDS 简单动态字符串",   "category": "datastruct", "value": 9,  "link": "/02-datastruct/sds" },
    { "id": "dict",        "name": "Dict 哈希表",         "category": "datastruct", "value": 10, "link": "/02-datastruct/dict" },
    { "id": "skiplist",    "name": "SkipList 跳表",       "category": "datastruct", "value": 10, "link": "/02-datastruct/skiplist" },
    { "id": "listpack",    "name": "Listpack 紧凑列表",   "category": "datastruct", "value": 8,  "link": "/02-datastruct/listpack" },
    { "id": "quicklist",   "name": "QuickList",           "category": "datastruct", "value": 8,  "link": "/02-datastruct/quicklist" },
    { "id": "stream",      "name": "Stream",              "category": "datastruct", "value": 9,  "link": "/02-datastruct/stream" },
    { "id": "object",      "name": "RedisObject",         "category": "datastruct", "value": 8,  "link": "/02-datastruct/object" },

    // ============== 03 持久化 ==============
    { "id": "persist-ov",  "name": "持久化总览",           "category": "persist",    "value": 9,  "link": "/03-persistence/overview" },
    { "id": "rdb",         "name": "RDB 快照",            "category": "persist",    "value": 10, "link": "/03-persistence/rdb" },
    { "id": "aof",         "name": "AOF 日志",            "category": "persist",    "value": 10, "link": "/03-persistence/aof" },
    { "id": "mixed",       "name": "混合持久化",           "category": "persist",    "value": 8,  "link": "/03-persistence/mixed" },
    { "id": "recovery",    "name": "数据恢复策略",         "category": "persist",    "value": 7,  "link": "/03-persistence/recovery" },

    // ============== 04 集群 ==============
    { "id": "replication", "name": "主从复制",             "category": "cluster",    "value": 10, "link": "/04-cluster/replication" },
    { "id": "sentinel",    "name": "Sentinel 哨兵",        "category": "cluster",    "value": 10, "link": "/04-cluster/sentinel" },
    { "id": "cluster",     "name": "Cluster 集群",         "category": "cluster",    "value": 10, "link": "/04-cluster/cluster" },
    { "id": "slots",       "name": "哈希槽分片",           "category": "cluster",    "value": 9,  "link": "/04-cluster/slots" },
    { "id": "gossip",      "name": "Gossip 协议",          "category": "cluster",    "value": 8,  "link": "/04-cluster/gossip" },
    { "id": "migration",   "name": "数据迁移",             "category": "cluster",    "value": 8,  "link": "/04-cluster/migration" },
    { "id": "scale",       "name": "集群扩容",             "category": "cluster",    "value": 7,  "link": "/04-cluster/scale" },

    // ============== 05 Java SDK ==============
    { "id": "jedis",       "name": "Jedis",               "category": "jdk",        "value": 9,  "link": "/05-jdk/jedis" },
    { "id": "lettuce",     "name": "Lettuce",             "category": "jdk",        "value": 9,  "link": "/05-jdk/lettuce" },
    { "id": "redisson",    "name": "Redisson",            "category": "jdk",        "value": 10, "link": "/05-jdk/redisson" },
    { "id": "pool",        "name": "连接池",               "category": "jdk",        "value": 7,  "link": "/05-jdk/connection-pool" },
    { "id": "spring-data", "name": "Spring Data Redis",   "category": "jdk",        "value": 9,  "link": "/05-jdk/spring-data-redis" },
    { "id": "spring-cache","name": "Spring Cache 集成",   "category": "jdk",        "value": 8,  "link": "/05-jdk/spring-cache" },

    // ============== 06 企业实战 ==============
    { "id": "lock",        "name": "分布式锁",             "category": "practice",   "value": 10, "link": "/06-practice/distributed-lock" },
    { "id": "session",     "name": "分布式 Session",       "category": "practice",   "value": 8,  "link": "/06-practice/session" },
    { "id": "global-id",   "name": "全局唯一 ID",          "category": "practice",   "value": 8,  "link": "/06-practice/global-id" },
    { "id": "ratelimit",   "name": "限流",                 "category": "practice",   "value": 9,  "link": "/06-practice/ratelimit" },
    { "id": "dist-rl",     "name": "分布式限流",           "category": "practice",   "value": 9,  "link": "/06-practice/distributed-ratelimit" },
    { "id": "stream-mq",   "name": "Stream 消息队列",      "category": "practice",   "value": 9,  "link": "/06-practice/stream-mq" },
    { "id": "delay-queue", "name": "延迟队列",             "category": "practice",   "value": 8,  "link": "/06-practice/delay-queue" },
    { "id": "leaderboard", "name": "排行榜",               "category": "practice",   "value": 8,  "link": "/06-practice/leaderboard" },
    { "id": "counter",     "name": "计数器",               "category": "practice",   "value": 7,  "link": "/06-practice/counter" },
    { "id": "cache-consist","name": "缓存一致性",          "category": "practice",   "value": 10, "link": "/06-practice/cache-consistency" },

    // ============== 07 运维调优 ==============
    { "id": "eviction",    "name": "内存淘汰策略",         "category": "ops",        "value": 9,  "link": "/07-ops/eviction" },
    { "id": "memory",      "name": "内存管理优化",         "category": "ops",        "value": 8,  "link": "/07-ops/memory" },
    { "id": "bigkey",      "name": "大 Key 热 Key",        "category": "ops",        "value": 9,  "link": "/07-ops/bigkey-hotkey" },
    { "id": "slowlog",     "name": "慢查询分析",           "category": "ops",        "value": 8,  "link": "/07-ops/slowlog" },
    { "id": "monitoring",  "name": "监控告警",             "category": "ops",        "value": 8,  "link": "/07-ops/monitoring" },
    { "id": "redis7",      "name": "Redis 7 新特性",       "category": "ops",        "value": 7,  "link": "/07-ops/redis7-features" },

    // ============== 08 面试手撕题 ==============
    { "id": "iv-basic",    "name": "高频面试题（上）",      "category": "interview",  "value": 9,  "link": "/08-interview/basic" },
    { "id": "iv-advanced", "name": "高频面试题（下）",      "category": "interview",  "value": 9,  "link": "/08-interview/advanced" },
    { "id": "iv-lock",     "name": "分布式锁手撕",          "category": "interview",  "value": 10, "link": "/08-interview/lock-coding" },
    { "id": "iv-lru",      "name": "LRU 算法手撕",          "category": "interview",  "value": 10, "link": "/08-interview/lru" },
    { "id": "iv-skip",     "name": "跳表手撕",              "category": "interview",  "value": 9,  "link": "/08-interview/skiplist-coding" },
    { "id": "iv-avalanche","name": "缓存穿透/击穿/雪崩",   "category": "interview",  "value": 10, "link": "/08-interview/avalanche" },
    { "id": "iv-hash",     "name": "一致性 Hash",           "category": "interview",  "value": 8,  "link": "/08-interview/consistent-hash" },
    { "id": "iv-consensus","name": "Paxos/Raft 概述",      "category": "interview",  "value": 8,  "link": "/08-interview/consensus" }
  ],
  "links": [
    // ====== 基础入门关联 ======
    { "source": "intro",       "target": "install" },
    { "source": "intro",       "target": "datatypes" },
    { "source": "datatypes",   "target": "keys" },
    { "source": "datatypes",   "target": "expiration" },
    { "source": "keys",        "target": "expiration" },

    // ====== 数据结构关联 ======
    { "source": "object",      "target": "datatypes" },
    { "source": "sds",         "target": "object" },
    { "source": "dict",        "target": "object" },
    { "source": "skiplist",    "target": "object" },
    { "source": "listpack",    "target": "object" },
    { "source": "quicklist",   "target": "object" },
    { "source": "stream",      "target": "object" },
    { "source": "dict",        "target": "rehash" } as any,

    // ====== 持久化关联 ======
    { "source": "persist-ov",  "target": "rdb" },
    { "source": "persist-ov",  "target": "aof" },
    { "source": "rdb",         "target": "aof" },
    { "source": "aof",         "target": "mixed" },
    { "source": "rdb",         "target": "mixed" },
    { "source": "mixed",       "target": "recovery" },

    // ====== 集群关联 ======
    { "source": "replication", "target": "sentinel" },
    { "source": "sentinel",    "target": "cluster" },
    { "source": "cluster",     "target": "slots" },
    { "source": "slots",       "target": "gossip" },
    { "source": "gossip",      "target": "migration" },
    { "source": "migration",   "target": "scale" },
    { "source": "cluster",     "target": "scale" },

    // ====== Java SDK 关联 ======
    { "source": "jedis",       "target": "lettuce" },
    { "source": "lettuce",     "target": "redisson" },
    { "source": "jedis",       "target": "pool" },
    { "source": "lettuce",     "target": "pool" },
    { "source": "spring-data", "target": "lettuce" },
    { "source": "spring-data", "target": "jedis" },
    { "source": "spring-cache","target": "spring-data" },
    { "source": "redisson",    "target": "lock" },

    // ====== 企业实战关联 ======
    { "source": "lock",        "target": "ratelimit" },
    { "source": "ratelimit",   "target": "dist-rl" },
    { "source": "global-id",   "target": "counter" },
    { "source": "counter",     "target": "leaderboard" },
    { "source": "stream-mq",   "target": "delay-queue" },
    { "source": "session",     "target": "cache-consistency" },
    { "source": "lock",        "target": "cache-consistency" },

    // ====== 运维关联 ======
    { "source": "eviction",    "target": "memory" },
    { "source": "memory",      "target": "bigkey" },
    { "source": "bigkey",      "target": "slowlog" },
    { "source": "slowlog",     "target": "monitoring" },
    { "source": "redis7",      "target": "eviction" },
    { "source": "redis7",      "target": "memory" },

    // ====== 面试关联 ======
    { "source": "iv-basic",    "target": "iv-advanced" },
    { "source": "iv-lock",     "target": "lock" },
    { "source": "iv-lru",      "target": "dict" },
    { "source": "iv-skip",     "target": "skiplist" },
    { "source": "iv-avalanche","target": "cache-consistency" },
    { "source": "iv-hash",     "target": "cluster" },
    { "source": "iv-consensus","target": "cluster" },

    // ====== 跨域关联 ======
    { "source": "datatypes",   "target": "sds" },
    { "source": "datatypes",   "target": "dict" },
    { "source": "datatypes",   "target": "skiplist" },
    { "source": "stream-mq",   "target": "stream" },
    { "source": "quicklist",   "target": "listpack" },
    { "source": "install",     "target": "cluster" },
    { "source": "intro",       "target": "iv-basic" }
  ]
}
