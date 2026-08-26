---
title: crates.io
---

# crates.io

crates.io 是 Rust 官方包仓库，与 npm / PyPI 同级，130k+ crates 覆盖几乎所有场景。

## 一句话总结

> **crates.io = Rust 生态的事实标准**。**核心：注册 / 搜索 / 版本管理 / 文档浏览**。

---

## 注册 crates.io 账号

```bash
# 1. 访问 https://crates.io/ 注册账号

# 2. 在 https://crates.io/me 获取 API token

# 3. 登录
cargo login <token>
```

## 搜索 crate

```bash
cargo search serde
```

```
在线搜索：https://crates.io/
- 按下载量排序
- 按最新版本
- 按类别筛选
- 按关键字筛选
- 查看文档：https://docs.rs/<crate-name>
```

## 主流 crates 速查

| 类别 | crate | 用途 |
|------|-------|------|
| **Web 框架** | axum | Tokio 生态 HTTP 框架 |
| **Web 框架** | actix-web | 高性能 HTTP 框架 |
| **异步** | tokio | 异步运行时 |
| **序列化** | serde | 序列化框架 |
| **HTTP Client** | reqwest | 同步 + 异步 |
| **数据库** | sqlx | 异步 SQL |
| **CLI** | clap | 命令行参数 |
| **日志** | tracing | 结构化日志 |
| **错误处理** | anyhow | 应用层错误 |
| **错误处理** | thiserror | 库错误 |
| **加密** | rustls | TLS |
| **性能** | rayon | 数据并行 |
| **并发** | crossbeam | 并发原语 |

## 版本管理

```toml
# Cargo.toml 中的版本约束
[dependencies]
serde = "1.0.215"      # 1.x.y，>= 1.0.215, < 2.0.0
tokio = "^1.40"
reqwest = "0.12"
clap = "~3.2"
```

## 文档站（docs.rs）

```
https://docs.rs/

自动为每个 crate 生成文档：
- API 参考
- 示例代码
- Feature flag 切换
- 版本切换
```

## lib.rs 索引

```
https://lib.rs/

crates.io 的"替代前端"：
- 更现代的 UI
- 更好的搜索
- 统计信息
```

## 实战案例：选型决策

```
场景：HTTP 服务
需求：
  - 高并发（10k+ QPS）
  - 异步
  - 易用
  - 生态成熟

候选：
  - axum（tokio 生态，推荐）
  - actix-web（性能强，学习曲线陡）
  - warp（filter 模式，灵活）

决策：用 axum

依赖：
[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
tower = "0.5"
serde = { version = "1", features = ["derive"] }
```

## 关联章节

- **03-ecosystem/overview**：生态总览
- **03-ecosystem/cargo**：Cargo
- **03-ecosystem/std-lib**：标准库


## crate 选型黄金法则

1. **下载量**：> 100 万 = 主流；> 10 万 = 可用；< 1 万 = 慎用
2. **活跃度**：最近 3 个月有 commit = 维护中；1 年没动 = 死亡
3. **issue/PR 响应**：核心维护者响应 < 7 天 = 健康
4. **文档完整度**：docs.rs 自动生成，看 example + 覆盖率
5. **MSRV（Minimum Supported Rust Version）**：决定可移植性

## 实战：选型 HTTP 客户端

| crate | 同步 | 异步 | TLS | 特点 |
|---|---|---|---|---|
| **reqwest** | ✅ | ✅ | rustls/native | 上手最快 |
| **hyper** | ❌ | ✅ | 需自配 | Tokio 底层 |
| **ureq** | ✅ | ❌ | rustls/native | 轻量 |
| **awc** (actix) | ✅ | ✅ | native | actix 生态 |
| **surf** | ✅ | ✅ | 多种 | 中间件系统 |

**决策树**：
- Tokio 生态 + 易用 → **reqwest**
- 极致控制 + 性能 → **hyper**
- 轻量 CLI 工具 → **ureq**
- actix-web 服务 → **awc**

## 实战：选型序列化框架

```toml
# serde：基础 trait
serde = { version = "1", features = ["derive"] }

# JSON
serde_json = "1"

# YAML
serde_yaml = "0.9"  # 注意：已弃用，推荐 serde_yml

# TOML
toml = "0.8"

# MessagePack（高性能二进制）
rmp-serde = "1"

# BSON（MongoDB）
serde = { version = "1", features = ["derive"] }
bson = "2"
```

## 实战：依赖审计（cargo-deny / cargo-audit）

```bash
# 安装
cargo install cargo-deny --locked
cargo install cargo-audit --locked

# 检查安全漏洞
cargo audit

# 检查许可证合规
cargo deny check license

# 重复依赖检测
cargo tree -d

# 检查过时依赖
cargo install cargo-outdated
cargo outdated
```

## 创建自己的 crate

```bash
# 1. cargo new --lib my_crate

# 2. 完善 Cargo.toml
[package]
name = "my_crate"
description = "A short description (< 200 chars)"
license = "MIT OR Apache-2.0"
repository = "https://github.com/me/my_crate"
keywords = ["async", "tokio"]
categories = ["network-programming"]
edition = "2021"
rust-version = "1.70"  # MSRV

# 3. README.md（crates.io 显示）

# 4. cargo publish --dry-run  # 检查
cargo publish                 # 发布
```

## 私有 registry（企业内部）

```toml
# 企业私有 registry（使用 GitLab / Gitea）
[registries.company]
index = "https://gitlab.mycompany.com/api/v4/packages/rust/cargo-index"

[net]
git-fetch-with-cli = true
```


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
