---
title: CI/CD Pipeline 最佳实践
---

# CI/CD Pipeline 最佳实践

跨工具通用的 Pipeline 设计原则，让团队从"能跑"到"跑得快、跑得稳"。

## 一句话总结

> **Pipeline 最佳实践 = 4 大原则：缓存 / 并行 / 分层 / 反馈**。**目标：提交到反馈 < 10 分钟、cache hit > 80%、success rate > 95%**。

---

## 1. 分层测试

```yaml
# Stage 1：快速反馈（< 2 分钟）
- lint（ESLint / golangci-lint）
- type check（tsc --noEmit）
- unit test（单文件）

# Stage 2：完整验证（< 10 分钟）
- 全量 unit test
- integration test（DB / 缓存）
- contract test（API 契约）

# Stage 3：端到端（< 30 分钟）
- e2e test（Playwright / Cypress）
- performance test（k6 / Locust）
- security scan（Trivy / Snyk）

# Stage 4：部署
- staging deploy
- smoke test
- production deploy（金丝雀）
```

## 2. 缓存策略

```yaml
# 依赖缓存
- uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      node_modules
    key: ${{ runner.os }}-deps-${{ hashFiles('**/lock.*') }}
    restore-keys: |
      ${{ runner.os }}-deps-

# 构建缓存（Docker BuildKit）
# Dockerfile
RUN --mount=type=cache,target=/root/.npm \
    npm ci

# 测试结果缓存
- uses: actions/cache@v4
  with:
    path: .test-cache
    key: test-${{ hashFiles('**/*.test.ts') }}
```

## 3. 并行优化

```yaml
# Matrix（多版本并行）
strategy:
  matrix:
    node: [18, 20, 22]
    os: [ubuntu, macos, windows]

# Job 并行（无依赖时）
jobs:
  lint:
  type-check:
  test-unit:
  test-e2e:
  build:
  # 这些 job 无依赖，全部并行
```

## 4. 反馈速度

```yaml
# 1. PR 触发快速 Pipeline（< 5 分钟）
on:
  pull_request:
    paths:
      - '**.go'
      - 'go.mod'

# 2. Required check vs Informational
# Required：lint / type check / unit test
# Informational：e2e / perf

# 3. 增量测试（只跑变更影响）
- uses: dorny/paths-filter@v3
  id: filter
  with:
    filters: |
      backend:
        - 'src/**'
        - 'tests/**'
```

## 5. 流水线设计反模式

```
❌ 反模式 1：单一大 Pipeline 跑 1 小时
✅ 正确：分层 + 并行，关键路径 < 10 分钟

❌ 反模式 2：缓存键不区分 OS
✅ 正确：key: ${{ runner.os }}-deps-...

❌ 反模式 3：每个 job 都从头 install
✅ 正确：artifact 上传下载 / mount cache

❌ 反模式 4：失败不通知
✅ 正确：Slack / Email / Lark 集成

❌ 反模式 5：生产部署不需要审批
✅ 正确：生产环境用 manual gate 或 PR approval
```

## 6. Pipeline 模板化

```yaml
# 复用：抽 5 个常用 pipeline 模板
templates/
├── nodejs-ci.yml       # Node 项目通用
├── docker-build.yml    # 镜像构建
├── k8s-deploy.yml      # K8s 部署
├── terraform-apply.yml # IaC 应用
└── notify.yml          # 通知（Slack / Lark）
```

## 关联章节

- **01-pipeline/github-actions**：GitHub Actions 缓存
- **01-pipeline/jenkins**：Jenkins 分布式 build
- **05-cicd-observability/pipeline-monitoring**：Pipeline 性能监控
- **06-best-practices/caching**：深度缓存策略

## 一句话总结

> **Pipeline 优化 = 分层 + 缓存 + 并行 + 反馈**。**关键指标：cycle time（提交到反馈）+ cache hit rate + success rate**。
