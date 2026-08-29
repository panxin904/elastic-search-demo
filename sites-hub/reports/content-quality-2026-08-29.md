# 内容质量审计报告 — 2026-08-29

> 自动生成 by `scripts/audit-content.py`（C3 baseline）
> 检测范围: 31 子站 × 1567 .md 文件

## 〇、Summary

| 指标 | 数值 | 健康阈值 | 状态 |
|------|------|----------|------|
| 总文件数 | 1567 | — | — |
| 总字数（中英混合） | 1,322,590 | — | — |
| frontmatter 覆盖率 | 100.0% | ≥ 95% | ✅ |
| 薄页豁免（cheatsheet.md, graph.md, mindmap.md + 站点:java-language） | 103 | — | 结构预期字数少，不计入薄页 |
| 薄页（< 200 字，扣除豁免） | 0 (0.0%) | ≤ 5% | ✅ |
| 缺 frontmatter | 0 | 0 | ✅ |
| frontmatter 缺 date | 1554 | 0 | ⚠️（VitePress `lastUpdated: true` 兜底）|
| 过期内容（> 365 天） | 0 | ≤ 10% | ✅ |
| 图片总数 | 101 | — | ⚠️ 偏少 |
| 缺 alt 的图片 | 0 | 0 | ✅ |
| 内部死链 | 0 | 0 | ✅ |
| 跨站引用 | 723 | ≥ 100 | ✅ |
| Vue prop 数组缺逗号 | 0 | 0 | ✅ |
| Vue 组件缺失（md 引用无 .vue） | 0 | 0 | ✅ |
| Mermaid 代码块未闭合 | 0 | 0 | ✅ |
| 标题层级跳级 | 0 | 0 | ✅ |
| 跨子站重复标题 | 0 | ≤ 20 | ✅ |

## 一、各子站统计

| 子站 | 文件 | 字数 | FM | 薄页 | 豁免 | 缺FM | 过期 | 图片 | 死链 | 跨站 | 密度 | VueBug | 缺组件 | Mermaid | 标题跳级 |
|------|-----:|-----:|---:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|-----:|---------:|
| ai | 57 | 33,714 | 57 | 0 | 3 | 0 | 0 | 4 | 0 | 9 | 0.27 | 0 | 0 | 0 | 0 |
| android | 29 | 11,435 | 29 | 0 | 2 | 0 | 0 | 3 | 0 | 13 | 1.14 | 0 | 0 | 0 | 0 |
| architecture | 51 | 34,788 | 51 | 0 | 3 | 0 | 0 | 7 | 0 | 12 | 0.34 | 0 | 0 | 0 | 0 |
| bigdata | 51 | 36,605 | 51 | 0 | 3 | 0 | 0 | 4 | 0 | 10 | 0.27 | 0 | 0 | 0 | 0 |
| chaos | 32 | 30,975 | 32 | 0 | 0 | 0 | 0 | 2 | 0 | 9 | 0.29 | 0 | 0 | 0 | 0 |
| clickhouse | 36 | 34,649 | 36 | 0 | 0 | 0 | 0 | 1 | 0 | 10 | 0.29 | 0 | 0 | 0 | 0 |
| cloud | 35 | 42,289 | 35 | 0 | 3 | 0 | 0 | 3 | 0 | 41 | 0.97 | 0 | 0 | 0 | 0 |
| cloud-native | 55 | 37,792 | 55 | 0 | 3 | 0 | 0 | 1 | 0 | 10 | 0.26 | 0 | 0 | 0 | 0 |
| design-pattern | 49 | 59,810 | 49 | 0 | 0 | 0 | 0 | 3 | 0 | 45 | 0.75 | 0 | 0 | 0 | 0 |
| devops | 30 | 21,943 | 30 | 0 | 0 | 0 | 0 | 3 | 0 | 10 | 0.46 | 0 | 0 | 0 | 0 |
| es | 63 | 19,748 | 63 | 0 | 0 | 0 | 0 | 3 | 0 | 11 | 0.56 | 0 | 0 | 0 | 0 |
| filesystem | 94 | 79,852 | 81 | 0 | 3 | 0 | 0 | 2 | 0 | 49 | 0.61 | 0 | 0 | 0 | 0 |
| frontend | 65 | 30,216 | 65 | 0 | 2 | 0 | 0 | 1 | 0 | 10 | 0.33 | 0 | 0 | 0 | 0 |
| game | 39 | 16,809 | 39 | 0 | 2 | 0 | 0 | 3 | 0 | 11 | 0.65 | 0 | 0 | 0 | 0 |
| go | 36 | 45,265 | 36 | 0 | 0 | 0 | 0 | 1 | 0 | 28 | 0.62 | 0 | 0 | 0 | 0 |
| iot | 35 | 13,901 | 35 | 0 | 2 | 0 | 0 | 2 | 0 | 12 | 0.86 | 0 | 0 | 0 | 0 |
| java | 53 | 19,676 | 53 | 0 | 0 | 0 | 0 | 3 | 0 | 13 | 0.66 | 0 | 0 | 0 | 0 |
| java-language | 55 | 5,787 | 55 | 0 | 55 | 0 | 0 | 2 | 0 | 8 | 1.38 | 0 | 0 | 0 | 0 |
| kafka | 73 | 103,245 | 73 | 0 | 3 | 0 | 0 | 4 | 0 | 59 | 0.57 | 0 | 0 | 0 | 0 |
| linux | 71 | 50,107 | 71 | 0 | 3 | 0 | 0 | 4 | 0 | 29 | 0.58 | 0 | 0 | 0 | 0 |
| mysql | 67 | 90,065 | 67 | 0 | 4 | 0 | 0 | 7 | 0 | 28 | 0.31 | 0 | 0 | 0 | 0 |
| network | 66 | 50,761 | 66 | 0 | 3 | 0 | 0 | 6 | 0 | 45 | 0.89 | 0 | 0 | 0 | 0 |
| observability | 50 | 44,692 | 50 | 0 | 0 | 0 | 0 | 5 | 0 | 28 | 0.63 | 0 | 0 | 0 | 0 |
| postgresql | 53 | 55,610 | 53 | 0 | 0 | 0 | 0 | 1 | 0 | 28 | 0.50 | 0 | 0 | 0 | 0 |
| python | 60 | 73,892 | 60 | 0 | 3 | 0 | 0 | 2 | 0 | 46 | 0.62 | 0 | 0 | 0 | 0 |
| redis | 59 | 76,830 | 59 | 0 | 3 | 0 | 0 | 6 | 0 | 47 | 0.61 | 0 | 0 | 0 | 0 |
| rust | 35 | 26,780 | 35 | 0 | 0 | 0 | 0 | 1 | 0 | 9 | 0.34 | 0 | 0 | 0 | 0 |
| security | 36 | 26,249 | 36 | 0 | 0 | 0 | 0 | 2 | 0 | 13 | 0.50 | 0 | 0 | 0 | 0 |
| system-design | 52 | 81,137 | 52 | 0 | 0 | 0 | 0 | 13 | 0 | 47 | 0.58 | 0 | 0 | 0 | 0 |
| tools | 13 | 9,792 | 13 | 0 | 0 | 0 | 0 | 1 | 0 | 8 | 0.82 | 0 | 0 | 0 | 0 |
| video | 67 | 58,176 | 67 | 0 | 3 | 0 | 0 | 1 | 0 | 25 | 0.43 | 0 | 0 | 0 | 0 |

