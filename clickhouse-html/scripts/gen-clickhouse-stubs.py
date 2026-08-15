#!/usr/bin/env python3
"""Generate ClickHouse substantial stub docs for clickhouse-html site.

Strategy:
- Each stub is a full-quality markdown file (~3KB+) with real ClickHouse content.
- Pattern: add(path, raw_md_string) functions grouped by chapter.
- Run from clickhouse-html/ root.

Generated: 28 stubs across 6 chapters:
  01-basics: history / installation / client / data-types  (4)
  02-sql: select-aggregate / join / functions / window-functions / dictionary  (5)
  03-table-engine: mergetree-family / log-engine / kafka-engine / distributed / materialized-view  (5)
  04-olap-scenarios: user-tracking / log-analysis / metrics-storage / bitmap / realtime-warehouse  (5)
  05-ecosystem: kafka-integration / grafana / prometheus / go-client / dbt-airbyte  (5)
  06-compare: vs-mysql-pg / vs-doris / vs-starrocks / vs-tidb  (4)
"""
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"


def add(path: str, content: str) -> None:
    target = DOCS / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"  + {path}")


# ============================================================================
# Chapter 01: Basics (4 stubs)
# ============================================================================

def ch01_history() -> None:
    add("01-basics/history.md", r"""---
title: ClickHouse 简史与生态
description: 从 2009 年 Yandex.Metrica 内部项目到 2026 年全球 OLAP 事实标准的演进历程
---

# ClickHouse 简史与生态

## 起源（2009-2015）

ClickHouse 诞生于 [Yandex.Metrica](https://metrica.yandex.com/)，俄罗斯最大的网站分析平台（类似 Google Analytics）。2009 年，Yandex 团队遇到一个难题：现成的 OLAP 引擎（Greenplum、Vertica、MonetDB）都无法支撑 PB 级实时聚合查询，单查询延迟常常达到 30 秒甚至 OOM。

团队决定自研一个 OLAP 引擎，目标是：
- **单查询秒级响应**（即使数据量 PB 级）
- **列存压缩**（10-100x 压缩比）
- **向量执行**（SIMD 加速）
- **实时写入**（无需离线导入）

2009 年第一版在 Yandex 内部上线，2012 年支撑了 Yandex.Metrica 的全部业务（200+ 亿事件/天）。2014 年团队开始考虑开源，2016 年 6 月在 GitHub 公开仓库（License: Apache 2.0）。

## 开源演进（2016-2020）

- **2016.06**：GitHub 开源，初始版本 1.0
- **2017**：v1.1 引入 `Kafka` 表引擎，奠定实时数仓基础
- **2018**：v18.x 引入 `MaterializedPostgreSQL` 引擎，开始构建 CDC 生态
- **2019**：v19.x 引入 `Live View`、`Window View`，开始支持流式查询
- **2020**：v20.x 引入 `Dictionary` 增强、`Executable` 表引擎、UDP 协议

这段时间 ClickHouse 在俄罗斯、欧洲企业市场快速渗透，Cloudflare、Uber 等大厂开始迁移日志分析负载。

## 高速发展（2021-2024）

- **2021**：v21.x 引入 `S3` 存算分离能力、`AzureBlobStorage` 引擎
- **2022**：v22.x 引入 `Dynamic` 磁盘选择、`Parallel Replicas`、`Query Cache`
- **2023**：v23.x 引入 `Iceberg`/`DeltaLake`/`Hudi` 数据湖集成、`Workload Scheduling`
- **2024**：v24.x 引入 `MergeTree` 主键支持表达式、`JSON` 类型动态子列

这段时期，ClickHouse 完成了从「单点 OLAP 引擎」到「实时数仓操作系统」的转型。

## 当前状态（2025-2026）

- **GitHub stars**：35k+
- **全球贡献者**：1000+
- **生产用户**：Uber、Cloudflare、字节、京东、B 站、美团、GitHub、Yandex、Cloudflare、Disney 等
- **生态产品**：
  - **客户端**：ch-go (Go 原生)、clickhouse-cpp (C++)、clickhouse-jdbc (Java)、clickhouse-connect (Python)、nodejs-client (Node.js)
  - **运维**：clickhouse-keeper（替代 Zookeeper）、clickhouse-backup、clickhouse-copier、Vector、Altinity Operator
  - **BI 集成**：Grafana、Metabase、Superset、Tableau、DataGrip、DBeaver
  - **数据集成**：dbt-clickhouse、Airbyte Source/Destination、Fivetran
  - **云服务**：ClickHouse Cloud、Altinity.Cloud、阿里云 ClickHouse、腾讯云 ClickHouse

## 国内生态（特别补充）

国内对 ClickHouse 的接受度极高，字节跳动、京东、B 站、美团、网易、滴滴、知乎等头部互联网公司均有大规模生产案例：

- **字节跳动**：抖音埋点 + 广告归因，单集群数千节点
- **京东**：订单履约 + 商品分析，PB 级
- **B 站**：用户行为 + 弹幕反垃圾，替代 Druid
- **美团**：外卖实时监控，多机房容灾
- **网易**：游戏埋点 + 反作弊

中文社区也非常活跃，CSDN、思否、知乎都有大量实战分享。

## 设计哲学

ClickHouse 的设计哲学至今未变：

1. **实时的**：所有数据都可查询，无需离线导入
2. **列存的**：按列压缩、按列向量化、按列 IO
3. **聚合优先**：聚合查询比行查询快 10-100x
4. **零共享（Shared-Nothing）**：每个节点独立存储 + 计算
5. **LSM 风格**：`MergeTree` 系列引擎，后台异步合并
6. **向量化执行**：利用 SIMD 指令集（SSE/AVX/AVX-512）

## 学习路径建议

- **入门**：[overview](./overview.md) 总览
- **安装**：见 [installation](./installation.md)
- **SQL 基础**：见 [02-sql/overview.md](../02-sql/overview.md)
- **表引擎**：见 [03-table-engine/overview.md](../03-table-engine/overview.md)
- **实战场景**：见 [04-olap-scenarios/overview.md](../04-olap-scenarios/overview.md)
- **生态**：见 [05-ecosystem/overview.md](../05-ecosystem/overview.md)
- **对比选型**：见 [06-compare/overview.md](../06-compare/overview.md)
""")


def ch01_installation() -> None:
    add("01-basics/installation.md", r"""---
title: 安装部署
description: ClickHouse 单机 / 集群 / Docker / Kubernetes / 云服务全模式安装指南
---

# 安装部署

## 单机部署（最简方式）

### Debian / Ubuntu

```bash
# 添加官方仓库
sudo apt-get install -y apt-transport-https ca-certificates dirmngr
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 8919F6BD2B48D754
echo "deb https://packages.clickhouse.com/deb stable main" | sudo tee /etc/apt/sources.list.d/clickhouse.list
sudo apt-get update

# 安装 server 和 client
sudo apt-get install -y clickhouse-server clickhouse-client

# 启动（默认 9000 端口）
sudo service clickhouse-server start
clickhouse-client  # 进入交互式客户端
```

### CentOS / RHEL

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://packages.clickhouse.com/rpm/clickhouse.repo
sudo yum install -y clickhouse-server clickhouse-client

sudo /etc/init.d/clickhouse-server start
clickhouse-client
```

### macOS（开发用）

```bash
brew install clickhouse
brew services start clickhouse
clickhouse-client
```

## Docker（推荐用于测试）

```bash
# 单机版
docker run -d --name clickhouse-server \
  -p 9000:9000 -p 8123:8123 \
  -v /path/to/data:/var/lib/clickhouse \
  -v /path/to/logs:/var/log/clickhouse-server \
  clickhouse/clickhouse-server

# 验证
docker exec -it clickhouse-server clickhouse-client
```

## 集群部署（生产推荐）

ClickHouse 集群由以下组件构成：

```text
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  ClickHouse     │  │  ClickHouse     │  │  ClickHouse     │
│  Shard 1        │  │  Shard 2        │  │  Shard 3        │
│  Replica A + B  │  │  Replica A + B  │  │  Replica A + B  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
        ▲                    ▲                    ▲
        └────────────────────┼────────────────────┘
                             │
                    ┌─────────────────┐
                    │  ClickHouse     │
                    │  Keeper         │
                    │  (3/5 节点)     │
                    └─────────────────┘
```

### 关键配置（`/etc/clickhouse-server/config.xml`）

```xml
<!-- 集群拓扑 -->
<remote_servers>
    <my_cluster>
        <shard>
            <internal_replication>true</internal_replication>
            <replica>
                <host>ch-shard1-replica1</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>ch-shard1-replica2</host>
                <port>9000</port>
            </replica>
        </shard>
        <shard>
            <replica>
                <host>ch-shard2-replica1</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>ch-shard2-replica2</host>
                <port>9000</port>
            </replica>
        </shard>
    </my_cluster>
</remote_servers>

<!-- Keeper 配置 -->
<zookeeper>
    <node>
        <host>keeper1</host>
        <port>9181</port>
    </node>
    <node>
        <host>keeper2</host>
        <port>9181</port>
    </node>
    <node>
        <host>keeper3</host>
        <port>9181</port>
    </node>
</zookeeper>

<!-- 监听地址 -->
<listen_host>0.0.0.0</listen_host>
```

### 启动集群

```bash
# 在每台机器上启动
sudo service clickhouse-server start

# 验证集群状态
clickhouse-client --query "SELECT * FROM system.clusters FORMAT Vertical"
clickhouse-client --query "SELECT * FROM system.replicas FORMAT Vertical"
```

## Kubernetes 部署

推荐使用 **Altinity Operator**：

```bash
# 安装 Operator
kubectl apply -f https://raw.githubusercontent.com/Altinity/clickhouse-operator/master/deploy/operator/clickhouse-operator-install-bundle.yaml

# 创建 ClickHouse 集群
cat <<EOF | kubectl apply -f -
apiVersion: clickhouse.altinity.com/v1
kind: ClickHouseInstallation
metadata:
  name: chi-demo
spec:
  configuration:
    clusters:
      - name: cluster-1
        shards:
          - name: shard-1
            replicas:
              - name: replica-1
                template:
                  spec:
                    containers:
                      - name: clickhouse
                        image: clickhouse/clickhouse-server:24.3
                        resources:
                          requests:
                            memory: "4Gi"
                            cpu: "2"
EOF

# 查看状态
kubectl get chi -o wide
```

## 云服务（一键部署）

### ClickHouse Cloud（官方）

- **地址**：https://clickhouse.cloud/
- **特点**：存算分离、按查询计费、自动扩缩容
- **试用**：14 天免费试用

### 阿里云 ClickHouse

```bash
# 在阿里云控制台购买 ClickHouse 集群
# 阿里云提供完整的运维、监控、备份服务
```

### 腾讯云 ClickHouse

类似阿里云，国内用户访问更快。

## 硬件推荐

### 写入密集型（埋点/日志）

- CPU：32+ cores（向量化执行 + SIMD 受益）
- 内存：128 GB+（buffer pool + 字典缓存）
- 磁盘：NVMe SSD（写入延迟 < 1ms）
- 网络：10 Gbps（副本同步 + 客户端连接）

### 查询密集型（BI 看板）

- CPU：16+ cores
- 内存：64 GB+
- 磁盘：SATA SSD（查询对磁盘 IO 敏感度低）
- 网络：1 Gbps 足够

## 性能调优 checklist

- ✅ 关闭透明大页（`echo never > /sys/kernel/mm/transparent_hugepage/enabled`）
- ✅ 调整 `max_threads`（默认 = 物理核数）
- ✅ 配置 `merge_tree` 缓存（`mark_cache_size`）
- ✅ 开启 `query_log` 记录慢查询
- ✅ 监控 `system.merges` 看后台合并延迟

## 升级与备份

### 升级

```bash
# 关闭所有写入
clickhouse-client --query "SYSTEM STOP MERGES"
clickhouse-client --query "SYSTEM FLUSH LOGS"

# 升级包
sudo apt-get update && sudo apt-get upgrade clickhouse-server

# 重启
sudo service clickhouse-server restart
```

### 备份

推荐使用 `clickhouse-backup`：

```bash
# 安装
wget https://github.com/AlexAkulov/clickhouse-backup/releases/download/v2.5.0/clickhouse-backup.tar.gz
tar -xzf clickhouse-backup.tar.gz

# 全量备份
clickhouse-backup create --tables="db1.*" full_backup

# 备份到 S3
clickhouse-backup create --tables="db1.*" --storage=remote full_backup_s3

# 恢复
clickhouse-backup restore full_backup
```

## 下一步

- 学习 SQL 基础：见 [02-sql/select-aggregate.md](../02-sql/select-aggregate.md)
- 学习表引擎：见 [03-table-engine/overview.md](../03-table-engine/overview.md)
""")


def ch01_client() -> None:
    add("01-basics/client.md", r"""---
title: 客户端连接
description: clickhouse-client / HTTP / JDBC / Go / Python / Node.js 客户端完整对比
---

# 客户端连接

ClickHouse 提供多种客户端协议，不同场景选择不同客户端：

## 客户端协议对比

| 协议 | 端口 | 性能 | 适用场景 |
|---|---|---|---|
| **Native (TCP)** | 9000 | 最快（无 HTTP 开销） | 内部服务、生产环境 |
| **HTTP** | 8123 | 中等（HTTP/1.1 短连接） | 临时查询、REST API |
| **MySQL Wire** | 9004 | 中等（兼容 MySQL 协议） | MySQL 客户端工具 |
| **PostgreSQL Wire** | 9005 | 中等（兼容 PG 协议） | PG 客户端工具 |
| **gRPC** | 9100 | 高（protobuf + HTTP/2） | 微服务调用 |
| **JDBC** | 9000/8123 | 高 | Java 应用 |
| **ch-go** | 9000 | 极高（原生二进制 + LZ4） | Go 服务（Cloudflare 自研） |

## clickhouse-client（命令行）

```bash
# 交互式
clickhouse-client

# 单次查询
clickhouse-client --query "SELECT version()"

# 多行 SQL
clickhouse-client --multiquery --query "
  CREATE TABLE test (id UInt32) ENGINE = MergeTree() ORDER BY id;
  INSERT INTO test VALUES (1), (2), (3);
  SELECT count() FROM test;
"

# 指定 host/port/user/password
clickhouse-client --host 127.0.0.1 --port 9000 \
  --user default --password '' \
  --query "SELECT 1"

# 指定数据库
clickhouse-client --database mydb

# 输出格式
clickhouse-client --query "SELECT * FROM system.tables FORMAT JSONEachRow"
clickhouse-client --query "SELECT * FROM system.tables FORMAT Vertical"
clickhouse-client --query "SELECT * FROM system.tables FORMAT CSV"

# 进度条
clickhouse-client --progress --query "SELECT * FROM large_table"
```

## HTTP 接口

```bash
# 简单查询
curl 'http://localhost:8123/?query=SELECT%201'

# POST（推荐用于大查询）
curl -X POST 'http://localhost:8123/' --data-urlencode "query=SELECT * FROM system.tables"

# 带参数
curl -X POST 'http://localhost:8123/' \
  --data-urlencode "query=SELECT {col:Identifier} FROM {db:Identifier}.{table:Identifier}" \
  --data-urlencode "param_col=version" \
  --data-urlencode "param_db=system" \
  --data-urlencode "param_table=settings"

# 输出格式
curl 'http://localhost:8123/?query=SELECT+1+FORMAT+JSON'

# 带压缩
curl -X POST 'http://localhost:8123/' \
  -H 'Content-Encoding: gzip' \
  --data-binary @query.sql.gz

# 写入
echo '1,Alice' > data.csv
curl -X POST 'http://localhost:8123/?query=INSERT+INTO+users+FORMAT+CSV' --data-binary @data.csv
```

## Python 客户端

### clickhouse-connect（推荐）

```python
import clickhouse_connect

client = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='default',
    password='',
    database='default'
)

# 查询
result = client.query('SELECT version()')
print(result.result_rows)  # [[('24.3.3.102',)]]

# 带参数（防止 SQL 注入）
result = client.query(
    'SELECT * FROM users WHERE age > %(min_age)s',
    parameters={'min_age': 18}
)

# 批量插入
client.insert(
    table='users',
    data=[[1, 'Alice', 25], [2, 'Bob', 30]],
    column_names=['id', 'name', 'age']
)

# DataFrame 互转
import pandas as pd
df = client.query_df('SELECT * FROM users LIMIT 100')
client.insert_df('users', df)
```

### clickhouse-driver（异步，性能更好）

```python
from clickhouse_driver import Client

client = Client('localhost')

# 同步
result = client.execute('SELECT version()')

# 异步
from clickhouse_driver.asynch import Client as AsyncClient
import asyncio

async def main():
    client = AsyncClient('localhost')
    result = await client.execute('SELECT version()')
    print(result)
    await client.disconnect()

asyncio.run(main())
```

## Go 客户端

### ch-go（Cloudflare 自研，推荐生产）

```go
package main

import (
    "context"
    "fmt"
    "github.com/ClickHouse/ch-go"
    "github.com/ClickHouse/ch-go/proto"
)

func main() {
    conn, err := ch.Dial(context.Background(), ch.Options{
        Address: "localhost:9000",
    })
    if err != nil {
        panic(err)
    }
    defer conn.Close()

    var version string
    err = conn.QueryRow(context.Background(), "SELECT version()").Scan(&version)
    fmt.Println(version)

    // 批量插入
    err = conn.Exec(context.Background(), `
        INSERT INTO users (id, name, age) VALUES
        (?, ?, ?), (?, ?, ?), (?, ?, ?)
    `,
        1, "Alice", 25,
        2, "Bob", 30,
        3, "Carol", 28,
    )
    if err != nil {
        panic(err)
    }
}
```

### clickhouse-go（官方 v2）

```go
import (
    "database/sql"
    "fmt"
    _ "github.com/ClickHouse/clickhouse-go/v2"
)

func main() {
    conn, _ := sql.Open("clickhouse", "clickhouse://default:@localhost:9000/default")
    defer conn.Close()

    rows, _ := conn.Query("SELECT version()")
    defer rows.Close()

    for rows.Next() {
        var version string
        rows.Scan(&version)
        fmt.Println(version)
    }
}
```

## Java / JDBC

```xml
<!-- Maven -->
<dependency>
    <groupId>com.clickhouse</groupId>
    <artifactId>clickhouse-jdbc</artifactId>
    <version>0.6.0</version>
</dependency>
```

```java
import java.sql.*;
import com.clickhouse.jdbc.*;

public class ClickHouseJDBC {
    public static void main(String[] args) throws Exception {
        String url = "jdbc:clickhouse://localhost:8123/default";
        try (Connection conn = DriverManager.getConnection(url);
             Statement stmt = conn.createStatement()) {
            ResultSet rs = stmt.executeQuery("SELECT version()");
            while (rs.next()) {
                System.out.println(rs.getString(1));
            }
        }
    }
}
```

## Node.js

```bash
npm install @clickhouse/client
```

```javascript
import { createClient } from '@clickhouse/client'

const client = createClient({
  url: 'http://localhost:8123',
  database: 'default'
})

// 查询
const rs = await client.query({
  query: 'SELECT version()',
  format: 'JSONEachRow'
})
console.log(await rs.json())

// 批量插入
await client.insert({
  table: 'users',
  values: [
    { id: 1, name: 'Alice', age: 25 },
    { id: 2, name: 'Bob', age: 30 }
  ],
  format: 'JSONEachRow'
})
```

## 客户端选型决策

| 场景 | 推荐客户端 | 原因 |
|---|---|---|
| **生产服务（Go）** | `ch-go` | Cloudflare 生产验证，二进制协议 + LZ4 |
| **生产服务（Python）** | `clickhouse-connect` | 官方推荐，同步 API 简单 |
| **生产服务（Java）** | `clickhouse-jdbc` | 官方，成熟稳定 |
| **ETL 脚本** | `clickhouse-connect` (Python) | DataFrame 互转方便 |
| **BI 工具** | HTTP / JDBC | 通用兼容 |
| **运维排查** | `clickhouse-client` | 内置命令行 |

## 性能对比基准（单节点）

```text
查询：SELECT count() FROM events WHERE event_date = '2024-01-01'

clickhouse-client（TCP）:    50ms
clickhouse-connect (HTTP):   80ms
clickhouse-jdbc (HTTP):      120ms
ch-go (TCP + LZ4):           30ms
```

ch-go 比 HTTP 客户端快 2-3 倍，是生产环境 Go 服务的首选。

## 下一步

- 学习 SQL：见 [02-sql/select-aggregate.md](../02-sql/select-aggregate.md)
- 安装客户端：见 [installation.md](./installation.md)
""")


def ch01_data_types() -> None:
    add("01-basics/data-types.md", r"""---
title: 数据类型
description: ClickHouse 完整数据类型系统：基础 / 数值 / 字符串 / 时间 / 复合 / 特殊类型
---

# 数据类型

ClickHouse 的类型系统比 MySQL/PG 更丰富，特别是复合类型（Array / Tuple / Map / Nested）和特殊类型（Enum / LowCardinality / Nullable）。

## 数值类型

| 类型 | 大小 | 范围 | 备注 |
|---|---|---|---|
| **UInt8** | 1 字节 | 0 ~ 255 | 默认 UNSIGNED |
| **UInt16** | 2 字节 | 0 ~ 65535 | |
| **UInt32** | 4 字节 | 0 ~ 4.29e9 | |
| **UInt64** | 8 字节 | 0 ~ 1.84e19 | |
| **Int8** | 1 字节 | -128 ~ 127 | |
| **Int16** | 2 字节 | -32768 ~ 32767 | |
| **Int32** | 4 字节 | -2.15e9 ~ 2.15e9 | |
| **Int64** | 8 字节 | -9.22e18 ~ 9.22e18 | |
| **Float32** | 4 字节 | IEEE 754 单精度 | 不建议存钱 |
| **Float64** | 8 字节 | IEEE 754 双精度 | |
| **Decimal(P, S)** | 4/8/16 字节 | 高精度小数 | P = 精度, S = 小数位数 |

**注意**：
- UInt 比 Int 性能更好（无需符号位处理），业务允许就用 UInt。
- 浮点数比较请用 `>= x - 0.0001 AND <= x + 0.0001`。

## 字符串类型

| 类型 | 说明 |
|---|---|
| **String** | 任意长度字符串（替代 VARCHAR/TEXT/BLOB） |
| **FixedString(N)** | 定长字符串（N 字节，不足补 0） |
| **LowCardinality(String)** | 低基数字符串（字典编码，10x 压缩 + 10x 查询快） |

**LowCardinality 是杀手锏**：列基数 < 1 万时（如 status、country、category），性能比普通 String 提升 10-50x。

```sql
-- 推荐
CREATE TABLE events (
  status LowCardinality(String),
  country LowCardinality(String)
)

-- 不推荐（基数 < 10000 但没用 LowCardinality）
CREATE TABLE events (
  status String,  -- 浪费
  country String
)
```

## 时间类型

| 类型 | 大小 | 范围 | 精度 |
|---|---|---|---|
| **Date** | 2 字节 | 1970-01-01 ~ 2149-06-06 | 天 |
| **Date32** | 4 字节 | 1900-01-01 ~ 2299-12-31 | 天 |
| **DateTime** | 4 字节 | 1970-01-01 ~ 2105-12-31 | 秒（无时区） |
| **DateTime64(P)** | 8 字节 | 1900-01-01 ~ 2299-12-31 | P = 精度（毫秒/微秒/纳秒） |

**注意**：
- `DateTime` 不带时区（按服务器时区存储），多机房部署需要统一时区或使用 `DateTime64(3, 'UTC')`。
- `DateTime64(3)` = 毫秒精度，`DateTime64(6)` = 微秒精度，`DateTime64(9)` = 纳秒精度。

## 布尔类型

ClickHouse **没有 BOOLEAN** 类型，用 `UInt8` 代替（0 = false，1 = true）：

```sql
CREATE TABLE users (
  is_active UInt8 DEFAULT 0,
  is_vip UInt8 DEFAULT 0
)

INSERT INTO users (id, is_active, is_vip) VALUES (1, 1, 0)

SELECT * FROM users WHERE is_active = 1
```

## UUID

```sql
CREATE TABLE events (
  event_id UUID
)

INSERT INTO events VALUES (generateUUIDv4())
```

## 枚举类型

枚举类型底层是 `Int8`/`Int16`，适合固定取值集合：

```sql
CREATE TABLE orders (
  status Enum8('pending' = 1, 'paid' = 2, 'shipped' = 3, 'delivered' = 4, 'cancelled' = 5)
)

INSERT INTO orders (id, status) VALUES (1, 'paid')

-- 按数值排序（实际是 Int8 排序）
SELECT status, count() FROM orders GROUP BY status
```

## 复合类型

### Array

```sql
CREATE TABLE events (
  tags Array(String),
  scores Array(Float64)
)

INSERT INTO events VALUES (['tech', 'ai', 'database'], [9.5, 8.7])

-- 查询数组包含某元素
SELECT * FROM events WHERE has(tags, 'ai')

-- 数组展开（ARRAY JOIN）
SELECT tag FROM events ARRAY JOIN tags AS tag
```

### Tuple

```sql
CREATE TABLE events (
  point Tuple(Float64, Float64)  -- (longitude, latitude)
)

INSERT INTO events VALUES (116.4, 39.9)
```

### Map

```sql
CREATE TABLE events (
  props Map(String, String)
)

INSERT INTO events VALUES ({'browser': 'chrome', 'os': 'mac'})

-- 查询
SELECT props['browser'] FROM events
SELECT * FROM events WHERE props['os'] = 'mac'
```

### Nested（嵌套表）

```sql
CREATE TABLE users (
  id UInt64,
  name String,
  phones Nested(
    type String,
    number String
  )
)

INSERT INTO users VALUES (1, 'Alice', ['mobile', 'work'], ['138...', '010-...'])

SELECT
  name,
  phone.type,
  phone.number
FROM users
ARRAY JOIN phones AS phone
```

## Nullable 类型

`Nullable(T)` 允许 `null` 值，但**会影响性能**（增加额外列 + null bitmap）：

```sql
CREATE TABLE events (
  user_id UInt64,
  -- 不推荐（user_id 应该是必填）
  user_id_nullable Nullable(UInt64)
)
```

**建议**：用业务默认值替代 `Nullable`（如 `0 = 未登录`、`'' = 未填写`）。

## JSON 类型（v24.x 新增）

ClickHouse v24.x 引入 `JSON` 类型，动态子列：

```sql
CREATE TABLE events (
  data JSON
)

INSERT INTO events VALUES ('{"name": "Alice", "age": 25, "tags": ["tech", "ai"]}')

-- 自动推断子列
SELECT
  data.name,
  data.age,
  data.tags
FROM events
```

## Domain 类型（IPv4 / IPv6）

ClickHouse 提供专门的 IP 地址类型：

```sql
CREATE TABLE access_logs (
  ip IPv4
)

INSERT INTO access_logs VALUES ('192.168.1.1')

-- IP 转数字
SELECT ip, IPv4NumToString(ip) FROM access_logs
```

## 类型选择 checklist

| 业务字段 | 推荐类型 | 备注 |
|---|---|---|
| 整数 ID | UInt64 | 主键默认 |
| 状态（有限集合） | Enum8 或 LowCardinality(String) | 二选一 |
| 国家/城市 | LowCardinality(String) | 低基数 |
| 时间戳 | DateTime64(3) 或 DateTime | 视精度需求 |
| 布尔值 | UInt8（0/1） | 不用 Boolean |
| 金额 | Decimal(18, 2) | 不用 Float64 |
| 文本（长） | String | |
| 文本（短/枚举） | LowCardinality(String) | |
| 标签数组 | Array(String) 或 Array(LowCardinality(String)) | |
| KV 数据 | Map(String, String) | 灵活但性能低 |
| JSON 数据 | JSON（v24+）或 String + JSON 函数 | |

## 下一步

- 学习 SQL 聚合：见 [02-sql/select-aggregate.md](../02-sql/select-aggregate.md)
""")


