# 内容质量审计报告 — 2026-08-29

> 自动生成 by `scripts/audit-content.py`（C3 baseline）
> 检测范围: 31 子站 × 1576 .md 文件

## 〇、Summary

| 指标 | 数值 | 健康阈值 | 状态 |
|------|------|----------|------|
| 总文件数 | 1576 | — | — |
| 总字数（中英混合） | 1,343,340 | — | — |
| frontmatter 覆盖率 | 100.0% | ≥ 95% | ✅ |
| 薄页豁免（cheatsheet.md, graph.md, mindmap.md + 站点:java-language） | 103 | — | 结构预期字数少，不计入薄页 |
| 薄页（< 200 字，扣除豁免） | 8 (0.5%) | ≤ 5% | ✅ |
| 缺 frontmatter | 0 | 0 | ✅ |
| frontmatter 缺 date | 0 | 0 | ✅（VitePress `lastUpdated: true` 兜底）|
| 过期内容（> 365 天） | 0 | ≤ 10% | ✅ |
| 图片总数 | 101 | — | ⚠️ 偏少 |
| 缺 alt 的图片 | 0 | 0 | ✅ |
| 内部死链 | 0 | 0 | ✅ |
| 跨站引用 | 1380 | ≥ 100 | ✅ |
| Vue prop 数组缺逗号 | 0 | 0 | ✅ |
| Vue 组件缺失（md 引用无 .vue） | 0 | 0 | ✅ |
| Mermaid 代码块未闭合 | 0 | 0 | ✅ |
| 标题层级跳级 | 0 | 0 | ✅ |
| 跨子站重复标题 | 0 | ≤ 20 | ✅ |

## 一、各子站统计

| 子站 | 文件 | 字数 | FM | 薄页 | 豁免 | 缺FM | 过期 | 图片 | 死链 | 跨站 | 密度 | VueBug | 缺组件 | Mermaid | 标题跳级 |
|------|-----:|-----:|---:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|-----:|---------:|
| ai | 57 | 34,662 | 57 | 0 | 3 | 0 | 0 | 4 | 0 | 45 | 1.30 | 0 | 0 | 0 | 0 |
| android | 29 | 11,551 | 29 | 0 | 2 | 0 | 0 | 3 | 0 | 13 | 1.13 | 0 | 0 | 0 | 0 |
| architecture | 51 | 34,992 | 51 | 0 | 3 | 0 | 0 | 7 | 0 | 12 | 0.34 | 0 | 0 | 0 | 0 |
| bigdata | 51 | 37,445 | 51 | 0 | 3 | 0 | 0 | 4 | 0 | 46 | 1.23 | 0 | 0 | 0 | 0 |
| chaos | 32 | 31,847 | 32 | 0 | 0 | 0 | 0 | 2 | 0 | 45 | 1.41 | 0 | 0 | 0 | 0 |
| clickhouse | 36 | 35,477 | 36 | 0 | 0 | 0 | 0 | 1 | 0 | 46 | 1.30 | 0 | 0 | 0 | 0 |
| cloud | 35 | 43,173 | 35 | 0 | 3 | 0 | 0 | 3 | 0 | 77 | 1.78 | 0 | 0 | 0 | 0 |
| cloud-native | 55 | 38,720 | 55 | 0 | 3 | 0 | 0 | 1 | 0 | 46 | 1.19 | 0 | 0 | 0 | 0 |
| design-pattern | 49 | 60,750 | 49 | 0 | 0 | 0 | 0 | 3 | 0 | 81 | 1.33 | 0 | 0 | 0 | 0 |
| devops | 30 | 22,405 | 30 | 0 | 0 | 0 | 0 | 3 | 0 | 28 | 1.25 | 0 | 0 | 0 | 0 |
| es | 63 | 20,000 | 63 | 0 | 0 | 0 | 0 | 3 | 0 | 11 | 0.55 | 0 | 0 | 0 | 0 |
| filesystem | 94 | 81,388 | 81 | 0 | 3 | 0 | 0 | 2 | 0 | 85 | 1.04 | 0 | 0 | 0 | 0 |
| frontend | 65 | 30,836 | 65 | 0 | 2 | 0 | 0 | 1 | 0 | 28 | 0.91 | 0 | 0 | 0 | 0 |
| game | 39 | 16,965 | 39 | 0 | 2 | 0 | 0 | 3 | 0 | 11 | 0.65 | 0 | 0 | 0 | 0 |
| go | 36 | 46,069 | 36 | 0 | 0 | 0 | 0 | 1 | 0 | 64 | 1.39 | 0 | 0 | 0 | 0 |
| iot | 35 | 14,041 | 35 | 0 | 2 | 0 | 0 | 2 | 0 | 12 | 0.85 | 0 | 0 | 0 | 0 |
| java | 53 | 19,888 | 53 | 0 | 0 | 0 | 0 | 3 | 0 | 13 | 0.65 | 0 | 0 | 0 | 0 |
| java-language | 55 | 6,007 | 55 | 0 | 55 | 0 | 0 | 2 | 0 | 8 | 1.33 | 0 | 0 | 0 | 0 |
| kafka | 73 | 103,537 | 73 | 0 | 3 | 0 | 0 | 4 | 0 | 59 | 0.57 | 0 | 0 | 0 | 0 |
| linux | 71 | 51,087 | 71 | 0 | 3 | 0 | 0 | 4 | 0 | 65 | 1.27 | 0 | 0 | 0 | 0 |
| mysql | 67 | 90,333 | 67 | 0 | 4 | 0 | 0 | 7 | 0 | 28 | 0.31 | 0 | 0 | 0 | 0 |
| network | 66 | 51,721 | 66 | 0 | 3 | 0 | 0 | 6 | 0 | 81 | 1.57 | 0 | 0 | 0 | 0 |
| observability | 50 | 45,576 | 50 | 0 | 0 | 0 | 0 | 5 | 0 | 64 | 1.40 | 0 | 0 | 0 | 0 |
| postgresql | 53 | 56,518 | 53 | 0 | 0 | 0 | 0 | 1 | 0 | 64 | 1.13 | 0 | 0 | 0 | 0 |
| python | 69 | 76,570 | 69 | 8 | 3 | 0 | 0 | 2 | 0 | 109 | 1.42 | 0 | 0 | 0 | 0 |
| redis | 59 | 77,810 | 59 | 0 | 3 | 0 | 0 | 6 | 0 | 83 | 1.07 | 0 | 0 | 0 | 0 |
| rust | 35 | 26,920 | 35 | 0 | 0 | 0 | 0 | 1 | 0 | 9 | 0.33 | 0 | 0 | 0 | 0 |
| security | 36 | 26,735 | 36 | 0 | 0 | 0 | 0 | 2 | 0 | 31 | 1.16 | 0 | 0 | 0 | 0 |
| system-design | 52 | 82,029 | 52 | 0 | 0 | 0 | 0 | 13 | 0 | 83 | 1.01 | 0 | 0 | 0 | 0 |
| tools | 13 | 9,844 | 13 | 0 | 0 | 0 | 0 | 1 | 0 | 8 | 0.81 | 0 | 0 | 0 | 0 |
| video | 67 | 58,444 | 67 | 0 | 3 | 0 | 0 | 1 | 0 | 25 | 0.43 | 0 | 0 | 0 | 0 |

