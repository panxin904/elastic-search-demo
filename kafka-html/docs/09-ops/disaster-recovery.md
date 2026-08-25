---
title: 故障恢复
---

# 🚑 故障恢复

> **故障恢复（Disaster Recovery）**是生产环境 Kafka 的最后一道防线。本章详解常见故障的恢复方案。

## 🎯 故障分类

```
Kafka 故障分类：
  1. Broker 故障（最常见）
  2. 磁盘故障
  3. 网络故障
  4. ZooKeeper/KRaft 故障
  5. 数据丢失/损坏
  6. 集群完全不可用（机房级故障）
```

## 🔧 故障 1：Broker 故障

### 现象

```
- 该 Broker 上的所有 Partition 不可用（如果是 Leader）
- Kafka 自动触发 Leader 选举
- Follower 提升为新 Leader
- Producer/Consumer 收到 LeaderNotAvailableException
```

### 自动恢复（无需干预）

```
1. Controller 检测到 Broker 失联
2. 从 ISR 中选择新 Leader
3. 更新元数据
4. 通知所有 Producer/Consumer
5. 自动恢复

时长：通常 5-15 秒
```

### 手动恢复步骤

```bash
# 1. 确认 Broker 真的宕机
ps aux | grep kafka | grep <broker-id>
# 无输出 = 真的宕机

# 2. 查看 Broker 日志
tail -f /var/log/kafka/server.log | grep ERROR

# 3. 确认 Partition 状态
kafka-topics.sh --describe --bootstrap-server localhost:9092 \
    --topic orders | grep "Isr"

# 4. 等待自动恢复（5-15 秒）

# 5. 如果未自动恢复，重启 Broker
systemctl restart kafka

# 6. 验证恢复
kafka-broker-api-versions.sh --bootstrap-server localhost:9092
kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic orders
```

### 故障后检查清单

```markdown
✅ Kafka 服务恢复（systemctl status kafka）
✅ Broker 加入集群（CLUSTER INFO）
✅ 所有 Partition 有 Leader
✅ 所有 Partition 有足够 ISR
✅ Consumer Lag 恢复正常
✅ Producer 错误率回到 0
✅ 数据完整性（如有必要）
```

## 🔧 故障 2：磁盘故障

### 现象

```
- 写入失败（No space left on device）
- 磁盘读取错误（I/O error）
- Broker 自动停止
```

### 恢复步骤

```bash
# 1. 立即停止写入（避免数据损坏）
# （Kafka 会自动停止，但手动更安全）
systemctl stop kafka

# 2. 备份数据（如果有救）
mkdir -p /backup/kafka-logs-$(date +%Y%m%d)
cp -r /data/kafka-logs/* /backup/kafka-logs-*/

# 3. 更换磁盘

# 4. 恢复数据（如果有备份）
cp -r /backup/kafka-logs-/* /data/kafka-logs/

# 5. 重启 Kafka
systemctl start kafka

# 6. 验证
kafka-log-dirs.sh --bootstrap-server localhost:9092 \
    --describe --broker-list <broker-id>
```

### 预防措施

```bash
# 1. RAID 配置（RAID 10 推荐）
mdadm --create /dev/md0 --level=10 --raid-devices=4 /dev/sd[abcd]

# 2. 多磁盘分散（log.dirs 多路径）
log.dirs=/data1/kafka-logs,/data2/kafka-logs,/data3/kafka-logs

# 3. 监控磁盘
alert: KafkaDiskUsageHigh > 80%

# 4. 定期备份
# （详见"备份策略"）
```

## 🔧 故障 3：网络故障

### 现象

```
- Producer 报 TimeoutException、NetworkException
- Consumer 报 FetchFailedException
- 副本同步延迟
- Rebalance 频繁
```

### 恢复步骤

```bash
# 1. 检查网络连接
ping <broker-ip>
telnet <broker-ip> 9092
traceroute <broker-ip>

# 2. 检查 DNS
nslookup kafka-1
dig kafka-1

# 3. 检查防火墙
iptables -L -n
firewall-cmd --list-all

# 4. 检查网络配置
ifconfig
ip route

# 5. 切换网络（如有备用）
```

### 网络分区处理

```bash
# 场景：机房内网络分区（部分 Broker 失联）

# 1. 等待网络恢复（Kafka 会自动重连）

# 2. 如果长时间不恢复
#    - 检查 ISR 是否收缩
kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic orders

#    - 修复网络后 ISR 会自动恢复
```

## 🔧 故障 4：Controller 故障

### 现象

```
- 无法创建 / 删除 Topic
- 无法扩容（增加 Partition）
- 集群元数据不可用
- Producer/Consumer 可能报错
```

