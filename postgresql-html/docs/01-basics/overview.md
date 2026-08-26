---
title: PostgreSQL 概述
---

# PostgreSQL 概述

> 世界上最先进的开源关系型数据库。**30+ 年演化，关系型 + 文档 + 空间 + 向量的全能选手**。

## 1. PostgreSQL 是什么？

```
PostgreSQL（简称 PG / postgres）：
  - 1986 年起源于加州伯克利分校（POSTGRES 项目）
  - 1996 年发布首个版本
  - 2024 年发布 17.x 版本
  - 口号："世界上最先进的开源关系型数据库"

为什么"最先进"：
  - 标准 SQL 完整支持
  - 扩展生态丰富（pgvector / PostGIS / TimescaleDB ...）
  - 严谨的工程实现（MVCC / 多进程架构）
  - 学术友好的许可证（BSD-like）

📌 不是 MySQL 的简单升级，而是完全不同的设计哲学
   - MySQL：易用 + 性能优先（互联网起家）
   - PostgreSQL：严谨 + 标准 + 扩展（学术起家）
```

## 2. 核心特性

### 2.1 数据类型丰富

```
内置：
  - 数值：int / bigint / numeric / float / serial
  - 字符：text / varchar(n) / char(n)
  - 时间：timestamp / date / time / interval
  - 布尔：boolean
  - 货币：money
  - 二进制：bytea
  - UUID：uuid
  - JSON / JSONB
  - 数组：int[] / text[]
  - 范围：int4range / tsrange / daterange
  - 网络：inet / cidr / macaddr
  - 几何：point / line / polygon / circle
  - 全文检索：tsvector / tsquery
  - XML
  - 自定义类型（CREATE TYPE）

📌 MySQL 类型约 30 种，PG 内置约 40 种 + 扩展无数
```

### 2.2 索引类型丰富

```
B-Tree：默认索引（等值 + 范围）
Hash：等值查询（PG 10+ 写入性能改进）
GIN（Generalized Inverted Index）：
  - JSONB
  - 全文检索
  - 数组
  - trigram
GiST（Generalized Search Tree）：
  - 几何（PostGIS）
  - 全文检索
  - 范围类型
BRIN（Block Range INdex）：
  - 大表（> 100GB）
  - 时序数据
  - 物理顺序相关的列
SP-GiST（Space-Partitioned GiST）：
  - IP 地址
  - 电话号码
  - 树形结构

📌 PG 索引类型是 MySQL 的 3-5 倍
```

### 2.3 高级 SQL 特性

```
窗口函数（MySQL 8 才有）：
  ROW_NUMBER() OVER (PARTITION BY ...)
  RANK() OVER (ORDER BY ...)
  LAG / LEAD / FIRST_VALUE / LAST_VALUE
  SUM / AVG ... OVER (...)

CTE（公用表表达式）：
  WITH cte AS (SELECT ...) SELECT * FROM cte;
  支持递归查询（RECURSIVE）

UPSERT：
  INSERT ... ON CONFLICT (key) DO UPDATE SET ...;

生成列：
  GENERATED ALWAYS AS (expr) STORED
  GENERATED ALWAYS AS (expr) VIRTUAL

DML 高级：
  RETURNING：INSERT/UPDATE/DELETE 返回修改的行
  MERGE（PG 15+）：合并 INSERT/UPDATE/DELETE

JSON 操作：
  -> / ->> / #> / @>
  jsonb_set / jsonb_path_query
```

### 2.4 扩展生态

```
PostGIS：空间数据库（GIS 行业标准）
pgvector：向量数据库（AI 时代）
TimescaleDB：时序数据库
Citus：分布式扩展（MPP）
pg_trgm：模糊匹配（trigram）
pg_cron：定时任务
PostgreSQL Anonymizer：数据脱敏
pg_stat_statements：慢查询统计
pgAudit：审计日志
pgBackRest：备份工具
pgFormatter：SQL 美化
```

## 3. 安装与启动

### 3.1 macOS

```bash
# Homebrew（推荐）
brew install postgresql@17
brew services start postgresql@17

# 进入 psql
psql postgres

# 创建数据库
createdb mydb
psql mydb
```

