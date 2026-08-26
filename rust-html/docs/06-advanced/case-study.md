---
title: Rust 案例研究
---

# Rust 案例研究

5 个真实 Rust 生产案例：Discord / Cloudflare / AWS / Figma / TiKV。每个案例展示 Rust 在生产中的关键决策与陷阱。

## 一句话总结

> **Rust 生产案例 = 高性能 + 高可靠 + 工程实践**。**核心场景：网络服务 / 数据库 / 系统工具 / WebAssembly**。

---

## 案例 1：Discord 的 Elixir → Rust 迁移

**背景**：Discord 的 Read State 服务最初用 Elixir 实现，2020 年因性能问题迁到 Rust。

**原 Elixir 服务**：
- 延迟 P99：数百毫秒
- CPU 占用高
- GC 停顿导致 P99 飙升

**Rust 重写后**：
- 延迟 P99：降到 5ms 以下
- CPU 占用降低 10 倍
- 内存占用降低 5 倍
- GC 停顿消失

**关键决策**：
```
1. 选择 tokio 作为异步运行时
2. 用 dashmap 实现高并发 HashMap
3. 用 moka 实现 LRU 缓存
4. 全链路 tracing + metrics
```

**经验**：
- Rust 在 IO 密集型服务上同样优于 BEAM
- 编译期类型安全减少了运行期 bug
- 团队需要 6 个月学习 Rust，期间效率下降是预期

## 案例 2：Cloudflare Workers 的 Rust Runtime

**背景**：Cloudflare Workers 是边缘计算平台，2023 年支持 Rust 编写的 Worker。

**挑战**：
- Worker 启动时间 < 5ms
- 多租户隔离
- 不能预热（冷启动要求）

**Rust 方案**：
```rust
use worker::*;

#[event(fetch)]
async fn main(req: Request, env: Env, ctx: Context) -> Result<Response> {
    let path = req.path();
    
    match path.as_str() {
        "/api/hello" => {
            let name = req.query().get("name").unwrap_or("World");
            Response::ok(format!("Hello, {}!", name))
        }
        _ => Response::error("Not Found", 404),
    }
}
```

**优势**：
- 启动时间 1ms 以下
- 内存占用比 Node.js Worker 小 70%
- 无 V8 GC 暂停
- wasm-bindgen 与 JS 互操作零开销

## 案例 3：AWS Firecracker 的微虚拟机

**背景**：AWS Lambda 用 Rust 实现了 Firecracker 微虚拟机，启动时间 < 125ms，内存占用 < 5MB。

**架构**：
```
Firecracker
  ├── KVM 内核接口（Linux）
  ├── 极简设备模型（virtio + serial + console）
  ├── REST API 控制
  └── 内存气球（balloon）动态调整
```

**Rust 的优势**：
- 无 GC：内存占用可预测
- 零成本抽象：硬件操作代码可读性等同 C
- 编译期保证：减少 CVE 数量
- tokio 异步 IO：处理数千个并发微 VM

**结果**：
- Lambda 启动时间 < 100ms
- 单机可运行 10000+ 微 VM
- 内存安全漏洞比 QEMU 少 80%

## 案例 4：Figma 的 Rust 重写

**背景**：Figma 的多人协同编辑引擎从 TypeScript 重写到 Rust。

**原 TypeScript**：
- 客户端内存占用高
- 大文档性能差
- 同步冲突频繁

**Rust 重写**（multiplayer-rs）：
- CRDT（Conflict-free Replicated Data Types）实现
- 通过 WebAssembly 在浏览器运行
- 用 webrtc-rs 实现 P2P 同步

**成果**：
- 文档大小支持从 1k 提升到 100k+ 对象
- 同步延迟 < 50ms
- 浏览器内存占用降低 60%

## 案例 5：TiKV 的分布式 KV 存储

**背景**：TiKV 是 PingCAP 的分布式事务 KV 存储，Rust 实现。

**架构**：
```
TiKV
  ├── Raft 共识（raft-rs）
  ├── RocksDB 存储引擎
  ├── 分布式事务（Percolator）
  └── Coprocessor（SQL 下推）
```

**Rust 的关键决策**：
```
1. 异步运行时：tokio + futures
2. RPC：grpc-rs（基于 HTTP/2）
3. 序列化：protobuf + serde
4. 错误处理：自定义 Error + thiserror
5. 测试：mockall + criterion
6. 监控：Prometheus exporter
```

**生产规模**：
- 单集群支持 PB 级
- 100 万+ QPS
- 99.99% 可用性

## 5 大共性经验

```
1. 异步运行时首选 tokio
   - 生态最完整、性能最强
   - 但要小心 blocking 操作要 spawn_blocking

2. 序列化首选 serde
   - 性能等同手写
   - 支持 JSON/YAML/TOML/Bincode/MessagePack

3. 错误处理分层
   - anyhow（应用层，简单）
   - thiserror（库层，结构化）
   - 自定义 Error enum（大型项目）

4. 性能优化工具链
   - cargo flamegraph（火焰图）
   - cargo bench（基准）
   - cargo bloat（二进制大小分析）

5. 部署目标
   - 原生可执行（最大性能）
   - WebAssembly（边缘 / 跨平台）
   - FFI 库（嵌入到 Python/Node/Ruby）
```

## 关联章节

- **04-concurrency/tokio**：Tokio 运行时
- **05-systems/unsafe**：unsafe 实战
- **05-systems/performance**：性能优化
- **05-systems/wasm**：WASM 实战

## 一句话总结

> **Rust 已从"前沿语言"变成"生产首选"**：Discord / Cloudflare / AWS / Figma / TiKV 都是大型生产部署。**关键场景：网络服务 / 数据库 / 嵌入式 / 高性能工具**。


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->
