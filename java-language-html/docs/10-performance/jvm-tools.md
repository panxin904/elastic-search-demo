---
title: jstack / jmap / jstat
date: 2026-08-15  # date-auto-injected
---
# JDK 诊断工具
- jps -l: list Java processes
- jstack pid: thread dump, find deadlocks
- jmap -histo:live pid | head: top objects by count
- jmap -dump:live,file=dump.hprof pid: heap dump
- jstat -gc pid 1000 5: GC stats every 1s, 5 times
- jcmd pid GC.heap_dump /tmp/dump.hprof
- jinfo pid: JVM flags
```bash
jps -l
jstack 1234 > stack.txt
jmap -dump:live,file=heap.hprof 1234
jstat -gcutil 1234 1000 10
```