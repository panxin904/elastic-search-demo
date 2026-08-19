# 内容质量审计报告 — 2026-08-19

> 自动生成 by `scripts/audit-content.py`（C3 baseline）
> 检测范围: 28 子站 × 1430 .md 文件

## 〇、Summary

| 指标 | 数值 | 健康阈值 | 状态 |
|------|------|----------|------|
| 总文件数 | 1430 | — | — |
| 总字数（中英混合） | 1,160,970 | — | — |
| frontmatter 覆盖率 | 100.0% | ≥ 95% | ✅ |
| 薄页豁免（cheatsheet.md, graph.md, mindmap.md） | 42 | — | 结构预期字数少，不计入薄页 |
| 薄页（< 200 字，扣除豁免） | 71 (5.0%) | ≤ 5% | ✅ |
| 缺 frontmatter | 0 | 0 | ✅ |
| frontmatter 缺 date | 1417 | 0 | ⚠️（VitePress `lastUpdated: true` 兜底）|
| 过期内容（> 365 天） | 0 | ≤ 10% | ✅ |
| 图片总数 | 0 | — | ⚠️ 偏少 |
| 缺 alt 的图片 | 0 | 0 | ✅ |
| 内部死链 | 0 | 0 | ✅ |
| 跨站引用 | 139 | ≥ 100 | ✅ |
| Vue prop 数组缺逗号 | 0 | 0 | ✅ |
| Vue 组件缺失（md 引用无 .vue） | 0 | 0 | ✅ |
| 跨子站重复标题 | 234 | ≤ 20 | ⚠️ |

## 一、各子站统计

| 子站 | 文件 | 字数 | FM | 薄页 | 豁免 | 缺FM | 过期 | 图片 | 死链 | 跨站 | VueBug | 缺组件 |
|------|-----:|-----:|---:|-----:|-----:|-----:|-----:|-----:|-----:|
| ai | 57 | 33,218 | 57 | 0 | 3 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| architecture | 51 | 34,085 | 51 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| bigdata | 51 | 36,007 | 51 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| chaos | 32 | 27,617 | 32 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| clickhouse | 36 | 33,122 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| cloud | 1 | 609 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cloud-native | 55 | 37,166 | 55 | 0 | 3 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| design-pattern | 49 | 55,679 | 49 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| devops | 30 | 17,872 | 30 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| es | 63 | 19,354 | 63 | 3 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| filesystem | 94 | 72,251 | 81 | 7 | 3 | 0 | 0 | 0 | 0 | 9 | 0 | 0 |
| frontend | 65 | 29,378 | 65 | 1 | 2 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| go | 36 | 41,658 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| java | 53 | 16,998 | 53 | 11 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| java-language | 55 | 5,541 | 55 | 49 | 3 | 0 | 0 | 0 | 0 | 4 | 0 | 0 |
| kafka | 73 | 98,005 | 73 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| linux | 71 | 48,647 | 71 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| mysql | 67 | 87,035 | 67 | 0 | 4 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| network | 66 | 48,127 | 66 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| observability | 50 | 42,317 | 50 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| postgresql | 53 | 48,967 | 53 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| python | 60 | 69,021 | 60 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| redis | 59 | 75,279 | 59 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| rust | 35 | 21,774 | 35 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| security | 36 | 21,683 | 36 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 0 | 0 |
| system-design | 52 | 73,595 | 52 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| tools | 13 | 8,284 | 13 | 0 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| video | 67 | 57,681 | 67 | 0 | 3 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |

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

## 七、跨子站重复标题（234 组 — 候选合并/跨站引用）

模板 词已在检测中过滤（在图谱中的位置 / 一句话定义 / 关键 takeaway 等）

- **'️ 路径 1：纯新手（1 周）'** (3 处)
  - `ai/path.md`
  - `cloud-native/path.md`
  - `linux/path.md`
- **'🆚 vs 其他'** (3 处)
  - `ai/gemini.md`
  - `cloud-native/falco.md`
  - `cloud-native/istio.md`
- **'多 GPU'** (3 处)
  - `ai/cuda-gpu.md`
  - `ai/vllm-tgi.md`
  - `video/gpu-cuda.md`
- **'Docker 镜像'** (2 处)
  - `ai/package-managers.md`
  - `cloud-native/image.md`
- **'Node.js'** (5 处)
  - `ai/openai-sdk.md`
  - `ai/openai-sdk.md`
  - `ai/claude-sdk.md`
  - `clickhouse/client.md`
  - `frontend/basic.md`
- **'Python'** (4 处)
  - `ai/claude-sdk.md`
  - `ai/vllm-tgi.md`
  - `observability/otlp.md`
  - `security/a06-vulnerable-component.md`
