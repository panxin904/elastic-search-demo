# §8.65 低完整度页补全建议

> 日期：2026-08-25 · 基于 audit-content.py §8.55 评分算法
> 总低完整度页：605 篇（score ≤ 3 / 7）

## 一、缺维度统计

| 维度 | 缺此维度的页数 | 占比 |
| --- | ---: | ---: |
| frontmatter | 13 | 2.1% |
| 代码块 | 64 | 10.6% |
| 表格 | 398 | 65.8% |
| Vue 组件 | 587 | 97.0% |
| Mermaid 图 | 605 | 100.0% |
| 内链 | 341 | 56.4% |
| 字数 ≥ 500 | 553 | 91.4% |

## 二、子站分布（按低完整度数量排序）

| 子站 | 平均分 | 低完整度 / 总数 |
| --- | ---: | ---: |
| filesystem | 3.4 | 50 / 91 |
| system-design | 2.6 | 46 / 52 |
| postgresql | 2.9 | 45 / 53 |
| kafka | 3.5 | 38 / 70 |
| python | 3.4 | 37 / 57 |
| game | 3.1 | 34 / 37 |
| rust | 2.4 | 34 / 35 |
| security | 3.0 | 33 / 36 |
| iot | 3.1 | 30 / 33 |
| devops | 2.6 | 28 / 30 |
| chaos | 2.7 | 27 / 32 |
| design-pattern | 3.3 | 27 / 49 |
| android | 3.1 | 25 / 27 |
| go | 3.1 | 23 / 36 |
| mysql | 4.0 | 23 / 63 |
| observability | 3.7 | 16 / 50 |
| network | 3.9 | 14 / 63 |
| clickhouse | 3.8 | 13 / 36 |
| tools | 2.0 | 13 / 13 |
| java | 3.9 | 9 / 53 |
| linux | 4.0 | 9 / 68 |
| frontend | 4.2 | 6 / 63 |
| cloud-native | 4.0 | 5 / 52 |
| redis | 4.6 | 5 / 56 |
| springcloud | 4.3 | 5 / 32 |
| bigdata | 4.1 | 4 / 48 |
| ai | 4.0 | 3 / 54 |
| architecture | 4.2 | 2 / 48 |
| video | 4.2 | 1 / 64 |

## 三、按缺维度分组的补全清单

### 缺frontmatter（13 篇）

补全方法见 `enrich-templates.md`。

| 子站 | 文件 | 当前 score | 当前字数 |
| --- | --- | ---: | ---: |
| filesystem | `01-basics/README.md` | 2 | 233 |
| filesystem | `02-disk-fs/README.md` | 3 | 170 |
| filesystem | `03-distributed/README.md` | 2 | 265 |
| filesystem | `04-object/README.md` | 2 | 226 |
| filesystem | `05-network/README.md` | 2 | 239 |
| filesystem | `06-cloud-native/README.md` | 2 | 209 |
| filesystem | `07-container/README.md` | 3 | 247 |
| filesystem | `08-tools/README.md` | 2 | 285 |
| filesystem | `09-perf/README.md` | 3 | 243 |
| filesystem | `10-security/README.md` | 3 | 206 |
| filesystem | `11-backup/README.md` | 3 | 184 |
| filesystem | `12-cases/README.md` | 2 | 278 |
| filesystem | `13-interview/README.md` | 3 | 184 |

### 缺代码块（64 篇）

补全方法见 `enrich-templates.md`。

| 子站 | 文件 | 当前 score | 当前字数 |
| --- | --- | ---: | ---: |
| android | `01-app/README.md` | 3 | 213 |
| android | `02-ui/README.md` | 3 | 228 |
| android | `03-system/README.md` | 3 | 208 |
| android | `04-cross/README.md` | 3 | 213 |
| android | `05-toolchain/README.md` | 3 | 207 |
| android | `06-perf/README.md` | 3 | 208 |
| android | `index.md` | 3 | 628 |
| android | `questions.md` | 3 | 811 |
| bigdata | `11-elt-pipeline/lineage.md` | 3 | 387 |
| chaos | `01-foundations/history.md` | 2 | 656 |
| chaos | `01-foundations/overview.md` | 3 | 1834 |
| chaos | `04-platform-compare/decision-tree.md` | 2 | 604 |
| chaos | `04-platform-compare/mesh-vs-litmus.md` | 3 | 651 |
| chaos | `04-platform-compare/open-vs-commercial.md` | 3 | 714 |
| chaos | `04-platform-compare/overview.md` | 3 | 1988 |
| chaos | `05-resilience-patterns/multi-region-dr.md` | 3 | 675 |
| chaos | `06-game-day/exercise-design.md` | 3 | 657 |
| chaos | `06-game-day/roles.md` | 3 | 647 |
| clickhouse | `01-basics/history.md` | 3 | 809 |
| clickhouse | `case-study.md` | 3 | 2888 |
| filesystem | `01-basics/README.md` | 2 | 233 |
| filesystem | `03-distributed/README.md` | 2 | 265 |
| filesystem | `04-object/README.md` | 2 | 226 |
| filesystem | `05-network/README.md` | 2 | 239 |
| filesystem | `06-cloud-native/README.md` | 2 | 209 |
| filesystem | `08-tools/README.md` | 2 | 285 |
| filesystem | `12-cases/README.md` | 2 | 278 |
| filesystem | `13-interview/comparison.md` | 3 | 925 |
| filesystem | `index.md` | 3 | 947 |
| filesystem | `path.md` | 3 | 787 |
| ... | 还有 34 篇 | | |

### 缺表格（398 篇）

补全方法见 `enrich-templates.md`。