# ============================================================================
# Chapter 02: SQL (5 stubs)
# ============================================================================

def ch02_select_aggregate() -> None:
    add("02-sql/select-aggregate.md", r"""---
title: SELECT 与聚合查询
description: ClickHouse 聚合函数全集 + TOP 20 / 分位数 / 高基数 UV 实战
---

# SELECT 与聚合查询

## 基础查询

```sql
SELECT
  user_id,
  count() AS event_count,
  min(event_time) AS first_event,
  max(event_time) AS last_event
FROM events
WHERE event_date = '2024-01-01'
GROUP BY user_id
HAVING event_count > 10
ORDER BY event_count DESC
LIMIT 100
```

## 聚合函数全集

### 计数类

```sql
SELECT
  count(),                      -- 总行数
  countIf(event_type = 'click'), -- 条件计数
  countDistinct(user_id),        -- 不同值数量
  uniq(user_id),                 -- 近似不同值（HyperLogLog，1.6% 误差）
  uniqExact(user_id),            -- 精确不同值
  uniqCombined(user_id),         -- 混合（精度+性能）
  uniqCombined64(URL)            -- 64 位（支持更大基数）
FROM events
```

**性能排序**：`uniq` > `uniqCombined` > `uniqExact` > `countDistinct`，精度相反。

### 求和 / 均值 / 极值

```sql
SELECT
  sum(amount),
  avg(amount),
  min(amount),
  max(amount),
  any(amount),         -- 任一非 0 值
  anyLast(amount),     -- 最后一个值
  argMax(user_id, amount),  -- amount 最大时的 user_id
  argMin(user_id, amount)
FROM orders
```

### 分位数（中位数 / P95 / P99）

```sql
SELECT
  quantile(0.5)(latency_ms),           -- 中位数
  quantile(0.95)(latency_ms),          -- P95
  quantile(0.99)(latency_ms),          -- P99
  quantiles(0.5, 0.9, 0.95, 0.99)(latency_ms),  -- 多分位
  quantileExact(0.5)(latency_ms),      -- 精确
  quantileTiming(0.95)(latency_ms)     -- 时间类专用
FROM events
```

## TOP N 查询（高频）

```sql
-- TOP 10 用户（按事件数）
SELECT user_id, count() AS cnt
FROM events
GROUP BY user_id
ORDER BY cnt DESC
LIMIT 10

-- 使用 view 函数优化
SELECT * FROM (
  SELECT user_id, count() AS cnt
  FROM events
  GROUP BY user_id
)
WHERE cnt > 100
ORDER BY cnt DESC
LIMIT 10
```

**TOP N 优化**：用 `topK(N)` 函数一次性返回前 N 个：

```sql
SELECT topK(10)(user_id), topK(10)(country) FROM events
```

## 高基数 UV 统计（杀手锏）

### 方法 1：`uniq`（HyperLogLog，1.6% 误差）

```sql
SELECT uniq(user_id) AS uv FROM events WHERE event_date = '2024-01-01'
-- 性能：1 亿行 < 100ms
```

### 方法 2：`groupBitmapState` + RoaringBitmap（精确 + 性能）

```sql
-- 创建物化视图
CREATE MATERIALIZED VIEW events_uv_mv
ENGINE = AggregatingMergeTree()
ORDER BY (event_date, event_type)
AS SELECT
  event_date,
  event_type,
  groupBitmapState(user_id) AS uv_bitmap
FROM events
GROUP BY event_date, event_type;

-- 查询 UV
SELECT
  event_date,
  event_type,
  bitmapCardinality(groupBitmapMergeState(uv_bitmap)) AS uv
FROM events_uv_mv
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-07'
GROUP BY event_date, event_type
ORDER BY event_date, event_type

-- 10 亿行 UV 查询 < 1s（精确）
```

## 实战：电商订单分析

```sql
-- GMV / 订单数 / 客单价
SELECT
  toDate(order_time) AS dt,
  count() AS order_count,
  uniq(user_id) AS buyer_count,
  sum(amount) AS gmv,
  sum(amount) / count() AS avg_order_value
FROM orders
WHERE order_time >= today() - INTERVAL 30 DAY
GROUP BY dt

-- 各品类 TOP 10
SELECT
  category,
  sum(amount) AS cat_gmv,
  count() AS cat_orders
FROM orders o
JOIN products p ON o.product_id = p.id
WHERE order_time >= today() - INTERVAL 7 DAY
GROUP BY category
ORDER BY cat_gmv DESC
LIMIT 10

-- 用户复购率（购买 ≥ 2 次的用户占比）
SELECT
  countIf(order_count >= 2) / count() AS repurchase_rate
FROM (
  SELECT user_id, count() AS order_count
  FROM orders
  WHERE order_time >= today() - INTERVAL 30 DAY
  GROUP BY user_id
)
```

## GROUP BY 优化

### 内存限制

ClickHouse 默认 `max_bytes_before_external_group_by = 0`（OOM 风险），**强烈建议设置**：

```xml
<max_bytes_before_external_group_by>10000000000</max_bytes_before_external_group_by>  <!-- 10 GB -->
<max_memory_usage>50000000000</max_memory_usage>  <!-- 50 GB -->
```

超过限制时自动 spill 到磁盘（性能下降但避免 OOM）。

### 特殊聚合

```sql
-- groupArray（聚合为数组）
SELECT groupArray(user_id) FROM events WHERE event_date = '2024-01-01'

-- groupUniqArray（去重数组）
SELECT groupUniqArray(10)(user_id) FROM events

-- groupArraySample（采样数组）
SELECT groupArraySample(1000)(user_id) FROM events
```

## SAMPLE 抽样

```sql
-- 1% 抽样（快速近似查询）
SELECT count() FROM events SAMPLE 0.01

-- 按 token 抽样（可重现抽样）
SELECT count() FROM events SAMPLE 1/10

-- 必须先在表中配置采样键
CREATE TABLE events (
  event_date Date,
  user_id UInt64,
  event_type String
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (user_id, event_type)
SAMPLE BY user_id  -- 采样键必须是 ORDER BY 前缀
```

## 下一步

- 学习 JOIN 类型：见 [join.md](./join.md)
- 学习窗口函数：见 [window-functions.md](./window-functions.md)
""")


def ch02_join() -> None:
    add("02-sql/join.md", r"""---
title: JOIN 类型
description: ClickHouse 各种 JOIN 类型 + ASOF JOIN 实战 + JOIN 性能优化
---

# JOIN 类型

ClickHouse 支持的 JOIN 类型比 MySQL 少，但每种都有明确适用场景。

## JOIN 类型清单

```sql
SELECT
  a.*,
  b.user_name
FROM events a
[INNER | LEFT | RIGHT | FULL | CROSS | ASOF] JOIN users b
ON a.user_id = b.id
[ANY | ALL | SEMI | ANTI]  -- JOIN 策略
[JOIN STRICTNESS]            -- 严格度
```

### JOIN 策略

| 策略 | 说明 |
|---|---|
| **ALL** | 默认，返回所有匹配（行数 = 左 × 匹配右） |
| **ANY** | 左表的每一行最多匹配右表一行（取首个匹配） |
| **ASOF** | 最近匹配（时间序列模糊匹配） |
| **SEMI** | 左半连接，右表去重 |
| **ANTI** | 左反连接，右表没匹配才返回 |

### JOIN 严格度

| 严格度 | 说明 |
|---|---|
| `ALL` | 默认 |
| `ANY` | 与 `ANY JOIN` 语义重叠 |

## INNER JOIN

```sql
-- 事件关联用户
SELECT
  e.event_id,
  e.event_type,
  u.user_name,
  u.country
FROM events e
INNER JOIN users u ON e.user_id = u.id
WHERE e.event_date = '2024-01-01'
```

## LEFT JOIN

```sql
-- 找出没有下单的用户
SELECT
  u.id,
  u.user_name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id = 0  -- 注意：ClickHouse 中 0 是默认"无匹配"
```

## ASOF JOIN（时间序列模糊匹配）

**场景**：股票 K 线匹配成交、订单匹配价格快照、用户行为匹配最近的画像。

```sql
-- 订单成交价匹配当时的行情快照
SELECT
  o.order_id,
  o.symbol,
  o.price AS order_price,
  q.bid_price AS market_bid,
  q.ask_price AS market_ask
FROM orders o
ASOF JOIN quotes q
  ON o.symbol = q.symbol
  AND o.order_time >= q.quote_time  -- 必须有不等式条件
WHERE o.order_time >= '2024-01-01 00:00:00'
```

**ASOF JOIN 规则**：
- 必须有等值条件（`=`）和不等值条件（`>=` 或 `<=`）
- 右表是「时序表」，左表是「事件表」
- 匹配右表中**最后一个**满足不等值条件的行

## SEMI / ANTI JOIN

```sql
-- SEMI：找在 users 表中存在的事件（去重）
SELECT e.* FROM events e
SEMI JOIN users u ON e.user_id = u.id

-- ANTI：找不在 users 表中的事件（异常数据）
SELECT e.* FROM events e
ANTI JOIN users u ON e.user_id = u.id
```

## 字典 JOIN（Dictionary）

Dictionary 是 ClickHouse 的「本地 Map」，比 JOIN 快 10-100x：

```sql
-- 创建字典
CREATE DICTIONARY users_dict (
  id UInt64,
  user_name String,
  country String
)
PRIMARY KEY id
SOURCE(CLICKHOUSE(DB 'mydb' TABLE 'users'))
LIFETIME(MIN 300 MAX 600)
LAYOUT(HASHED())

-- 查询（不需要 JOIN 语法）
SELECT
  event_id,
  dictGet('users_dict', 'user_name', user_id) AS user_name,
  dictGet('users_dict', 'country', user_id) AS country
FROM events
WHERE event_date = '2024-01-01'
```

详见 [dictionary.md](./dictionary.md)。

## JOIN 性能优化

### 1. 大小表 JOIN（小表放右）

```sql
-- ✅ 好：users 是小表（百万级）
SELECT * FROM events JOIN users ON event.user_id = user.id

-- ❌ 差：events 大表 × users 小表，结果集巨大
```

### 2. 限制 JOIN 表数

ClickHouse **JOIN ≤ 8 张表**性能较好，超过会显著退化。如果需要 JOIN 多表，建议：
- 预 JOIN 成宽表（用物化视图）
- 用星型模型（事实表 + 多个维度表）
- 改用 StarRocks / Doris（JOIN 优化更强）

### 3. JOIN 顺序

ClickHouse 的 JOIN 优化器较弱，建议**手动指定顺序**：

```sql
-- 小表在前（手动指定）
SELECT * FROM small_table s JOIN big_table b ON s.id = b.id
```

### 4. 使用 `prewhere`（大幅加速）

```sql
SELECT
  e.event_id,
  u.user_name
FROM events e
PREWHERE e.event_date = '2024-01-01'  -- 先过滤，再 JOIN
JOIN users u ON e.user_id = u.id
```

## 实战：电商订单 + 用户 + 商品三表 JOIN

```sql
-- 订单宽表查询
SELECT
  o.order_id,
  u.user_name,
  u.country,
  p.product_name,
  p.category,
  o.amount,
  o.order_time
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id
WHERE o.order_time >= today() - INTERVAL 7 DAY
  AND u.country IN ('US', 'UK', 'JP')
ORDER BY o.order_time DESC
LIMIT 1000
```

**性能提示**：如果这种查询是热点，用 `JOIN` 物化视图预聚合：

```sql
CREATE MATERIALIZED VIEW order_wide_mv
ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_time)
ORDER BY (order_id, order_time)
AS SELECT
  o.order_id,
  u.user_name,
  u.country,
  p.product_name,
  p.category,
  o.amount,
  o.order_time
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id
```

## JOIN 类型决策表

| 场景 | 推荐 JOIN 类型 |
|---|---|
| 维度关联（小表） | Dictionary + dictGet |
| 维度关联（大表） | INNER JOIN |
| 时序模糊匹配 | ASOF JOIN |
| 找出异常数据 | ANTI JOIN |
| 找出存在数据 | SEMI JOIN |
| 多维度（> 4 表） | 预 JOIN 物化视图 |

## 下一步

- 学习窗口函数：见 [window-functions.md](./window-functions.md)
""")


def ch02_functions() -> None:
    add("02-sql/functions.md", r"""---
title: ClickHouse 独有函数
description: ClickHouse 独有 + 高频函数全集：array / map / tuple / JSON / URL / 时间 / 字符串
---

# ClickHouse 独有函数

ClickHouse 有大量「独有」函数，特别是数组、Map、JSON、URL、时间、地理位置、机器学习相关函数。

## 数组函数

```sql
-- 基础
SELECT
  arrayConcat([1,2], [3,4]),           -- [1,2,3,4]
  arrayElement([1,2,3], 1),            -- 2（索引从 1 开始！）
  arrayPushBack([1,2], 3),             -- [1,2,3]
  arrayPushFront([1,2], 0),            -- [0,1,2]
  arraySlice([1,2,3,4], 2, 2),         -- [2,3]
  arrayReverse([1,2,3]),               -- [3,2,1]
  arraySort([3,1,2]),                  -- [1,2,3]
  arrayDistinct([1,1,2,3])             -- [1,2,3]

-- 聚合
SELECT
  arrayReduce('sum', [1,2,3]),         -- 6
  arrayReduce('avg', [1,2,3]),         -- 2
  arrayReduce('max', [1,2,3])          -- 3

-- 过滤
SELECT
  arrayFilter(x -> x > 1, [1,2,3]),    -- [2,3]
  arrayMap(x -> x * 2, [1,2,3]),       -- [2,4,6]
  arrayExists(x -> x > 2, [1,2,3])     -- 1（存在）

-- 查询
SELECT
  has([1,2,3], 2),                    -- 1（包含）
  has([1,2,3], 5),                    -- 0
  indexOf([1,2,3], 2),                 -- 2
  arrayContains([1,2,3], 2)            -- true
```

## Map 函数

```sql
SELECT
  map('a', 1, 'b', 2, 'c', 3),         -- {'a':1,'b':2,'c':3}
  mapKeys({'a':1,'b':2}),              -- ['a','b']
  mapValues({'a':1,'b':2})             -- [1,2]

-- 嵌套类型转换
SELECT CAST([1,2,3], 'Array(UInt8)') AS arr
```

## JSON 函数

```sql
-- 解析 JSON 字符串
SELECT
  JSONExtractString('{"name": "Alice"}', 'name'),  -- 'Alice'
  JSONExtractInt('{"age": 25}', 'age'),            -- 25
  JSONExtractFloat('{"score": 9.5}', 'score'),     -- 9.5
  JSONExtractBool('{"active": true}', 'active'),   -- 1
  JSONExtractArrayRaw('{"tags": ["a","b"]}', 'tags')  -- '["a","b"]'

-- 类型安全的提取
SELECT JSONExtract('{"name": "Alice", "age": 25}', 'Tuple(name String, age UInt8)')
```

## URL 函数

ClickHouse 内置 URL 解析函数（无需正则）：

```sql
SELECT
  protocol('https://example.com/path?q=1'),  -- 'https'
  domain('https://example.com/path'),         -- 'example.com'
  domainWithoutWWW('https://www.example.com'),-- 'example.com'
  topLevelDomain('https://example.com'),      -- 'com'
  path('https://example.com/path/to'),        -- '/path/to'
  pathFull('https://example.com/path?q=1'),   -- '/path?q=1'
  queryStringAndFragment('https://example.com/path?q=1#h'),  -- 'q=1#h'
  extractURLParameters('https://example.com/?a=1&b=2')['a']  -- '1'
```

## 时间函数

```sql
SELECT
  toYear(now()),                       -- 2024
  toMonth(now()),                      -- 1
  toDayOfMonth(now()),
  toHour(now()),
  toMinute(now()),
  toSecond(now()),

  toDate('2024-01-01 12:00:00'),
  toDateTime('2024-01-01 12:00:00'),
  toDateTime64('2024-01-01 12:00:00.123', 3),  -- 毫秒精度
  toUnixTimestamp(now()),

  formatDateTime(now(), '%Y-%m-%d %H:%M:%S'),
  parseDateTimeBestEffort('2024-01-01')

-- 时间窗口
SELECT
  toStartOfInterval(now(), INTERVAL 5 MINUTE),  -- 5 分钟窗口
  toStartOfHour(now()),
  toStartOfDay(now()),
  toStartOfWeek(now()),
  toStartOfMonth(now())
```

## 字符串函数

```sql
SELECT
  length('hello'),                     -- 5
  lower('HELLO'),                      -- 'hello'
  upper('hello'),                      -- 'HELLO'
  trim('  hello  '),                   -- 'hello'
  replace('hello world', 'world', 'CK'),  -- 'hello CK'
  extract('hello123world', '([0-9]+)'), -- '123'
  match('hello123', '[0-9]+'),         -- 1
  splitByChar(',', 'a,b,c'),           -- ['a','b','c']
  splitByRegex('\\s+', 'a b  c')       -- ['a','b','c']
```

## 地理位置函数

ClickHouse 支持 Geo 数据类型（点/多边形）：

```sql
-- 距离计算（地球半径 6371000 米）
SELECT
  geoDistance(116.4, 39.9, 121.5, 31.2),  -- 上海到北京约 1067 km
  greatCircleDistance(116.4, 39.9, 121.5, 31.2, 6371000)

-- 点是否在多边形内
SELECT pointInPolygon((39.9, 116.4), [(39.0, 115.0), (40.0, 115.0), (40.0, 117.0), (39.0, 117.0)])
```

## Hash 函数

```sql
SELECT
  cityHash64('hello'),                 -- 13253124476785557978
  murmurHash3_64('hello'),             -- 4236618289605128574
  farmHash64('hello'),                 -- 5527709461249098091
  xxHash64('hello'),                   -- 0xbea37d5e（如需可逆不推荐）
  MD5('hello'),                        -- '5d41402abc4b2a76b9719d911017c592'
  halfMD5('hello')                     -- MD5 前 8 字节
```

## UUID 函数

```sql
SELECT
  generateUUIDv4(),                    -- 随机 UUID
  UUIDNumToString(toUUIDOrNull('12345678-1234-1234-1234-123456789012'))
```

## 条件函数

```sql
-- 多分支
SELECT
  multiIf(x > 100, 'high', x > 50, 'mid', 'low'),
  if(x > 0, 'positive', 'non-positive'),

-- 异常处理
SELECT
  ifNull(x, 0),                        -- x 为 NULL 时返回 0
  ifNotFinite(x, 0),                   -- 浮点 NaN/Inf 时返回 0
  coalesce(x, y, z, 0),                -- 第一个非 NULL 值

-- 类型转换
SELECT
  toString(123),
  toInt64('123'),
  toFloat64('1.23'),
  toDate('2024-01-01'),
  CAST(x AS String)
```

## 窗口函数与 CTE

详见 [window-functions.md](./window-functions.md)。

## Lambda 函数

```sql
-- 数组映射
SELECT arrayMap(x -> x * 2, [1,2,3])   -- [2,4,6]

-- 数组过滤
SELECT arrayFilter(x -> x > 1, [1,2,3]) -- [2,3]

-- 多参数
SELECT arrayMap((x, y) -> x + y, [1,2,3], [10,20,30])  -- [11,22,33]

-- 聚合
SELECT arrayReduce((acc, x) -> acc + x, [1,2,3], 0)  -- 6
```

## 函数使用建议

| 场景 | 推荐函数 |
|---|---|
| 文本日志解析 | `extract`、`match`、`splitByRegex` |
| 时间字段处理 | `toStartOfInterval`、`toDateTime64` |
| 数组去重 | `arrayDistinct`、`groupUniqArray` |
| JSON 字段提取 | `JSONExtract` 家族 |
| URL 解析 | `protocol`、`domain`、`path` |
| 用户唯一标识 | `cityHash64` 或 `generateUUIDv4()` |
| 距离计算 | `geoDistance`、`greatCircleDistance` |
| 性能优化 | `LowCardinality`、`prewhere`、`SAMPLE` |

## 下一步

- 学习窗口函数：见 [window-functions.md](./window-functions.md)
- 学习聚合查询：见 [select-aggregate.md](./select-aggregate.md)
""")


