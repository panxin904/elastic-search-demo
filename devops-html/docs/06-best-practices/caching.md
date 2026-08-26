---
title: CI 缓存策略
---

# CI 缓存策略

缓存是 Pipeline 优化的"第一性原理"——同样的输入，不应该重复劳动。本章梳理跨工具的缓存策略。

## 一句话总结

> **CI 缓存 = 时间换时间**。**核心：依赖缓存 + 构建缓存 + 测试结果缓存**。**目标：cache hit rate > 85%、duration 降低 50%+**。

---

## 缓存类型矩阵

| 缓存类型 | 内容 | 命中率目标 |
|----------|------|------------|
| **依赖缓存** | npm / pip / go mod / cargo | > 95% |
| **构建缓存** | Docker layer / Bazel / Turborepo | > 80% |
| **测试结果缓存** | 单元测试 / lint | > 70% |
| **源码缓存** | git clone（去 shallow） | > 99% |

## GitHub Actions 缓存

```yaml
# 1. 依赖缓存（最常用）
- uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      node_modules
    key: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-deps-

# 2. 构建缓存
- uses: actions/cache@v4
  with:
    path: |
      dist
      .next
      target
    key: ${{ runner.os }}-build-${{ hashFiles('**/src/**') }}
```

## Docker BuildKit 缓存

```dockerfile
# Dockerfile（mount cache）
# syntax=docker/dockerfile:1.6
FROM node:20-alpine
WORKDIR /app

# 缓存 npm registry
RUN --mount=type=cache,target=/root/.npm \
    --mount=type=bind,source=package-lock.json,target=package-lock.json \
    npm ci

COPY . .
RUN --mount=type=cache,target=/app/.next/cache \
    npm run build
```

```yaml
# GitHub Actions Docker Build
- uses: docker/build-push-action@v5
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Turborepo（Monorepo 缓存）

```json
// turbo.json
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "test": {
      "dependsOn": ["build"],
      "outputs": ["coverage/**"]
    }
  }
}
```

```yaml
# GitHub Actions
- uses: actions/cache@v4
  with:
    path: .turbo
    key: ${{ runner.os }}-turbo-${{ hashFiles('**/turbo.json', '**/*.tsx') }}
```

## Bazel（极致缓存）

```bash
# Bazel remote cache
.bazelrc
build --remote_cache=https://bazel-cache.example.com
build --remote_upload_local_results=true

# 命中缓存的 build：秒级
bazel build //...
# 第一次 build：可能 10 分钟
# 第二次 build：< 30 秒（缓存命中）
```

## GitLab CI 缓存

```yaml
# .gitlab-ci.yml
cache:
  key:
    files:
      - package-lock.json
  paths:
    - node_modules/
    - .npm/

test:
  stage: test
  script:
    - npm ci --cache .npm --prefer-offline
    - npm test
```

## Jenkins 缓存

```groovy
// Jenkinsfile
pipeline {
    agent any
    options {
        // 整个 Pipeline 共享 workspace
        skipDefaultCheckout(true)
    }
    stages {
        stage('Build') {
            steps {
                cache(maxCacheSize: 1000, caches: [
                    [$class: 'ArbitraryFileCache', excludes: '', includes: 'node_modules/**']
                ]) {
                    sh 'npm ci'
                    sh 'npm run build'
                }
            }
        }
    }
}
```

## 缓存键设计原则

```yaml
# 关键：key 必须包含"决定缓存有效性的所有变量"

# ✅ 正确
key: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json') }}
# 包含：OS + lockfile hash

# ❌ 错误
key: deps
# 问题：lockfile 变了但缓存命中 → 用旧依赖编译新代码 → bug

# ✅ 正确（多 key 策略）
primary: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json') }}
fallback: ${{ runner.os }}-deps-
# 优先精确匹配，失败用最近一次匹配
```

## 关联章节

- **01-pipeline/best-practices**：Pipeline 优化
- **01-pipeline/github-actions**：GitHub Actions 缓存细节
- **01-pipeline/jenkins**：Jenkins 缓存

## 一句话总结

> **缓存 = Pipeline 性能的第一杠杆**。**目标：cache hit > 85%、duration 降低 50%**。**关键：正确的 key 设计 + 适当的 fallback**。


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
