---
title: 零信任落地实践
---

# 零信任落地实践

## 一句话总结

> **零信任落地 = 5 步走（SSO → 设备清单 → 身份引擎 → 信任分级 → 迁移）**。**核心：身份 + 设备 + 上下文 = 持续访问决策**。**业务结果：取代 VPN + 服务网格默认安全 + SaaS 零信任**。

---

## Google BeyondCorp 8 步迁移

```
┌────────────────────────────────────────┐
│  Step 1：统一 SSO                       │
│  Step 2：用户 / 设备 / 应用 清单         │
│  Step 3：访问控制引擎                   │
│  Step 4：Trust Tier（设备分级）         │
│  Step 5：逐步迁移应用                   │
│  Step 6：外部化（无 VPN）                │
│  Step 7：持续验证（实时决策）            │
│  Step 8：去掉传统 VPN                   │
└────────────────────────────────────────┘
```

## 实战：BeyondCorp 信任层级

| 层 | 设备要求 | 访问级别 |
|----|---------|---------|
| **Tier 0** | 公司管理 + 加密 + 最新补丁 | 完全访问 |
| **Tier 1** | 公司管理 + 加密 | 内部应用 |
| **Tier 2** | BYOD + 注册 | 公开应用 |
| **Tier 3** | 未注册 | 拒绝 |

## 实战：Cloudflare Access（零信任 SDP）

```yaml
# Cloudflare Zero Trust 配置
# 1. 创建应用
---
name: "Internal Wiki"
type: "self_hosted"
session_duration: "24h"
app_launcher_visible: true
policies:
  - name: "Employees only"
    decision: "allow"
    include:
      - email: "*@company.com"
    require:
      - mfa: true
      - device_posture:
          os_version: ">= 14"
          firewall: "on"
```

## 实战：Tailscale（个人零信任 VPN）

```bash
# 安装
# macOS
brew install tailscale
# 启动
sudo tailscale up

# 共享设备
tailscale status

# ACL（访问控制）
# tailnet-policy.json
{
  "acls": [
    {
      "action": "accept",
      "src": ["group:engineers"],
      "dst": ["tag:prod:*"]
    }
  ]
}
```

## 实战：Okta + Workforce Identity

```yaml
# Okta 设备信任
device_assurance:
  - name: "High Trust"
    os_min_version: "macOS 13"
    disk_encryption: required
    screen_lock: required
    jailbreak: blocked

# 条件访问
policy:
  name: "Block unknown device"
  conditions:
    - device.trust != "managed"
  actions:
    - deny
```

## 实战：服务网格零信任（Istio）

```yaml
# 1. 全命名空间默认 mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT

# 2. 授权策略
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payment-service
  namespace: prod
spec:
  selector:
    matchLabels:
      app: payment-service
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/prod/sa/order-service"]
      to:
        - operation:
            methods: ["POST"]
            paths: ["/api/v1/payments*"]

# 3. 请求认证（JWT）
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: prod
spec:
  selector:
    matchLabels:
      app: payment-service
  jwtRules:
    - issuer: "https://auth.example.com"
      jwksUri: "https://auth.example.com/.well-known/jwks.json"
```

## 实战：OPA（Open Policy Agent）

```rego
# OPA 策略：谁能访问 payment
package payment.authz

default allow = false

allow {
    input.method == "POST"
    input.path == "/api/v1/payments"
    input.user.role == "finance"
    input.request_time >= "09:00:00"
    input.request_time <= "18:00:00"
    not input.user.flagged
}

allow {
    input.method == "GET"
    input.path == "/api/v1/payments"
    input.user.role in ["finance", "viewer"]
}
```

```yaml
# Envoy 集成 OPA
envoy.filters.http.ext_authz:
  - name: envoy.ext_authz
    config:
      grpc_service:
        envoy_grpc:
          cluster_name: opa
      with_request_body:
        max_request_bytes: 8192
        allow_partial_message: true
```

## 实战：Cedar（AWS 授权策略）

```cedar
# Cedar 策略
permit (
    principal in Role::"OrderService",
    action in [Action::"call", Action::"read"],
    resource in Resource::"PaymentService"
) when {
    principal has tenant && principal.tenant == resource.tenant
};
```

## 实战：传统应用零信任迁移

```yaml
# 阶段 1：OAuth 2.0 + OIDC 接入
# 阶段 2：JWT 替代 Session
# 阶段 3：API 网关强鉴权
# 阶段 4：服务网格 mTLS
# 阶段 5：删除 VPN
```

## 实战：业务约束（BeyondCorp 实战）

```python
# 业务规则：只在工作时间 + 公司内访问
def check_access(user, device, request):
    if user.department != "Finance":
        return False
    if not device.is_managed:
        return False
    if request.geo.country != "CN":
        return False
    if request.time < time(9, 0) or request.time > time(18, 0):
        return False
    return True
```

## 实战：监控与审计

```yaml
# 持续验证
- name: "Login outside business hours"
  query: |
    event=login AND result=success
    AND hour < 9 OR hour > 18
  alert: "Suspicious login"
  severity: medium

- name: "Access from new country"
  query: |
    event=access AND resource.intern=true
    AND user.country != user.last_country
  alert: "Possible account takeover"
  severity: high
```

## 关联章节

- **06-zero-trust/overview**：零信任总览
- **06-zero-trust/spiffe**：SPIFFE / SPIRE
- **04-network/mtls**：mTLS 双向认证
- **02-auth/oidc**：OIDC 身份

## 一句话总结

> **零信任落地 = SSO + 设备清单 + 信任分级 + 持续验证**。**技术栈：SPIFFE（身份）+ mTLS（加密）+ OPA（策略）+ 服务网格（落地）**。**业务结果：取代 VPN + SaaS 零信任**。


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
