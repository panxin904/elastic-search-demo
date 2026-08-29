---
title: 对象创建 / OOM
date: 2026-08-15  # date-auto-injected
---
# OOM 排查
- java.lang.OutOfMemoryError: Java heap space → -Xmx too small / memory leak
- OOM: GC overhead limit → GC spends >98% time reclaiming <2% heap
- OOM: Metaspace → too many classes loaded
- OOM: Direct buffer memory → direct ByteBuffer
- Analyze heap dump: jmap -dump, MAT (Eclipse Memory Analyzer), JProfiler
```bash
-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/dump.hprof
```