---
title: A09 日志与监控失效
date: 2026-08-15  # date-auto-injected
---

# A09 · Security Logging & Monitoring Failures（日志与监控失效）

## 一句话总结

> **A09 = 攻击者来了你不知道**。**典型：登录失败不记录 / 告警缺位 / 日志被攻击者清除 / 审计日志不可追溯**。**防御：完整审计日志 + 实时告警 + 不可篡改的日志存储**。

---

## 常见失效

| 失效 | 后果 |
|------|------|
| 登录失败不记录 | 暴力破解无人知 |
| 关键操作不审计 | 数据泄漏无法追溯 |
| 日志只存本地 | 攻击者 rm -rf |
| 没有告警 | 攻击 30 天才发现 |
| 缺乏演练 | 真实事件慌乱 |
| 缺乏关联 | 单点异常无法识别攻击链 |

## 实战：缺失日志 = 攻击者 200 天未被发现

```bash
# 真实案例：某公司 200 天才发现数据泄漏
# 攻击者每天导出 10 GB
# 没有"外发流量异常"告警
```

## 实战：JWT 异常监控

```python
import logging

# 登录失败
def on_login_failed(username, ip):
    logging.warning(f"LOGIN_FAILED user={username} ip={ip}")

# JWT 异常
def on_jwt_invalid(jwt_token, reason):
    logging.error(f"JWT_INVALID reason={reason} token_prefix={jwt_token[:20]}")

# 限流触发
def on_rate_limit_exceeded(ip, endpoint):
    logging.warning(f"RATE_LIMIT_EXCEEDED ip={ip} endpoint={endpoint}")
```

## 实战：审计日志结构

```json
{
  "timestamp": "2026-08-10T10:30:00.123Z",
  "event_type": "user.login",
  "result": "success",
  "user_id": 12345,
  "username": "alice@example.com",
  "ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "mfa": "totp",
  "session_id": "sess_abc123",
  "request_id": "req_xyz789",
  "geo": {"country": "CN", "city": "Beijing"}
}
```

## 实战：实时告警（SIEM）

```yaml
# Splunk / ELK / Datadog SIEM 规则
- name: "Suspicious login from new country"
  query: |
    event_type=user.login AND result=success
    | lookup geoip ip
    | stats count by user_id, country
    | where count > 1 and country != "CN"
  alert: "Possible account takeover"
  severity: high

- name: "Privilege escalation"
  query: |
    event_type=user.role_changed AND new_role="admin"
  alert: "New admin created"
  severity: critical
```

## 实战：日志不可篡改

```bash
# 集中日志存储 + WORM (Write Once Read Many)
# AWS S3 Object Lock
aws s3api put-object-lock-configuration     --bucket audit-logs     --object-lock-configuration '{
        "ObjectLockEnabled": "Enabled",
        "Rule": {
            "DefaultRetention": {
                "Mode": "GOVERNANCE",
                "Years": 7
            }
        }
    }'

# 或用 syslog-ng 远程 + 签名
```

## 防御清单

| 措施 | 落地 |
|------|------|
| 登录审计 | 成功 / 失败 / 异常全部记录 |
| 关键操作 | 权限变更 / 数据导出 / 资金操作 |
| 集中日志 | ELK / Loki / Splunk / Datadog |
| 长期保留 | 7 年（合规）/ 1 年（普通）|
| 实时告警 | SIEM / 异常检测 |
| 不可篡改 | S3 Object Lock / WORM |
| 演练 | 季度红蓝对抗 |

## 关联章节

- **observability/08-alerting**：告警与值班
- **observability/09-app-instrumentation**：日志埋点
- **01-web-top10/a04-insecure-design**：A04 不安全设计 = 监控缺失设计

## 一句话总结

> **A09 日志缺失 = 攻击者隐身**。**核心：完整审计 + 实时告警 + 不可篡改 + 持续演练**。**没有预警 = 200 天才发现**。


<!-- auto-enrich:do-not-edit -->

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
