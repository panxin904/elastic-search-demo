---
title: 慢查询分析
date: 2026-08-15  # date-auto-injected
---

# 慢查询分析

Redis 命令的"快"是相对的。一个 O(1) 的 GET 在大 Key 面前可能变成"卡住整个 Redis 的慢操作"。SLOWLOG 是定位慢命令的标准武器。

## SLOWLOG 三个命令

```bash
# 查看最近的慢查询（默认 10 条）
redis-cli SLOWLOG GET
# 1) 1) (integer) 1234
#    2) (integer) 1700000000    # Unix 时间戳
#    3) (integer) 15234         # 耗时 15234 微秒 = 15.2ms
#    4) 1) "KEYS"
#       2) "user:*"
#    5) "127.0.0.1:52344"
#    6) ""

# 查询队列长度
redis-cli SLOWLOG LEN
# (integer) 128

# 清空慢日志
redis-cli SLOWLOG RESET
```

每条记录的字段：

| 字段 | 含义 |
|---|---|
| 1 | 唯一 ID（自增） |
| 2 | 时间戳 |
| 3 | 耗时（微秒） |
| 4 | 命令参数 |
| 5 | 客户端地址 |
| 6 | 客户端名称（CLIENT SETNAME 设置） |

## 关键配置

```properties
# redis.conf
# 超过多少微秒记入 slowlog（默认 10000 = 10ms）
slowlog-log-slower-than 10000

# slowlog 队列长度（默认 128，建议 1000+）
slowlog-max-len 1000

# 内存不够时直接清空（不建议，会丢历史）
slowlog-reset-on-rewrite no
```

### 阈值怎么定？

```
推荐阈值：5ms ~ 10ms（5000~10000 微秒）

理由：
- Redis 单命令理论 < 1ms
- 5ms 已经算异常
- 阈值太低会刷屏有效警告
```

```bash
# 临时调整（不需要重启）
redis-cli CONFIG SET slowlog-log-slower-than 5000
redis-cli CONFIG SET slowlog-max-len 2000
```

## 典型慢操作分析

### 慢操作 1：KEYS 命令

```bash
# 反面教材
redis-cli SLOWLOG GET
# 3) 1) (integer) 5678
#      3) (integer) 15234000      # 15 秒！
#      4) 1) "KEYS"
#         2) "session:*"
```

`KEYS pattern` 是 O(N) 全库扫描，1 亿 key 时要遍历 5 秒以上，期间 Redis 完全卡住。

**替代方案：SCAN**

```bash
# 用 SCAN 游标分批遍历
redis-cli SCAN 0 MATCH "session:*" COUNT 1000
# 1) "12345"          # 下一个 cursor
# 2) 1) "session:abc"
#    2) "session:def"
#    ...

# 配合 xargs 删除
redis-cli --scan --pattern "session:expired:*" | xargs -L 500 redis-cli UNLINK
```

### 慢操作 2：DEL 大 Key

```bash
redis-cli SLOWLOG GET
# 3) (integer) 256000      # 256ms
#    4) "DEL"
#    5) "cart:user:12345"
```

DEL 是同步删除，会阻塞主线程。

**替代方案**：

```bash
# 1. 用 UNLINK（Redis 4.0+，默认 lazyfree）
redis-cli UNLINK "cart:user:12345"

# 2. 用 HSCAN 分批删
redis-cli HSCAN "cart:user:12345" 0 COUNT 1000 | \
  awk 'NR%2==0' | xargs -I {} redis-cli HDEL "cart:user:12345" {}
```

### 慢操作 3：全量 SCAN

```bash
redis-cli SLOWLOG GET
# 3) 3) (integer) 520000      # 520ms
#      4) "SCAN"
```

SCAN 本身是 O(1)，但一次 SCAN COUNT 1000 遍历 1 亿 key 需要 10w 次调用，每次 5ms 就累成 500s。

**优化**：

```bash
# 加大 COUNT
redis-cli SCAN 0 MATCH "*" COUNT 10000

# 用 SSCAN / HSCAN / ZSCAN 遍历单集合
redis-cli HSCAN "big:hash" 0 COUNT 5000
```

### 慢操作 4：RENAME / SORT / SUNION 等

```bash
redis-cli SLOWLOG GET
# 3) 3) (integer) 89000       # 89ms
#      4) "SORT"
#      5) "rank:all"
```

`SORT` 默认会触发 STORE，会复制整个列表；`SUNION` / `SINTER` / `ZUNION` 都是 O(N) 集合运算。

**避免方案**：
- `SORT` 数据量大时改用 `ZRANGEBYSCORE` + 业务层排序
- 集合运算前判断大小：`SCARD key`

### 慢操作 5：Lua 脚本超时

```bash
redis-cli SLOWLOG GET
# 4) 4) "EVALSHA"
#    5) "..."
#    6) ")"
#    3) (integer) 5000000    # 5 秒
```

