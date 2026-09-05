---
title: 进程架构
date: 2026-08-15  # date-auto-injected
description: PostgreSQL 进程模型与内存结构
---

![PostgreSQL MVCC 原理](/postgresql-mvcc.svg)

# PostgreSQL 进程架构

> **TL;DR**：PG 用 **Postmaster + 多 backend 进程**模式，每客户端连接一个 backend。共享内存用 `shared_buffers / wal_buffers / clog`。**理解进程模型是调优和故障排查的基础**。

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">PostgreSQL WAL 写流程</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">预写日志 · 顺序 IO 优先 · 崩溃恢复</text>

  <!-- 客户端 → 后端 -->
  <rect class="at-hover-card" x="30" y="100" width="100" height="50" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="80" y="125" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">Client</text>
  <text x="80" y="142" text-anchor="middle" font-size="9" fill="#475569">INSERT/UPDATE</text>

  <!-- 后端进程 -->
  <rect class="at-hover-card" x="160" y="100" width="110" height="50" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="215" y="125" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">Backend</text>
  <text x="215" y="142" text-anchor="middle" font-size="9" fill="#475569">解析/执行</text>

  <!-- 共享缓冲 -->
  <rect class="at-hover-card" x="300" y="100" width="110" height="50" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="355" y="125" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">shared_buffers</text>
  <text x="355" y="142" text-anchor="middle" font-size="9" fill="#475569">脏页 (dirty)</text>

  <!-- WAL Buffer -->
  <rect class="at-hover-card" x="160" y="180" width="110" height="50" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="215" y="205" text-anchor="middle" font-size="11" font-weight="700" fill="#991b1b">WAL Buffer</text>
  <text x="215" y="222" text-anchor="middle" font-size="9" fill="#475569">wal_level=replica</text>

  <!-- WAL 文件 -->
  <rect class="at-hover-card" x="30" y="180" width="100" height="50" rx="6" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="80" y="205" text-anchor="middle" font-size="11" font-weight="700" fill="#5b21b6">pg_wal/</text>
  <text x="80" y="222" text-anchor="middle" font-size="9" fill="#475569">段文件 16MB</text>

  <!-- 数据文件 -->
  <rect class="at-hover-card" x="300" y="180" width="110" height="50" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="355" y="205" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">base/</text>
  <text x="355" y="222" text-anchor="middle" font-size="9" fill="#475569">数据文件</text>

  <!-- 箭头 -->
  <line x1="130" y1="125" x2="160" y2="125" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>
  <line x1="215" y1="150" x2="215" y2="180" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>
  <line x1="215" y1="230" x2="130" y2="230" stroke="#10b981" stroke-width="2" marker-end="url(#arr)"/>
  <line x1="270" y1="205" x2="300" y2="205" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>
  <text x="290" y="200" font-size="8" fill="#475569">checkpoint</text>

  <!-- fsync 时机 -->
  <rect x="40" y="260" width="520" height="100" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="300" y="283" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">fsync 时机（commit 时）</text>
  <text x="60" y="305" font-size="11" fill="#334155">① commit → WAL Buffer fsync 到 pg_wal（commit 同步点）</text>
  <text x="60" y="325" font-size="11" fill="#334155">② checkpoint → shared_buffers 脏页刷到 base（异步）</text>
  <text x="60" y="345" font-size="11" font-weight="700" fill="#dc2626">synchronous_commit = on（默认）：commit 等 fsync 返回</text>

  <!-- 崩溃恢复 -->
  <rect x="40" y="375" width="520" height="90" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="300" y="398" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">崩溃恢复（Recovery）</text>
  <text x="60" y="420" font-size="11" fill="#334155">1. 从最近 checkpoint 重放 WAL（redo）</text>
  <text x="60" y="440" font-size="11" fill="#334155">2. 回滚未提交事务（undo）</text>
  <text x="60" y="458" font-size="10" fill="#64748b" font-style="italic">WAL 是「真相之源」—— 数据文件可重建</text>
</svg>

## 一句话定义

```
PostgreSQL = C/S 架构
  服务端 = 1 个 Postmaster + N 个 backend 子进程 + 多个后台 worker
  客户端 = 通过 TCP/Unix socket 连接
```

## 进程模型

### Postmaster 主进程

