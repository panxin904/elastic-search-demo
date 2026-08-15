---
title: Java async-profiler
description: Java 生产级低开销 profiler
---

# Java async-profiler

> **TL;DR**：**async-profiler = Java 生产级低开销 profiler（基于 asyncGetCallTrace）**。**比 perf + HotSpot 调试更稳定**，**支持 CPU / Wall clock / Allocation / Lock**。**输出 HTML / Flame Graph + JFR 格式**。**生产标配：JVM 启动参数 + 定时收集 + 告警驱动**。

## 一句话定义

```
async-profiler = async-profiler 项目（JVM 内部 profiler）
              = 2016 起源，基于 HotSpot asyncGetCallTrace API
              = 低开销（< 1% CPU）
              = 支持 4 种事件：cpu / wall / alloc / lock
              = 输出火焰图 / JFR / 文本
```

## 安装与启动

```bash
# 1. 下载 async-profiler
curl -L -o async-profiler.jar   https://github.com/async-profiler/async-profiler/releases/latest/download/async-profiler.jar
# 同时下载 native lib（async-profiler-2.9-linux-x64.tar.gz）
tar xzf async-profiler-2.9-linux-x64.tar.gz

# 2. 启动 JVM 时 attach
java -jar app.jar &
APP_PID=$!

# 3. 启动 profiling（30 秒 CPU profile）
./profiler.sh -e cpu -d 30 -f /tmp/cpu.html $APP_PID
# 也可以启动时 attach：java -agentpath:./libasyncProfiler.so=start,event=cpu,flamegraph -jar app.jar
```

## 常用命令

```bash
# 1. CPU 火焰图（30 秒）
./profiler.sh -e cpu -d 30 -f /tmp/cpu.html <pid>

# 2. Wall clock（包含 IO 等待）
./profiler.sh -e wall -d 30 -f /tmp/wall.html <pid>

# 3. 内存分配字节
./profiler.sh -e alloc -d 30 -f /tmp/alloc.html <pid>

# 4. 内存分配对象数
./profiler.sh -e alloc -d 30 -o jfr -f /tmp/alloc.jfr <pid>

# 5. 锁竞争
./profiler.sh -e lock -d 30 -f /tmp/lock.html <pid>

# 6. JFR 格式（导入 JDK Mission Control 分析）
./profiler.sh -e cpu -d 30 -o jfr -f /tmp/cpu.jfr <pid>

# 7. 采样频率
./profiler.sh -e cpu -i 5ms -d 30 -f /tmp/cpu.html <pid>
# 5ms = 200Hz
```

## JVM 启动时附加

```bash
# 启动时注入 async-profiler agent（推荐生产）
java -agentpath:./libasyncProfiler.so=start,event=cpu,flamegraph,interval=10ms,log=./profiler.log      -jar app.jar

# 同时采集多种事件
java -agentpath:./libasyncProfiler.so=start,event=cpu,alloc,lock,flamegraph      -jar app.jar

# 启动后远程控制（通过 HTTP / JMX）
java -agentpath:./libasyncProfiler.so=start,event=cpu,flamegraph,server=8086      -jar app.jar
# 然后通过 HTTP API 控制：
curl http://localhost:8086/start?event=alloc
curl http://localhost:8086/stop
curl http://localhost:8086/threaddump
```

## 输出格式

```bash
# 1. HTML（内嵌 SVG 火焰图）
./profiler.sh -e cpu -d 30 -f cpu.html <pid>
# 浏览器打开 cpu.html

# 2. JFR（Java Flight Recorder）
./profiler.sh -e cpu -d 30 -o jfr -f cpu.jfr <pid>
# 用 JDK Mission Control / JMC Analyzer 打开

# 3. Tree 模式（文本）
./profiler.sh -e cpu -d 30 -o tree -f cpu.txt <pid>

# 4. Collapsed 模式（用于 FlameGraph 脚本）
./profiler.sh -e cpu -d 30 -o collapsed -f cpu.collapsed <pid>
./FlameGraph/flamegraph.pl --title "CPU Flame Graph" cpu.collapsed > cpu.svg
```

## 实战案例：定位 GC 频繁

```bash
# 1. 采集 alloc 事件（30 秒）
./profiler.sh -e alloc -d 30 -f alloc.html <pid>

# 2. 看火焰图
# 找最大块：通常是某个 byte[] / char[] 反复分配

# 3. 找具体代码
./profiler.sh -e alloc -d 30 -o tree -f alloc.txt <pid>
grep "allocate" alloc.txt | head -20
```

## 实战案例：定位锁竞争

```bash
# 1. 采集 lock 事件
./profiler.sh -e lock -d 30 -f lock.html <pid>

# 2. 看火焰图顶部
# 如果某个 Object.wait 或 synchronized 占大头 → 锁竞争严重

# 3. 实战解决：
#    - 用 ConcurrentHashMap 代替 Collections.synchronizedMap
#    - 用 ReentrantLock 代替 synchronized（更细粒度控制）
#    - 用 LongAdder 代替 AtomicLong（高并发写）
```

## 与 JFR 对比

| 维度 | async-profiler | JFR（Java Flight Recorder） |
|---|---|---|
| 开销 | 极低（< 1%） | 低（2-3%） |
| 火焰图 | ✓ 原生 | 需要转换 |
| JFR 格式 | ✓ | ✓ |
| 远程采集 | ✓ HTTP API | ✓ JMX |
| CPU event | ✓ | ✓ |
| Wall clock | ✓ | ✓ |
| Allocation | ✓ | ✓ |
| Lock | ✓ | ✓ |
| 推荐 | 生产首选 | JDK 自带 / JDK 17+ 已内置 |

## 一句话总结

> **async-profiler = Java 生产级 profiler**。**比 perf 稳定，比 JFR 灵活**。**火焰图一键生成**。**生产标配：JVM 启动 attach + 告警驱动 + 持续剖析**。

---

## 关联章节

- [持续剖析](./continuous-profiling.md) — Continuous Profiling
- [Pyroscope](./pyroscope.md) — 多语言平台
- [Go pprof](./pprof.md) — Go 等价工具
- [JVM 指标](../09-app-instrumentation/jvm-metrics.md) — JVM 运行时

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
