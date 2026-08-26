---
title: 03 · 边缘计算
---

# 03 · 边缘计算

云边协同 + 离线自治 + 边缘智能。

## 章节目录

| 节点 | 一句话 |
|------|--------|
| [EdgeX / KubeEdge](./framework) | 边缘计算框架 |
| [边缘智能 AI](./ai-edge) | TensorFlow Lite / ONNX / OpenVINO |
| [离线自治](./offline) | 本地缓存 + 协议转换 |
| [K8s 边缘](./k8s-edge) | K3s / KubeEdge / OpenYurt |

## 选型决策

- 单边缘节点：K3s
- 多节点协同：KubeEdge / OpenYurt
- 纯框架：EdgeX Foundry
- AI 推理：TF Lite / ONNX Runtime
## 🎯 云边协同模式

- **数据上行**：边缘 → 云（聚合 / 过滤 / 压缩）
- **控制下行**：云 → 边缘（配置 / 命令 / 模型更新）
- **离线自治**：网络断时边缘独立工作，恢复后增量同步

**关键指标**：自治时长 / 网络恢复同步时间 / 边缘节点数。
**安全**：边缘节点物理暴露，硬件安全更重要
**架构**：云边端三层（云端训练 / 边缘推理 / 端侧采集）。


<!-- auto-enrich:do-not-edit -->

## 实战示例

\`\`\`bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
\`\`\`

\`\`\`yaml
# TODO: 配置示例
key: value
\`\`\`

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
