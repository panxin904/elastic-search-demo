---
title: G1 / ZGC / Shenandoah
date: 2026-08-15  # date-auto-injected
---
# 垃圾收集器
| Collector | Young | Old | Pause | Target |
|-----------|-------|-----|-------|--------|
| Serial | Serial | Serial Old | long | single CPU |
| Parallel | Parallel Scavenge | Parallel Old | medium | throughput |
| CMS | ParNew | CMS | short | low pause |
| **G1** | G1 | G1 (region) | configurable (-XX:MaxGCPauseMillis) | balanced |
| **ZGC** | ZGC | ZGC | <1ms (Java 17+) | ultra-low pause |
| **Shenandoah** | Shenandoah | Shenandoah | <10ms | low pause |
```bash
# Select GC
-XX:+UseG1GC            # JDK 9+ default
-XX:+UseZGC             # JDK 15+ production
-XX:+UseShenandoahGC    # JDK 15+ production
```