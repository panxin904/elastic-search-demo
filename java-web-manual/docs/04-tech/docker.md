---
title: Docker
date: 2026-08-15  # date-auto-injected
---

# Docker

Docker 实现应用容器化，解决"在我机器上能跑"的问题。

## 🛠️ Docker 实战要点

**多阶段构建**：减少镜像体积（builder stage + runtime stage），最终镜像只含运行时依赖。

**Dockerfile 最佳实践**：
- 基础镜像用 `eclipse-temurin:17-jre-alpine`（小、含 JRE）
- 容器跑应用用非 root 用户（`USER appuser`）
- .dockerignore 排除 target/、.git/、node_modules/ 等
- 健康检查用 `HEALTHCHECK`（不是业务自己探活）

**Docker Compose vs K8s**：本地开发用 Compose（简单），生产用 K8s（编排 / 自愈 / 扩缩容）。

## 核心概念

| 概念 | 说明 |
|---|---|
| 镜像 Image | 应用的只读模板 |
| 容器 Container | 镜像的运行实例 |
| Dockerfile | 镜像构建脚本 |
| docker-compose | 多容器编排 |

## Dockerfile

```dockerfile
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/app.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "-Dspring.profiles.active=${PROFILE}", "app.jar"]
```

## docker-compose

```yaml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root123
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      PROFILE: dev
    depends_on:
      - mysql
      - redis

volumes:
  mysql_data:
```

## 常用命令

```bash
docker build -t my-app:1.0 .           # 构建镜像
docker run -d -p 8080:8080 my-app:1.0  # 运行容器
docker-compose up -d                    # 启动所有服务
docker logs -f <container>              # 查看日志
docker exec -it <container> bash        # 进入容器
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="docker" :height="400" />
