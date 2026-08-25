# 内容质量审计报告 — 2026-08-25

> 自动生成 by `scripts/audit-content.py`（C3 baseline）
> 检测范围: 31 子站 × 1567 .md 文件

## 〇、Summary

| 指标 | 数值 | 健康阈值 | 状态 |
|------|------|----------|------|
| 总文件数 | 1567 | — | — |
| 总字数（中英混合） | 1,237,176 | — | — |
| frontmatter 覆盖率 | 100.0% | ≥ 95% | ✅ |
| 薄页豁免（cheatsheet.md, graph.md, mindmap.md + 站点:java-language） | 103 | — | 结构预期字数少，不计入薄页 |
| 薄页（< 200 字，扣除豁免） | 0 (0.0%) | ≤ 5% | ✅ |
| 缺 frontmatter | 0 | 0 | ✅ |
| frontmatter 缺 date | 1554 | 0 | ⚠️（VitePress `lastUpdated: true` 兜底）|
| 过期内容（> 365 天） | 0 | ≤ 10% | ✅ |
| 图片总数 | 0 | — | ⚠️ 偏少 |
| 缺 alt 的图片 | 0 | 0 | ✅ |
| 内部死链 | 0 | 0 | ✅ |
| 跨站引用 | 319 | ≥ 100 | ✅ |
| Vue prop 数组缺逗号 | 0 | 0 | ✅ |
| Vue 组件缺失（md 引用无 .vue） | 0 | 0 | ✅ |
| Mermaid 代码块未闭合 | 0 | 0 | ✅ |
| 标题层级跳级 | 0 | 0 | ✅ |
| 跨子站重复标题 | 186 | ≤ 20 | ⚠️ |

## 一、各子站统计

| 子站 | 文件 | 字数 | FM | 薄页 | 豁免 | 缺FM | 过期 | 图片 | 死链 | 跨站 | 密度 | VueBug | 缺组件 | Mermaid | 标题跳级 |
|------|-----:|-----:|---:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|-----:|---------:|
| ai | 57 | 33,297 | 57 | 0 | 3 | 0 | 0 | 0 | 0 | 9 | 0.27 | 0 | 0 | 0 | 0 |
| android | 29 | 8,444 | 29 | 0 | 2 | 0 | 0 | 0 | 0 | 13 | 1.54 | 0 | 0 | 0 | 0 |
| architecture | 51 | 34,189 | 51 | 0 | 3 | 0 | 0 | 0 | 0 | 12 | 0.35 | 0 | 0 | 0 | 0 |
| bigdata | 51 | 36,077 | 51 | 0 | 3 | 0 | 0 | 0 | 0 | 10 | 0.28 | 0 | 0 | 0 | 0 |
| chaos | 32 | 27,685 | 32 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0.33 | 0 | 0 | 0 | 0 |
| clickhouse | 36 | 33,196 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0.30 | 0 | 0 | 0 | 0 |
| cloud | 35 | 40,972 | 35 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0.12 | 0 | 0 | 0 | 0 |
| cloud-native | 55 | 37,252 | 55 | 0 | 3 | 0 | 0 | 0 | 0 | 10 | 0.27 | 0 | 0 | 0 | 0 |
| design-pattern | 49 | 55,749 | 49 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0.16 | 0 | 0 | 0 | 0 |
| devops | 30 | 17,946 | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0.56 | 0 | 0 | 0 | 0 |
| es | 63 | 19,692 | 63 | 0 | 0 | 0 | 0 | 0 | 0 | 11 | 0.56 | 0 | 0 | 0 | 0 |
| filesystem | 94 | 72,924 | 81 | 0 | 3 | 0 | 0 | 0 | 0 | 13 | 0.18 | 0 | 0 | 0 | 0 |
| frontend | 65 | 29,554 | 65 | 0 | 2 | 0 | 0 | 0 | 0 | 10 | 0.34 | 0 | 0 | 0 | 0 |
| game | 39 | 12,703 | 39 | 0 | 2 | 0 | 0 | 0 | 0 | 11 | 0.87 | 0 | 0 | 0 | 0 |
| go | 36 | 41,733 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0.24 | 0 | 0 | 0 | 0 |
| iot | 35 | 10,383 | 35 | 0 | 2 | 0 | 0 | 0 | 0 | 12 | 1.16 | 0 | 0 | 0 | 0 |
| java | 53 | 18,226 | 53 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 0.71 | 0 | 0 | 0 | 0 |
| java-language | 55 | 5,715 | 55 | 0 | 55 | 0 | 0 | 0 | 0 | 8 | 1.40 | 0 | 0 | 0 | 0 |
| kafka | 73 | 98,108 | 73 | 0 | 3 | 0 | 0 | 0 | 0 | 11 | 0.11 | 0 | 0 | 0 | 0 |
| linux | 71 | 48,733 | 71 | 0 | 3 | 0 | 0 | 0 | 0 | 11 | 0.23 | 0 | 0 | 0 | 0 |
| mysql | 67 | 87,138 | 67 | 0 | 4 | 0 | 0 | 0 | 0 | 12 | 0.14 | 0 | 0 | 0 | 0 |
| network | 66 | 48,191 | 66 | 0 | 3 | 0 | 0 | 0 | 0 | 9 | 0.19 | 0 | 0 | 0 | 0 |
| observability | 50 | 42,391 | 50 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0.24 | 0 | 0 | 0 | 0 |
| postgresql | 53 | 49,045 | 53 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 0.20 | 0 | 0 | 0 | 0 |
| python | 60 | 69,098 | 60 | 0 | 3 | 0 | 0 | 0 | 0 | 10 | 0.14 | 0 | 0 | 0 | 0 |
| redis | 59 | 75,380 | 59 | 0 | 3 | 0 | 0 | 0 | 0 | 11 | 0.15 | 0 | 0 | 0 | 0 |
| rust | 35 | 21,837 | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0.41 | 0 | 0 | 0 | 0 |
| security | 36 | 21,758 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 13 | 0.60 | 0 | 0 | 0 | 0 |
| system-design | 52 | 73,679 | 52 | 0 | 0 | 0 | 0 | 0 | 0 | 11 | 0.15 | 0 | 0 | 0 | 0 |
| tools | 13 | 8,336 | 13 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0.96 | 0 | 0 | 0 | 0 |
| video | 67 | 57,745 | 67 | 0 | 3 | 0 | 0 | 0 | 0 | 9 | 0.16 | 0 | 0 | 0 | 0 |

