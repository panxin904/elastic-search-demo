---
title: Loki Pipeline 处理
description: Promtail pipeline stages / 字段提取 / 转换
---

# Loki Pipeline 处理

> **TL;DR**：**Pipeline = Promtail 把原始日志解析成结构化字段的规则链**。**核心 stage：regex / json / logfmt / timestamp / label / template / drop / limit**。**类比 Logstash filter，但更轻量**。**实战：把 nginx 默认日志解析成结构化字段，便于 LogQL 查询**。

## 一句话定义

```
Pipeline = Promtail 的日志处理规则链
         = 顺序应用多个 stage（解析 / 转换 / 丢弃）
         = 类似 Logstash filter / Fluentd filter
         = 输出：提取的字段 + 标签（可加入 Loki 索引）
```

## Pipeline Stage 一览

| Stage | 功能 |
|---|---|
| `regex` | 正则提取字段 |
| `json` | JSON 解析 |
| `logfmt` | logfmt 解析 |
| `timestamp` | 提取/转换时间戳 |
| `label` | 提取字段作为标签 |
| `template` | 模板字符串 |
| `drop` | 丢弃匹配行 |
| `limit` | 限制速率 |
| `replace` | 字符串替换 |
| `match` | 条件分支 |
| `merge` | 多行合并 |

## 实战案例：nginx access log

```yaml
# Promtail 配置
scrape_configs:
  - job_name: nginx
    static_configs:
      - targets: [localhost]
        labels:
          job: nginx
          __path__: /var/log/nginx/*.log
    pipeline_stages:
      # 1. 正则提取字段
      - regex:
          expression: '^(?P<remote_addr>\S+) - \S+ \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d+) (?P<bytes>\d+) (?P<req_time>\S+)'

      # 2. 提取字段作为标签（labels，影响 Loki 索引）
      - labels:
          method:
          status:

      # 3. 转换时间戳
      - timestamp:
          source: time
          format: '02/Jan/2006:15:04:05 -0700'

      # 4. 丢弃 favicon 请求
      - match:
          selector: '{job="nginx"}'
          stages:
            - drop:
                expression: ".*favicon\.ico.*"
                older_than: 1h
```

## 实战案例：JSON 日志

```yaml
pipeline_stages:
  # 1. 解析 JSON 到 root
  - json:
      expressions:
        level: level
        msg: message
        trace_id: trace_id
      # 把 JSON 字段也作为 Loki 标签
      # 注意：高基数字段不要作为标签

  # 2. 应用格式
  - template:
      source: msg
      template: '{{ .msg }}'

  # 3. 提取 status_code
  - label:
      level:
```

## 实战案例：Java 应用日志

```bash
# 输入日志：
# 2026-08-09 14:23:45.123 ERROR [http-nio-8080-exec-3] com.example.Service - NullPointerException at UserService.java:42
```

```yaml
pipeline_stages:
  - regex:
      expression: '^(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) (?P<level>\S+) \[[^\]]+\] (?P<logger>\S+) - (?P<msg>.*)'
      # 提取：time / level / logger / msg

  - labels:
      level:    # level 作为标签（低基数）
      logger:   # logger 名作为标签

  - timestamp:
      source: time
      format: '2006-01-02 15:04:05.000'

  # 提取异常类型到 msg 字段
  - regex:
      expression: '(?P<exception>\w+Exception)'
      # 配合第一个 regex 的 msg
```

## 高级技巧

### 1. 条件分支

```yaml
pipeline_stages:
  - match:
      selector: '{job="nginx", status="5.."}'
      stages:
        - regex:
            expression: '...'
        # 只对 5xx 应用额外处理
```

### 2. 多行合并（Java stack trace）

```yaml
pipeline_stages:
  # 检测：以 "	at " 开头的行是上一行的延续
  - match:
      selector: '{job="java"}'
      stages:
        - regex:
            # 匹配 stack trace 起始行（含 "Exception"）
            expression: '.*(?P<exception>\w+Exception)'
        - template:
            source: msg
            template: '{{ .msg }}'
```

## 性能优化

```
- regex 顺序：先简单后复杂
- 提取的字段越少越好（labels 尤其）
- 避免高基数字段作为标签
- drop stage 减少写入量
- limit stage 限制单文件速率（防爆）
```

## 一句话总结

> **Pipeline = Promtail 日志解析链**。**核心 stage：regex / json / logfmt / timestamp / labels / drop**。**先解析后打标，性能可控**。

---

## 关联章节

- [Loki 概览](../05-loki/overview.md)
- [LogQL 查询](../05-loki/logql.md)
- [Loki 最佳实践](../05-loki/best-practice.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
