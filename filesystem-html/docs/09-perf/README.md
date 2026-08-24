# 09 · 性能调优

<span class="kg-badge kg-badge-perf">性能</span>

让文件系统跑得更快的核心方法论。

## 章节目录

| 节点 | 一句话 |
|------|--------|
| [IO 调度器选型](/09-perf/io-scheduler) | SSD vs HDD 的调度器差异 |
| [Page Cache 调优](/09-perf/page-cache-tune) | `vm.dirty_ratio` 等关键参数 |
| [fsync 语义与坑](/09-perf/fsync) | 为什么"明明 fsync 了还是丢数据" |
| [readahead 预读](/09-perf/readahead) | 顺序读加速 |
| [Direct I/O 旁路缓存](/09-perf/direct-io) | 数据库场景 |
| [性能分析方法论](/09-perf/methodology) | 从 iostat 到 bcc |

## 性能分析的金字塔

```
        应用层 perf / bcc
       ─────────────────
        内核层 trace / strace
       ─────────────────
        文件系统层 /proc/slabinfo
       ─────────────────
        块设备层 iostat / biosnoop
       ─────────────────
        硬件层 smartctl
```

**从上往下**：越底层越通用，越上层越具体。Always start from the top。
## 🎯 本章学习路径

1. **了解场景**：每个协议都有它的设计目标（NFS = Unix 共享、SMB = Windows、FTP = 老系统）
2. **掌握配置**：端口 / 加密方式 / 性能调优
3. **安全加固**：防火墙规则 / TLS 配置 / 用户认证
4. **监控告警**：连接数 / 延迟 / 错误率

详细各协议配置见子节点文章。
