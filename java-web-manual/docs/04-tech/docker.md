---
title: Docker
---

# Docker

Docker 实现应用容器化，解决"在我机器上能跑"的问题。

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
