# 内容质量审计报告 — 2026-08-26

> 自动生成 by `scripts/audit-content.py`（C3 baseline）
> 检测范围: 31 子站 × 1567 .md 文件

## 〇、Summary

| 指标 | 数值 | 健康阈值 | 状态 |
|------|------|----------|------|
| 总文件数 | 1567 | — | — |
| 总字数（中英混合） | 1,313,356 | — | — |
| frontmatter 覆盖率 | 100.0% | ≥ 95% | ✅ |
| 薄页豁免（cheatsheet.md, graph.md, mindmap.md + 站点:java-language） | 103 | — | 结构预期字数少，不计入薄页 |
| 薄页（< 200 字，扣除豁免） | 0 (0.0%) | ≤ 5% | ✅ |
| 缺 frontmatter | 0 | 0 | ✅ |
| frontmatter 缺 date | 1554 | 0 | ⚠️（VitePress `lastUpdated: true` 兜底）|
| 过期内容（> 365 天） | 0 | ≤ 10% | ✅ |
| 图片总数 | 0 | — | ⚠️ 偏少 |
| 缺 alt 的图片 | 0 | 0 | ✅ |
| 内部死链 | 0 | 0 | ✅ |
| 跨站引用 | 399 | ≥ 100 | ✅ |
| Vue prop 数组缺逗号 | 0 | 0 | ✅ |
| Vue 组件缺失（md 引用无 .vue） | 0 | 0 | ✅ |
| Mermaid 代码块未闭合 | 0 | 0 | ✅ |
| 标题层级跳级 | 0 | 0 | ✅ |
| 跨子站重复标题 | 143 | ≤ 20 | ⚠️ |

## 一、各子站统计

| 子站 | 文件 | 字数 | FM | 薄页 | 豁免 | 缺FM | 过期 | 图片 | 死链 | 跨站 | 密度 | VueBug | 缺组件 | Mermaid | 标题跳级 |
|------|-----:|-----:|---:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|-----:|---------:|
| ai | 57 | 33,615 | 57 | 0 | 3 | 0 | 0 | 0 | 0 | 9 | 0.27 | 0 | 0 | 0 | 0 |
| android | 29 | 11,139 | 29 | 0 | 2 | 0 | 0 | 0 | 0 | 13 | 1.17 | 0 | 0 | 0 | 0 |
| architecture | 51 | 34,676 | 51 | 0 | 3 | 0 | 0 | 0 | 0 | 12 | 0.35 | 0 | 0 | 0 | 0 |
| bigdata | 51 | 36,513 | 51 | 0 | 3 | 0 | 0 | 0 | 0 | 10 | 0.27 | 0 | 0 | 0 | 0 |
| chaos | 32 | 30,922 | 32 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0.29 | 0 | 0 | 0 | 0 |
| clickhouse | 36 | 34,631 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0.29 | 0 | 0 | 0 | 0 |
| cloud | 35 | 41,502 | 35 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0.12 | 0 | 0 | 0 | 0 |
| cloud-native | 55 | 37,782 | 55 | 0 | 3 | 0 | 0 | 0 | 0 | 10 | 0.26 | 0 | 0 | 0 | 0 |
| design-pattern | 49 | 59,036 | 49 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0.15 | 0 | 0 | 0 | 0 |
| devops | 30 | 21,874 | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0.46 | 0 | 0 | 0 | 0 |
| es | 63 | 19,692 | 63 | 0 | 0 | 0 | 0 | 0 | 0 | 11 | 0.56 | 0 | 0 | 0 | 0 |
| filesystem | 94 | 79,081 | 81 | 0 | 3 | 0 | 0 | 0 | 0 | 13 | 0.16 | 0 | 0 | 0 | 0 |
| frontend | 65 | 30,190 | 65 | 0 | 2 | 0 | 0 | 0 | 0 | 10 | 0.33 | 0 | 0 | 0 | 0 |
| game | 39 | 16,398 | 39 | 0 | 2 | 0 | 0 | 0 | 0 | 11 | 0.67 | 0 | 0 | 0 | 0 |
| go | 36 | 44,913 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0.22 | 0 | 0 | 0 | 0 |
| iot | 35 | 13,596 | 35 | 0 | 2 | 0 | 0 | 0 | 0 | 12 | 0.88 | 0 | 0 | 0 | 0 |
| java | 53 | 19,597 | 53 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 0.66 | 0 | 0 | 0 | 0 |
| java-language | 55 | 5,715 | 55 | 0 | 55 | 0 | 0 | 0 | 0 | 8 | 1.40 | 0 | 0 | 0 | 0 |
| kafka | 73 | 103,186 | 73 | 0 | 3 | 0 | 0 | 0 | 0 | 59 | 0.57 | 0 | 0 | 0 | 0 |
| linux | 71 | 49,687 | 71 | 0 | 3 | 0 | 0 | 0 | 0 | 11 | 0.22 | 0 | 0 | 0 | 0 |
| mysql | 67 | 89,929 | 67 | 0 | 4 | 0 | 0 | 0 | 0 | 28 | 0.31 | 0 | 0 | 0 | 0 |
| network | 66 | 49,984 | 66 | 0 | 3 | 0 | 0 | 0 | 0 | 9 | 0.18 | 0 | 0 | 0 | 0 |
| observability | 50 | 44,270 | 50 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0.23 | 0 | 0 | 0 | 0 |
| postgresql | 53 | 55,240 | 53 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0.18 | 0 | 0 | 0 | 0 |
| python | 60 | 73,098 | 60 | 0 | 3 | 0 | 0 | 0 | 0 | 10 | 0.14 | 0 | 0 | 0 | 0 |
| redis | 59 | 75,988 | 59 | 0 | 3 | 0 | 0 | 0 | 0 | 11 | 0.14 | 0 | 0 | 0 | 0 |
| rust | 35 | 26,756 | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0.34 | 0 | 0 | 0 | 0 |
| security | 36 | 26,231 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 0.50 | 0 | 0 | 0 | 0 |
| system-design | 52 | 80,212 | 52 | 0 | 0 | 0 | 0 | 0 | 0 | 11 | 0.14 | 0 | 0 | 0 | 0 |
| tools | 13 | 9,762 | 13 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0.82 | 0 | 0 | 0 | 0 |
| video | 67 | 58,141 | 67 | 0 | 3 | 0 | 0 | 0 | 0 | 25 | 0.43 | 0 | 0 | 0 | 0 |

