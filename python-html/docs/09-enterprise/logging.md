---
title: 日志与监控
---

# 🔍 日志与监控

> **可观测性（Observability）**是生产环境稳定运行的基石。本章详解 Python 应用的日志、监控和告警。

## 🎯 可观测性三大支柱

```
1. 日志（Logging）：离散事件记录（"发生了什么"）
2. 指标（Metrics）：数值化测量（"现在怎样"）
3. 追踪（Tracing）：请求链路（"哪里慢了"）
```

## 📝 日志（Logging）

### Python logging 基础

```python
import logging

# 1. 基本配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# 2. 使用
logger = logging.getLogger(__name__)
logger.info("User logged in")
logger.warning("Disk space low")
logger.error("Failed to process")
```

### 字典配置

```python
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)d"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s"
        }
    },
    
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "formatter": "json",
            "level": "INFO"
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/error.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "formatter": "detailed",
            "level": "ERROR"
        }
    },
    
    "loggers": {
        "": {  # root logger
            "handlers": ["console", "file", "error_file"],
            "level": "INFO"
        },
        "myapp": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}

import logging.config
logging.config.dictConfig(LOGGING_CONFIG)
```

### 结构化日志（推荐）

```python
from pythonjsonlogger import jsonlogger

# JSON 日志（适合 ELK / Loki 等日志系统）
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
))
logger.addHandler(handler)

# 输出
logger.info("User login", extra={
    "user_id": 123,
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0"
})
# {"asctime": "...", "levelname": "INFO", "name": "root", 
#  "message": "User login", "user_id": 123, "ip": "192.168.1.1"}
```

### 上下文日志

```python
import logging
from contextvars import ContextVar

# 上下文变量（用于链路追踪）
request_id_var = ContextVar("request_id", default="")
user_id_var = ContextVar("user_id", default="")

# 日志过滤器
class ContextFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        record.user_id = user_id_var.get()
        return True

# 中间件中设置上下文
from fastapi import Request

@app.middleware("http")
async def log_context(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# 业务代码中自动带上下文
logger.info("Processing order")  # 自动包含 request_id
```

## 📊 指标（Metrics）

### Prometheus 指标

```bash
pip install prometheus-client prometheus-fastapi-instrumentator
```

```python
from prometheus_client import Counter, Histogram, Gauge, Summary

# 1. Counter（单调递增）
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

# 2. Histogram（分布）
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"]
)

# 3. Gauge（当前值）
ACTIVE_USERS = Gauge(
    "active_users",
    "Number of active users"
)

# 4. Summary（分位数）
REQUEST_SIZE = Summary(
    "http_request_size_bytes",
    "HTTP request size"
)
```

### FastAPI 集成

```python
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# 自动埋点（推荐）
Instrumentator().instrument(app).expose(app)

# 或手动埋点
@app.get("/orders")
async def list_orders():
    REQUEST_COUNT.labels(method="GET", endpoint="/orders", status="200").inc()
    with REQUEST_LATENCY.labels(method="GET", endpoint="/orders").time():
        orders = db.query("SELECT * FROM orders")
    return orders
```

### 暴露指标端点

```python
from prometheus_client import generate_latest
from starlette.responses import Response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### 业务指标

```python
# 业务自定义指标
ORDERS_CREATED = Counter("orders_created_total", "Total orders created")
ORDERS_AMOUNT = Histogram("orders_amount", "Order amount distribution")
USER_BALANCE = Gauge("user_balance", "User balance", ["user_id"])

@app.post("/orders")
async def create_order(order: Order):
    ORDERS_CREATED.inc()
    ORDERS_AMOUNT.observe(order.amount)
    return {"order_id": "12345"}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = db.get_user(user_id)
    USER_BALANCE.labels(user_id=user_id).set(user.balance)
    return user
```

## 🔍 追踪（Tracing）

### OpenTelemetry

```bash
pip install opentelemetry-api opentelemetry-sdk
pip install opentelemetry-instrumentation-fastapi
pip install opentelemetry-exporter-jaeger
```

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# 1. 设置 Tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# 2. 配置 Exporter（Jaeger）
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# 3. FastAPI 自动埋点
app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

# 4. 手动埋点
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    with tracer.start_as_current_span("get_user"):
        user = db.get_user(user_id)
        return user
```

### 链路追踪

