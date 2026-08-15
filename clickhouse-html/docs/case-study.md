---
title: 大厂 ClickHouse 实战案例
description: 12 个真实生产级 ClickHouse 案例：Uber / Cloudflare / 字节 / B 站 / 京东等
---

# 大厂 ClickHouse 实战案例

> 从 2016 年 Yandex 开源至今，ClickHouse 已成为 OLAP 领域事实标准之一。本章精选 12 个真实生产案例，覆盖日志分析、用户埋点、指标存储、实时数仓、广告归因等核心场景，每个案例给出「为什么选 / 怎么用 / 踩了什么坑 / 学到什么」四段式总结。

## 案例索引

| # | 公司 | 场景 | 数据规模 | 关键指标 |
|---|------|------|---------|---------|
| 1 | Uber | 日志分析（替换 ES） | 50+ PB | 成本 -90%，查询 +10x |
| 2 | Cloudflare | DNS / CDN 日志 | 50+ PB 单集群 | 自研 ch-go 客户端 |
| 3 | 字节跳动 | 抖音埋点 + 广告归因 | 数 PB | 千万级 QPS |
| 4 | GitHub | Events / Audit log | 数十 PB | 替换 Elasticsearch |
| 5 | B 站 | 用户行为 + 弹幕反垃圾 | PB 级 | 替代 Druid/Kylin |
| 6 | 京东 | 订单履约 + 商品分析 | PB 级 | 替代 Presto + ES |
| 7 | 美团 | 外卖实时监控 | 数 PB | 多机房容灾 |
| 8 | 网易 | 游戏埋点 + 反作弊 | PB 级 | 高基数 UV 统计 |
| 9 | 滴滴 | 行程数据实时分析 | PB 级 | 与 StarRocks 共存 |
| 10 | 知乎 | 内容质量分析 | 百 TB | 替代 Druid |
| 11 | Yandex.Metrica | 原始应用案例 | 数十 PB | ClickHouse 起源 |
| 12 | 头条 | 新闻推荐实时数仓 | PB 级 | Kafka 引擎 |

---

## 案例 1：Uber 日志分析平台从 ES 到 ClickHouse

**背景**：Uber 每天产生 10+ TB 服务日志（订单、行程、司机行为），原 Elasticsearch 集群规模 100+ 节点，月度成本 $1M+。

**为什么选 ClickHouse**：
- ES 倒排索引适合文本搜索，但聚合/统计性能远不如列存。
- 团队对比 CK vs ES vs Druid：CK 在聚合查询快 10x，存储压缩 5-10x。

**怎么用**：
- Schema：每张表按服务名分（如 `uber_logs_ride`、`uber_logs_trip`），按 `event_date` 分区，按 `(service, level)` 排序。
- 写入：Fluent Bit → Kafka → ClickHouse Kafka 引擎 + MaterializedView。
- 查询：自研 `LogGlass` UI，封装 Grafana + CK，提供下钻、日志上下文关联。

**踩坑**：
1. 早期用 ReplacingMergeTree 去重，但司机位置上报频次高（每秒 1 次），合并压力大 → 改用 `AggregatingMergeTree` 预聚合。
2. 单表 100 亿行后 JOIN 慢 → 引入 `Dictionary` 缓存维度表。
3. Zookeeper 故障导致全集群不可用 → 迁移到 ClickHouse Keeper。

**学到**：日志分析不是单纯「文本搜索」，聚合查询占比 > 50% 时列存完胜。

## 案例 2：Cloudflare DNS 日志分析

**背景**：Cloudflare 服务全球 20% 网站，每天 1.7 万亿 DNS 查询，单集群处理 50+ PB 数据。

**为什么选 ClickHouse**：
- 自 2018 年开始用 CK 替代自研的 Graphite/WhisperDB。
- 客户账单查询（按域名聚合）、安全分析（DDoS 检测）、网络优化（延迟分位数）三大场景统一在一个 OLAP 引擎上。

**怎么用**：
- 自研 `ch-go` 客户端（Go 原生，二进制协议 LZ4 压缩），比 HTTP 客户端快 3-5x。
- 写入路径：`dnsproxy` → 自研 logpush → Kafka → CK Kafka 引擎 + MV。
- 存储：每个机房 1 个集群（10-30 节点），3 副本；全球跨机房数据通过 `Distributed` 表联邦查询。