### 〇·a、跨站引用低密度站（29 站，每千字 < 1 链接）

| 子站 | 密度（每千字）| xsite 链接 | 字数 |
|------|-----:|-----:|-----:|
| cloud | 0.12 | 5 | 41,502 |
| python | 0.14 | 10 | 73,098 |
| system-design | 0.14 | 11 | 80,212 |
| redis | 0.14 | 11 | 75,988 |
| design-pattern | 0.15 | 9 | 59,036 |
| filesystem | 0.16 | 13 | 79,081 |
| network | 0.18 | 9 | 49,984 |
| postgresql | 0.18 | 10 | 55,240 |
| linux | 0.22 | 11 | 49,687 |
| go | 0.22 | 10 | 44,913 |
| observability | 0.23 | 10 | 44,270 |
| cloud-native | 0.26 | 10 | 37,782 |
| ai | 0.27 | 9 | 33,615 |
| bigdata | 0.27 | 10 | 36,513 |
| clickhouse | 0.29 | 10 | 34,631 |
| chaos | 0.29 | 9 | 30,922 |
| mysql | 0.31 | 28 | 89,929 |
| frontend | 0.33 | 10 | 30,190 |
| rust | 0.34 | 9 | 26,756 |
| architecture | 0.35 | 12 | 34,676 |
| video | 0.43 | 25 | 58,141 |
| devops | 0.46 | 10 | 21,874 |
| security | 0.50 | 13 | 26,231 |
| es | 0.56 | 11 | 19,692 |
| kafka | 0.57 | 59 | 103,186 |
| java | 0.66 | 13 | 19,597 |
| game | 0.67 | 11 | 16,398 |
| tools | 0.82 | 8 | 9,762 |
| iot | 0.88 | 12 | 13,596 |

**建议**：这些站当前主要靠 index.md 末尾的 📚 相关阅读 段落带跨站链接，子文档间应互相引用。可参考 §8.60 xlink-injector 注入术语映射。

### 〇·b、内容完整度低（59 篇，completeness_score ≤ 3）