```
进程 PID = 1（如 /var/lib/postgresql/data/postmaster.pid 记录）
职责：
  - 监听端口（5432）
  - 接受客户端连接
  - fork backend 子进程
  - 管理共享内存
  - 启动后台 worker（bgwriter / walwriter / autovacuum launcher）
```

### backend 子进程

```
每个客户端连接 = 一个 backend 进程
连接断开 = 进程退出

backend 负责：
  - 解析 SQL
  - 生成执行计划
  - 执行查询
  - 返回结果
```

**进程 vs 线程**：

| 维度 | PG（进程） | MySQL（线程） |
|---|---|---|
| 内存 | 不共享（独立） | 共享（需锁） |
| 上下文切换 | 重 | 轻 |
| 稳定性 | 单连接崩溃不影响其他 | | 线程崩溃可能影响全局 |
| 连接数上限 | 几百（受进程数限制） | 上千 |

> **PG 13+**：改进 fork 性能，1000+ 连接数 OK。

### 后台 Worker 进程

| 进程 | 职责 | 默认数量 |
|---|---|---|
| **bgwriter** | 把脏页写回磁盘 | 1 |
| **walwriter** | 把 WAL 刷盘 | 1 |
| **autovacuum launcher** | autovacuum worker 调度 | 1 |
| **autovacuum worker** | 实际 vacuum | max_workers（默认 3） |
| **stats collector** | 收集统计信息 | 1 |
| **logical replication launcher** | 逻辑复制调度 | 1 |
| **walsender** | 流复制 sender | max_wal_senders |
| **walreceiver** | 流复制 receiver | 每个从库 1 个 |

## 内存结构

### 共享内存（Shared Memory）

```
┌────────────────────────────────────────────────┐
│                Shared Buffers                  │
│  ┌──────────────────────────────────────────┐  │
│  │  shared_buffers（默认 128MB）             │  │
│  │  - 数据页缓存                              │  │
│  │  - 索引页缓存                              │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │  wal_buffers（默认 16MB）                 │  │
│  │  - WAL 日志缓冲                            │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │  CLOG（Commit Log）                       │  │
│  │  - 事务提交状态                            │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │  Lock Manager（锁管理）                    │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │  FSM（Free Space Map）+ VM（Visibility Map）│  │
│  └──────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
```

### 每个 backend 的私有内存

```
- work_mem：排序/哈希操作（默认 4MB，可按需调整）
- temp_buffers：临时表（默认 8MB）
- maintenance_work_mem：vacuum / create index（默认 64MB）
```

## 关键配置

```ini
# postgresql.conf

# 1. 共享内存
shared_buffers = '8GB'              # 推荐 25% 物理内存
wal_buffers = '64MB'                # 默认 16MB，写密集型加大

# 2. 后台 worker
bgwriter_delay = '50ms'             # bgwriter 唤醒间隔
bgwriter_lru_maxpages = 400         # 每次最多写 400 页
autovacuum_max_workers = 4          # autovacuum worker 数

# 3. 连接
max_connections = 200               # 最大连接数
superuser_reserved_connections = 3  # 给 superuser 预留

# 4. 内存
work_mem = '64MB'                   # 每操作内存
hash_mem_multiplier = 2.0           # hash join 内存倍数（PG 13+）
maintenance_work_mem = '512MB'      # 维护操作
```

## 实战案例

### 案例：1000 并发系统的进程数调优

**问题**：应用 1000 并发，PG 默认 max_connections=100，后端连接不够。

**方案**：

```ini
# 1. 提高 max_connections（不推荐，因为每连接吃 5-10MB）
max_connections = 300

# 2. 用 PgBouncer 连接池（推荐）
pool_mode = transaction
default_pool_size = 50
# 应用 1000 并发 → PG 后端 50 个连接
```

```sql
-- 查看当前连接数
SELECT count(*) FROM pg_stat_activity;

-- 看每个 backend 状态
SELECT pid, state, query_start, query
FROM pg_stat_activity
WHERE backend_type = 'client backend';
```

## 一句话总结

> **PG 进程模型 = Postmaster + N backend + N worker**。**每连接一个进程 = 内存 5-10MB**，**生产用 PgBouncer 池化**。**shared_buffers 设 25% RAM**，**work_mem 按需调整**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


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

<!-- svg-injected:do-not-edit -->

## 图示：PostgreSQL 进程与内存

![PostgreSQL 进程与内存](/postgres-architecture.svg)
