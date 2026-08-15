---
title: 命令速查
---
# 📋 Java 命令速查

## 🔨 编译 / 运行
```bash
javac Main.java                 # 编译
java Main                       # 运行（.class 在同目录）
java -cp ".:lib/*" Main         # 带 classpath
java -jar app.jar               # 运行 fat jar
java --enable-preview Main      # 启用预览特性

javac -d out/ *.java            # 编译到 out/
javac -source 21 -target 21     # 指定版本
javac --release 21 Main.java    # Java 9+
```

## 📦 打包
```bash
jar cf app.jar -C out/ .        # 打包
jar tf app.jar                  # 看内容
war cf app.war -C out/ .        # 打包 war
```

## 🛠 Maven
```bash
mvn clean                       # 清
mvn compile                     # 编译
mvn test                        # 测试
mvn package -DskipTests         # 打包跳测试
mvn install                     # 装到本地仓库
mvn spring-boot:run             # 跑 Spring Boot
mvn dependency:tree             # 看依赖树
mvn versions:display-dependency-updates
```

## 🛠 Gradle
```bash
gradle build                    # 构建
gradle test                     # 测试
gradle bootRun                  # 跑 Spring Boot
gradle dependencies             # 看依赖
```

## ⚙️ JVM 诊断
```bash
jps -l                          # 列 Java 进程
jstack <pid>                    # 线程堆栈
jstack <pid> > stack.txt        # 导出
jmap -heap <pid>                # 堆概要
jmap -histo:live <pid> | head   # 对象直方图
jmap -dump:live,file=dump.hprof <pid>  # heap dump
jstat -gc <pid> 1000            # GC 统计 1s
jstat -gcutil <pid> 1000        # GC 百分比
jinfo <pid>                     # JVM 参数
jcmd <pid> GC.heap_dump dump.hprof
jcmd <pid> VM.flags              # 看 JVM flags
jcmd <pid> Thread.print          # 同 jstack
```

## 🔥 Arthas
```bash
curl -O https://arthas.aliyun.com/arthas-boot.jar
java -jar arthas-boot.jar       # 选择 PID
dashboard                        # 实时面板
thread                          # 线程
thread -n 3                     # top 3 CPU 线程
thread -b                       # 找死锁
jad com.example.MyClass          # 反编译
watch com.example.MyClass method # 观察调用
trace com.example.MyClass method # 追踪耗时
monitor -c 5 com.example.MyClass method  # 监控
```

## 🧪 JUnit5
```bash
mvn test -Dtest=MyClassTest      # 单测
mvn test -Dtest="*Integration"   # 通配
gradle test --tests "MyClassTest"
```

## 🏗 Spring Boot
```bash
java -jar app.jar --server.port=8080      # 改端口
java -jar app.jar --spring.profiles.active=prod
java -jar app.jar --debug                 # 远程 debug
java -Dlogging.level.root=DEBUG -jar app.jar

# Actuator
curl http://localhost:8080/actuator/health
curl http://localhost:8080/actuator/metrics
```

## 🔐 keytool
```bash
keytool -genkey -alias mykey -keystore keystore.jks
keytool -list -keystore keystore.jks
keytool -import -alias cert -file cert.cer -keystore trust.jks
```

## 🔗 下一步
- [OOP 类与对象](/01-basics/oop)
- [Arthas 诊断](/10-performance/arthas)
- [JVM 调优参数](/10-performance/jvm-tuning)