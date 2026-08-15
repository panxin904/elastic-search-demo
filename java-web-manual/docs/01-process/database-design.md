---
title: 数据库设计
---

# 数据库设计

好的数据库设计是系统稳定运行的基石。设计不当会导致性能问题、数据错乱、扩展困难。

## 设计流程

### 1. 画 ER 图

先理清实体和关系：

```
[用户] ──1:N──> [订单] ──1:N──> [订单明细] ──N:1──> [商品]
  │                                          
  └──1:N──> [收货地址]
```

### 2. 建表规范

```sql
-- 用户表
CREATE TABLE `t_user` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` VARCHAR(64) NOT NULL COMMENT '用户名',
  `phone` VARCHAR(20) NOT NULL COMMENT '手机号',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 1-正常 2-禁用',
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  KEY `idx_phone` (`phone`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

<div class="kg-note kg-note-tip">
<strong>规范要点</strong>：
<ul>
<li>表名加前缀 t_，字段命名用下划线</li>
<li>每个字段必须有 COMMENT</li>
<li>必须有 create_time 和 update_time</li>
<li>用 BIGINT 做主键，不用分布式ID的提前规划</li>
<li>字符集 utf8mb4，存储引擎 InnoDB</li>
<li>索引命名：主键 pk_，唯一 uk_，普通 idx_</li>
</ul>
</div>

### 3. 索引设计原则

| 原则 | 说明 | 反例 |
|---|---|---|
| 最左匹配 | 联合索引按最左前缀匹配 | `(a,b,c)` 查询 `b=?` 不走索引 |
| 选择性高 | 区分度高的字段适合建索引 | 性别字段只有男女，区分度低 |
| 覆盖索引 | 查询字段都在索引中，避免回表 | SELECT * 无法利用覆盖索引 |
| 避免过多索引 | 索引有维护成本，影响写入性能 | 给所有字段都建索引 |
| 避免函数操作 | WHERE 中字段不能包函数 | `WHERE DATE(create_time)='2024-01-01'` |

### 4. 分库分表策略

| 策略 | 适用场景 | 示例 |
|---|---|---|
| 垂直拆分 | 字段太多，冷热分离 | 用户表拆出扩展信息表 |
| 水平拆分-按时间 | 按时间归档 | 订单表按月分表 `t_order_202401` |
| 水平拆分-按ID | 按ID取模均匀分布 | `t_order_0` ~ `t_order_15` |

### 5. 数据库设计检查清单

- [ ] 所有表都有主键
- [ ] 所有字段都有 COMMENT 注释
- [ ] 高频查询条件都建了索引
- [ ] 没有 SELECT *，明确列出字段
- [ ] 大表评估了分表策略
- [ ] 敏感字段（密码、手机号）评估了加密/脱敏
- [ ] 评估了数据量和增长速度
- [ ] 与 DBA 确认设计方案

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="database-design" :height="400" />
