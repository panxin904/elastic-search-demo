# 内容质量审计报告 — 2026-08-29

> 自动生成 by `scripts/audit-content.py`（C3 baseline）
> 检测范围: 31 子站 × 1567 .md 文件

## 〇、Summary

| 指标 | 数值 | 健康阈值 | 状态 |
|------|------|----------|------|
| 总文件数 | 1567 | — | — |
| 总字数（中英混合） | 1,328,722 | — | — |
| frontmatter 覆盖率 | 100.0% | ≥ 95% | ✅ |
| 薄页豁免（cheatsheet.md, graph.md, mindmap.md + 站点:java-language） | 103 | — | 结构预期字数少，不计入薄页 |
| 薄页（< 200 字，扣除豁免） | 0 (0.0%) | ≤ 5% | ✅ |
| 缺 frontmatter | 0 | 0 | ✅ |
| frontmatter 缺 date | 1554 | 0 | ⚠️（VitePress `lastUpdated: true` 兜底）|
| 过期内容（> 365 天） | 0 | ≤ 10% | ✅ |
| 图片总数 | 101 | — | ⚠️ 偏少 |
| 缺 alt 的图片 | 0 | 0 | ✅ |
| 内部死链 | 0 | 0 | ✅ |
| 跨站引用 | 1011 | ≥ 100 | ✅ |
| Vue prop 数组缺逗号 | 0 | 0 | ✅ |
| Vue 组件缺失（md 引用无 .vue） | 0 | 0 | ✅ |
| Mermaid 代码块未闭合 | 0 | 0 | ✅ |
| 标题层级跳级 | 0 | 0 | ✅ |
| 跨子站重复标题 | 0 | ≤ 20 | ✅ |

## 一、各子站统计

