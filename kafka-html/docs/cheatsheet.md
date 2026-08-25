---
title: 命令速查
---

# 📋 Kafka 命令速查

> 30+ 高频 Kafka 命令，支持分类过滤和关键词搜索。

<ClientOnly>
  <CommandCheatsheet />
</ClientOnly>

## 🧰 常用场景快速索引

| 场景 | 命令 |
|------|------|
| 创建 Topic | `kafka-topics.sh --create --topic <name> --partitions 3 --replication-factor 2` |
| 查看 Topic | `kafka-topics.sh --describe --topic <name>` |
| 命令行生产 | `kafka-console-producer.sh --broker-list <host:port> --topic <name>` |
| 命令行消费 | `kafka-console-consumer.sh --bootstrap-server <host:port> --topic <name> --from-beginning` |
| 查看消费者组 | `kafka-consumer-groups.sh --list` |
| 查看消费进度 | `kafka-consumer-groups.sh --describe --group <name>` |
| 重置 Offset | `kafka-consumer-groups.sh --reset-offsets --to-earliest --topic <name> --execute` |
| 分区扩容 | `kafka-reassign-partitions.sh --reassignment-json-file <file> --execute` |
| 修改 Broker 配置 | `kafka-configs.sh --alter --add-config <key>=<value>` |
| 查看 ACL | `kafka-acls.sh --list` |

## 📚 跨站参考：🧰 常用场景快速索引

<!-- xlink-dedup:do-not-edit -->

本节在 3 站展开，最权威版本位于 **redis** 站（[https://java-px.bot.cd/redis/](https://java-px.bot.cd/redis/)）。

其他站参考：[kafka](https://java-px.bot.cd/kafka/) / [python](https://java-px.bot.cd/python/)

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。