| 子站 | 文件 | 当前 score | 当前字数 |
| --- | --- | ---: | ---: |
| ai | `02-coding-tools/commands.md` | 3 | 74 |
| ai | `03-sdks/claude-sdk.md` | 3 | 66 |
| ai | `12-install/docker.md` | 3 | 99 |
| android | `01-app/coroutine.md` | 3 | 182 |
| android | `01-app/jetpack.md` | 3 | 177 |
| android | `01-app/language.md` | 3 | 189 |
| android | `02-ui/compose.md` | 3 | 186 |
| android | `02-ui/resource.md` | 3 | 187 |
| android | `02-ui/view-system.md` | 3 | 169 |
| android | `03-system/ipc.md` | 3 | 196 |
| android | `03-system/runtime.md` | 3 | 175 |
| android | `03-system/services.md` | 3 | 181 |
| android | `03-system/startup.md` | 3 | 193 |
| android | `04-cross/decision.md` | 3 | 169 |
| android | `04-cross/frameworks.md` | 3 | 172 |
| android | `05-toolchain/gradle.md` | 3 | 179 |
| android | `05-toolchain/ide.md` | 3 | 185 |
| android | `05-toolchain/publish.md` | 3 | 183 |
| android | `06-perf/performance.md` | 3 | 186 |
| android | `06-perf/security.md` | 3 | 180 |
| android | `index.md` | 3 | 628 |
| architecture | `04-rate-limit/distributed.md` | 3 | 189 |
| architecture | `06-microservice/split.md` | 3 | 449 |
| bigdata | `02-hdfs/commands.md` | 3 | 41 |
| bigdata | `14-interview-practice/cases.md` | 3 | 443 |
| bigdata | `14-interview-practice/questions.md` | 3 | 206 |
| chaos | `01-foundations/history.md` | 2 | 656 |
| chaos | `01-foundations/steady-state.md` | 2 | 462 |
| chaos | `02-chaos-mesh/network-chaos.md` | 2 | 221 |
| chaos | `02-chaos-mesh/pod-chaos.md` | 2 | 318 |
| ... | 还有 368 篇 | | |

### 缺Vue 组件（587 篇）

补全方法见 `enrich-templates.md`。

| 子站 | 文件 | 当前 score | 当前字数 |
| --- | --- | ---: | ---: |
| ai | `02-coding-tools/commands.md` | 3 | 74 |
| ai | `03-sdks/claude-sdk.md` | 3 | 66 |
| ai | `12-install/docker.md` | 3 | 99 |
| android | `01-app/README.md` | 3 | 213 |
| android | `01-app/coroutine.md` | 3 | 182 |
| android | `01-app/jetpack.md` | 3 | 177 |
| android | `01-app/language.md` | 3 | 189 |
| android | `02-ui/README.md` | 3 | 228 |
| android | `02-ui/compose.md` | 3 | 186 |
| android | `02-ui/resource.md` | 3 | 187 |
| android | `02-ui/view-system.md` | 3 | 169 |
| android | `03-system/README.md` | 3 | 208 |
| android | `03-system/ipc.md` | 3 | 196 |
| android | `03-system/runtime.md` | 3 | 175 |
| android | `03-system/services.md` | 3 | 181 |
| android | `03-system/startup.md` | 3 | 193 |
| android | `04-cross/README.md` | 3 | 213 |
| android | `04-cross/decision.md` | 3 | 169 |
| android | `04-cross/frameworks.md` | 3 | 172 |
| android | `05-toolchain/README.md` | 3 | 207 |
| android | `05-toolchain/gradle.md` | 3 | 179 |
| android | `05-toolchain/ide.md` | 3 | 185 |
| android | `05-toolchain/publish.md` | 3 | 183 |
| android | `06-perf/README.md` | 3 | 208 |
| android | `06-perf/performance.md` | 3 | 186 |
| android | `06-perf/security.md` | 3 | 180 |
| android | `questions.md` | 3 | 811 |
| architecture | `04-rate-limit/distributed.md` | 3 | 189 |
| architecture | `06-microservice/split.md` | 3 | 449 |
| bigdata | `02-hdfs/commands.md` | 3 | 41 |
| ... | 还有 557 篇 | | |

### 缺Mermaid 图（605 篇）

补全方法见 `enrich-templates.md`。

| 子站 | 文件 | 当前 score | 当前字数 |
| --- | --- | ---: | ---: |
| ai | `02-coding-tools/commands.md` | 3 | 74 |
| ai | `03-sdks/claude-sdk.md` | 3 | 66 |
| ai | `12-install/docker.md` | 3 | 99 |
| android | `01-app/README.md` | 3 | 213 |
| android | `01-app/coroutine.md` | 3 | 182 |
| android | `01-app/jetpack.md` | 3 | 177 |
| android | `01-app/language.md` | 3 | 189 |
| android | `02-ui/README.md` | 3 | 228 |
| android | `02-ui/compose.md` | 3 | 186 |
| android | `02-ui/resource.md` | 3 | 187 |
| android | `02-ui/view-system.md` | 3 | 169 |
| android | `03-system/README.md` | 3 | 208 |
| android | `03-system/ipc.md` | 3 | 196 |
| android | `03-system/runtime.md` | 3 | 175 |
| android | `03-system/services.md` | 3 | 181 |
| android | `03-system/startup.md` | 3 | 193 |
| android | `04-cross/README.md` | 3 | 213 |
| android | `04-cross/decision.md` | 3 | 169 |
| android | `04-cross/frameworks.md` | 3 | 172 |
| android | `05-toolchain/README.md` | 3 | 207 |
| android | `05-toolchain/gradle.md` | 3 | 179 |
| android | `05-toolchain/ide.md` | 3 | 185 |
| android | `05-toolchain/publish.md` | 3 | 183 |
| android | `06-perf/README.md` | 3 | 208 |
| android | `06-perf/performance.md` | 3 | 186 |
| android | `06-perf/security.md` | 3 | 180 |
| android | `index.md` | 3 | 628 |
| android | `questions.md` | 3 | 811 |
| architecture | `04-rate-limit/distributed.md` | 3 | 189 |
| architecture | `06-microservice/split.md` | 3 | 449 |
| ... | 还有 575 篇 | | |

### 缺内链（341 篇）

补全方法见 `enrich-templates.md`。