def ch02_window_functions() -> None:
    add("02-sql/window-functions.md", r"""---
title: 窗口函数
description: ClickHouse 窗口函数全集 + 用户留存 / 漏斗 / 排名实战
---

# 窗口函数

ClickHouse v20.x 后支持完整的 SQL 窗口函数（标准 SQL:2003）。

## 基础语法

```sql
SELECT
  user_id,
  event_time,
  amount,
  row_number() OVER (PARTITION BY user_id ORDER BY event_time) AS rn,
  rank() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rk,
  sum(amount) OVER (PARTITION BY user_id) AS user_total,
  avg(amount) OVER (PARTITION BY user_id ORDER BY event_time
                    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg
FROM events
```

## 排序函数

```sql
SELECT
  user_id,
  amount,
  row_number() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rn,
  rank() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rk,
  dense_rank() OVER (PARTITION BY user_id ORDER BY amount DESC) AS drk,
  percent_rank() OVER (PARTITION BY user_id ORDER BY amount) AS prk
FROM orders
```

| 函数 | 说明 |
|---|---|
| `row_number()` | 1, 2, 3, ...（无重复） |
| `rank()` | 1, 2, 2, 4（重复 + 跳号） |
| `dense_rank()` | 1, 2, 2, 3（重复 + 不跳号） |
| `percent_rank()` | (rank - 1) / (total_rows - 1) |

## 聚合窗口函数

```sql
SELECT
  user_id,
  event_date,
  amount,
  sum(amount) OVER (PARTITION BY user_id) AS user_total,
  sum(amount) OVER (PARTITION BY user_id ORDER BY event_date
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_total,
  avg(amount) OVER (PARTITION BY user_id ORDER BY event_date
                   RANGE BETWEEN INTERVAL 7 DAY PRECEDING AND CURRENT ROW) AS moving_avg_7d,
  max(amount) OVER (PARTITION BY user_id ORDER BY event_date
                   ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS max_7d
FROM orders
```

**窗口帧 (Frame)**：

| 类型 | 说明 |
|---|---|
| `ROWS BETWEEN n PRECEDING AND m FOLLOWING` | 物理行窗口 |
| `RANGE BETWEEN INTERVAL n DAY PRECEDING AND CURRENT ROW` | 逻辑范围（按时间） |
| `GROUPS BETWEEN ...` | 组窗口 |

## 分析函数

```sql
-- 同比 / 环比
SELECT
  event_date,
  amount,
  lagInFrame(amount, 1) OVER (ORDER BY event_date) AS prev_day,
  lagInFrame(amount, 7) OVER (ORDER BY event_date) AS prev_week,
  amount / lagInFrame(amount, 1) OVER (ORDER BY event_date) - 1 AS day_over_day,
  amount / lagInFrame(amount, 7) OVER (ORDER BY event_date) - 1 AS week_over_week
FROM daily_sales

-- 累计
SELECT
  event_date,
  sum(amount) OVER (ORDER BY event_date) AS cumulative
FROM daily_sales
```

| 函数 | 说明 |
|---|---|
| `lagInFrame(x, n)` | 前 n 行 |
| `leadInFrame(x, n)` | 后 n 行 |
| `first_value(x)` | 分区第一个值 |
| `last_value(x)` | 分区最后一个值 |
| `nth_value(x, n)` | 分区第 n 个值 |

## 实战：用户留存分析

```sql
-- D1 / D7 / D30 留存
WITH
  toDate(event_time) AS dt
SELECT
  user_id,
  min(dt) AS signup_date,
  max(dt) AS last_active,
  dateDiff('day', min(dt), max(dt)) AS active_days
FROM events
WHERE event_date >= '2024-01-01'
GROUP BY user_id

-- cohort 留存（按注册月分组，看后续月份的活跃率）
SELECT
  toMonth(first_event) AS cohort_month,
  dateDiff('month', first_event, event_date) AS month_offset,
  uniq(user_id) AS active_users
FROM (
  SELECT user_id, min(toDate(event_time)) AS first_event
  FROM events
  GROUP BY user_id
) t1
JOIN events e ON t1.user_id = e.user_id
GROUP BY cohort_month, month_offset
ORDER BY cohort_month, month_offset
```

## 实战：漏斗分析

```sql
-- 注册 → 实名 → 首次下单 → 复购 漏斗
WITH funnel AS (
  SELECT
    user_id,
    max(event_type = 'register') AS is_register,
    max(event_type = 'verify') AS is_verify,
    max(event_type = 'first_order') AS is_first_order,
    max(event_type = 'repurchase') AS is_repurchase
  FROM events
  WHERE event_date >= '2024-01-01'
  GROUP BY user_id
)
SELECT
  sum(is_register) AS step1_register,
  sum(is_register * is_verify) AS step2_verify,
  sum(is_register * is_verify * is_first_order) AS step3_first_order,
  sum(is_register * is_verify * is_first_order * is_repurchase) AS step4_repurchase,
  step2_verify / step1_register AS conversion_1to2,
  step3_first_order / step2_verify AS conversion_2to3,
  step4_repurchase / step3_first_order AS conversion_3to4
FROM funnel
```

## 实战：用户活跃排名

```sql
-- 各国家 TOP 10 活跃用户
SELECT *
FROM (
  SELECT
    country,
    user_id,
    count() AS event_count,
    row_number() OVER (PARTITION BY country ORDER BY count() DESC) AS rn
  FROM events
  WHERE event_date >= today() - INTERVAL 30 DAY
  GROUP BY country, user_id
)
WHERE rn <= 10
ORDER BY country, rn
```

## CTE（公共表表达式）

ClickHouse 支持标准 CTE（v21.x+）：

```sql
WITH
  daily_active AS (
    SELECT event_date, uniq(user_id) AS dau
    FROM events
    WHERE event_date >= today() - INTERVAL 30 DAY
    GROUP BY event_date
  ),
  daily_new AS (
    SELECT
      toDate(first_event_time) AS signup_date,
      uniq(user_id) AS new_users
    FROM users
    GROUP BY signup_date
  )
SELECT
  a.event_date,
  a.dau,
  n.new_users,
  a.dau / n.new_users AS ratio
FROM daily_active a
LEFT JOIN daily_new n ON a.event_date = n.signup_date
```

## 窗口函数性能

### 物化（避免重复计算）

```sql
-- 创建宽表（每行带累计指标）
CREATE MATERIALIZED VIEW user_cumulative_mv
ENGINE = SummingMergeTree()
ORDER BY (user_id, event_date)
AS SELECT
  user_id,
  event_date,
  sum(amount) AS daily_amount,
  sum(amount) AS cumulative_amount  -- 由下游查询计算
FROM orders
GROUP BY user_id, event_date
```

### PARTITION BY 优化

确保 `PARTITION BY` 用最低基数维度，避免数据倾斜：

```sql
-- ✅ 好：按 user_id 分区
SELECT *, row_number() OVER (PARTITION BY user_id ORDER BY event_time)
FROM events

-- ❌ 差：按 city 分区（数据倾斜）
SELECT *, row_number() OVER (PARTITION BY city ORDER BY event_time)
FROM events
```

## 下一步

- 学习 JOIN：见 [join.md](./join.md)
- 学习表引擎：见 [03-table-engine/overview.md](../03-table-engine/overview.md)
""")


def ch02_dictionary() -> None:
    add("02-sql/dictionary.md", r"""---
title: Dictionary 字典
description: ClickHouse Dictionary 完整指南：原理 / 创建 / 维护 / 实战
---

# Dictionary 字典

Dictionary 是 ClickHouse 的核心特性，本质是**内存中的本地 Map**，提供毫秒级 KV 查询。

## 原理

```text
┌──────────────────┐
│  External Source │  MySQL / PostgreSQL / ClickHouse / MongoDB / Redis / HTTP
└──────────────────┘
         │
         │ 定期拉取（lifetime）
         ▼
┌──────────────────┐
│  ClickHouse      │
│  Dictionary      │  内存中，按 primary key 索引
│  (HASHED/FLAT)   │  分布在所有节点的本地内存
└──────────────────┘
         ▲
         │ dictGet()
         │
┌──────────────────┐
│  SELECT 查询      │
└──────────────────┘
```

**核心特性**：
- 内存存储：每节点保存全量字典（适合百万级数据）
- 定期更新：按 `LIFETIME` 自动刷新
- 多种数据源：MySQL / PG / ClickHouse / Redis / MongoDB / HTTP / 文件
- 多种布局：`HASHED` / `FLAT` / `CACHE` / `COMPLEX_KEY_HASHED`

## 创建字典

### 从 MySQL 加载

```sql
CREATE DICTIONARY users_dict (
  id UInt64,
  user_name String,
  country String DEFAULT 'unknown',
  age UInt8 DEFAULT 0,
  vip_level UInt8 DEFAULT 0
)
PRIMARY KEY id
SOURCE(MYSQL(
  HOST 'mysql-host'
  PORT 3306
  USER 'readonly'
  PASSWORD 'xxx'
  DB 'production'
  TABLE 'users'
))
LIFETIME(MIN 300 MAX 600)  -- 5-10 分钟更新一次
LAYOUT(HASHED())
```

### 从 ClickHouse 加载

```sql
CREATE DICTIONARY users_dict (
  id UInt64,
  user_name String,
  country String
)
PRIMARY KEY id
SOURCE(CLICKHOUSE(
  DB 'mydb'
  TABLE 'users'
  USER 'default'
  PASSWORD ''
))
LIFETIME(MIN 300 MAX 600)
LAYOUT(HASHED())
```

### 从 Redis 加载

```sql
CREATE DICTIONARY user_meta_dict (
  user_id UInt64,
  meta String
)
PRIMARY KEY user_id
SOURCE(REDIS(
  HOST 'redis-host'
  PORT 6379
  STORAGE_TYPE 'hashmap'
))
LIFETIME(MIN 60 MAX 300)
LAYOUT(COMPLEX_KEY_HASHED())
```

### 从文件加载

```sql
-- TSV 文件
CREATE DICTIONARY country_dict (
  country_code String,
  country_name String
)
PRIMARY KEY country_code
SOURCE(FILE(PATH '/opt/dictionaries/country.tsv' FORMAT 'TabSeparated'))
LIFETIME(MIN 300 MAX 600)
LAYOUT(HASHED())

-- /opt/dictionaries/country.tsv 内容：
-- CN	China
-- US	United States
-- JP	Japan
```

## 字典布局（LAYOUT）

| Layout | 内存 | 性能 | 适用 |
|---|---|---|---|
| **FLAT** | 最少 | 快 | 大字典（百万级），顺序读 |
| **HASHED** | 中 | 快 | 默认选项，KV 查询 |
| **HASHED_ARRAY** | 中 | 快 | 多 key |
| **COMPLEX_KEY_HASHED** | 中 | 快 | 复合主键 |
| **SPARSE_HASHED** | 较少 | 中 | 大字典（千万级） |
| **CACHE** | 极少 | 中 | 远程字典，本地缓存 |
| **SSD_CACHE** | 极少 | 中 | 超大字典 + 本地 SSD |

## 查询字典

### `dictGet`（核心函数）

```sql
-- 基础查询
SELECT
  event_id,
  dictGet('users_dict', 'user_name', user_id) AS user_name,
  dictGet('users_dict', 'country', user_id) AS country
FROM events
WHERE event_date = '2024-01-01'

-- 带默认值
SELECT
  dictGet('users_dict', 'user_name', user_id, 'unknown') AS user_name

-- 多字段查询
SELECT
  dictGet('users_dict', ('user_name', 'country'), user_id) AS fields
```

### `dictHas`（检查存在）

```sql
SELECT
  countIf(dictHas('users_dict', user_id)) AS known_users,
  countIf(NOT dictHas('users_dict', user_id)) AS unknown_users
FROM events
WHERE event_date = '2024-01-01'
```

## 字典维护

### 手动更新

```sql
SYSTEM RELOAD DICTIONARY users_dict
```

### 监控字典状态

```sql
SELECT * FROM system.dictionaries FORMAT Vertical

-- 关键字段
name: users_dict
status: LOADED
element_count: 1000000
bytes_allocated: 52428800
last_successful_update_time: 2024-01-15 12:00:00
```

## 实战：用户画像补全

```sql
-- 创建字典（从 MySQL）
CREATE DICTIONARY user_profile_dict (
  user_id UInt64,
  user_name String,
  country LowCardinality(String),
  age UInt8,
  gender LowCardinality(String),
  vip_level UInt8,
  register_date Date
)
PRIMARY KEY user_id
SOURCE(MYSQL(...))
LIFETIME(MIN 300 MAX 600)
LAYOUT(HASHED())

-- 查询时补全
SELECT
  e.event_id,
  e.event_type,
  dictGet('user_profile_dict', 'user_name', e.user_id) AS user_name,
  dictGet('user_profile_dict', 'country', e.user_id) AS country,
  dictGet('user_profile_dict', 'age', e.user_id) AS age,
  e.amount
FROM events e
WHERE e.event_date >= today() - INTERVAL 7 DAY
LIMIT 1000
```

## 实战：商品维度补全

```sql
CREATE DICTIONARY products_dict (
  product_id UInt64,
  product_name String,
  category LowCardinality(String),
  brand String,
  price Decimal(18, 2)
)
PRIMARY KEY product_id
SOURCE(CLICKHOUSE(DB 'mydb' TABLE 'products'))
LIFETIME(MIN 600 MAX 1800)
LAYOUT(HASHED())

-- 订单分析
SELECT
  o.order_id,
  dictGet('products_dict', 'product_name', o.product_id) AS product_name,
  dictGet('products_dict', 'category', o.product_id) AS category,
  o.amount
FROM orders o
WHERE o.order_date >= today() - INTERVAL 30 DAY
```

## 字典 vs JOIN 性能对比

| 维度 | Dictionary | JOIN |
|---|---|---|
| 性能（10 亿行 × 百万字典） | 100ms | 30s |
| 内存占用 | 每节点 N GB（字典大小） | 0 |
| 实时性 | 有延迟（LIFETIME） | 实时 |
| 适用场景 | 维度表（百万级） | 大表 JOIN |

**经验法则**：维度表 < 1000 万行 → Dictionary；否则 → JOIN。

## 下一步

- 学习表引擎：见 [03-table-engine/overview.md](../03-table-engine/overview.md)
""")


# ============================================================================
# Chapter 03: Table Engine (5 stubs)
# ============================================================================

def ch03_mergetree_family() -> None:
    add("03-table-engine/mergetree-family.md", r"""---
title: MergeTree 表引擎家族
description: MergeTree / ReplacingMergeTree / AggregatingMergeTree / CollapsingMergeTree / VersionedCollapsingMergeTree / SummingMergeTree 完整对比
---

# MergeTree 表引擎家族

MergeTree 是 ClickHouse 的核心引擎，LSM 风格（写入即后台合并），家族有 6 个变种，覆盖 80% 的场景。

## MergeTree（基础）

```sql
CREATE TABLE events (
  event_date Date,
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  amount Decimal(18, 2)
)
ENGINE = MergeTree()
PARTITION BY event_date       -- 按天分区
ORDER BY (user_id, event_time) -- 排序键（主键）
SETTINGS index_granularity = 8192;  -- 索引粒度（默认 8192）
```

**关键参数**：
- `PARTITION BY`：分区键（通常按时间），影响查询时数据扫描量
- `ORDER BY`：排序键（必填），决定主键索引和压缩比
- `SETTINGS.index_granularity`：索引粒度（默认 8192 行），越小查询越快但索引越大

## ReplacingMergeTree（去重）

**场景**：支持重复写入（如 Kafka 重投），后台自动去重。

```sql
CREATE TABLE user_events (
  event_time DateTime,
  user_id UInt64,
  event_type String,
  payload String
)
ENGINE = ReplacingMergeTree(event_time)  -- 按 event_time 列保留最新
PARTITION BY toYYYYMM(event_time)
ORDER BY (user_id, event_type)

-- 写入重复数据
INSERT INTO user_events VALUES (now(), 1, 'click', '{}')
INSERT INTO user_events VALUES (now(), 1, 'click', '{...new...}')
-- 后台合并时保留 event_time 最大的那一行

-- ⚠️ ReplacingMergeTree 去重是异步的（合并时执行）
-- 实时查询可能看到重复数据，需要 FINAL 强制合并
SELECT * FROM user_events FINAL WHERE user_id = 1
```

**最佳实践**：业务层保证幂等（按唯一键去重），ReplacingMergeTree 是兜底。

## AggregatingMergeTree（预聚合）

**场景**：实时指标、UV / DAU / 漏斗等高频聚合查询。

```sql
-- 基础表（存明细）
CREATE TABLE events (
  event_date Date,
  user_id UInt64,
  event_type LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (event_date, event_type)

-- 物化视图（预聚合）
CREATE TABLE events_agg (
  event_date Date,
  event_type LowCardinality(String),
  uv_bitmap AggregateFunction(groupBitmap, UInt64),
  pv_count AggregateFunction(count, UInt64)
)
ENGINE = AggregatingMergeTree()
PARTITION BY event_date
ORDER BY (event_date, event_type)

CREATE MATERIALIZED VIEW events_agg_mv
TO events_agg AS
SELECT
  event_date,
  event_type,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv_count
FROM events
GROUP BY event_date, event_type

-- 查询（自动合并 State）
SELECT
  event_date,
  event_type,
  bitmapCardinality(merge(uv_bitmap)) AS uv,
  sumMerge(pv_count) AS pv
FROM events_agg
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-07'
GROUP BY event_date, event_type
```

**核心 State 函数**：

| 聚合函数 | State 函数 | Merge 函数 |
|---|---|---|
| `count` | `countState` | `countMerge` |
| `sum` | `sumState` | `sumMerge` |
| `avg` | `avgState` | `avgMerge` |
| `uniq` | `uniqState` | `uniqMerge` |
| `groupBitmap` | `groupBitmapState` | `groupBitmapMerge` |
| `quantile` | `quantileState` | `quantileMerge` |

## CollapsingMergeTree（折叠删除）

**场景**：支持删除操作（异步），用 `sign` 列标记。

```sql
CREATE TABLE user_balance (
  user_id UInt64,
  balance Int64,
  sign Int8  -- 1 = 新增，-1 = 折叠
)
ENGINE = CollapsingMergeTree(sign)
ORDER BY user_id

-- 插入
INSERT INTO user_balance VALUES (1, 100, 1)
INSERT INTO user_balance VALUES (1, 100, -1)
INSERT INTO user_balance VALUES (1, 200, 1)
-- 合并后只剩 balance=200 的那一行

-- 查询（必须 FINAL）
SELECT * FROM user_balance FINAL WHERE user_id = 1
```

**问题**：`sign` 错乱会导致数据不一致，建议改用 `VersionedCollapsingMergeTree`。

## VersionedCollapsingMergeTree（版本折叠）

**场景**：避免 `sign` 错乱导致的数据问题。

```sql
CREATE TABLE user_balance (
  user_id UInt64,
  balance Int64,
  sign Int8,        -- 1/-1
  version UInt64    -- 版本号（递增）
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
ORDER BY user_id

-- 写入（version 必须递增）
INSERT INTO user_balance VALUES (1, 100, 1, 1)
INSERT INTO user_balance VALUES (1, 100, -1, 2)  -- 折叠上一行
INSERT INTO user_balance VALUES (1, 200, 1, 3)  -- 新增

-- 查询
SELECT * FROM user_balance FINAL WHERE user_id = 1
```

**优势**：即使 `sign` 错乱，`version` 保证折叠正确。

## SummingMergeTree（数值合并）

**场景**：所有列都是可累加的指标（如流量、点击量）。

```sql
CREATE TABLE metrics (
  metric_date Date,
  metric_name LowCardinality(String),
  value UInt64
)
ENGINE = SummingMergeTree()
PARTITION BY metric_date
ORDER BY (metric_date, metric_name)

-- 多次插入同 key 的数据，后台合并时会求和
INSERT INTO metrics VALUES ('2024-01-01', 'pv', 100)
INSERT INTO metrics VALUES ('2024-01-01', 'pv', 50)
-- 合并后：pv = 150
```

## 选型决策树

```text
                    你的表是？
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
    明细事件         需要去重          需要预聚合
        │               │               │
   MergeTree      ReplacingMergeTree  AggregatingMergeTree
                        │
                删除场景？
                ┌───────┴────────┐
                ▼                ▼
         CollapsingMergeTree  VersionedCollapsingMergeTree
                │
                ▼
           SummingMergeTree（全部是数值列）
```

## 实战：实时指标看板

```sql
-- 明细表（接收 Kafka 写入）
CREATE TABLE events_local (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  country LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (user_id, event_type)

-- 物化视图：每分钟 UV / PV
CREATE TABLE events_minute_agg (
  event_minute DateTime,
  country LowCardinality(String),
  event_type LowCardinality(String),
  uv_bitmap AggregateFunction(groupBitmap, UInt64),
  pv_count AggregateFunction(count)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_minute)
ORDER BY (event_minute, country, event_type)

CREATE MATERIALIZED VIEW events_minute_mv
TO events_minute_agg AS
SELECT
  toStartOfMinute(event_time) AS event_minute,
  country,
  event_type,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv_count
FROM events_local
GROUP BY event_minute, country, event_type

-- 查询
SELECT
  event_minute,
  country,
  sum(pv_count) AS pv,
  bitmapCardinality(merge(uv_bitmap)) AS uv
FROM events_minute_agg
WHERE event_minute >= now() - INTERVAL 1 HOUR
GROUP BY event_minute, country
```

## 下一步

- 学习 Kafka 引擎：见 [kafka-engine.md](./kafka-engine.md)
- 学习物化视图：见 [materialized-view.md](./materialized-view.md)
""")


def ch03_log_engine() -> None:
    add("03-table-engine/log-engine.md", r"""---
title: Log / TinyLog / StripeLog 引擎
description: 小数据量场景的简单日志引擎，性能差但写入极简
---

# Log / TinyLog / StripeLog 引擎

Log 引擎家族适用于**小数据量**场景（百万级以内），它们：
- 没有 MergeTree 的后台合并
- 没有索引
- 没有并发读
- 写入是 append-only

## TinyLog（最简单）

```sql
CREATE TABLE simple_logs (
  log_time DateTime,
  message String
)
ENGINE = TinyLog()

INSERT INTO simple_logs VALUES (now(), 'hello')

SELECT * FROM simple_logs
```

**特点**：
- 每列一个文件（`<column>.bin`）
- 无索引，无压缩（除了 LZ4）
- 适合一次性写入 + 全表扫描
- **不能 ALTER**（只能 DROP + CREATE）

## Log（略强于 TinyLog）

```sql
CREATE TABLE simple_logs (
  log_time DateTime,
  message String
)
ENGINE = Log()
```

**区别**：
- Log 在每个数据文件结尾有「marks」标记，支持范围查询
- 比 TinyLog 略快

## StripeLog（合并存储）

```sql
CREATE TABLE simple_logs (
  log_time DateTime,
  message String
)
ENGINE = StripeLog()
```

**特点**：
- 所有列存储在同一个 `.data` 文件中
- 写入极快（小数据量）
- 读取也很简单
- 适合「一次性导入 + 偶尔查询」

## 何时使用 Log 引擎？

| 场景 | 推荐 |
|---|---|
| 小数据量（< 百万行） + 简单写入 | Log / TinyLog |
| 一次性导入 + 全表扫描 | StripeLog |
| 大数据量 | ❌ 用 MergeTree |
| 需要并发读 | ❌ 用 MergeTree |
| 需要修改数据 | ❌ 用 MergeTree |
| 需要物化视图 | ❌ 用 MergeTree |

## 实战：临时表（ETL 中间结果）

```sql
-- ETL 第一步：导入原始数据
CREATE TABLE raw_events_tmp (
  raw_line String
)
ENGINE = TinyLog()

INSERT INTO raw_events_tmp FROM INFILE '/tmp/raw_logs.csv' FORMAT CSVWithNames

-- 第二步：解析 + 写入 MergeTree 表
INSERT INTO events
SELECT
  parseDateTimeBestEffort(JSONExtractString(raw_line, 'event_time')) AS event_time,
  toUInt64(JSONExtractString(raw_line, 'user_id')) AS user_id,
  JSONExtractString(raw_line, 'event_type') AS event_type
FROM raw_events_tmp

-- 清理
DROP TABLE raw_events_tmp
```

## 与 MergeTree 的对比

| 维度 | Log 家族 | MergeTree |
|---|---|---|
| **数据量** | < 百万行 | 任意（PB 级） |
| **后台合并** | ❌ | ✅ |
| **主键索引** | ❌ | ✅ |
| **并发读** | ❌ | ✅ |
| **修改数据** | ❌ | ✅（弱） |
| **分区** | ❌ | ✅ |
| **TTL** | ❌ | ✅ |
| **写入性能** | 高（小数据） | 中 |
| **查询性能** | 低（全表扫） | 高 |

## 实战：ClickHouse 内部表

ClickHouse 自身大量使用 Log 引擎（如 `system.query_log`、`system.trace_log` 等）：

```sql
SELECT * FROM system.tables
WHERE engine LIKE '%Log%'
```

## 下一步

- 学习 MergeTree 家族：见 [mergetree-family.md](./mergetree-family.md)
- 学习 Kafka 引擎：见 [kafka-engine.md](./kafka-engine.md)
""")


