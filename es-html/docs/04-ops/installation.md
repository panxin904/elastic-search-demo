---
title: 安装部署
date: 2026-08-15  # date-auto-injected
category: ops
graphNodeId: installation
---

<span class="kg-badge kg-badge-ops">运维层</span>

# 安装部署 Installation

## 📌 三种主要部署方式

| 方式 | 适用 | 难度 |
|---|---|---|
| **Tar 包** | 生产环境、定制化 | ⭐⭐⭐ |
| **Docker** | 快速试用、容器化 | ⭐⭐ |
| **RPM/DEB** | 传统服务器 | ⭐⭐ |

## 🔧 Tar 包单机部署

```bash
# 下载
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.10-linux-x86_64.tar.gz

# 解压
tar -xzf elasticsearch-7.17.10-linux-x86_64.tar.gz
cd elasticsearch-7.17.10

# 禁用安全特性（开发环境）
echo "xpack.security.enabled: false" >> config/elasticsearch.yml

# 启动（不能用 root）
useradd esuser
chown -R esuser:esuser /opt/elasticsearch-7.17.10
su esuser -c "./bin/elasticsearch -d"
```

> ⚠️ ES **不能用 root 启动**（出于安全考虑）

## 🔧 Docker 单机

```bash
docker run -d --name es \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  -v /data/es:/usr/share/elasticsearch/data \
  elasticsearch:7.17.10
```

## 🔧 Docker Compose 集群 (3 节点)

```yaml
version: '3'
services:
  es01:
    image: elasticsearch:7.17.10
    environment:
      - cluster.name=es-cluster
      - node.name=es01
      - discovery.seed_hosts=es02,es03
      - cluster.initial_master_nodes=es01,es02,es03
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    ulimits:
      memlock: { soft: -1, hard: -1 }
    volumes: [ ./data/es01:/usr/share/elasticsearch/data ]
    ports: [ "9200:9200" ]
  es02: { ... }
  es03: { ... }
```

## 🔗 对应项目 Testcontainers

本项目使用 Testcontainers 启动 ES 容器跑集成测试：

```java
@Testcontainers
class ElasticsearchServiceTest {
    @Container
    static ElasticsearchContainer container =
        new ElasticsearchContainer("docker.elastic.co/elasticsearch/elasticsearch:7.17.10");
}
```

## ⚙️ 核心配置 (elasticsearch.yml)

```yaml
cluster.name: es-prod
node.name: ${HOSTNAME}
network.host: 0.0.0.0
http.port: 9200
discovery.seed_hosts: ["es01", "es02", "es03"]
cluster.initial_master_nodes: ["es01", "es02", "es03"]
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="installation" :height="400" />

## 📚 延伸阅读
- [JVM 调优](/04-ops/jvm-tuning)
- [集群重启](/04-ops/restart)
