---
title: libpq C 库
description: PostgreSQL C API 实战
---

# libpq C 库

> **TL;DR**：libpq = PG 的 **C 语言客户端库**。**所有 PG 客户端（JDBC / psycopg / libpq 本身）都基于或参考 libpq 设计**。

## 一句话定义

```
libpq = PG 的 C API
     = 所有 PG 客户端的基础
     = 异步查询 + COPY 协议
```

## 基本使用

```c
#include <libpq-fe.h>

int main() {
    PGconn *conn = PQconnectdb(
      "host=localhost dbname=mydb user=postgres password=xxx"
    );
    
    if (PQstatus(conn) != CONNECTION_OK) {
        fprintf(stderr, "Connection failed: %s", PQerrorMessage(conn));
        PQfinish(conn);
        return 1;
    }
    
    // 执行查询
    PGresult *res = PQexec(conn, "SELECT id, name FROM users");
    
    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        fprintf(stderr, "Query failed: %s", PQresultErrorMessage(res));
        PQclear(res);
        PQfinish(conn);
        return 1;
    }
    
    // 处理结果
    int rows = PQntuples(res);
    int cols = PQnfields(res);
    
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            printf("%s	", PQgetvalue(res, i, j));
        }
        printf("
");
    }
    
    PQclear(res);
    PQfinish(conn);
    return 0;
}
```

**编译**：
```bash
gcc app.c -I/usr/include/postgresql -lpq -o app
```

## 参数化查询

```c
// 防止 SQL 注入
PGresult *res = PQexecParams(
    conn,
    "SELECT * FROM users WHERE id = $1 AND status = $2",
    2,                          // 参数个数
    NULL,                       // 参数类型（NULL 让 PG 推断）
    paramValues,                // 参数值
    paramLengths,               // 参数长度
    paramFormats,               // 0 = text, 1 = binary
    0                           // 结果格式
);
```

```c
const char *paramValues[2] = {"123", "active"};
int paramLengths[2] = {3, 6};
int paramFormats[2] = {0, 0};
```

## 异步查询

```c
// 1. 发送
PGresult *res = PQsendQuery(conn, "SELECT pg_sleep(10), now()");
// PQsendQuery 返回 1 表示已发送，立即返回

// 2. 轮询
while (PQisBusy(conn)) {
    // 等待 socket 可读
    int fd = PQsocket(conn);
    fd_set read_fds;
    FD_ZERO(&read_fds);
    FD_SET(fd, &read_fds);
    select(fd + 1, &read_fds, NULL, NULL, NULL);
    
    // 接收数据
    PQconsumeInput(conn);
}

// 3. 获取结果
res = PQgetResult(conn);
```

## COPY 协议

```c
// 1. COPY FROM STDIN
PGresult *res = PQexec(conn, "COPY users (name, email) FROM STDIN");
if (PQresultStatus(res) == PGRES_COPY_IN) {
    // 2. 发送数据
    PQputCopyData(conn, "Alice,[email protected]
", strlen("Alice,[email protected]
"));
    PQputCopyData(conn, "Bob,[email protected]
", strlen("Bob,[email protected]
"));
    
    // 3. 结束
    PQputCopyEnd(conn, NULL);
    
    // 4. 获取结果
    PGresult *result = PQgetResult(conn);
}

// 100 万行约 5 秒
```

## 事务

```c
// BEGIN
PGresult *res = PQexec(conn, "BEGIN");

// 业务 SQL
PQexec(conn, "INSERT INTO ...");
PQexec(conn, "UPDATE ...");

// COMMIT
res = PQexec(conn, "COMMIT");
```

或用 prepared statement 避免 SQL 注入。

## 大对象（LO）

```c
Oid loid = lo_creat(conn, INV_READ | INV_WRITE);

// 写入
int fd = lo_open(conn, loid, INV_WRITE);
PQlo_export(conn, loid, "/path/to/file");

// 读取
PQlo_import(conn, "/path/to/file");
```

> **现代做法**：用 bytea 字段代替大对象。

## 错误处理

```c
PGresult *res = PQexec(conn, "SELECT bad_col FROM users");

// 状态码
ExecStatusType status = PQresultStatus(res);
switch (status) {
    case PGRES_COMMAND_OK:
        // 非 SELECT 命令成功
        break;
    case PGRES_TUPLES_OK:
        // SELECT 成功
        break;
    case PGRES_FATAL_ERROR:
        // 致命错误
        fprintf(stderr, "%s
", PQresultErrorMessage(res));
        break;
}
```

## 实战案例

### 案例 1：批量导入 CSV

```c
PGconn *conn = PQconnectdb("host=localhost dbname=mydb");
PGresult *res = PQexec(conn, "COPY users (name, email) FROM STDIN WITH (FORMAT csv)");

FILE *fp = fopen("users.csv", "r");
char buf[8192];

while (fgets(buf, sizeof(buf), fp)) {
    PQputCopyData(conn, buf, strlen(buf));
}

PQputCopyEnd(conn, NULL);
fclose(fp);
PQclear(res);
PQfinish(conn);
```

## 一句话总结

> **libpq = PG 的 C API 基础**：**所有客户端都借鉴它的设计**。**COPY 协议是百万级数据导入的关键**。**实际项目大多用高层封装**（JDBC / psycopg），libpq 主要用于 C/C++ 应用和嵌入式开发。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
