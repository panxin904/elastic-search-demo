---
title: 函数与过程
description: PL/pgSQL 编程
---

# 函数与过程

> **TL;DR**：PG 函数 = SQL 块 + 流程控制 + 变量。**PL/pgSQL** 是默认语言，**SQL 函数**纯函数式，**PL/Python** 等支持多语言。**触发器、批量处理、业务封装**全靠函数。

## 一句话定义

```
函数 (FUNCTION)  = 返回值，可能无副作用
过程 (PROCEDURE) = 无返回值，可有事务控制（PG 11+）
```

## SQL 函数（最纯）

```sql
-- 1. 简单函数
CREATE FUNCTION add(a INT, b INT) RETURNS INT AS $$
  SELECT a + b;
$$ LANGUAGE SQL IMMUTABLE;

-- 2. 调用
SELECT add(1, 2);  -- 3

-- 3. 表函数（返回 SETOF）
CREATE FUNCTION get_active_users() RETURNS SETOF users AS $$
  SELECT * FROM users WHERE is_active = true;
$$ LANGUAGE SQL;

-- 4. 调用
SELECT * FROM get_active_users();
```

**属性**：

| 属性 | 含义 |
|---|---|
| `IMMUTABLE` | 相同输入永远相同输出 |
| `STABLE` | 同一事务内不变 |
| `VOLATILE` | 每次调用可能不同（默认） |

> **IMMUTABLE 函数可以参与表达式索引**。

## PL/pgSQL 函数

```sql
-- 1. 基本函数
CREATE FUNCTION greet(name TEXT) RETURNS TEXT AS $$
DECLARE
  greeting TEXT;
BEGIN
  greeting := 'Hello, ' || name || '!';
  RETURN greeting;
END;
$$ LANGUAGE plpgsql;

-- 2. 调用
SELECT greet('Alice');  -- 'Hello, Alice!'
```

### 变量与流程

```sql
CREATE FUNCTION analyze_user(user_id BIGINT) RETURNS TEXT AS $$
DECLARE
  user_record users%ROWTYPE;
  status TEXT;
BEGIN
  -- 1. 变量赋值
  SELECT * INTO user_record FROM users WHERE id = user_id;
  
  IF NOT FOUND THEN
    RETURN 'User not found';
  END IF;
  
  -- 2. 条件分支
  IF user_record.age >= 18 THEN
    status := 'adult';
  ELSIF user_record.age >= 13 THEN
    status := 'teen';
  ELSE
    status := 'child';
  END IF;
  
  -- 3. 循环
  FOR i IN 1..10 LOOP
    RAISE NOTICE 'Iteration %', i;
  END LOOP;
  
  RETURN status;
END;
$$ LANGUAGE plpgsql;
```

### 异常处理

```sql
CREATE FUNCTION safe_divide(a INT, b INT) RETURNS NUMERIC AS $$
DECLARE
  result NUMERIC;
BEGIN
  result := a::NUMERIC / b;
  RETURN result;
EXCEPTION
  WHEN division_by_zero THEN
    RAISE NOTICE 'Division by zero';
    RETURN NULL;
  WHEN OTHERS THEN
    RAISE EXCEPTION 'Unknown error: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
```

### 游标

```sql
CREATE FUNCTION process_users() RETURNS INT AS $$
DECLARE
  user_rec RECORD;
  total INT := 0;
BEGIN
  FOR user_rec IN SELECT * FROM users WHERE is_active LOOP
    UPDATE orders SET status = 'reviewed' WHERE user_id = user_rec.id;
    total := total + 1;
  END LOOP;
  RETURN total;
END;
$$ LANGUAGE plpgsql;
```

### OUT / INOUT 参数

```sql
CREATE FUNCTION get_user_stats(
  IN user_id BIGINT,
  OUT total_orders INT,
  OUT total_spent NUMERIC
) AS $$
BEGIN
  SELECT count(*), coalesce(sum(amount), 0)
  INTO total_orders, total_spent
  FROM orders WHERE user_id = get_user_stats.user_id;
END;
$$ LANGUAGE plpgsql;

-- 调用（返回 RECORD）
SELECT * FROM get_user_stats(123);
```

## 过程（PROCEDURE）

**PG 11+ 支持事务控制**：

```sql
CREATE PROCEDURE transfer_money(
  from_account BIGINT,
  to_account BIGINT,
  amount NUMERIC
) AS $$
BEGIN
  UPDATE accounts SET balance = balance - amount WHERE id = from_account;
  UPDATE accounts SET balance = balance + amount WHERE id = to_account;
  
  COMMIT;  -- 过程内可以事务控制（函数不行）
END;
$$ LANGUAGE plpgsql;

-- 调用
CALL transfer_money(1, 2, 100);
```

## 多语言函数

### PL/Python

```sql
-- 1. 安装扩展
CREATE EXTENSION plpython3u;

-- 2. 创建函数
CREATE FUNCTION py_upper(text) RETURNS TEXT AS $$
  return args[0].upper()
$$ LANGUAGE plpython3u;

SELECT py_upper('hello');  -- 'HELLO'
```

### PL/Perl

```sql
CREATE EXTENSION plperlu;
CREATE FUNCTION perl_func() RETURNS TEXT AS $$
  return "Perl says hi";
$$ LANGUAGE plperlu;
```

## 函数管理

```sql
-- 1. 查看函数
\df                 -- psql 命令
SELECT * FROM pg_proc WHERE proname = 'add';

-- 2. 修改函数
ALTER FUNCTION add(INT, INT) IMMUTABLE;

-- 3. 删除
DROP FUNCTION add(INT, INT);

-- 4. 函数权限
GRANT EXECUTE ON FUNCTION add(INT, INT) TO app_user;
```

## 实战案例

### 案例 1：触发器函数

```sql
CREATE FUNCTION update_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### 案例 2：批量处理函数

```sql
CREATE FUNCTION archive_old_logs(days INT) RETURNS INT AS $$
DECLARE
  cutoff TIMESTAMPTZ := now() - (days || ' days')::INTERVAL;
  deleted INT;
BEGIN
  DELETE FROM logs WHERE created_at < cutoff;
  GET DIAGNOSTICS deleted = ROW_COUNT;
  RETURN deleted;
END;
$$ LANGUAGE plpgsql;

-- 调用
SELECT archive_old_logs(30);  -- 删除 30 天前的日志
```

## 一句话总结

> **PG 函数 = SQL + 流程控制**：**SQL 函数（纯）+ PL/pgSQL（带逻辑）+ 过程（带事务控制）**。**触发器、批量处理、业务封装**都靠函数。**90% 场景用 PL/pgSQL 就够了**。

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
