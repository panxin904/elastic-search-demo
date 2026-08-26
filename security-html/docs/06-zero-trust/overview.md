---
title: 零信任架构总览
---

# 零信任架构

## 一句话总结

> **零信任 = "Never Trust, Always Verify"**。**核心三原则：默认拒绝所有（默认 deny）/ 最小权限（least privilege）/ 持续验证（continuous verification）**。**关键技术：mTLS / SPIFFE / SDP / BeyondCorp**。**业务结果：取代 VPN，服务网格标配**。

---

## 传统 vs 零信任

```
┌────────────────────────────────────────────┐
│  传统边界安全（Castle-and-Moat）            │
│  ┌────────────────────────────────────┐    │
│  │         防火墙 = 边界              │    │
│  │  ┌──────────┐    ┌──────────┐     │    │
│  │  │ 内网：可信 │    │ 外网：威胁 │     │    │
│  │  └──────────┘    └──────────┘     │    │
│  │  内网一旦攻破 = 全军覆没           │    │
│  └────────────────────────────────────┘    │
├────────────────────────────────────────────┤
│  零信任（BeyondCorp）                      │
│  ┌────────────────────────────────────┐    │
│  │  每个请求都要验证身份 + 设备 +     │    │
│  │  上下文 + 持续鉴权                  │    │
│  │  内部外部，无差别                    │    │
│  │  攻破一个点 ≠ 攻破全部             │    │
│  └────────────────────────────────────┘    │
└────────────────────────────────────────────┘
```

## 三大原则

| 原则 | 含义 | 落地 |
|------|------|------|
| **默认拒绝** | 所有访问默认 deny | K8s NetworkPolicy 默认 all-deny |
| **最小权限** | 只给必需的权限 | RBAC / ABAC / OAuth 2.0 scope |
| **持续验证** | 每次请求都验证 | mTLS + 短期证书 + JWT 短期 token |

## 核心技术栈

| 层级 | 技术 | 作用 |
|------|------|------|
| **身份** | OAuth 2.0 / OIDC / SAML | 身份认证 |
| **工作负载身份** | SPIFFE / SPIRE | 服务间身份 |
| **网络** | mTLS / WireGuard | 加密通信 |
| **访问控制** | OPA / Cedar / OpenFGA | 策略引擎 |
| **SDP** | Cloudflare Access / Tailscale | 零信任网络接入 |
| **服务网格** | Istio / Linkerd / Consul | 透明 mTLS |

## SPIFFE 框架

```
┌────────────────────────────────────────┐
│  SPIFFE = Secure Production Identity   │
│  Framework for Everyone               │
│                                        │
│  SVID = SPIFFE Verifiable Identity    │
│  Document（X.509 证书或 JWT）          │
│                                        │
│  URI 格式：                            │
│  spiffe://trust-domain/path           │
│  例：spiffe://prod.example.com/ns/foo │
│      /sa/bar                           │
└────────────────────────────────────────┘
```

## 实战：Google BeyondCorp 8 步迁移

1. **Single Sign-On**（统一身份）
2. **User Inventory**（员工 / 设备 / 应用清单）
3. **Device Inventory**（设备合规）
4. **Access Control Engine**（策略引擎）
5. **Trust Tier**（设备分级）
6. **Migrate Application**（逐步迁移）
7. **Externalize Apps**（无 VPN）
8. **Continuous Validation**（持续验证）

## 实战：Istio mTLS 零信任

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT  # 强制所有服务间 mTLS
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-frontend
  namespace: prod
spec:
  selector:
    matchLabels:
      app: order-service
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/prod/sa/frontend"]
      to:
        - operation:
            methods: ["GET", "POST"]
            paths: ["/api/v1/orders*"]
```

## 关联章节

- **02-auth**：OAuth 2.0 / OIDC 身份基础
- **03-crypto/asymmetric**：非对称加密（mTLS 基础）
- **04-network/mtls**：mTLS 双向认证
- **05-container/supply-chain**：SPIFFE Workload Identity

## 一句话总结

> **零信任 = 默认拒绝 + 最小权限 + 持续验证**。**技术栈：SPIFFE 给身份 + mTLS 给加密 + OPA 给策略 + 服务网格给落地**。**业务结果：取代 VPN，服务网格默认安全**。


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
