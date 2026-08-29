---
title: Maven / Gradle
date: 2026-08-15  # date-auto-injected
---
# Maven / Gradle
- Maven lifecycle: validate → compile → test → package → verify → install → deploy
- Dependency scope: compile (default), provided, runtime, test, system, import
- Gradle: Groovy/Kotlin DSL, incremental build, build cache
```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```
```groovy
dependencies {
  implementation 'org.springframework.boot:spring-boot-starter-web'
  testImplementation 'org.springframework.boot:spring-boot-starter-test'
}
```