---
title: SPIFFE / SPIRE
---

# SPIFFE / SPIRE

## 一句话总结

> **SPIFFE = 工作负载身份标准**。**SPIRE = SPIFFE Runtime Environment（实现）**。**核心：SVID（X.509 证书 / JWT）+ 自动签发 + 短期**。**服务网格 / 零信任 / mTLS 的身份基座**。

---

## SPIFFE 4 组件

```
┌────────────────────────────────────────┐
│  SPIFFE 4 个核心概念                    │
│  ├── SPIFFE ID（身份 URI）             │
│  │   spiffe://trust-domain/ns/name     │
│  ├── SVID（可验证身份文档）             │
│  │   ├── X.509-SVID（X.509 证书）      │
│  │   └── JWT-SVID（JWT）               │
│  ├── Workload API（应用获取 SVID）      │
│  └── Federated Trust（跨集群信任）     │
└────────────────────────────────────────┘
```

## SPIFFE ID 格式

```
spiffe://trust-domain/ns/<namespace>/sa/<service-account>
       │              │              │
       │              │              └─ K8s ServiceAccount
       │              └─ K8s Namespace
       └─ 信任域（类似组织域名）
```

## 实战：SPIRE 部署

```bash
# 1. 启动 SPIRE Server
spire-server run -config conf/server/server.conf

# 2. 启动 SPIRE Agent（每个节点）
spire-agent run -config conf/agent/agent.conf -joinToken <token>

# 3. 注册 Workload
spire-server api create registration     -spiffeID spiffe://example.com/ns/prod/sa/order-service     -parentID spiffe://example.com/spire/agent/k8s-node-1     -selector k8s:ns:prod     -selector k8s:sa:order-service     -ttl 3600
```

```yaml
# SPIRE K8s 自动注册（用 spire-controller-manager）
apiVersion: spire.spiffe.io/v1alpha1
kind: ClusterSPIFFEID
metadata:
  name: order-service
spec:
  spiffeIDTemplate: "spiffe://example.com/ns/{{ .PodMeta.Namespace }}/sa/{{ .PodSpec.ServiceAccountName }}"
  podSelector:
    matchLabels:
      app: order-service
  namespaceSelector:
    matchLabels:
      name: prod
```

## 实战：Java 应用获取 SVID

```java
import io.spiffe.spire.SpireClient;
import io.spiffe.spire.Svid;

public class App {
    public static void main(String[] args) {
        // SPIRE SDK
        SpireClient client = SpireClient.newSocketClient("/run/spire/sockets/agent.sock");
        Svid svid = client.fetchX509Svid();
        System.out.println("Spiffe ID: " + svid.getSpiffeId());
        System.out.println("Cert: " + svid.getCert());
    }
}
```

## 实战：Envoy + SPIRE

```yaml
# Envoy SDS 配置
static_resources:
  listeners:
    - address: { socket_address: { address: 0.0.0.0, port_value: 8443 } }
      filter_chains:
        - transport_socket:
            name: envoy.transport_sockets.tls
            typed_config:
              common_tls_context:
                tls_certificate_sds_secret_configs:
                  - name: spiffe_cert
                    sds_config:
                      api_config_source:
                        api_type: GRPC
                        grpc_services:
                          - envoy_grpc:
                              cluster_name: spire_agent
              validation_context_sds_secret_config:
                name: spiffe_validation
                sds_config:
                  api_config_source:
                    api_type: GRPC
                    grpc_services:
                      - envoy_grpc:
                          cluster_name: spire_agent
```

## 实战：Istio 用 SPIRE

```yaml
# Istio 默认从 k8s 拿 ServiceAccount 证书
# 配合 SPIRE 增强
meshConfig:
  defaultConfig:
    # 启用 SDS（Secret Discovery Service）
    sds:
      enabled: true
  trustDomain: "example.com"
```

## 实战：Istio AuthorizationPolicy 用 SPIFFE ID

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: order-service
  namespace: prod
spec:
  selector:
    matchLabels:
      app: order-service
  rules:
    - from:
        - source:
            principals:
              - "spiffe://example.com/ns/prod/sa/frontend"
      to:
        - operation:
            methods: ["GET", "POST"]
            paths: ["/api/v1/orders"]
```

## 实战：JWT-SVID

```bash
# 签发 JWT-SVID
spire-server api fetch jwt-svid -spiffeID spiffe://example.com/sa/order-service

# 验证 JWT-SVID
jwt decode <token>
```

## 实战：联邦信任（Federated）

```hcl
# SPIRE Server 配置
federation {
  bundle_endpoint {
    address = "0.0.0.0:8443"
    trust_domain = "example.com"
  }
  trusts {
    spiffe_id_matches {
      spiffe_id_pattern = "spiffe://partner.example.com/*"
    }
    bundle_endpoint_url = "https://spire.partner.example.com"
  }
}
```

## 关联章节

- **06-zero-trust/overview**：零信任总览
- **06-zero-trust/implementation**：零信任落地
- **04-network/mtls**：mTLS 双向认证
- **cloud-native**：Istio 服务网格

## 一句话总结

> **SPIFFE = 工作负载身份标准**。**SPIRE = 实现**。**核心：SVID（自动签发 + 短期）+ Workload API**。**服务网格 / 零信任 / mTLS 的身份基座**。


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
