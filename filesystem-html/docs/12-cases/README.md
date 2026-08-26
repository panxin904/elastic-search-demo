# 12 · 企业案例

<span class="kg-badge kg-badge-cases">案例</span>

真实世界的大型存储架构演进。

## 章节目录

| 节点 | 一句话 |
|------|--------|
| [Netflix S3 架构](/12-cases/netflix-s3) | 每天 1.4 万亿次 S3 操作 |
| [ByteDance JuiceFS](/12-cases/juicefs-bytedance) | PB 级元数据 + 对象存储组合 |
| [CERN EOS 物理存储](/12-cases/cern-eos) | 对撞机数据：200 PB+ |
| [Snowflake 存储层](/12-cases/snowflake) | 计算存储分离的典范 |
| [Meta HDFS 演进](/12-cases/meta-hdfs) | 从 HDFS 到 Tectonic / Alchemy |

## 阅读建议

每个案例包含：
- **背景**：业务规模与挑战
- **架构**：核心组件与数据流
- **演进**：从 v1 到 vN 的关键决策
- **教训**：踩过的坑与最佳实践

这些案例不是"标准答案"，而是"特定约束下的最优解"——理解背后的**约束**比抄架构更重要。
## 🎯 本章学习路径

1. **了解场景**：每个协议都有它的设计目标（NFS = Unix 共享、SMB = Windows、FTP = 老系统）
2. **掌握配置**：端口 / 加密方式 / 性能调优
3. **安全加固**：防火墙规则 / TLS 配置 / 用户认证
4. **监控告警**：连接数 / 延迟 / 错误率

详细各协议配置见子节点文章。


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