| 子站 | 文件 | 当前 score | 当前字数 |
| --- | --- | ---: | ---: |
| android | `index.md` | 3 | 628 |
| android | `questions.md` | 3 | 811 |
| chaos | `01-foundations/blast-radius.md` | 3 | 468 |
| chaos | `01-foundations/history.md` | 2 | 656 |
| chaos | `01-foundations/overview.md` | 3 | 1834 |
| chaos | `01-foundations/steady-state.md` | 2 | 462 |
| chaos | `02-chaos-mesh/architecture.md` | 3 | 435 |
| chaos | `02-chaos-mesh/network-chaos.md` | 2 | 221 |
| chaos | `02-chaos-mesh/pod-chaos.md` | 2 | 318 |
| chaos | `02-chaos-mesh/workflow.md` | 2 | 425 |
| chaos | `03-litmus/chaos-experiment.md` | 2 | 167 |
| chaos | `03-litmus/probe-check.md` | 2 | 227 |
| chaos | `03-litmus/sdk.md` | 2 | 356 |
| chaos | `04-platform-compare/decision-tree.md` | 2 | 604 |
| chaos | `04-platform-compare/mesh-vs-litmus.md` | 3 | 651 |
| chaos | `04-platform-compare/open-vs-commercial.md` | 3 | 714 |
| chaos | `04-platform-compare/overview.md` | 3 | 1988 |
| chaos | `05-resilience-patterns/bulkhead.md` | 2 | 437 |
| chaos | `05-resilience-patterns/circuit-breaker.md` | 2 | 241 |
| chaos | `05-resilience-patterns/multi-region-dr.md` | 3 | 675 |
| chaos | `05-resilience-patterns/rate-limit-degrade.md` | 3 | 523 |
| chaos | `05-resilience-patterns/retry-backoff.md` | 2 | 223 |
| chaos | `06-game-day/exercise-design.md` | 3 | 657 |
| chaos | `06-game-day/retro.md` | 2 | 195 |
| chaos | `06-game-day/roles.md` | 3 | 647 |
| chaos | `07-observability-for-chaos/case-study.md` | 3 | 632 |
| chaos | `07-observability-for-chaos/measure-steady-state.md` | 2 | 221 |
| chaos | `07-observability-for-chaos/overview.md` | 3 | 1469 |
| chaos | `07-observability-for-chaos/slo-feedback-loop.md` | 2 | 463 |
| clickhouse | `02-sql/overview.md` | 3 | 346 |
| ... | 还有 311 篇 | | |

### 缺字数 ≥ 500（553 篇）

补全方法见 `enrich-templates.md`。

| 子站 | 文件 | 当前 score | 当前字数 |
| --- | --- | ---: | ---: |
| ai | `02-coding-tools/commands.md` | 3 | 74 |
| ai | `03-sdks/claude-sdk.md` | 3 | 66 |
| ai | `12-install/docker.md` | 3 | 99 |
| android | `01-app/README.md` | 3 | 213 |
| android | `01-app/coroutine.md` | 3 | 182 |
| android | `01-app/jetpack.md` | 3 | 177 |
| android | `01-app/language.md` | 3 | 189 |
| android | `02-ui/README.md` | 3 | 228 |
| android | `02-ui/compose.md` | 3 | 186 |
| android | `02-ui/resource.md` | 3 | 187 |
| android | `02-ui/view-system.md` | 3 | 169 |
| android | `03-system/README.md` | 3 | 208 |
| android | `03-system/ipc.md` | 3 | 196 |
| android | `03-system/runtime.md` | 3 | 175 |
| android | `03-system/services.md` | 3 | 181 |
| android | `03-system/startup.md` | 3 | 193 |
| android | `04-cross/README.md` | 3 | 213 |
| android | `04-cross/decision.md` | 3 | 169 |
| android | `04-cross/frameworks.md` | 3 | 172 |
| android | `05-toolchain/README.md` | 3 | 207 |
| android | `05-toolchain/gradle.md` | 3 | 179 |
| android | `05-toolchain/ide.md` | 3 | 185 |
| android | `05-toolchain/publish.md` | 3 | 183 |
| android | `06-perf/README.md` | 3 | 208 |
| android | `06-perf/performance.md` | 3 | 186 |
| android | `06-perf/security.md` | 3 | 180 |
| architecture | `04-rate-limit/distributed.md` | 3 | 189 |
| architecture | `06-microservice/split.md` | 3 | 449 |
| bigdata | `02-hdfs/commands.md` | 3 | 41 |
| bigdata | `11-elt-pipeline/lineage.md` | 3 | 387 |
| ... | 还有 523 篇 | | |

## 四、重点子站详情（每个文件 + 缺什么）

### filesystem（50 / 91）

