# 内容质量审计报告 — 2026-09-05

> 自动生成 by `scripts/audit-content.py`（C3 baseline）
> 检测范围: 31 子站 × 1662 .md 文件

## 〇、Summary

| 指标 | 数值 | 健康阈值 | 状态 |
|------|------|----------|------|
| 总文件数 | 1662 | — | — |
| 总字数（中英混合） | 1,364,991 | — | — |
| frontmatter 覆盖率 | 100.0% | ≥ 95% | ✅ |
| 薄页豁免（cheatsheet.md, graph.md, mindmap.md + 站点:java-language） | 146 | — | 结构预期字数少，不计入薄页 |
| 薄页（< 200 字，扣除豁免） | 28 (1.7%) | ≤ 5% | ✅ |
| 缺 frontmatter | 0 | 0 | ✅ |
| frontmatter 缺 date | 0 | 0 | ✅（VitePress `lastUpdated: true` 兜底）|
| 过期内容（> 365 天） | 0 | ≤ 10% | ✅ |
| 图片总数 | 201 | — | ✅ |
| 缺 alt 的图片 | 0 | 0 | ✅ |
| 内部死链 | 0 | 0 | ✅ |
| 跨站引用 | 1387 | ≥ 100 | ✅ |
| Vue prop 数组缺逗号 | 0 | 0 | ✅ |
| Vue 组件缺失（md 引用无 .vue） | 0 | 0 | ✅ |
| Mermaid 代码块未闭合 | 0 | 0 | ✅ |
| 标题层级跳级 | 0 | 0 | ✅ |
| 跨子站重复标题 | 0 | ≤ 20 | ✅ |

## 一、各子站统计

