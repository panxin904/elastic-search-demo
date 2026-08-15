---
title: 版本升级
description: pg_upgrade / 逻辑复制升级
---

# 版本升级

> **TL;DR**：PG 大版本升级有 **3 种方式**：**pg_upgrade 原地升级（5-30 分钟停机）、pg_upgrade --link（秒级停机）、逻辑复制升级（停机 < 1 分钟）**。**生产推荐逻辑复制升级**。

## 一句话定义

```
升级策略 = 大版本升级（13 → 16）+ 零停机
        = 用 pg_upgrade（秒级-分钟级停机）
        = 用逻辑复制（零停机，但需双写）
```

## 三种升级方式对比

| 方式 | 停机时间 | 复杂度 | 数据量限制 |
|---|---|---|---|
| pg_upgrade | 5-30 分钟 | 低 | 无 |
| pg_upgrade --link | 秒级 | 低 | 无（不能回退） |
| 逻辑复制 | < 1 分钟 | 中 | 无（需双倍存储） |
| dump + restore | 数小时 | 低 | 大库慢 |

## 1. pg_upgrade 原地升级

```bash
# 1. 备份
pg_dumpall -h /tmp -f backup.sql

# 2. 停 PG
pg_ctl stop

# 3. 安装新版本（Debian/Ubuntu）
apt install postgresql-16

# 4. 检查升级
/usr/lib/postgresql/16/bin/pg_upgrade   --old-datadir=/var/lib/postgresql/13/main   --new-datadir=/var/lib/postgresql/16/main   --old-bindir=/usr/lib/postgresql/13/bin   --new-bindir=/usr/lib/postgresql/16/bin   --check

# 5. 执行升级
/usr/lib/postgresql/16/bin/pg_upgrade   --old-datadir=/var/lib/postgresql/13/main   --new-datadir=/var/lib/postgresql/16/main   --old-bindir=/usr/lib/postgresql/13/bin   --new-bindir=/usr/lib/postgresql/16/bin

# 6. 启动新版本
pg_ctl -D /var/lib/postgresql/16/main start

# 7. 分析统计
/usr/lib/postgresql/16/bin/vacuumdb --all --analyze-in-stages

# 8. 删除老版本
./delete_old_cluster.sh
```

## 2. pg_upgrade --link 硬链接（秒级停机）

```bash
# 1. 停 PG
pg_ctl stop

# 2. 升级（用硬链接共享文件，不复制）
/usr/lib/postgresql/16/bin/pg_upgrade   --old-datadir=/var/lib/postgresql/13/main   --new-datadir=/var/lib/postgresql/16/main   --old-bindir=/usr/lib/postgresql/13/bin   --new-bindir=/usr/lib/postgresql/16/bin   --link

# ⚠️ 硬链接后不能回退到老版本
# 老数据和新数据指向同一文件

# 3. 启动
pg_ctl -D /var/lib/postgresql/16/main start
```

> **优势**：**停机时间 < 1 秒**（仅启动新版本进程时间）。

## 3. 逻辑复制升级（零停机）

**适用于**：可接受双倍存储的复杂场景。

```bash
# 1. 老版本（13）作为 PUBLISHER
psql -p 5432 -c "CREATE PUBLICATION pub_upgrade FOR ALL TABLES;"

# 2. 新版本（16）作为 SUBSCRIBER
initdb -D /var/lib/postgresql/16/main
pg_ctl -D /var/lib/postgresql/16/main start

psql -p 5433 -c "CREATE SUBSCRIPTION sub_upgrade 
  CONNECTION 'host=localhost port=5432 dbname=mydb' 
  PUBLICATION pub_upgrade;"

# 3. 等待同步完成
psql -p 5433 -c "SELECT * FROM pg_stat_subscription;"

# 4. 应用切换（停写老版本，启用新版本）
# 4.1 停应用
# 4.2 等同步完成
psql -p 5433 -c "SELECT pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), received_lsn)) FROM pg_stat_subscription;"
-- 应该为 0

# 4.3 切流到新版本
# 修改应用连接端口 5432 → 5433

# 4.4 启用老版本为只读 / 删除
```

## 4. pg_dumpall + restore

```bash
# 1. 备份
pg_dumpall -h /tmp -f backup.sql

# 2. 启动新版本
pg_ctl -D /var/lib/postgresql/16/main start

# 3. 恢复
psql -h /tmp -d postgres -f backup.sql
```

## 升级检查清单

```
1. 扩展兼容性
   - 每个扩展都支持新版本？
   - 比如 PostGIS、pg_partman、pg_cron

2. 配置兼容性
   - 废弃参数（如 background_sleep_delay → pg_sleep）
   - 默认值变化

3. SQL 兼容性
   - 数据类型变化（如 timestamp → timestamptz）
   - 函数废弃

4. 性能变化
   - planner 改进可能让查询变慢或变快
   - 需要重新 ANALYZE

5. 客户端驱动
   - JDBC / psycopg / libpq 升级
```

## 实战案例

### 案例 1：PG 13 → 16 在线升级

```bash
# 1. 检查
/usr/lib/postgresql/16/bin/pg_upgrade --check ...

# 2. 测试升级（用副本）
# 在新机器上跑同样步骤

# 3. 生产升级
# - 选择业务低峰
# - 通知所有依赖方
# - 准备回滚方案（dump）
# - 执行 pg_upgrade
# - 启动新版本
# - 验证应用
```

### 案例 2：逻辑复制升级大库

```bash
# 1. 老库（13）开启逻辑复制
psql -p 5432 -c "ALTER SYSTEM SET wal_level = logical;"

# 2. 重启老库（应用 wal_level）
pg_ctl restart

# 3. 创建 PUBLICATION
psql -p 5432 -c "CREATE PUBLICATION pub FOR ALL TABLES;"

# 4. 新库（16）创建 SUBSCRIPTION
psql -p 5433 -c "CREATE SUBSCRIPTION sub CONNECTION '...' PUBLICATION pub;"

# 5. 等待同步（小时级，取决于数据量）

# 6. 切换
# - 应用停写（5 分钟）
# - 等同步
# - 切流
# - 应用启动
```

## 一句话总结

> **PG 升级 = pg_upgrade（秒级-分钟级）+ 逻辑复制（零停机）**。**生产首选 pg_upgrade --link**，**大库用逻辑复制**。**升级前检查扩展兼容性 + 配置兼容性 + SQL 兼容性**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
