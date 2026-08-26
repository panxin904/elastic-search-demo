---
title: 触发器
description: BEFORE / AFTER / INSTEAD OF 触发器实战
---

# 触发器

> **TL;DR**：PG 触发器 = **表/视图上自动执行的函数**。**审计日志、自动时间戳、跨表一致性、复杂校验**全靠它。**PG 9+ 支持每语句触发 + 每行触发**。

## 一句话定义

```
触发器 = 表/视图上的"事件钩子"
       = INSERT/UPDATE/DELETE 时自动执行函数
       = BEFORE（修改前）/ AFTER（修改后）/ INSTEAD OF（替代）
```

## 触发器分类

| 维度 | 选项 |
|---|---|
| **时机** | BEFORE / AFTER / INSTEAD OF |
| **范围** | FOR EACH ROW / FOR EACH STATEMENT |
| **事件** | INSERT / UPDATE / DELETE / TRUNCATE |
| **条件** | WHEN（条件触发） |

## 触发器函数

```sql
-- 1. 函数签名
CREATE FUNCTION trg_func() RETURNS TRIGGER AS $$
BEGIN
  -- TG_OP = 'INSERT' / 'UPDATE' / 'DELETE' / 'TRUNCATE'
  -- TG_TABLE_NAME = 表名
  -- NEW.column / OLD.column
  RETURN NEW;  -- INSERT/UPDATE 必须返回 NEW
  -- RETURN OLD;  -- DELETE 必须返回 OLD
  -- RETURN NULL; -- BEFORE + 行触发：跳过本次操作
END;
$$ LANGUAGE plpgsql;

-- 2. 绑定到表
CREATE TRIGGER trg_users_insert
BEFORE INSERT ON users
FOR EACH ROW EXECUTE FUNCTION trg_func();
```

## 实战案例

### 案例 1：自动时间戳

```sql
CREATE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

### 案例 2：审计日志

```sql
CREATE TABLE users_audit (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT,
  operation TEXT,
  old_data JSONB,
  new_data JSONB,
  changed_by TEXT,
  changed_at TIMESTAMPTZ DEFAULT now()
);

CREATE FUNCTION audit_users() RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO users_audit (user_id, operation, new_data, changed_by)
    VALUES (NEW.id, 'INSERT', to_jsonb(NEW), current_user);
    RETURN NEW;
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO users_audit (user_id, operation, old_data, new_data, changed_by)
    VALUES (NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), current_user);
    RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN
    INSERT INTO users_audit (user_id, operation, old_data, changed_by)
    VALUES (OLD.id, 'DELETE', to_jsonb(OLD), current_user);
    RETURN OLD;
  END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_audit
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION audit_users();
```

### 案例 3：软删除

```sql
CREATE FUNCTION soft_delete() RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    UPDATE users SET deleted_at = now() WHERE id = OLD.id;
    RETURN NULL;  -- 阻止真删除
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_soft_delete
BEFORE DELETE ON users
FOR EACH ROW EXECUTE FUNCTION soft_delete();
```

### 案例 4：跨表一致性

```sql
-- 订单表 + 订单日志表
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  status TEXT,
  total NUMERIC
);

CREATE TABLE order_logs (
  id BIGSERIAL PRIMARY KEY,
  order_id BIGINT,
  status TEXT,
  changed_at TIMESTAMPTZ DEFAULT now()
);

CREATE FUNCTION log_order_status() RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status != OLD.status THEN
    INSERT INTO order_logs (order_id, status)
    VALUES (NEW.id, NEW.status);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_orders_status_change
AFTER UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION log_order_status();
```

## INSTEAD OF 触发器（视图）

```sql
-- 1. 创建视图
CREATE VIEW users_view AS
SELECT id, name, email FROM users;

-- 2. 视图不能直接 INSERT，需要 INSTEAD OF
CREATE FUNCTION insert_user_view() RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO users (id, name, email) 
  VALUES (NEW.id, NEW.name, NEW.email);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_view_insert
INSTEAD OF INSERT ON users_view
FOR EACH ROW EXECUTE FUNCTION insert_user_view();

-- 3. 现在可以
INSERT INTO users_view (id, name, email) VALUES (1, 'Alice', '[email protected]');
```

## WHEN 条件触发

```sql
-- 只在 status 变化时触发
CREATE TRIGGER trg_orders_status_change
AFTER UPDATE ON orders
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION log_order_status();
```

> **优化**：WHEN 条件让触发器只在必要时执行，**减少 50%+ 触发次数**。

## 触发器性能

```
BEFORE 触发器 = 修改 NEW（数据预处理）
AFTER 触发器 = 审计 / 跨表一致性
INSTEAD OF  = 视图可写

性能影响：每次 INSERT/UPDATE/DELETE 多一次函数调用
建议：触发器函数保持精简，避免复杂逻辑
```

## 查看触发器

```sql
SELECT 
  trigger_name, 
  event_manipulation, 
  action_timing, 
  action_orientation
FROM information_schema.triggers
WHERE event_object_table = 'users';
```

## 一句话总结

> **触发器 = 表事件钩子**：**BEFORE / AFTER / INSTEAD OF + ROW / STATEMENT + WHEN**。**审计日志、自动时间戳、跨表一致性、软删除、视图可写**都靠它。**PG 触发器支持 WHEN 条件，比 MySQL 灵活**。

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