| 子站 | 文件 | 字数 | FM | 薄页 | 豁免 | 缺FM | 过期 | 图片 | 死链 | 跨站 | 密度 | VueBug | 缺组件 | Mermaid | 标题跳级 |
|------|-----:|-----:|---:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|-----:|---------:|
| ai | 67 | 41,711 | 67 | 0 | 3 | 0 | 0 | 4 | 0 | 45 | 1.08 | 0 | 0 | 0 | 0 |
| android | 36 | 12,236 | 36 | 6 | 3 | 0 | 0 | 3 | 0 | 13 | 1.06 | 0 | 0 | 0 | 0 |
| architecture | 51 | 35,035 | 51 | 0 | 3 | 0 | 0 | 7 | 0 | 12 | 0.34 | 0 | 0 | 0 | 0 |
| bigdata | 51 | 37,488 | 51 | 0 | 3 | 0 | 0 | 4 | 0 | 46 | 1.23 | 0 | 0 | 0 | 0 |
| chaos | 36 | 32,551 | 36 | 0 | 3 | 0 | 0 | 2 | 0 | 45 | 1.38 | 0 | 0 | 0 | 0 |
| clickhouse | 40 | 36,180 | 40 | 0 | 3 | 0 | 0 | 3 | 0 | 46 | 1.27 | 0 | 0 | 0 | 0 |
| cloud | 35 | 43,216 | 35 | 0 | 3 | 0 | 0 | 3 | 0 | 77 | 1.78 | 0 | 0 | 0 | 0 |
| cloud-native | 55 | 38,891 | 55 | 0 | 3 | 0 | 0 | 20 | 0 | 46 | 1.18 | 0 | 0 | 0 | 0 |
| design-pattern | 53 | 61,454 | 53 | 0 | 3 | 0 | 0 | 3 | 0 | 81 | 1.32 | 0 | 0 | 0 | 0 |
| devops | 34 | 23,085 | 34 | 0 | 3 | 0 | 0 | 3 | 0 | 28 | 1.21 | 0 | 0 | 0 | 0 |
| es | 67 | 21,243 | 67 | 0 | 3 | 0 | 0 | 19 | 0 | 14 | 0.66 | 0 | 0 | 0 | 0 |
| filesystem | 94 | 81,452 | 81 | 0 | 3 | 0 | 0 | 4 | 0 | 85 | 1.04 | 0 | 0 | 0 | 0 |
| frontend | 66 | 31,566 | 66 | 0 | 3 | 0 | 0 | 4 | 0 | 28 | 0.89 | 0 | 0 | 0 | 0 |
| game | 48 | 17,943 | 48 | 8 | 3 | 0 | 0 | 3 | 0 | 11 | 0.61 | 0 | 0 | 0 | 0 |
| go | 40 | 46,772 | 40 | 0 | 3 | 0 | 0 | 3 | 0 | 64 | 1.37 | 0 | 0 | 0 | 0 |
| iot | 42 | 14,801 | 42 | 6 | 3 | 0 | 0 | 2 | 0 | 12 | 0.81 | 0 | 0 | 0 | 0 |
| java | 57 | 21,251 | 57 | 0 | 3 | 0 | 0 | 3 | 0 | 17 | 0.80 | 0 | 0 | 0 | 0 |
| java-language | 55 | 6,050 | 55 | 0 | 55 | 0 | 0 | 2 | 0 | 8 | 1.32 | 0 | 0 | 0 | 0 |
| kafka | 73 | 103,713 | 73 | 0 | 3 | 0 | 0 | 20 | 0 | 59 | 0.57 | 0 | 0 | 0 | 0 |
| linux | 71 | 51,130 | 71 | 0 | 3 | 0 | 0 | 4 | 0 | 65 | 1.27 | 0 | 0 | 0 | 0 |
| mysql | 67 | 90,519 | 67 | 0 | 4 | 0 | 0 | 23 | 0 | 28 | 0.31 | 0 | 0 | 0 | 0 |
| network | 66 | 51,764 | 66 | 0 | 3 | 0 | 0 | 6 | 0 | 81 | 1.56 | 0 | 0 | 0 | 0 |
| observability | 54 | 46,280 | 54 | 0 | 3 | 0 | 0 | 5 | 0 | 64 | 1.38 | 0 | 0 | 0 | 0 |
| postgresql | 57 | 57,223 | 57 | 0 | 3 | 0 | 0 | 4 | 0 | 64 | 1.12 | 0 | 0 | 0 | 0 |
| python | 69 | 76,613 | 69 | 8 | 3 | 0 | 0 | 2 | 0 | 109 | 1.42 | 0 | 0 | 0 | 0 |
| redis | 59 | 77,994 | 59 | 0 | 3 | 0 | 0 | 22 | 0 | 83 | 1.06 | 0 | 0 | 0 | 0 |
| rust | 39 | 27,623 | 39 | 0 | 3 | 0 | 0 | 3 | 0 | 9 | 0.33 | 0 | 0 | 0 | 0 |
| security | 40 | 27,423 | 40 | 0 | 3 | 0 | 0 | 2 | 0 | 31 | 1.13 | 0 | 0 | 0 | 0 |
| system-design | 56 | 82,733 | 56 | 0 | 3 | 0 | 0 | 13 | 0 | 83 | 1.00 | 0 | 0 | 0 | 0 |
| tools | 17 | 10,532 | 17 | 0 | 3 | 0 | 0 | 1 | 0 | 8 | 0.76 | 0 | 0 | 0 | 0 |
| video | 67 | 58,519 | 67 | 0 | 3 | 0 | 0 | 4 | 0 | 25 | 0.43 | 0 | 0 | 0 | 0 |

### 〇·a、跨站引用低密度站（11 站，每千字 < 1 链接）

| 子站 | 密度（每千字）| xsite 链接 | 字数 |
|------|-----:|-----:|-----:|
| mysql | 0.31 | 28 | 90,519 |
| rust | 0.33 | 9 | 27,623 |
| architecture | 0.34 | 12 | 35,035 |
| video | 0.43 | 25 | 58,519 |
| kafka | 0.57 | 59 | 103,713 |
| game | 0.61 | 11 | 17,943 |
| es | 0.66 | 14 | 21,243 |
| tools | 0.76 | 8 | 10,532 |
| java | 0.80 | 17 | 21,251 |
| iot | 0.81 | 12 | 14,801 |
| frontend | 0.89 | 28 | 31,566 |

**建议**：这些站当前主要靠 index.md 末尾的 📚 相关阅读 段落带跨站链接，子文档间应互相引用。可参考 §8.60 xlink-injector 注入术语映射。

## 二、薄页清单（28 篇）

