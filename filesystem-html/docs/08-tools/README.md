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