### 〇·a、跨站引用低密度站（28 站，每千字 < 1 链接）

| 子站 | 密度（每千字）| xsite 链接 | 字数 |
|------|-----:|-----:|-----:|
| kafka | 0.11 | 11 | 98,108 |
| cloud | 0.12 | 5 | 40,972 |
| mysql | 0.14 | 12 | 87,138 |
| python | 0.14 | 10 | 69,098 |
| redis | 0.15 | 11 | 75,380 |
| system-design | 0.15 | 11 | 73,679 |
| video | 0.16 | 9 | 57,745 |
| design-pattern | 0.16 | 9 | 55,749 |
| filesystem | 0.18 | 13 | 72,924 |
| network | 0.19 | 9 | 48,191 |
| postgresql | 0.20 | 10 | 49,045 |
| linux | 0.23 | 11 | 48,733 |
| observability | 0.24 | 10 | 42,391 |
| go | 0.24 | 10 | 41,733 |
| cloud-native | 0.27 | 10 | 37,252 |
| ai | 0.27 | 9 | 33,297 |
| bigdata | 0.28 | 10 | 36,077 |
| clickhouse | 0.30 | 10 | 33,196 |
| chaos | 0.33 | 9 | 27,685 |
| frontend | 0.34 | 10 | 29,554 |
| architecture | 0.35 | 12 | 34,189 |
| rust | 0.41 | 9 | 21,837 |
| devops | 0.56 | 10 | 17,946 |
| es | 0.56 | 11 | 19,692 |
| security | 0.60 | 13 | 21,758 |
| java | 0.71 | 13 | 18,226 |
| game | 0.87 | 11 | 12,703 |
| tools | 0.96 | 8 | 8,336 |

