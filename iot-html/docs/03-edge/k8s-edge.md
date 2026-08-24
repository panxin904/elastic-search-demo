---
title: K8s 边缘
---

# K8s 边缘

> K3s / KubeEdge / OpenYurt 三种 K8s 边缘方案对比与选型。

## 🎯 核心要点

- K3s：轻量级 K8s（单 binary < 100MB），适合边缘网关
- KubeEdge：完整 K8s 边缘管理，云边协同 + 离线自治
- OpenYurt：阿里云开源，原生 K8s + 边缘单元化
- 选型：单边缘节点 → K3s；多节点协同 → KubeEdge / OpenYurt

## 🛠️ 实战示例

```bash
# K3s 单命令安装
curl -sfL https://get.k3s.io | sh -
# 启动后直接 kubectl get nodes 可用
```

## 🔗 相关链接

- [EdgeX](./framework)
- [网关硬件](../02-device/gateway)
- [← 返回 边缘计算 目录](./)
- [← 返回 iot 首页](../)
## 🎯 K8s 边缘方案对比

- **K3s**：单 binary < 100MB，适合单节点
- **KubeEdge**：完整云边协同，多节点
- **OpenYurt**：阿里云开源，原生 K8s + 边缘单元化
**网络**：边缘节点常网络受限，需优化控制面流量
**部署**：k3s 单 binary < 100MB，适合边缘资源受限场景。

- **小贴士**：K3s 单节点够用就上 K3s，省资源。