- `06-cloud-native/README.md` · score=2 · 209字 · 缺: frontmatter, 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-object/README.md` · score=2 · 226字 · 缺: frontmatter, 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-basics/README.md` · score=2 · 233字 · 缺: frontmatter, 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-distributed/README.md` · score=2 · 265字 · 缺: frontmatter, 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-network/README.md` · score=2 · 239字 · 缺: frontmatter, 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-tools/README.md` · score=2 · 285字 · 缺: frontmatter, 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `12-cases/README.md` · score=2 · 278字 · 缺: frontmatter, 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `path.md` · score=3 · 787字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图
- `index.md` · score=3 · 947字 · 缺: 代码块, 表格, Mermaid 图, 内链
- `06-cloud-native/dynamic.md` · score=3 · 474字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-cloud-native/openebs.md` · score=3 · 335字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-cloud-native/rook.md` · score=3 · 383字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-security/xattr.md` · score=3 · 293字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-security/acl.md` · score=3 · 446字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-security/README.md` · score=3 · 206字 · 缺: frontmatter, Vue 组件, Mermaid 图, 字数 ≥ 500
- `10-security/auditd.md` · score=3 · 306字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/vfs.md` · score=3 · 328字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/mount.md` · score=3 · 398字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/path-resolution.md` · score=3 · 466字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/page-cache.md` · score=3 · 463字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/inode-dentry.md` · score=3 · 462字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/file-descriptor.md` · score=3 · 276字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-distributed/cephfs.md` · score=3 · 473字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-network/rsync.md` · score=3 · 432字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `11-backup/restic.md` · score=3 · 402字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `11-backup/borg.md` · score=3 · 431字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `11-backup/snapshot.md` · score=3 · 461字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `11-backup/README.md` · score=3 · 184字 · 缺: frontmatter, Vue 组件, Mermaid 图, 字数 ≥ 500
- `11-backup/3-2-1.md` · score=3 · 431字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `08-tools/fuse.md` · score=3 · 472字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `08-tools/du-df.md` · score=3 · 351字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `08-tools/debugfs.md` · score=3 · 385字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `08-tools/find-fd.md` · score=3 · 366字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `08-tools/strace.md` · score=3 · 445字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `08-tools/lsof.md` · score=3 · 371字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `07-container/buildkit.md` · score=3 · 495字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `07-container/README.md` · score=3 · 247字 · 缺: frontmatter, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-disk-fs/compare.md` · score=3 · 484字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-disk-fs/README.md` · score=3 · 170字 · 缺: frontmatter, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-disk-fs/btrfs.md` · score=3 · 479字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-disk-fs/ext4.md` · score=3 · 373字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-disk-fs/xfs.md` · score=3 · 493字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `13-interview/comparison.md` · score=3 · 925字 · 缺: 代码块, Vue 组件, Mermaid 图, 内链
- `13-interview/README.md` · score=3 · 184字 · 缺: frontmatter, Vue 组件, Mermaid 图, 字数 ≥ 500
- `09-perf/io-scheduler.md` · score=3 · 493字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `09-perf/readahead.md` · score=3 · 361字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `09-perf/README.md` · score=3 · 243字 · 缺: frontmatter, Vue 组件, Mermaid 图, 字数 ≥ 500
- `09-perf/page-cache-tune.md` · score=3 · 455字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `12-cases/snowflake.md` · score=3 · 473字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `12-cases/netflix-s3.md` · score=3 · 476字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500

### system-design（46 / 52）

- `06-cache/cache-pattern.md` · score=2 · 170字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-cache/multi-level.md` · score=2 · 202字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-cache/hotspot.md` · score=2 · 182字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-cache/three-problems.md` · score=2 · 201字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-cache/consistency.md` · score=2 · 220字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `08-availability/cluster.md` · score=2 · 223字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `08-availability/multi-idc.md` · score=2 · 238字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `08-availability/disaster-recovery.md` · score=2 · 249字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `07-messaging/not-lost.md` · score=2 · 226字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `07-messaging/backlog.md` · score=2 · 187字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `07-messaging/order.md` · score=2 · 210字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-transaction/saga.md` · score=2 · 166字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-transaction/3pc.md` · score=2 · 183字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-transaction/2pc.md` · score=2 · 156字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-patterns/distributed-trace.md` · score=2 · 224字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-patterns/circuit-breaker.md` · score=2 · 157字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-cases/ranking.md` · score=2 · 224字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-cases/seckill.md` · score=2 · 187字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-cases/search-suggest.md` · score=2 · 189字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-cases/grab-redpacket.md` · score=2 · 289字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-cases/nearby.md` · score=2 · 187字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-cases/feed-stream.md` · score=2 · 278字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-cases/notification.md` · score=2 · 236字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-coordination/leader-election.md` · score=2 · 155字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-coordination/raft.md` · score=2 · 174字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-coordination/zab.md` · score=2 · 185字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-coordination/paxos.md` · score=2 · 192字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-storage/consistent-hash.md` · score=3 · 468字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-storage/sharding.md` · score=3 · 234字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-storage/replica.md` · score=3 · 254字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-storage/quorum.md` · score=3 · 219字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `09-id/snowflake.md` · score=3 · 227字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `09-id/uuid-vs-snowflake.md` · score=3 · 289字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `09-id/leaf.md` · score=3 · 239字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-theory/pacelc.md` · score=3 · 365字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `08-availability/master-slave.md` · score=3 · 209字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `07-messaging/idempotent.md` · score=3 · 720字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `04-transaction/tcc.md` · score=3 · 200字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-transaction/transactional-message.md` · score=3 · 291字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-transaction/local-message-table.md` · score=3 · 258字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-patterns/rpc.md` · score=3 · 227字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-patterns/config-center.md` · score=3 · 269字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-patterns/service-discovery.md` · score=3 · 265字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-patterns/api-gateway.md` · score=3 · 253字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-patterns/rate-limiter.md` · score=3 · 243字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-coordination/distributed-lock.md` · score=3 · 241字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500

### postgresql（45 / 53）

- `05-transaction/deadlock.md` · score=2 · 240字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `08-replication/hot-standby.md` · score=2 · 138字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/config.md` · score=2 · 318字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-extensions/citus.md` · score=2 · 189字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-tables-and-indexes/table.md` · score=2 · 208字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-tables-and-indexes/btree.md` · score=2 · 352字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `07-operations/stats.md` · score=2 · 120字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `09-connection/jdbc.md` · score=2 · 188字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `09-connection/psycopg.md` · score=2 · 170字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `09-connection/libpq.md` · score=2 · 192字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-query/explain.md` · score=2 · 182字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-query/fulltext-search.md` · score=2 · 181字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-query/recursive.md` · score=2 · 189字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-transaction/lock.md` · score=3 · 484字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-transaction/mvcc.md` · score=3 · 250字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-advanced/view.md` · score=3 · 230字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-advanced/upsert.md` · score=3 · 237字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-advanced/trigger.md` · score=3 · 258字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-advanced/function.md` · score=3 · 252字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-advanced/generated.md` · score=3 · 189字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `08-replication/patroni.md` · score=3 · 444字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `08-replication/logical.md` · score=3 · 228字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/architecture.md` · score=3 · 337字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/overview.md` · score=3 · 282字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-extensions/pgvector.md` · score=3 · 386字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-extensions/postgis.md` · score=3 · 214字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-extensions/timescaledb.md` · score=3 · 246字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-extensions/pg_trgm.md` · score=3 · 216字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-tables-and-indexes/gist.md` · score=3 · 234字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-tables-and-indexes/spgist.md` · score=3 · 188字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-tables-and-indexes/gin.md` · score=3 · 336字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-tables-and-indexes/partition.md` · score=3 · 415字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-tables-and-indexes/brin.md` · score=3 · 305字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `07-operations/backup.md` · score=3 · 250字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `07-operations/upgrade.md` · score=3 · 270字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `07-operations/slow-query.md` · score=3 · 425字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-data-types/jsonb.md` · score=3 · 318字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-data-types/array.md` · score=3 · 432字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-data-types/custom.md` · score=3 · 329字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-data-types/built-in.md` · score=3 · 479字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-data-types/range.md` · score=3 · 465字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `09-connection/pgbouncer.md` · score=3 · 373字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-query/cte.md` · score=3 · 286字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-query/window.md` · score=3 · 342字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-query/planner.md` · score=3 · 369字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500

### kafka（38 / 70）

- `10-interview/message-loss.md` · score=3 · 470字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `10-interview/advanced.md` · score=3 · 302字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `10-interview/election.md` · score=3 · 294字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-consumer/multi-thread.md` · score=3 · 305字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-consumer/rebalance.md` · score=3 · 383字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-consumer/offset.md` · score=3 · 404字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-consumer/principle.md` · score=3 · 247字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-basics/install.md` · score=3 · 207字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-basics/topic-partition.md` · score=3 · 230字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-enterprise/cluster.md` · score=3 · 285字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-enterprise/dead-letter.md` · score=3 · 345字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-enterprise/streams.md` · score=3 · 309字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-enterprise/connect.md` · score=3 · 245字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-enterprise/backlog.md` · score=3 · 491字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-enterprise/monitoring.md` · score=3 · 346字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-architecture/overview.md` · score=3 · 204字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-architecture/leader-election.md` · score=3 · 248字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-architecture/log-storage.md` · score=3 · 246字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-architecture/controller.md` · score=3 · 213字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-producer/principle.md` · score=3 · 268字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `09-ops/benchmark.md` · score=3 · 300字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `09-ops/capacity.md` · score=3 · 303字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `09-ops/metrics.md` · score=3 · 293字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `09-ops/disaster-recovery.md` · score=3 · 447字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-jdk/consumer-api.md` · score=3 · 190字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-jdk/admin-client.md` · score=3 · 261字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-jdk/partitioner.md` · score=3 · 312字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-jdk/exception.md` · score=3 · 222字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-jdk/producer-api.md` · score=3 · 261字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-cli/consumer-group.md` · score=3 · 322字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-spring/spring-boot.md` · score=3 · 270字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-spring/listener.md` · score=3 · 247字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-spring/intro.md` · score=3 · 194字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-spring/kafka-template.md` · score=3 · 221字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-spring/transaction.md` · score=3 · 311字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-persistence/rdb.md` · score=3 · 304字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-persistence/recovery.md` · score=3 · 252字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-persistence/aof.md` · score=3 · 308字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500

