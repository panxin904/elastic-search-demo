---
title: 服务发现
date: 2026-08-15  # date-auto-injected
---
# 服务发现（Service Discovery）

## 1. 问题

```
微服务 A 调微服务 B：
  - B 的 IP 经常变（k8s pod IP 不固定）
  - B 可能有多个实例
  - B 可能扩缩容
  
问：A 怎么知道调哪个 IP？
```

## 2. 两种模式

### 客户端发现（Client-Side Discovery）

```
A: GET /users/123
   ↓
应用代码：service-discovery.getInstance("user-service")
   ↓ 返回 [10.0.1.5, 10.0.1.6, 10.0.1.7]
   ↓
客户端自己负载均衡（轮询 / 随机 / 一致性哈希）
```

代表：Eureka、Consul、Nacos、ZooKeeper
**缺点**：语言绑定、客户端复杂

### 服务端发现（Server-Side Discovery）

```
A: GET http://user-service/users/123
   ↓
Service Mesh（Envoy / Sidecar）
   ↓ 从注册中心拿 B 的实例 IP
   ↓ 负载均衡 + 转发
```

代表：Kubernetes Service + DNS、Consul Connect、Istio
**优点**：客户端无感，跨语言

## 3. K8s 服务发现（最常用）

### Service 类型

| 类型 | 用途 | 发现方式 |
|------|------|---------|
| ClusterIP | 集群内（默认） | DNS: my-svc.my-ns.svc.cluster.local |
| NodePort | 节点端口 | 任意 NodeIP:NodePort |
| LoadBalancer | 云 LB | 外部 IP |
| ExternalName | CNAME 别名 | DNS 别名 |
| Headless | 直接返 Pod IP | DNS 返 A 记录列表 |

### CoreDNS

```bash
# Pod 内 DNS 查询
nslookup user-service
# → Server: 10.96.0.10  (CoreDNS)
# → Address: 10.96.45.123 (ClusterIP)
```

查询规则：
- `my-svc` → 集群默认 namespace
- `my-svc.my-ns` → 指定 namespace
- `my-svc.my-ns.svc.cluster.local` → 完整 FQDN

### Service vs Pod

```
Service: 虚拟 IP（ClusterIP），负载均衡到 Pod
Pod: 真实 IP（每次重启变）
```

K8s 自动通过 label selector 关联：service.spec.selector → pod.metadata.labels

## 4. 实战：Spring Cloud + Nacos

```yaml
# application.yml
spring.cloud.nacos.discovery.server-addr: 192.168.1.1:8848
spring.cloud.nacos.discovery.namespace: dev
```

```java
// 启动时自动注册到 Nacos
@SpringBootApplication
@EnableDiscoveryClient
public class OrderService {
  public static void main(String[] args) {
    SpringApplication.run(OrderService.class, args);
  }
}
```

```java
// 调用：OpenFeign
@FeignClient(name = "user-service")
public interface UserClient {
  @GetMapping("/users/{id}")
  User getUser(@PathVariable Long id);
}

// 负载均衡（ribbon 自动）
@Autowired
UserClient userClient;
```

## 5. 注册中心对比

| 系统 | 特点 |
|------|------|
| **Nacos** | CP/AP 双模，配置中心，国内最常用 |
| **Eureka** | AP，Spring Cloud 生态，2.x 已闭源 |
| **Consul** | CP，Gossip 协议，多数据中心 |
| **ZooKeeper** | CP，老牌，etcd 是其精神继任者 |
| **etcd** | CP，K8s 内置，强一致 |

**推荐**：Nacos（功能全面） / Consul（多数据中心）。

## 6. 客户端缓存

```
问题：每次调用都查注册中心 = 慢 + 压垮注册中心
解决：本地缓存 + 异步刷新
```

```java
// Ribbon / Spring Cloud LoadBalancer 自带本地缓存
// 30s 刷新一次
```

## 7. 健康检查

注册中心需要知道实例健康状态：
- **心跳**：实例定期向注册中心发心跳（默认 5s）
- **超时剔除**：30s 没心跳 = 不可用
- **主动探测**：注册中心主动 HTTP / TCP 探活

## 8. 多集群服务发现

```
Cluster A (us-east) ←→  Cluster B (us-west)
        ↑                      ↑
   跨集群注册中心（Consul Federation / Nacos Cluster）
```

**坑**：跨集群调用延迟大，慎用。

## 9. 实战选型

| 场景 | 选 |
|------|-----|
| K8s 单集群 | CoreDNS（内置）|
| K8s 多语言微服务 | Nacos / Consul |
| 多数据中心 | Consul Federation |
| 老 Spring Cloud | Eureka / Nacos |
| Service Mesh | Service Mesh（应用无侵入）|

## 🔗 下一步
- [API 网关](/06-microservice/gateway)
- [配置中心](/06-microservice/config)
- [Service Mesh](/12-microservice-patterns/service-mesh)
