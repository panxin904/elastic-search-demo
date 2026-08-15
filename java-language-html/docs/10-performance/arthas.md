---
title: Arthas 诊断
---
# Arthas
- dashboard: real-time CPU/memory/GC (like htop for JVM)
- thread -n 3: top 3 CPU threads
- thread -b: find deadlock
- watch: observe method invocation args, return, exception
- trace: method call tree with timing
- monitor -c 5: method call stats every 5 seconds
- ognl: evaluate expression (ognl '@System@getProperty("user.dir")')
```bash
curl -O https://arthas.aliyun.com/arthas-boot.jar
java -jar arthas-boot.jar
# dashboard
# thread -n 3
# watch com.example.UserService findById '{params, returnObj}'
```