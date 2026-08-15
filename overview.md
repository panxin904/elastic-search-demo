# Go 知识图谱（第 25 站）上线总结

> **25 个 VitePress 子站点 · 1345+ 内容页 · 1070+ 知识节点 · https://java-px.bot.cd/go/**

## 1. ADR-007 Go 决策

**Theme**: go-cyan `#00ADD8`（Go 官方 cyan）

**6 章 35 页**（覆盖 Go 语言生态 + 云原生 + 微服务全栈）：
- 01-basics (6): 基础语法 / 类型与函数 / 错误处理 / 包与模块 / Hello World / 总览
- 02-concurrency (6): goroutine / channel / sync 包 / context / 并发模式 / CSP 总览
- 03-ecosystem (5): Go 工具链 / 标准库 / testing / benchmark / 生态总览
- 04-cloud-native (6): Docker 源码 / K8s 源码 / Prometheus 源码 / etcd 源码 / CNCF 全景 / 总览
- 05-microservices (6): Gin / gRPC / Kratos/go-zero/go-micro / 服务治理 / 案例研究 / 总览
- 06-advanced (6): runtime GMP / GC 三色标记 / pprof 与 trace / cgo 与 FFI / 反射 / 总览

**双主线架构**：
- 主线一（基础）：01-basics → 02-concurrency → 03-ecosystem
- 主线二（云原生微服务）：04-cloud-native（Docker / K8s / Prometheus / etcd）→ 05-microservices（Gin / gRPC / Kratos）→ 06-advanced（GMP / GC / pprof）

**显式不做**：
- Web 框架完整对比（聚焦 Gin / gRPC / Kratos 三大主线）
- Go vs 其他语言完整对比（避免与 rust / java-language 重复）
- 游戏开发 / GUI / 移动端（Go 在这些领域生态弱）
- 完整 Go 标准库文档（仅介绍 TOP 20 + 用法）
- CGO 深度优化（仅介绍基础）

**与其它站的交叉引用**：
- cloud-native：K8s 部署 Go 应用 / Operator 模式
- rust：Go 的 GMP vs Rust async runtime 对比
- system-design：微服务架构 + 分布式系统
- observability：Prometheus client_golang / OpenTelemetry Go SDK
- security：Go crypto 标准库 / SPIFFE / cert-manager

## 2. 4 大子任务（Task 67-70）

### Task 67：ADR-007（已完成）
`release/adr/007-go.md`（~8.8KB），决策主题色 #00ADD8、双主线、6 章 35 页规划、显式不做边界。

### Task 68：Scaffold go-html（已完成）
- `go-html/package.json`：vitepress 1.6.4 + vue 3.4 + echarts + vue-echarts
- `go-html/.vitepress/config.mts`：base=/go/、6 章 sidebar、25 站下拉、theme #00ADD8
- `go-html/docs/index.md`：layout home + hero "Go 知识图谱 · 云原生 + 后端微服务深度图谱 · 从 goroutine 到 Kubernetes" + 6 features
- 6 篇手写 overview 总览（5-6KB / 篇）
- 1 篇 case-study（12KB，12 个真实大厂 Go 实践：Uber / 字节 Kitex / Twitch Twirp / B 站 Kratos / Cloudflare / 好未来 go-zero / HashiCorp / 滴滴 / GitHub Actions / K8s scheduler / etcd Raft / Prometheus TSDB）

### Task 69：批量生成 28 篇 stub（已完成）
- `scripts/gen-go-stubs.py`（10004 行 / 28 entries / `add(path, r"""...""")` raw string 模式）
- **关键发现**：Go 1.18+ 泛型 `[T any]` 用方括号（中括号），与 Rust 泛型 `<T>`（尖括号）不同，**不需要 fix 脚本**
- 28 篇一次性生成，Python `ast.parse` 验证通过
- **最终 35/35 substantial（最小 4.6KB = go-toolchain.md / 最大 20.8KB = case-study.md）**，0 stub 残留

### Task 70：4 处同步 + 部署 + 25 站冒烟（已完成）
| 位置 | 修改 |
|---|---|
| `sites-hub/build-release.sh` | line 20：加 `go-html` 到 `for project in` 列表末尾；line 47：新增 `go-html) target_name="go"` case |
| `release/deploy-fs.sh` | line 13：`SITE_LIST` 末尾 append `go`；nginx patches：新增 /go 裸路径 301 + /go/ 服务 block（锚点用 rust 而非 video） |
| `sites-hub/www/index.html` | 24→25 / 1310→1345 / 1035→1070 / chip counts (data 4→5 / backend 6→7 / infra 3→4) / visibleCount 24→25 / og / brand-sub / hero-lede / footer / about；新增 Go 卡片（🐹 #00ADD8 900ms）+ Go update feed 条目（2026-08-10 第 25 站） |
| go favicon | 从 `shared-assets/` 复制 favicon.ico / favicon.svg / apple-touch-icon.png 到 `go-html/.vitepress/public/` |

