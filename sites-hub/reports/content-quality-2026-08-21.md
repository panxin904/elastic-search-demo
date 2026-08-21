# 内容质量审计报告 — 2026-08-21

> 自动生成 by `scripts/audit-content.py`（C3 baseline）
> 检测范围: 29 子站 × 1436 .md 文件

## 〇、Summary

| 指标 | 数值 | 健康阈值 | 状态 |
|------|------|----------|------|
| 总文件数 | 1436 | — | — |
| 总字数（中英混合） | 1,165,053 | — | — |
| frontmatter 覆盖率 | 100.0% | ≥ 95% | ✅ |
| 薄页豁免（cheatsheet.md, graph.md, mindmap.md） | 44 | — | 结构预期字数少，不计入薄页 |
| 薄页（< 200 字，扣除豁免） | 71 (4.9%) | ≤ 5% | ✅ |
| 缺 frontmatter | 0 | 0 | ✅ |
| frontmatter 缺 date | 1423 | 0 | ⚠️（VitePress `lastUpdated: true` 兜底）|
| 过期内容（> 365 天） | 0 | ≤ 10% | ✅ |
| 图片总数 | 0 | — | ⚠️ 偏少 |
| 缺 alt 的图片 | 0 | 0 | ✅ |
| 内部死链 | 0 | 0 | ✅ |
| 跨站引用 | 145 | ≥ 100 | ✅ |
| Vue prop 数组缺逗号 | 0 | 0 | ✅ |
| Vue 组件缺失（md 引用无 .vue） | 0 | 0 | ✅ |
| Mermaid 代码块未闭合 | 0 | 0 | ✅ |
| 标题层级跳级 | 0 | 0 | ✅ |
| 跨子站重复标题 | 188 | ≤ 20 | ⚠️ |

## 一、各子站统计

| 子站 | 文件 | 字数 | FM | 薄页 | 豁免 | 缺FM | 过期 | 图片 | 死链 | 跨站 | VueBug | 缺组件 | Mermaid | 标题跳级 |
|------|-----:|-----:|---:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|-----:|---------:|
| ai | 57 | 33,218 | 57 | 0 | 3 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| architecture | 51 | 34,085 | 51 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| bigdata | 51 | 36,007 | 51 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| chaos | 32 | 27,617 | 32 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| clickhouse | 36 | 33,122 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| cloud | 1 | 609 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cloud-native | 55 | 37,166 | 55 | 0 | 3 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| design-pattern | 49 | 55,679 | 49 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| devops | 30 | 17,872 | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| es | 63 | 19,354 | 63 | 3 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| filesystem | 94 | 72,251 | 81 | 7 | 3 | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 |
| frontend | 65 | 29,378 | 65 | 1 | 2 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| go | 36 | 41,658 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| iot | 6 | 4,083 | 6 | 0 | 2 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 |
| java | 53 | 16,998 | 53 | 11 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| java-language | 55 | 5,541 | 55 | 49 | 3 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| kafka | 73 | 98,005 | 73 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| linux | 71 | 48,647 | 71 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| mysql | 67 | 87,035 | 67 | 0 | 4 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| network | 66 | 48,127 | 66 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| observability | 50 | 42,317 | 50 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| postgresql | 53 | 48,967 | 53 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| python | 60 | 69,021 | 60 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| redis | 59 | 75,279 | 59 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| rust | 35 | 21,774 | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| security | 36 | 21,683 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 |
| system-design | 52 | 73,595 | 52 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| tools | 13 | 8,284 | 13 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |
| video | 67 | 57,681 | 67 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 |

## 二、薄页清单（71 篇）

