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
| 跨子站重复标题 | 0 | ≤ 20 | ✅ |

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

### 〇·b、内容完整度低（13 篇，completeness_score ≤ 3）

| 子站 | 平均分 | 低完整度 / 总数 | 建议 |
|------|------:|------:|------|
| filesystem-html | 3.8 | 13 / 94 | 加代码示例 / 表格 / Vue 组件 |

## 七·b、同站重复标题（58 组 — cheatsheet 类常见）

同站多个文件出现相同标题（多为 cheatsheet / overview / 总览页）。

- **'🆚 vs LangGraph'** (4 处)
  - `ai/langchain.md`
  - `ai/dify-coze.md`
  - `ai/autogen.md`
  - `ai/crewai.md`
- **'🆚 vs Deployment'** (2 处)
  - `cloud-native/daemonset.md`
  - `cloud-native/statefulset.md`
- **'与 Decorator 区别'** (2 处)
  - `design-pattern/proxy.md`
  - `design-pattern/chain-of-responsibility.md`
- **'🆚 三者对比'** (2 处)
  - `frontend/package-manager.md`
  - `frontend/svelte.md`
- **'KafkaTemplate'** (2 处)
  - `kafka/intro.md`
  - `kafka/kafka-template.md`
- **'htop - top 的升级版'** (2 处)
  - `linux/top-htop.md`
  - `linux/ps-top.md`
- **'🆚 替代品'** (4 处)
  - `linux/find.md`
  - `linux/xargs.md`
  - `linux/grep.md`
  - `linux/ss.md`
- **'关联数组（map）'** (2 处)
  - `linux/bash-syntax.md`
  - `linux/arrays.md`
- **'开启慢查询日志'** (2 处)
  - `mysql/slow-log.md`
  - `mysql/slow-query.md`
- **'慢查询日志格式'** (2 处)
  - `mysql/slow-log.md`
  - `mysql/slow-query.md`
- **'性能提升数据'** (2 处)
  - `mysql/proxysql.md`
  - `mysql/read-write-split.md`
- **'自动填充（create_time / update_time）'** (2 处)
  - `mysql/advanced.md`
  - `mysql/mybatis-plus.md`
- **'ShardingSphere 是什么？'** (2 处)
  - `mysql/shardingsphere.md`
  - `mysql/sharding-jdbc.md`
- **'Saga 模式详解'** (2 处)
  - `mysql/saga-pattern.md`
  - `mysql/db-pattern.md`
- **'为什么需要读写分离？'** (2 处)
  - `mysql/read-write-split.md`
  - `mysql/read-write-split.md`
- **'实战案例：定位锁竞争'** (2 处)
  - `observability/pprof.md`
  - `observability/async-profiler.md`
- **'OTel Collector 详解'** (2 处)
  - `observability/overview.md`
  - `observability/collector.md`
- **'三大指标详解'** (2 处)
  - `observability/red-method.md`
  - `observability/use-method.md`
- **'何时选 PG'** (2 处)
  - `postgresql/oracle-vs-postgresql.md`
  - `postgresql/mongodb-vs-postgresql.md`
- **'COPY 协议（最快）'** (2 处)
  - `postgresql/jdbc.md`
  - `postgresql/psycopg.md`
- **'数据分析实战'** (2 处)
  - `python/analysis.md`
  - `python/pandas.md`
- **'创建 DataFrame'** (2 处)
  - `python/pandas.md`
  - `python/pandas.md`
- **'第一个爬虫'** (2 处)
  - `python/basics.md`
  - `python/scrapy.md`
- **'实战：登录 + 爬取'** (2 处)
  - `python/dynamic.md`
  - `python/requests-bs4.md`
- **'Hugging Face'** (2 处)
  - `python/huggingface.md`
  - `python/overview.md`
- **'计算机视觉'** (2 处)
  - `python/cv.md`
  - `python/overview.md`
- **'LLM 应用开发'** (2 处)
  - `python/overview.md`
  - `python/llm-apps.md`
- **'自然语言处理'** (2 处)
  - `python/overview.md`
  - `python/nlp.md`
- **'Fixture（测试夹具）'** (2 处)
  - `python/pytest.md`
  - `python/testing.md`
- **'参数化测试'** (2 处)
  - `python/pytest.md`
  - `python/testing.md`
- ... 及其他 28 组

## 八、关键发现与建议

1. **图片覆盖率极低**：0 张图 / 1567 篇 = 0.0%，纯文字技术文档严重缺乏视觉化（C11 价值高）
2. **跨站引用密度**：全局 399 处（§8.60 注入 +152），平均 0.30 链接/千字。详见'〇·a 低密度站清单'补强
3. **薄页比例 0.0%**：0 篇字数 < 200，可能为 placeholder 或拆分过度（C3 持续 review）
4. **frontmatter 覆盖率 100.0%**：0 篇缺 FM，1554 篇 FM 缺 date——但 VitePress 已配 `lastUpdated: true`，自动用 git commit 时间，**非真问题**（C1 模板可选择性根治）
5. **过期内容 0 篇**（> 365 天）：需要月度 review 流程（C10）
6. **内部死链 0 处**：可能是 VitePress cleanUrls 导致文件名不一致，建议用 check-links.py depth=3 交叉验证
