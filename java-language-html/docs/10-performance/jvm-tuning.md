---
title: JVM 调优参数
---
# JVM 调优
- -Xms512m -Xmx2g (heap), -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=256m
- GC: -XX:+UseG1GC -XX:MaxGCPauseMillis=200
- Dump: -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/dump.hprof
- Thread stack: -Xss256k (default ~1MB, reduce for microservices)
```bash
java -Xms1g -Xmx2g -XX:+UseZGC -XX:+HeapDumpOnOutOfMemoryError -jar app.jar
```