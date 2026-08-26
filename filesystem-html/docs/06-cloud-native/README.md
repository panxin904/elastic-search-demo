# 06 · 云原生存储

<span class="kg-badge kg-badge-cloud-native">云原生</span>

Kubernetes 时代的存储抽象——CSI、PV/PVC、Operator。

## 章节目录

| 节点 | 一句话 |
|------|--------|
| [CSI 容器存储接口](/06-cloud-native/csi) | K8s 存储标准 |
| [PV / PVC / StorageClass](/06-cloud-native/pv-pvc) | 声明式存储三件套 |
| [动态配置 StorageClass](/06-cloud-native/dynamic) | 自动创建 PV |
| [Rook Ceph Operator](/06-cloud-native/rook) | 工业级 Ceph on K8s |
| [Longhorn 分布式块](/06-cloud-native/longhorn) | Rancher 出品，轻量块存储 |
| [OpenEBS 容器化存储](/06-cloud-native/openebs) | MayaData 出品 |
| [Volume Snapshot / Clone](/06-cloud-native/snapshot) | 数据保护 |

## 为什么需要 CSI

在 CSI 出现之前，存储插件必须编译进 kubelet 二进制，每次升级都要重新编译。CSI 把存储抽象成独立 Pod（driver），kubelet 通过 gRPC 与之通信，实现：

- ✅ 独立升级（不影响 K8s）
- ✅ 跨厂商统一接口
- ✅ 支持动态供给 / 快照 / 扩容


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
