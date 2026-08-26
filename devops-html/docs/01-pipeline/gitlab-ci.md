---
title: GitLab CI
---

# GitLab CI

GitLab 内置 CI/CD，业界最完整的一体化方案：SCM + CI + CD + Container Registry + Security 全部内置。

## 一句话总结

> **GitLab CI = DevSecOps 一体化**。**优势：一体化 / 内置 security / 多 runner 池**。**劣势：自托管运维成本高、UI 较 GitHub Actions 复杂**。

---

## 核心模型

```
.gitlab-ci.yml（YAML）
  ├── stages: [build, test, deploy]
  │     ├── stage: build
  │     │     └── job 1, job 2
  │     ├── stage: test
  │     └── stage: deploy
  └── variables / include / workflow
```

## 完整示例

```yaml
stages:
  - build
  - test
  - deploy

variables:
  DOCKER_IMAGE: registry.gitlab.com/myorg/myapp

build:
  stage: build
  image: docker:24
  services:
    - docker:24-dind
  script:
    - docker build -t $DOCKER_IMAGE:$CI_COMMIT_SHA .
    - docker push $DOCKER_IMAGE:$CI_COMMIT_SHA

test:
  stage: test
  image: node:20
  script:
    - npm ci
    - npm test
  coverage: '/Statements\s*:\s*(\d+\.\d+%)/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml

deploy:staging:
  stage: deploy
  image: bitnami/kubectl:latest
  script:
    - kubectl apply -f k8s/overlays/staging
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop

deploy:prod:
  stage: deploy
  script:
    - kubectl apply -f k8s/overlays/prod
  environment:
    name: production
  when: manual
  only:
    - main
```

## DAG（Directed Acyclic Graph）

```yaml
# 复杂流水线不必串行 stage
stages:
  - pre
  - parallel
  - post

pre:
  stage: pre
  script: echo "lint"

unit-test:
  stage: parallel
  needs: ["pre"]
  script: npm test

integration-test:
  stage: parallel
  needs: ["pre"]
  script: npm run test:e2e

build-image:
  stage: parallel
  needs: ["pre"]
  script: docker build

deploy:
  stage: post
  needs: ["unit-test", "integration-test", "build-image"]
  script: kubectl apply
```

## 内置 Security

```yaml
# SAST（静态扫描）
include:
  - template: Security/SAST.gitlab-ci.yml

# Dependency Scanning
include:
  - template: Security/Dependency-Scanning.gitlab-ci.yml

# Container Scanning
include:
  - template: Security/Container-Scanning.gitlab-ci.yml
```

## Runner 类型

```yaml
# 1. Shared Runner（GitLab.com 公共 runner）
# 2. Group Runner（组内共享，自托管）
# 3. Project Runner（项目私有）

# runner tag 用于 job 调度
job:
  tags:
    - docker
    - gpu
    - linux
```

## 实战案例

```
场景：100 研发团队，从 Jenkins 迁移到 GitLab CI
阶段 1（月 1-2）：影子运行
  - GitLab CI 与 Jenkins 并行，所有项目两份 Pipeline
  - 验证 GitLab CI 工作流、收集团队反馈

阶段 2（月 3-4）：分批迁移
  - 按团队优先级（前端 / 后端 / 移动）分批切换
  - 每个团队切完后保留 Jenkins 1 周兜底

阶段 3（月 5-6）：完全切换
  - Jenkins 进入只读模式（保留历史）
  - GitLab CI 成为唯一 CI

结果：
  - 部署频率：从 周 2 次 提升到 日 8 次
  - Pipeline duration：从 25 分钟 压到 8 分钟
  - 开发者满意度：NPS 从 32 提升到 58
```

## 关联章节

- **01-pipeline/github-actions**：GitHub Actions 横向对比
- **01-pipeline/tekton**：Tekton（云原生）
- **06-best-practices/secure-pipeline**：安全 Pipeline 最佳实践

## 一句话总结

> **GitLab CI = 自托管完整 DevSecOps 平台**。**强项：SaaS + 自托管双模式 / 一体化 / DAG / 内置 security**。**弱项：Runner 运维成本、UI 学习曲线**。


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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