**建议**：这些站当前主要靠 index.md 末尾的 📚 相关阅读 段落带跨站链接，子文档间应互相引用。可参考 §8.60 xlink-injector 注入术语映射。

### 〇·b、内容完整度低（295 篇，completeness_score ≤ 3）

| 子站 | 平均分 | 低完整度 / 总数 | 建议 |
|------|------:|------:|------|
| tools-html | 2.0 | 13 / 13 | 加代码示例 / 表格 / Vue 组件 |
| android-html | 2.9 | 25 / 29 | 加代码示例 / 表格 / Vue 组件 |
| iot-html | 2.9 | 30 / 35 | 加代码示例 / 表格 / Vue 组件 |
| chaos-html | 3.0 | 25 / 32 | 加代码示例 / 表格 / Vue 组件 |
| game-html | 3.0 | 34 / 39 | 加代码示例 / 表格 / Vue 组件 |
| rust-html | 3.0 | 25 / 35 | 加代码示例 / 表格 / Vue 组件 |
| devops-html | 3.3 | 17 / 30 | 加代码示例 / 表格 / Vue 组件 |
| system-design-html | 3.5 | 28 / 52 | 加代码示例 / 表格 / Vue 组件 |
| design-pattern-html | 3.6 | 25 / 49 | 加代码示例 / 表格 / Vue 组件 |
| go-html | 3.7 | 12 / 36 | 加代码示例 / 表格 / Vue 组件 |
| filesystem-html | 3.7 | 16 / 94 | 加代码示例 / 表格 / Vue 组件 |
| postgresql-html | 3.8 | 13 / 53 | 加代码示例 / 表格 / Vue 组件 |
| security-html | 3.9 | 6 / 36 | 加代码示例 / 表格 / Vue 组件 |
| network-html | 4.0 | 3 / 66 | 加代码示例 / 表格 / Vue 组件 |
| java-html | 4.0 | 9 / 53 | 加代码示例 / 表格 / Vue 组件 |
| frontend-html | 4.2 | 5 / 65 | 加代码示例 / 表格 / Vue 组件 |
| mysql-html | 4.3 | 1 / 67 | 加代码示例 / 表格 / Vue 组件 |
| observability-html | 4.4 | 1 / 50 | 加代码示例 / 表格 / Vue 组件 |
| bigdata-html | 4.5 | 2 / 51 | 加代码示例 / 表格 / Vue 组件 |
| video-html | 4.5 | 1 / 67 | 加代码示例 / 表格 / Vue 组件 |
| clickhouse-html | 4.5 | 3 / 36 | 加代码示例 / 表格 / Vue 组件 |
| cloud-native-html | 4.7 | 1 / 55 | 加代码示例 / 表格 / Vue 组件 |

## 七、跨子站重复标题（186 组 — 候选合并/跨站引用）

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
- **'BASE 理论'** (2 处)
  - `architecture/base.md`
  - `cloud/cap-base.md`
- **'Raft 共识算法'** (2 处)
  - `architecture/raft.md`
  - `system-design/raft.md`
- **'Paxos vs Raft'** (2 处)
  - `architecture/raft.md`
  - `system-design/paxos.md`
- **'角色与状态'** (2 处)
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
- ... 及其他 156 组

## 八、关键发现与建议

1. **图片覆盖率极低**：0 张图 / 1567 篇 = 0.0%，纯文字技术文档严重缺乏视觉化（C11 价值高）
2. **跨站引用密度**：全局 319 处（§8.60 注入 +152），平均 0.26 链接/千字。详见'〇·a 低密度站清单'补强
3. **薄页比例 0.0%**：0 篇字数 < 200，可能为 placeholder 或拆分过度（C3 持续 review）
4. **frontmatter 覆盖率 100.0%**：0 篇缺 FM，1554 篇 FM 缺 date——但 VitePress 已配 `lastUpdated: true`，自动用 git commit 时间，**非真问题**（C1 模板可选择性根治）
5. **过期内容 0 篇**（> 365 天）：需要月度 review 流程（C10）
6. **内部死链 0 处**：可能是 VitePress cleanUrls 导致文件名不一致，建议用 check-links.py depth=3 交叉验证
