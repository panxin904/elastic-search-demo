---
title: GC 日志 / 调优
---
# GC 调优
- Goals: throughput >98%, pause <200ms, full GC rare
- Tuning: adjust Young/Old ratio, survivor ratio, promotion threshold
- G1: -XX:MaxGCPauseMillis=200, -XX:G1HeapRegionSize
- ZGC: almost no tuning needed, -Xms == -Xmx recommended
```bash
# GC Logging (JDK 9+)
-Xlog:gc*=info:file=gc.log:time,uptime,level,tags:filecount=10,filesize=100M
```