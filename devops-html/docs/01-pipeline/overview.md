---
title: CI/CD Pipeline 总览
---

# CI/CD Pipeline 总览

Pipeline as Code 是 DevOps 的核心范式。本章梳理 4 大主流 CI/CD 工具的设计取舍与工程实践。

## Pipeline as Code 范式

传统 CI/CD 把构建脚本写在 Jenkinsfile / .gitlab-ci.yml / GitHub Actions YAML 里，本质都是 **"用 DSL 描述流水线阶段"**。演进趋势：

```
1.0 Shell 脚本时代
  ↓ 配置散落，难以复用，难以审计
2.0 DSL 时代（Jenkinsfile / .travis.yml）
  ↓ 工具绑定，跨平台迁移难
3.0 Pipeline as Code（GitHub Actions / GitLab CI / Tekton）
  ↓ 声明式 + Git 真相源 + 复用 actions/components
4.0 平台工程时代（Backstage IDP / 黄金路径）
  ↓ 屏蔽 CI/CD 细节，开发者只关心业务逻辑
```

## 4 大工具横向对比

| 维度 | GitHub Actions | GitLab CI | Jenkins | Tekton |
|------|----------------|-----------|---------|--------|
| **托管形态** | SaaS + 自托管 Runner | SaaS + 自托管 Runner | 完全自托管 | K8s 原生 |
| **DSL 风格** | YAML 声明式 | YAML 声明式 | Groovy 脚本 | YAML 声明式 |
| **执行模型** | Job → Step | Stage → Job | Stage → Step | Task → Step |
| **Runner** | VM / Container / K8s | VM / Docker / K8s | Agent | K8s Pod |
| **可扩展性** | Actions 市场 | CI Components | 3000+ 插件 | 自由组合 Task |
| **缓存机制** | 内置 cache action | 内置 cache | 插件 + 手动 | PVC / OCI 镜像 |
| **最佳场景** | 开源 / GitHub 项目 | GitLab 全家桶 | 传统企业 / 复杂编排 | K8s 原生 / 多云 |
| **学习曲线** | 低 | 中 | 高 | 中高 |

## 核心概念地图

```yaml
# 通用 Pipeline 抽象
pipeline:
  trigger: [push, pr, schedule, manual]
  stage:
    - name: build
      steps: [checkout, install-deps, compile, unit-test]
    - name: test
      steps: [integration-test, coverage, security-scan]
    - name: package
      steps: [docker-build, push-registry, sign-image]
    - name: deploy
      steps: [argocd-sync, smoke-test]
```

## 选型决策树

```
Q1: 代码托管在哪？
  ├─ GitHub    → GitHub Actions
  ├─ GitLab    → GitLab CI
  └─ 其他 / 自建 → Jenkins 或 Tekton

Q2: 是否 K8s 原生？
  ├─ 是 → Tekton / Argo Workflows
  └─ 否 → GitHub Actions / GitLab CI / Jenkins

Q3: 团队规模？
  ├─ < 10 人  → GitHub Actions（最简单）
  ├─ 10-100 人 → GitLab CI / Jenkins（更可控）
  └─ > 100 人 → Tekton + 自建平台
```

## 关键工程实践

1. **缓存命中率**：70%+ 命中率是优秀管线的标志；用 `actions/cache` / GitLab `cache:key` 缓存 `node_modules`、`~/.m2`、`~/.gradle`
2. **并行化**：把测试拆成单元 / 集成 / E2E 并行执行，单 pipeline 从 15 分钟压到 5 分钟
3. **Matrix 矩阵**：跨 OS / 跨 Node 版本 / 跨数据库版本测试，参数化构建
4. **安全门禁**：集成 SAST（CodeQL / Semgrep）+ SCA（Trivy / Snyk）+ 镜像签名（Cosign / Sigstore）
5. **可观测性**：把 pipeline 元数据（duration / status / flakiness）打到 Prometheus，Grafana 看板可视化

## 关联章节

- **02-iac** → Pipeline 如何 provision 测试环境
- **03-gitops** → Pipeline 产物如何触发 GitOps 同步
- **05-cicd-observability** → 流水线自身的可观测性
- **06-best-practices** → 缓存 / 安全 / Secrets 集成
