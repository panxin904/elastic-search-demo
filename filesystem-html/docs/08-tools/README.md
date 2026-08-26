# 08 · 文件工具集

<span class="kg-badge kg-badge-tools">工具</span>

日常必备的文件操作、调试、监控工具。

## 章节目录

| 节点 | 一句话 |
|------|--------|
| [FUSE 用户态 FS](/08-tools/fuse) | 让用户态程序实现文件系统 |
| [debugfs 调试工具](/08-tools/debugfs) | ext 系列底层调试器 |
| [rsync 同步备份](/11-backup/snapshot) | 增量同步之王 |
| [find / fd / ripgrep](/08-tools/find-fd) | 现代文件查找三剑客 |
| [inotify / fanotify](/08-tools/inotify) | 文件系统事件监控 |
| [du / df / ncdu](/08-tools/du-df) | 磁盘空间分析 |
| [lsof / fuser](/08-tools/lsof) | 谁在用这个文件 |

## 工具选型速查

| 需求 | 推荐 |
|------|------|
| 查找文件（快） | `fd` |
| 查找文件（标准） | `find` |
| 内容搜索（快） | `ripgrep` (rg) |
| 内容搜索（标准） | `grep -r` |
| 同步目录 | `rsync -a` |
| 监控文件变化 | `inotifywait` |
| 谁占了文件 | `lsof` |
| 空间占用 | `ncdu` |
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