### python（37 / 57）

- `08-algorithms/tree-graph.md` · score=3 · 279字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-algorithms/builtin.md` · score=3 · 221字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-algorithms/dp.md` · score=3 · 304字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-data/cleaning.md` · score=3 · 238字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-data/analysis.md` · score=3 · 229字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-data/matplotlib.md` · score=3 · 191字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-data/pandas.md` · score=3 · 198字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-data/numpy.md` · score=3 · 195字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-concurrency/threading.md` · score=3 · 205字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-concurrency/patterns.md` · score=3 · 224字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-concurrency/sync-primitives.md` · score=3 · 243字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-concurrency/asyncio.md` · score=3 · 214字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-basics/install.md` · score=3 · 223字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-scraping/basics.md` · score=3 · 276字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-scraping/scrapy.md` · score=3 · 208字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-scraping/requests-bs4.md` · score=3 · 189字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-scraping/anti-crawl.md` · score=3 · 288字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-ai-ml/huggingface.md` · score=3 · 244字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-ai-ml/cv.md` · score=3 · 204字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-ai-ml/nlp.md` · score=3 · 217字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-ai-ml/llm-apps.md` · score=3 · 238字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-ai-ml/ml-basics.md` · score=3 · 269字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-libraries/sqlalchemy.md` · score=3 · 204字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-libraries/pytest.md` · score=3 · 232字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-libraries/stdlib.md` · score=3 · 200字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-libraries/requests.md` · score=3 · 202字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-libraries/pandas.md` · score=3 · 201字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `09-enterprise/structure.md` · score=3 · 212字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `09-enterprise/performance.md` · score=3 · 290字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `09-enterprise/logging.md` · score=3 · 228字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `09-enterprise/docker.md` · score=3 · 234字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `09-enterprise/fastapi.md` · score=3 · 187字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `09-enterprise/security.md` · score=3 · 266字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-principles/object-model.md` · score=3 · 249字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-principles/profiling.md` · score=3 · 316字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-principles/memory.md` · score=3 · 291字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-principles/gc.md` · score=3 · 280字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500

### game（34 / 37）

- `index.md` · score=3 · 687字 · 缺: 代码块, 表格, Mermaid 图, 内链
- `02-render/pipeline.md` · score=3 · 184字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-render/README.md` · score=3 · 208字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-render/shader.md` · score=3 · 198字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-render/postprocess.md` · score=3 · 190字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-render/lighting.md` · score=3 · 180字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-physics/softbody.md` · score=3 · 170字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-physics/README.md` · score=3 · 216字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-physics/collision.md` · score=3 · 176字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-physics/rigidbody.md` · score=3 · 201字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-toolchain/vcs.md` · score=3 · 177字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-toolchain/assets.md` · score=3 · 200字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-toolchain/README.md` · score=3 · 212字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-toolchain/build.md` · score=3 · 194字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-engine/commercial.md` · score=3 · 183字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-engine/README.md` · score=3 · 219字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-engine/custom.md` · score=3 · 199字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-engine/decision.md` · score=3 · 182字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-audio/engine.md` · score=3 · 172字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-audio/mix.md` · score=3 · 174字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-audio/README.md` · score=3 · 201字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-audio/spatial.md` · score=3 · 202字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-network/anticheat.md` · score=3 · 173字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-network/README.md` · score=3 · 227字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-network/sync.md` · score=3 · 183字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-network/arch.md` · score=3 · 165字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-network/consistency.md` · score=3 · 188字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-ai/ml.md` · score=3 · 207字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-ai/pathfinding.md` · score=3 · 151字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-ai/README.md` · score=3 · 204字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-ai/decision.md` · score=3 · 202字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-ship/launch.md` · score=3 · 186字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-ship/README.md` · score=3 · 217字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-ship/perf.md` · score=3 · 182字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500

### rust（34 / 35）