Lua 脚本执行期间阻塞整个 Redis。

```properties
# redis.conf
lua-time-limit 5000    # 5 秒强制终止
```

**规范**：
- 单个 Lua 脚本 < 1ms
- 避免在 Lua 里调用 `KEYS *`
- 用 `redis.call('TIME')` 加超时保护

```lua
-- 推荐：带时间检查的脚本
local start = tonumber(redis.call('TIME')[1])
-- ... 业务逻辑 ...
local now = tonumber(redis.call('TIME')[1])
if now - start > 1 then
    return redis.error_reply("timeout")
end
```

## 慢查询分析方法论

### 步骤 1：抓全量慢查询

```bash
# 抓最近 100 条
redis-cli SLOWLOG GET 100 > slowlog_$(date +%Y%m%d).log

# 按耗时排序
sort -t, -k3 -nr slowlog.log | head -20
```

### 步骤 2：聚类分析

```bash
# 统计命令类型分布
awk -F'"' '{print $2}' slowlog.log | sort | uniq -c | sort -rn
# 15234 KEYS
#  8210 DEL
#  1203 EVALSHA
```

### 步骤 3：定位热点

```bash
# 提取所有命令涉及的 key
awk '/^[0-9]+)/{flag=1; next} /^$/{flag=0} flag' slowlog.log | \
  awk '{for(i=2;i<=NF;i++) if($i !~ /^"$/) print $i}' | \
  sort | uniq -c | sort -rn | head -20
```

### 步骤 4：定位客户端

```bash
grep -oE '"[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+"' slowlog.log | \
  sort | uniq -c | sort -rn | head
# 找出哪个客户端在发慢命令
```

## 优化方案汇总

| 慢操作 | 根因 | 替代方案 |
|---|---|---|
| `KEYS pattern` | O(N) 全扫描 | `SCAN cursor MATCH pattern COUNT n` |
| `DEL bigkey` | 同步阻塞 | `UNLINK` / 分批 HDEL |
| `RENAME bigkey` | 同上 | 用 `RENAMENX` + 手动迁移 |
| `SORT` | 默认会复制 | 加 `LIMIT offset count` |
| `SUNIONSTORE` | O(N) 合并 | 业务层合并 / 用 Sorted Set |
| Lua 脚本长 | 单线程阻塞 | 拆脚本 / 加超时检查 |
| `FLUSHDB` | 全清阻塞 | 用 `FLUSHDB ASYNC` |

## 监控集成

把 SLOWLOG 接入 Prometheus：

```bash
# Redis Exporter 默认暴露 redis_slowlog_length
curl http://redis-exporter:9121/metrics | grep slowlog
# redis_slowlog_last_id 1234
# redis_slowlog_length 56
```

Grafana 告警配置：

```yaml
# alertmanager rule
- alert: RedisSlowQuery
  expr: redis_slowlog_length > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Redis 慢查询过多"
    description: "{{ $labels.instance }} 慢查询队列长度 {{ $value }}"
```

## 生产监控案例

### 案例 1：KEYS 命令把 Redis 卡 30 秒

某天凌晨，Redis 实例卡死：

```bash
redis-cli SLOWLOG GET 10
# 1) 3) (integer) 30000000   # 30 秒
#      4) 1) "KEYS"
#         2) "user:*"
#    5) "10.0.5.23:54321"     # 应用服务器 IP
```

定位：是某应用凌晨定时任务调 `KEYS user:*` 清理用户数据。

修复：
1. 临时 `SLOWLOG RESET` 后重启
2. 应用改成 `SCAN cursor MATCH "user:*" COUNT 1000`
3. 加监控：发现 KEYS 命令立刻告警

### 案例 2：Lua 脚本 OOM

某营销活动 Lua 脚本里调用 `KEYS *` 取所有用户积分排序，结果在 Redis 里跑了 5 秒被强制 kill：

```
BUSY script execution forced to stop
```

排查：

```lua
-- 错误写法
local keys = redis.call('KEYS', 'points:*')
local list = {}
for _, k in ipairs(keys) do
    table.insert(list, redis.call('GET', k))
end
table.sort(list)
```

修复：

```lua
-- 正确写法：用 SSCAN + 限制处理量
local cursor = "0"
local count = 0
local max = 1000
repeat
    local result = redis.call('SCAN', cursor, 'MATCH', 'points:*', 'COUNT', 100)
    cursor = result[1]
    for _, k in ipairs(result[2]) do
        if count < max then
            -- 处理
            count = count + 1
        end
    end
until cursor == "0" or count >= max
```

## 下一步

找到慢查询根因后，还需要建立完整的监控体系，让问题在发生时就告警。看 [📊 监控告警](/07-ops/monitoring)，搭一套 Prometheus + Grafana + Alertmanager 的标准方案。