### 自动恢复（KRaft）

```
KRaft 模式下：
  - Active Controller 宕机
  - Standby Controller 发起选举
  - 新 Controller 接管
  - 通常 1-5 秒恢复

⚠️ 选举期间无法修改元数据（但读写不受影响）
```

### 手动恢复

```bash
# 1. 查看 Controller 状态
kafka-metadata-quorum.sh --bootstrap-server localhost:9092 \
    describe --status

# 2. 如果选举卡住
#    - 重启所有 Controller 节点
systemctl restart kafka

# 3. 验证 Controller 已选举
kafka-controller-status.sh --bootstrap-server localhost:9092
```

## 🔧 故障 5：数据丢失

### 场景 1：未设置 min.insync.replicas

```
现象：acks=all + replication.factor=3 + min.insync.replicas=1
     → 仅 Leader 写入即可（其他 Follower 异步同步）
     → 如果 Leader 故障，Follower 数据可能落后 → 数据丢失

解决：
  设置 min.insync.replicas=2（保证 2 副本写入）
```

### 场景 2：自动提交 offset 过早

```
现象：Consumer 自动提交后崩溃，处理逻辑未执行 → 数据丢失

解决：
  1. 关闭自动提交
  2. 处理完再手动提交
  3. 或使用事务
```

### 场景 3：磁盘损坏未备份

```
现象：磁盘物理损坏，log 文件丢失

解决：
  1. 多副本（避免单点）
  2. 远程备份
  3. 跨机房复制（MirrorMaker 2.0）
```

### 数据恢复策略

```bash
# 1. 从多副本恢复（自动）
#    - 其他 Broker 上的副本还在
#    - 重新加入集群后自动同步

# 2. 从备份恢复
#    - 定期全量备份（RDB / tar）
#    - 异地容灾（MirrorMaker / 对象存储）

# 3. 从源数据恢复
#    - 数据库 → Kafka（CDC 重新导入）
#    - 日志重放（log-shipper）
```

## 🔧 故障 6：集群完全不可用

### 现象

```
- 所有 Broker 宕机
- 机房故障（网络、电力、空调）
- KRaft 集群无 Controller（少数派）
```

### 恢复步骤

```bash
# 1. 启动应急恢复模式（少数派不可用时）

# 2. 强制单节点启动（破坏性，最后手段）
# ⚠️ 仅在所有副本都不可用时使用
# 编辑 server.properties
unclean.leader.election.enable=true

# 3. 启动所有 Broker
systemctl start kafka

# 4. 验证数据
kafka-log-dirs.sh --bootstrap-server localhost:9092 \
    --describe --broker-list 1,2,3

# 5. 修复集群（恢复副本同步）
#    - 通常会自动恢复
#    - 检查 ISR 是否完整

# 6. 关闭 unclean.leader.election
unclean.leader.election.enable=false
```

## 🛠️ 备份策略

### 1. 数据备份

```bash
#!/bin/bash
# kafka-backup.sh
# 每天凌晨 3 点执行全量备份

BACKUP_DIR=/backup/kafka/$(date +%Y%m%d)
mkdir -p $BACKUP_DIR

# 备份 Kafka 数据目录
rsync -av /data/kafka-logs/ $BACKUP_DIR/

# 保留最近 7 天的备份
find /backup/kafka -mtime +7 -delete

# 上传到对象存储
aws s3 sync $BACKUP_DIR s3://kafka-backup/$(date +%Y%m%d)/
```

### 2. 配置备份

```bash
# 备份 Kafka 配置
cp /opt/kafka/config/*.properties /backup/config-$(date +%Y%m%d)/

# 版本控制（推荐）
cd /etc/kafka
git init
git add *.properties
git commit -m "Kafka config backup"
```

### 3. Schema 备份

```bash
# Schema Registry 备份
curl -X GET http://schema-registry:8081/subjects | jq > schema-subjects.json
```

## 🛠️ 灾难恢复（DR）

### 跨机房容灾架构

```
机房 A（主）               机房 B（备）
─────────                ─────────
Broker 1, 2, 3          Broker 4, 5, 6
     │                       ↑
     │      MirrorMaker 2.0    │
     └─────────────────────┘
```

### MirrorMaker 2.0 配置

```properties
# mm2.properties
clusters=primary,standby

primary.bootstrap.servers=primary-kafka:9092
standby.bootstrap.servers=standby-kafka:9092

# 主 → 备（关键业务）
primary->standby.enabled=true
primary->standby.topics=orders,payments,users
primary->standby.topics.excluded=__.*

# 备 → 主（避免反向回流）
standby->primary.enabled=false

# 配置
replication.factor=3
offset.sync.topic.replication.factor=3
```

