---
title: Probe 与 Check
---

# Probe 与 Check

## 五种 Probe 类型

Litmus 提供五种 Probe 类型，用于显式断言实验成功/失败：

**1. httpProbe**：

```yaml
httpProbe:
  url: http://app:80/health
  method: GET
  expectedResponseCodes: ["200"]
  timeout: 5s
  interval: 2s
  retries: 3
```

**2. cmdProbe**：

```yaml
cmdProbe:
  command: "kubectl get pods -l app=nginx -o jsonpath='{.items[?(@.status.phase==\"Running\")].metadata.name}' | wc -l"
  expectedOutput: ">=3"
```

**3. promProbe**：

```yaml
promProbe:
  endpoint: http://prometheus:9090
  query: "rate(http_requests_total{status=~\"5..\"}[5m])"
  comparator: "LessThan"
  value: "0.05"
```

**4. sqlProbe**：

```yaml
sqlProbe:
  connectionInfo:
    host: postgres
    port: 5432
    user: chaos
    password: secret
    dbname: orders
  query: "SELECT COUNT(*) FROM orders WHERE created_at > NOW() - INTERVAL '5 minutes'"
  comparator: "GreaterThan"
  value: "100"
```

**5. k8sProbe**：

```yaml
k8sProbe:
  resourceType: "deployment"
  resourceName: "nginx"
  namespace: "default"
  statusCheck: true
  timeout: 30s
```

## Probe 模式

**Continuous（持续探测）**：

- 实验期间持续探测
- 失败立即中止实验
- 默认模式

```yaml
probe:
  - name: check-health
    type: httpProbe
    mode: Continuous
    runProperties:
      interval: 5s
      stopOnFailure: true
```

**OnChaos（故障时探测）**：

- 仅在故障开始时探测一次
- 验证「故障注入后」系统行为

```yaml
probe:
  - name: check-initial-response
    type: httpProbe
    mode: OnChaos
    runProperties:
      timeout: 30s
```

**EOT（End of Test）**：

- 故障结束时探测
- 验证「故障恢复后」系统行为

```yaml
probe:
  - name: check-recovery
    type: httpProbe
    mode: EOT
    runProperties:
      timeout: 60s
```

## Probe Property 详解

**runProperties 完整配置**：

```yaml
probe:
  - name: comprehensive-check
    type: promProbe
    mode: Continuous
    runProperties:
      probeTimeout: 60s       # 总超时（超过则失败）
      interval: 5s            # 探测间隔
      retry: 3                # 重试次数（连续 3 次失败才算失败）
      stopOnFailure: true     # 失败立即中止实验
      verbosity: info         # 日志级别（debug/info/warn/error）
```

**Probe 状态机**：

```
Probe Pending → Probe Running → Probe Completed
                  │
                  └→ Probe Failed (重试中)
```

**Probe 与 ChaosResult 关联**：

- Probe 成功 → ChaosResult verdict: Pass
- Probe 失败 → ChaosResult verdict: Fail

**实战建议**：

1. **多维度**：同时 Probe 业务指标 + 系统指标 + 资源
2. **持续探测**：Continuous 模式捕获「瞬时失败」
3. **快速失败**：stopOnFailure 减少实验影响
4. **合理重试**：retry=3 避免「假阳性」

## 与其他站点关系

- **observability/03-prometheus**：Prometheus Probe
- **devops/05-cicd-observability**：CI/CD 集成
- **chaos/02-chaos-mesh**：Chaos Mesh 间接验证对比


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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