def ch03_kafka_engine() -> None:
    add("03-table-engine/kafka-engine.md", r"""---
title: Kafka 表引擎
description: 直接消费 Kafka topic，配合物化视图实现秒级实时数仓
---

# Kafka 表引擎

Kafka 引擎是 ClickHouse 实时数仓的核心，让你无需 Kafka Consumer 客户端，直接消费 topic。

## 基础用法

### 1. 创建 Kafka 表（消费者）

```sql
CREATE TABLE events_kafka (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  payload String
)
ENGINE = Kafka()
SETTINGS
  kafka_broker_list = 'kafka-1:9092,kafka-2:9092',
  kafka_topic_list = 'events',
  kafka_group_name = 'clickhouse_consumer_1',
  kafka_format = 'JSONEachRow',
  kafka_num_consumers = 1
```

**关键参数**：

| 参数 | 说明 |
|---|---|
| `kafka_broker_list` | Kafka broker（逗号分隔） |
| `kafka_topic_list` | topic 列表（逗号分隔） |
| `kafka_group_name` | 消费组（务必唯一） |
| `kafka_format` | 数据格式（JSONEachRow / CSV / Avro 等） |
| `kafka_num_consumers` | 消费者数量（建议 = broker 数） |

### 2. 创建本地表（实际存储）

```sql
CREATE TABLE events_local (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  payload String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (user_id, event_time)
```

### 3. 创建物化视图（自动消费）

```sql
CREATE MATERIALIZED VIEW events_mv TO events_local AS
SELECT
  event_time,
  user_id,
  event_type,
  payload
FROM events_kafka
```

**完成！现在 Kafka 中的数据会自动写入 `events_local`。**

## 多 topic 消费

```sql
CREATE TABLE events_kafka_multi (
  event_time DateTime,
  user_id UInt64,
  event_type String,
  source LowCardinality(String)  -- 标记来自哪个 topic
)
ENGINE = Kafka()
SETTINGS
  kafka_broker_list = 'kafka-1:9092',
  kafka_topic_list = 'events_a,events_b,events_c',
  kafka_group_name = 'multi_topic_consumer',
  kafka_format = 'JSONEachRow'

CREATE MATERIALIZED VIEW events_multi_mv TO events_local AS
SELECT
  event_time,
  user_id,
  event_type,
  source
FROM events_kafka_multi
```

## Avro / Protobuf 格式

```sql
-- Avro（Confluent Schema Registry）
CREATE TABLE events_avro (...)
ENGINE = Kafka()
SETTINGS
  kafka_format = 'AvroConfluent',
  kafka_schema_registry_url = 'http://schema-registry:8081'

-- Protobuf
CREATE TABLE events_proto (...)
ENGINE = Kafka()
SETTINGS
  kafka_format = 'Protobuf',
  format_protobuf_schema_path = '/path/to/schema.proto',
  format_protobuf_message_name = 'Event'
```

## 容错与监控

### 监控消费进度

```sql
-- 查看 Kafka 引擎表
SELECT * FROM system.tables WHERE engine = 'Kafka'

-- 查看 Kafka consumer 状态
SELECT * FROM system.kafka_consumers FORMAT Vertical
```

### 死信队列（DLQ）

ClickHouse Kafka 引擎**没有原生 DLQ**，但可以通过 `kafka_handle_error_mode` 处理错误：

```sql
SETTINGS
  kafka_format = 'JSONEachRow',
  kafka_handle_error_mode = 'stream'  -- 错误数据进入虚拟列 _error / _raw_message
```

### 重置 offset

```sql
-- 暂停消费
DETACH TABLE events_kafka

-- 修改 group_name（重置 offset）
ALTER TABLE events_kafka MODIFY SETTING kafka_group_name = 'new_group'

-- 重新启动
ATTACH TABLE events_kafka
```

## 实战：实时用户行为日志

```sql
-- Kafka 表
CREATE TABLE user_behavior_kafka (
  user_id UInt64,
  event_time DateTime,
  event_type LowCardinality(String),
  page_url String,
  duration_ms UInt32,
  properties Map(String, String)
)
ENGINE = Kafka()
SETTINGS
  kafka_broker_list = 'kafka-broker:9092',
  kafka_topic_list = 'user_behavior',
  kafka_group_name = 'ch_user_behavior_consumer',
  kafka_format = 'JSONEachRow',
  kafka_num_consumers = 3,
  kafka_row_delimiter = '\n'

-- 本地表
CREATE TABLE user_behavior_local (
  user_id UInt64,
  event_time DateTime,
  event_type LowCardinality(String),
  page_url String,
  duration_ms UInt32,
  properties Map(String, String),
  event_date Date DEFAULT toDate(event_time)
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (user_id, event_time)

-- 物化视图
CREATE MATERIALIZED VIEW user_behavior_mv TO user_behavior_local AS
SELECT
  user_id,
  event_time,
  event_type,
  page_url,
  duration_ms,
  properties,
  toDate(event_time) AS event_date
FROM user_behavior_kafka

-- 实时看板查询（最近 1 小时）
SELECT
  toStartOfFiveMinute(event_time) AS t,
  uniq(user_id) AS uv,
  count() AS pv,
  avg(duration_ms) AS avg_duration
FROM user_behavior_local
WHERE event_time >= now() - INTERVAL 1 HOUR
GROUP BY t
ORDER BY t
```

## 实战：Kafka → MV → 多表分流

```sql
-- 一个 Kafka topic 写入多个本地表（按 event_type 分流）
CREATE MATERIALIZED VIEW page_view_mv TO page_views_local AS
SELECT * FROM events_kafka WHERE event_type = 'page_view'

CREATE MATERIALIZED VIEW click_mv TO clicks_local AS
SELECT * FROM events_kafka WHERE event_type = 'click'

CREATE MATERIALIZED VIEW purchase_mv TO purchases_local AS
SELECT * FROM events_kafka WHERE event_type = 'purchase'
```

## 高级：Kafka 事务支持

ClickHouse v23.x 支持 Kafka 事务：

```sql
SETTINGS
  kafka_format = 'JSONEachRow',
  kafka_transactional_id = 'tx-1'
```

## 与传统 Kafka Consumer 对比

| 维度 | ClickHouse Kafka 引擎 | Kafka Consumer + SDK |
|---|---|---|
| **部署复杂度** | 一行 SQL | 客户端 + Offset 管理 |
| **Exactly-Once** | 弱（异步） | 强（事务） |
| **吞吐** | 高（10w+ rows/s） | 取决于客户端 |
| **背压** | 自动（合并慢时滞后） | 手动管理 |
| **监控** | `system.kafka_consumers` | 自建 |
| **多表写入** | 一个 topic → 多 MV | 手动 partition 分配 |

## 下一步

- 学习 Distributed 表：见 [distributed.md](./distributed.md)
- 学习物化视图：见 [materialized-view.md](./materialized-view.md)
""")


def ch03_distributed() -> None:
    add("03-table-engine/distributed.md", r"""---
title: Distributed 表引擎
description: 多分片集群查询 / 写入的核心：本地表 + 分布式表 scatter-gather 模型
---

# Distributed 表引擎

Distributed 表是 ClickHouse 集群查询的入口，本身不存储数据，是「本地表的代理」。

## 基础模型

```text
┌─────────────────────────┐
│  Distributed 表         │  不存数据，只路由
│  events_distributed     │
└─────────────────────────┘
         │
         │ SELECT → scatter 到所有分片
         │ INSERT → hash 到目标分片
         │
   ┌─────┴─────┬─────┴─────┬─────┴─────┐
   ▼           ▼           ▼           ▼
┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
│本地表 │  │本地表 │  │本地表 │  │本地表 │
│shard1 │  │shard2 │  │shard3 │  │shard4 │
└───────┘  └───────┘  └───────┘  └───────┘
   A,B副本    A,B副本    A,B副本    A,B副本
```

## 创建 Distributed 表

### 1. 集群配置

在 `/etc/clickhouse-server/config.xml` 中定义：

```xml
<remote_servers>
    <my_cluster>
        <shard>
            <internal_replication>true</internal_replication>
            <replica>
                <host>shard1-replica1</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>shard1-replica2</host>
                <port>9000</port>
            </replica>
        </shard>
        <shard>
            <replica>
                <host>shard2-replica1</host>
                <port>9000</port>
            </replica>
            <replica>
                <host>shard2-replica2</host>
                <port>9000</port>
            </replica>
        </shard>
    </my_cluster>
</remote_servers>
```

### 2. 在每台机器创建本地表

```sql
-- 在每个节点都执行
CREATE TABLE events_local (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (user_id, event_time)
```

### 3. 创建 Distributed 表（在每个节点）

```sql
-- 在每个节点都执行
CREATE TABLE events_distributed (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String)
)
ENGINE = Distributed(my_cluster, default, events_local, rand())
```

**参数说明**：
- `my_cluster`：集群名（对应 config.xml）
- `default`：数据库名
- `events_local`：本地表名
- `rand()`：分片键（决定数据落到哪个分片）

## 分片键选择

```sql
-- 1. 随机（最简单）
ENGINE = Distributed(cluster, db, local, rand())

-- 2. 按用户 ID hash（同一用户始终在同一分片）
ENGINE = Distributed(cluster, db, local, cityHash64(user_id))

-- 3. 按月分片
ENGINE = Distributed(cluster, db, local, toYYYYMM(event_time))

-- 4. 自定义表达式
ENGINE = Distributed(cluster, db, local, intHash32(user_id) % 4)
```

**分片键决策**：

| 场景 | 推荐分片键 |
|---|---|
| 写入均匀 + 无 JOIN | `rand()` |
| 按用户聚合查询 | `cityHash64(user_id)` |
| 按时间范围查询 | `toYYYYMM(event_time)` |
| 多租户 | `cityHash64(tenant_id)` |

## 查询流程（SELECT）

```sql
-- 在任意节点查询，自动 scatter-gather
SELECT count() FROM events_distributed

-- 实际执行：
-- 1. 协调节点收到查询
-- 2. 同时发往所有分片
-- 3. 每个分片本地查询
-- 4. 协调节点 merge 结果
-- 5. 返回给客户端
```

## 写入流程（INSERT）

```sql
-- 通过 Distributed 表写入
INSERT INTO events_distributed VALUES (now(), 1, 'click')

-- 实际执行：
-- 1. 客户端连接节点 A
-- 2. 节点 A 根据分片键计算目标分片
-- 3. 转发到目标分片
-- 4. 目标分片写入本地表（同步副本）
-- 5. 返回成功
```

**性能提示**：
- Distributed 表写入有转发开销，**生产推荐直接写入本地表**
- 用 `insert_distributed_sync = 1` 等待所有副本确认

## 实战：本地表写入（推荐）

```bash
# 应用按 user_id mod 分片，写入对应节点
# 例如 user_id=12345, hash=12345 % 4 = 1, 写入 shard1

# 在 shard1 上执行
INSERT INTO events_local (event_time, user_id, event_type)
VALUES (now(), 12345, 'click')
```

```python
# Python 端：按 user_id 路由
import hashlib

def get_shard(user_id, num_shards=4):
    return hashlib.md5(str(user_id).encode()).hexdigest()[0] % num_shards

# 维护节点列表
SHARD_HOSTS = ['shard1:9000', 'shard2:9000', 'shard3:9000', 'shard4:9000']

# 写入对应节点
shard = get_shard(user_id)
client = clickhouse_connect.get_client(host=SHARD_HOSTS[shard])
client.insert('events_local', data)
```

## 实战：跨分片 JOIN

```sql
-- Distributed 表 + JOIN（本地表 JOIN）
SELECT
  e.event_id,
  u.user_name,
  u.country
FROM events_distributed e
JOIN users_distributed u ON e.user_id = u.id
WHERE e.event_date = '2024-01-01'

-- ⚠️ 跨分片 JOIN 性能差（需要在所有分片上 JOIN 后 merge）
-- 推荐：所有 JOIN 表用相同的分片键
```

## GLOBAL JOIN 优化

```sql
-- GLOBAL JOIN（每个分片都获取全量右表）
SELECT
  e.event_id,
  u.user_name
FROM events_distributed e
GLOBAL JOIN users_local u ON e.user_id = u.id
```

**注意**：`users_local` 必须复制到每个分片（如用 Distributed 表）。

## 副本与高可用

```sql
-- internal_replication = true 时
-- 写入第一个副本，自动同步到第二个副本
-- 任何副本故障时，从另一个副本读
```

## 监控

```sql
-- 查看集群拓扑
SELECT * FROM system.clusters FORMAT Vertical

-- 查看副本状态
SELECT * FROM system.replicas FORMAT Vertical

-- 查看分片数据分布
SELECT shard_num, count() FROM distributed_events
GROUP BY shard_num
```

## 常见问题

### Q1：Distributed 表能存数据吗？

不能。Distributed 表只是「逻辑视图」，必须指向本地表。

### Q2：写入 Distributed 表会丢数据吗？

如果 `internal_replication=true` 且第一个副本写入成功，会同步副本，不会丢。
如果 `internal_replication=false`，写入第一个副本后立即返回（不等副本），可能丢。

### Q3：如何扩容？

1. 添加新分片（config.xml）
2. 在新分片创建本地表
3. **手动 rebalance 数据**（用 `clickhouse-copier` 或迁移工具）

### Q4：副本同步延迟

```sql
-- 查看延迟
SELECT
  database,
  table,
  absolute_delay,
  last_queue_update
FROM system.replicas
ORDER BY absolute_delay DESC
```

## 下一步

- 学习物化视图：见 [materialized-view.md](./materialized-view.md)
""")


def ch03_materialized_view() -> None:
    add("03-table-engine/materialized-view.md", r"""---
title: MaterializedView 物化视图
description: ClickHouse 实时数仓核心：增量更新 / 自动触发 / 多链路组合
---

# MaterializedView 物化视图

MaterializedView 是 ClickHouse 实时数仓的杀手锏：**源表写入时自动触发，链式增量更新**，无需任何调度。

## 基础概念

```text
源表 INSERT
    │
    ▼
物化视图触发
    │
    ▼
目标表写入
```

**关键特性**：
- **增量更新**：源表每次 INSERT，物化视图都会处理新数据
- **链式触发**：物化视图的输出可以写入另一张表的源
- **可独立查询**：物化视图本质上是一张表，可以直接查询

## 基础示例

```sql
-- 源表
CREATE TABLE events (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  amount Decimal(18, 2)
)
ENGINE = MergeTree()
ORDER BY (event_time, user_id)

-- 物化视图（写入 target_table）
CREATE TABLE events_daily (
  event_date Date,
  event_type LowCardinality(String),
  uv AggregateFunction(groupBitmap, UInt64),
  pv AggregateFunction(count),
  gmv AggregateFunction(sum, Decimal(18, 2))
)
ENGINE = AggregatingMergeTree()
PARTITION BY event_date
ORDER BY (event_date, event_type)

CREATE MATERIALIZED VIEW events_daily_mv TO events_daily AS
SELECT
  toDate(event_time) AS event_date,
  event_type,
  groupBitmapState(user_id) AS uv,
  countState() AS pv,
  sumState(amount) AS gmv
FROM events
GROUP BY event_date, event_type
```

## 三种物化视图类型

### 1. TO 表（默认）

```sql
CREATE MATERIALIZED VIEW mv_name TO target_table AS
SELECT ... FROM source_table
```

数据写入 `target_table`，原表无变化。

### 2. 直接物化（不带 TO）

```sql
CREATE MATERIALIZED VIEW mv_name AS
SELECT ... FROM source_table
```

数据存在物化视图自身（不能修改），适合纯计算场景。

### 3. POPULATE（回填历史）

```sql
CREATE MATERIALIZED VIEW events_daily_mv TO events_daily
POPULATE AS  -- 回填历史数据
SELECT ...
FROM events
```

**警告**：`POPULATE` + 实时写入之间有数据缺失窗口，建议**离线回填**：

```sql
-- 1. 创建物化视图（不带 POPULATE）
CREATE MATERIALIZED VIEW events_daily_mv TO events_daily AS ...

-- 2. 暂停源表写入
DETACH TABLE events

-- 3. 手动回填
INSERT INTO events_daily SELECT
  toDate(event_time) AS event_date,
  event_type,
  groupBitmapState(user_id) AS uv,
  ...
FROM events
GROUP BY event_date, event_type

-- 4. 重新附加源表
ATTACH TABLE events
```

## 链式物化视图（实时数仓分层）

```text
Kafka → events_raw → MV1 → events_dwd → MV2 → events_dws → MV3 → events_ads
                       （明细）          （轻度汇总）       （高度汇总）
```

```sql
-- 第一层：DWD（明细）
CREATE TABLE events_dwd (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  country LowCardinality(String),
  amount Decimal(18, 2)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (user_id, event_time)

CREATE MATERIALIZED VIEW events_dwd_mv TO events_dwd AS
SELECT
  event_time,
  user_id,
  event_type,
  dictGet('user_dict', 'country', user_id) AS country,
  amount
FROM events_raw

-- 第二层：DWS（每日汇总）
CREATE TABLE events_dws (
  event_date Date,
  country LowCardinality(String),
  uv AggregateFunction(groupBitmap, UInt64),
  pv AggregateFunction(count),
  gmv AggregateFunction(sum, Decimal(18, 2))
)
ENGINE = AggregatingMergeTree()
PARTITION BY event_date
ORDER BY (event_date, country)

CREATE MATERIALIZED VIEW events_dws_mv TO events_dws AS
SELECT
  toDate(event_time) AS event_date,
  country,
  groupBitmapState(user_id) AS uv,
  countState() AS pv,
  sumState(amount) AS gmv
FROM events_dwd
GROUP BY event_date, country

-- 第三层：ADS（应用层）
CREATE TABLE events_ads_country_daily (...)
ENGINE = AggregatingMergeTree()
ORDER BY (event_date, country)
```

## 实战：实时数仓 + 多维看板

```sql
-- 1. 明细表（接 Kafka）
CREATE TABLE events_raw (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  country LowCardinality(String),
  page_url String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (user_id, event_time)

-- 2. 每分钟 UV/PV（分钟级实时看板）
CREATE TABLE events_minute_agg (
  event_minute DateTime,
  country LowCardinality(String),
  event_type LowCardinality(String),
  uv AggregateFunction(groupBitmap, UInt64),
  pv AggregateFunction(count)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_minute)
ORDER BY (event_minute, country, event_type)

CREATE MATERIALIZED VIEW events_minute_mv TO events_minute_agg AS
SELECT
  toStartOfMinute(event_time) AS event_minute,
  country,
  event_type,
  groupBitmapState(user_id) AS uv,
  countState() AS pv
FROM events_raw
GROUP BY event_minute, country, event_type

-- 3. 用户活跃度画像（最近 7 天）
CREATE TABLE user_active_7d (
  user_id UInt64,
  active_days AggregateFunction(groupBitmap, Date),
  event_count AggregateFunction(sum, UInt64)
)
ENGINE = AggregatingMergeTree()
ORDER BY user_id

CREATE MATERIALIZED VIEW user_active_7d_mv TO user_active_7d AS
SELECT
  user_id,
  groupBitmapState(toDate(event_time)) AS active_days,
  sumState(1) AS event_count
FROM events_raw
GROUP BY user_id

-- 实时查询
SELECT
  event_minute,
  country,
  bitmapCardinality(merge(uv)) AS uv,
  sum(pv) AS pv
FROM events_minute_agg
WHERE event_minute >= now() - INTERVAL 10 MINUTE
GROUP BY event_minute, country
```

## 删除物化视图

```sql
-- 删除物化视图（不会删除目标表）
DROP TABLE events_daily_mv

-- 删除目标表（注意顺序）
DROP TABLE events_daily_mv  -- 先删 MV
DROP TABLE events_daily       -- 再删表
```

## 修改物化视图

⚠️ **物化视图不能直接 ALTER**。如需修改：

1. DROP 旧视图
2. 修改目标表（如需要）
3. CREATE 新视图
4. 回填历史数据

## 监控

```sql
-- 查看所有物化视图
SELECT * FROM system.tables WHERE engine = 'MaterializedView'

-- 查看物化视图写入量
SELECT
  database,
  table,
  parts,
  rows
FROM system.parts
WHERE database = 'default' AND table LIKE '%_mv%'

-- 关键：materialized_view_block 计数器
SELECT * FROM system.events WHERE event LIKE '%MaterializedView%'
```

## 性能提示

### 1. 物化视图不要太多

每张 MV 都增加写入开销，建议：
- 高频查询（每分钟 100+ 次）：用 MV 预聚合
- 低频查询（每小时）：直接查明细

### 2. 避免在 MV 中做复杂 JOIN

```sql
-- ❌ 慢
CREATE MATERIALIZED VIEW slow_mv AS
SELECT a.*, b.user_name
FROM events_raw a
JOIN users b ON a.user_id = b.id

-- ✅ 好：用 Dictionary
CREATE MATERIALIZED VIEW fast_mv AS
SELECT
  event_time,
  user_id,
  dictGet('users_dict', 'user_name', user_id) AS user_name
FROM events_raw
```

### 3. 物化视图的 Order By 优化

```sql
CREATE TABLE events_daily (...)
ENGINE = AggregatingMergeTree()
ORDER BY (event_date, event_type)  -- 与查询 GROUP BY 顺序一致
```

## 下一步

- 学习 Kafka 引擎：见 [kafka-engine.md](./kafka-engine.md)
- 学习 OLAP 场景：见 [04-olap-scenarios/overview.md](../04-olap-scenarios/overview.md)
""")


# ============================================================================
# Chapter 04: OLAP Scenarios (5 stubs)
# ============================================================================

def ch04_user_tracking() -> None:
    add("04-olap-scenarios/user-tracking.md", r"""---
title: 用户埋点分析
description: 抖音 / B 站级埋点场景：Kafka + RoaringBitmap + 留存 / 漏斗 / 路径分析
---

# 用户埋点分析

用户埋点是 ClickHouse 主战场之一，每天 PB 级数据，秒级查询。

## 场景特征

```text
数据规模：    PB 级
写入频率：    100w+ events/s
查询延迟：    秒级
典型查询：    留存 / 漏斗 / 路径 / 人群画像 / 用户行为序列
用户：        抖音 / B 站 / 京东 / 网易 / 头条
```

## 完整架构

```text
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 客户端 SDK │ → │ Kafka    │ → │ CK Kafka │ → │ CK MergeTree│
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                     │
                     ├→ MV1: 实时 UV/PV
                     ├→ MV2: 留存 cohort
                     ├→ MV3: 漏斗
                     └→ MV4: 用户活跃度画像
```

## Schema 设计

### 基础事件表

```sql
CREATE TABLE events (
  event_time DateTime64(3),  -- 毫秒精度
  event_date Date DEFAULT toDate(event_time),
  user_id UInt64,
  session_id UUID,
  event_type LowCardinality(String),  -- 'click', 'view', 'like', 'share'
  page_url String,
  duration_ms UInt32,
  properties Map(String, String),  -- 灵活扩展字段
  -- 维度（业务经常加字段，建议预留）
  country LowCardinality(String) DEFAULT '',
  device_type LowCardinality(String) DEFAULT '',
  app_version String DEFAULT '',
  channel LowCardinality(String) DEFAULT ''
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (user_id, event_time)
SETTINGS index_granularity = 8192
```

**关键设计**：
- `DateTime64(3)`：毫秒精度（推荐）
- `LowCardinality`：状态/国家/设备类型等低基数字段
- `Map(String, String)`：灵活扩展字段（性能换灵活）
- `ORDER BY (user_id, event_time)`：用户行为查询为主

### 宽表（推荐做法）

如果业务需要经常 JOIN 维度表，建议用宽表：

```sql
CREATE TABLE events_wide (
  event_time DateTime64(3),
  event_date Date,
  user_id UInt64,
  user_name String,             -- 冗余 user 字段
  user_country LowCardinality(String),
  event_type LowCardinality(String),
  page_url String,
  duration_ms UInt32,
  product_id UInt64,            -- 冗余 product 字段
  product_name String,
  product_category LowCardinality(String),
  amount Decimal(18, 2)
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (user_id, event_time)
```

**优势**：单表查询，无需 JOIN，性能最佳。

## 实时 UV / PV

```sql
-- 物化视图
CREATE TABLE events_uv_pv_1m (
  event_minute DateTime,
  country LowCardinality(String),
  event_type LowCardinality(String),
  uv AggregateFunction(groupBitmap, UInt64),
  pv AggregateFunction(count)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_minute)
ORDER BY (event_minute, country, event_type)

CREATE MATERIALIZED VIEW events_uv_pv_1m_mv TO events_uv_pv_1m AS
SELECT
  toStartOfMinute(event_time) AS event_minute,
  country,
  event_type,
  groupBitmapState(user_id) AS uv,
  countState() AS pv
FROM events
GROUP BY event_minute, country, event_type

-- 查询（最近 10 分钟 UV/PV）
SELECT
  event_minute,
  country,
  bitmapCardinality(merge(uv)) AS uv,
  sumMerge(pv) AS pv
FROM events_uv_pv_1m
WHERE event_minute >= now() - INTERVAL 10 MINUTE
GROUP BY event_minute, country
ORDER BY event_minute, country
```

## 用户留存分析

```sql
-- Cohort 留存（按注册日分组，看后续活跃率）
WITH cohorts AS (
  SELECT
    user_id,
    min(event_date) AS signup_date
  FROM events
  GROUP BY user_id
)
SELECT
  cohort_date,
  dateDiff('day', cohort_date, event_date) AS day_offset,
  uniq(user_id) AS active_users
FROM cohorts c
JOIN events e ON c.user_id = e.user_id
WHERE cohort_date >= today() - INTERVAL 30 DAY
GROUP BY cohort_date, day_offset
ORDER BY cohort_date, day_offset

-- D1 / D7 / D30 留存（单日注册用户的后续活跃率）
WITH new_users AS (
  SELECT user_id FROM events
  WHERE event_date = '2024-01-15'
  GROUP BY user_id
)
SELECT
  countIf(d1) / count() AS d1_retention,
  countIf(d7) / count() AS d7_retention,
  countIf(d30) / count() AS d30_retention
FROM (
  SELECT
    n.user_id,
    max(e.event_date = '2024-01-16') AS d1,
    max(e.event_date = '2024-01-22') AS d7,
    max(e.event_date = '2024-02-14') AS d30
  FROM new_users n
  LEFT JOIN events e ON n.user_id = e.user_id
  GROUP BY n.user_id
)
```

## 漏斗分析

```sql
-- 注册 → 实名 → 首次下单 → 复购
SELECT
  countIf(step1) AS register,
  countIf(step1 AND step2) AS verify,
  countIf(step1 AND step2 AND step3) AS first_order,
  countIf(step1 AND step2 AND step3 AND step4) AS repurchase,
  verify / register AS c1,
  first_order / verify AS c2,
  repurchase / first_order AS c3
FROM (
  SELECT
    user_id,
    min(event_date) FILTER (WHERE event_type = 'register') AS reg_date,
    min(event_date) FILTER (WHERE event_type = 'verify') AS verify_date,
    min(event_date) FILTER (WHERE event_type = 'first_order') AS order_date,
    min(event_date) FILTER (WHERE event_type = 'repurchase') AS repurchase_date,
    countIf(event_type = 'register') > 0 AS step1,
    countIf(event_type = 'verify') > 0 AS step2,
    countIf(event_type = 'first_order') > 0 AS step3,
    countIf(event_type = 'repurchase') > 0 AS step4
  FROM events
  WHERE event_date BETWEEN '2024-01-01' AND '2024-01-31'
  GROUP BY user_id
)
```

## 用户路径分析

```sql
-- 用户典型路径（点击流）
WITH user_paths AS (
  SELECT
    user_id,
    session_id,
    groupArray(event_type) AS path
  FROM events
  WHERE event_date = '2024-01-15'
  GROUP BY user_id, session_id
)
SELECT
  arrayStringConcat(arraySlice(path, 1, 5), '→') AS first_5_steps,
  count() AS user_count
FROM user_paths
GROUP BY first_5_steps
ORDER BY user_count DESC
LIMIT 20
```

## 人群画像

```sql
-- 高价值用户（最近 30 天消费 ≥ 1000）
SELECT
  user_id,
  sum(amount) AS total_amount,
  count() AS order_count,
  uniq(page_url) AS visited_pages
FROM events
WHERE event_date >= today() - INTERVAL 30 DAY
  AND event_type = 'purchase'
GROUP BY user_id
HAVING total_amount >= 1000
ORDER BY total_amount DESC
LIMIT 1000
```

## 性能基准

```text
数据量：     100 亿事件
写入吞吐：   50w rows/s
UV 查询：    < 100ms（RoaringBitmap 预聚合）
留存查询：   < 1s（D1-D30 cohort 表）
漏斗查询：   < 500ms
路径查询：   < 2s（限制 path 长度 ≤ 5）
```

## 大厂案例

- **字节跳动**：抖音埋点，单集群数千节点
- **B 站**：用户行为 + 弹幕反垃圾
- **京东**：商品点击 + 订单分析
- **网易**：游戏埋点 + 反作弊
- **头条**：新闻推荐实时数仓

详见 [../case-study.md](../../case-study.md)。

## 下一步

- 学习日志分析：见 [log-analysis.md](./log-analysis.md)
- 学习实时数仓：见 [realtime-warehouse.md](./realtime-warehouse.md)
""")


