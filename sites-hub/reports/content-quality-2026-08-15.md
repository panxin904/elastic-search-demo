# 内容质量审计报告 — 2026-08-15

> 自动生成 by `scripts/audit-content.py`（C3 baseline）
> 检测范围: 28 子站 × 1430 .md 文件

## 〇、Summary

| 指标 | 数值 | 健康阈值 | 状态 |
|------|------|----------|------|
| 总文件数 | 1430 | — | — |
| 总字数（中英混合） | 1,156,538 | — | — |
| frontmatter 覆盖率 | 100.0% | ≥ 95% | ✅ |
| 薄页（< 500 字） | 324 (22.7%) | ≤ 5% | ❌ |
| 缺 frontmatter | 0 | 0 | ✅ |
| frontmatter 缺 date | 1417 | 0 | ❌ |
| 过期内容（> 365 天） | 0 | ≤ 10% | ✅ |
| 图片总数 | 9 | — | ⚠️ 偏少 |
| 缺 alt 的图片 | 7 | 0 | ❌ |
| 内部死链 | 0 | 0 | ✅ |
| 跨站引用 | 29 | ≥ 100 | ⚠️ 偏少 |
| 跨子站重复标题 | 244 | ≤ 20 | ⚠️ |

## 一、各子站统计

| 子站 | 文件 | 字数 | FM | 薄页 | 缺FM | 过期 | 图片 | 死链 | 跨站 |
|------|-----:|-----:|---:|-----:|-----:|-----:|-----:|-----:|-----:|
| ai | 57 | 33,139 | 57 | 18 | 0 | 0 | 0 | 0 | 4 |
| architecture | 51 | 34,046 | 51 | 7 | 0 | 0 | 0 | 0 | 5 |
| bigdata | 51 | 35,602 | 51 | 9 | 0 | 0 | 0 | 0 | 5 |
| chaos | 32 | 27,504 | 32 | 7 | 0 | 0 | 0 | 0 | 0 |
| clickhouse | 36 | 33,010 | 36 | 1 | 0 | 0 | 0 | 0 | 0 |
| cloud | 1 | 609 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| cloud-native | 55 | 37,127 | 55 | 4 | 0 | 0 | 0 | 0 | 4 |
| design-pattern | 49 | 55,400 | 49 | 0 | 0 | 0 | 0 | 0 | 0 |
| devops | 30 | 17,709 | 30 | 7 | 0 | 0 | 0 | 0 | 0 |
| es | 63 | 19,136 | 63 | 59 | 0 | 0 | 0 | 0 | 0 |
| filesystem | 94 | 72,091 | 81 | 15 | 0 | 0 | 0 | 0 | 4 |
| frontend | 65 | 29,161 | 65 | 51 | 0 | 0 | 8 | 0 | 0 |
| go | 36 | 41,445 | 36 | 1 | 0 | 0 | 0 | 0 | 0 |
| java | 53 | 16,761 | 53 | 47 | 0 | 0 | 0 | 0 | 0 |
| java-language | 55 | 5,502 | 55 | 54 | 0 | 0 | 0 | 0 | 4 |
| kafka | 73 | 97,787 | 73 | 3 | 0 | 0 | 0 | 0 | 0 |
| linux | 71 | 48,435 | 71 | 5 | 0 | 0 | 0 | 0 | 0 |
| mysql | 67 | 86,826 | 67 | 4 | 0 | 0 | 0 | 0 | 0 |
| network | 66 | 47,949 | 66 | 2 | 0 | 0 | 0 | 0 | 0 |
| observability | 50 | 42,094 | 50 | 4 | 0 | 0 | 0 | 0 | 0 |
| postgresql | 53 | 48,860 | 53 | 0 | 0 | 0 | 0 | 0 | 0 |
| python | 60 | 68,948 | 60 | 3 | 0 | 0 | 0 | 0 | 0 |
| redis | 59 | 75,180 | 59 | 3 | 0 | 0 | 0 | 0 | 0 |
| rust | 35 | 21,553 | 35 | 11 | 0 | 0 | 0 | 0 | 0 |
| security | 36 | 21,554 | 36 | 3 | 0 | 0 | 1 | 0 | 3 |
| system-design | 52 | 73,532 | 52 | 0 | 0 | 0 | 0 | 0 | 0 |
| tools | 13 | 8,064 | 13 | 2 | 0 | 0 | 0 | 0 | 0 |
| video | 67 | 57,514 | 67 | 4 | 0 | 0 | 0 | 0 | 0 |

## 二、薄页清单（324 篇）