**部署**（用户临时提供 root 密码）：
- 增量 build：`rm -rf release/sites-hub/{www,go}` + cp 重新 stage + tar 重新打包（40MB）
- ⚠️ **坑**：go-html 无 package-lock.json，必须先 `npm install`（15s）生成，再 `npm run docs:build`（11.45s）
- `printf '%s\n' "$PW" | bash deploy-fs.sh`
- Release: `/var/www/sites-hub/releases/20260811130010`
- nginx -t + reload 成功
- htpasswd 重新写入

**冒烟**（25/25 全 OK）：
- 25 个站点首页：nav≥2 / foot≥2 / hero≥3 / size > 19KB
- go 站首页 25.4KB，nav=2 foot=2 hero=4
- 6 个抽样 go 子页（01-basics/overview / 02-concurrency/goroutine / 03-ecosystem/standard-library / 04-cloud-native/kubernetes-internals / 05-microservices/case-study / 06-advanced/runtime）全部 200，size 50-110KB
- 25 站总页面数：1345+ pages / 25 sites

## 3. 关键经验沉淀

### Go 泛型不需要 fix 脚本（与 Rust 对比）
**与 Rust 泛型差异**：
- Rust：`<T>`、`Box<dyn Trait>`、`Arc<Mutex>` — 尖括号，被 Vue 当 HTML 标签
- Go 1.18+：`[T any]`、`[K comparable, V any]` — 方括号，被 Vue 当普通文本

**原因**：VitePress 用 Vue 的 markdown 解析器，`<` 后跟字母字符才识别为 HTML；`[` 不会。

**未来 Go 站新内容**：无需 fix 脚本，直接写。

### Stub 生成脚本模式（rust → go 复用）
- 模式：`add(path, r"""...""")` 函数 + raw string + CONTENT 字典
- raw string 让内嵌 `"""` 不被识别为字符串闭合
- 10004 行 / 28 entries，单文件可读
- Python `ast.parse` 验证语法
- 冷门主题天然短（hash / spgist / sdk.md / otlp.md），需要手动扩"实战案例"

### 部署脚本增量模式
**避免全量重建**：只 stage 变更站点（`www` + 新站）+ 重新 tar，节省 30+ 分钟。
```
rm -rf release/sites-hub/{www,go}
cp -R sites-hub/www release/sites-hub/www
cp -R go-html/.vitepress/dist release/sites-hub/go
cp -R go-html/.vitepress/public/. release/sites-hub/go/  # favicon
tar -C release -czf sites-hub-static.tar.gz sites-hub
```

### macOS BSD cp 陷阱（已踩）
- `cp -R src dst` 不覆盖已存在的 dst
- 必须先 `rm -rf dst` 再 `cp -R src dst`
- 否则 tar 里还是旧内容，部署后冒烟失败

### npm ci vs npm install
- `npm ci` 要求 package-lock.json 存在
- 全新站（无 lockfile）必须用 `npm install` 先生成
- 然后 `npm ci` 用于持续集成（严格按 lockfile）

### 部署密码管理（建议改进）
- 当前：用户每次提供 `export PW=...` + `printf '%s\n' "$PW" | bash deploy-fs.sh`
- 改进：`security add-generic-password -s vps-root -a root -w <PW> -U` 写入 macOS keychain
- 后续 deploy 脚本自动从 keychain 读取

## 4. 最终状态

- **24 → 25 站**：Go 语言生态图谱（🐹 #00ADD8）
- **1345+ 内容页** / **1070+ 知识节点**
- **40 MB tar** 部署包
- 25/25 站冒烟通过，go 站 6/6 抽样子页 200
- 0 stub 残留（35 篇 md 全 ≥3KB）
- 完整 ADR-007 决策文档
- 4 处同步（build-release.sh / deploy-fs.sh / www/index.html / favicon）齐备
- CNCF 80% Go 写 → go-html 与 cloud-native / observability 强互补

## 5. 后续可扩展方向

- **新章节**：07-go-tooling-deep（delve 调试 / golangci-lint 100+ linter）/ 08-otel-go（OpenTelemetry Go SDK 实战）/ 09-k8s-operator（Kubebuilder 实战）
- **新站点候选**（Tier 2 roadmap 剩余）：MongoDB（第 26）/ ClickHouse（第 27）/ gRPC-deep-dive（第 28）/ Design Patterns（第 29）/ Kotlin / Scala / MLOps
- **ADR-008 候选**：MongoDB（文档型 vs Go 的 BSON）/ ClickHouse（OLAP vs Go 的 ch-go driver）
- **关键 chain**：go-html 与 cloud-native / observability 互补（CNCF 80% Go 写）→ 未来 26-30 站可优先 MongoDB / ClickHouse / Chaos Engineering
