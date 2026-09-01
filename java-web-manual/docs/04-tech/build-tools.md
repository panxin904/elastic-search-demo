---
title: 构建工具 Maven/Gradle
date: 2026-08-15  # date-auto-injected
---

# Maven / Gradle

构建工具管理项目的依赖、编译、测试、打包、发布全生命周期。

## Maven 核心概念

| 概念 | 说明 |
|---|---|
| GAV 坐标 | groupId:artifactId:version，唯一标识一个依赖 |
| 生命周期 | clean(清理) → compile(编译) → test(测试) → package(打包) → install(安装) → deploy(发布) |
| 依赖管理 | 传递依赖、依赖排除、版本仲裁（最短路径/最先声明） |
| 多模块 | parent pom 统一管理子模块 |

## pom.xml 配置

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.0</version>
</parent>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-boot-starter</artifactId>
        <version>3.5.5</version>
    </dependency>
</dependencies>
```

## 多模块项目

```
parent-project/
├── pom.xml              # 父 POM（依赖管理 + 模块声明）
├── common/              # 公共模块
├── service-a/           # 业务模块 A
└── service-b/           # 业务模块 B
```

```xml
<!-- 父 POM -->
<modules>
    <module>common</module>
    <module>service-a</module>
    <module>service-b</module>
</modules>
```

## Maven vs Gradle

| | Maven | Gradle |
|---|---|---|
| 配置文件 | pom.xml (XML) | build.gradle (Groovy/Kotlin) |
| 构建速度 | 一般 | 快（增量编译、缓存） |
| 灵活性 | 约定优于配置，较死板 | 高度可定制 |
| 学习曲线 | 平缓 | 稍陡 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="build-tools" :height="400" />