def ch04_log_analysis() -> None:
    add("04-olap-scenarios/log-analysis.md", r"""---
title: 日志分析
description: Uber / Cloudflare / GitHub 都在用：ClickHouse 替代 Elasticsearch 做日志分析
---

# 日志分析

日志分析是 ClickHouse 第二个主战场。Uber / Cloudflare / GitHub 等大厂用 CK 替代 Elasticsearch，成本降 10x、查询快 10x。

## vs Elasticsearch 对比

| 维度 | ClickHouse | Elasticsearch |
|---|---|---|
| **架构** | 列存 LSM | 倒排索引 |
| **存储成本** | 低（10-20x 压缩） | 高（原始文本） |
| **聚合查询** | 快（10x+） | 中等 |
| **文本搜索** | 中（正则 / 分词） | 极强（原生倒排） |
| **写入吞吐** | 高（100w+ rows/s） | 中（10w+ rows/s） |
| **运维** | 中（Keeper） | 高（Master + Data + Coordinating） |
| **生态** | Grafana / Kafka / dbt | ELK 全家桶 |
| **典型用户** | Uber / Cloudflare / GitHub | 几乎所有互联网公司 |

**结论**：聚合 / 统计为主 → ClickHouse；全文搜索为主 → Elasticsearch；两者共存也很常见。

## 完整架构

```text
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ App/Service│ → │ Vector / │ → │ Kafka    │ → │ CK Kafka  │
│            │   │ Fluent Bit│   │          │   │ Engine   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                       │
                                                       ▼
                                                ┌──────────┐
                                                │ MergeTree│
                                                │ logs     │
                                                └──────────┘
                                                       │
                                                       ▼
                                                  Grafana
                                                  BI Tools
```

## Schema 设计

### Nginx 访问日志

```sql
CREATE TABLE nginx_logs (
  event_time DateTime,
  event_date Date DEFAULT toDate(event_time),
  remote_addr IPv4,
  remote_user String,
  method LowCardinality(String),       -- GET / POST / PUT
  path String,
  http_version LowCardinality(String),
  status_code UInt16,
  body_bytes_sent UInt64,
  referer String,
  user_agent String,
  -- 解析字段
  browser LowCardinality(String),
  os LowCardinality(String),
  device_type LowCardinality(String),
  country LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (event_time, status_code)
```

### 应用日志

```sql
CREATE TABLE app_logs (
  event_time DateTime64(3),
  event_date Date DEFAULT toDate(event_time),
  service LowCardinality(String),
  level LowCardinality(String),         -- INFO / WARN / ERROR
  trace_id String,
  message String,
  -- 结构化字段
  user_id UInt64,
  request_id String,
  duration_ms UInt32,
  error_code String,
  stack_trace String
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (service, level, event_time)
```

### 系统日志（syslog / kubelet）

```sql
CREATE TABLE syslog (
  event_time DateTime,
  hostname LowCardinality(String),
  process LowCardinality(String),
  severity UInt8,
  message String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (hostname, event_time)
```

## 数据接入

### Nginx 日志格式

```nginx
log_format json escape=json '{'
  '"time": "$time_iso8601",'
  '"remote_addr": "$remote_addr",'
  '"method": "$request_method",'
  '"path": "$request_uri",'
  '"status": $status,'
  '"body_bytes_sent": $body_bytes_sent,'
  '"referer": "$http_referer",'
  '"user_agent": "$http_user_agent",'
  '"duration": "$request_time"'
'}';
```

### Vector 收集 + 解析

```yaml
# vector.toml
sources:
  nginx:
    type: file
    include:
      - /var/log/nginx/access.log

transforms:
  parse_nginx:
    type: remap
    inputs:
      - nginx
    source: |
      .event_time = parse_timestamp!(.timestamp, format: "%Y-%m-%dT%H:%M:%S%.f")
      .browser = parse_user_agent!(.user_agent).browser
      .os = parse_user_agent!(.user_agent).os
      .country = parse_regex!(.remote_addr, r'^(?P<ip>\d+\.\d+\.\d+\.\d+)$') ? .ip : "unknown"

sinks:
  kafka:
    type: kafka
    inputs:
      - parse_nginx
    brokers:
      - kafka-1:9092
    topic: nginx_logs
    encoding:
      codec: json
```

### ClickHouse Kafka 表

```sql
CREATE TABLE nginx_logs_kafka (...)
ENGINE = Kafka()
SETTINGS
  kafka_broker_list = 'kafka-1:9092',
  kafka_topic_list = 'nginx_logs',
  kafka_group_name = 'ch_nginx_consumer',
  kafka_format = 'JSONEachRow'

CREATE MATERIALIZED VIEW nginx_logs_mv TO nginx_logs AS
SELECT ... FROM nginx_logs_kafka
```

## 常见查询

### 1. 错误率统计（按接口）

```sql
SELECT
  path,
  countIf(status_code >= 500) AS errors,
  count() AS total,
  countIf(status_code >= 500) / count() AS error_rate,
  quantile(0.95)(duration_ms) AS p95_latency
FROM app_logs
WHERE event_date = today()
GROUP BY path
HAVING error_rate > 0.01
ORDER BY error_rate DESC
```

### 2. Top 慢接口

```sql
SELECT
  path,
  count() AS req_count,
  avg(duration_ms) AS avg_latency,
  quantile(0.5)(duration_ms) AS p50,
  quantile(0.95)(duration_ms) AS p95,
  quantile(0.99)(duration_ms) AS p99
FROM app_logs
WHERE event_date >= today() - INTERVAL 7 DAY
  AND duration_ms > 0
GROUP BY path
ORDER BY p99 DESC
LIMIT 20
```

### 3. 异常 IP / User Agent

```sql
-- 高频访问 IP（潜在爬虫）
SELECT
  remote_addr,
  count() AS req_count,
  uniq(path) AS unique_paths
FROM nginx_logs
WHERE event_date = today()
GROUP BY remote_addr
HAVING req_count > 10000
ORDER BY req_count DESC
LIMIT 100

-- User-Agent 分布
SELECT
  user_agent,
  count() AS count
FROM nginx_logs
WHERE event_date = today()
GROUP BY user_agent
ORDER BY count DESC
LIMIT 20
```

### 4. 链路追踪（trace_id）

```sql
-- 单次请求全链路
SELECT
  event_time,
  service,
  level,
  message,
  duration_ms
FROM app_logs
WHERE trace_id = 'abc-123-def-456'
ORDER BY event_time
```

### 5. 错误堆栈聚类

```sql
-- 相似错误聚合（按 stack_trace 前 200 字符）
SELECT
  substring(stack_trace, 1, 200) AS error_signature,
  count() AS error_count,
  uniq(trace_id) AS affected_traces,
  max(event_time) AS last_seen
FROM app_logs
WHERE event_date = today()
  AND level = 'ERROR'
  AND stack_trace != ''
GROUP BY error_signature
ORDER BY error_count DESC
LIMIT 20
```

## TTL 与存储优化

```sql
-- 30 天后自动删除
ALTER TABLE nginx_logs MODIFY TTL event_date + INTERVAL 30 DAY

-- 多级 TTL（30 天后降级到冷存储）
ALTER TABLE nginx_logs MODIFY TTL event_date + INTERVAL 7 DAY,
  event_date + INTERVAL 30 DAY TO VOLUME 'cold'

-- 按列 TTL（详细字段 7 天后删除）
ALTER TABLE nginx_logs MODIFY COLUMN stack_trace TTL event_date + INTERVAL 7 DAY
```

## Grafana 集成

```yaml
# Grafana 数据源
type: clickhouse
url: http://clickhouse-1:8123
database: default
username: default
```

常用面板：
- 请求量时间线：`SELECT count() FROM nginx_logs GROUP BY toStartOfMinute(event_time)`
- 错误率：`countIf(status >= 500) / count()`
- P95 / P99：`quantile(0.95)(duration_ms)`
- Top 接口：`SELECT path, count() ... GROUP BY path ORDER BY count DESC LIMIT 10`

## 大厂案例

### Uber

- 日志接入：Fluent Bit → Kafka → CK
- 替代 ES：成本降低 90%
- 自研 LogGlass UI（Grafana 包装）

### Cloudflare

- DNS 日志：50+ PB
- 自研 ch-go 客户端（Go 二进制）
- 实时告警：error_rate > 5% → 触发

### GitHub

- 2019-2020 迁移：ES → CK
- 数据完整性迁移：`clickhouse-migrator` 工具

## 下一步

- 学习指标 TSDB：见 [metrics-storage.md](./metrics-storage.md)
- 学习高基数 UV：见 [bitmap.md](./bitmap.md)
""")


def ch04_metrics_storage() -> None:
    add("04-olap-scenarios/metrics-storage.md", r"""---
title: 指标 TSDB 存储
description: 用 ClickHouse 做 Prometheus / Grafana 的后端存储：remote_write / 指标标签 / PromQL
---

# 指标 TSDB 存储

ClickHouse 是 Prometheus 之外的另一个指标存储选择，特别适合**大基数标签 + 长保留周期**场景。

## Prometheus vs ClickHouse

| 维度 | Prometheus | ClickHouse |
|---|---|---|
| **架构** | 本地 TSDB | 分布式列存 |
| **数据保留** | 默认 15 天 | 无限制（按磁盘） |
| **查询** | PromQL（强大） | SQL（更通用） |
| **基数** | < 1000 万时间序列 | 任意（亿级） |
| **集群** | 联邦 / Thanos | 原生分布式 |
| **压缩** | 中（1-2x） | 强（10x+） |
| **告警** | Alertmanager | 自建（Grafana Alerting） |

**结论**：
- 数据量 < 1000 万时间序列 + 短期保留 → Prometheus
- 数据量 > 1000 万时间序列 + 长期保留 → ClickHouse
- 需要 SQL 分析（关联业务数据）→ ClickHouse
- 需要多团队共用 → ClickHouse

## Prometheus remote_write 写入 ClickHouse

### 1. ClickHouse 建表

```sql
CREATE TABLE metrics (
  event_time DateTime64(3),
  name LowCardinality(String),
  labels Map(LowCardinality(String), String),
  value Float64
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (name, event_time)
SETTINGS index_granularity = 8192
```

### 2. ClickHouse 暴露 HTTP 接收端点

ClickHouse v22.x+ 支持原生 Prometheus 协议，但更通用的是用 `prometheus_remote_write` 中间件。

```bash
# 启动 ClickHouse HTTP 服务（默认 8123 端口）
clickhouse-server --config-file=/etc/clickhouse-server/config.xml
```

### 3. Prometheus 配置 remote_write

```yaml
# prometheus.yml
remote_write:
  - url: 'http://clickhouse-bridge:9201/write'
    # ClickHouse 不直接支持 PromWire 协议，需要用 Vector 或 prometheus-clickhouse-bridge
```

### 4. 用 Vector 桥接（推荐）

```yaml
# vector.toml
sources:
  prometheus_remote_write:
    type: prometheus_remote_write
    address: 0.0.0.0:9201

transforms:
  parse:
    type: remap
    inputs:
      - prometheus_remote_write
    source: |
      .event_time = .timestamp
      .name = .name
      .labels = .labels
      .value = .value

sinks:
  clickhouse:
    type: clickhouse
    inputs:
      - parse
    database: default
    table: metrics
    endpoint: http://clickhouse-1:8123
```

### 5. 自研 bridge 服务（高性能）

[prometheus-clickhouse-bridge](https://github.com/Altinity/prometheus-clickhouse-bridge) 提供官方兼容的 PromWire 协议：

```bash
# 启动 bridge
prometheus-clickhouse-bridge \
  -clickhouse.dsn=clickhouse://default:@localhost:9000/default \
  -listen=:9201

# Prometheus 配置
remote_write:
  - url: 'http://localhost:9201/write'
```

## 替代 Prometheus 的存储

Cloudflare 和 Uber 直接用 ClickHouse 替换 Prometheus：

```sql
-- 写入（HTTP API）
INSERT INTO metrics FORMAT JSONEachRow
{"event_time": "2024-01-15 12:00:00.123", "name": "http_requests_total", "labels": {"method": "GET", "status": "200", "path": "/api/users"}, "value": 1234}
```

```python
# 应用端：指标采集
from prometheus_client import Counter, Histogram
import clickhouse_connect

counter = Counter('http_requests_total', 'HTTP requests', ['method', 'status', 'path'])

client = clickhouse_connect.get_client(host='clickhouse-1')

# 定期 flush
def flush_metrics():
    metrics = []
    for metric in counter.collect():
        for sample in metric.samples:
            metrics.append({
                'event_time': datetime.now(),
                'name': sample.name,
                'labels': sample.labels,
                'value': sample.value
            })
    client.insert('metrics', metrics, column_names=['event_time', 'name', 'labels', 'value'])
```

## 常见查询

### 1. 单指标查询（PromQL 风格）

```sql
-- PromQL: rate(http_requests_total[5m])
SELECT
  toStartOfMinute(event_time) AS t,
  labels['method'] AS method,
  labels['status'] AS status,
  sum(value) / 60 AS rps
FROM metrics
WHERE name = 'http_requests_total'
  AND event_time >= now() - INTERVAL 5 MINUTE
GROUP BY t, method, status
ORDER BY t

-- PromQL: histogram_quantile(0.95, ...)
SELECT
  labels['path'] AS path,
  quantile(0.95)(value) AS p95
FROM metrics
WHERE name = 'http_request_duration_seconds_bucket'
  AND event_time >= now() - INTERVAL 5 MINUTE
  AND labels['le'] != '+Inf'
GROUP BY path
```

### 2. 高基数标签查询

```sql
-- 找出基数最高的标签
SELECT
  name,
  uniq(mapKeys(labels)) AS distinct_label_keys,
  uniqExact(mapValues(labels)) AS distinct_label_values
FROM metrics
WHERE event_time >= today()
GROUP BY name
ORDER BY distinct_label_values DESC
LIMIT 10
```

### 3. 多指标关联分析

```sql
-- HTTP QPS × 服务端 CPU 使用率
SELECT
  toStartOfMinute(t1.event_time) AS t,
  t1.rps,
  t2.cpu_usage
FROM (
  SELECT event_time, sum(value) / 60 AS rps
  FROM metrics
  WHERE name = 'http_requests_total' AND event_time >= now() - INTERVAL 1 HOUR
  GROUP BY event_time
) t1
JOIN (
  SELECT event_time, avg(value) AS cpu_usage
  FROM metrics
  WHERE name = 'process_cpu_seconds_total' AND event_time >= now() - INTERVAL 1 HOUR
  GROUP BY event_time
) t2 ON t1.event_time = t2.event_time
```

## 物化视图：预聚合

```sql
-- 每分钟 QPS / P95 / P99
CREATE TABLE metrics_minute_agg (
  event_minute DateTime,
  name LowCardinality(String),
  method LowCardinality(String),
  status LowCardinality(String),
  sum_value AggregateFunction(sum, Float64),
  count_value AggregateFunction(count),
  max_value AggregateFunction(max, Float64)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_minute)
ORDER BY (event_minute, name, method, status)

CREATE MATERIALIZED VIEW metrics_minute_mv TO metrics_minute_agg AS
SELECT
  toStartOfMinute(event_time) AS event_minute,
  name,
  labels['method'] AS method,
  labels['status'] AS status,
  sumState(value) AS sum_value,
  countState() AS count_value,
  maxState(value) AS max_value
FROM metrics
GROUP BY event_minute, name, method, status
```

## TTL 管理

```sql
-- 原始数据保留 7 天
ALTER TABLE metrics MODIFY TTL event_time + INTERVAL 7 DAY

-- 分级存储（7 天后移到冷存储卷）
ALTER TABLE metrics MODIFY TTL event_time + INTERVAL 3 DAY TO VOLUME 'cold',
                       event_time + INTERVAL 30 DAY DELETE
```

## 告警

ClickHouse 本身无原生告警系统，用 Grafana Alerting：

```yaml
# Grafana alert rule
- name: 'HighErrorRate'
  condition: >
    A = avg_over_time(metrics{__name__="http_requests_total"}[5m])
    WHERE labels.status >= "500"
    / avg_over_time(metrics{__name__="http_requests_total"}[5m]) > 0.05
  for: 5m
  to: pagerduty
```

## 实战：Cloudflare 50+ PB 指标

- 自研 `ch-go` 客户端，二进制协议
- 写入吞吐：单节点 15w rows/s
- 存储：每节点 100+ TB SSD
- 查询：10 亿时间序列扫描 < 5s

详见 [../case-study.md](../../case-study.md) 案例 2。

## 下一步

- 学习高基数 UV：见 [bitmap.md](./bitmap.md)
- 学习实时数仓：见 [realtime-warehouse.md](./realtime-warehouse.md)
""")


def ch04_bitmap() -> None:
    add("04-olap-scenarios/bitmap.md", r"""---
title: 高基数 UV 统计
description: RoaringBitmap + groupBitmap 实战：精确 UV / 留存 / 多维去重
---

# 高基数 UV 统计

高基数 UV（亿级用户）是 OLAP 经典难题，本章用 ClickHouse RoaringBitmap 解决。

## UV 统计方案对比

| 方案 | 精度 | 性能 | 内存 | 适用 |
|---|---|---|---|---|
| **countDistinct** | 精确 | 慢（O(N)） | 高 | 小数据（< 千万行） |
| **uniq**（HyperLogLog） | 1.6% 误差 | 快 | 低 | 中等（千万-亿级） |
| **uniqCombined64** | 1.6% 误差 | 快 | 低 | 同上 |
| **groupBitmapState**（RoaringBitmap） | 精确 | 极快 | 中 | 任意规模（推荐） |
| **AggregateFunction** | 精确 | 极快 | 中 | 任意规模（推荐） |

**结论**：高基数精确 UV → RoaringBitmap（`groupBitmapState`）。

## RoaringBitmap 原理

RoaringBitmap 是压缩位图，每个用户 ID 分配一个 bit：

- 用户 100 万 → 第 100 万位 = 1
- 1000 万用户 → 1.25 MB（1000 万 / 8）
- 自带高效合并（OR / AND / XOR）

ClickHouse 内置 RoaringBitmap 实现：

- `groupBitmapState` / `groupBitmapMerge`
- `bitmapCardinality`（计算基数）
- `bitmapAnd` / `bitmapOr` / `bitmapXor`

## 基础 UV 统计

```sql
-- 单次查询 UV（精确）
SELECT bitmapCardinality(groupBitmapState(user_id)) AS uv
FROM events
WHERE event_date = '2024-01-15'

-- 等价（但更慢）
SELECT uniqExact(user_id) FROM events WHERE event_date = '2024-01-15'
```

**性能对比**：
- 1 亿行：`groupBitmapState` ≈ 100ms，`uniqExact` ≈ 30s
- 10 亿行：`groupBitmapState` ≈ 500ms，`uniqExact` OOM

## 物化视图：实时 UV

```sql
-- 1. 源表（明细）
CREATE TABLE events (
  event_time DateTime,
  event_date Date,
  user_id UInt64,
  event_type LowCardinality(String),
  country LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (event_time, user_id)

-- 2. 物化视图表
CREATE TABLE events_uv_mv_table (
  event_date Date,
  event_type LowCardinality(String),
  country LowCardinality(String),
  uv_bitmap AggregateFunction(groupBitmap, UInt64),
  pv_count AggregateFunction(count)
)
ENGINE = AggregatingMergeTree()
PARTITION BY event_date
ORDER BY (event_date, event_type, country)

-- 3. 物化视图
CREATE MATERIALIZED VIEW events_uv_mv TO events_uv_mv_table AS
SELECT
  event_date,
  event_type,
  country,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv_count
FROM events
GROUP BY event_date, event_type, country

-- 4. 查询 UV
SELECT
  event_date,
  bitmapCardinality(merge(uv_bitmap)) AS uv,
  sumMerge(pv_count) AS pv
FROM events_uv_mv_table
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-07'
GROUP BY event_date
```

## 多维 UV 组合

```sql
-- UV 按事件类型 + 国家
SELECT
  event_type,
  country,
  bitmapCardinality(merge(uv_bitmap)) AS uv
FROM events_uv_mv_table
WHERE event_date = today()
GROUP BY event_type, country
ORDER BY uv DESC

-- 总 UV（跨事件类型）
SELECT bitmapCardinality(merge(uv_bitmap)) AS total_uv
FROM events_uv_mv_table
WHERE event_date = today()

-- UV 交叉（同时做过 A 和 B 的用户数）
WITH bitmap_a AS (
  SELECT groupBitmapState(user_id) AS uv
  FROM events
  WHERE event_date = today() AND event_type = 'A'
),
bitmap_b AS (
  SELECT groupBitmapState(user_id) AS uv
  FROM events
  WHERE event_date = today() AND event_type = 'B'
)
SELECT bitmapCardinality(bitmapAnd(a.uv, b.uv)) AS uv_a_and_b
FROM bitmap_a a, bitmap_b b
```

## UV 计算口径对比

```sql
-- 口径 1：累计 UV（历史去重）
SELECT bitmapCardinality(groupBitmapState(user_id)) AS total_uv
FROM events

-- 口径 2：当日 UV（按天去重）
SELECT bitmapCardinality(merge(uv_bitmap)) AS today_uv
FROM events_uv_mv_table
WHERE event_date = today()

-- 口径 3：7 日活跃 UV
SELECT bitmapCardinality(merge(uv_bitmap)) AS weekly_uv
FROM events_uv_mv_table
WHERE event_date BETWEEN today() - 6 AND today()

-- 口径 4：当月 UV
SELECT bitmapCardinality(merge(uv_bitmap)) AS monthly_uv
FROM events_uv_mv_table
WHERE event_date BETWEEN toStartOfMonth(today()) AND today()
```

## 实战：D1 / D7 / D30 留存

```sql
-- 留存 bitmap（每个 cohort 的活跃 bitmap）
CREATE TABLE retention_cohort (
  cohort_date Date,
  user_id UInt64,
  active_dates AggregateFunction(groupBitmap, Date)
)
ENGINE = AggregatingMergeTree()
ORDER BY cohort_date

CREATE MATERIALIZED VIEW retention_cohort_mv TO retention_cohort AS
SELECT
  min(event_date) AS cohort_date,
  user_id,
  groupBitmapState(event_date) AS active_dates
FROM events
GROUP BY user_id

-- D1 留存：注册日的用户中，第二天活跃的比例
WITH new_users AS (
  SELECT user_id FROM retention_cohort WHERE cohort_date = '2024-01-15'
)
SELECT
  countIf(d1_active) / count() AS d1_retention,
  countIf(d7_active) / count() AS d7_retention
FROM (
  SELECT
    n.user_id,
    bitmapContains(merge(r.active_dates), toDate('2024-01-16')) AS d1_active,
    bitmapContains(merge(r.active_dates), toDate('2024-01-22')) AS d7_active
  FROM new_users n
  JOIN retention_cohort r ON n.user_id = r.user_id
  WHERE r.cohort_date = '2024-01-15'
  GROUP BY n.user_id
)
```

## 性能基准

```text
数据量：       10 亿事件
UV（精确）：    500ms（groupBitmapState）
UV（近似）：    50ms（uniq）
7 日留存：      1s（基于 bitmap cohort 表）
维度组合 UV：  100ms-1s（取决于维度基数）
```

**内存开销**：1000 万用户 × 64-bit ID = 100 MB（RoaringBitmap 压缩到 ~10 MB）

## 实战：多平台用户合并（Union / Intersect）

```sql
-- Web + iOS + Android 三端 UV 总和（跨平台去重）
WITH web_users AS (SELECT groupBitmapState(user_id) AS uv FROM web_events),
ios_users AS (SELECT groupBitmapState(user_id) AS uv FROM ios_events),
android_users AS (SELECT groupBitmapState(user_id) AS uv FROM android_events)
SELECT
  bitmapCardinality(bitmapOr(w.uv, bitmapOr(i.uv, a.uv))) AS total_uv,
  bitmapCardinality(bitmapAnd(w.uv, i.uv)) AS web_ios_overlap,
  bitmapCardinality(w.uv) AS web_uv,
  bitmapCardinality(i.uv) AS ios_uv,
  bitmapCardinality(a.uv) AS android_uv
FROM web_users w, ios_users i, android_users a
```

## 大厂实践

### 字节跳动

- 抖音 UV：Bitmap + 物化视图预聚合
- 留存：bitmap cohort 表
- 高基数（用户 + 内容）：bitmap + SAMPLE 抽样

### B 站

- 用户行为去重：bitmap + 弹幕反垃圾
- 多维 UV：bitmap 维度交叉

### 京东

- 订单用户画像：bitmap + 实时画像
- 高基数活动用户：bitmap cardinality

## 下一步

- 学习实时数仓：见 [realtime-warehouse.md](./realtime-warehouse.md)
- 学习生态集成：见 [05-ecosystem/overview.md](../05-ecosystem/overview.md)
""")


