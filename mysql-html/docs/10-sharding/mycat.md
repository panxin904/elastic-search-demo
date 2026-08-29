---
title: MyCat 中间件
date: 2026-08-15  # date-auto-injected
---

# 🐱 MyCat 中间件

> MyCat 是基于阿里 Cobar 二次开发的数据库中间件，是 Java 生态中最老牌的分库分表方案之一。

## 🎯 MyCat 是什么？

MyCat 是一个**数据库代理**，位于应用和 MySQL 之间，对应用表现为一个 MySQL 服务器。

```
┌──────────┐       ┌──────────┐       ┌──────────────┐
│   App    │ ────→ │  MyCat   │ ────→ │  MySQL 多实例 │
│          │  3306  │  (8066)  │       │  (3306)       │
└──────────┘       └──────────┘       └──────────────┘
                  (像 MySQL 一样连接)
```

## 🏆 MyCat 的核心特性

### 1. 分库分表

```
- 水平分表：按分片键将数据分布到多个表
- 垂直分库：按业务将数据分布到多个库
- 多分片键：支持复合分片
- ER 分片：父子表绑定（同分片）
```

### 2. 读写分离

```
- 主库写入
- 从库读取
- 负载均衡
- 心跳检测
```

### 3. 多租户

```
- 逻辑库隔离
- 资源控制
- 权限管理
```

## 📦 MyCat 安装

### 1. 下载

```bash
# 下载最新版本（1.6.x）
wget http://dl.mycat.org.cn/1.6.7.6/20190927161129/Mycat-server-1.6.7.6-release-20190927161129-linux.tar.gz

# 解压
tar -xzf Mycat-server-*.tar.gz

# 进入目录
cd mycat
ls
# bin/  conf/  lib/  logs/
```

### 2. 启动

```bash
# 启动
./bin/mycat start

# 查看状态
./bin/mycat status

# 停止
./bin/mycat stop

# 重启
./bin/mycat restart
```

## ⚙️ MyCat 配置

### 1. server.xml（核心配置）

```xml
<!-- conf/server.xml -->
<mycat:server xmlns:mycat="http://io.mycat/">
  <system>
    <property name="nonePasswordLogin">0</property>
    <property name="useHandshakeV10">1</property>
    <property name="useSqlStat">0</property>
    <property name="useGlobleTableCheck">0</property>
    <property name="sequnceHandlerType">2</property>
    <property name="processorCheckPeriod">1000</property>
  </system>

  <!-- 用户配置 -->
  <user name="app_user" defaultAccount="true">
    <property name="password">StrongP@ss!</property>
    <property name="schemas">order_db</property>
    <property name="readOnly">false</property>
  </user>
</mycat:server>
```

### 2. schema.xml（分片配置）

```xml
<!-- conf/schema.xml -->
<mycat:schema xmlns:mycat="http://io.mycat/">

  <!-- 逻辑库：order_db -->
  <schema name="order_db" checkSQLschema="true" sqlMaxLimit="100">
    <!-- 订单表（分片表） -->
    <table name="orders" dataNode="dn0,dn1,dn2,dn3" rule="mod-long">
      <!-- ER 绑定：order_items 与 orders 同分片 -->
      <childTable name="order_items" primaryKey="id" joinKey="order_id" parentKey="id"/>
    </table>

    <!-- 广播表：每个节点都存一份 -->
    <table name="config" type="global"/>
  </schema>

  <!-- 数据节点（物理库） -->
  <dataNode name="dn0" dataHost="dh0" database="order_db_0"/>
  <dataNode name="dn1" dataHost="dh1" database="order_db_0"/>
  <dataNode name="dn2" dataHost="dh0" database="order_db_1"/>
  <dataNode name="dn3" dataHost="dh1" database="order_db_1"/>

  <!-- 数据主机（物理 MySQL） -->
  <dataHost name="dh0" maxCon="1000" minCon="10" balance="0" writeType="0" dbType="mysql" dbDriver="native" switchType="1" slaveThreshold="100">
    <heartbeat>select user()</heartbeat>
    <writeHost host="mysql-master-0" url="192.168.1.10:3306" user="root" password="xxx"/>
  </dataHost>

  <dataHost name="dh1" maxCon="1000" minCon="10" balance="0" writeType="0" dbType="mysql" dbDriver="native" switchType="1" slaveThreshold="100">
    <heartbeat>select user()</heartbeat>
    <writeHost host="mysql-master-1" url="192.168.1.11:3306" user="root" password="xxx"/>
  </dataHost>
</mycat:schema>
```

### 3. rule.xml（分片规则）

```xml
<!-- conf/rule.xml -->
<mycat:rule xmlns:mycat="http://io.mycat/">
  <tableRule name="mod-long">
    <rule>
      <columns>user_id</columns>
      <algorithm>mod-long</algorithm>
    </rule>
  </tableRule>

  <function name="mod-long" class="io.mycat.route.function.PartitionByMod">
    <property name="count">4</property>  <!-- 分 4 个片 -->
  </function>
</mycat:rule>
```

### 4. 客户端连接

```bash
# 像连接 MySQL 一样连接 MyCat
mysql -h 127.0.0.1 -P 8066 -u app_user -p

# 切换到逻辑库
USE order_db;

# 查询（MyCat 自动路由）
SELECT * FROM orders WHERE user_id = 100;
```

