# 01 · 文件系统基础

<span class="kg-badge kg-badge-basics">基础</span>

理解"打开一个文件背后发生了什么"——这是掌握所有存储技术的起点。

## 章节目录

| 节点 | 一句话 |
|------|--------|
| [inode 与 dentry](/01-basics/inode-dentry) | 文件的"身份证"——文件名背后的元数据 |
| [VFS 虚拟文件系统](/01-basics/vfs) | Linux 用一层抽象统一所有 FS |
| [文件描述符](/01-basics/file-descriptor) | open/read/write 的核心数据结构 |
| [Page Cache 页缓存](/01-basics/page-cache) | 让"读过的内容再次读"变快的秘密 |
| [挂载 mount](/01-basics/mount) | FS 如何接入目录树 |
| [日志 journal](/01-basics/journal) | 断电后如何保证数据一致性 |
| [路径解析](/01-basics/path-resolution) | `/a/b/c` 是怎么找到 c 的 |

## 学习建议

本章是后续所有内容的基石。如果第一次接触 Linux FS，建议按顺序读完；如果已熟悉可重点复习 inode / Page Cache 这两个高频考点。