| 子站 | 平均分 | 低完整度 / 总数 | 建议 |
|------|------:|------:|------|
| tools-html | 3.2 | 11 / 13 | 加代码示例 / 表格 / Vue 组件 |
| android-html | 3.5 | 7 / 29 | 加代码示例 / 表格 / Vue 组件 |
| iot-html | 3.6 | 6 / 35 | 加代码示例 / 表格 / Vue 组件 |
| game-html | 3.6 | 8 / 39 | 加代码示例 / 表格 / Vue 组件 |
| chaos-html | 3.7 | 9 / 32 | 加代码示例 / 表格 / Vue 组件 |
| filesystem-html | 3.7 | 14 / 94 | 加代码示例 / 表格 / Vue 组件 |
| network-html | 4.0 | 2 / 66 | 加代码示例 / 表格 / Vue 组件 |
| java-html | 4.1 | 1 / 53 | 加代码示例 / 表格 / Vue 组件 |
| clickhouse-html | 4.8 | 1 / 36 | 加代码示例 / 表格 / Vue 组件 |

## 七、跨子站重复标题（143 组 — 候选合并/跨站引用）

模板 词已在检测中过滤（在图谱中的位置 / 一句话定义 / 关键 takeaway 等）

- **'相关阅读（跨站导航）'** (30 处)
  - `ai/index.md`
  - `architecture/index.md`
  - `bigdata/index.md`
  - `chaos/index.md`
  - `clickhouse/index.md`
  - ... 等 25 处
- **'Saga 分布式事务'** (2 处)
  - `architecture/saga.md`
  - `design-pattern/saga.md`
- **'Sidecar 模式'** (3 处)
  - `architecture/sidecar.md`
  - `cloud-native/sidecar.md`
  - `cloud-native/sidecar.md`
- **'多级缓存架构'** (2 处)
  - `architecture/architecture.md`
  - `system-design/multi-level.md`
- **'缓存一致性'** (3 处)
  - `architecture/consistency.md`
  - `redis/cache-consistency.md`
  - `system-design/consistency.md`
- **'BASE 理论'** (2 处)
  - `architecture/base.md`
  - `cloud/cap-base.md`
- **'Raft 共识算法'** (2 处)
  - `architecture/raft.md`
  - `system-design/raft.md`
- **'CAP 定理'** (3 处)
  - `architecture/cap.md`
  - `cloud/cap-base.md`
  - `system-design/cap.md`
- **'可观测性三大支柱'** (2 处)
  - `architecture/three-pillars.md`
  - `python/logging.md`
- **'Kafka Streams'** (2 处)
  - `bigdata/streams.md`
  - `kafka/streams.md`
- **'TODO: 在此补充本页主题的实战命令'** (64 处)
  - `bigdata/lineage.md`
  - `chaos/overview.md`
  - `chaos/decision-tree.md`
  - `chaos/mesh-vs-litmus.md`
  - `chaos/open-vs-commercial.md`
  - ... 等 59 处
- **'TODO: 配置示例'** (64 处)
  - `bigdata/lineage.md`
  - `chaos/overview.md`
  - `chaos/decision-tree.md`
  - `chaos/mesh-vs-litmus.md`
  - `chaos/open-vs-commercial.md`
  - ... 等 59 处
- **'三大核心组件'** (2 处)
  - `chaos/architecture.md`
  - `cloud-native/control-plane.md`
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
- **'监控与告警'** (3 处)
  - `clickhouse/realtime-warehouse.md`
  - `clickhouse/dbt-airbyte.md`
  - `kafka/recovery.md`
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
- **'指定数据库'** (2 处)
  - `clickhouse/client.md`
  - `mysql/mysql-client.md`
- **'分片键选择'** (2 处)
  - `clickhouse/distributed.md`
  - `mysql/sharding-strategy.md`
- **'微服务架构'** (2 处)
  - `cloud/intro.md`
  - `java/microservices.md`
- **'选举超时（毫秒）'** (2 处)
  - `cloud/nacos-principle.md`
  - `kafka/controller.md`
- ... 及其他 113 组

## 八、关键发现与建议

1. **图片覆盖率极低**：0 张图 / 1567 篇 = 0.0%，纯文字技术文档严重缺乏视觉化（C11 价值高）
2. **跨站引用密度**：全局 399 处（§8.60 注入 +152），平均 0.30 链接/千字。详见'〇·a 低密度站清单'补强
3. **薄页比例 0.0%**：0 篇字数 < 200，可能为 placeholder 或拆分过度（C3 持续 review）
4. **frontmatter 覆盖率 100.0%**：0 篇缺 FM，1554 篇 FM 缺 date——但 VitePress 已配 `lastUpdated: true`，自动用 git commit 时间，**非真问题**（C1 模板可选择性根治）
5. **过期内容 0 篇**（> 365 天）：需要月度 review 流程（C10）
6. **内部死链 0 处**：可能是 VitePress cleanUrls 导致文件名不一致，建议用 check-links.py depth=3 交叉验证
