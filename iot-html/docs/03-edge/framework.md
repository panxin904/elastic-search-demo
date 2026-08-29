---
title: EdgeX / KubeEdge
date: 2026-08-27  # date-auto-injected
---

# EdgeX / KubeEdge

> 边缘计算框架，统一设备接入 + 数据处理 + 云边协同。

## 🎯 核心要点

- EdgeX Foundry：Linux 基金会项目，模块化（Core/Supporting/Application Service）
- KubeEdge：Kubernetes 原生，边缘节点管理 + 离线自治
- Azure IoT Edge：微软云生态，容器化部署
- AWS Greengrass：AWS IoT 边缘运行时

## 🛠️ 实战示例

```bash
# KubeEdge 边缘节点加入集群
kubectl apply -f edge-node.yaml
# 边缘节点本地运行 Pod，云端 API 失联仍可工作
```

## 🔗 相关链接

- [K8s 边缘](./k8s-edge)
- [设备影子](../04-management/shadow)
- [← 返回 边缘计算 目录](./)
- [← 返回 iot 首页](../)
## 🎯 选型

- **EdgeX Foundry**：Linux 基金会，模块化设计
- **KubeEdge**：K8s 原生，云边协同
- **Azure IoT Edge**：微软云生态
- **AWS Greengrass**：AWS IoT 生态
**部署**：Helm chart 简化 K8s 边缘部署
**部署**：EdgeX 用 Docker Compose / KubeEdge 用 Helm。

- **云中立**：EdgeX 是云中立框架，可对接任意云。


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
