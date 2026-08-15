---
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