### 3.2 Ubuntu

```bash
# 添加官方源
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# 安装
sudo apt-get update
sudo apt-get install postgresql-17

# 启动
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 切换到 postgres 用户
sudo -u postgres psql
```

### 3.3 Docker

```bash
docker run --name pg17 \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -v /pgdata:/var/lib/postgresql/data \
  -d postgres:17

# 进入容器
docker exec -it pg17 psql -U postgres
```

### 3.4 psql 客户端

```bash
# 连接
psql -h localhost -p 5432 -U postgres -d mydb

# 常用命令
\l              # 列出数据库
\d              # 列出表
\d table_name   # 描述表
\dt             # 列出表
\dv             # 列出视图
\di             # 列出索引
\df             # 列出函数
\dn             # 列出 schema
\du             # 列出用户
\x              # 切换扩展显示
\timing         # 开启计时
\q              # 退出

# 设置
\set AUTOCOMMIT off
```

## 4. 与 MySQL 对比（速览）

| 维度 | PostgreSQL | MySQL |
|---|---|---|
| 许可证 | BSD-like（更宽松） | GPL |
| SQL 标准 | 严格遵循 | 部分支持 |
| JSON 支持 | JSONB（原生索引） | JSON（无索引友好） |
| 全文检索 | tsvector + GIN | FULLTEXT |
| 空间数据 | PostGIS（行业标准） | 基础空间类型 |
| 向量搜索 | pgvector | 无 |
| 写入性能 | 中 | 高 |
| 复杂查询 | 强 | 一般 |
| 运维成本 | 中 | 低 |
| 互联网采用 | 上升（GitHub / Reddit / Instagram） | 主流（淘宝 / 美团） |

📌 PG 是"数据库里的 Linux"，MySQL 是"数据库里的 Windows"
   - PG：可定制、可扩展、技术深度
   - MySQL：开箱即用、性能优先

## 5. 何时选 PostgreSQL？

```
✅ 适合：
  - 复杂查询（窗口函数 / CTE / 递归）
  - 半结构化数据（JSONB）
  - GIS 应用（PostGIS）
  - AI / 向量搜索（pgvector）
  - 时序数据（TimescaleDB）
  - 数据分析（窗口函数强大）
  - 严谨业务（金融 / 医疗）

❌ 不适合：
  - 极简 CRUD（MySQL 更轻量）
  - 单纯高写入（MySQL InnoDB 更成熟）
  - 团队只熟悉 MySQL（迁移成本高）
  - 老旧系统依赖 MySQL 特性

📌 2024 年的趋势：
   新项目选 PG，老 MySQL 项目逐步迁移
```

## 6. 经典案例

```
- GitHub：核心数据存储（部分）
- Reddit：评论系统（PG 9.6+）
- Instagram：早期用户数据（PG 9.x）
- 苹果：iCloud 服务
- 微软：Azure Database for PostgreSQL
- 阿里巴巴：ADB PG（AnalyticDB）
- 字节跳动：内部数据库
- Cloudflare：边缘配置
- Stripe：金融支付数据
- Notion：文档元数据
```

## 7. 一句话总结

```
📌 PostgreSQL = 严谨 SQL + 丰富类型 + 多索引 + 强扩展
📌 30+ 年演化，是 MySQL 的"学术派对手"
📌 杀手锏：JSONB / PostGIS / pgvector / 窗口函数 / CTE
📌 适合：复杂查询 / GIS / AI / 金融 / 半结构化数据
📌 安装：brew / apt / docker，1 行命令
📌 客户端：psql / pgAdmin / DBeaver
📌 AI 时代：pgvector 让 PG 同时是向量数据库（关键）
```

## 8. 参考资料

- PostgreSQL 官方文档
- 《PostgreSQL 修炼之道：从初学者到高手》
- 《PostgreSQL 实战》（谭峰）
- 《高可用 PostgreSQL》（CSDN）
- Hacker News 讨论 PG vs MySQL
- Supabase / Neon / Crunchy Data PG 云服务


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