| 子站 | 文件 | 字数 | FM | 薄页 | 豁免 | 缺FM | 过期 | 图片 | 死链 | 跨站 | 密度 | VueBug | 缺组件 | Mermaid | 标题跳级 |
|------|-----:|-----:|---:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|-----:|---------:|
| ai | 57 | 34,074 | 57 | 0 | 3 | 0 | 0 | 4 | 0 | 27 | 0.79 | 0 | 0 | 0 | 0 |
| android | 29 | 11,435 | 29 | 0 | 2 | 0 | 0 | 3 | 0 | 13 | 1.14 | 0 | 0 | 0 | 0 |
| architecture | 51 | 34,788 | 51 | 0 | 3 | 0 | 0 | 7 | 0 | 12 | 0.34 | 0 | 0 | 0 | 0 |
| bigdata | 51 | 36,923 | 51 | 0 | 3 | 0 | 0 | 4 | 0 | 28 | 0.76 | 0 | 0 | 0 | 0 |
| chaos | 32 | 31,347 | 32 | 0 | 0 | 0 | 0 | 2 | 0 | 27 | 0.86 | 0 | 0 | 0 | 0 |
| clickhouse | 36 | 34,991 | 36 | 0 | 0 | 0 | 0 | 1 | 0 | 28 | 0.80 | 0 | 0 | 0 | 0 |
| cloud | 35 | 42,661 | 35 | 0 | 3 | 0 | 0 | 3 | 0 | 59 | 1.38 | 0 | 0 | 0 | 0 |
| cloud-native | 55 | 38,146 | 55 | 0 | 3 | 0 | 0 | 1 | 0 | 28 | 0.73 | 0 | 0 | 0 | 0 |
| design-pattern | 49 | 60,182 | 49 | 0 | 0 | 0 | 0 | 3 | 0 | 63 | 1.05 | 0 | 0 | 0 | 0 |
| devops | 30 | 21,943 | 30 | 0 | 0 | 0 | 0 | 3 | 0 | 10 | 0.46 | 0 | 0 | 0 | 0 |
| es | 63 | 19,748 | 63 | 0 | 0 | 0 | 0 | 3 | 0 | 11 | 0.56 | 0 | 0 | 0 | 0 |
| filesystem | 94 | 80,704 | 81 | 0 | 3 | 0 | 0 | 2 | 0 | 67 | 0.83 | 0 | 0 | 0 | 0 |
| frontend | 65 | 30,216 | 65 | 0 | 2 | 0 | 0 | 1 | 0 | 10 | 0.33 | 0 | 0 | 0 | 0 |
| game | 39 | 16,809 | 39 | 0 | 2 | 0 | 0 | 3 | 0 | 11 | 0.65 | 0 | 0 | 0 | 0 |
| go | 36 | 45,595 | 36 | 0 | 0 | 0 | 0 | 1 | 0 | 46 | 1.01 | 0 | 0 | 0 | 0 |
| iot | 35 | 13,901 | 35 | 0 | 2 | 0 | 0 | 2 | 0 | 12 | 0.86 | 0 | 0 | 0 | 0 |
| java | 53 | 19,676 | 53 | 0 | 0 | 0 | 0 | 3 | 0 | 13 | 0.66 | 0 | 0 | 0 | 0 |
| java-language | 55 | 5,787 | 55 | 0 | 55 | 0 | 0 | 2 | 0 | 8 | 1.38 | 0 | 0 | 0 | 0 |
| kafka | 73 | 103,245 | 73 | 0 | 3 | 0 | 0 | 4 | 0 | 59 | 0.57 | 0 | 0 | 0 | 0 |
| linux | 71 | 50,455 | 71 | 0 | 3 | 0 | 0 | 4 | 0 | 47 | 0.93 | 0 | 0 | 0 | 0 |
| mysql | 67 | 90,065 | 67 | 0 | 4 | 0 | 0 | 7 | 0 | 28 | 0.31 | 0 | 0 | 0 | 0 |
| network | 66 | 51,109 | 66 | 0 | 3 | 0 | 0 | 6 | 0 | 63 | 1.23 | 0 | 0 | 0 | 0 |
| observability | 50 | 45,034 | 50 | 0 | 0 | 0 | 0 | 5 | 0 | 46 | 1.02 | 0 | 0 | 0 | 0 |
| postgresql | 53 | 55,958 | 53 | 0 | 0 | 0 | 0 | 1 | 0 | 46 | 0.82 | 0 | 0 | 0 | 0 |
| python | 60 | 74,252 | 60 | 0 | 3 | 0 | 0 | 2 | 0 | 64 | 0.86 | 0 | 0 | 0 | 0 |
| redis | 59 | 77,202 | 59 | 0 | 3 | 0 | 0 | 6 | 0 | 65 | 0.84 | 0 | 0 | 0 | 0 |
| rust | 35 | 26,780 | 35 | 0 | 0 | 0 | 0 | 1 | 0 | 9 | 0.34 | 0 | 0 | 0 | 0 |
| security | 36 | 26,249 | 36 | 0 | 0 | 0 | 0 | 2 | 0 | 13 | 0.50 | 0 | 0 | 0 | 0 |
| system-design | 52 | 81,479 | 52 | 0 | 0 | 0 | 0 | 13 | 0 | 65 | 0.80 | 0 | 0 | 0 | 0 |
| tools | 13 | 9,792 | 13 | 0 | 0 | 0 | 0 | 1 | 0 | 8 | 0.82 | 0 | 0 | 0 | 0 |
| video | 67 | 58,176 | 67 | 0 | 3 | 0 | 0 | 1 | 0 | 25 | 0.43 | 0 | 0 | 0 | 0 |

### 〇·a、跨站引用低密度站（24 站，每千字 < 1 链接）

| 子站 | 密度（每千字）| xsite 链接 | 字数 |
|------|-----:|-----:|-----:|
| mysql | 0.31 | 28 | 90,065 |
| frontend | 0.33 | 10 | 30,216 |
| rust | 0.34 | 9 | 26,780 |
| architecture | 0.34 | 12 | 34,788 |
| video | 0.43 | 25 | 58,176 |
| devops | 0.46 | 10 | 21,943 |
| security | 0.50 | 13 | 26,249 |
| es | 0.56 | 11 | 19,748 |
| kafka | 0.57 | 59 | 103,245 |
| game | 0.65 | 11 | 16,809 |
| java | 0.66 | 13 | 19,676 |
| cloud-native | 0.73 | 28 | 38,146 |
| bigdata | 0.76 | 28 | 36,923 |
| ai | 0.79 | 27 | 34,074 |
| system-design | 0.80 | 65 | 81,479 |
| clickhouse | 0.80 | 28 | 34,991 |
| tools | 0.82 | 8 | 9,792 |
| postgresql | 0.82 | 46 | 55,958 |
| filesystem | 0.83 | 67 | 80,704 |
| redis | 0.84 | 65 | 77,202 |
| chaos | 0.86 | 27 | 31,347 |
| python | 0.86 | 64 | 74,252 |
| iot | 0.86 | 12 | 13,901 |
| linux | 0.93 | 47 | 50,455 |