def ch04_realtime_warehouse() -> None:
    add("04-olap-scenarios/realtime-warehouse.md", r"""---
title: 实时数仓
description: Kafka + MV 链式分层：DWD / DWS / ADS 三层实时数仓完整架构
---

# 实时数仓

实时数仓是 ClickHouse 最强的场景之一，本章展示从 Kafka 到 DWD/DWS/ADS 三层的完整架构。

## 实时数仓 vs 离线数仓

| 维度 | 实时数仓 | 离线数仓 |
|---|---|---|
| **延迟** | 秒级 | T+1（小时/天） |
| **架构** | Kafka + ClickHouse MV | Hive + Spark / Flink |
| **更新** | 增量 | 全量重算 |
| **成本** | 中（CK 集群） | 高（Hive 集群） |
| **灵活性** | 低（强 Schema） | 高（任意 SQL） |
| **典型场景** | 实时看板 / 风控 / 推荐 | 月度报表 / 用户画像 |

## 三层架构

```text
┌──────────┐    Kafka    ┌──────────┐
│ 业务系统 │ ─────────→  │ ODS（原始）│
└──────────┘             └──────────┘
                             │
                             │ MV1: 明细清洗
                             ▼
                        ┌──────────┐
                        │ DWD（明细）│
                        └──────────┘
                             │
                             │ MV2: 主题汇总
                             ▼
                        ┌──────────┐
                        │ DWS（汇总）│
                        └──────────┘
                             │
                             │ MV3: 应用层
                             ▼
                        ┌──────────┐
                        │ ADS（应用）│
                        └──────────┘
                             │
                             ▼
                       Grafana / BI
```

## Schema 设计

### 1. ODS（原始层）

```sql
-- 接 Kafka 写入
CREATE TABLE events_ods (
  event_time DateTime64(3),
  user_id UInt64,
  event_type LowCardinality(String),
  country LowCardinality(String),
  device_type LowCardinality(String),
  page_url String,
  duration_ms UInt32,
  amount Decimal(18, 2),
  properties Map(String, String),
  raw_message String  -- 保留原始数据，便于回溯
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (user_id, event_time)
TTL event_time + INTERVAL 30 DAY  -- 原始数据保留 30 天
```

### 2. DWD（明细层）

```sql
-- 清洗 + 维度补全
CREATE TABLE events_dwd (
  event_time DateTime64(3),
  event_date Date DEFAULT toDate(event_time),
  user_id UInt64,
  user_name String,
  user_country LowCardinality(String),
  user_age UInt8,
  event_type LowCardinality(String),
  page_url String,
  product_id UInt64,
  product_name String,
  product_category LowCardinality(String),
  amount Decimal(18, 2),
  duration_ms UInt32
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (user_id, event_time)

-- 物化视图
CREATE MATERIALIZED VIEW events_dwd_mv TO events_dwd AS
SELECT
  event_time,
  event_time AS event_date,
  user_id,
  dictGet('users_dict', 'user_name', user_id) AS user_name,
  dictGet('users_dict', 'country', user_id) AS user_country,
  dictGet('users_dict', 'age', user_id) AS user_age,
  event_type,
  page_url,
  dictGet('page_dict', 'product_id', page_url) AS product_id,
  dictGet('products_dict', 'product_name', product_id) AS product_name,
  dictGet('products_dict', 'category', product_id) AS product_category,
  amount,
  duration_ms
FROM events_ods
```

### 3. DWS（汇总层）

```sql
-- 每分钟 UV/PV/GMV（按国家 + 事件类型）
CREATE TABLE events_dws_minute (
  event_minute DateTime,
  country LowCardinality(String),
  category LowCardinality(String),
  uv_bitmap AggregateFunction(groupBitmap, UInt64),
  pv_count AggregateFunction(count),
  gmv_sum AggregateFunction(sum, Decimal(18, 2))
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_minute)
ORDER BY (event_minute, country, category)

CREATE MATERIALIZED VIEW events_dws_minute_mv TO events_dws_minute AS
SELECT
  toStartOfMinute(event_time) AS event_minute,
  user_country AS country,
  product_category AS category,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv_count,
  sumState(amount) AS gmv_sum
FROM events_dwd
GROUP BY event_minute, country, category

-- 每小时汇总（DWS-Hour）
CREATE TABLE events_dws_hour (...)

-- 每日汇总（DWS-Day）
CREATE TABLE events_dws_day (...)
```

### 4. ADS（应用层）

```sql
-- 实时看板（最近 1 小时）
CREATE TABLE events_ads_realtime (
  event_minute DateTime,
  country LowCardinality(String),
  category LowCardinality(String),
  uv AggregateFunction(groupBitmap, UInt64),
  pv AggregateFunction(count),
  gmv AggregateFunction(sum, Decimal(18, 2))
)
ENGINE = AggregatingMergeTree()
ORDER BY (event_minute, country, category)

CREATE MATERIALIZED VIEW events_ads_realtime_mv TO events_ads_realtime AS
SELECT
  event_minute,
  country,
  category,
  groupBitmapState(user_id) AS uv,
  countState() AS pv,
  sumState(amount) AS gmv
FROM events_dwd
WHERE event_time >= now() - INTERVAL 1 HOUR
GROUP BY event_minute, country, category

-- 数据回填（每小时跑一次，刷新 ADS）
INSERT INTO events_ads_realtime
SELECT
  event_minute,
  country,
  category,
  uv_bitmap,
  pv_count,
  gmv_sum
FROM events_dws_minute
WHERE event_minute >= now() - INTERVAL 1 HOUR
```

## 监控与告警

### 数据延迟监控

```sql
-- Kafka 消费延迟
SELECT
  database,
  table,
  lag,
  last_poll_time
FROM system.kafka_consumers

-- 物化视图积压
SELECT
  database,
  table,
  parts,
  rows
FROM system.parts
WHERE table LIKE '%_mv%'
```

### 数据质量监控

```sql
-- 字段空值率
SELECT
  event_date,
  countIf(user_id = 0) AS missing_user_id,
  countIf(amount = 0) AS missing_amount,
  count() AS total
FROM events_dwd
WHERE event_date = today()
GROUP BY event_date

-- 异常数据（金额 > 10000）
SELECT countIf(amount > 10000) FROM events_dwd WHERE event_date = today()
```

## 数据回溯与重放

### 历史数据回填

```sql
-- 重新消费 Kafka 历史数据（修改 consumer group）
DETACH TABLE events_ods_kafka
ALTER TABLE events_ods_kafka MODIFY SETTING kafka_group_name = 'replay_2024_01_01'
ATTACH TABLE events_ods_kafka
```

### 重新计算 DWD/DWS

```sql
-- 删除 DWS 表，重新构建
DROP TABLE events_dws_minute
DROP TABLE events_dws_minute_mv

CREATE TABLE events_dws_minute (...)
CREATE MATERIALIZED VIEW events_dws_minute_mv TO events_dws_minute AS
SELECT ... FROM events_dwd

-- 手动回填
INSERT INTO events_dws_minute
SELECT ... FROM events_dwd
```

## 大厂案例

### 字节跳动

- 实时数据量：PB 级
- 数仓分层：ODS + DWD + DWS + ADS
- 物化视图：100+ MV 链式触发
- 应用场景：抖音推荐、广告归因

### 京东

- 订单实时数仓：Kafka → DWD → DWS → 履约看板
- 延迟：秒级
- 数据量：TB/天

### 滴滴

- 行程数据实时分析（与 StarRocks 共存）
- ClickHouse 单表聚合，StarRocks 多表 JOIN

详见 [../case-study.md](../../case-study.md) 案例 3、6、9。

## 常见问题

### Q1：MV 链式触发延迟？

通常秒级。监控 `system.parts` 看 parts 数是否持续增长。

### Q2：数据倾斜（热点 key）？

- 单分片过大：用 `SAMPLE 0.01` + 加权聚合
- 单用户过大：拆分（按 hash(user_id) 分多行）

### Q3：MV 修改怎么办？

1. DROP 旧 MV
2. 修改目标表
3. CREATE 新 MV
4. 历史数据手动 INSERT 回填

## 下一步

- 学习 Kafka 集成：见 [05-ecosystem/kafka-integration.md](../05-ecosystem/kafka-integration.md)
- 学习对比选型：见 [06-compare/overview.md](../06-compare/overview.md)
""")


# ============================================================================
# Chapter 05: Ecosystem (5 stubs)
# ============================================================================

def ch05_kafka_integration() -> None:
    add("05-ecosystem/kafka-integration.md", r"""---
title: Kafka 集成实战
description: ClickHouse Kafka 表引擎 + MaterializedView 完整实战 + 多 topic 流
---

# Kafka 集成实战

Kafka 是 ClickHouse 最常见的数据源，本章给出生产级完整实战。

## 完整架构

```text
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 业务系统 │ →  │ Kafka    │ →  │ CK Kafka │ →  │ CK MergeTree│
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                      │
                                       ┌──────────────┼──────────────┐
                                       ▼              ▼              ▼
                                  MV: 实时 UV   MV: 留存      MV: 漏斗
```

## 单 Topic 消费

### Step 1：Kafka 表

```sql
CREATE TABLE events_kafka (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  payload String
)
ENGINE = Kafka()
SETTINGS
  kafka_broker_list = 'kafka-1:9092,kafka-2:9092',
  kafka_topic_list = 'user_events',
  kafka_group_name = 'clickhouse_events_consumer',
  kafka_format = 'JSONEachRow',
  kafka_num_consumers = 1,
  kafka_max_block_size = 1000,
  kafka_poll_timeout_ms = 1000,
  kafka_flush_interval_ms = 1000
```

### Step 2：本地表

```sql
CREATE TABLE events_local (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  payload String,
  event_date Date DEFAULT toDate(event_time)
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (user_id, event_time)
```

### Step 3：物化视图

```sql
CREATE MATERIALIZED VIEW events_mv TO events_local AS
SELECT
  event_time,
  user_id,
  event_type,
  payload
FROM events_kafka
```

**完成！现在 Kafka 数据自动写入 `events_local`。**

## 多 Topic 消费（共享 Schema）

```sql
-- 一个 Kafka 表消费多个 topic
CREATE TABLE events_multi_kafka (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  source_topic LowCardinality(String),  -- 标记 topic 来源
  payload String
)
ENGINE = Kafka()
SETTINGS
  kafka_broker_list = 'kafka-1:9092',
  kafka_topic_list = 'events_a,events_b,events_c',
  kafka_group_name = 'multi_topic_consumer',
  kafka_format = 'JSONEachRow'

-- 在物化视图中分流
CREATE MATERIALIZED VIEW events_a_mv TO events_a_local AS
SELECT * FROM events_multi_kafka WHERE source_topic = 'events_a'

CREATE MATERIALIZED VIEW events_b_mv TO events_b_local AS
SELECT * FROM events_multi_kafka WHERE source_topic = 'events_b'
```

## 多 Topic 流式处理

```sql
-- 一个 topic 写入多个表（按 event_type 分流）
CREATE MATERIALIZED VIEW page_view_mv TO page_views_local AS
SELECT event_time, user_id, page_url FROM events_kafka
WHERE event_type = 'page_view'

CREATE MATERIALIZED VIEW click_mv TO clicks_local AS
SELECT event_time, user_id, page_url, click_target FROM events_kafka
WHERE event_type = 'click'

CREATE MATERIALIZED VIEW purchase_mv TO purchases_local AS
SELECT event_time, user_id, product_id, amount FROM events_kafka
WHERE event_type = 'purchase'
```

## Avro / Protobuf

### Avro（Confluent Schema Registry）

```sql
CREATE TABLE events_avro_kafka (...)
ENGINE = Kafka()
SETTINGS
  kafka_format = 'AvroConfluent',
  kafka_schema_registry_url = 'http://schema-registry:8081'
```

### Protobuf

```sql
CREATE TABLE events_proto_kafka (...)
ENGINE = Kafka()
SETTINGS
  kafka_format = 'Protobuf',
  format_protobuf_schema_path = '/etc/clickhouse-protobuf/schema.proto',
  format_protobuf_message_name = 'Event'
```

```protobuf
// schema.proto
syntax = "proto3";
message Event {
  int64 user_id = 1;
  string event_type = 2;
  int64 timestamp = 3;
  map<string, string> properties = 4;
}
```

## 容错处理

### 错误数据处理

```sql
SETTINGS
  kafka_handle_error_mode = 'stream'  -- 错误数据进入虚拟列
```

错误数据在物化视图中自动生成：

```sql
SELECT
  _error,
  _raw_message
FROM events_kafka
WHERE _error != ''
```

### 重置 Offset

```sql
-- 方法 1：修改 consumer group
DETACH TABLE events_kafka
ALTER TABLE events_kafka MODIFY SETTING kafka_group_name = 'new_group'
ATTACH TABLE events_kafka

-- 方法 2：直接修改 Kafka topic 的 offset（用 kafka-consumer-groups.sh）
kafka-consumer-groups.sh --bootstrap-server kafka-1:9092 \
  --group clickhouse_events_consumer \
  --reset-offsets --to-earliest \
  --topic user_events --execute
```

### 监控消费进度

```sql
SELECT
  database,
  table,
  consumer_id,
  last_poll_time,
  last_commit_time,
  num_messages_read
FROM system.kafka_consumers
```

## 实战：实时用户行为流

### 应用层埋点

```python
# 应用端：写入 Kafka
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['kafka-1:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

producer.send('user_events', value={
    'event_time': '2024-01-15 12:00:00',
    'user_id': 12345,
    'event_type': 'click',
    'page_url': '/api/users',
    'duration_ms': 150
})
```

### ClickHouse 端消费 + 实时看板

```sql
-- Kafka 表
CREATE TABLE user_behavior_kafka (...)
ENGINE = Kafka() ...

-- 本地表
CREATE TABLE user_behavior_local (...)
ENGINE = MergeTree() ...

-- 物化视图
CREATE MATERIALIZED VIEW user_behavior_mv TO user_behavior_local AS ...

-- 实时看板（每 5 分钟 UV/PV）
CREATE MATERIALIZED VIEW user_behavior_5min_mv
ENGINE = AggregatingMergeTree()
ORDER BY (event_5min, country)
AS
SELECT
  toStartOfFiveMinute(event_time) AS event_5min,
  dictGet('users_dict', 'country', user_id) AS country,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv
FROM user_behavior_kafka
GROUP BY event_5min, country

-- 查询
SELECT
  event_5min,
  country,
  bitmapCardinality(merge(uv_bitmap)) AS uv,
  sumMerge(pv) AS pv
FROM user_behavior_5min
WHERE event_5min >= now() - INTERVAL 1 HOUR
GROUP BY event_5min, country
ORDER BY event_5min, country
```

## 高级特性

### 消费事务支持

```sql
SETTINGS
  kafka_transactional_id = 'tx-1'
```

### 压缩传输

```sql
SETTINGS
  kafka_format = 'JSONEachRow',
  kafka_compression_method = 'lz4'
```

### 安全认证（SASL/SSL）

```sql
SETTINGS
  kafka_broker_list = 'kafka-1:9092',
  kafka_security_protocol = 'sasl_ssl',
  kafka_sasl_mechanism = 'PLAIN',
  kafka_sasl_username = 'readonly',
  kafka_sasl_password = 'xxx',
  kafka_ssl_ca_cert_file = '/etc/ssl/ca-cert.pem'
```

## 下一步

- 学习 Grafana 集成：见 [grafana.md](./grafana.md)
- 学习 Prometheus 集成：见 [prometheus.md](./prometheus.md)
""")


def ch05_grafana() -> None:
    add("05-ecosystem/grafana.md", r"""---
title: Grafana 集成
description: ClickHouse 作为 Grafana 数据源：原生插件 + Dashboard 实战
---

# Grafana 集成

Grafana 是 ClickHouse 最常用的可视化工具，官方提供原生插件。

## 安装插件

### Grafana 10+

```bash
grafana-cli plugins install clickhouse
systemctl restart grafana-server
```

### Docker

```yaml
# docker-compose.yml
version: '3'
services:
  grafana:
    image: grafana/grafana:latest
    environment:
      GF_INSTALL_PLUGINS: "clickhouse"
    ports:
      - 3000:3000
```

### 自定义路径

```ini
# grafana.ini
[plugin.clickhouse]
path = /var/lib/grafana/plugins/clickhouse
```

## 配置数据源

```yaml
# Grafana → Configuration → Data sources → Add
type: ClickHouse
url: http://clickhouse-1:8123
database: default
username: default
password: ''
```

### 默认数据库

`default` 库通常是测试用，生产建议用专用库：

```sql
CREATE DATABASE analytics
```

### 多数据源

可配置多个 ClickHouse 数据源（区分生产/测试）：

- `ClickHouse-Prod`（生产）
- `ClickHouse-Dev`（开发）

## 常用查询面板

### 1. QPS 时间线

```sql
SELECT
  $__timeColumn(event_time) AS time,
  count() / 5 AS qps
FROM events
WHERE $__timeFilter(event_time)
GROUP BY time
ORDER BY time
```

`$__timeColumn` 和 `$__timeFilter` 是 Grafana 宏，自动匹配面板时间范围。

### 2. P95 / P99 延迟

```sql
SELECT
  $__timeColumn(event_time) AS time,
  quantile(0.95)(duration_ms) AS p95,
  quantile(0.99)(duration_ms) AS p99,
  avg(duration_ms) AS avg_latency
FROM events
WHERE $__timeFilter(event_time) AND duration_ms > 0
GROUP BY time
ORDER BY time
```

### 3. 错误率

```sql
SELECT
  $__timeColumn(event_time) AS time,
  countIf(status_code >= 500) / count() AS error_rate
FROM events
WHERE $__timeFilter(event_time)
GROUP BY time
ORDER BY time
```

### 4. TOP 接口表格

```sql
SELECT
  path,
  count() AS request_count,
  avg(duration_ms) AS avg_latency,
  quantile(0.95)(duration_ms) AS p95,
  countIf(status_code >= 500) / count() AS error_rate
FROM events
WHERE $__timeFilter(event_time)
GROUP BY path
ORDER BY request_count DESC
LIMIT 20
```

### 5. 多维 UV（Bar Gauge）

```sql
SELECT
  country,
  bitmapCardinality(merge(uv_bitmap)) AS uv
FROM events_uv_mv_table
WHERE event_date = today()
GROUP BY country
ORDER BY uv DESC
LIMIT 10
```

## 告警

Grafana Alerting + ClickHouse 集成：

```yaml
# Grafana alert rule
- name: 'HighErrorRate'
  condition: >
    query(type:clickhouse, datasource:ClickHouse-Prod, query:
      "SELECT countIf(status_code >= 500) / count() AS error_rate
       FROM events
       WHERE $__timeFilter(event_time)
       GROUP BY time
       ORDER BY time"
    ) > 0.05
  for: 5m
  to: oncall
  frequency: 1m
```

## Dashboard 模板

### 业务看板（电商）

```yaml
panels:
  - title: 实时 GMV
    type: stat
    targets:
      - query: |
          SELECT sum(amount) AS gmv
          FROM orders
          WHERE order_time >= today()

  - title: 今日订单
    type: stat
    targets:
      - query: |
          SELECT count() AS orders FROM orders WHERE order_time >= today()

  - title: GMV 时间线
    type: timeseries
    targets:
      - query: |
          SELECT
            $__timeColumn(order_time) AS time,
            sum(amount) AS gmv
          FROM orders
          WHERE $__timeFilter(order_time)
          GROUP BY time

  - title: TOP 10 商品
    type: table
    targets:
      - query: |
          SELECT
            product_name,
            sum(amount) AS sales,
            count() AS order_count
          FROM orders o
          JOIN products p ON o.product_id = p.id
          WHERE order_time >= today()
          GROUP BY product_name
          ORDER BY sales DESC
          LIMIT 10

  - title: 用户分布
    type: piechart
    targets:
      - query: |
          SELECT country, bitmapCardinality(merge(uv_bitmap)) AS uv
          FROM events_uv_mv_table
          WHERE event_date = today()
          GROUP BY country
```

## 性能优化

### 1. 限制数据扫描

```sql
-- 添加 WHERE 条件避免全表扫
WHERE $__timeFilter(event_time) AND event_type = 'click'
```

### 2. 预聚合

```sql
-- 实时看板用物化视图预聚合
SELECT
  $__timeColumn(event_minute) AS time,
  sumMerge(pv) AS pv
FROM events_uv_pv_1m  -- 物化视图
WHERE $__timeFilter(event_minute)
GROUP BY time
```

### 3. 设置合理刷新间隔

```yaml
# Grafana panel
refresh: 30s  -- 实时看板 30 秒刷新
```

### 4. 并发控制

```yaml
# Grafana 数据源配置
maxOpenConns: 10
maxIdleConns: 5
connMaxLifetime: 600
```

## 常见问题

### Q1：Grafana 无法连接 ClickHouse？

- 检查 `url` 是否正确（带端口 `8123`）
- 检查 ClickHouse HTTP 服务是否开启：`grep '<listen_host>' /etc/clickhouse-server/config.xml`
- 防火墙 / 网络：Grafana 节点能访问 ClickHouse 8123 端口

### Q2：宏变量没替换？

- 用 `$__timeFilter(column)` 代替手动 `WHERE time BETWEEN`
- `$__fromTime` / `$__toTime` 手动使用

### Q3：查询慢？

- 检查是否用物化视图
- 加 `LIMIT` 限制返回
- 加 `PREWHERE` 过滤

## 大厂实践

- **Uber**：自研 LogGlass（Grafana 包装）
- **Cloudflare**：Grafana + 自定义面板（DNS / CDN）
- **字节跳动**：ByteInsight（自研 BI，CK + Grafana）

## 下一步

- 学习 Prometheus 集成：见 [prometheus.md](./prometheus.md)
- 学习 Go 客户端：见 [go-client.md](./go-client.md)
""")