- `02-types-traits/overview.md` · score=2 · 217字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-types-traits/generics.md` · score=2 · 170字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-types-traits/trait.md` · score=2 · 179字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-types-traits/trait-objects.md` · score=2 · 172字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-types-traits/enum-and-pattern.md` · score=2 · 165字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-advanced/smart-pointer.md` · score=2 · 184字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-advanced/error-handling.md` · score=2 · 154字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-advanced/closure-and-iterator.md` · score=2 · 158字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-concurrency/async-await.md` · score=2 · 147字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-concurrency/overview.md` · score=2 · 200字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-concurrency/tokio.md` · score=2 · 146字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-concurrency/channels.md` · score=2 · 171字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-systems/overview.md` · score=2 · 212字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-systems/wasm.md` · score=2 · 155字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-systems/unsafe.md` · score=2 · 157字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-systems/ffi.md` · score=2 · 160字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-systems/embedded.md` · score=2 · 158字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-systems/performance.md` · score=2 · 174字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/syntax-fundamentals.md` · score=2 · 161字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/lifetimes.md` · score=2 · 325字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/ownership.md` · score=2 · 185字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/borrowing.md` · score=2 · 193字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-ecosystem/tooling.md` · score=2 · 144字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-ecosystem/std-lib.md` · score=2 · 152字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-types-traits/advanced-types.md` · score=3 · 230字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-advanced/macro.md` · score=3 · 266字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-advanced/async-ecosystem.md` · score=3 · 264字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-advanced/case-study.md` · score=3 · 636字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `04-concurrency/threads.md` · score=3 · 198字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/hello-world.md` · score=3 · 188字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/overview.md` · score=3 · 260字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-ecosystem/overview.md` · score=3 · 350字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-ecosystem/crates-io.md` · score=3 · 404字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-ecosystem/cargo.md` · score=3 · 131字 · 缺: 表格, Mermaid 图, 内链, 字数 ≥ 500

### security（33 / 36）

- `06-zero-trust/spiffe.md` · score=2 · 173字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-web-top10/a10-ssrf.md` · score=2 · 260字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-network/mtls.md` · score=2 · 182字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-auth/overview.md` · score=3 · 411字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-auth/session-attack.md` · score=3 · 209字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-auth/jwt.md` · score=3 · 294字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-auth/oidc.md` · score=3 · 289字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-auth/mfa.md` · score=3 · 297字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-auth/oauth2.md` · score=3 · 288字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-zero-trust/implementation.md` · score=3 · 291字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-zero-trust/overview.md` · score=3 · 372字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-web-top10/a06-vulnerable-component.md` · score=3 · 316字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-web-top10/a03-injection.md` · score=3 · 302字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-web-top10/a05-misconfig.md` · score=3 · 342字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-web-top10/a07-auth-failure.md` · score=3 · 330字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-web-top10/a08-software-data-integrity.md` · score=3 · 340字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-web-top10/a01-broken-access.md` · score=3 · 422字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-web-top10/a09-logging-failure.md` · score=3 · 362字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-web-top10/a02-crypto-failure.md` · score=3 · 472字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-web-top10/a04-insecure-design.md` · score=3 · 391字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-crypto/overview.md` · score=3 · 403字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-crypto/hash.md` · score=3 · 346字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-crypto/signature.md` · score=3 · 279字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-crypto/tls-deep-dive.md` · score=3 · 250字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-crypto/asymmetric.md` · score=3 · 273字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-crypto/symmetric.md` · score=3 · 311字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-container/overview.md` · score=3 · 312字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-container/supply-chain.md` · score=3 · 256字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-container/image-scan.md` · score=3 · 255字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-container/runtime-security.md` · score=3 · 251字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-network/tls-pki.md` · score=3 · 413字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-network/hsts-csp.md` · score=3 · 393字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-network/cors.md` · score=3 · 263字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500

### iot（30 / 33）

- `path.md` · score=3 · 658字 · 缺: 代码块, Vue 组件, Mermaid 图, 内链
- `index.md` · score=3 · 730字 · 缺: 代码块, 表格, Mermaid 图, 内链
- `03-edge/k8s-edge.md` · score=3 · 186字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-edge/ai-edge.md` · score=3 · 190字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-edge/README.md` · score=3 · 208字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-edge/offline.md` · score=3 · 195字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-edge/framework.md` · score=3 · 179字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-device/mcu.md` · score=3 · 145字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-device/rtos.md` · score=3 · 189字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-device/README.md` · score=3 · 222字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-device/sensor.md` · score=3 · 170字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-device/gateway.md` · score=3 · 165字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-protocol/modbus.md` · score=3 · 174字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-protocol/lpwan.md` · score=3 · 194字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-protocol/coap.md` · score=3 · 176字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-protocol/README.md` · score=3 · 218字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-protocol/mqtt.md` · score=3 · 199字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-timeseries/integration.md` · score=3 · 183字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-timeseries/schema.md` · score=3 · 199字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-timeseries/processing.md` · score=3 · 178字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-timeseries/database.md` · score=3 · 152字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-platform/iiot.md` · score=3 · 188字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-platform/README.md` · score=3 · 215字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-platform/self-hosted.md` · score=3 · 179字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-platform/public-cloud.md` · score=3 · 181字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-platform/smart-home.md` · score=3 · 158字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-management/ota.md` · score=3 · 195字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-management/shadow.md` · score=3 · 201字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-management/README.md` · score=3 · 226字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-management/security.md` · score=3 · 193字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500

### devops（28 / 30）

- `06-best-practices/oidc-federation.md` · score=2 · 198字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-pipeline/jenkins.md` · score=2 · 189字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-pipeline/best-practices.md` · score=2 · 169字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-pipeline/gitlab-ci.md` · score=2 · 164字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-pipeline/github-actions.md` · score=2 · 159字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-iac/terraform.md` · score=2 · 189字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-release/rollback.md` · score=2 · 187字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-release/canary.md` · score=2 · 225字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-release/blue-green.md` · score=2 · 187字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-cicd-observability/dora-metrics.md` · score=2 · 191字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-cicd-observability/flaky-test.md` · score=2 · 168字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-cicd-observability/pipeline-monitoring.md` · score=2 · 158字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-gitops/argocd.md` · score=2 · 162字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-best-practices/caching.md` · score=3 · 226字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-best-practices/case-study.md` · score=3 · 555字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `06-best-practices/secure-pipeline.md` · score=3 · 171字 · 缺: 表格, Mermaid 图, 内链, 字数 ≥ 500
- `06-best-practices/secrets-management.md` · score=3 · 222字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-pipeline/overview.md` · score=3 · 398字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-pipeline/tekton.md` · score=3 · 193字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-iac/overview.md` · score=3 · 417字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-iac/pulumi.md` · score=3 · 278字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-iac/terraform-vs-pulumi.md` · score=3 · 297字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-iac/ansible.md` · score=3 · 232字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-release/feature-flag.md` · score=3 · 246字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-cicd-observability/overview.md` · score=3 · 336字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-gitops/overview.md` · score=3 · 357字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-gitops/flux.md` · score=3 · 262字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-gitops/progressive-delivery.md` · score=3 · 267字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500