- `java-language/04-jvm/bytecode.md (32字)`
- `java-language/10-performance/jvm-tuning.md (41字)`
- `java-language/03-concurrency/future.md (46字)`
- `java-language/12-tools/lombok.md (47字)`
- `java-language/07-spring-cloud/seata.md (47字)`
- `java-language/13-testing/junit5.md (48字)`
- `java-language/03-concurrency/locks.md (49字)`
- `java-language/07-spring-cloud/gateway.md (50字)`
- `java-language/05-gc/tuning.md (51字)`
- `java-language/07-spring-cloud/nacos.md (52字)`
- `java-language/09-io/serialize.md (53字)`
- `java-language/12-tools/commands.md (54字)`
- `java-language/06-spring/transaction.md (55字)`
- `java-language/06-spring/boot.md (55字)`
- `java-language/02-collections/set.md (56字)`
- `java-language/02-collections/stream.md (56字)`
- `java-language/06-spring/mvc.md (56字)`
- `java-language/02-collections/concurrent.md (57字)`
- `java-language/01-basics/exceptions.md (59字)`
- `java-language/04-jvm/oom.md (59字)`
- `java-language/03-concurrency/juc.md (59字)`
- `java-language/13-testing/mockito.md (59字)`
- `java-language/03-concurrency/thread-pool.md (60字)`
- `java-language/03-concurrency/virtual-threads.md (62字)`
- `java-language/12-tools/build.md (63字)`
- `java-language/05-gc/collectors.md (64字)`
- `java-language/02-collections/list.md (66字)`
- `java-language/04-jvm/classloading.md (67字)`
- `java-language/13-testing/spring-test.md (67字)`
- `java-language/01-basics/generics.md (68字)`
- `java-language/08-database/mybatis.md (68字)`
- `java-language/02-collections/map.md (69字)`
- `java-language/10-performance/jvm-tools.md (69字)`
- `java-language/05-gc/algorithms.md (69字)`
- `java-language/09-io/netty.md (70字)`
- `java-language/08-database/jdbc.md (71字)`
- `java-language/04-jvm/runtime.md (72字)`
- `java-language/09-io/nio.md (73字)`
- `java-language/10-performance/arthas.md (77字)`
- `java-language/11-design/creational.md (81字)`
- `java-language/11-design/structural.md (82字)`
- `java-language/11-design/behavioral.md (86字)`
- `java-language/14-interview/path.md (89字)`
- `java-language/01-basics/new-features.md (90字)`
- `java-language/08-database/jpa.md (90字)`
- `java-language/06-spring/ioc-aop.md (91字)`
- `java/02-design/factory-pattern.md (107字)`
- `java-language/14-interview/coding.md (138字)`
- `java/02-design/proxy-pattern.md (142字)`
- `filesystem/10-security/README.md (151字)`
- ... 及其他 21 篇

## 七、跨子站重复标题（188 组 — 候选合并/跨站引用）

模板 词已在检测中过滤（在图谱中的位置 / 一句话定义 / 关键 takeaway 等）

- **'Saga 分布式事务'** (2 处)
  - `architecture/saga.md`
  - `design-pattern/saga.md`
- **'Sidecar 模式'** (3 处)
  - `architecture/sidecar.md`
  - `cloud-native/sidecar.md`
  - `cloud-native/sidecar.md`
- **'Saga 模式'** (2 处)
  - `architecture/saga.md`
  - `system-design/saga.md`
- **'消息可靠性'** (2 处)
  - `architecture/compare.md`
  - `java/message-queue.md`
- **'多级缓存架构'** (4 处)
  - `architecture/architecture.md`
  - `architecture/architecture.md`
  - `system-design/multi-level.md`
  - `system-design/multi-level.md`
- **'缓存一致性'** (3 处)
  - `architecture/consistency.md`
  - `redis/cache-consistency.md`
  - `system-design/consistency.md`
- **'Raft 共识算法'** (2 处)
  - `architecture/raft.md`
  - `system-design/raft.md`
- **'Paxos vs Raft'** (2 处)
  - `architecture/raft.md`
  - `system-design/paxos.md`
- **'角色与状态'** (2 处)
  - `architecture/raft.md`
  - `system-design/raft.md`