**踩坑**：
1. 早期用 Zookeeper，跨大洲延迟 200ms+ → 全部迁移到 ClickHouse Keeper（基于 Raft）。
2. 单分区过大（> 1TB/分区）导致合并慢 → 强制按天分区 + 按小时子分区（生产环境实验性）。

**学到**：写入客户端二进制协议（ch-go）比 HTTP 协议节省 30-50% 网络带宽，单节点写入吞吐从 5w rows/s 提升到 15w rows/s。

## 案例 3：字节跳动抖音埋点 + 广告归因

**背景**：抖音日活 7 亿+，每天产生 PB 级埋点（曝光、点击、滑动、点赞、关注）；广告系统 CTR/CVR 实时归因要求秒级延迟。

**为什么选 ClickHouse**：
- 埋点宽表（200+ 列），CK 列存压缩 10-20x。
- 实时数仓场景：Kafka → CK Kafka 引擎 → MV → 业务查询，全程秒级。

**怎么用**：
- 埋点入口：`event_tracker` SDK → Kafka（按业务线分 topic）→ CK Kafka 引擎 + `ReplacingMergeTree` 去重。
- 广告归因：`click_log` + `conversion_log` 双流 JOIN，通过 MV 预计算 `attribution_result` 表。
- 查询入口：自研 `ByteQuery`（Presto 协议兼容），CK 作为执行引擎之一。

**踩坑**：
1. 埋点宽表列数过多（> 200），单 INSERT 卡顿 → 拆成 `main_event` + `event_extra` 两张表，查询时用 `JOIN` 或 `dictGet`。
2. 高基数 UV（用户维度 10 亿+） → 用 `RoaringBitmap` + `groupBitmapState` 预聚合，UV 查询从 30s 降到 100ms。
4. 广告归因数据倾斜（爆款视频曝光 1 亿+） → 用 `SAMPLE` 抽样 + `prewhere` 优化。

**学到**：高基数 UV 场景，`RoaringBitmap` 是 ClickHouse 的杀手锏，比 HyperLogLog 精确且性能相当。

## 案例 4：GitHub Events / Audit Log 迁移

**背景**：GitHub 每年产生 13+ 亿 events（push / PR / issue / release），原 Elasticsearch 集群规模 30+ 节点，聚合查询慢（90s+）。

**为什么选 ClickHouse**：
- 2019 年开始迁移，2020 年完成，节省 50%+ 存储成本。
- 聚合查询（按 repo / user / time 多维分析）从 90s 降到 < 1s。

**怎么用**：
- Schema：`events` 表按月分区，按 `(repo_id, user_id, event_type)` 排序。
- 写入：GitHub Rails monolith → Kafka → CK Kafka 引擎。
- 查询：自研 UI `GitHub Insights`，CK SQL 直查。

**踩坑**：
1. Audit log 含敏感数据（IP、邮箱），CK 列级加密 + 访问审计。
2. 历史数据从 ES 迁移：用 `clickhouse-migrator` 工具，5 亿行/小时迁移速度。

**学到**：迁移 OLAP 引擎需要关注数据完整性（checksum）和查询一致性（同一查询在新旧系统对比结果）。

## 案例 5：B 站用户行为 + 弹幕反垃圾

**背景**：B 站日活 1 亿+，每天产生 PB 级用户行为（播放、点赞、投币、收藏）和弹幕数据。

**为什么选 ClickHouse**：
- 替代原 Druid + Kylin 双引擎架构，Druid 运维复杂，Kylin Cube 维护成本高。
- CK 实时数仓方案：`Kafka → CK Kafka 引擎 → MV → 业务查询`。

**怎么用**：
- 弹幕反垃圾：实时计算弹幕发送频率（按用户 + 视频），CK 用 `AggregatingMergeTree` + `State` 函数预聚合 5 分钟窗口。
- 用户留存分析：`Retention` 函数直接计算 cohort，比 Druid 简单一个数量级。

**踩坑**：
1. 弹幕高基数（视频 ID 数十亿），`groupBitmapState` 内存爆 → 改用 `uniqExact64` + `SAMPLE 0.1`。
2. Druid 迁移期双跑 3 个月，逐步切流量。

