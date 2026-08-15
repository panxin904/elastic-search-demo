---
title: Oracle vs PostgreSQL
description: 企业级 RDBMS 迁移对比
---

# Oracle vs PostgreSQL

> **TL;DR**：Oracle 和 PG 都是企业级 RDBMS，PG 在 2000 年代崛起后逐渐替代 Oracle。**90% 业务场景 PG 已够用**（除极端 OLAP / RAC / 高级特性），**迁移成本主要是 SQL 语法 + 数据类型 + 高级特性**。

## 一句话定义

```
Oracle = 老牌商业 RDBMS，统治企业市场 30+ 年
PG    = 开源 RDBMS，功能完整度已对标 Oracle
```

## 整体对比

| 维度 | Oracle | PostgreSQL |
|---|---|---|
| 厂商 | Oracle 公司 | 全球社区 + 多家公司 |
| 许可 | 商业（昂贵） | BSD 开源（免费） |
| 性能 | 极致（专用优化） | 接近（取决于配置） |
| 高可用 | RAC（共享存储） | 流复制 + Patroni（异步同步） |
| 扩展性 | 复杂（Exadata / 分区） | 灵活（FDW / Citus / TimescaleDB） |
| SQL 兼容性 | SQL 完整 | 高度兼容 ANSI + Oracle 风格 |
| 运维成本 | 高（DBA 专业） | 中（门槛低） |
| 成本 | 数十万$/年 | 0 元 |
| 适用 | 金融 / 电信 / 大型 OLTP | 互联网 / 中小企业 / 通用 |

## SQL 语法差异

### 序列 vs AUTO_INCREMENT

```sql
-- Oracle
CREATE SEQUENCE user_seq START WITH 1 INCREMENT BY 1;
CREATE TABLE users (id NUMBER DEFAULT user_seq.NEXTVAL PRIMARY KEY, ...);

-- PostgreSQL
CREATE TABLE users (id BIGSERIAL PRIMARY KEY, ...);
-- 或更标准
CREATE SEQUENCE user_seq START 1;
CREATE TABLE users (id INT DEFAULT nextval('user_seq') PRIMARY KEY);
```

### 分页

```sql
-- Oracle（11g 之前用 ROWNUM）
SELECT * FROM (
  SELECT t.*, ROWNUM rn FROM users t WHERE ROWNUM <= 20
) WHERE rn > 10;

-- Oracle 12c+
SELECT * FROM users
ORDER BY id OFFSET 10 ROWS FETCH NEXT 10 ROWS ONLY;

-- PostgreSQL（标准 SQL）
SELECT * FROM users ORDER BY id LIMIT 10 OFFSET 10;
```

### 字符串拼接

```sql
-- Oracle
SELECT 'Hello' || ', ' || 'World' FROM dual;
-- 'Hello, World'

-- PG 同样支持 ||，但更推荐 concat()
SELECT concat('Hello', ', ', 'World');
```

### NVL vs COALESCE

```sql
-- Oracle
SELECT NVL(name, 'unknown') FROM users;

-- PG（更标准）
SELECT COALESCE(name, 'unknown') FROM users;
```

### SYSDATE vs now()

```sql
-- Oracle
SELECT SYSDATE FROM dual;
SELECT SYSTIMESTAMP FROM dual;

-- PG
SELECT now();
SELECT current_timestamp;
SELECT clock_timestamp();  -- 包含时区，更精确
```

### DECODE vs CASE

```sql
-- Oracle
SELECT DECODE(status, 'A', 'Active', 'I', 'Inactive', 'Unknown') FROM users;

-- PG（更标准）
SELECT CASE status 
  WHEN 'A' THEN 'Active'
  WHEN 'I' THEN 'Inactive'
  ELSE 'Unknown'
END FROM users;
```

## 数据类型映射

| Oracle | PostgreSQL |
|---|---|
| NUMBER(p, s) | NUMERIC(p, s) |
| VARCHAR2(n) | VARCHAR(n) |
| CLOB | TEXT |
| BLOB | BYTEA |
| DATE | TIMESTAMP |
| TIMESTAMP | TIMESTAMP WITH TIME ZONE |
| RAW(16) | UUID |
| ROWID | CTID（类似但不同） |

```sql
-- UUID 映射（Oracle RAW(16) → PG UUID）
-- Oracle
SELECT SYS_GUID() FROM dual;     -- RAW(16)
-- PG
SELECT gen_random_uuid();        -- UUID

-- 大对象
-- Oracle: BLOB / CLOB
-- PG: BYTEA / TEXT（无单独类型，最大 1GB）
-- 或用 Large Objects (OID)
```

## 高级特性对比

### 分区

```sql
-- Oracle（语法丰富）
CREATE TABLE orders (
  id NUMBER,
  created_at DATE
)
PARTITION BY RANGE (created_at) (
  PARTITION p_2024 VALUES LESS THAN (TO_DATE('2025-01-01', 'YYYY-MM-DD')),
  PARTITION p_2025 VALUES LESS THAN (TO_DATE('2026-01-01', 'YYYY-MM-DD'))
);

-- PostgreSQL（声明式）
CREATE TABLE orders (
  id BIGSERIAL,
  created_at TIMESTAMPTZ
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_2024 PARTITION OF orders
  FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### 物化视图

```sql
-- Oracle
CREATE MATERIALIZED VIEW sales_mv
REFRESH FAST START WITH SYSDATE NEXT SYSDATE + 1/24
AS SELECT product_id, SUM(amount) FROM orders GROUP BY product_id;