### 〇·a、跨站引用低密度站（29 站，每千字 < 1 链接）

| 子站 | 密度（每千字）| xsite 链接 | 字数 |
|------|-----:|-----:|-----:|
| cloud-native | 0.26 | 10 | 37,792 |
| ai | 0.27 | 9 | 33,714 |
| bigdata | 0.27 | 10 | 36,605 |
| clickhouse | 0.29 | 10 | 34,649 |
| chaos | 0.29 | 9 | 30,975 |
| mysql | 0.31 | 28 | 90,065 |
| frontend | 0.33 | 10 | 30,216 |
| rust | 0.34 | 9 | 26,780 |
| architecture | 0.34 | 12 | 34,788 |
| video | 0.43 | 25 | 58,176 |
| devops | 0.46 | 10 | 21,943 |
| security | 0.50 | 13 | 26,249 |
| postgresql | 0.50 | 28 | 55,610 |
| es | 0.56 | 11 | 19,748 |
| kafka | 0.57 | 59 | 103,245 |
| linux | 0.58 | 29 | 50,107 |
| system-design | 0.58 | 47 | 81,137 |
| redis | 0.61 | 47 | 76,830 |
| filesystem | 0.61 | 49 | 79,852 |
| go | 0.62 | 28 | 45,265 |
| python | 0.62 | 46 | 73,892 |
| observability | 0.63 | 28 | 44,692 |
| game | 0.65 | 11 | 16,809 |
| java | 0.66 | 13 | 19,676 |
| design-pattern | 0.75 | 45 | 59,810 |
| tools | 0.82 | 8 | 9,792 |
| iot | 0.86 | 12 | 13,901 |
| network | 0.89 | 45 | 50,761 |
| cloud | 0.97 | 41 | 42,289 |

**建议**：这些站当前主要靠 index.md 末尾的 📚 相关阅读 段落带跨站链接，子文档间应互相引用。可参考 §8.60 xlink-injector 注入术语映射。

### 〇·b、内容完整度低（13 篇，completeness_score ≤ 3）

| 子站 | 平均分 | 低完整度 / 总数 | 建议 |
|------|------:|------:|------|
| filesystem-html | 3.9 | 13 / 94 | 加代码示例 / 表格 / Vue 组件 |

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
2. **跨站引用密度**：全局 723 处（§8.60 注入 +152），平均 0.55 链接/千字。详见'〇·a 低密度站清单'补强
3. **薄页比例 0.0%**：0 篇字数 < 200，可能为 placeholder 或拆分过度（C3 持续 review）
4. **frontmatter 覆盖率 100.0%**：0 篇缺 FM，1554 篇 FM 缺 date——但 VitePress 已配 `lastUpdated: true`，自动用 git commit 时间，**非真问题**（C1 模板可选择性根治）
5. **过期内容 0 篇**（> 365 天）：需要月度 review 流程（C10）
6. **内部死链 0 处**：可能是 VitePress cleanUrls 导致文件名不一致，建议用 check-links.py depth=3 交叉验证