**学到**：`AggregatingMergeTree` + State 函数是 CK 的实时指标利器，比 Spark Streaming + Redis 简单太多。

## 案例 6：京东订单履约 + 商品分析

**背景**：京东每天千万级订单，PB 级订单履约数据（仓储、配送、签收、退款）。

**为什么选 ClickHouse**：
- 替代 Presto + Elasticsearch 组合，单集群统一查询入口。
- 实时看板要求秒级延迟，CK Kafka 引擎 + MV 完美匹配。

**怎么用**：
- 订单大宽表：200+ 列（订单 ID / 用户 / 商品 / 仓 / 配送 / 支付 / 售后），按 `order_date` 分区，按 `order_id` 排序。
- 实时履约看板：Kafka → CK Kafka 引擎 → MV → 自研 BI。

**踩坑**：
1. Presto 迁移：PrestoSQL 兼容 CK 大部分语法，但 `SELECT *` 性能差 → 强制要求业务方指定列。
2. 商品分析涉及多表 JOIN（订单 + 商品 + 库存 + 用户），改用星型模型 + 预 JOIN 物化视图。

**学到**：实时大宽表场景，`AggregatingMergeTree` 预聚合 + 物化视图链路，比 Spark/Flink 链路简单 10 倍。

## 案例 7：美团外卖实时监控

**背景**：美团外卖日订单 6000 万+，实时监控订单状态、配送时效、商家出餐速度。

**为什么选 ClickHouse**：
- 替代原 Druid + Flink 链路，单系统简化运维。
- 多机房容灾：CK 跨机房 `Distributed` 表 + 自研副本管理。

**怎么用**：
- 订单状态机：CK 用 `VersionedCollapsingMergeTree` 维护订单状态变更。
- 配送时效：Kafka → CK Kafka 引擎 → MV 预聚合 `delivery_duration_p99`。
- 多机房容灾：3 机房 9 副本，CK Keeper 集群 5 节点。

**踩坑**：
1. 早期 `CollapsingMergeTree` 误用 sign 标记 → 数据错乱，改用 `VersionedCollapsingMergeTree` + version 列。
2. 跨机房 `Distributed` 表延迟 200ms → 高优查询走单机房 leader 节点。

**学到**：`VersionedCollapsingMergeTree` 比 `CollapsingMergeTree` 更鲁棒，避免 sign 错乱导致数据丢失。

## 案例 8：网易游戏埋点 + 反作弊

**背景**：网易旗下多款手游（《阴阳师》《荒野行动》），每天 TB 级埋点（登录、对战、付费、聊天）。

**为什么选 ClickHouse**：
- 替代原 Hadoop + Hive 离线链路，T+1 报表延迟降到秒级。
- 反作弊实时计算（5 分钟窗口）要求高基数 UV 统计。

**怎么用**：
- 埋点入口：游戏客户端 SDK → Kafka → CK Kafka 引擎 + MV。
- 反作弊：`AggregatingMergeTree` 维护 5 分钟滑动窗口，UV 用 `RoaringBitmap`。

**踩坑**：
1. 聊天文本含敏感词，需要 CK 列级加密 + 审计日志。
2. 高基数反作弊特征（玩家 ID × 时间） → 用 `SAMPLE` 抽样 + `prewhere`。

**学到**：游戏行业反作弊对实时性要求极高，CK + RoaringBitmap 比 Spark + HBase 性能 + 简单度都更优。

## 案例 9：滴滴行程数据实时分析

**背景**：滴滴日订单数千万，行程数据（轨迹、时长、费用、评价）实时入仓。

**为什么选 ClickHouse + StarRocks 双引擎**：
- 单表聚合（订单统计）用 ClickHouse，多表 JOIN（订单 + 用户 + 司机 + 城市）用 StarRocks。
- 两套系统各自擅长，团队分工维护。

**怎么用**：
- ClickHouse：单表聚合（订单趋势、GMV、用户活跃），Kafka 引擎写入。
- StarRocks：多表 JOIN（订单履约 + 司机调度 + 城市运营），StarRocks CBO 更强。