-- PostgreSQL
CREATE MATERIALIZED VIEW sales_mv AS
SELECT product_id, SUM(amount) FROM orders GROUP BY product_id;

-- 手动刷新
REFRESH MATERIALIZED VIEW sales_mv;
-- 或并发刷新（不阻塞读）
REFRESH MATERIALIZED VIEW CONCURRENTLY sales_mv;
```

### 触发器

```sql
-- Oracle
CREATE OR REPLACE TRIGGER trg_users_bi
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
  :NEW.created_at := SYSDATE;
END;

-- PostgreSQL
CREATE OR REPLACE FUNCTION trg_users_bi()
RETURNS TRIGGER AS $$
BEGIN
  NEW.created_at := now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_bi
BEFORE INSERT ON users
FOR EACH ROW EXECUTE FUNCTION trg_users_bi();
```

## 存储过程语言

```sql
-- Oracle PL/SQL
CREATE OR REPLACE PROCEDURE calc_bonus(emp_id NUMBER) AS
  v_salary NUMBER;
BEGIN
  SELECT salary INTO v_salary FROM employees WHERE id = emp_id;
  UPDATE employees SET bonus = v_salary * 0.1 WHERE id = emp_id;
  COMMIT;
END;

-- PostgreSQL PL/pgSQL
CREATE OR REPLACE PROCEDURE calc_bonus(emp_id INT)
LANGUAGE plpgsql AS $$
DECLARE
  v_salary NUMERIC;
BEGIN
  SELECT salary INTO v_salary FROM employees WHERE id = emp_id;
  UPDATE employees SET bonus = v_salary * 0.1 WHERE id = emp_id;
  COMMIT;
END;
$$;
```

## 迁移实战

### 工具链

| 工具 | 用途 |
|---|---|
| **ora2pg** | Oracle schema → PG schema 自动转换 |
| **AWS DMS** | 数据迁移服务 |
| **pgloader** | 异构数据库实时迁移 |
| **ora2pg** | 评估迁移工作量 |
| **EDB Postgres Advanced Server** | Oracle 兼容 PG 发行版 |

### 评估迁移工作量

```bash
# ora2pg 评估
ora2pg -t SHOW_REPORT -c config/ora2pg.conf > migration_report.html
```

报告包含：

```
- 表数量、视图、序列、触发器数量
- PL/SQL 代码行数（需重写）
- 物化视图数量
- 估计迁移工作量（人月）
```

### 迁移步骤

```
1. 评估（ora2pg report）
   ↓
2. Schema 转换（ora2pg）
   ↓
3. 数据迁移（pgloader / DMS）
   ↓
4. PL/SQL → PL/pgSQL 重写
   ↓
5. 应用改造（JDBC 驱动、SQL 兼容性）
   ↓
6. 性能对比（pgbench）
   ↓
7. 切换（双写 → 切读 → 切写）
```

### 应用层兼容

```java
// Oracle
Class.forName("oracle.jdbc.driver.OracleDriver");
Connection conn = DriverManager.getConnection(
  "jdbc:oracle:thin:@host:1521:ORCL", "user", "pass");

// PostgreSQL
Class.forName("org.postgresql.Driver");
Connection conn = DriverManager.getConnection(
  "jdbc:postgresql://host:5432/mydb", "user", "pass");

// ORM 层（MyBatis/Hibernate）：多数 SQL 通用，需调整：
// 1. ROWNUM → LIMIT/OFFSET
// 2. SYSDATE → now()
// 3. NVL → COALESCE
// 4. 序列语法 → PG 标准
```

## 性能对比

| 场景 | Oracle | PG |
|---|---|---|
| OLTP（简单查询） | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 复杂分析（窗口函数） | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 大数据量分区表 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| RAC 横向扩展 | ⭐⭐⭐⭐⭐ | ⭐⭐（用 Citus 弥补） |
| 地理位置 | ⭐⭐⭐（需 Spatial） | ⭐⭐⭐⭐⭐（PostGIS 原生） |
| JSON/JSONB | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 全文检索 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 扩展（pgvector / pg_trgm） | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## 何时选 Oracle

```
✓ 已有 Oracle 资产 + DBA 团队 + 历史包袱
✓ 极端 RAC / Exadata 性能需求
✓ 高级特性（高级队列、高级压缩、TimesTen）
✓ 金融强一致（虽然 PG 也行，但 Oracle 历史更稳）
✓ 客户/审计要求商业 DB
```

## 何时选 PG

```
✓ 互联网业务（启动成本敏感）
✓ 云原生 / K8s（PG 容器化更友好）
✓ 高级扩展需求（pgvector / PostGIS / TimescaleDB）
✓ 多数据源集成（FDW / 逻辑复制）
✓ 想用开源 + 社区驱动
```

## 一句话总结

> **PG 已对标 Oracle 90% 功能**。**迁移决策点不在技术**，**在成本**（Oracle 数十万$/年 vs PG 0 元）和**生态**（既有 DBA / 应用代码）。互联网新业务直接 PG，传统企业系统评估后迁移。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>