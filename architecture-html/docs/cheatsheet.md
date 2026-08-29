---
title: 命令速查
date: 2026-08-15  # date-auto-injected
---
# 📋 命令速查

> 30+ 高频命令，分类速查。

## 🔍 排查 / 监控

```bash
# JVM 进程
jps -l                          # 列 Java 进程
jstack <pid>                    # 线程堆栈（找死锁）
jmap -histo:live <pid>          # 对象直方图（找内存泄漏）
jstat -gcutil <pid> 1000 5     # GC 状态 1s 一次 × 5
jcmd <pid> Thread.print          # 同 jstack
jcmd <pid> GC.heap_dump /tmp/dump.hprof

# Arthas（生产诊断神器）
curl -O https://arthas.aliyun.com/arthas-boot.jar
java -jar arthas-boot.jar
# dashboard / thread -n 3 / watch / trace / ognl
```

## 🐰 Kafka

```bash
# 主题
kafka-topics --create --bootstrap-server localhost:9092 \
  --topic orders --partitions 6 --replication-factor 3
kafka-topics --list --bootstrap-server localhost:9092
kafka-topics --delete --bootstrap-server localhost:9092 --topic orders
kafka-topics --describe --bootstrap-server localhost:9092 --topic orders

# 生产 / 消费
kafka-console-producer --bootstrap-server localhost:9092 --topic orders
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic orders --from-beginning --max-messages 10
kafka-consumer-groups --bootstrap-server localhost:9092 --list
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group mygroup --reset-offsets --to-earliest --topic orders

# 性能
kafka-broker-api-versions --bootstrap-server localhost:9092
kafka-producer-perf-test --bootstrap-server localhost:9092 --topic orders ...
kafka-consumer-perf-test --bootstrap-server localhost:9092 --topic orders ...

# 镜像启动（KRaft 模式，KR 1.0+）
docker run -p 9092:9092 apache/kafka:3.8.0 \
  /opt/kafka/bin/kafka-server-start.sh /etc/kafka/server.properties
```

## 🐰 RabbitMQ

```bash
# 启用管理插件
rabbitmq-plugins enable rabbitmq_management

# 命令行
rabbitmqctl status                # 集群状态
rabbitmqctl list_queues           # 列队列
rabbitmqctl list_exchanges
rabbitmqctl list_consumers
rabbitmqctl list_bindings
rabbitmqctl purge_queue myqueue   # 清空队列

# 镜像
docker run -d --name rabbit -p 5672:5672 -p 15672:15672 \
  rabbitmq:3.13-management
# Web UI: http://localhost:15672  (guest/guest)
```

## 🚦 Redis

```bash
redis-cli info                    # 服务器信息
redis-cli info memory             # 内存详细
redis-cli info clients
redis-cli --bigkeys               # 找大 key
redis-cli --memkeys               # 找 memory 占用大的 key
redis-cli monitor                  # 实时监控
redis-cli slowlog get 100          # 慢查询 top 100
redis-cli config get maxmemory

# 集群
redis-cli -c -h <ip> cluster info
redis-cli --cluster create 192.168.1.1:6379 ... --cluster-replicas 1

# 限流 Lua
EVAL "local k=KEYS[1]; local l=tonumber(ARGV[1]); local c=tonumber(ARGV[2]); local cur=redis.call('GET',k); if cur and tonumber(cur)>c then return 0 end; local n=redis.call('INCR',k); if tonumber(n)>l then return 0 end; redis.call('EXPIRE',k,1); return 1 end" 1 rate:user 10 100
```

## 🌐 Nginx

```bash
# 限流
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;

# 限流黑名单
deny 192.168.1.0/24;
allow all;

# 调试
nginx -t                           # 配置检查
nginx -s reload                    # 重新加载
nginx -T 2>/dev/null | grep -A 5 "upstream"
tail -f /var/log/nginx/access.log
```

## 🐳 Docker

```bash
# 资源限制
docker run -d --name app --memory 512m --cpus 1.0 --restart=unless-stopped myapp

# 看资源使用
docker stats
docker top <container>

# 资源审计
docker run --cpuset-cpus="0,1" --cpu-shares=512 myapp
docker run --device-read-bps /dev/sda:1mb  # IO limit

# 容器限速（iptables 替代）
docker run --link-rate=10mb --link-burst=2mb myapp
```

## ☕ JVM / 性能

```bash
# 调优参数
java -Xms1g -Xmx2g \
  -XX:+UseG1GC \
  -XX:MaxGCPauseMillis=200 \
  -XX:+HeapDumpOnOutOfMemoryError \
  -XX:HeapDumpPath=/tmp/oom.hprof \
  -jar app.jar

# Profiler 端口
java -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5005 -jar app.jar
```

## 🏛️ Nacos / Seata

```bash
# Nacos
nacos-server --mode=standalone    # 单机
nacos-server --mode=cluster         # 集群

# Seata server
sh seata-server.sh 8091
```

## 🔗 下一步
- [秒杀系统](/14-enterprise-cases/flash-sale)
- [CAP 定理](/03-ha-theory/cap)
- [分布式事务 2PC](/07-distributed-tx/2pc)