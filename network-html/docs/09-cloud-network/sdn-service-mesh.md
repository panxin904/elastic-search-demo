---
title: SDN 与 Service Mesh
---

# SDN 与 Service Mesh

<div class="nt-badge nt-badge-cloud">云网络</div>
<div class="nt-badge nt-badge-cases">进阶</div>

SDN（Software Defined Networking）将网络**控制面**与**数据面**分离；Service Mesh 是微服务时代的**服务间通信基础设施**。两者都体现了"网络可编程"的趋势。

## 1. SDN 概念

```
传统网络：
  路由器/交换机  = 控制面 + 数据面（紧耦合）

SDN：
  ┌──────────────┐     协议     ┌──────────────┐
  │  Controller   │ ──────────> │  Switch      │
  │  (控制面)     │  OpenFlow  │  (数据面)     │
  └──────────────┘             └──────────────┘
```

| 组件 | 作用 |
| --- | --- |
| Controller | 集中控制（ONOS、ODL、Floodlight） |
| Southbound | OpenFlow、NETCONF、OVSDB |
| Northbound | REST、gRPC |
| Switch | 转发（白盒交换机、OVS） |

## 2. SDN 优势

| 优势 | 说明 |
| --- | --- |
| 集中控制 | 全网视图，统一策略 |
| 可编程 | 自动化、API 驱动 |
| 灵活 | 快速变更、灰度 |
| 抽象 | 业务不感知网络细节 |

## 3. OpenFlow

最知名的 SDN 南向协议：

```
Controller ──> Switch：
  - PacketIn
  - FlowMod（增删改流表）
  - ReadState

Switch ──> Controller：
  - PacketIn
  - FlowRemoved
  - PortStatus
```

流表示例：

```
match: src_ip=10.0.0.1, dst_port=80
action: output → port 2
priority: 100
```

## 4. 虚拟交换机（OVS）

- Open vSwitch：开源虚拟交换机
- 数据中心 VM 互联
- 支持 OpenFlow、VXLAN、Geneve

```bash
ovs-vsctl add-br br0
ovs-vsctl add-port br0 eth0
ovs-vsctl set-controller br0 tcp:1.2.3.4:6653
```

## 5. Overlay 网络

| 隧道 | 协议号 | 描述 |
| --- | --- | --- |
| VXLAN | UDP 4789 | 最流行 |
| Geneve | UDP 6081 | 更通用 |
| GRE | IP 47 | 老牌 |
| STT | TCP 类似 | 已淘汰 |
| GENEVE | UDP | Cumulus / Linux |

VXLAN 帧：

```
Outer Ethernet | Outer IP | Outer UDP | VXLAN Header | Inner Ethernet | Inner IP | Payload
```

VXLAN 24 bit VNI = 16M 虚拟网络。

## 6. Underlay vs Overlay

| 维度 | Underlay | Overlay |
| --- | --- | --- |
| 层级 | 物理 / 链路 | 虚拟 / 隧道 |
| 设备 | 路由器、交换机 | 软件 |
| 隔离 | VLAN | VXLAN |
| 扩展 | 有限 | 16M+ 段 |

## 7. Service Mesh 概念

微服务间通信的**专用基础设施层**：

```
App A ──> Sidecar Proxy ──> Sidecar Proxy ──> App B
                          （Service Mesh）
```

| 组件 | 作用 |
| --- | --- |
| Data Plane | Sidecar 代理（Envoy） |
| Control Plane | 配置 / 策略 / 证书（Istio、Linkerd） |

## 8. Service Mesh 优势

| 优势 | 说明 |
| --- | --- |
| 解耦 | 业务代码与通信解耦 |
| 统一 | 流量管理、可观测、安全 |
| 跨语言 | Sidecar 代理 |
| 零侵入 | 业务无感升级 |

## 9. Istio 核心概念

| 概念 | 描述 |
| --- | --- |
| Envoy | 数据面 Sidecar |
| Pilot | 配置分发（xDS） |
| Citadel | 证书 / 安全 |
| Galley | 配置校验 |
| Mixer（旧） | 策略 / 遥测 |
| VirtualService | 路由规则 |
| DestinationRule | 目标策略 |
| Gateway | 入口网关 |
| ServiceEntry | 外部服务 |

## 10. Istio 流量管理示例

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts:
  - reviews
  http:
  - match:
    - headers:
        end-user:
          exact: jason
    route:
    - destination:
        host: reviews
        subset: v2
  - route:
    - destination:
        host: reviews
        subset: v1
```

## 11. 可观测性

| 维度 | 工具 |
| --- | --- |
| Metrics | Prometheus + Grafana |
| Logs | Loki / ELK |
| Traces | Jaeger / Zipkin |
| Topology | Kiali |

Mesh 自动注入：trace ID、metric、access log。

## 12. mTLS

- Sidecar 自动协商 mTLS
- Citadel 颁发短生命周期证书
- 业务代码无感知

## 13. 限流与熔断

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: ratings
spec:
  host: ratings
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: UPGRADE
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 30s
```

## 14. Mesh 对比

| 维度 | Istio | Linkerd | Consul Connect |
| --- | --- | --- | --- |
| 数据面 | Envoy | linkerd2-proxy | Envoy |
| 控制面 | istiod | linkerd | Consul |
| 性能 | 中 | 高 | 中 |
| 功能 | 强 | 中 | 中 |
| 学习曲线 | 陡 | 平 | 平 |

## 15. 实战：Mesh 部署

```bash
istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled
kubectl apply -f samples/bookinfo/platform/kube/bookinfo.yaml
```

## 16. 常见面试题

1. **SDN 核心？** 控制面 / 数据面分离，集中控制。
2. **OpenFlow 是什么？** SDN 南向协议。
3. **VXLAN 作用？** Overlay 隧道，扩展到 16M 段。
4. **Service Mesh 是什么？** 微服务通信基础设施层。
5. **Istio 数据面？** Envoy。
6. **mTLS 作用？** 自动双向加密，无需业务改代码。