### chaos（27 / 32）

- `04-platform-compare/decision-tree.md` · score=2 · 604字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图, 内链
- `06-game-day/retro.md` · score=2 · 195字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-resilience-patterns/bulkhead.md` · score=2 · 437字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-resilience-patterns/circuit-breaker.md` · score=2 · 241字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-resilience-patterns/retry-backoff.md` · score=2 · 223字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `07-observability-for-chaos/slo-feedback-loop.md` · score=2 · 463字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `07-observability-for-chaos/measure-steady-state.md` · score=2 · 221字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-chaos-mesh/network-chaos.md` · score=2 · 221字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-chaos-mesh/pod-chaos.md` · score=2 · 318字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-chaos-mesh/workflow.md` · score=2 · 425字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-litmus/sdk.md` · score=2 · 356字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-litmus/probe-check.md` · score=2 · 227字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-litmus/chaos-experiment.md` · score=2 · 167字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-foundations/steady-state.md` · score=2 · 462字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-foundations/history.md` · score=2 · 656字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图, 内链
- `04-platform-compare/overview.md` · score=3 · 1988字 · 缺: 代码块, Vue 组件, Mermaid 图, 内链
- `04-platform-compare/mesh-vs-litmus.md` · score=3 · 651字 · 缺: 代码块, Vue 组件, Mermaid 图, 内链
- `04-platform-compare/open-vs-commercial.md` · score=3 · 714字 · 缺: 代码块, Vue 组件, Mermaid 图, 内链
- `06-game-day/roles.md` · score=3 · 647字 · 缺: 代码块, Vue 组件, Mermaid 图, 内链
- `06-game-day/exercise-design.md` · score=3 · 657字 · 缺: 代码块, Vue 组件, Mermaid 图, 内链
- `05-resilience-patterns/multi-region-dr.md` · score=3 · 675字 · 缺: 代码块, Vue 组件, Mermaid 图, 内链
- `05-resilience-patterns/rate-limit-degrade.md` · score=3 · 523字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `07-observability-for-chaos/overview.md` · score=3 · 1469字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `07-observability-for-chaos/case-study.md` · score=3 · 632字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `02-chaos-mesh/architecture.md` · score=3 · 435字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-foundations/overview.md` · score=3 · 1834字 · 缺: 代码块, Vue 组件, Mermaid 图, 内链
- `01-foundations/blast-radius.md` · score=3 · 468字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500

### design-pattern（27 / 49）

- `02-gof-structural/composite.md` · score=2 · 485字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-modern-patterns/specification.md` · score=2 · 354字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-anti-patterns/big-ball-of-mud.md` · score=2 · 497字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-anti-patterns/callback-hell.md` · score=2 · 427字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-gof-behavioral/iterator.md` · score=2 · 419字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-gof-behavioral/interpreter.md` · score=2 · 427字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-gof-behavioral/command.md` · score=2 · 424字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-gof-behavioral/memento.md` · score=2 · 451字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-gof-behavioral/observer.md` · score=2 · 492字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-gof-behavioral/strategy.md` · score=2 · 445字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-gof-creational/builder.md` · score=2 · 419字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-gof-creational/factory-method.md` · score=2 · 469字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-gof-structural/facade.md` · score=3 · 593字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `02-gof-structural/bridge.md` · score=3 · 494字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-gof-structural/flyweight.md` · score=3 · 523字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `04-modern-patterns/null-object.md` · score=3 · 375字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-modern-patterns/dependency-injection.md` · score=3 · 519字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `06-anti-patterns/magic-number.md` · score=3 · 564字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `06-anti-patterns/circular-dependency.md` · score=3 · 635字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `06-anti-patterns/god-object.md` · score=3 · 543字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `03-gof-behavioral/visitor.md` · score=3 · 563字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `03-gof-behavioral/mediator.md` · score=3 · 561字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `01-gof-creational/singleton.md` · score=3 · 683字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `01-gof-creational/prototype.md` · score=3 · 507字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `05-architectural-patterns/event-sourcing.md` · score=3 · 557字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `05-architectural-patterns/sidecar.md` · score=3 · 640字 · 缺: 表格, Vue 组件, Mermaid 图, 内链
- `05-architectural-patterns/saga.md` · score=3 · 434字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500

### android（25 / 27）

- `index.md` · score=3 · 628字 · 缺: 代码块, 表格, Mermaid 图, 内链
- `questions.md` · score=3 · 811字 · 缺: 代码块, Vue 组件, Mermaid 图, 内链
- `05-toolchain/gradle.md` · score=3 · 179字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-toolchain/ide.md` · score=3 · 185字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-toolchain/publish.md` · score=3 · 183字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-toolchain/README.md` · score=3 · 207字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-perf/performance.md` · score=3 · 186字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-perf/README.md` · score=3 · 208字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-perf/security.md` · score=3 · 180字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-cross/frameworks.md` · score=3 · 172字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-cross/README.md` · score=3 · 213字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-cross/decision.md` · score=3 · 169字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-ui/view-system.md` · score=3 · 169字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-ui/README.md` · score=3 · 228字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-ui/compose.md` · score=3 · 186字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-ui/resource.md` · score=3 · 187字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-system/README.md` · score=3 · 208字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-system/services.md` · score=3 · 181字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-system/startup.md` · score=3 · 193字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-system/runtime.md` · score=3 · 175字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-system/ipc.md` · score=3 · 196字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-app/language.md` · score=3 · 189字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-app/jetpack.md` · score=3 · 177字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-app/README.md` · score=3 · 213字 · 缺: 代码块, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-app/coroutine.md` · score=3 · 182字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500

### go（23 / 36）