**踩坑**：
1. 双系统运维成本高 → 抽象统一查询入口（PrestoSQL），业务方无感知。
2. 数据一致性：CK 与 SR 都需要从 Kafka 独立消费，做最终一致对齐。

**学到**：双 OLAP 引擎不是坏事，关键是查询入口统一（Presto/Trino），业务方只关心 SQL。

## 案例 10：知乎内容质量分析

**背景**：知乎每天百万级回答、评论、点赞，内容质量分析（低质、灌水、广告）需要实时判定。

**为什么选 ClickHouse**：
- 替代原 Druid（运维复杂），CK + MV 实时聚合更简单。
- 数据量百 TB 级，单集群 10 节点足够。

**怎么用**：
- 内容事件：`answer_created` / `comment_created` / `vote_created` → Kafka → CK Kafka 引擎 + `ReplacingMergeTree`。
- 低质内容识别：MV 预聚合 `low_quality_score`，5 分钟更新一次。

**踩坑**：
1. 早期单副本 → 改为 3 副本，跨机架分布。
2. 删除违规内容需要 `ALTER TABLE ... DELETE` 异步操作 → 业务方接受分钟级延迟。

**学到**：CK 的 `ALTER TABLE ... DELETE` 是异步操作，不能当作 OLTP 删除使用。

## 案例 11：Yandex.Metrica（ClickHouse 起源）

**背景**：Yandex.Metrika 是俄罗斯最大的网站分析平台（类似 Google Analytics），2009 年自研 ClickHouse，2016 年开源。

**为什么自研**：
- 2009 年市面没有满足 PB 级实时聚合的 OLAP 引擎（Greenplum 太重、Druid 还未出现）。
- 团队需求：单查询秒级响应、列存压缩、向量执行、向量化 SIMD。

**怎么用**：
- 每天 200+ 亿事件，单集群 1000+ 节点，PB 级数据。
- 自研 `mergetree` 引擎家族（LSM + 列存 + 后台合并）。

**学到**：ClickHouse 的设计哲学「实时的、列存的、聚合优先」至今仍是 OLAP 引擎的事实标准。

## 案例 12：头条新闻推荐实时数仓

**背景**：今日头条每天 PB 级推荐日志（曝光、点击、停留、转化），推荐系统需要实时特征工程。

**为什么选 ClickHouse**：
- 推荐特征 100+ 维度，CK 列存压缩 + 向量化聚合完美匹配。
- 实时特征：从 Kafka 到 CK 延迟 < 5s，模型训练链路秒级。

**怎么用**：
- 入口：客户端埋点 → Kafka → CK Kafka 引擎 + `ReplacingMergeTree` 去重。
- 特征计算：MV 预聚合用户 × 文章 × 时间多维特征，导出到 Redis 在线特征库。

**踩坑**：
1. 推荐冷启动（新增用户/文章）需要实时计算 → 用 `Dictionary` 缓存用户画像。
2. 推荐效果 A/B 实验：高基数实验 ID → 改用 `SAMPLE` 抽样。

**学到**：CK 在实时数仓场景是「Kafka + MV + 特征工程」链路的事实标准，比 Spark/Flink 简单 10 倍。

---

## 总结：12 个案例的共性经验

1. **场景匹配**：埋点/日志/指标/数仓是 CK 主战场，OLTP/强事务不是。
2. **架构套路**：Kafka → CK Kafka 引擎 → MV → 业务查询，链路标准化。
3. **引擎选型**：`ReplacingMergeTree` 去重、`AggregatingMergeTree` 预聚合、`VersionedCollapsingMergeTree` 状态变更，三件套搞定 80% 场景。
4. **客户端**：Go 项目用 `ch-go`（二进制协议），Python 用 `clickhouse-connect`，Java 用 `clickhouse-jdbc`。
5. **运维**：跨机房用 `Distributed` 表 + 副本；Zookeeper 迁移到 ClickHouse Keeper。
6. **生态**：Grafana 数据源、Prometheus remote_write、dbt-clickhouse、Airbyte Source/Destination 全链路打通。

> 一句话：**ClickHouse 已经从单一 OLAP 引擎演进为「实时数仓操作系统」**，是日志/埋点/指标场景的事实标准。