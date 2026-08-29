---
title: 常用命令速查
date: 2026-08-15  # date-auto-injected
---
# Java 常用命令
```bash
javac --release 21 Main.java && java Main
javap -c -v Main.class
jar cf app.jar -C out/ .
java -jar app.jar
jpackage --input target/ --name MyApp --main-jar app.jar --main-class com.example.Main
native-image -jar app.jar  # GraalVM
```