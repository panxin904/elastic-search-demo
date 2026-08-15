---
title: kubectl debug
---

# kubectl debug

> k8s 1.30+ 内置的 `kubectl debug` —— **不重启 / 不改镜像**就能进容器内部排查。

## 🤔 为什么需要

```
❌ 经典进容器：kubectl exec -it pod -- bash
   但容器：
   - 镜像没 bash（alpine / distroless）
   - 没你想用的工具（curl / tcpdump / strace）
   - 已崩了（CrashLoopBackOff），exec 不进去

✅ kubectl debug：
   - 注入新容器（带工具的镜像）共享 Pod 网络 / 卷
   - 原容器不动
   - 还能给"卡死"容器附加进程
```

## 🚀 基础

```bash
# 默认：注入一个调试容器（默认镜像：registry.k8s.io/e2e-test-images/jessie-dnsutils:1.5）
kubectl debug -it pod-name --image=busybox

# 指定调试镜像
kubectl debug -it pod-name --image=nicolaka/netshoot -- bash

# 共享目标 Pod 的 namespace（必须）
kubectl debug -it pod-name -n prod --image=busybox

# 容器名（避免和业务容器重名）
kubectl debug -it pod-name --image=busybox --container=debugger
```

## 🎯 三种模式

### 1. 同 Pod 注入新容器（默认）

```bash
kubectl debug -it pod-name --image=busybox -- bash
# 在新容器里：
ls /proc/1/root              # 能看到原容器的文件系统
cat /proc/1/root/etc/nginx/nginx.conf
```

适合：镜像没工具 / 想看原容器 FS。

### 2. 共享进程命名空间

```bash
kubectl debug -it pod-name --image=busybox --target=<container>
# 在新容器里：ps aux 能看到原容器的所有进程
```

适合：原容器**未崩溃**，但你想看它跑什么。

### 3. 附加到崩溃容器

```bash
# 原容器已死 / exec 不进去
kubectl debug -it pod-name --image=busybox --fork-pod=true
# 新建一个 copy 容器副本，attach 进去
```

适合：CrashLoopBackOff 排查。

## 🔧 高级

### 复制文件出

```bash
# 看原容器文件
kubectl debug pod-name --image=busybox --target=web -- \
  cat /etc/nginx/conf.d/default.conf > default.conf
```

### 网络排查

```bash
kubectl debug pod-name --image=nicolaka/netshoot -- bash
# netshoot 包含：curl / wget / dig / nslookup / tcpdump / ss / netstat

# DNS 解析
nslookup kubernetes.default

# TCP 探测
nc -zv service.namespace 80

# 抓包（需 NET_ADMIN / NET_RAW）
tcpdump -i any -w /tmp/cap.pcap port 80
```

### 看进程

```bash
kubectl debug pod-name --image=busybox --target=web -- ps aux
# 看原容器进程

# 找 PID 1 资源
ls -la /proc/1/cwd
cat /proc/1/cmdline | tr '\0' ' '
```

## 🔧 与 krew 插件（更多功能）

```bash
# 装 krew
kubectl krew install debug
kubectl krew install node-shell   # 直接进 Node 主机
kubectl krew install snode         # 同上

# 装 nicolaka/netshoot（瑞士军刀）
kubectl krew install netshoot
kubectl netshoot pod-name
```

## 🛠 实战

### CrashLoopBackOff 排查

```bash
# 1. 看 Pod 错在哪
kubectl describe pod myapp-xxx
# Events: BackOff restarting failed container

# 2. 看上一个实例的日志（崩了的实例）
kubectl logs myapp-xxx --previous

# 3. 创建 debug 副本
kubectl debug -it myapp-xxx --image=nicolaka/netshoot --fork-pod=true
# 看到实例的 FS
cat /etc/myapp/config.yaml
```

### 网络不通

```bash
# 从 Pod 内探
kubectl debug -it myapp-xxx --image=nicolaka/netshoot -- bash

# DNS
nslookup db
nslookup db.default.svc.cluster.local

# 连通
nc -zv db 5432
curl http://api:8080/health

# 抓包
tcpdump -i eth0 -w /tmp/cap.pcap
```

### 容器镜像没工具

```bash
# distroless 没 shell
kubectl exec -it myapp-xxx -- sh
# rpc error: code = 2 ... no such file

# 用 debug
kubectl debug -it myapp-xxx --image=alpine --target=web
# 进新容器 / 原容器的 FS 在 /proc/1/root
ls /proc/1/root/usr/local/bin/
```

## 🩹 故障

```bash
# 1.20 之前版本可能没有 kubectl debug
# 升级 / 改用 krew 插件

# ImagePullBackOff
kubectl debug pod-name --image=busybox
# 看 events
kubectl describe pod pod-name | grep -A 5 Events

# 调试容器装不了（namespace 禁）
# 解决：找 kube-system 跑
```

## 🔗 下一步

- [Pod 卡死 / 排错套路](/13-troubleshooting/pod-trouble)
- [网络 / DNS 排错](/13-troubleshooting/network)