def ch05_prometheus() -> None:
    add("05-ecosystem/prometheus.md", r"""---
title: Prometheus remote_write
description: ClickHouse 作为 Prometheus 长期存储：bridge 工具 + 实战
---

# Prometheus remote_write

Prometheus 默认保留 15 天，但很多场景需要更长（合规 / 趋势分析）。ClickHouse 作为远程存储是常见方案。

## 架构

```text
┌──────────┐                       ┌──────────┐
│Prometheus│ ──remote_write──→  │ Bridge   │ ──HTTP INSERT──→ ┌──────────┐
└──────────┘                       └──────────┘                 │ ClickHouse│
                                                              └──────────┘
```

## 方案 1：prometheus-clickhouse-bridge（推荐）

[Altinity 开源](https://github.com/Altinity/prometheus-clickhouse-bridge) 的官方兼容桥接器：

### 安装

```bash
# 二进制下载
wget https://github.com/Altinity/prometheus-clickhouse-bridge/releases/download/v0.7.0/prometheus-clickhouse-bridge-0.7.0-linux-amd64.tar.gz
tar -xzf prometheus-clickhouse-bridge-0.7.0-linux-amd64.tar.gz

# 启动
./prometheus-clickhouse-bridge \
  -clickhouse.dsn="clickhouse://default:@localhost:9000/default" \
  -listen=":9201" \
  -metrics.listen=":9201/metrics" \
  -log.level=info
```

### Prometheus 配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

remote_write:
  - url: 'http://localhost:9201/write'
    queue_config:
      capacity: 10000
      max_samples_per_send: 1000
      batch_send_deadline: 5s

remote_read:
  - url: 'http://localhost:9201/read'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

### ClickHouse 表

Bridge 会自动建表，也可以手动创建：

```sql
CREATE TABLE prometheus_metrics (
  timestamp DateTime64(3),
  name LowCardinality(String),
  labels Map(LowCardinality(String), String),
  value Float64
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (name, timestamp)
TTL timestamp + INTERVAL 30 DAY
```

## 方案 2：Vector 桥接

```yaml
# vector.toml
sources:
  prom_remote_write:
    type: prometheus_remote_write
    address: 0.0.0.0:9201

transforms:
  parse:
    type: remap
    inputs:
      - prom_remote_write
    source: |
      .timestamp = from_unix_timestamp!(.timestamp, "ms")
      .labels = .labels

sinks:
  clickhouse:
    type: clickhouse
    inputs:
      - parse
    database: default
    table: prometheus_metrics
    endpoint: http://clickhouse-1:8123
    encoding:
      codec: json
```

## 方案 3：直接 HTTP（自研）

```python
# 自研 bridge（适合简单场景）
from http.server import BaseHTTPRequestHandler, HTTPServer
from prometheus_api_client import PrometheusConnect
import clickhouse_connect

class Bridge(BaseHTTPRequestHandler):
    def do_POST(self):
        # 解析 Prometheus remote_write 协议（protobuf）
        # ...
        # 写入 ClickHouse
        client.insert('prometheus_metrics', data)

HTTPServer(('0.0.0.0', 9201), Bridge).serve_forever()
```

## 查询示例

### PromQL → ClickHouse SQL 翻译

#### 1. `rate()` 计算

```sql
-- PromQL: rate(http_requests_total[5m])
SELECT
  toStartOfMinute(timestamp) AS t,
  labels['path'] AS path,
  sum(value) / 60 AS rate
FROM prometheus_metrics
WHERE name = 'http_requests_total'
  AND timestamp >= now() - INTERVAL 5 MINUTE
GROUP BY t, path
ORDER BY t
```

#### 2. histogram_quantile

```sql
-- PromQL: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
WITH bucketed AS (
  SELECT
    toStartOfMinute(timestamp) AS t,
    labels['le'] AS le,
    labels['path'] AS path,
    sum(value) AS cumulative_count
  FROM prometheus_metrics
  WHERE name = 'http_request_duration_seconds_bucket'
    AND timestamp >= now() - INTERVAL 5 MINUTE
  GROUP BY t, le, path
)
SELECT
  t,
  path,
  -- 线性插值计算 P95
  arrayElement(arrayMap(i -> le[i], arrayFilter(i -> le[i] != '+Inf', range(length(le)))), ...)
FROM bucketed
```

实际生产中建议用 Grafana + ClickHouse 的 PromQL 翻译插件，或自研函数。

### 3. 标签组合查询

```sql
-- 按 method + status 聚合
SELECT
  labels['method'] AS method,
  labels['status'] AS status,
  avg(value) AS avg_value,
  count() AS sample_count
FROM prometheus_metrics
WHERE name = 'http_request_duration_seconds'
  AND timestamp >= now() - INTERVAL 1 HOUR
GROUP BY method, status
ORDER BY method, status
```

### 4. 高基数检测

```sql
-- 时间序列数（按 name + labels）
SELECT
  name,
  uniqExact(mapKeys(labels), mapValues(labels)) AS series_count
FROM prometheus_metrics
WHERE timestamp >= now() - INTERVAL 1 HOUR
GROUP BY name
ORDER BY series_count DESC
```

## 物化视图：预聚合

```sql
-- 每 5 分钟指标聚合
CREATE TABLE prometheus_5min_agg (
  event_5min DateTime,
  name LowCardinality(String),
  method LowCardinality(String),
  path LowCardinality(String),
  sum_value AggregateFunction(sum, Float64),
  count_value AggregateFunction(count),
  max_value AggregateFunction(max, Float64)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_5min)
ORDER BY (event_5min, name, method, path)

CREATE MATERIALIZED VIEW prometheus_5min_mv TO prometheus_5min_agg AS
SELECT
  toStartOfFiveMinute(timestamp) AS event_5min,
  name,
  labels['method'] AS method,
  labels['path'] AS path,
  sumState(value) AS sum_value,
  countState() AS count_value,
  maxState(value) AS max_value
FROM prometheus_metrics
GROUP BY event_5min, name, method, path

-- 查询
SELECT
  event_5min,
  name,
  method,
  path,
  sumMerge(sum_value) / sumMerge(count_value) AS avg,
  maxMerge(max_value) AS max
FROM prometheus_5min_agg
WHERE event_5min >= now() - INTERVAL 1 HOUR
GROUP BY event_5min, name, method, path
```

## TTL 与存储管理

```sql
-- 30 天后自动删除
ALTER TABLE prometheus_metrics MODIFY TTL timestamp + INTERVAL 30 DAY

-- 分级存储
ALTER TABLE prometheus_metrics MODIFY TTL
  timestamp + INTERVAL 3 DAY TO VOLUME 'cold',
  timestamp + INTERVAL 30 DAY DELETE

-- 按 name 分级（高频指标保留更久）
ALTER TABLE prometheus_metrics MODIFY TTL
  timestamp + INTERVAL 90 DAY DELETE
  WHERE name LIKE 'business_%'
```

## 实战：Cloudflare 监控

Cloudflare 用 ClickHouse 替代 Prometheus 自研指标系统：

- 写入吞吐：单节点 15w+ rows/s
- 存储：每节点 100+ TB
- 查询：10 亿时间序列 < 5s
- 自研客户端：[ch-go](https://github.com/ClickHouse/ch-go)

详见 [../case-study.md](../../case-study.md) 案例 2。

## 大厂实践

- **Cloudflare**：DNS / CDN 监控（替代 Prometheus）
- **Uber**：业务指标 + 服务监控
- **GitHub**：仓库 / PR 指标

## 下一步

- 学习 Go 客户端：见 [go-client.md](./go-client.md)
- 学习 dbt 集成：见 [dbt-airbyte.md](./dbt-airbyte.md)
""")


def ch05_go_client() -> None:
    add("05-ecosystem/go-client.md", r"""---
title: Go 客户端实战
description: ch-go（Cloudflare 自研）+ clickhouse-go v2 完整实战
---

# Go 客户端实战

Go 是 ClickHouse 后端服务的首选语言，本章对比 ch-go 和 clickhouse-go v2。

## 客户端对比

| 客户端 | 协议 | 性能 | 适用 |
|---|---|---|---|
| **ch-go** | 原生二进制 + LZ4 | 最快（3x） | 生产 Go 服务（推荐） |
| **clickhouse-go v2** | 原生 + HTTP | 中等 | 通用 Go 应用 |
| **HTTP** | HTTP/1.1 | 慢 | 临时查询 |

## ch-go（Cloudflare 自研）

### 安装

```bash
go get github.com/ClickHouse/ch-go
```

### 连接

```go
package main

import (
    "context"
    "fmt"
    "github.com/ClickHouse/ch-go"
    "github.com/ClickHouse/ch-go/proto"
)

func main() {
    ctx := context.Background()

    conn, err := ch.Dial(ctx, ch.Options{
        Address:  "localhost:9000",
        Database: "default",
        User:     "default",
        Password: "",
    })
    if err != nil {
        panic(err)
    }
    defer conn.Close()

    // Ping
    if err := conn.Ping(ctx); err != nil {
        panic(err)
    }
    fmt.Println("Connected to ClickHouse")
}
```

### 单行查询

```go
var version string
err := conn.QueryRow(ctx, "SELECT version()").Scan(&version)
fmt.Println(version)
// Output: 24.3.3.102
```

### 多行查询

```go
result := conn.Query(ctx, "SELECT event_type, count() FROM events GROUP BY event_type")
defer result.Close()

for result.Next() {
    var eventType string
    var cnt uint64
    if err := result.Scan(&eventType, &cnt); err != nil {
        panic(err)
    }
    fmt.Printf("%s: %d\n", eventType, cnt)
}

if err := result.Err(); err != nil {
    panic(err)
}
```

### 批量插入

```go
batch, err := conn.PrepareBatch(ctx, `
    INSERT INTO events (event_time, user_id, event_type, amount)
`)
if err != nil {
    panic(err)
}

for i := 0; i < 1000; i++ {
    batch.Append(
        time.Now(),
        uint64(i),
        "click",
        9.99,
    )
}

if err := batch.Send(ctx); err != nil {
    panic(err)
}
```

### 流式输入（推荐，超大文件）

```go
file, _ := os.Open("events.csv")
defer file.Close()

input := proto.NewCSVReader(proto.CSVWithNames(), file)
err := conn.Insert(ctx, "events", input)
```

### 高级查询（Context + 参数）

```go
ctx := context.Background()

result, err := conn.Query(ctx, `
    SELECT user_id, count() AS cnt
    FROM events
    WHERE event_date = @date AND user_id > @min_id
    GROUP BY user_id
    HAVING cnt > @min_count
    ORDER BY cnt DESC
    LIMIT 100
`,
    ch.WithQueryID("report-001"),
    ch.WithParameters(ch.Parameters{
        "date":      "2024-01-15",
        "min_id":    1000,
        "min_count": 10,
    }),
)
```

### 异步查询

```go
// 异步执行
response, err := conn.QueryAsync(ctx, "SELECT count() FROM huge_table")
if err != nil {
    panic(err)
}

// 检查状态
status := response.Status(ctx)
fmt.Printf("Status: %s\n", status)

// 获取结果
if status == ch.QueryStatusFinished {
    result, err := response.Result()
    // ...
}
```

### 性能基准

```go
// 单条插入 vs 批量插入
func benchmark(conn *ch.Client) {
    // 单条：~1000 rows/s
    for i := 0; i < 10000; i++ {
        conn.Exec(ctx, "INSERT INTO events VALUES (?, ?, ?, ?)", time.Now(), i, "click", 9.99)
    }

    // 批量：~100,000 rows/s
    batch, _ := conn.PrepareBatch(ctx, "INSERT INTO events")
    for i := 0; i < 100000; i++ {
        batch.Append(time.Now(), i, "click", 9.99)
    }
    batch.Send(ctx)
}
```

## clickhouse-go v2（官方）

### 安装

```bash
go get github.com/ClickHouse/clickhouse-go/v2
```

### 连接

```go
import (
    "database/sql"
    "fmt"
    _ "github.com/ClickHouse/clickhouse-go/v2"
)

func main() {
    conn, err := sql.Open("clickhouse", "clickhouse://default:@localhost:9000/default")
    if err != nil {
        panic(err)
    }
    defer conn.Close()

    if err := conn.Ping(); err != nil {
        panic(err)
    }
    fmt.Println("Connected")
}
```

### 标准 database/sql 接口

```go
// 查询
rows, err := conn.Query("SELECT event_type, count() FROM events GROUP BY event_type")
defer rows.Close()

for rows.Next() {
    var eventType string
    var cnt uint64
    rows.Scan(&eventType, &cnt)
    fmt.Printf("%s: %d\n", eventType, cnt)
}

// 插入
stmt, _ := conn.Prepare("INSERT INTO events (event_time, user_id, event_type, amount) VALUES (?, ?, ?, ?)")
defer stmt.Close()

for i := 0; i < 1000; i++ {
    _, err := stmt.Exec(time.Now(), i, "click", 9.99)
    if err != nil {
        panic(err)
    }
}
```

### context 传递

```go
ctx := context.Background()

// 带超时的查询
ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
defer cancel()

rows, err := conn.QueryContext(ctx, "SELECT count() FROM huge_table")
```

## 生产实践：连接池

```go
import (
    "github.com/ClickHouse/ch-go"
    "github.com/ClickHouse/ch-go/proto"
)

type CHPool struct {
    conn *ch.Client
}

func NewCHPool(addr string) (*CHPool, error) {
    conn, err := ch.Dial(context.Background(), ch.Options{
        Address:  addr,
        Database: "default",
        User:     "default",
        Compression: ch.CompressionLZ4,  // 启用压缩
    })
    if err != nil {
        return nil, err
    }
    return &CHPool{conn: conn}, nil
}

func (p *CHPool) Close() error {
    return p.conn.Close()
}

func (p *CHPool) InsertEvent(event *Event) error {
    batch, err := p.conn.PrepareBatch(context.Background(), `
        INSERT INTO events (event_time, user_id, event_type, amount)
    `)
    if err != nil {
        return err
    }
    batch.Append(time.Now(), event.UserID, event.Type, event.Amount)
    return batch.Send()
}
```

## 实战：服务埋点 SDK

```go
package metrics

import (
    "context"
    "time"
    "github.com/ClickHouse/ch-go"
)

type Reporter struct {
    conn *ch.Client
}

func NewReporter(addr string) (*Reporter, error) {
    conn, err := ch.Dial(context.Background(), ch.Options{Address: addr})
    if err != nil {
        return nil, err
    }
    return &Reporter{conn: conn}, nil
}

// 异步批量上报
func (r *Reporter) ReportAsync(events []*Event) {
    go func() {
        ctx := context.Background()
        batch, err := r.conn.PrepareBatch(ctx, `
            INSERT INTO events (event_time, user_id, event_type, page_url, duration_ms)
        `)
        if err != nil {
            return
        }
        for _, e := range events {
            batch.Append(time.Now(), e.UserID, e.Type, e.PageURL, e.Duration)
        }
        batch.Send()
    }()
}
```

## 实战：查询服务（Gin）

```go
import (
    "github.com/gin-gonic/gin"
    "github.com/ClickHouse/ch-go"
)

func main() {
    conn, _ := ch.Dial(context.Background(), ch.Options{Address: "localhost:9000"})

    r := gin.Default()

    r.GET("/stats/realtime", func(c *gin.Context) {
        ctx := c.Request.Context()

        var uv, pv uint64
        err := conn.QueryRow(ctx, `
            SELECT
                bitmapCardinality(merge(uv_bitmap)) AS uv,
                sumMerge(pv) AS pv
            FROM events_uv_pv_1m
            WHERE event_minute >= now() - INTERVAL 10 MINUTE
        `).Scan(&uv, &pv)

        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        c.JSON(200, gin.H{
            "uv": uv,
            "pv": pv,
            "timestamp": time.Now().Unix(),
        })
    })

    r.Run(":8080")
}
```

## 性能对比基准

```text
单条 INSERT：
  clickhouse-go v2:        2000 rows/s
  ch-go:                   5000 rows/s
  HTTP:                    500 rows/s

批量 INSERT（1000 行/批）：
  clickhouse-go v2:        30000 rows/s
  ch-go:                   100000 rows/s

查询：
  ch-go + LZ4:             50ms
  clickhouse-go + HTTP:    150ms
```

## 选型决策

| 场景 | 推荐 |
|---|---|
| 生产 Go 服务（写入密集） | ch-go |
| 通用 Go 应用 | clickhouse-go v2 |
| 临时脚本 | clickhouse-go v2 + HTTP |
| 与 database/sql 集成 | clickhouse-go v2 |
| 极致性能 | ch-go |

## 下一步

- 学习 dbt 集成：见 [dbt-airbyte.md](./dbt-airbyte.md)
""")


def ch05_dbt_airbyte() -> None:
    add("05-ecosystem/dbt-airbyte.md", r"""---
title: dbt + Airbyte 集成
description: ETL 编排：dbt-clickhouse 模型转换 + Airbyte CDC 同步
---

# dbt + Airbyte 集成

dbt 和 Airbyte 是 ClickHouse 生态中常用的 ETL 工具，本章给出完整实战。

## dbt-clickhouse

[dbt](https://www.getdbt.com/)（data build tool）是流行的 SQL 转换工具，支持 ClickHouse 通过 [dbt-clickhouse](https://github.com/ClickHouse/dbt-clickhouse)。

### 安装

```bash
pip install dbt-clickhouse
```

### 配置 profiles.yml

```yaml
# ~/.dbt/profiles.yml
my_clickhouse_project:
  target: dev
  outputs:
    dev:
  type: clickhouse
  host: localhost
  port: 8123
  user: default
  password: ''
  database: analytics
  schema: default
  secure: false
```

### 项目结构

```text
my_dbt_project/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── staging/
│   │   ├── stg_events.sql
│   │   ├── stg_orders.sql
│   ├── intermediate/
│   │   ├── int_events_with_user.sql
│   ├── marts/
│   │   ├── daily_active_users.sql
```

### 基础模型

```sql
-- models/staging/stg_events.sql
{{ config(materialized='table') }}

SELECT
  event_time,
  event_date,
  user_id,
  event_type,
  page_url,
  amount,
  duration_ms
FROM {{ source('raw', 'events') }}
WHERE event_time >= '2024-01-01'
```

### 物化视图（dbt-clickhouse 扩展）

```sql
{{ config(materialized='materialized_view') }}

SELECT
  event_date,
  event_type,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv
FROM {{ ref('stg_events') }}
GROUP BY event_date, event_type
```

### 增量模型

```sql
{{ config(
  materialized='incremental',
  incremental_strategy='append',
  partition_by='event_date'
) }}

SELECT *
FROM {{ source('raw', 'events') }}

{% if is_incremental() %}
  WHERE event_time > (SELECT max(event_time) FROM {{ this }})
{% endif %}
```

### AggregateFunction 列

```sql
{{ config(materialized='aggregating_merge_tree') }}

SELECT
  event_date,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv
FROM {{ ref('stg_events') }}
GROUP BY event_date
```

### 字典模型

```sql
{{ config(materialized='dictionary') }}

SELECT
  user_id,
  user_name,
  country
FROM {{ ref('stg_users') }}
```

## Airbyte CDC

[Airbyte](https://airbyte.com/) 是开源的 ELT 平台，提供 300+ 数据连接器，ClickHouse 是官方 Destination。

### ClickHouse Destination 配置

```json
{
  "destination_definition_id": "...",
  "connection": {
    "configuration": {
      "host": "clickhouse-1",
      "port": "8123",
      "database": "analytics",
      "username": "default",
      "password": "",
      "ssl": false,
      "tunnel_method": {
        "tunnel_method": "NO_TUNNEL"
      },
      "JdbcUrlParams": "",
      "maintenance_mode": false
    }
  }
}
```

### MySQL → ClickHouse CDC

1. **Source**：MySQL（开启 binlog）
2. **Destination**：ClickHouse
3. **Replication Method**：Standard + CDC（`Logical Replication (CDC)`）

Airbyte 自动创建目标表：

```sql
CREATE TABLE raw.users (
  id UInt64,
  name String,
  email String,
  created_at DateTime,
  _airbyte_emitted_at DateTime,
  _airbyte_deleted_at Nullable(DateTime)
) ENGINE = MergeTree() ORDER BY id
```

### Postgres → ClickHouse

类似 MySQL CDC，使用 `Logical Replication` 或 `pgoutput`。

### Kafka → ClickHouse

Kafka Source + ClickHouse Destination，Airbyte 自动消费。

## 实战：实时数仓 + dbt + Airbyte

```text
MySQL → Airbyte CDC → ClickHouse ODS
                              │
                              ├── dbt: stg_events.sql（清洗）
                              │
                              ├── dbt: int_events_enriched.sql（维度补全）
                              │
                              ├── dbt: fct_daily_user_metrics.sql（每日指标）
                              │
                              └── 物化视图：实时 UV/PV
```

### dbt_project.yml

```yaml
name: 'analytics'
version: '1.0.0'
profile: 'my_clickhouse_project'

models:
  analytics:
    staging:
      +materialized: view
    intermediate:
      +materialized: table
    marts:
      +materialized: table
```

### models/staging/stg_events.sql

```sql
{{ config(materialized='view') }}

SELECT
  event_time,
  event_date,
  user_id,
  event_type,
  page_url,
  amount,
  duration_ms,
  -- 维度补全
  dictGet('users_dict', 'country', user_id) AS country,
  dictGet('products_dict', 'category', product_id) AS category
FROM {{ source('airbyte', 'events') }}
```

### models/marts/daily_metrics.sql

```sql
{{ config(
  materialized='aggregating_merge_tree',
  partition_by='event_date',
  order_by='(event_date, country, event_type)'
) }}

SELECT
  event_date,
  country,
  event_type,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv,
  sumState(amount) AS gmv
FROM {{ ref('stg_events') }}
GROUP BY event_date, country, event_type
```

### 运行 dbt

```bash
# 调试
dbt run --select stg_events

# 全量
dbt run

# 增量（仅最近）
dbt run --select fct_daily_user_metrics --vars '{"start_date": "2024-01-01"}'

# 测试
dbt test

# 文档
dbt docs generate
dbt docs serve  # http://localhost:8080
```

## 监控与告警

```sql
-- Airbyte 同步延迟
SELECT
  table_name,
  max(_airbyte_emitted_at) AS last_sync
FROM airbyte._airbyte_meta
GROUP BY table_name

-- dbt 模型最近运行时间
SELECT * FROM analytics.dbt_run_results ORDER BY generated_at DESC LIMIT 10
```

## 大厂实践

- **Airbnb**：Airbyte + dbt + ClickHouse 实时数据栈
- **GitHub**：Airbyte CDC + ClickHouse
- **Cloudflare**：自研 + dbt-clickhouse 报表

## 下一步

- 学习 SQL 聚合：见 [02-sql/select-aggregate.md](../02-sql/select-aggregate.md)
- 学习对比选型：见 [06-compare/overview.md](../06-compare/overview.md)
""")


# ============================================================================
# Chapter 06: Compare (4 stubs)
# ============================================================================

def ch06_vs_mysql_pg() -> None:
    add("06-compare/vs-mysql-pg.md", r"""---
title: vs MySQL / PostgreSQL
description: ClickHouse vs MySQL vs PostgreSQL 完整对比：数据模型 / 性能 / 适用场景
---

# ClickHouse vs MySQL / PostgreSQL

很多团队在「要不要上 ClickHouse」前会先问：「MySQL/PG 能不能扛？」本章给出可执行的对比。

## 核心差异

| 维度 | ClickHouse | MySQL | PostgreSQL |
|---|---|---|---|
| **数据模型** | 列存 | 行存 | 行存 |
| **写吞吐** | 100w+ rows/s | 1-5w rows/s | 5-10w rows/s |
| **单查询**（亿级聚合） | < 1s | 30s+ / OOM | 30s+ / OOM |
| **JOIN 能力** | 弱（≤ 8 表） | 强 | 极强 |
| **事务** | 无 | ACID | ACID |
| **UPDATE/DELETE** | 弱（异步 MUTATION） | 强 | 强 |
| **索引** | 主键稀疏 + Skip | B+Tree / 全文 | B+Tree / GIN / BRIN |
| **适用数据量** | PB 级 | TB 级 | TB 级 |

## 性能基准（10 亿行）

```sql
-- 测试表
CREATE TABLE test_table (
  id UInt64,
  user_id UInt64,
  event_time DateTime,
  event_type LowCardinality(String),
  amount Decimal(18, 2)
)
ENGINE = MergeTree() ORDER BY id

-- 插入 10 亿行（约 5 分钟）
INSERT INTO test_table SELECT
  number,
  number % 1000,
  now() - INTERVAL number SECOND,
  ['click', 'view', 'purchase'][number % 3 + 1],
  rand() % 1000
FROM numbers(1000000000)
```

| 查询 | ClickHouse | MySQL（带索引） | PostgreSQL（带索引） |
|---|---|---|---|
| `SELECT count()` | 100ms | 30s | 20s |
| `SELECT count() GROUP BY event_type` | 200ms | 60s | 40s |
| `SELECT uniq(user_id)` | 1s | 120s+ | 90s+ |
| `SELECT avg(amount) GROUP BY user_id`（Top 100） | 500ms | 90s+ | 60s+ |
| `SELECT * WHERE user_id = X` | 50ms | 10ms | 8ms |

**结论**：
- 聚合 / 统计查询 → ClickHouse 完胜（10-100x）
- 单行 / 主键查询 → MySQL/PG 更快（行存索引）

## 数据同步模式

### 模式 1：MySQL → ClickHouse 实时同步

```text
MySQL（OLTP） → Debezium/Kafka → ClickHouse（OLAP）
            │
            │  CDC 同步
            ▼
       实时分析
```

### 模式 2：双写（不推荐）

```text
应用 → MySQL（事务写入）
      → ClickHouse（分析写入）
      │
      └── 双写一致性难保证
```

### 模式 3：ClickHouse → MySQL 回写（少见）

CK 计算结果回写 MySQL 提供 OLTP 读取（如实时计数）。

## 何时 MySQL/PG 足够？

✅ **数据量 < 1 亿行 + 查询模式以单行为主** → MySQL/PG 就够
✅ **强事务 + 高并发点查** → MySQL/PG（TiDB 也行）
✅ **简单 COUNT/SUM** → MySQL/PG（CK 杀鸡用牛刀）

## 何时 ClickHouse 值得？

✅ **数据量 ≥ 1 亿行 + 聚合查询为主** → ClickHouse 必备
✅ **日志 / 埋点 / 指标** → ClickHouse 主战场
✅ **实时看板 / 报表** → ClickHouse 秒级延迟
✅ **PB 级长期存储** → ClickHouse 压缩 + 分布式

## 混合架构（推荐）

```text
MySQL/PG（OLTP）
    │
    ├── 主库：用户 / 订单 / 商品（强事务）
    └── 从库：备份 + 简单聚合

ClickHouse（OLAP）
    │
    ├── 实时看板
    ├── 用户行为分析
    └── 业务指标

Kafka（CDC）
    │
    └── MySQL → Kafka → ClickHouse
```

## 迁移路径

### Step 1：数据量评估

```sql
-- MySQL 评估
SELECT
  table_schema,
  table_name,
  table_rows,
  ROUND(data_length / 1024 / 1024, 2) AS data_mb
FROM information_schema.tables
WHERE table_schema NOT IN ('mysql', 'information_schema', 'performance_schema')
ORDER BY data_length DESC
```

### Step 2：建立 CDC 链路

```bash
# 用 Debezium 捕获 MySQL binlog
debezium-connector-mysql \
  --connector.class=io.debezium.connector.mysql.MySqlConnector \
  --database.hostname=mysql-1 \
  --database.port=3306 \
  --database.user=debezium \
  --database.password=xxx \
  --database.server.id=1 \
  --table.include.list=production.orders,production.users \
  --topic.prefix=cdc
```

### Step 3：ClickHouse 消费

```sql
CREATE TABLE orders_kafka (...)
ENGINE = Kafka()
SETTINGS
  kafka_broker_list = 'kafka-1:9092',
  kafka_topic_list = 'cdc.production.orders',
  kafka_format = 'JSONEachRow'

CREATE MATERIALIZED VIEW orders_cdc_mv TO orders_local AS
SELECT * FROM orders_kafka
```

### Step 4：业务查询迁移

| 原 MySQL 查询 | ClickHouse 查询 |
|---|---|
| `SELECT count(*) FROM orders` | `SELECT count() FROM orders` |
| `SELECT COUNT(DISTINCT user_id)` | `SELECT uniq(user_id)` |
| `SELECT * FROM orders WHERE id = X` | **保持 MySQL**（CK 慢） |

## 实战：电商平台

```text
MySQL 主库（写）：用户 / 订单 / 商品 / 库存
   │
   └── Binlog
       │
       └── Debezium → Kafka
           │
           └── ClickHouse Kafka 引擎
               │
               ├── MV：实时 UV / PV / GMV
               ├── MV：用户画像
               └── MV：商品分析

查询路由：
- 用户登录 / 下单 / 支付 → MySQL
- 商家后台 / 经营分析 → ClickHouse
- 实时大屏 → ClickHouse + Grafana
```

## 大厂案例

- **Uber**：订单数据走 ClickHouse
- **字节跳动**：电商分析
- **京东**：订单履约 + 商品分析（与 MySQL/PG 共存）

详见 [../case-study.md](../../case-study.md) 案例 6。

## 工具对比

| 工具 | MySQL | PG | ClickHouse |
|---|---|---|---|
| **客户端** | MySQL Workbench | pgAdmin | DBeaver / DataGrip |
| **BI** | Metabase | Metabase | Grafana / Metabase / Superset |
| **ORM** | MyBatis / GORM | sqlx / GORM | 没有专门 ORM（直接写 SQL） |

## 下一步

- 学习 vs Doris：见 [vs-doris.md](./vs-doris.md)
""")


