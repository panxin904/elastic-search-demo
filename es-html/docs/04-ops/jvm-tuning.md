---
title: JVM 调优
category: ops
graphNodeId: jvm-tuning
---

<span class="kg-badge kg-badge-ops">运维层</span>

# JVM 调优

ES 是 Java 应用，**JVM 调优**直接影响性能与稳定性。

## 📏 堆内存 (Heap)

### 推荐设置

```bash
# jvm.options
-Xms16g    # 初始堆
-Xmx16g    # 最大堆（必须与 Xms 相同）
```

| 维度 | 建议 |
|---|---|
| 最大堆 | **≤ 32 GB**（超出会失去 CompressedOops 优化） |
| Xms = Xmx | **必须相等**，避免运行时扩容 |
| 物理内存比例 | 堆 ≤ 物理内存的 **50%**（剩余给 file system cache） |

## 🗑️ 垃圾回收 (GC)

ES 7.x 默认使用 **G1GC**（G1 Garbage Collector），对大堆友好。

```bash
-XX:+UseG1GC
-XX:MaxGCPauseMillis=200
-XX:G1HeapRegionSize=16m
```

| GC 模式 | 适用 |
|---|---|
| G1GC（默认） | **生产推荐** |
| CMS | 已废弃，仅 ES 6 旧集群 |

## 📊 监控 GC

```bash
GET /_nodes/stats/jvm
```

返回关键指标：
```json
{
  "jvm": {
    "mem": {
      "heap_used_percent": 45
    },
    "gc": {
      "collectors": {
        "young": { "collection_time_millis": 120, "collection_count": 100 },
        "old":   { "collection_time_millis": 50,  "collection_count": 5 }
      }
    }
  }
}
```

| 指标 | 警戒值 |
|---|---|
| `heap_used_percent` | > 75% 警告，> 85% 严重 |
| `old.gc.collection_time_millis` | 频繁 Full GC 需调优 |
| GC 总耗时占比 | < 10% 正常 |

## 📁 文件描述符与线程

```yaml
# elasticsearch.yml
bootstrap:
  memory_lock: true        # 锁定堆内存（需 ulimit 配置）
  system_call_filter: true
```

```bash
# /etc/security/limits.conf
esuser  -  nofile  65536
esuser  -  nproc   4096
```

## ⚙️ Swap 必须关闭

```bash
sudo swapoff -a
# 永久：/etc/fstab 中注释掉 swap 行
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="jvm-tuning" :height="400" />

## 📚 延伸阅读
- [安装部署](/04-ops/installation)
- [集群健康](/04-ops/cluster-health)
- [监控 Cerebro](/04-ops/monitoring)