## 📊 分片算法

### 1. 取模分片

```xml
<function name="mod-long" class="io.mycat.route.function.PartitionByMod">
  <property name="count">8</property>
</function>

-- user_id = 100
-- 100 % 8 = 4
-- 路由到：orders_4
```

### 2. 范围分片

```xml
<function name="range-long" class="io.mycat.route.function.AutoPartitionByLong">
  <property name="mapFile">autopartition-long.txt</property>
</function>
```

```properties
# autopartition-long.txt
0-1000=0
1001-2000=1
2001-3000=2
3001-4000=3
```

### 3. 一致性 Hash

```xml
<function name="murmur" class="io.mycat.route.function.PartitionByMurmurHash">
  <property name="seed">0</property>
  <property name="count">8</property>
  <property name="virtualBucketTimes">160</property>
</function>
```

### 4. 按日期分片

```xml
<function name="sharding-by-month" class="io.mycat.route.function.PartitionByMonth">
  <property name="dateFormat">yyyy-MM-dd</property>
  <property name="sBeginDate">2025-01-01</property>
</function>
```

## 🔧 高级功能

### 1. 全局序列号

```sql
-- 1. 数据库方式
CREATE TABLE MYCAT_SEQUENCE (
  name VARCHAR(50) NOT NULL,
  current_value INT NOT NULL,
  increment INT NOT NULL DEFAULT 1,
  PRIMARY KEY (name)
) ENGINE=InnoDB;

-- 2. 使用序列
INSERT INTO orders (id, name) VALUES (NEXT VALUE FOR MYCATSEQ_GLOBAL, '张三');

-- 3. 自定义序列
<function name="mycat-seq" class="io.mycat.route.function.Sequence">
  <property name="fileName">mycat-seq.txt</property>
</function>
```

### 2. 读写分离

```xml
<dataHost name="dh0" balance="3" switchType="1">
  <!-- balance: 0=不读写分离, 1=写 + 2 读, 2=写 + 随机读, 3=写 + 所有读 -->
  <heartbeat>select user()</heartbeat>
  <writeHost host="master" url="192.168.1.10:3306" user="root" password="xxx">
    <readHost host="slave1" url="192.168.1.11:3306" user="root" password="xxx"/>
    <readHost host="slave2" url="192.168.1.12:3306" user="root" password="xxx"/>
  </writeHost>
</dataHost>
```

### 3. 全局表（广播表）

```xml
<!-- 每个分片都存一份，更新时会同步所有分片 -->
<table name="config" dataNode="dn0,dn1,dn2,dn3" type="global"/>
```

适用：小表、配置表、字典表

## 📈 性能数据

```
单库 MySQL：
- QPS：~5000
- 写 TPS：~2000

MyCat（4 节点 4 分片）：
- QPS：~15000（3x）
- 写 TPS：~6000（3x）
- 延迟增加：1-3ms（代理网络开销）
```

## 🔧 运维管理

### 1. 查看分片状态

```sql
-- 连接 MyCat 管理端口
mysql -h 127.0.0.1 -P 9066 -u root -p

-- 查看所有逻辑库
SHOW DATABASES;

-- 查看物理节点状态
SHOW @@DATANODE WHERE NAME="dn0";

-- 查看数据主机状态
SHOW @@DATAHOST WHERE NAME="dh0";
```

### 2. 慢查询

```xml
<!-- server.xml -->
<property name="sqlSlowTime">1000</property>  <!-- 慢查询阈值 1 秒 -->
```

```bash
# 查看慢查询日志
tail -f logs/mycat.log | grep "slow"
```

### 3. 监控

```bash
# JMX 监控（端口 9066）
# 通过 JMX 暴露指标给 Prometheus

# 关键指标：
# - mycat_network_in_pool
# - mycat_network_out_pool
# - mycat_session_count
```

## 🎯 MyCat vs ShardingSphere

| 特性 | MyCat | ShardingSphere |
|---|---|---|
| 架构 | Proxy（独立部署） | JDBC（嵌入）或 Proxy |
| 性能 | 中（多一跳） | 高（JDBC 模式） |
| 部署 | 简单 | 中等 |
| 多语言支持 | ✅（对应用透明） | JDBC 模式需 Java |
| 配置复杂度 | 中（XML） | 中（YAML） |
| 生态 | 老牌、成熟 | Apache 顶级、活跃 |
| 性能开销 | 1-3ms | < 1ms（JDBC） |

**选择建议：**
- 多语言应用、追求简单：选 MyCat
- Java 应用、追求性能：选 ShardingSphere
- 已有 MyCat 项目：继续用

## 🎯 总结

**MyCat 核心特性：**
- ✅ 代理模式（独立部署）
- ✅ 分库分表 + 读写分离
- ✅ 多语言支持（对应用透明）
- ✅ 老牌成熟方案

**配置核心：**
- server.xml：用户、逻辑库
- schema.xml：分片表、数据节点
- rule.xml：分片规则、算法

**适用场景：**
- 多语言应用
- 已有 MySQL 集群
- 需要透明的分库分表

**下一步：** [🔑 一致性 Hash 与分片键](../10-sharding/sharding-key) — 深入分片键设计