```python
@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    with tracer.start_as_current_span("get_order") as span:
        span.set_attribute("order.id", order_id)
        
        # 调用其他服务（自动追踪）
        order = order_service.get(order_id)
        
        with tracer.start_as_current_span("get_user_info"):
            user = user_service.get(order.user_id)
        
        return {"order": order, "user": user}
```

## 🛠️ 完整监控方案

### Prometheus + Grafana

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: myapp
    static_configs:
      - targets: ['myapp:8000']
    metrics_path: /metrics
```

```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  prometheus-data:
  grafana-data:
```

### ELK 日志方案

```yaml
# docker-compose.logging.yml
services:
  elasticsearch:
    image: elasticsearch:8.0.0
    environment:
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms512m -Xmx512m
    volumes:
      - es-data:/usr/share/elasticsearch/data

  logstash:
    image: logstash:8.0.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: kibana:8.0.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch

volumes:
  es-data:
```

```ruby
# logstash.conf
input {
  file {
    path => "/var/log/app/*.log"
    codec => "json"
  }
}

filter {
  # 解析 JSON 日志
  json {
    source => "message"
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "app-logs-%{+YYYY.MM.dd}"
  }
}
```

## 🛠️ 实战：完整 FastAPI 应用监控

```python
# main.py
import logging
import time
from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

# 1. 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# 2. Prometheus 指标
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "app_request_duration_seconds",
    "Request duration",
    ["method", "endpoint"]
)

# 3. FastAPI 应用
app = FastAPI()

# 4. 监控中间件
@app.middleware("http")
async def monitor(request: Request, call_next):
    start = time.time()
    
    # 记录请求日志
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # 记录指标
    duration = time.time() - start
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    # 响应头
    response.headers["X-Process-Time"] = str(duration)
    return response

# 5. 业务端点
@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    logger.info(f"Fetching order {order_id}")
    order = {"id": order_id, "amount": 99.9}
    return order

# 6. Prometheus 暴露
Instrumentator().instrument(app).expose(app)
```

## 🛠️ 告警配置

### Prometheus 告警规则

```yaml
# alerts.yml
groups:
  - name: app_alerts
    interval: 30s
    rules:
      # 高错误率
      - alert: HighErrorRate
        expr: |
          sum(rate(app_requests_total{status=~"5.."}[5m])) / 
          sum(rate(app_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "错误率超过 5%"
      
      # 高延迟
      - alert: HighLatency
        expr: |
          histogram_quantile(0.99, 
            sum(rate(app_request_duration_seconds_bucket[5m])) by (le)
          ) > 1
        for: 5m
        labels:
          severity: warning
      
      # 服务下线
      - alert: ServiceDown
        expr: up{job="myapp"} == 0
        for: 1m
        labels:
          severity: critical
```

### Alertmanager

```yaml
# alertmanager.yml
route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'default'
    webhook_configs:
      - url: 'http://example.com/alert'
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'xxx'
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/xxx'
        channel: '#alerts'
```

## 📊 关键指标

### RED 方法

```
Rate（请求速率）：
  - app_requests_total
  - app_errors_total

Errors（错误率）：
  - error_rate = errors_total / requests_total
  - status_code 5xx

Duration（延迟）：
  - app_request_duration_seconds
  - P50 / P95 / P99
```

### USE 方法

```
Utilization（资源利用率）：
  - CPU: process_cpu_seconds_total
  - Memory: process_resident_memory_bytes
  - Disk: node_filesystem_used_bytes

Saturation（饱和度）：
  - 队列长度
  - 等待时间

Errors（错误）：
  - OOM / Disk Full
```

## 🎯 总结

**日志与监控核心要点**：
- ✅ 结构化日志（JSON）
- ✅ 日志级别合理（DEBUG/INFO/WARNING/ERROR）
- ✅ 上下文日志（request_id、user_id）
- ✅ Prometheus 指标（RED/USE 方法）
- ✅ 链路追踪（OpenTelemetry）
- ✅ Grafana 可视化
- ✅ Prometheus 告警
- ✅ ELK / Loki 日志系统
- ⚠️ 监控要全但不过度
- ⚠️ 告警要 actionable

**下一步：** [🛡️ 安全最佳实践](/09-enterprise/security) — Web 应用安全


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java](https://java-px.bot.cd/java-web-manual/):Java 对比
- [ai](https://java-px.bot.cd/ai/):AI / 机器学习
- [data](https://java-px.bot.cd/data/):数据处理