- **'CAP 定理'** (2 处)
  - `architecture/cap.md`
  - `system-design/cap.md`
- **'可观测性三大支柱'** (2 处)
  - `architecture/three-pillars.md`
  - `python/logging.md`
- **'Kafka Streams'** (2 处)
  - `bigdata/streams.md`
  - `kafka/streams.md`
- **'dbt_project.yml'** (2 处)
  - `bigdata/airflow-dbt.md`
  - `clickhouse/overview.md`
- **'数据写入流程'** (2 处)
  - `bigdata/architecture.md`
  - `kafka/overview.md`
- **'故障切换流程'** (2 处)
  - `bigdata/ha.md`
  - `postgresql/patroni.md`
- **'三大核心组件'** (2 处)
  - `chaos/architecture.md`
  - `cloud-native/control-plane.md`
- **'5xx 错误率'** (2 处)
  - `chaos/overview.md`
  - `observability/logql.md`
- **'聚合窗口函数'** (2 处)
  - `clickhouse/window-functions.md`
  - `postgresql/window.md`
- **'CTE（公共表表达式）'** (2 处)
  - `clickhouse/window-functions.md`
  - `mysql/functions.md`
- **'JOIN 类型'** (2 处)
  - `clickhouse/join.md`
  - `postgresql/planner.md`
- **'JOIN 性能优化'** (2 处)
  - `clickhouse/join.md`
  - `mysql/join.md`
- **'Grafana 数据源'** (2 处)
  - `clickhouse/log-analysis.md`
  - `observability/tempo.md`
- **'Grafana 集成'** (5 处)
  - `clickhouse/log-analysis.md`
  - `clickhouse/grafana.md`
  - `cloud-native/loki.md`
  - `observability/pyroscope.md`
  - `observability/tempo.md`
- **'监控与告警'** (5 处)
  - `clickhouse/realtime-warehouse.md`
  - `clickhouse/dbt-airbyte.md`
  - `kafka/recovery.md`
  - `system-design/not-lost.md`
  - `system-design/backlog.md`
- **'Prometheus 配置'** (3 处)
  - `clickhouse/metrics-storage.md`
  - `kafka/backlog.md`
  - `mysql/prometheus.md`
- **'字符串类型'** (3 处)
  - `clickhouse/data-types.md`
  - `mysql/data-types.md`
  - `postgresql/built-in.md`
- **'验证集群状态'** (2 处)
  - `clickhouse/installation.md`
  - `kafka/install.md`
- **'备份到 S3'** (2 处)
  - `clickhouse/installation.md`
  - `mysql/mysqldump.md`
- **'Kubernetes 部署'** (5 处)
  - `clickhouse/installation.md`
  - `design-pattern/sidecar.md`
  - `observability/collector.md`
  - `observability/jaeger.md`
  - `python/docker.md`
- **'客户端连接'** (2 处)
  - `clickhouse/client.md`
  - `redis/install.md`
- ... 及其他 158 组

## 八、关键发现与建议

1. **图片覆盖率极低**：0 张图 / 1436 篇 = 0.0%，纯文字技术文档严重缺乏视觉化（C11 价值高）
2. **跨站引用近零**：仅 145 处，28 站 1429+ 页形成内容孤岛（C2 价值高）
3. **薄页比例 4.9%**：71 篇字数 < 200，可能为 placeholder 或拆分过度（C3 持续 review）
4. **frontmatter 覆盖率 100.0%**：0 篇缺 FM，1423 篇 FM 缺 date——但 VitePress 已配 `lastUpdated: true`，自动用 git commit 时间，**非真问题**（C1 模板可选择性根治）
5. **过期内容 0 篇**（> 365 天）：需要月度 review 流程（C10）
6. **内部死链 0 处**：可能是 VitePress cleanUrls 导致文件名不一致，建议用 check-links.py depth=3 交叉验证
