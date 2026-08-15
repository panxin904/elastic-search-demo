---
title: GitHub Actions
---

# GitHub Actions

GitHub 内置的 CI/CD 平台，与 GitHub Repo 深度集成，无需外部服务即可完成 build / test / deploy。

## 一句话总结

> **GitHub Actions = GitHub 原生 CI/CD**。**YAML 写在 .github/workflows/**，**核心：workflow → job → step → action（复用 marketplace）**。

---

## 核心模型

```
Workflow（.github/workflows/*.yml）
  ├── Job 1 (runs-on: ubuntu-latest)
  │     ├── Step 1: actions/checkout@v4
  │     ├── Step 2: actions/setup-node@v4
  │     └── Step 3: npm test
  ├── Job 2 (depends on Job 1)
  └── Job 3 (matrix: [node 18, 20, 22])
```

## 完整示例：Node.js CI/CD

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node: [18, 20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: 'npm'
      - run: npm ci
      - run: npm test
      - run: npm run build

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to K8s
        env:
          KUBECONFIG: ${{ secrets.KUBECONFIG }}
        run: |
          echo "$KUBECONFIG" > kubeconfig
          kubectl apply -f k8s/
          kubectl rollout status deployment/myapp
```

## 3 大复用机制

```yaml
# 1. Marketplace Actions（官方/社区 action）
- uses: actions/checkout@v4
- uses: docker/build-push-action@v5
- uses: aws-actions/configure-aws-credentials@v4

# 2. Composite Actions（组合 step）
# .github/actions/setup-env/action.yml
runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
    - run: npm ci
      shell: bash

# 3. Reusable Workflows（跨 repo 共享）
# .github/workflows/reusable-deploy.yml
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
```

## Self-hosted Runner

```yaml
# 适用场景：需要访问内网 GPU / 编译 ARM
runs-on: [self-hosted, linux, gpu]
```

```bash
# 注册 runner
./config.sh --url https://api.github.com/enterprise --token XXX
./run.sh

# Docker runner
docker run -d \
  -e RUNNER_TOKEN=XXX \
  -e RUNNER_NAME=runner-1 \
  myoung34/github-runner:latest
```

## 性能优化

```yaml
# 1. 缓存依赖
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}

# 2. 并发 job
strategy:
  fail-fast: false
  matrix:
    service: [api, worker, scheduler]

# 3. 只跑变更的 job
# uses: dorny/paths-filter
```

## 关联章节

- **01-pipeline/gitlab-ci**：GitLab CI 横向对比
- **01-pipeline/tekton**：Tekton（云原生 Pipeline）
- **06-best-practices/caching**：CI 缓存最佳实践
- **06-best-practices/oidc-federation**：GitHub OIDC 联邦到云厂商

## 一句话总结

> **GitHub Actions = GitHub 生态首选**。**优势：零配置 / marketplace / OIDC / matrix**。**劣势：复杂 Pipeline 编排弱、GPU runner 需要自建**。