- `06-advanced/runtime.md` · score=2 · 387字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/hello-world.md` · score=2 · 246字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/syntax-fundamentals.md` · score=2 · 206字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/package-and-module.md` · score=2 · 409字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/error-handling.md` · score=2 · 343字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-concurrency/context.md` · score=2 · 336字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-ecosystem/testing.md` · score=2 · 340字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-ecosystem/go-toolchain.md` · score=2 · 279字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-ecosystem/benchmark.md` · score=2 · 497字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-cloud-native/docker-internals.md` · score=2 · 347字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-cloud-native/etcd-internals.md` · score=2 · 429字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `index.md` · score=3 · 615字 · 缺: 代码块, 表格, Mermaid 图, 内链
- `06-advanced/cgo.md` · score=3 · 479字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `06-advanced/pprof.md` · score=3 · 425字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `01-basics/types-and-functions.md` · score=3 · 237字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-concurrency/goroutine.md` · score=3 · 366字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-concurrency/patterns.md` · score=3 · 294字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-concurrency/channel.md` · score=3 · 378字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-microservices/service-governance.md` · score=3 · 429字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-microservices/grpc.md` · score=3 · 323字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-microservices/gin-framework.md` · score=3 · 303字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-cloud-native/prometheus-internals.md` · score=3 · 469字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-cloud-native/kubernetes-internals.md` · score=3 · 352字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500

### mysql（23 / 63）

- `09-monitoring/prometheus.md` · score=3 · 354字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-ha/proxysql.md` · score=3 · 251字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `07-ha/mha.md` · score=3 · 463字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-sql/crud.md` · score=3 · 314字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-sql/functions.md` · score=3 · 187字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `12-mybatis/pitfalls.md` · score=3 · 464字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `12-mybatis/spring-boot.md` · score=3 · 267字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `12-mybatis/generator.md` · score=3 · 284字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `12-mybatis/quickstart.md` · score=3 · 288字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `12-mybatis/plugins.md` · score=3 · 289字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `10-sharding/shardingsphere.md` · score=3 · 265字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `10-sharding/sharding-key.md` · score=3 · 320字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-backup/binlog-recovery.md` · score=3 · 354字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-backup/mysqldump.md` · score=3 · 359字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-transaction/deadlock.md` · score=3 · 488字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-replication/replication.md` · score=3 · 388字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-replication/read-write-split.md` · score=3 · 327字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `06-replication/binlog.md` · score=3 · 437字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `02-index/covering.md` · score=3 · 464字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `13-multids/sharding-jdbc.md` · score=3 · 396字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `13-multids/multi-datasource.md` · score=3 · 483字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `13-multids/dynamic-datasource.md` · score=3 · 352字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `11-tools/perf-calculator.md` · score=3 · 340字 · 缺: 代码块, 表格, Mermaid 图, 字数 ≥ 500

### observability（16 / 50）

- `11-scenarios/k8s-monitor.md` · score=2 · 347字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-profiling/pyroscope.md` · score=3 · 238字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `10-profiling/pprof.md` · score=3 · 205字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-loki/logql.md` · score=3 · 252字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-loki/best-practice.md` · score=3 · 247字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-prometheus/alert.md` · score=3 · 224字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `03-prometheus/data-model.md` · score=3 · 190字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `11-scenarios/cost-optimization.md` · score=3 · 253字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `11-scenarios/database-monitor.md` · score=3 · 169字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `11-scenarios/microservice-trace.md` · score=3 · 223字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `09-app-instrumentation/k8s-metrics.md` · score=3 · 162字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `09-app-instrumentation/business-metrics.md` · score=3 · 320字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-grafana/overview.md` · score=3 · 191字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-grafana/annotation.md` · score=3 · 211字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-alerting/severity.md` · score=3 · 191字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `08-alerting/alertmanager.md` · score=3 · 255字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500

### network（14 / 63）

- `12-interview-practice/cases.md` · score=2 · 279字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `path.md` · score=3 · 227字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `07-security/pki-tls.md` · score=3 · 413字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `08-wireless/bluetooth.md` · score=3 · 481字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `12-interview-practice/comparison.md` · score=3 · 775字 · 缺: 代码块, Vue 组件, Mermaid 图, 内链
- `12-interview-practice/questions.md` · score=3 · 893字 · 缺: 代码块, Vue 组件, Mermaid 图, 内链
- `04-network/ipv6.md` · score=3 · 484字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `04-network/icmp.md` · score=3 · 420字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-tools/troubleshooting.md` · score=3 · 424字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-tools/performance-test.md` · score=3 · 401字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `10-tools/tcpdump-curl.md` · score=3 · 283字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `11-cases/https-https.md` · score=3 · 495字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `11-cases/microservice-network.md` · score=3 · 487字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-transport/socket.md` · score=3 · 462字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500

### clickhouse（13 / 36）

- `04-olap-scenarios/overview.md` · score=2 · 452字 · 缺: 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `case-study.md` · score=3 · 2888字 · 缺: 代码块, Vue 组件, Mermaid 图, 内链
- `02-sql/overview.md` · score=3 · 346字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `02-sql/select-aggregate.md` · score=3 · 194字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `04-olap-scenarios/user-tracking.md` · score=3 · 279字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `01-basics/history.md` · score=3 · 809字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图
- `03-table-engine/overview.md` · score=3 · 487字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `03-table-engine/materialized-view.md` · score=3 · 382字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-ecosystem/prometheus.md` · score=3 · 283字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-ecosystem/overview.md` · score=3 · 427字 · 缺: Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `05-ecosystem/kafka-integration.md` · score=3 · 195字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-ecosystem/dbt-airbyte.md` · score=3 · 263字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500
- `05-ecosystem/grafana.md` · score=3 · 333字 · 缺: 表格, Vue 组件, Mermaid 图, 字数 ≥ 500

### tools（13 / 13）

- `json.md` · score=1 · 446字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `base64.md` · score=1 · 343字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图, 内链, 字数 ≥ 500
- `relative.md` · score=2 · 534字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图, 内链
- `url.md` · score=2 · 537字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图, 内链
- `uuid.md` · score=2 · 513字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图, 内链
- `json-csv.md` · score=2 · 668字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图, 内链
- `iso.md` · score=2 · 540字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图, 内链
- `timestamp.md` · score=2 · 605字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图, 内链
- `json-yaml.md` · score=2 · 1084字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图, 内链
- `json-diff.md` · score=2 · 605字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图, 内链
- `cron.md` · score=2 · 951字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图, 内链
- `timezone.md` · score=3 · 695字 · 缺: 代码块, 表格, Vue 组件, Mermaid 图
- `index.md` · score=3 · 815字 · 缺: 代码块, 表格, Mermaid 图, 内链