- `android/01-app/index.md (73字)`
- `android/04-cross/index.md (74字)`
- `android/03-system/index.md (74字)`
- `android/02-ui/index.md (75字)`
- `android/05-toolchain/index.md (76字)`
- `android/06-perf/index.md (83字)`
- `iot/03-edge/index.md (85字)`
- `iot/01-protocol/index.md (85字)`
- `iot/05-timeseries/index.md (85字)`
- `iot/02-device/index.md (88字)`
- `game/06-audio/index.md (88字)`
- `game/02-render/index.md (90字)`
- `iot/04-management/index.md (91字)`
- `iot/06-platform/index.md (92字)`
- `game/05-network/index.md (92字)`
- `game/08-ship/index.md (93字)`
- `game/03-physics/index.md (94字)`
- `game/01-engine/index.md (94字)`
- `game/07-toolchain/index.md (95字)`
- `game/04-ai/index.md (96字)`
- `python/05-scraping/README.md (154字)`
- `python/04-concurrency/README.md (167字)`
- `python/07-data/README.md (168字)`
- `python/03-libraries/README.md (168字)`
- `python/01-basics/README.md (173字)`
- `python/06-ai-ml/README.md (186字)`
- `python/08-algorithms/README.md (188字)`
- `python/09-enterprise/README.md (189字)`

### 〇·b、内容完整度低（43 篇，completeness_score ≤ 3）

| 子站 | 平均分 | 低完整度 / 总数 | 建议 |
|------|------:|------:|------|
| tools-html | 3.4 | 1 / 17 | 加代码示例 / 表格 / Vue 组件 |
| android-html | 3.6 | 6 / 36 | 加代码示例 / 表格 / Vue 组件 |
| iot-html | 3.6 | 6 / 42 | 加代码示例 / 表格 / Vue 组件 |
| game-html | 3.7 | 8 / 48 | 加代码示例 / 表格 / Vue 组件 |
| chaos-html | 3.7 | 1 / 36 | 加代码示例 / 表格 / Vue 组件 |
| devops-html | 3.7 | 1 / 34 | 加代码示例 / 表格 / Vue 组件 |
| security-html | 3.8 | 1 / 40 | 加代码示例 / 表格 / Vue 组件 |
| rust-html | 3.8 | 1 / 39 | 加代码示例 / 表格 / Vue 组件 |
| go-html | 3.8 | 1 / 40 | 加代码示例 / 表格 / Vue 组件 |
| postgresql-html | 3.9 | 1 / 57 | 加代码示例 / 表格 / Vue 组件 |
| java-html | 3.9 | 1 / 57 | 加代码示例 / 表格 / Vue 组件 |
| design-pattern-html | 4.0 | 1 / 53 | 加代码示例 / 表格 / Vue 组件 |
| system-design-html | 4.0 | 1 / 56 | 加代码示例 / 表格 / Vue 组件 |
| clickhouse-html | 4.4 | 1 / 40 | 加代码示例 / 表格 / Vue 组件 |
| python-html | 4.4 | 9 / 69 | 加代码示例 / 表格 / Vue 组件 |
| ai-html | 4.4 | 1 / 67 | 加代码示例 / 表格 / Vue 组件 |
| observability-html | 4.5 | 1 / 54 | 加代码示例 / 表格 / Vue 组件 |
| es-html | 4.6 | 1 / 67 | 加代码示例 / 表格 / Vue 组件 |

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

1. **图片覆盖率极低**：201 张图 / 1662 篇 = 12.1%，纯文字技术文档严重缺乏视觉化（C11 价值高）
2. **跨站引用密度**：全局 1387 处（§8.60 注入 +152），平均 1.02 链接/千字。详见'〇·a 低密度站清单'补强
3. **薄页比例 1.7%**：28 篇字数 < 200，可能为 placeholder 或拆分过度（C3 持续 review）
4. **frontmatter 覆盖率 100.0%**：0 篇缺 FM，0 篇 FM 缺 date——但 VitePress 已配 `lastUpdated: true`，自动用 git commit 时间，**非真问题**（C1 模板可选择性根治）
5. **过期内容 0 篇**（> 365 天）：需要月度 review 流程（C10）
6. **内部死链 0 处**：可能是 VitePress cleanUrls 导致文件名不一致，建议用 check-links.py depth=3 交叉验证