### 〇·a、跨站引用低密度站（11 站，每千字 < 1 链接）

| 子站 | 密度（每千字）| xsite 链接 | 字数 |
|------|-----:|-----:|-----:|
| mysql | 0.31 | 28 | 90,333 |
| rust | 0.33 | 9 | 26,920 |
| architecture | 0.34 | 12 | 34,992 |
| video | 0.43 | 25 | 58,444 |
| es | 0.55 | 11 | 20,000 |
| kafka | 0.57 | 59 | 103,537 |
| game | 0.65 | 11 | 16,965 |
| java | 0.65 | 13 | 19,888 |
| tools | 0.81 | 8 | 9,844 |
| iot | 0.85 | 12 | 14,041 |
| frontend | 0.91 | 28 | 30,836 |

**建议**：这些站当前主要靠 index.md 末尾的 📚 相关阅读 段落带跨站链接，子文档间应互相引用。可参考 §8.60 xlink-injector 注入术语映射。

## 二、薄页清单（8 篇）

- `python/05-scraping/README.md (154字)`
- `python/04-concurrency/README.md (167字)`
- `python/07-data/README.md (168字)`
- `python/03-libraries/README.md (168字)`
- `python/01-basics/README.md (173字)`
- `python/06-ai-ml/README.md (186字)`
- `python/08-algorithms/README.md (188字)`
- `python/09-enterprise/README.md (189字)`

### 〇·b、内容完整度低（9 篇，completeness_score ≤ 3）

| 子站 | 平均分 | 低完整度 / 总数 | 建议 |
|------|------:|------:|------|
| python-html | 4.4 | 9 / 69 | 加代码示例 / 表格 / Vue 组件 |

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

1. **图片覆盖率极低**：101 张图 / 1576 篇 = 6.4%，纯文字技术文档严重缺乏视觉化（C11 价值高）
2. **跨站引用密度**：全局 1380 处（§8.60 注入 +152），平均 1.03 链接/千字。详见'〇·a 低密度站清单'补强
3. **薄页比例 0.5%**：8 篇字数 < 200，可能为 placeholder 或拆分过度（C3 持续 review）
4. **frontmatter 覆盖率 100.0%**：0 篇缺 FM，0 篇 FM 缺 date——但 VitePress 已配 `lastUpdated: true`，自动用 git commit 时间，**非真问题**（C1 模板可选择性根治）
5. **过期内容 0 篇**（> 365 天）：需要月度 review 流程（C10）
6. **内部死链 0 处**：可能是 VitePress cleanUrls 导致文件名不一致，建议用 check-links.py depth=3 交叉验证