### 机房切换

```bash
# 1. 停止 MirrorMaker（避免双向复制）
bin/connect-mirror-maker.sh stop mm2.properties

# 2. 客户端切换到备机房
#    修改应用配置：bootstrap-servers 改为 standby-kafka:9092

# 3. 启动 MirrorMaker（反向复制）
#    修改 mm2 配置：standby → primary

# 4. 主机房恢复后切回
```

## 📊 故障演练

### 定期演练（推荐）

```markdown
✅ 月度：Broker 故障演练
   - 模拟 Kill Broker
   - 验证自动恢复
   - 检查告警是否触发

✅ 季度：网络分区演练
   - 模拟网络分区
   - 验证 ISR 行为
   - 检查客户端降级

✅ 半年度：机房切换演练
   - 模拟主机房故障
   - 切换到备机房
   - 验证业务可用性

✅ 年度：完整灾难恢复演练
   - 完整数据恢复
   - 验证 SLA
```

### 故障演练脚本

```bash
#!/bin/bash
# kafka-drill.sh
# 模拟 Broker 故障

echo "=== 开始故障演练 ==="

# 1. 记录当前状态
echo "当前 Lag:"
kafka-consumer-groups.sh --describe --bootstrap-server localhost:9092 \
    --group order-processor | awk '{print $5}' | tail -n +2 | paste -sd+ | bc

# 2. 模拟 Broker 宕机
echo "模拟 Broker 1 宕机..."
ssh kafka-1 "kill -9 \$(pgrep -f kafka)"

# 3. 观察集群状态
echo "等待自动恢复..."
sleep 30

# 4. 检查恢复
echo "恢复后状态:"
kafka-topics.sh --describe --bootstrap-server localhost:9092 \
    --topic orders | head -20

# 5. 重启 Broker
ssh kafka-1 "systemctl start kafka"

echo "=== 故障演练完成 ==="
```

## 📊 故障恢复手册

### 故障分级响应

```
P0（紧急，5 分钟内响应）：
  - 集群完全不可用
  - 数据丢失
  - 业务中断

P1（重要，30 分钟内响应）：
  - 部分 Broker 故障
  - Lag 严重

P2（一般，4 小时内响应）：
  - 性能下降
  - 监控告警
```

### 故障响应流程

```
1. 接收告警
   ↓
2. 确认故障（不是误报）
   ↓
3. 评估影响范围（哪些业务受影响）
   ↓
4. 启动应急方案（应急联系方式）
   ↓
5. 恢复服务（按恢复手册）
   ↓
6. 验证（业务恢复、SLA 达标）
   ↓
7. 复盘（写故障报告）
```

### 应急联系方式

```markdown
Kafka on-call：XXX
数据库 on-call：XXX
基础设施 on-call：XXX
应用 on-call：XXX
值班经理：XXX
```

## ⚠️ 常见问题

### 问题 1：自动恢复不工作

```
原因：
  1. unclean.leader.election.enable=false + ISR 都不可用
  2. Controller 选举卡住

解决：
  1. 临时开启 unclean.leader.election
  2. 手动重启 Controller
```

### 问题 2：恢复后数据不一致

```
场景：恢复后某些消息丢失或重复
解决：
  1. 业务端幂等
  2. 数据校验（对账）
  3. 重新导入（从源数据）
```

### 问题 3：恢复时间过长

```
原因：恢复流程不熟练
解决：
  1. 定期演练
  2. 自动化恢复（脚本）
  3. 文档化（runbook）
```

## 🎯 总结

**故障恢复核心要点**：
- ✅ Broker 故障自动恢复（5-15 秒）
- ✅ 副本机制保证数据可靠
- ✅ MirrorMaker 2.0 跨机房容灾
- ✅ 定期备份（数据 + 配置）
- ✅ 故障演练（定期）
- ✅ 故障响应流程文档化
- ⚠️ 自动化恢复（脚本）
- ⚠️ 灾难恢复预案

**下一步：** [📝 高频面试题（上）](/10-interview/basic) — 面试准备

## 📚 跨站参考：📊 监控告警

<!-- xlink-dedup:do-not-edit -->

本节在 3 站展开，最权威版本位于 **observability** 站（[https://java-px.bot.cd/observability/](https://java-px.bot.cd/observability/)）。

其他站参考：[kafka](https://java-px.bot.cd/kafka/) / [mysql](https://java-px.bot.cd/mysql/) / [video](https://java-px.bot.cd/video/)

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。
