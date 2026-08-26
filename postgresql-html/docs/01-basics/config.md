---
title: 关键配置参数
description: postgresql.conf 核心参数调优
---

# 关键配置参数

> **TL;DR**：`postgresql.conf` 有 300+ 参数，**生产只需调 10 个核心参数**就能拿到 80% 性能。**调参原则：先用默认 → 监控瓶颈 → 针对性调整**。

## 一句话定义

```
postgresql.conf = PG 主配置文件
                 = 300+ 参数
                 = 90% 时间只动 10 个核心参数
```

## 10 个核心参数

### 1. shared_buffers（共享缓冲）

```ini
shared_buffers = '8GB'    # 默认 128MB
```

**推荐**：**25% 物理内存**（如 32GB 机器 → 8GB）

**效果**：缓存数据页 + 索引页，**命中 = 不读盘**

### 2. effective_cache_size（planner 决策）

```ini
effective_cache_size = '24GB'    # 默认 4GB
```

**推荐**：**50-75% 物理内存**

**作用**：**不是真实内存分配**，而是告诉 planner "OS 文件缓存大约这么多"，影响是否选择索引扫描

### 3. work_mem（操作内存）

```ini
work_mem = '64MB'    # 默认 4MB
```

**适用**：sort / hash join / hash aggregate

**调优**：根据实际查询调，**太大 = 占用过多内存**，**太小 = 临时文件 spill**

### 4. maintenance_work_mem（维护内存）

```ini
maintenance_work_mem = '512MB'    # 默认 64MB
```

**适用**：VACUUM / CREATE INDEX / ALTER TABLE ADD FOREIGN KEY

**调优**：**可以比 work_mem 大很多**（不是并发操作）

### 5. max_connections（最大连接）

```ini
max_connections = 200    # 默认 100
```

**调优**：**不要超过 300**，**配 PgBouncer 池化**

### 6. WAL 相关

```ini
wal_level = replica                  # 流复制需要
wal_compression = on                 # 压缩 WAL
max_wal_size = '4GB'                 # checkpoint 后最大
min_wal_size = '1GB'
wal_keep_size = '1GB'                # 防止从库断连 WAL 撑爆
```

### 7. autovacuum

```ini
autovacuum = on                      # 默认 on
autovacuum_max_workers = 4           # 默认 3
autovacuum_naptime = '60s'           # 默认 60s 检测
```

### 8. checkpoint

```ini
checkpoint_completion_target = 0.9   # 默认 0.5，平滑 checkpoint
max_wal_size = '4GB'                 # 触发 checkpoint
```

### 9. 查询规划器

```ini
random_page_cost = 1.1               # 默认 4，SSD 改成 1.1
effective_io_concurrency = 200       # SSD 推荐 200，HDD 用 2
```

### 10. 日志

```ini
logging_collector = on
log_destination = 'stderr'
log_min_duration_statement = '500ms' # 记录 > 500ms 的 SQL
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on                  # 锁等待日志
log_temp_files = 0                   # 记录所有临时文件
```

## 调参检查清单

```ini
# 1. 内存类
shared_buffers = '25% RAM'           # 8GB
effective_cache_size = '70% RAM'     # 22GB
work_mem = '32-128MB'                # 看并发数调整
maintenance_work_mem = '512MB'

# 2. 存储类（SSD 优化）
random_page_cost = 1.1
effective_io_concurrency = 200
wal_compression = on

# 3. 连接类
max_connections = 200                # 配合 PgBouncer
superuser_reserved_connections = 3

# 4. WAL 类
wal_level = replica
max_wal_size = '4GB'
checkpoint_completion_target = 0.9

# 5. autovacuum
autovacuum_max_workers = 4
autovacuum_naptime = '30s'           # 检测频率提高

# 6. 监控
shared_preload_libraries = 'pg_stat_statements'
log_min_duration_statement = '500ms'
auto_explain.log_min_duration = '1s' # 配合 auto_explain
```

## 查看当前配置

```sql
-- 当前生效的配置
SHOW shared_buffers;
SHOW all;                  -- 所有参数
SELECT * FROM pg_settings;

-- 修改（session 级别）
SET work_mem = '128MB';

-- 修改（持久）
ALTER SYSTEM SET work_mem = '128MB';
SELECT pg_reload_conf();
```

## 配置文件位置

```bash
# 默认位置
/usr/local/pgsql/data/postgresql.conf      # 源码编译
/etc/postgresql/15/main/postgresql.conf   # Debian/Ubuntu
/var/lib/pgsql/data/postgresql.conf       # CentOS

# 配置目录（include_dir）
postgresql.conf 中：
include_dir = 'conf.d'  # 加载 conf.d/*.conf
```

> **生产建议**：**自定义参数放 conf.d/，不动主配置文件**，方便升级。

## 一句话总结

> **调参 80/20**：**shared_buffers 25% RAM + effective_cache_size 70% RAM + work_mem 64MB + 8 个其他参数 = 拿到 80% 性能**。**先用默认 → 监控 → 针对性调整**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


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

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