- **'JSON 输出'** (3 处)
  - `ai/few-shot.md`
  - `es/cat-api.md`
  - `video/mediainfo.md`
- **'AWS Secrets Manager'** (2 处)
  - `ai/api-keys.md`
  - `devops/secrets-management.md`
- **'config.yaml'** (2 处)
  - `ai/cost.md`
  - `bigdata/log-platform.md`
- **'Easy（基础）'** (2 处)
  - `ai/questions.md`
  - `cloud-native/questions.md`
- **'Python 客户端'** (2 处)
  - `ai/vector-db.md`
  - `clickhouse/client.md`
- **'docker-compose.yml'** (10 处)
  - `ai/vllm-tgi.md`
  - `clickhouse/grafana.md`
  - `cloud-native/network.md`
  - `cloud-native/compose.md`
  - `kafka/install.md`
  - ... 等 5 处
- **'命令行启动'** (2 处)
  - `ai/vllm-tgi.md`
  - `redis/sentinel.md`
- **'macOS'** (9 处)
  - `ai/ollama.md`
  - `ai/cursor.md`
  - `cloud-native/helmfile.md`
  - `filesystem/restic.md`
  - `go/hello-world.md`
  - ... 等 4 处
- **'Linux'** (9 处)
  - `ai/ollama.md`
  - `cloud-native/helmfile.md`
  - `filesystem/restic.md`
  - `go/hello-world.md`
  - `network/wifi.md`
  - ... 等 4 处
- **'用 curl'** (2 处)
  - `ai/ollama.md`
  - `filesystem/webdav.md`
- **'Docker'** (3 处)
  - `ai/ollama.md`
  - `java/docker.md`
  - `video/inpainting.md`
- **'为什么需要'** (7 处)
  - `ai/function-calling.md`
  - `ai/structured-output.md`
  - `cloud-native/falco.md`
  - `cloud-native/policy.md`
  - `cloud-native/debug.md`
  - ... 等 2 处
- **'Schema 设计'** (4 处)
  - `ai/function-calling.md`
  - `clickhouse/user-tracking.md`
  - `clickhouse/log-analysis.md`
  - `clickhouse/realtime-warehouse.md`
- **'Hello World'** (2 处)
  - `ai/crewai.md`
  - `rust/overview.md`
- **'分布式限流'** (3 处)
  - `architecture/distributed.md`
  - `redis/distributed-ratelimit.md`
  - `system-design/rate-limiter.md`
- **'双写一致性'** (2 处)
  - `architecture/routing.md`
  - `redis/cache-consistency.md`
- **'application.yml'** (21 处)
  - `architecture/strategy.md`
  - `architecture/config.md`
  - `architecture/discovery.md`
  - `architecture/three-pillars.md`
  - `architecture/otel.md`
  - ... 等 16 处
- **'ShardingSphere 实战'** (2 处)
  - `architecture/strategy.md`
  - `mysql/shardingsphere.md`
- **'三种部署模式'** (2 处)
  - `architecture/multi-region.md`
  - `observability/collector.md`
- **'实战 checklist'** (43 处)
  - `architecture/multi-region.md`
  - `architecture/architecture.md`
  - `architecture/breakdown.md`
  - `architecture/split.md`
  - `architecture/event-storming.md`
  - ... 等 38 处
- **'秒杀系统设计'** (2 处)
  - `architecture/flash-sale.md`
  - `system-design/seckill.md`
- **'Fallback 策略'** (2 处)
  - `architecture/fallback.md`
  - `design-pattern/circuit-breaker.md`
- **'Hystrix（已停止维护）'** (2 处)
  - `architecture/impl.md`
  - `design-pattern/circuit-breaker.md`
- **'熔断器（Circuit Breaker）'** (2 处)
  - `architecture/states.md`
  - `chaos/overview.md`
- ... 及其他 204 组

## 八、关键发现与建议

1. **图片覆盖率极低**：0 张图 / 1430 篇 = 0.0%，纯文字技术文档严重缺乏视觉化（C11 价值高）
2. **跨站引用近零**：仅 139 处，28 站 1429+ 页形成内容孤岛（C2 价值高）
3. **薄页比例 5.0%**：71 篇字数 < 200，可能为 placeholder 或拆分过度（C3 持续 review）
4. **frontmatter 覆盖率 100.0%**：0 篇缺 FM，1417 篇 FM 缺 date——但 VitePress 已配 `lastUpdated: true`，自动用 git commit 时间，**非真问题**（C1 模板可选择性根治）
5. **过期内容 0 篇**（> 365 天）：需要月度 review 流程（C10）
6. **内部死链 0 处**：可能是 VitePress cleanUrls 导致文件名不一致，建议用 check-links.py depth=3 交叉验证