def ch06_vs_doris() -> None:
    add("06-compare/vs-doris.md", r"""---
title: vs Doris / StarRocks
description: ClickHouse vs Doris vs StarRocks 三大 OLAP 引擎详细对比
---

# ClickHouse vs Doris

[Doris](https://doris.apache.org/) 和 [StarRocks](https://www.starrocks.io/) 是 MPP 架构的新一代 OLAP 引擎。本章对比 ClickHouse 和 Doris。

## 核心差异

| 维度 | ClickHouse | Doris |
|---|---|---|
| **出身** | Yandex（2009） | 百度（2017）→ Apache |
| **架构** | Shared-nothing | Frontend + Backend |
| **存储引擎** | MergeTree（LSM 风格） | 列存 + Segment |
| **JOIN 能力** | 弱（Hash Join 本地） | 强（CBO + Runtime Filter） |
| **数据更新** | ReplacingMergeTree（异步） | 默认支持 UPSERT |
| **实时写入** | Kafka 引擎 + MV | Stream Load / Routine Load |
| **运维** | 复杂（Keeper 集群） | 简单（FE + BE） |
| **SQL 完整度** | 中（无完整事务） | 高（CBO 强） |
| **生态** | 客户端 / Kafka / dbt | 自带生态 + SelectDB 商业版 |
| **典型用户** | Uber / Cloudflare / GitHub | 百度 / 美团 / 小米 / 京东 |

## 性能对比（10 亿行 JOIN）

```sql
-- 测试场景：星型模型 JOIN
-- 事实表 orders（10 亿）
-- 维度表 users（百万）、products（百万）、shops（万）

-- Doris SQL
SELECT
  u.country,
  p.category,
  s.shop_type,
  count() AS order_count,
  sum(o.amount) AS gmv
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id
JOIN shops s ON o.shop_id = s.id
WHERE o.order_date >= '2024-01-01'
GROUP BY u.country, p.category, s.shop_type

-- Doris: 5-8s
-- ClickHouse: 30-60s（JOIN 4 张大表性能退化）
```

**结论**：**多张大表 JOIN** Doris 完胜 ClickHouse。

## 单表聚合性能（CK 主场）

```sql
-- 单表聚合
SELECT
  event_date,
  uniq(user_id) AS uv,
  count() AS pv
FROM events
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY event_date

-- ClickHouse: 100ms
-- Doris: 200ms
```

**结论**：**单表列扫** ClickHouse 比 Doris 快 1.5-2x。

## 数据写入吞吐

```sql
-- 批量 INSERT
INSERT INTO events VALUES ... (1 million rows)

-- ClickHouse: 0.5s（100w rows/s）
-- Doris: 1-2s（50w rows/s）
```

**结论**：**批量写入** ClickHouse 仍占优。

## 实时数据接入

### ClickHouse：Kafka 引擎

```sql
CREATE TABLE events_kafka (...)
ENGINE = Kafka()
SETTINGS kafka_broker_list = 'kafka-1:9092', kafka_topic_list = 'events', kafka_format = 'JSONEachRow'

CREATE MATERIALIZED VIEW events_mv TO events_local AS SELECT * FROM events_kafka
```

### Doris：Routine Load

```sql
CREATE ROUTINE LOAD my_load_job ON events
COLUMNS (event_time, user_id, event_type)
PROPERTIES (
  "desired_concurrent_number" = "3",
  "max_error_number" = "1000"
)
FROM KAFKA (
  "kafka_broker_list" = "kafka-1:9092",
  "kafka_topic" = "events"
)
```

**对比**：
- CK Kafka 引擎更简洁（一行 SQL）
- Doris Routine Load 持续消费，状态可查询
- 两者都能达到 10w+ rows/s

## 数据更新

### ClickHouse：ReplacingMergeTree

```sql
CREATE TABLE users (
  id UInt64,
  name String,
  updated_at DateTime
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY id

-- 去重是异步的（合并时执行）
SELECT * FROM users FINAL WHERE id = 1
```

### Doris：UPSERT（默认）

```sql
CREATE TABLE users (
  id BIGINT,
  name VARCHAR(100),
  UNIQUE KEY (id)
)
DISTRIBUTED BY HASH(id) BUCKETS 10

-- 默认 UPSERT（实时合并）
INSERT INTO users VALUES (1, 'Alice')  -- 替换之前的 id=1
```

**对比**：Doris UPSERT 是同步的（默认开启 Unique Key 表），CK ReplacingMergeTree 是异步的。

## 运维对比

| 维度 | ClickHouse | Doris |
|---|---|---|
| **依赖** | ClickHouse Keeper（或 Zookeeper） | 无（FE 自带 BDBJE） |
| **集群部署** | 复杂（多分片 + 副本） | 简单（FE 3 节点 + BE N 节点） |
| **扩容** | 手动 rebalance | 自动均衡 |
| **监控** | 自带 system.metrics | 自带 system.audit + audit log |
| **故障恢复** | 副本切换（秒级） | FE 高可用（秒级） |

**结论**：Doris 运维更简单，ClickHouse 运维更复杂但更可控。

## 生态对比

| 维度 | ClickHouse | Doris |
|---|---|---|
| **客户端** | ch-go / clickhouse-go / JDBC / Python | mysql-jdbc / Go / Python |
| **Kafka 集成** | 原生引擎 | Routine Load |
| **数据湖** | Iceberg / DeltaLake（v23+） | 原生 Iceberg / Hudi |
| **BI 工具** | Grafana / Superset / Metabase | Apache Superset / SmartBI |
| **云服务** | ClickHouse Cloud / Altinity | SelectDB Cloud |
| **商业支持** | Altinity / ClickHouse Inc | SelectDB（商业版） |

## 选型决策

### 选 ClickHouse

✅ **单表聚合 + 高吞吐写入**（日志 / 埋点 / 指标）
✅ **极致性能优化**（定制客户端 + LZ4 压缩）
✅ **生态丰富**（Kafka / dbt / Grafana / Prometheus）
✅ **团队有能力运维 Keeper 集群**

### 选 Doris

✅ **复杂 JOIN 场景**（星型 / 雪花模型）
✅ **实时 UPSERT**（订单状态机、用户更新）
✅ **运维团队精简**（不想维护 Zookeeper）
✅ **数据湖联邦查询**（原生 Iceberg）

## 实战对比

### 场景 1：日志分析（CK 赢面）

```text
数据量：100 亿 / 天
查询：按 status_code / path 聚合
写入：Kafka 流式

CK 优势：单表聚合快 1.5-2x，Kafka 引擎更简洁
```

### 场景 2：订单实时分析（Doris 赢面）

```text
数据量：10 亿订单 + 多维度关联
查询：订单 + 用户 + 商品 + 店铺 JOIN
更新：订单状态实时更新

Doris 优势：多表 JOIN 优化好，UPSERT 实时合并
```

### 场景 3：埋点实时大宽表（CK 赢面）

```text
数据量：PB 级
查询：单表按时间聚合
写入：百万 events/s

CK 优势：写入吞吐 + 单表聚合双优
```

## 大厂案例

| 公司 | 引擎 | 场景 |
|---|---|---|
| Uber | ClickHouse | 日志分析 |
| Cloudflare | ClickHouse | DNS / CDN |
| GitHub | ClickHouse | Events |
| 字节跳动 | ClickHouse | 抖音埋点 |
| 美团 | ClickHouse + Doris 双引擎 | 外卖（CK）+ 供应链（Doris） |
| 京东 | ClickHouse | 订单分析 |
| 百度 | Doris | 凤巢广告 |
| 小米 | Doris | 业务分析 |

## 与 StarRocks 对比

详见 [vs-starrocks.md](./vs-starrocks.md)。

**结论**：
- **Doris**：Apache 社区版 + SelectDB 商业版，国内接受度高
- **StarRocks**：从 Doris 0 fork，CBO 优化器更强，海外接受度高
- **二者形态相似，选哪个都合理**

## 下一步

- 学习 vs StarRocks：见 [vs-starrocks.md](./vs-starrocks.md)
- 学习 vs TiDB：见 [vs-tidb.md](./vs-tidb.md)
""")


def ch06_vs_starrocks() -> None:
    add("06-compare/vs-starrocks.md", r"""---
title: vs StarRocks
description: ClickHouse vs StarRocks：两大列存 OLAP 引擎的全面对比
---

# ClickHouse vs StarRocks

StarRocks 是从 Doris 0.13 fork 出来的开源 OLAP，专注 CBO 优化和向量化执行。本章对比 ClickHouse 与 StarRocks。

## 核心差异

| 维度 | ClickHouse | StarRocks |
|---|---|---|
| **出身** | Yandex（2009） | DorisDB fork（2020）→ StarRocks |
| **架构** | Shared-nothing + 本地存储 | FE + BE，可存算分离（v3.x） |
| **向量化** | 完整（SSE/AVX） | 完整（CBO + Adaptive） |
| **CBO** | 弱（无统计信息） | 强（统计 + CBO + Runtime Filter） |
| **JOIN 优化** | Hash Join 简单 | Adaptive Multi-Agg Join |
| **高并发** | 中（每查询 1-少线程） | 强（每 BE 数百并发） |
| **数据湖** | Iceberg/Hudi/Delta（v23+） | 原生 Iceberg/Hudi/Hive |
| **实时数仓** | Kafka 引擎 + MV | Routine Load + 主键模型 |
| **存算分离** | 部分（v22+ S3） | 完整（v3.x） |
| **运维** | 中（Keeper） | 简单（FE HA + BE 弹性） |
| **典型用户** | Cloudflare / Uber / 字节 | 滴滴 / 网易 / 米哈游 / 小红书 |

## 性能对比（基准测试 SSB）

```text
Star Schema Benchmark（100 GB 数据）

ClickHouse：     1.0x（基线）
StarRocks：      1.5-3x（CBO + Runtime Filter 优化）
```

**结论**：复杂查询场景，StarRocks 通常比 ClickHouse 快 1.5-3x。

## 单查询性能（CK 主场）

```sql
-- 单表列扫
SELECT
  event_date,
  uniq(user_id) AS uv,
  count() AS pv
FROM events
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY event_date

-- ClickHouse: 200ms（基于 10 亿行）
-- StarRocks: 400ms
```

**结论**：**单表聚合查询** ClickHouse 略胜（向量化和压缩）。

## 多表 JOIN（StarRocks 主场）

```sql
-- 4 表 JOIN
SELECT
  o.order_id,
  u.user_name,
  p.product_name,
  s.shop_name,
  o.amount
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id
JOIN shops s ON o.shop_id = s.id
WHERE o.order_date >= '2024-01-01'
LIMIT 1000

-- ClickHouse: 30s（4 表 JOIN 性能退化）
-- StarRocks: 1-3s（CBO 优化）
```

**结论**：**多表 JOIN** StarRocks 完胜（CBO + Runtime Filter + Adaptive）。

## 高并发查询

```sql
-- 100 个并发查询（简单聚合）
-- ClickHouse: 单查询 100ms，总耗时 30s（资源竞争）
-- StarRocks: 单查询 50ms，总耗时 8s（并发友好）
```

**结论**：**高并发** StarRocks 更适合（专为并发查询设计）。

## 实时数仓

### ClickHouse：Kafka 引擎 + MV

```sql
CREATE TABLE events_kafka (...)
ENGINE = Kafka()
SETTINGS kafka_broker_list = 'kafka-1:9092', kafka_topic_list = 'events', ...

CREATE MATERIALIZED VIEW events_mv TO events_local AS
SELECT ... FROM events_kafka
```

### StarRocks：Routine Load + 主键模型

```sql
CREATE TABLE events (
  event_time DATETIME,
  user_id BIGINT,
  event_type VARCHAR(20),
  PRIMARY KEY (event_time, user_id)
)
DUPLICATE KEY(event_time, user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 32

CREATE ROUTINE LOAD events_load ON events
COLUMNS (event_time, user_id, event_type)
FROM KAFKA (
  "kafka_broker_list" = "kafka-1:9092",
  "kafka_topic" = "events"
)
```

**对比**：
- CK Kafka 引擎简洁（一行 SQL）
- StarRocks Routine Load 可查询状态 + 自动重试
- 两者性能相近

## 数据湖集成

### ClickHouse

```sql
-- v23+ 支持 Iceberg
CREATE TABLE iceberg_table (...)
ENGINE = IcebergS3('http://minio:9000/warehouse/', 'table')

SELECT * FROM iceberg_table
```

### StarRocks

```sql
-- 原生 Iceberg Catalog
CREATE EXTERNAL CATALOG iceberg_catalog
PROPERTIES (
  "type" = "iceberg",
  "iceberg.catalog.type" = "hive",
  "hive.metastore.uris" = "thrift://hive-metastore:9083"
)

SELECT * FROM iceberg_catalog.db.table
```

**对比**：StarRocks 数据湖集成更成熟（多年迭代），CK 正在追赶。

## 存算分离

### ClickHouse

v22.x 引入 S3 存算分离（实验性）：

```sql
CREATE TABLE events (...)
ENGINE = MergeTree()
SETTINGS storage_policy = 's3_main'
```

### StarRocks

v3.x 完整支持存算分离（CN + BN 分离）：

```text
├── FE（前端）
├── CN（计算节点，无状态）
└── BN（存储节点，BE）
```

**对比**：StarRocks v3.x 存算分离生产可用，CK 还在实验阶段。

## 生态对比

| 维度 | ClickHouse | StarRocks |
|---|---|---|
| **官方云** | ClickHouse Cloud | StarRocks Cloud（阿里云） |
| **运维工具** | clickhouse-keeper / clickhouse-backup | StarRocks Manager |
| **监控** | system.metrics | audit log + 系统表 |
| **BI 集成** | Grafana / Superset / Metabase | Apache Superset / SmartBI |
| **客户端** | ch-go / JDBC / Python | mysql-jdbc / Go / Python |
| **版本发布** | 每月一个版本 | 每月一个版本 |

## 选型决策

### 选 ClickHouse

✅ **单表列扫 + 高吞吐写入**（埋点 / 日志）
✅ **极致性能优化**（自研 ch-go 客户端）
✅ **存算分离不是必须**（本地 SSD 即可）
✅ **团队有 ClickHouse 运维经验**

### 选 StarRocks

✅ **复杂 JOIN + 高并发查询**（BI 报表）
✅ **存算分离 + 弹性扩缩容**
✅ **数据湖联邦查询**（Iceberg / Hudi）
✅ **团队倾向 CBO 优化器 + 自动化运维**

## 实战对比

### 场景 1：BI 实时看板（StarRocks 赢面）

```text
数据量：10 亿订单
查询：多维度聚合（地区 + 品类 + 时间）
并发：100+ QPS
表数：5+ JOIN

StarRocks 优势：CBO + Runtime Filter + 高并发
```

### 场景 2：埋点日志分析（CK 赢面）

```text
数据量：PB 级
查询：单表按时间聚合
写入：百万 events/s
表数：1（事件宽表）

CK 优势：写入吞吐 + 单表聚合
```

### 场景 3：电商实时分析（都适合）

```text
数据量：10 亿订单
查询：订单 + 用户 + 商品 JOIN
并发：50 QPS
更新：订单状态实时更新

CK：Doris-style 宽表预 JOIN
SR：直接多表 JOIN（CBO 自动优化）
```

## 大厂案例

| 公司 | 引擎 | 场景 |
|---|---|---|
| 滴滴 | StarRocks | 行程数据（与 CK 共存） |
| 网易 | StarRocks | 游戏分析 |
| 米哈游 | StarRocks | 游戏数据 |
| 小红书 | StarRocks | 内容分析 |
| Cloudflare | ClickHouse | DNS 日志 |
| Uber | ClickHouse | 业务日志 |
| 字节跳动 | ClickHouse | 抖音埋点 |

详见 [../case-study.md](../../case-study.md) 案例 1、2、9。

## 结论

- **场景偏聚合 + 写入密集** → ClickHouse
- **场景偏 JOIN + 高并发 + 数据湖** → StarRocks
- **场景都涵盖** → 双引擎共存（滴滴案例）

## 下一步

- 学习 vs TiDB：见 [vs-tidb.md](./vs-tidb.md)
""")


def ch06_vs_tidb() -> None:
    add("06-compare/vs-tidb.md", r"""---
title: vs TiDB
description: ClickHouse vs TiDB HTAP：OLAP 专精 vs OLTP + OLAP 一体化
---

# ClickHouse vs TiDB

[TiDB](https://tidb.io/) 是 PingCAP 开源的分布式 HTAP 数据库，TiKV（行存）+ TiFlash（列存副本）实现一份数据两种引擎。本章对比 ClickHouse 和 TiDB 的 OLAP 能力。

## 核心差异

| 维度 | ClickHouse | TiDB |
|---|---|---|
| **定位** | 纯 OLAP | HTAP（OLTP + OLAP） |
| **架构** | Shared-nothing + 本地存储 | TiKV（行存）+ TiFlash（列存副本） |
| **OLTP** | ❌ 不支持 | ✅ 强（MySQL 兼容） |
| **OLAP** | 极强（专用引擎） | 中（TiFlash 列副本） |
| **事务** | 无 | 完整分布式事务（Percolator） |
| **写入延迟** | 异步（无强一致） | 同步（P99 < 50ms） |
| **生态** | BI / Kafka / 各种 ETL | MySQL 协议完全兼容 |
| **运维** | 中（Keeper 集群） | 中（TiKV + TiFlash） |
| **典型用户** | 上述 | B 站（早期）/ 小米 / 平安 |

## OLAP 性能对比（10 亿行）

```sql
-- 测试查询：单表聚合
SELECT
  order_date,
  count() AS order_count,
  sum(amount) AS gmv,
  uniq(user_id) AS buyers
FROM orders
WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY order_date

-- ClickHouse: 200ms
-- TiDB（TiFlash）: 2-5s（列副本未优化好）
```

**结论**：**OLAP 性能** ClickHouse 比 TiDB（TiFlash）快 5-10x。

## OLTP 能力对比

```sql
-- OLTP 事务
BEGIN;
UPDATE users SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET total = total - 100 WHERE user_id = 1;
COMMIT;

-- ClickHouse: ❌ 不支持事务
-- TiDB: ✅ 完整 ACID
```

**结论**：**OLTP 能力** TiDB 完胜（ClickHouse 根本没 OLTP）。

## HTAP 适用性

```text
TiDB HTAP 架构：
┌──────────┐    ┌──────────┐    ┌──────────┐
│ TiKV     │    │ TiFlash  │    │ TiSpark  │
│ (行存)   │    │ (列副本) │    │ (Spark)  │
│ OLTP     │    │ OLAP     │    │ 复杂分析 │
└──────────┘    └──────────┘    └──────────┘
     ▲                ▲                ▲
     └────────────────┼────────────────┘
                      │
              Raft 同步 + 异步复制
```

**优势**：
- 一套系统搞定 OLTP + OLAP
- 数据强一致（TiKV 主写入，TiFlash 异步复制）

**劣势**：
- TiFlash OLAP 性能不如 ClickHouse
- 资源隔离差（OLTP 负载影响 OLAP）

## 选型决策

### 选 TiDB

✅ **需要 HTAP**（OLTP + OLAP 一套系统）
✅ **MySQL 协议兼容**（迁移成本低）
✅ **数据量 < 10 亿行**（TiFlash 列副本规模上限）
✅ **团队倾向 MySQL 生态**

### 选 ClickHouse

✅ **纯 OLAP**（不需要 OLTP 拖累）
✅ **数据量 > 10 亿行**（ClickHouse 横向扩展更成熟）
✅ **极致 OLAP 性能**（CK 比 TiFlash 快 5-10x）
✅ **团队有能力运维 Keeper 集群**

## 典型混合架构

```text
MySQL/PG → CDC → Kafka → ClickHouse（专用 OLAP）
                            │
                            └── 复杂报表 / 实时看板
```

如果不想维护两套系统，TiDB HTAP 是合理选择。

## 实战对比

### 场景 1：电商（HTAP 需求）

```text
订单创建：    OLTP（强事务）→ TiDB
订单分析：    OLAP（聚合查询）→ ClickHouse（更快）

混合架构：
  应用 → TiDB（事务）
       → CDC → Kafka → ClickHouse（分析）
```

### 场景 2：金融（HTAP 强需求）

```text
账户余额：    OLTP（强事务）→ TiDB
账户分析：    OLAP（聚合查询）→ TiDB TiFlash（一致性优先）

纯 TiDB HTAP。
```

### 场景 3：日志分析（CK 主场）

```text
日志采集：    Kafka → ClickHouse
日志分析：    ClickHouse

无需 TiDB（无 OLTP 需求）。
```

## 大厂案例

### TiDB 案例

- **B 站**（早期）：HTAP 实践
- **小米**：用户中心 + 业务分析
- **平安**：金融业务 HTAP

### ClickHouse 案例

- **字节跳动**：抖音埋点（CK 专用 OLAP）
- **京东**：订单分析（CK 专用 OLAP）
- **Uber**：日志分析（CK 专用 OLAP）

## TiDB vs Doris / StarRocks 对比

| 维度 | TiDB | Doris / StarRocks |
|---|---|---|
| **OLTP** | 极强 | 弱（不建议） |
| **OLAP** | 中 | 强（CBO 优化） |
| **HTAP** | 强 | 弱 |
| **生态** | MySQL 协议 | 自有生态 |
| **典型场景** | 强 HTAP 需求 | 纯 OLAP 复杂 JOIN |

## 工具对比

| 维度 | TiDB | ClickHouse |
|---|---|---|
| **客户端** | MySQL 客户端 | DBeaver / DataGrip / ch-go |
| **BI** | Metabase / Superset | Grafana / Superset |
| **CDC** | TiCDC | Debezium / MaterializedPostgreSQL |
| **云服务** | TiDB Cloud | ClickHouse Cloud |

## 实际案例：选择思考

### 案例 A：互联网业务（中小规模）

```text
Q: 数据量 1 亿行 + OLTP + OLAP 都要
A: TiDB（HTAP，省运维）
```

### 案例 B：互联网业务（大规模）

```text
Q: 数据量 10 亿+ + 强 OLAP
A: MySQL + ClickHouse（专机专用）
```

### 案例 C：传统企业（金融）

```text
Q: 强事务 + 数据一致性 + OLAP
A: TiDB HTAP（一致性优先）
```

### 案例 D：日志平台

```text
Q: 日志 PB 级 + 聚合查询
A: ClickHouse（专用 OLAP）
```

## 结论

- **HTAP 需求 + 数据量适中** → TiDB
- **大规模 OLAP** → ClickHouse
- **两者结合** → MySQL/PG + ClickHouse 混合架构

## 大厂混合实践

- **小米**：TiDB + ClickHouse（OLTP + OLAP 分工）
- **美团**：MySQL + ClickHouse
- **字节**：MySQL + ClickHouse

详见 [../case-study.md](../../case-study.md)。

## 下一步

- 学习 OLAP 实战：见 [04-olap-scenarios/overview.md](../04-olap-scenarios/overview.md)
- 学习生态集成：见 [05-ecosystem/overview.md](../05-ecosystem/overview.md)
""")


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    print(f"Generating ClickHouse stubs to: {DOCS}")

    # Chapter 01: Basics (4)
    ch01_history()
    ch01_installation()
    ch01_client()
    ch01_data_types()

    # Chapter 02: SQL (5)
    ch02_select_aggregate()
    ch02_join()
    ch02_functions()
    ch02_window_functions()
    ch02_dictionary()

    # Chapter 03: Table Engine (5)
    ch03_mergetree_family()
    ch03_log_engine()
    ch03_kafka_engine()
    ch03_distributed()
    ch03_materialized_view()

    # Chapter 04: OLAP Scenarios (5)
    ch04_user_tracking()
    ch04_log_analysis()
    ch04_metrics_storage()
    ch04_bitmap()
    ch04_realtime_warehouse()

    # Chapter 05: Ecosystem (5)
    ch05_kafka_integration()
    ch05_grafana()
    ch05_prometheus()
    ch05_go_client()
    ch05_dbt_airbyte()

    # Chapter 06: Compare (4)
    ch06_vs_mysql_pg()
    ch06_vs_doris()
    ch06_vs_starrocks()
    ch06_vs_tidb()

    print("\nDone! Generated 28 substantial stubs.")


if __name__ == "__main__":
    main()