**建议**：这些站当前主要靠 index.md 末尾的 📚 相关阅读 段落带跨站链接，子文档间应互相引用。可参考 §8.60 xlink-injector 注入术语映射。

## 七·b、同站重复标题（38 组 — cheatsheet 类常见）

同站多个文件出现相同标题（多为 cheatsheet / overview / 总览页）。

- **'KafkaTemplate'** (2 处)
  - `kafka/intro.md`
  - `kafka/kafka-template.md`
- **'htop - top 的升级版'** (2 处)
  - `linux/top-htop.md`
  - `linux/ps-top.md`
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
- **'OTel Collector 详解'** (2 处)
  - `observability/overview.md`
  - `observability/collector.md`
- **'何时选 PG'** (2 处)
  - `postgresql/oracle-vs-postgresql.md`
  - `postgresql/mongodb-vs-postgresql.md`
- **'数据分析实战'** (2 处)
  - `python/analysis.md`
  - `python/pandas.md`
- **'第一个爬虫'** (2 处)
  - `python/basics.md`
  - `python/scrapy.md`
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
- **'Mock（模拟对象）'** (2 处)
  - `python/pytest.md`
  - `python/testing.md`
- **'Lettuce 连接池（可选）'** (2 处)
  - `redis/connection-pool.md`
  - `redis/lettuce.md`
- **'嵌入式 Rust'** (2 处)
  - `rust/overview.md`
  - `rust/embedded.md`
- **'WebAssembly'** (2 处)
  - `rust/overview.md`
  - `rust/wasm.md`
- **'Cargo.toml'** (2 处)
  - `rust/hello-world.md`
  - `rust/cargo.md`
- **'实战：Ed25519 签名'** (2 处)
  - `security/signature.md`
  - `security/asymmetric.md`
- **'Python API'** (3 处)
  - `video/gstreamer.md`
  - `video/super-res-ai.md`
  - `video/super-res.md`
- **'Wav2Lip 使用'** (2 处)
  - `video/digital-human.md`
  - `video/lip-sync.md`
- **'视频批量超分'** (2 处)
  - `video/super-res-ai.md`
  - `video/super-res.md`
- **'MPS 核心能力'** (2 处)
  - `video/aliyun-mps.md`
  - `video/tencent-mps.md`
- **'SDK 调用'** (2 处)
  - `video/aliyun-mps.md`
  - `video/tencent-mps.md`
- **'FFmpeg 实操'** (2 处)
  - `video/color-space.md`
  - `video/audio-codec.md`
- ... 及其他 8 组

## 八、关键发现与建议

1. **图片覆盖率极低**：101 张图 / 1567 篇 = 6.4%，纯文字技术文档严重缺乏视觉化（C11 价值高）
2. **跨站引用密度**：全局 1011 处（§8.60 注入 +152），平均 0.76 链接/千字。详见'〇·a 低密度站清单'补强
3. **薄页比例 0.0%**：0 篇字数 < 200，可能为 placeholder 或拆分过度（C3 持续 review）
4. **frontmatter 覆盖率 100.0%**：0 篇缺 FM，1554 篇 FM 缺 date——但 VitePress 已配 `lastUpdated: true`，自动用 git commit 时间，**非真问题**（C1 模板可选择性根治）
5. **过期内容 0 篇**（> 365 天）：需要月度 review 流程（C10）
6. **内部死链 0 处**：可能是 VitePress cleanUrls 导致文件名不一致，建议用 check-links.py depth=3 交叉验证
