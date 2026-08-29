---
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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [es](https://java-px.bot.cd/es/):ES 对比
- [bigdata](https://java-px.bot.cd/bigdata/):大数据生态
- [postgresql](https://java-px.bot.cd/postgresql/):PostgreSQL 对比
