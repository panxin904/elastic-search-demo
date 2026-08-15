---
title: 网络 / DNS 排错
---

# 网络 / DNS 排错

> k8s 网络 80% 问题 = DNS / iptables / CNI / Service 配错。

## 🤔 为什么网络问题多

```
k8s 网络栈：
  1. Pod IP 分配（CNI）
  2. Service ClusterIP（kube-proxy）
  3. DNS 解析（CoreDNS / kube-dns）
  4. Ingress 七层（nginx / traefik）
  5. NetworkPolicy（防火墙）

任一环节错 = 连不通
```

## 🔧 第一步：定义"连不通"

```bash
# 1. 同 Pod 内的容器能互相访问？
# 2. 同 namespace 不同 Pod 能互相访问？
# 3. 跨 namespace 能访问？
# 4. Pod 能访问 Service ClusterIP？
# 5. Pod 能访问外网？
# 6. 外部能通过 Ingress / LoadBalancer 访问？
```

先缩小范围。

## 🌐 DNS 排查

```bash
# 从 Pod 内部
kubectl exec -it <pod> -- nslookup kubernetes

# 期望解析到 ClusterIP
# Server:    10.96.0.10
# Name:      kubernetes.default.svc.cluster.local
# Address:  10.96.0.1

# 同 namespace 短名
nslookup kube-dns
# Service 短名（pod-name → service-name）
# 同 ns：service-name
# 跨 ns：service-name.namespace.svc.cluster.local

# CoreDNS 状态
kubectl -n kube-system get pods -l k8s-app=kube-dns
kubectl -n kube-system logs -l k8s-app=kube-dns

# resolv.conf
kubectl exec <pod> -- cat /etc/resolv.conf
# 应该是 kube-dns Service IP
```

### DNS 常见错

```bash
# 服务短名不通
nslookup myapp
# 解决：full 域名
nslookup myapp.default.svc.cluster.local

# Pod 没配 DNS（自定义镜像）
cat /etc/resolv.conf
# 应有 ndots:5

# CoreDNS 挂
kubectl -n kube-system logs -l k8s-app=kube-dns
# 重启
kubectl -n kube-system rollout restart deployment coredns
```

## 🔌 Service / Endpoints

```bash
# 看 Service
kubectl get svc myapp
# NAME    TYPE        CLUSTER-IP    EXTERNAL-IP   PORT(S)   AGE
# myapp   ClusterIP   10.96.100.50  <none>        80/TCP    10m

# Endpoints（背后 Pod 列表）
kubectl get endpoints myapp
# NAME    ENDPOINTS                            AGE
# myapp   10.244.1.5:8080,10.244.1.6:8080      10m
# 空 → selector 错 / Pod 标签错 / Pod not Ready

# describe
kubectl describe svc myapp
kubectl describe endpoints myapp
# 找 "Endpoints:" 段
```

### Service 不通的常见原因

```bash
# 1. Endpoints 为空
kubectl get endpoints myapp
# → 检查 Pod labels 匹配 svc.spec.selector
# → Pod 不在 Running 状态

# 2. Port 配错
# Service port: 80
# targetPort: 8080  ← 容器实际监听这个

# 3. readinessProbe 不过
kubectl get pods -l app=myapp
# STATUS 应该是 Running 且 READY 1/1
# 否则 service 不会把流量给它
```

## 🌐 Pod 内部探网络

```bash
# 装 netshoot
kubectl run -it --rm --image=nicolaka/netshoot --restart=Never netshoot -- bash

# 或用 debug
kubectl debug -it <pod> --image=nicolaka/netshoot -- bash

# 在容器内：
ping 8.8.8.8
curl http://my-service:80
nc -zv my-service 80
ss -tlnp
traceroute 8.8.8.8
```

## 🛡 NetworkPolicy 排查

```bash
# 看是否启用了 NP
kubectl get networkpolicy -A

# 看 Pod 实际能不能连
kubectl run test --rm -it --image=alpine --restart=Never -- sh
# 进 Pod 内 nc -zv target:port
```

**关键**：NP 是白名单模式，**没列出的全拒绝**。

```yaml
# 默认拒绝一切
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: prod
spec:
  podSelector: {}
  policyTypes: [IngressPolicy, EgressPolicy]
  # 不写任何规则
```

**必须**有"放行 DNS + 同 ns 通信"的规则，否则全阻断。

## 🛣 Service 内部网络

```bash
# ClusterIP 走 iptables / IPVS
iptables-save | grep my-service
# 大量 DNAT / load-balance 规则

# IPVS
ipvsadm -ln
```

## 🚪 Ingress 排查

```bash
# 1. Ingress Controller 起来了吗
kubectl get pods -n ingress-nginx
# 或 -n traefik / istio-system

# 2. Ingress 资源
kubectl get ing
kubectl describe ing my-app
# Events 显示 sync 失败

# 3. Service backend 健康
kubectl get endpoints my-app
# 应有 IP

# 4. 从集群外到 Ingress
curl -v https://app.example.com

# 5. 从集群内
kubectl run curl --rm -it --image=alpine --restart=Never -- \
  curl -v http://my-app.default.svc.cluster.local
```

## 🩹 CNI 故障

```bash
# 节点 ping 不通
# 看 CNI
kubectl -n kube-system get pods -l k8s-app=calico-node
# 或
kubectl -n kube-system get pods -l k8s-app=cilium

# 看 Node CNI 日志
journalctl -u kubelet -f
# 通常：network not ready / cni plugin not found

# 重启 CNI
systemctl restart kubelet
```

## ⚡ 性能 / 连接数

```bash
# 看 conntrack
sysctl net.netfilter.nf_conntrack_max
sysctl net.netfilter.nf_conntrack_count

# 改大
sysctl -w net.netfilter.nf_conntrack_max=262144

# 看 socket
ss -s

# 节点 TIME_WAIT
ss -tan | grep TIME-WAIT | wc -l
# 多 → net.ipv4.tcp_tw_reuse=1 / tcp_max_tw_buckets 调大
```

## 🩺 实战：Service 不通

```bash
# 1. Endpoints 存在？
kubectl get endpoints myapp
# 空 → 后端 Pod 不对
# 1a. Pod 在 Running 且 Ready？
kubectl get pods -l app=myapp
# 1b. Pod 标签匹配 Service selector？
kubectl get pods -l app=myapp -o jsonpath='{.items[*].metadata.labels}'
kubectl get svc myapp -o jsonpath='{.spec.selector}'

# 2. 进 Pod
kubectl debug -it myapp-xxx --image=nicolaka/netshoot
# 看 /etc/resolv.conf
# dig my-service
# curl http://my-service:80

# 3. 看 NP
kubectl get networkpolicy -A

# 4. 看 CNI
# 节点上
ip route
ip link
```

## 🩺 实战：Ingress 502

```bash
# 502 = 后端不通
kubectl describe ing my-app
# Events: sync 失败

# 1. Ingress Controller 日志
kubectl -n ingress-nginx logs deploy/ingress-nginx-controller --tail 100

# 2. 后端 Service
kubectl get svc my-app
kubectl get endpoints my-app
# 0 endpoints → Pod 没 ready

# 3. Pod 健康
kubectl get pods -l app=my-app
# 应该是 Running 1/1
```

## 🔗 下一步

- [kubectl debug](/13-troubleshooting/debug)
- [Pod 卡死 / 排错套路](/13-troubleshooting/pod-trouble)
- [NetworkPolicy](/04-k8s-service/network-policy)