- `ai/mindmap.md (80字)`
- `ai/graph.md (190字)`
- `ai/08-finetuning/quantization.md (478字)`
- `ai/01-models/deepseek.md (419字)`
- `ai/01-models/compare.md (399字)`
- `ai/01-models/gpt.md (367字)`
- `ai/01-models/gemini.md (278字)`
- `ai/12-install/cuda-gpu.md (494字)`
- `ai/03-sdks/langchain.md (491字)`
- `ai/03-sdks/gemini-sdk.md (404字)`
- `ai/06-mcp/codex-integration.md (223字)`
- `ai/02-coding-tools/cursor.md (392字)`
- `ai/02-coding-tools/continue-cody.md (404字)`
- `ai/02-coding-tools/aider.md (341字)`
- `ai/02-coding-tools/copilot.md (322字)`
- `ai/04-agents/dify-coze.md (383字)`
- `ai/04-agents/autogen.md (358字)`
- `ai/04-agents/crewai.md (447字)`
- `architecture/mindmap.md (18字)`
- `architecture/graph.md (108字)`
- `architecture/02-thread-pool/virtual.md (495字)`
- `architecture/02-thread-pool/forkjoin.md (399字)`
- `architecture/01-concurrency-theory/happens-before.md (368字)`
- `architecture/01-concurrency-theory/cas.md (384字)`
- `architecture/01-concurrency-theory/volatile.md (425字)`
- `bigdata/mindmap.md (17字)`
- `bigdata/graph.md (93字)`
- `bigdata/03-mapreduce/optimize.md (374字)`
- `bigdata/06-hive/engine.md (481字)`
- `bigdata/11-elt-pipeline/lineage.md (21字)`
- `bigdata/11-elt-pipeline/cdc.md (441字)`
- `bigdata/02-hdfs/replication.md (368字)`
- `bigdata/02-hdfs/commands.md (494字)`
- `bigdata/02-hdfs/ha.md (496字)`
- `chaos/index.md (494字)`
- `chaos/05-resilience-patterns/circuit-breaker.md (419字)`
- `chaos/05-resilience-patterns/retry-backoff.md (397字)`
- `chaos/07-observability-for-chaos/measure-steady-state.md (402字)`
- `chaos/02-chaos-mesh/network-chaos.md (441字)`
- `chaos/03-litmus/probe-check.md (409字)`
- `chaos/03-litmus/chaos-experiment.md (383字)`
- `clickhouse/index.md (482字)`
- `cloud-native/mindmap.md (82字)`
- `cloud-native/graph.md (189字)`
- `cloud-native/03-k8s-workload/deployment.md (421字)`
- `cloud-native/01-docker/intro.md (426字)`
- `devops/01-pipeline/jenkins.md (443字)`
- `devops/01-pipeline/tekton.md (462字)`
- `devops/01-pipeline/github-actions.md (419字)`
- `devops/02-iac/terraform.md (449字)`
- ... 及其他 274 篇

## 五、缺 alt 图片清单（7 张）

- `frontend/12-perf/cwv.md <img>`
- `frontend/12-perf/cwv.md <img>`
- `frontend/12-perf/a11y.md <img>`
- `frontend/12-perf/loading.md <img>`
- `frontend/12-perf/loading.md <img>`
- `frontend/12-perf/loading.md <img>`
- `security/02-auth/session-attack.md <img>`

## 七、跨子站重复标题（244 组 — 候选合并/跨站引用）

模板 词已在检测中过滤（在图谱中的位置 / 一句话定义 / 关键 takeaway 等）

- **'️ 路径 1：纯新手（1 周）'** (3 处)
  - `ai/path.md`
  - `cloud-native/path.md`
  - `linux/path.md`
- **'非交互（CI 用）'** (2 处)
  - `ai/cheatsheet.md`
  - `linux/lynis.md`
- **'Python'** (5 处)
  - `ai/cheatsheet.md`
  - `ai/claude-sdk.md`
  - `ai/vllm-tgi.md`
  - `observability/otlp.md`
  - `security/a06-vulnerable-component.md`
- **'Node.js'** (6 处)
  - `ai/cheatsheet.md`
  - `ai/openai-sdk.md`
  - `ai/openai-sdk.md`
  - `ai/claude-sdk.md`
  - `clickhouse/client.md`
  - ... 等 1 处
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
- **'Docker'** (5 处)
  - `ai/ollama.md`
  - `architecture/cheatsheet.md`
  - `cloud-native/cheatsheet.md`
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
- **'Nacos'** (2 处)
  - `architecture/cheatsheet.md`
  - `java-language/nacos.md`
- **'Kafka'** (5 处)
  - `architecture/cheatsheet.md`
  - `bigdata/cheatsheet.md`
  - `bigdata/questions.md`
  - `bigdata/streaming.md`
  - `bigdata/streaming.md`
- **'Redis'** (3 处)
  - `architecture/cheatsheet.md`
  - `cloud-native/helmfile.md`
  - `java/redis.md`
- **'Nginx'** (3 处)
  - `architecture/cheatsheet.md`
  - `filesystem/webdav.md`
  - `java/nginx.md`
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
- ... 及其他 214 组

## 八、关键发现与建议

1. **图片覆盖率极低**：9 张图 / 1430 篇 = 0.6%，纯文字技术文档严重缺乏视觉化（C11 价值高）
2. **跨站引用近零**：仅 29 处，28 站 1429+ 页形成内容孤岛（C2 价值高）
3. **薄页比例 22.7%**：324 篇字数 < 500，可能为 placeholder 或拆分过度（C3 持续 review）
4. **frontmatter 覆盖率 100.0%**：0 篇缺 FM，1417 篇 FM 缺 date（C1 模板可根治）
5. **过期内容 0 篇**（> 365 天）：需要月度 review 流程（C10）
6. **内部死链 0 处**：可能是 VitePress cleanUrls 导致文件名不一致，建议用 check-links.py depth=3 交叉验证
