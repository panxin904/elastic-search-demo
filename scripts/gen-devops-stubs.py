"""Generate devops stub pages via CONTENT dictionary.

Reuses the pattern from scripts/gen-security-stubs.py:
- Each entry is a multiline string with Frontmatter + 5-7 H2 sections + code blocks + 实战案例 + 关联章节 + 一句话总结
- After write, run find -size -3000c to find any remaining stubs
"""
import os

DOCS_ROOT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "devops-html", "docs",
)

CONTENT = {

# ============ 01-pipeline (5 stubs) ============
"01-pipeline/github-actions.md": """---
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
docker run -d \\
  -e RUNNER_TOKEN=XXX \\
  -e RUNNER_NAME=runner-1 \\
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
""",

"01-pipeline/gitlab-ci.md": """---
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
  coverage: '/Statements\\s*:\\s*(\\d+\\.\\d+%)/'
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

## 关联章节

- **01-pipeline/github-actions**：GitHub Actions 横向对比
- **01-pipeline/tekton**：Tekton（云原生）
- **06-best-practices/secure-pipeline**：安全 Pipeline 最佳实践

## 一句话总结

> **GitLab CI = 自托管完整 DevSecOps 平台**。**强项：SaaS + 自托管双模式 / 一体化 / DAG / 内置 security**。**弱项：Runner 运维成本、UI 学习曲线**。
""",

"01-pipeline/jenkins.md": """---
title: Jenkins
---

# Jenkins

Jenkins 是 CI/CD 工具的鼻祖（2004 年 Hudson 衍生），功能最全面但运维最重。本章梳理 Jenkins 核心架构与现代化用法。

## 一句话总结

> **Jenkins = 经典 CI/CD 工具**。**强项：插件生态最丰富 / Pipeline as Code / 分布式 Master-Agent**。**弱项：运维重 / UI 老旧 / 配置漂移（解决：Configuration as Code）**。

---

## 架构

```
Jenkins Master（控制器）
  ├── 调度 job
  ├── 存储配置 / build 历史 / plugins
  └── 不执行 build（避免 master 资源竞争）

Jenkins Agent（执行器）
  ├── SSH / JNLP / K8s Pod 启动
  ├── 接收 job 执行
  └── 并发能力（多个 agent）
```

## Jenkinsfile（Pipeline as Code）

```groovy
pipeline {
    agent any

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        timestamps()
    }

    stages {
        stage('Build') {
            steps {
                sh 'npm ci'
                sh 'npm run build'
            }
        }

        stage('Test') {
            parallel {
                stage('Unit') {
                    steps { sh 'npm test' }
                }
                stage('Integration') {
                    steps { sh 'npm run test:e2e' }
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                input 'Deploy to production?'
                sh 'kubectl apply -f k8s/'
            }
        }
    }

    post {
        success { slackSend(channel: '#deploys', message: '✅ Deployed') }
        failure { slackSend(channel: '#alerts', message: '❌ Failed') }
    }
}
```

## K8s 上的 Jenkins（动态 Agent）

```yaml
# jenkins-casc.yaml（Configuration as Code）
jenkins:
  clouds:
    - kubernetes:
        name: "k8s"
        serverUrl: "https://k8s-api.example.com"
        namespace: "jenkins"
        templates:
          - name: "jenkins-agent"
            label: "jenkins-agent"
            containerTemplate:
              name: "jnlp"
              image: "jenkins/inbound-agent:latest"
```

```groovy
// Jenkinsfile 中动态使用 K8s Agent
pipeline {
    agent {
        kubernetes {
            label 'jenkins-agent'
            yaml '''
                apiVersion: v1
                kind: Pod
                spec:
                  containers:
                    - name: jnlp
                      image: jenkins/inbound-agent
                    - name: node
                      image: node:20
                      command: ["cat"]
                      tty: true
                '''
        }
    }
    stages {
        stage('Test') {
            steps {
                container('node') {
                    sh 'npm ci && npm test'
                }
            }
        }
    }
}
```

## Configuration as Code（JCasC）

```yaml
# jenkins.yaml（声明式配置，避免 UI 配置漂移）
jenkins:
  systemMessage: "Production Jenkins"
  numExecutors: 0
  securityRealm:
    local:
      allowsSignup: false
  authorizationStrategy:
    loggedInUsersCanDoAnything:
      allowAnonymousRead: false

credentials:
  system:
    domainCredentials:
      - credentials:
          - usernamePassword:
              scope: GLOBAL
              id: "github-creds"
              username: "ci-bot"
              password: "${GITHUB_TOKEN}"
```

## 插件管理

```yaml
# plugins.yaml（声明式插件列表）
plugins:
  required:
    - kubernetes:4260.va7866468c5b_d
    - configuration-as-code:1850.va_a_8c31d99e1
    - pipeline-stage-view:2.34
    - blueocean:1.27.7
```

## 关联章节

- **01-pipeline/github-actions**：GitHub Actions 对比（云原生 vs 老牌）
- **01-pipeline/tekton**：Tekton（更云原生的 Pipeline 框架）
- **06-best-practices/caching**：Jenkins 缓存策略

## 一句话总结

> **Jenkins = 复杂场景的常青树**。**核心价值：插件 1800+ / JCasC 解决配置漂移 / K8s 动态 agent**。**何时不用：SaaS 优先 / 团队小 / 追求现代化 UI**。
""",

"01-pipeline/tekton.md": """---
title: Tekton
---

# Tekton

Tekton 是 CNCF 毕业项目，云原生的 CI/CD 框架，基于 K8s CRD 定义 Pipeline，与 K8s 生态深度集成。

## 一句话总结

> **Tekton = K8s 原生 CI/CD 框架**。**核心 CRD：Task / TaskRun / Pipeline / PipelineRun**。**强项：K8s 集成 / 复用 Pipeline / 跨集群**。**弱项：学习曲线 / 缺少 UI / 配置复杂**。

---

## 4 大 CRD

```
Task        单个可复用步骤集合（如 git clone + build）
TaskRun     执行 Task（K8s Pod）
Pipeline    多 Task 编排
PipelineRun 执行 Pipeline
```

## Task 示例

```yaml
apiVersion: tekton.dev/v1
kind: Task
metadata:
  name: build-and-push
spec:
  workspaces:
    - name: source
  params:
    - name: image
      type: string
    - name: dockerfile
      type: string
      default: Dockerfile
  steps:
    - name: build
      image: gcr.io/kaniko-project/executor:latest
      args:
        - --dockerfile=$(params.dockerfile)
        - --destination=$(params.image)
        - --context=/workspace/source
```

## Pipeline 示例

```yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: build-deploy-pipeline
spec:
  workspaces:
    - name: shared-data
  params:
    - name: git-url
    - name: image-name
  tasks:
    - name: fetch-source
      taskRef: { name: git-clone }
      workspaces:
        - name: output
          workspace: shared-data
      params:
        - { name: url, value: $(params.git-url) }

    - name: build
      runAfter: [fetch-source]
      taskRef: { name: build-and-push }
      workspaces:
        - name: source
          workspace: shared-data
      params:
        - { name: image, value: $(params.image-name) }

    - name: deploy
      runAfter: [build]
      taskRef: { name: kubectl-apply }
      params:
        - { name: manifest, value: k8s/deployment.yaml }
```

## PipelineRun

```yaml
apiVersion: tekton.dev/v1
kind: PipelineRun
metadata:
  generateName: build-deploy-
spec:
  pipelineRef:
    name: build-deploy-pipeline
  workspaces:
    - name: shared-data
      volumeClaimTemplate:
        spec:
          accessModes: [ReadWriteOnce]
          resources: { requests: { storage: 1Gi } }
  params:
    - { name: git-url, value: "https://github.com/myorg/myapp" }
    - { name: image-name, value: "registry.example.com/myapp:latest" }
```

## 复用机制

```yaml
# 1. Remote Resolution（远程 Task）
- name: lint
  taskRef:
    resolver: git
    params:
      - { name: url, value: https://github.com/myorg/catalog }
      - { name: revision, value: main }
      - { name: pathInRepo, value: tasks/lint.yaml }

# 2. Pipeline as Code（Tekton Chains）
# 自动记录镜像签名 + provenance

# 3. Trigger（Tekton Triggers）
apiVersion: triggers.tekton.dev/v1beta1
kind: EventListener
metadata:
  name: github-listener
spec:
  triggers:
    - bindings: [{ ref: github-push-binding }]
      template: { ref: pipeline-template }
```

## 生态工具

| 工具 | 用途 |
|------|------|
| **tkn CLI** | Tekton 命令行 |
| **Tekton Dashboard** | Web UI（官方） |
| **Tekton Hub** | 共享 Task 库 |
| **Pipelines as Code (PaC)** | GitOps Pipeline（PR 自动触发） |
| **ArgoCD Events** | 与 ArgoCD 集成 |

## 关联章节

- **01-pipeline/github-actions**：GitHub Actions 对比
- **01-pipeline/jenkins**：Jenkins 对比
- **03-gitops/argocd**：ArgoCD Events 触发 Tekton

## 一句话总结

> **Tekton = K8s 团队的 Pipeline 底座**。**何时用：已经在 K8s / 需要 Pipeline 复用 / 跨集群 / 需要 provenance**。**何时不用：MVP / 小团队 / GitHub Actions 已够**。
""",

"01-pipeline/best-practices.md": """---
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
RUN --mount=type=cache,target=/root/.npm \\
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
""",

# ============ 02-iac (4 stubs) ============
"02-iac/terraform.md": """---
title: Terraform
---

# Terraform

HashiCorp 推出的 IaC 工具，使用 HCL（HashiCorp Configuration Language）声明基础设施。是 IaC 行业事实标准。

## 一句话总结

> **Terraform = IaC 事实标准**。**核心：HCL + Provider 生态 + State 管理**。**强项：多云 / 模块化 / State 协作**。**弱项：HCL 不通用 / 状态管理复杂 / 商业化后部分功能需付费**。

---

## 核心模型

```
Provider       云厂商适配器（AWS / GCP / K8s / GitHub）
Resource       基础设施资源（aws_instance, kubernetes_pod）
Data Source    只读查询（aws_ami, data "terraform_remote_state"）
State          真实资源 ↔ 代码映射（terraform.tfstate）
Module         复用的资源集合
```

## 完整示例：AWS EC2

```hcl
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket = "myorg-tfstate"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "tfstate-lock"
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.medium"

  tags = {
    Name        = "web-${var.environment}"
    Environment = var.environment
  }
}

output "instance_ip" {
  value = aws_instance.web.public_ip
}
```

## Module 设计

```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block = var.cidr_block
}

resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
}
```

```hcl
# 使用 module
module "vpc" {
  source      = "./modules/vpc"
  cidr_block  = "10.0.0.0/16"
  environment = var.environment
}
```

## State 管理

```bash
# 远程 State（S3 + DynamoDB Lock）
terraform {
  backend "s3" {
    bucket         = "myorg-tfstate"
    key            = "prod/vpc.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-lock"   # 防止并发
    encrypt        = true
  }
}

# 操作
terraform init      # 初始化（下载 provider / 配置 backend）
terraform plan      # 预览变更
terraform apply     # 执行
terraform destroy   # 销毁
terraform import    # 把现有资源导入 State
```

## State 协作

```hcl
# 跨项目共享数据
data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = "myorg-tfstate"
    key    = "shared/vpc.tfstate"
    region = "us-east-1"
  }
}

resource "aws_subnet" "app" {
  vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id
}
```

## 常用工作流

```bash
# 1. 工作区（多环境隔离）
terraform workspace new staging
terraform workspace new prod
terraform workspace select prod

# 2. 变量文件
terraform.tfvars
terraform.tfvars.staging
terraform.tfvars.prod

# 3. tfsec（安全扫描）
tfsec .

# 4. drift detection（生产建议定期 plan）
terraform plan -detailed-exitcode
```

## 关联章节

- **02-iac/pulumi**：Pulumi（编程语言 IaC）
- **02-iac/ansible**：Ansible（配置管理）
- **02-iac/terraform-vs-pulumi**：详细对比
- **03-gitops**：State 后端用 GitOps 模式管理

## 一句话总结

> **Terraform = 多云 IaC 的标准答案**。**何时用：多云 / 大规模基础设施 / 团队熟悉 HCL**。**何时不用：纯 K8s（用 Helm/Kustomize）/ 简单脚本（用 Pulumi/Python）**。
""",

"02-iac/pulumi.md": """---
title: Pulumi
---

# Pulumi

Pulumi 是 IaC 的现代化方案：用 TypeScript / Python / Go 等通用编程语言定义基础设施。

## 一句话总结

> **Pulumi = 编程语言 IaC**。**核心：通用语言 + 强类型 + 标准工具链（IDE / 测试 / 包管理）**。**强项：编程能力（循环 / 条件 / 函数）/ 测试友好**。**弱项：学习曲线 / 社区生态小于 Terraform**。

---

## 与 Terraform 对比

| 维度 | Terraform | Pulumi |
|------|-----------|--------|
| 语言 | HCL（DSL） | TypeScript / Python / Go / Java |
| 类型系统 | 弱类型 | 强类型（IDE 自动补全） |
| 测试 | terratest（Go） | 原生 unit test（用语言生态） |
| State | tfstate 文件 | Pulumi Service（云托管）+ 本地 |
| 复用 | Module + Terraform Registry | NPM / PyPI 包 + 任意语言 |
| 多云 | Provider 生态（成熟） | Provider（覆盖主流但较少） |
| 学习曲线 | 低（HCL 易学） | 中（需编程能力） |

## 完整示例：TypeScript

```typescript
import * as aws from "@pulumi/aws";
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();
const environment = config.require("environment");

// VPC
const vpc = new aws.ec2.Vpc("main", {
    cidrBlock: "10.0.0.0/16",
    tags: { Environment: environment },
});

// Subnet
const subnet = new aws.ec2.Subnet("public", {
    vpcId: vpc.id,
    cidrBlock: "10.0.1.0/24",
    availabilityZone: "us-east-1a",
});

// EC2
const web = new aws.ec2.Instance("web", {
    ami: "ami-0c55b159cbfafe1f0",
    instanceType: "t3.medium",
    subnetId: subnet.id,
    tags: { Name: `web-${environment}` },
});

export const instanceIp = web.publicIp;
export const vpcId = vpc.id;
```

## 编程能力示例

```typescript
// 循环创建多 AZ subnet
const azs = ["us-east-1a", "us-east-1b", "us-east-1c"];
const subnets = azs.map((az, i) =>
    new aws.ec2.Subnet(`subnet-${az}`, {
        vpcId: vpc.id,
        cidrBlock: `10.0.${i + 1}.0/24`,
        availabilityZone: az,
    })
);

// 函数封装复用
function createWebServer(name: string, port: number) {
    return new aws.ec2.Instance(name, { /* ... */ });
}

const webServers = ["api", "worker", "scheduler"]
    .map(name => createWebServer(name, 8080));

// 条件
const enableLogging = config.getBoolean("logging") ?? true;
if (enableLogging) {
    new aws.cloudwatch.LogGroup("app", { /* ... */ });
}
```

## 测试（Pulumi 强项）

```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import "mocha";
import { expect } from "chai";
import { getStack, getStackOutputs } from "./test-utils";

describe("Infrastructure", () => {
    let stack: string;
    let outputs: Record<string, any>;

    before(async () => {
        stack = await getStack();
        outputs = await getStackOutputs(stack);
    });

    it("should have 3 subnets", async () => {
        expect(outputs.subnetCount).to.equal(3);
    });

    it("should have correct VPC CIDR", async () => {
        expect(outputs.vpcCidr).to.equal("10.0.0.0/16");
    });
});
```

## 工作流

```bash
# 安装
npm install -g @pulumi/pulumi

# 初始化
pulumi new aws-typescript

# 预览
pulumi preview

# 部署
pulumi up

# 销毁
pulumi destroy

# Stack（多环境）
pulumi stack init staging
pulumi stack init prod
pulumi stack select prod
```

## 关联章节

- **02-iac/terraform**：Terraform（HCL DSL）
- **02-iac/terraform-vs-pulumi**：详细对比
- **02-iac/ansible**：Ansible（配置管理）

## 一句话总结

> **Pulumi = 开发者友好的 IaC**。**何时用：团队有强编程能力 / 需要测试 / 想用 IDE 自动补全**。**何时不用：HCL 已足够 / 团队不想学编程**。
""",

"02-iac/ansible.md": """---
title: Ansible
---

# Ansible

Ansible 是 Red Hat 推出的配置管理工具，使用 YAML（Playbook）定义任务，agentless 架构（SSH 执行）。

## 一句话总结

> **Ansible = 配置管理 + 轻量部署**。**核心：Playbook（YAML）+ Inventory（主机列表）+ Module（执行单元）**。**强项：agentless / 简单易学 / 适合运维场景**。**弱项：编排能力弱 / 大规模性能差 / 不适合云基础设施**。

---

## 核心模型

```
Inventory     主机列表（IP / 域名 / 分组）
Playbook      YAML 文件，定义任务序列
Role          可复用的 Playbook 集合（tasks / handlers / vars / templates）
Task          单个操作（用 module 执行）
Module        执行单元（apt, copy, service, file, command）
Handler       触发器（notify + listen）
```

## 完整示例

```yaml
# inventory.ini
[web]
web1.example.com
web2.example.com

[db]
db1.example.com

[prod:children]
web
db

# playbook.yml
- name: Deploy web app
  hosts: web
  become: yes
  vars:
    app_version: "1.2.3"
    app_port: 8080

  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
        update_cache: yes

    - name: Copy app config
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/sites-available/app.conf
      notify: reload nginx

    - name: Ensure nginx running
      service:
        name: nginx
        state: started
        enabled: yes

  handlers:
    - name: reload nginx
      service:
        name: nginx
        state: reloaded
```

## Role 结构

```
roles/
└── webserver/
    ├── tasks/main.yml
    ├── handlers/main.yml
    ├── templates/nginx.conf.j2
    ├── files/index.html
    ├── vars/main.yml
    ├── defaults/main.yml
    └── meta/main.yml
```

```yaml
# 使用 role
- hosts: web
  roles:
    - webserver
    - { role: db, when: "inventory_hostname in groups['db']" }
```

## 常用 Module

```yaml
# 包管理
- apt: { name: nginx, state: present }
- yum: { name: httpd, state: latest }
- pip: { name: django, version: "4.2" }

# 文件
- copy: { src: app.conf, dest: /etc/app.conf }
- template: { src: app.conf.j2, dest: /etc/app.conf }
- file: { path: /var/log/app, state: directory, mode: '0755' }

# 服务
- service: { name: nginx, state: started, enabled: yes }

# 命令
- command: /opt/app/bin/migrate
- shell: "ps aux | grep nginx"
```

## 与 Terraform 的边界

| 工具 | 适合 |
|------|------|
| **Terraform** | 云基础设施（VPC / K8s / 托管服务） |
| **Ansible** | OS 配置（包 / 服务 / 文件 / 用户） |
| **混合** | Terraform 创建资源 → Ansible 配置软件 |

## AWX（Ansible Tower）

```yaml
# AWX = Ansible 的 Web UI + REST API
# 功能：
# - Job Template（Web 触发 Playbook）
# - 凭据管理（Vault / SSH key）
# - 审批流
# - 调度（cron）
# - 审计日志
```

## 关联章节

- **02-iac/terraform**：Terraform（云基础设施）
- **02-iac/pulumi**：Pulumi（编程 IaC）
- **01-pipeline/best-practices**：CI 中调用 Ansible

## 一句话总结

> **Ansible = 运维自动化的事实标准**。**何时用：OS 配置 / 批量部署 / 已有 SSH 主机**。**何时不用：云基础设施（用 Terraform）/ 大规模 K8s（用 Helm）/ 复杂编排（用 Ansible + AWX）**。
""",

"02-iac/terraform-vs-pulumi.md": """---
title: Terraform vs Pulumi
---

# Terraform vs Pulumi

两个 IaC 工具的详细对比，帮团队选择合适的方案。

## 一句话总结

> **Terraform = 生态成熟 / HCL DSL**；**Pulumi = 编程语言 / 测试友好**。**决策点：团队编程能力 + 生态需求 + 测试要求**。

---

## 11 个维度对比

| 维度 | Terraform | Pulumi | 推荐场景 |
|------|-----------|--------|----------|
| **语言** | HCL（DSL） | TS / Python / Go / Java | Pulumi 适合编程团队 |
| **学习曲线** | 低 | 中 | Terraform 适合新手 |
| **类型系统** | 弱 | 强（IDE 补全） | Pulumi 适合大型项目 |
| **Provider 生态** | 3000+ | 150+ | Terraform 多云首选 |
| **State** | 多种 backend（S3/Terraform Cloud） | Pulumi Service / 本地 | Terraform 更灵活 |
| **复用** | Module + Registry | NPM / PyPI + 任意语言 | Pulumi 更通用 |
| **测试** | terratest（外置） | 原生 unit test | Pulumi 强 |
| **Plan/Preview** | terraform plan | pulumi preview | 都优秀 |
| **工具链** | terraform CLI | pulumi CLI + 语言工具 | Pulumi 用 IDE 工具 |
| **CI/CD 集成** | 简单（plan + apply） | 简单 | 都优秀 |
| **社区规模** | 大 | 中 | Terraform 文档丰富 |

## 代码示例对比

```hcl
# Terraform：创建 S3 bucket
resource "aws_s3_bucket" "logs" {
  bucket = "myorg-logs-${var.environment}"

  tags = {
    Environment = var.environment
    Owner       = "platform"
  }
}

# 创建多个 bucket（for_each）
resource "aws_s3_bucket" "logs" {
  for_each = toset(["app", "audit", "metrics"])

  bucket = "myorg-logs-${each.key}-${var.environment}"
}
```

```typescript
// Pulumi：创建 S3 bucket
import * as aws from "@pulumi/aws";

const buckets = ["app", "audit", "metrics"].map(name =>
    new aws.s3.Bucket(`logs-${name}`, {
        bucket: `myorg-logs-${name}-${environment}`,
        tags: { Environment: environment, Owner: "platform" },
    })
);

export const bucketNames = buckets.map(b => b.bucket);
```

## 选型决策树

```
Q1：团队是否熟悉编程？
  ├─ 是 → Pulumi（TS / Python / Go 都可以）
  └─ 否 → Terraform（HCL 易学）

Q2：需要多云管理（AWS / GCP / Azure 都有资源）？
  ├─ 是 → Terraform（Provider 生态最完整）
  └─ 否 → Pulumi 也可以

Q3：基础设施规模（> 100 资源 / > 50 模块）？
  ├─ 是 → Pulumi（编程语言抽象能力更强）
  └─ 否 → Terraform（够用）

Q4：是否需要单元测试 + CI 集成？
  ├─ 是 → Pulumi（原生测试框架）
  └─ 否 → Terraform（terratest 也能用）

Q5：是否已经在用 Terraform？
  ├─ 是 → 继续用（迁移成本高）
  └─ 否 → 新项目看上面 Q1-Q4
```

## 混合方案

```bash
# 常见模式：Terraform 管基础设施，Pulumi 管应用
# - Terraform：VPC / Subnet / IAM / EKS
# - Pulumi：应用 K8s manifest / ArgoCD Application

# 通过 data source 共享
# Terraform output
output "vpc_id" { value = aws_vpc.main.id }

# Pulumi 引用
const vpcId = require("./terraform-output").vpcId;
```

## 关联章节

- **02-iac/terraform**：Terraform 详情
- **02-iac/pulumi**：Pulumi 详情
- **02-iac/ansible**：Ansible（配置管理）

## 一句话总结

> **Terraform = 默认选择 / 生态优先**；**Pulumi = 编程团队 / 大规模项目 / 测试驱动**。**两者可共存：Terraform 管云基础设施，Pulumi 管应用层**。
""",

# ============ 03-gitops (3 stubs) ============
"03-gitops/argocd.md": """---
title: ArgoCD
---

# ArgoCD

ArgoCD 是 CNCF 毕业项目，GitOps 领域的标志性工具，自动同步 Git Repo 与 K8s 集群状态。

## 一句话总结

> **ArgoCD = GitOps 事实标准**。**核心：Application CRD + 调和循环 + Web UI**。**强项：UI / 多租户 / 多集群**。**弱项：单点（HA 需要 Workaround）**。

---

## 核心概念

```
Application    单个应用（Git 源 + 目标集群 + 目标 namespace）
AppProject     多应用分组（RBAC + 集群白名单）
Repository     Git/Helm 仓库源
Sync Status    Healthy / Degraded / Suspended / Unknown
Drift          Git 与集群实际状态不一致
```

## Application CRD

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/myorg/my-app-manifests
    targetRevision: HEAD
    path: overlays/prod
    helm:
      valueFiles:
        - values-prod.yaml

  destination:
    server: https://kubernetes.default.svc
    namespace: my-app

  syncPolicy:
    automated:
      prune: true           # 自动删除 Git 不存在的资源
      selfHeal: true        # 自动修复集群漂移
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

  revisionHistoryLimit: 10
```

## 调和循环

```yaml
# 1. Poll Git（默认 3 分钟，可改为 webhook）
# 2. Diff Git vs 集群
# 3. Sync（应用差异）
# 4. 健康检查（Resource Hooks）
```

## Sync Phases

```yaml
# PreSync：先执行（数据库 migration）
# Sync：核心（deployment apply）
# PostSync：后执行（通知 / 缓存预热）
# SyncFail：失败时执行

metadata:
  name: my-app
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
```

## App of Apps 模式

```yaml
# 父 Application 管所有子 Application
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/myorg/manifests
    path: apps/             # apps/ 目录下每个目录 = 一个子 Application
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
```

```yaml
# apps/my-app/my-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  source:
    repoURL: https://github.com/myorg/manifests
    path: my-app
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app
```

## HA 架构

```yaml
# ArgoCD HA = 多副本 + Redis HA + Repo Server 多副本
spec:
  replicas: 3

# 关键组件：
# - argocd-application-controller（多副本）
# - argocd-repo-server（多副本）
# - argocd-server（多副本）
# - argocd-redis（HA 模式）
```

## 实战案例

```bash
# 安装 ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 端口转发 UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# CLI 登录
argocd login localhost:8080

# 创建应用
argocd app create my-app \\
  --repo https://github.com/myorg/manifests \\
  --path overlays/prod \\
  --dest-server https://kubernetes.default.svc \\
  --dest-namespace my-app \\
  --sync-policy automated

# 查看状态
argocd app list
argocd app get my-app
argocd app history my-app
```

## 关联章节

- **03-gitops/overview**：GitOps 总览
- **03-gitops/flux**：Flux 对比
- **04-release/canary**：Argo Rollouts 实现的金丝雀
- **04-release/progressive-delivery**：Argo Rollouts 高级用法

## 一句话总结

> **ArgoCD = GitOps 首选**。**何时用：K8s 团队 / 需要 UI / 多租户**。**何时不用：非 K8s 工作负载（VM / Serverless）/ 跨云编排（用 Crossplane）**。
""",

"03-gitops/flux.md": """---
title: Flux
---

# Flux

Flux 是 CNCF 毕业项目，GitOps 工具集，采用微服务架构（多个 Controller 协同工作）。

## 一句话总结

> **Flux = GitOps-native 框架**。**核心：GitOps Toolkit（多个 CRD Controller）**。**强项：云原生 / GitOps 原则贯彻 / 与 ArgoCD 互补**。**弱项：UI 弱（需 CLI 或外部）/ 多租户需要自己实现**。

---

## GitOps Toolkit（6 个 Controller）

```
Source Controller      拉取 Git/Helm/S3 源
Kustomize Controller   调和 Kustomization
Helm Controller        调和 HelmRelease
Notification Controller  事件通知（Slack / Lark）
Image Reflector / Updater  自动更新镜像 tag
Image Automation Controller  基于策略更新 image
```

## 核心 CRD

```yaml
# GitRepository（源码）
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  url: https://github.com/myorg/my-app-manifests
  ref:
    branch: main
```

```yaml
# Kustomization（应用）
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: my-app
  path: ./overlays/prod
  prune: true
  wait: true
  timeout: 5m
```

```yaml
# HelmRelease（Helm 应用）
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  chart:
    spec:
      chart: my-app
      version: "1.2.3"
      sourceRef:
        kind: HelmRepository
        name: my-registry
  values:
    replicaCount: 3
    image:
      tag: v1.2.3
```

## Flux CLI

```bash
# 安装
curl -s https://fluxcd.io/install.sh | sudo bash

# bootstrap（一次性安装 + 接入 Git）
flux bootstrap github \\
  --owner=myorg \\
  --repository=fleet-infra \\
  --branch=main \\
  --path=clusters/prod \\
  --personal

# 常用命令
flux get sources git
flux get kustomizations
flux get helmreleases
flux reconcile kustomization my-app
flux suspend kustomization my-app
flux resume kustomization my-app
```

## Flux vs ArgoCD 决策

| 维度 | ArgoCD | Flux |
|------|--------|------|
| **架构** | 单体 + UI | 微服务 + CLI |
| **UI** | 强（Web） | 弱（CLI + Grafana） |
| **多租户** | AppProject 原生 | 需要 namespace 隔离 |
| **Helm 集成** | 内置 | Helm Controller |
| **Kustomize** | 内置 | Kustomize Controller |
| **通知** | 弱 | Notification Controller |
| **学习曲线** | 中（概念集中） | 中（多个 CRD） |
| **GitOps 纯粹度** | 高（但有人批评 UI 不够 GitOps） | 极高（GitOps-native） |
| **生态** | Argo Rollouts / Argo Events / Argo Workflows | Flagger（渐进式发布） |

## 通知配置

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta2
kind: Alert
metadata:
  name: on-call
  namespace: flux-system
spec:
  providerRef:
    name: slack
  eventSeverity: error
  eventSources:
    - kind: Kustomization
      name: '*'
```

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta1
kind: Provider
metadata:
  name: slack
  namespace: flux-system
spec:
  type: slack
  channel: alerts
  address: https://hooks.slack.com/services/XXX
```

## 关联章节

- **03-gitops/overview**：GitOps 总览
- **03-gitops/argocd**：ArgoCD 对比
- **03-gitops/progressive-delivery**：Flagger 渐进式发布
- **04-release/canary**：金丝雀发布策略

## 一句话总结

> **Flux = GitOps-native 框架**。**何时用：纯 GitOps 团队 / 不需要 UI / 与 Prometheus 深度集成**。**何时不用：需要 UI / 多租户 / 团队习惯 ArgoCD**。
""",

"03-gitops/progressive-delivery.md": """---
title: 渐进式发布
---

# 渐进式发布

渐进式发布（Progressive Delivery）= 金丝雀 + 蓝绿 + A/B 测试的自动化实现。本章梳理主流工具 Flagger 与 Argo Rollouts。

## 一句话总结

> **渐进式发布 = 自动化的金丝雀/蓝绿/A/B**。**核心工具：Flagger（Flux 生态）+ Argo Rollouts（ArgoCD 生态）**。**价值：发布自动化 + 自动回滚 + 度量驱动决策**。

---

## Flagger（Flux 生态）

```yaml
# Canary 资源
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: my-app
  namespace: my-app
spec:
  provider: istio
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app

  metricTemplate:
    - name: request-success-rate
      provider: prometheus
      query: |
        sum(rate(istio_requests_total{destination_service=~"my-app.*",response_code!~"5.."}[2m]))
        /
        sum(rate(istio_requests_total{destination_service=~"my-app.*"}[2m]))

  analysis:
    interval: 30s
    threshold: 5       # 连续 5 次失败就回滚
    maxWeight: 50      # 最大 50% 流量
    stepWeight: 5      # 每步 5%
    steps:
      - setWeight: 5
      - pause: { duration: 2m }
      - setWeight: 25
      - pause: { duration: 2m }
      - setWeight: 50
```

## Argo Rollouts（ArgoCD 生态）

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 5
  strategy:
    canary:
      canaryService: my-app-canary
      stableService: my-app-stable
      trafficRouting:
        istio:
          virtualService:
            name: my-app-vsvc
      steps:
        - setWeight: 5
        - pause: { duration: 10m }
        - setWeight: 25
        - pause: { duration: 10m }
        - setWeight: 50
        - pause: { duration: 10m }

      analysis:
        templates:
          - templateName: success-rate
        args:
          - name: service-name
            value: my-app

---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  metrics:
    - name: success-rate
      interval: 30s
      successCondition: result >= 0.95
      failureLimit: 3
      provider:
        prometheus:
          query: |
            sum(rate(http_requests_total{service="my-app",code!~"5.."}[2m]))
            /
            sum(rate(http_requests_total{service="my-app"}[2m]))
```

## Flagger vs Argo Rollouts

| 维度 | Flagger | Argo Rollouts |
|------|---------|---------------|
| **生态** | Flux | ArgoCD |
| **Provider** | Istio / Linkerd / App Mesh / Nginx / Gloo / Contour | Istio / Nginx / ALB / SMI |
| **CRD** | Canary | Rollout / AnalysisTemplate |
| **配置复杂度** | 中（YAML 多） | 低（可视化插件强） |
| **实验功能** | A/B 测试 | A/B 测试 + 蓝绿 + 金丝雀 |
| **Kubectl 插件** | 无 | 有（argo-rollouts kubectl plugin） |
| **活跃度** | 中 | 高 |

## 度量驱动决策

```yaml
# 度量维度（决定发布是否继续）
- request-success-rate: 成功率 > 95%
- request-duration-p99: P99 延迟 < 500ms
- error-budget: 错误预算未耗尽
- custom-metrics: 业务指标（CTR / 转化率）

# 失败响应
- 自动 abort（停止发布）
- 自动回滚（切回 stable）
- 通知 oncall
```

## 关联章节

- **04-release/overview**：发布策略总览
- **04-release/canary**：金丝雀原理
- **03-gitops/argocd**：ArgoCD + Argo Rollouts 完整链路

## 一句话总结

> **渐进式发布 = 工具化的发布策略**。**何时用：关键服务 / 用户可感知的变更 / 算法更新**。**何时不用：内部工具 / 后台 job / 一次性脚本**。
""",

# ============ 04-release (4 stubs) ============
"04-release/blue-green.md": """---
title: 蓝绿部署
---

# 蓝绿部署 (Blue-Green)

蓝绿部署是经典的零停机发布策略，同时维护两套环境（旧=blue，新=green），通过切换流量实现秒级回滚。

## 一句话总结

> **蓝绿 = 流量切换 + 秒级回滚**。**核心：两套等价环境 + Router/LB 切换**。**适用：大版本 / 数据库 schema 变更 / 风险敏感**。**代价：资源 2 倍**。

---

## 工作流

```
时间线：
T0: blue=v1.0（生产），green=v2.0（部署完成但无流量）
T1: Router 切到 green（v2.0 接收 100% 流量）
T2: green=v2.0（生产），blue=v1.0（保留 7 天）
T3: blue 销毁

故障响应：
T1 + 5min: green 错误率飙升
T1 + 6min: Router 切回 blue（秒级回滚）
```

## K8s 实现（Service selector 切换）

```yaml
# blue（旧版本）
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
      version: blue
  template:
    metadata:
      labels:
        app: my-app
        version: blue
    spec:
      containers:
        - name: my-app
          image: my-app:v1.0
---
# green（新版本，先不接流量）
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
      version: green
  template:
    metadata:
      labels:
        app: my-app
        version: green
    spec:
      containers:
        - name: my-app
          image: my-app:v2.0
---
# Service（流量切换 = 改一行 selector）
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  selector:
    app: my-app
    version: green   # 切回 blue 就是改这一行
  ports:
    - port: 80
      targetPort: 8080
```

## Argo Rollouts 实现

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 5
  strategy:
    blueGreen:
      activeService: my-app-active
      previewService: my-app-preview
      autoPromotionEnabled: false   # 手动 promote
      scaleDownDelaySeconds: 600    # blue 保留 10 分钟
```

## 数据库 schema 变更的兼容

```sql
-- 蓝绿场景：DB schema 必须前后兼容

-- 阶段 1：新增字段（双写）
ALTER TABLE users ADD COLUMN new_email TEXT;

-- 阶段 2：旧代码读 old email 写 old + new
-- 阶段 3：新代码读 new email 写 new
UPDATE users SET new_email = email WHERE new_email IS NULL;
ALTER TABLE users ALTER COLUMN new_email SET NOT NULL;

-- 阶段 4：删除旧字段（需要所有实例都升级后才能执行）
ALTER TABLE users DROP COLUMN email;
```

## 适用 vs 不适用

```
✅ 适用
- 大版本变更（v1 → v2）
- 数据库 schema 不兼容变更
- 风险敏感（金融 / 医疗）
- 资源相对充足

❌ 不适用
- 资源敏感（成本）
- 有状态服务（DB 自身无法蓝绿）
- 长期维护两套环境成本高
- 频繁小版本发布（用金丝雀更经济）
```

## 关联章节

- **04-release/overview**：5 大发布策略对比
- **04-release/canary**：金丝雀发布
- **04-release/rollback**：回滚机制

## 一句话总结

> **蓝绿 = 最保险的发布策略**。**优势：秒级回滚 / 完整隔离**。**劣势：资源 2 倍 / DB schema 兼容挑战**。
""",

"04-release/canary.md": """---
title: 金丝雀发布
---

# 金丝雀发布 (Canary)

金丝雀发布源自矿井的金丝雀比喻：新版本先接小比例流量（5%），观察无异常后逐步扩大（25% → 50% → 100%）。

## 一句话总结

> **金丝雀 = 渐进式放量**。**核心：小流量试错 + 监控驱动 + 自动回滚**。**适用：算法更新 / 性能优化 / 用户可感知的变更**。**代价：需要 Service Mesh / Ingress 支持按权重路由**。

---

## 工作流

```
T0: v1.0 = 100%（生产）
T1: v2.0 = 5%（观察 10 分钟）
T2: v2.0 = 25%（观察 10 分钟）
T3: v2.0 = 50%（观察 10 分钟）
T4: v2.0 = 100%（v1.0 退役）
```

## Istio VirtualService 实现

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-app
spec:
  hosts:
    - my-app
  http:
    - route:
        - destination:
            host: my-app
            subset: v1
          weight: 95
        - destination:
            host: my-app
            subset: v2
          weight: 5
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: my-app
spec:
  host: my-app
  subsets:
    - name: v1
      labels: { version: v1 }
    - name: v2
      labels: { version: v2 }
```

## Argo Rollouts 实现

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 10
  strategy:
    canary:
      steps:
        - setWeight: 5
        - pause: { duration: 10m }
        - setWeight: 25
        - pause: { duration: 10m }
        - setWeight: 50
        - pause: { duration: 10m }
        - setWeight: 100
      canaryService: my-app-canary
      stableService: my-app-stable
      trafficRouting:
        istio:
          virtualService:
            name: my-app-vsvc
```

## Nginx Ingress 实现（按 Header）

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "5"
    nginx.ingress.kubernetes.io/canary-by-header: "X-Canary"
    nginx.ingress.kubernetes.io/canary-by-header-value: "always"
spec:
  rules:
    - host: my-app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app-stable
                port:
                  number: 80
```

```bash
# 内部测试
curl -H "X-Canary: always" https://my-app.example.com
```

## 自动回滚条件

```yaml
# Argo Rollouts Analysis
analysis:
  templates:
    - templateName: error-rate
  args:
    - name: service-name
      value: my-app

---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate
spec:
  metrics:
    - name: error-rate
      interval: 30s
      successCondition: result < 0.01   # 错误率 < 1%
      failureLimit: 3                   # 连续 3 次失败回滚
      provider:
        prometheus:
          query: |
            sum(rate(http_requests_total{service="{{args.service-name}}",code=~"5.."}[2m]))
            /
            sum(rate(http_requests_total{service="{{args.service-name}}"}[2m]))
```

## 度量选择

```yaml
# 必备：技术指标
- error_rate: HTTP 5xx 比例
- p99_latency: P99 延迟
- throughput: QPS（不应下降过多）

# 高级：业务指标
- ctr: 点击率（推荐系统）
- conversion_rate: 转化率（电商）
- retention: 留存（功能上线）

# 来源
- Prometheus（最常用）
- DataDog
- 自建 metrics API
```

## 关联章节

- **04-release/overview**：5 大发布策略
- **04-release/blue-green**：蓝绿对比
- **03-gitops/progressive-delivery**：渐进式发布工具
- **04-release/feature-flag**：Feature Flag 互补

## 一句话总结

> **金丝雀 = 发布策略的事实标准**。**何时用：算法 / 性能 / 用户可感知的变更**。**何时不用：内部工具 / 后台 job / 一次性脚本（蓝绿或滚动更简单）**。
""",

"04-release/feature-flag.md": """---
title: Feature Flag
---

# Feature Flag（特性开关）

Feature Flag 是代码内的开关，通过配置中心动态启用 / 关闭 / 灰度功能，不需要重新部署。

## 一句话总结

> **Feature Flag = 配置驱动的代码开关**。**核心：代码内置 + 配置中心 + 用户分群**。**适用：新功能试用 / 多变体 / Kill Switch**。**挑战：Flag 治理（清理过期 Flag）**。

---

## 4 大使用场景

```
1. Kill Switch（紧急关闭）
   新功能出问题，秒级关闭，不需要回滚

2. Canary Release（用户分群）
   内部用户 / Beta 用户先体验，逐步放量

3. A/B Testing（多变体）
   对比不同实现的转化率 / 性能

4. Trunk-Based Development
   主干开发，Flag 控制未完成功能
```

## 自建 Feature Flag 模式

```typescript
// 简单实现：基于配置文件 + 缓存
import { featureFlags } from './flags';

async function checkout(req: Request) {
    if (await featureFlags.isEnabled('new-checkout', {
        userId: req.user.id,
        attributes: { country: req.user.country },
    })) {
        return newCheckoutFlow(req);
    } else {
        return legacyCheckoutFlow(req);
    }
}
```

```typescript
// flags.ts
const flags: Record<string, RolloutStrategy> = {
    'new-checkout': {
        type: 'percentage',
        percentage: 10,             // 10% 用户
        userWhitelist: [1, 2, 3],   // 内部用户强制开启
    },
    'beta-feature': {
        type: 'attribute',
        attribute: 'user.tier',
        values: ['beta', 'enterprise'],
    },
};

// 缓存（避免每次请求查 DB）
const cache = new Map<string, { value: boolean; expires: number }>();

async function isEnabled(flag: string, context: Context): Promise<boolean> {
    const key = `${flag}:${context.userId}`;
    const cached = cache.get(key);
    if (cached && cached.expires > Date.now()) {
        return cached.value;
    }

    const value = evaluate(flags[flag], context);
    cache.set(key, { value, expires: Date.now() + 60000 });
    return value;
}
```

## 商业方案

| 方案 | 特点 |
|------|------|
| **LaunchDarkly** | SaaS / 功能完整 / 价格高 |
| **Unleash** | 开源 / 自托管 / 功能丰富 |
| **Split.io** | 企业级 / A/B 测试集成 |
| **Statsig** | 新兴 / 现代化 / 实验功能强 |
| **自建** | 简单场景 / 节省成本 |

## Unleash 自托管示例

```typescript
import { UnleashClient } from 'unleash-proxy-client';

const unleash = new UnleashClient({
    url: 'https://unleash.example.com/api/frontend',
    clientKey: 'xxx',
    appName: 'my-app',
});

unleash.on('ready', () => {
    if (unleash.isEnabled('new-checkout')) {
        // 启用
    }
});
```

```yaml
# Unleash Toggle 配置（Web UI）
name: new-checkout
type: gradual-rollout
rollout: 100%           # 启用 100%
stickiness: userId       # 按用户稳定分桶
```

## Flag 治理

```
# 1. Flag 生命周期
created → in-use → (deprecated) → removed

# 2. Owner 制度
每个 Flag 必须有 owner（团队或个人）

# 3. 过期时间
创建时强制设置过期时间（如 90 天），过期前提醒

# 4. 死代码清理
定期 grep 未使用 Flag，PR 移除

# 5. 度量
- Flag 总数（越少越好）
- Flag 存活时间
- 死代码比例
```

## 反模式

```
❌ 反模式 1：Flag 嵌套（if(flagA) { if(flagB) {} }）
✅ 正确：扁平 Flag，避免组合爆炸

❌ 反模式 2：长期 Flag（超过 6 个月还在）
✅ 正确：定期清理，过期前 promote 或删除

❌ 反模式 3：Flag 没有 owner
✅ 正确：每个 Flag 都有 owner，Slack 提醒

❌ 反模式 4：测试不覆盖 Flag 分支
✅ 正确：Flag 各分支都要测（包括灰度比例）

❌ 反模式 5：滥用 Flag 做权限控制
✅ 正确：权限用 RBAC，Flag 做产品功能
```

## 关联章节

- **04-release/overview**：5 大发布策略
- **04-release/canary**：金丝雀发布
- **04-release/blue-green**：蓝绿发布

## 一句话总结

> **Feature Flag = 产品发布的瑞士军刀**。**何时用：频繁发布 / 多变体 / 需要 Kill Switch**。**何时不用：变更极少 / 团队小 / 治理能力弱**。
""",

"04-release/rollback.md": """---
title: 回滚机制
---

# 回滚机制

发布失败的快速恢复能力，决定 MTTR（Mean Time To Recover）。本章梳理回滚的 4 大要素与最佳实践。

## 一句话总结

> **回滚 = 流量切换 + DB 回退 + 配置回退 + 通知**。**目标：MTTR < 5 分钟（生产事故标准）**。**反模式：靠手工人肉回滚**。

---

## 4 大回滚要素

```
1. 流量切换
   - 蓝绿：秒级（改 Service selector）
   - 金丝雀：分钟级（Argo Rollouts abort）
   - Feature Flag：秒级（关开关）

2. 数据库回退
   - 前向兼容：旧版本代码能读新版本 schema
   - 反向迁移：DB migration 必须有 down()
   - 双写期：新旧版本都写新 schema

3. 配置回退
   - Helm values 回到上一个 Git commit
   - ArgoCD 自动同步

4. 通知
   - 失败自动 @oncall
   - Slack / PagerDuty / Lark
```

## Argo Rollouts 一键回滚

```bash
# 中止金丝雀并回滚
kubectl argo rollouts abort my-app

# 手动回滚到指定版本
kubectl argo rollouts undo my-app --to-revision=3

# 查看历史
kubectl argo rollouts history my-app
```

## GitOps 自动回滚

```yaml
# ArgoCD 检测到失败 sync 自动回滚
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  syncPolicy:
    automated:
      selfHeal: true   # 集群漂移自动修复
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

```bash
# 手动回滚（git revert + 自动 sync）
git revert HEAD
git push
# ArgoCD 自动检测 + sync + 回滚
```

## 数据库 migration 安全回滚

```sql
-- 1. 永远写 forward + backward
-- Up:
ALTER TABLE users ADD COLUMN new_email TEXT;
UPDATE users SET new_email = email;
ALTER TABLE users ALTER COLUMN new_email SET NOT NULL;

-- Down:
ALTER TABLE users ALTER COLUMN new_email DROP NOT NULL;
UPDATE users SET email = new_email;
ALTER TABLE users DROP COLUMN new_email;

-- 2. 大表 ALTER 异步（避免锁表）
-- pt-online-schema-change / gh-ost / pg_repack
gh-ost --alter="ADD COLUMN new_email TEXT" \\
  --host=db --table=users --alter-foreign-keys-method=auto

-- 3. 双写期（数据迁移）
-- 阶段 1：旧代码写 old + new
-- 阶段 2：新代码读 new，写 new
-- 阶段 3：删除旧字段
```

## 回滚预案检查清单

```
发布前：
  ✅ 数据库 migration 有 down
  ✅ 上一版本镜像保留（不删除）
  ✅ 配置有 Git 历史
  ✅ oncall 值班明确
  ✅ 回滚 RunBook 文档化
  ✅ 演练过（季度至少 1 次）

发布中：
  ✅ 监控大盘实时观察
  ✅ 异常指标触发 abort
  ✅ oncall 待命
  ✅ 通讯渠道畅通

发布后：
  ✅ 7 天观察期
  ✅ 旧版本保留可快速回滚
  ✅ 故障复盘
```

## MTTR 优化

```yaml
# 1. 自动化（避免人肉操作）
- 告警 → 自动 abort（Argo Rollouts Analysis）
- 自动回滚（selfHeal）
- 通知 oncall（PagerDuty）

# 2. 可观测性
- 发布状态看板
- 异常告警（错误率 / 延迟 / 业务指标）
- 链路追踪（TraceID 贯穿全链路）

# 3. 演练
- Chaos Engineering（Chaos Mesh / Litmus）
- 季度回滚演练
- GameDay 活动
```

## 关联章节

- **04-release/overview**：发布策略总览
- **04-release/blue-green**：蓝绿秒级回滚
- **04-release/canary**：金丝雀自动回滚
- **05-cicd-observability/dora-metrics**：MTTR 作为 DORA 度量

## 一句话总结

> **回滚 = 发布能力的天花板**。**目标：MTTR < 5 分钟**。**核心：自动化 + 预案 + 演练**。
""",

# ============ 05-cicd-observability (3 stubs) ============
"05-cicd-observability/dora-metrics.md": """---
title: DORA Metrics
---

# DORA Metrics

DORA（DevOps Research & Assessment）是 Google 与 DORA 团队发布的研发效能度量框架，4 个核心指标被业界广泛采用。

## 一句话总结

> **DORA = 研发效能的事实标准**。**4 大指标：部署频率 / 变更前置时间 / 变更失败率 / 恢复时间**。**价值：跨团队对比 + 识别瓶颈 + 行业 benchmark**。

---

## 4 大核心指标

```yaml
# 1. Deployment Frequency（部署频率）
# 含义：单位时间内部署到生产的次数
# 行业 benchmark（Accelerate 2023）：
#   - 精英：on-demand（每天多次）
#   - 高：每周到每天
#   - 中：每月到每周
#   - 低：每月以下

# 2. Lead Time for Changes（变更前置时间）
# 含义：commit 到 production 的时间
# 行业 benchmark：
#   - 精英：< 1 小时
#   - 高：1 天 - 1 周
#   - 中：1 周 - 1 月
#   - 低：> 1 月

# 3. Change Failure Rate（变更失败率）
# 含义：导致生产故障的变更比例
# 行业 benchmark：
#   - 精英：0-15%
#   - 高：16-30%
#   - 中：31-45%
#   - 低：46-60%

# 4. Mean Time to Recover / MTTR（恢复时间）
# 含义：从故障到恢复的时间
# 行业 benchmark：
#   - 精英：< 1 小时
#   - 高：< 1 天
#   - 中：< 1 周
#   - 低：> 1 周
```

## 数据采集

```python
# DORA metrics 计算示例（伪代码）
import pandas as pd

# 数据源
deploys = get_deployments()        # 来自 CI/CD 系统
incidents = get_incidents()         # 来自 PagerDuty
commits = get_commits()             # 来自 Git

# 1. Deployment Frequency
deploy_freq = deploys.groupby(deploys.timestamp.dt.date).size()
# 输出：每天 5 次

# 2. Lead Time for Changes
# commit → production 时间差
merged = commits.merge(deploys, on='commit_sha')
lead_time = (merged.deploy_time - merged.commit_time).dt.total_seconds() / 3600
# 输出：中位数 4 小时

# 3. Change Failure Rate
# 假设 100 次部署中 5 次导致 P0/P1 故障
failure_rate = len(incidents) / len(deploys)
# 输出：5%

# 4. MTTR
# 从 incident 开始到恢复
mttr = (incidents.resolved_time - incidents.started_time).dt.total_seconds() / 3600
# 输出：中位数 30 分钟
```

## 工具实现

```yaml
# 1. Four Keys（Google 开源项目）
# GitHub: GoogleCloudPlatform/fourkeys
# 自动采集 4 个指标 + Grafana 看板

# 2. LinearB / Jellyfish
# 商业 SaaS，自带 benchmark

# 3. 自建（Prometheus + Grafana）
# 用 GitHub Actions API + ArgoCD API 采集
```

## 行动映射

```yaml
deployment_frequency_low:
  根因：CI 慢 / 部署复杂 / 团队规模过大
  行动：
    - CI 缓存 + 并行（参考 01-pipeline/best-practices）
    - 拆分大 Pipeline
    - 引入 GitOps 降低部署摩擦
    - 团队拓扑调整（康威定律）

lead_time_long:
  根因：code review 慢 / 测试慢 / PR 过大
  行动：
    - PR 模板 + 拆分
    - 自动化测试覆盖率
    - Code review SLA（24 小时内 first review）
    - Trunk-based development

change_failure_rate_high:
  根因：测试不足 / 灰度不够 / 监控缺位
  行动：
    - 测试金字塔（unit / integration / e2e）
    - 金丝雀发布（04-release/canary）
    - Feature Flag（04-release/feature-flag）
    - SLO 驱动（observability/）

mttr_long:
  根因：回滚复杂 / 监控盲区 / oncall 不熟
  行动：
    - 蓝绿部署（秒级回滚）
    - 完善告警链路
    - RunBook 文档化
    - GameDay 演练
```

## 关联章节

- **05-cicd-observability/overview**：流水线可观测性总览
- **05-cicd-observability/flaky-test**：失败率根因之一
- **05-cicd-observability/pipeline-monitoring**：Pipeline 性能
- **observability/**：SLO 体系

## 一句话总结

> **DORA = 度量研发效能的金标准**。**何时用：团队 / 组织级效能诊断 + 行业 benchmark**。**何时不用：开发者个人绩效（避免副作用）**。
""",

"05-cicd-observability/flaky-test.md": """---
title: Flaky Test
---

# Flaky Test

Flaky Test（不稳定测试）= 同一份代码、同一个测试，有时通过有时失败。这是研发团队的"隐形税"。

## 一句话总结

> **Flaky Test = 团队的隐形杀手**。**影响：CI 时间翻倍 + 信任崩溃 + 真 bug 被掩盖**。**治理：分类 + 修复 + quarantine + 根因分析**。

---

## Flaky Test 的危害

```
1. 开发者信任崩溃
   "测试又挂了，重跑吧" → 失去信号

2. CI 时间翻倍
   auto-retry 机制 → 实际耗时 × 2-3

3. 真 bug 被掩盖
   Flaky + 新 bug = 都是红，难以分辨

4. 团队 culture 损伤
   "测试不可信" → 失去测试投入动力

5. 部署阻塞
   Required check 不稳定 → PR 阻塞
```

## 常见根因（按比例）

```yaml
# 1. 异步时序问题（40%）
# 测试假设 A 在 B 之前完成，实际并发
test('user flow', async () => {
    const user = await createUser();      // 不等待
    const order = await createOrder(user); // user 还没 ready
    expect(order.userId).toBe(user.id);
});

# 2. 时间相关（20%）
# Date.now() / setTimeout / 缓存 TTL
test('cache expires', () => {
    cache.set('key', 'value', 60);  // 假设 60 秒
    sleep(61);
    expect(cache.get('key')).toBeNull();
});

# 3. 共享状态（15%）
# 测试间共享 DB / 文件 / 全局变量
let user;
beforeAll(() => {
    user = createUser();  // 别的测试也用 user
});

# 4. 网络依赖（10%）
# 真实 HTTP 调用 / DNS / TLS 握手
test('api', async () => {
    const res = await fetch('https://api.real.com/users');
    expect(res.status).toBe(200);
});

# 5. 并发 / 竞态（10%）
# 多线程 / worker / 微服务并发
test('concurrent', async () => {
    const promises = [createOrder(), createOrder(), createOrder()];
    await Promise.all(promises);
    expect(orders.length).toBe(3);  // 可能少了
});

# 6. 环境差异（5%）
# OS / Node 版本 / 时区 / locale
```

## 治理流程

```
发现 → 分类 → 修复 / quarantine → 监控 → 反思

1. 发现
   - CI 报告
   - 开发者主动标记 flaky
   - 自动检测（re-run 后状态变化）

2. 分类
   - Network（外部依赖）
   - Async（时序）
   - State（共享）
   - Time（时间相关）
   - Env（环境）
   - Concurrency（并发）

3. 修复 vs Quarantine
   - 修复优先级：高频 + 阻塞 PR
   - Quarantine：暂时隔离，限期修复

4. 监控
   - Flaky Rate（每个测试）
   - Quarantine 数量
   - Quarantine 时间（最长多久）

5. 反思
   - 每月复盘
   - 写 RunBook
   - 培训团队
```

## Quarantine 实现

```typescript
// Jest Quarantine Plugin
// 标记 flaky 但不阻塞 PR
test.flaky('complex flow', async () => {
    // 跳过：标记为 known-flaky
});

test.skip('complex flow', async () => {
    // 跳过：阻塞但标记原因
});
```

```python
# pytest-flaky
@pytest.mark.flaky(retries=3, delay=1)
def test_complex_flow():
    pass

# pytest -p no:flaky  # 禁用 flaky 装饰器，强制修复
```

```yaml
# GitHub Actions
- name: Detect flaky
  run: |
    npm test
    if [ $? -ne 0 ]; then
      npm test  # 重跑
      if [ $? -ne 0 ]; then
        echo "::warning::Test failed twice, marking flaky"
        exit 0  # 不阻塞
      fi
    fi
```

## 修复模式

```typescript
// 反模式 1：固定等待
test('flow', async () => {
    await sleep(1000);  // ❌ 不可靠
});

// 正确：显式等待
test('flow', async () => {
    await waitFor(() => user.isReady);
});

// 反模式 2：共享状态
let user;
beforeAll(() => {
    user = createUser();
});

// 正确：每个测试独立 setup
beforeEach(() => {
    user = createUser();
});

// 反模式 3：真实网络
test('api', async () => {
    await fetch('https://api.real.com');
});

// 正确：mock
jest.mock('axios');
axios.get.mockResolvedValue({ data: mockData });
```

## 关联章节

- **05-cicd-observability/overview**：流水线可观测性总览
- **01-pipeline/best-practices**：Pipeline 优化
- **observability/**：监控 + 告警体系

## 一句话总结

> **Flaky Test = 必须治理的工程债**。**关键指标：Flaky Rate < 1%、Quarantine 时长 < 30 天**。**行动：分类 + 修复 + 监控 + 反思**。
""",

"05-cicd-observability/pipeline-monitoring.md": """---
title: 流水线监控
---

# 流水线监控

CI/CD Pipeline 本身的运行状态监控：duration / success rate / queue time / cache hit rate。

## 一句话总结

> **Pipeline 监控 = Pipeline 自身的 SRE**。**核心指标：duration / success rate / queue time / cache hit rate**。**价值：发现瓶颈 + SLA 保障 + 成本优化**。

---

## 4 大核心指标

```yaml
# 1. Pipeline Duration
# 关键路径耗时（PR 到反馈）
p50: 5 分钟
p90: 15 分钟
p99: 30 分钟
目标：p90 < 10 分钟

# 2. Success Rate（按分支 / 服务）
main: > 95%
feature: > 80%（允许新代码有问题）
目标：main > 95%

# 3. Queue Time（等待 runner 时间）
p90: < 1 分钟
目标：< 30 秒
瓶颈信号：runner 不足

# 4. Cache Hit Rate
dep cache: > 90%
docker cache: > 80%
目标：> 85%
```

## Prometheus 采集

```yaml
# GitHub Actions Exporter
# https://github.com/cpanato/github_actions_exporter
scrape_configs:
  - job_name: github-actions
    static_configs:
      - targets: ['github-actions-exporter:9101']
```

```promql
# Pipeline duration p90
histogram_quantile(0.9,
  rate(github_actions_workflow_duration_seconds_bucket{workflow="CI"}[5m])
)

# Success rate
sum(rate(github_actions_workflow_completed_total{conclusion="success"}[1h]))
/
sum(rate(github_actions_workflow_completed_total[1h]))
```

## ArgoCD 指标

```promql
# 同步状态
argocd_app_sync_status{namespace="argocd"}

# 漂移检测（Git vs 实际）
argocd_app_sync_status{sync_status="OutOfSync"}

# 健康状态
argocd_app_health_status{health_status="Healthy"}
```

## Jenkins 指标

```yaml
# Prometheus Plugin（自动暴露）
# /prometheus/ 端点

# 关键指标
- jenkins_job_duration_seconds
- jenkins_job_result_total
- jenkins_queue_size
- jenkins_node_executors_available
```

## GitLab CI 指标

```yaml
# GitLab Prometheus exporter
# https://docs.gitlab.com/ee/administration/monitoring/prometheus/

# 关键指标
- gitlab_ci_pipeline_duration_seconds
- gitlab_ci_pipeline_status
- gitlab_ci_runner_jobs
```

## 告警规则

```yaml
# alertmanager rules
groups:
  - name: pipeline
    rules:
      - alert: PipelineSlow
        expr: |
            histogram_quantile(0.9,
              rate(github_actions_workflow_duration_seconds_bucket[5m])
            ) > 600
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Pipeline duration p90 > 10 minutes"

      - alert: PipelineFailureSpike
        expr: |
            sum(rate(github_actions_workflow_completed_total{conclusion="failure"}[1h]))
            /
            sum(rate(github_actions_workflow_completed_total[1h]))
            > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pipeline failure rate > 10%"

      - alert: RunnerQueueLong
        expr: github_actions_runner_queue_duration_seconds > 60
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Runner queue > 60 seconds"
```

## 优化行动

```yaml
duration_high:
  行动：
    - 启用 cache（依赖 + Docker layer）
    - 并行 job
    - 拆分大 Pipeline
    - 升级 runner（更快 CPU / IO）

success_rate_low:
  行动：
    - 治理 Flaky Test
    - 增加 retry
    - 修复根本性 bug（可能是依赖问题）

queue_time_long:
  行动：
    - 增加 runner 数量
    - 优化 job 调度（大 job 拆小）
    - 自建 runner

cache_hit_low:
  行动：
    - 检查 cache key 是否过细
    - 检查 cache 失效原因
    - 增大 cache 容量
```

## 关联章节

- **05-cicd-observability/overview**：可观测性总览
- **05-cicd-observability/dora-metrics**：DORA 度量
- **05-cicd-observability/flaky-test**：失败率根因
- **observability/**：通用可观测性体系

## 一句话总结

> **Pipeline 监控 = Pipeline SRE**。**目标：duration p90 < 10min / success > 95% / queue < 30s / cache > 85%**。**工具：各平台 Exporter + Prometheus + 告警**。
""",

# ============ 06-best-practices (4 stubs) ============
"06-best-practices/caching.md": """---
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
RUN --mount=type=cache,target=/root/.npm \\
    --mount=type=bind,source=package-lock.json,target=package-lock.json \\
    npm ci

COPY . .
RUN --mount=type=cache,target=/app/.next/cache \\
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
""",

"06-best-practices/secure-pipeline.md": """---
title: 安全 Pipeline
---

# 安全 Pipeline

CI/CD Pipeline 本身是攻击面最大的目标之一（拥有生产部署权限）。本章梳理 Pipeline 全链路的 8 大安全措施。

## 一句话总结

> **Pipeline 安全 = SLSA + 最小权限 + 可审计**。**核心：Secret 管理 / OIDC 联邦 / SBOM / 镜像签名 / 制品完整性**。

---

## 8 大安全措施

```
1. Secret 管理（HashiCorp Vault / AWS Secrets Manager）
2. OIDC 联邦（消除 long-lived Secret）
3. SBOM 生成（CycloneDX / SPDX）
4. 镜像签名（Cosign / Notary）
5. 依赖扫描（Snyk / Trivy / npm audit）
7. SLSA Level 3（来源可追溯）
8. 最小权限 Runner（专用 runner 隔离）
```

## 1. Secret 管理

```yaml
# ❌ 反模式：Secret 明文写在 YAML
env:
  AWS_ACCESS_KEY: AKIAIOSFODNN7EXAMPLE
  AWS_SECRET_KEY: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# ✅ 正确：使用 Secret Manager
env:
  AWS_ROLE_ARN: arn:aws:iam::123456789012:role/GitHubActionsRole
  # AWS 自动生成临时凭证，无 long-lived Secret
```

## 2. OIDC 联邦

```yaml
# GitHub Actions OIDC
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
      aws-region: us-east-1
```

```json
// IAM Role Trust Policy
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:sub": "repo:myorg/myapp:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

```yaml
# GitLab CI OIDC
deploy:
  id_tokens:
    GITLAB_OIDC_TOKEN:
      aud: https://vault.example.com
  script:
    - export VAULT_TOKEN=$(vault login -method=oidc role=my-role)
    - vault kv get -format=json secret/myapp
```

## 3. SBOM 生成

```yaml
# GitHub Actions 生成 SBOM
- name: Generate SBOM
  uses: anchore/sbom-action@v0
  with:
    format: cyclonedx-json
    artifact-name: sbom.json

# 上传到 Dependency Track / Grype
- uses: anchore/scan-action@v3
  with:
    sbom: sbom.json
    fail-build: true
    severity-cutoff: high
```

## 4. 镜像签名（Cosign）

```bash
# 构建并签名
cosign sign --key cosign.key myapp:v1.0.0

# 部署前验证
cosign verify --key cosign.pub myapp:v1.0.0

# K8s 强制验证（policy-controller）
kubectl apply -f - <<EOF
apiVersion: policy.sigstore.dev/v1beta1
kind: ClusterImagePolicy
metadata:
  name: my-policy
spec:
  images:
    - glob: "registry.example.com/**"
  authorities:
    - keyless:
        url: https://fulcio.sigstore.dev
        identities:
          - issuer: "https://token.actions.githubusercontent.com"
            subject: "https://github.com/myorg/*"
EOF
```

## 5. 依赖扫描

```yaml
# Snyk
- uses: snyk/actions/node@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  with:
    args: --severity-threshold=high

# Trivy（容器 + IaC）
- uses: aquasecurity/trivy-action@master
  with:
    image-ref: myapp:v1.0.0
    severity: 'CRITICAL,HIGH'
    exit-code: '1'
    ignore-unfixed: true

# npm audit
- run: npm audit --audit-level=high
```

## 6. Pipeline 自身加固

```yaml
# 1. PR 触发（不能直接 push main）
on:
  pull_request:
  push:
    branches: [main]

# 2. 限制环境变量可见性
env:
  PUBLIC_VAR: value       # 暴露给 fork PR
  SECRET_VAR: ${{ secrets.X }}  # 不暴露给 fork PR

# 3. 第三方 action 锁定版本
- uses: actions/checkout@v4.1.7  # 不用 @v4（防止供应链攻击）
  # 或 hash
- uses: actions/checkout@8e5e7c5c8b36f4fa9bb1e0a5e9a8c8b8b8b8b8b8
```

## 7. SLSA Level 3

```yaml
# SLSA = Supply-chain Levels for Software Artifacts
# Level 3 要求：
# - 构建过程可追溯
# - 构建环境隔离
# - 产物签名 + provenance

# GitHub Actions 自动生成 provenance
- uses: actions/attest-build-provenance@v1
  with:
    subject-name: myapp
    subject-digest: sha256:abc...
```

## 8. 最小权限 Runner

```yaml
# 1. 自托管 Runner 隔离网络
runs-on: [self-hosted, isolated, prod-deploy]

# 2. 不同环境用不同 Runner
- production: 仅部署，不能访问源码
- staging: 可访问源码，可部署 staging
- ci: 可访问所有仓库

# 3. Runner 定期轮换 Token
```

## 关联章节

- **06-best-practices/secrets-management**：Secret 管理深度
- **06-best-practices/oidc-federation**：OIDC 联邦
- **04-network/tls-pki** (security)：TLS / PKI

## 一句话总结

> **Pipeline 安全 = 8 大措施闭环**。**优先级：Secret 管理 → OIDC → SBOM → 签名 → 依赖扫描 → SLSA → Runner 隔离**。
""",

"06-best-practices/secrets-management.md": """---
title: Secret 管理
---

# Secret 管理

Secret（密钥 / 凭证 / Token）是 Pipeline 中最敏感的资源。本章梳理 Secret 全生命周期管理。

## 一句话总结

> **Secret 管理 = Vault 化 + OIDC 化 + 轮换化**。**核心：避免明文 + 最小权限 + 自动轮换 + 审计追溯**。

---

## 4 大原则

```
1. 永不提交到 Git
   - Pre-commit hook 检测
   - GitHub Secret Scanning 自动报警

2. 最小权限
   - 每个 Secret 只授予必要权限
   - 短期凭证（OIDC / STS）优于长期

3. 自动轮换
   - 数据库密码 90 天
   - API Token 60 天
   - SSH Key 180 天

4. 完整审计
   - 谁 + 何时 + 用哪个 Secret + 做了什么
   - 失败告警（异常访问）
```

## Secret 类型与方案

| 类型 | 推荐方案 |
|------|----------|
| **数据库密码** | HashiCorp Vault + 动态凭证 |
| **云厂商凭证** | OIDC / IAM Role（推荐）/ 短期 STS |
| **API Token** | Vault / 云厂商 Secret Manager |
| **SSH Key** | HashiCorp Vault SSH 签名 |
| **TLS 证书** | cert-manager + Vault PKI |
| **容器镜像 push** | Image Pull Secret（K8s）/ OIDC |

## HashiCorp Vault 集成

```bash
# Vault 启动（dev 模式）
vault server -dev

# 启用 K8s auth
vault auth enable kubernetes

# 配置 K8s auth
vault write auth/kubernetes/config \\
  kubernetes_host="https://k8s-api.example.com"

# 创建 Secret
vault kv put secret/myapp \\
  db_password=xxx \\
  api_key=yyy
```

```yaml
# Vault Agent Injector（Sidecar 自动注入）
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "myapp"
    vault.hashicorp.com/agent-inject-secret-db: "secret/data/myapp"
    vault.hashicorp.com/agent-inject-template-db: |
      {{- with secret "secret/data/myapp" -}}
      export DB_PASSWORD="{{ .Data.data.db_password }}"
      {{- end }}
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
    spec:
      serviceAccountName: myapp
      containers:
        - name: myapp
          image: myapp:v1.0
          env:
            - name: DB_PASSWORD
              value: /vault/secrets/db
```

## AWS Secrets Manager

```python
import boto3

client = boto3.client('secretsmanager')

# 读取
response = client.get_secret_value(SecretId='myapp/db')
password = response['SecretString']

# 自动轮换
response = client.rotate_secret(
    SecretId='myapp/db',
    RotationRules={'AutomaticallyAfterDays': 30}
)
```

## K8s Secret（最简方案）

```bash
# 创建
kubectl create secret generic myapp-secret \\
  --from-literal=db-password=xxx \\
  --from-literal=api-key=yyy

# 使用
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: myapp-secret
        key: db-password
```

```yaml
# External Secrets Operator（从 Vault/AWS 同步）
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: myapp-secret
spec:
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: myapp-secret
  data:
    - secretKey: db-password
      remoteRef:
        key: secret/myapp
        property: db_password
```

## Secret 扫描

```yaml
# GitHub Secret Scanning（自动）
# https://docs.github.com/en/code-security/secret-scanning

# Pre-commit hook（本地拦截）
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

```bash
# gitleaks（CI 拦截）
gitleaks detect --source . --verbose
```

## 轮换策略

```yaml
# 1. 数据库密码
- Vault 动态凭证：自动生成 + 自动撤销
- 传统方案：每 90 天强制轮换 + 应用启动重连

# 2. API Token
- 短期（< 1 小时）：OAuth / OIDC
- 中期（< 90 天）：Token 刷新机制
- 长期（> 90 天）：必须强制轮换

# 3. SSH Key
- 短期：Vault SSH 签名（每次登录新 Key）
- 长期：定期重生成
```

## 关联章节

- **06-best-practices/secure-pipeline**：Pipeline 安全
- **06-best-practices/oidc-federation**：OIDC 联邦
- **security/03-crypto/secret-management** (security)：Secret 管理安全

## 一句话总结

> **Secret 管理 = 全生命周期**。**关键：避免明文 + 短期凭证 + 自动轮换 + 审计追溯**。**推荐：OIDC + Vault + External Secrets Operator**。
""",

"06-best-practices/oidc-federation.md": """---
title: OIDC 联邦
---

# OIDC 联邦（CI/CD ↔ 云厂商）

OIDC 联邦让 CI/CD Pipeline（GitHub / GitLab）无需 long-lived Secret 就能访问云厂商（AWS / GCP / Azure），是现代 Secret 管理的最佳实践。

## 一句话总结

> **OIDC 联邦 = 无长期凭证的云访问**。**核心：JWT Token 交换临时 STS**。**优势：消除长期 Secret / 自动过期 / 细粒度权限**。

---

## 为什么需要 OIDC 联邦

```
传统方式（❌ 危险）
  GitHub Secret 中存 AWS_ACCESS_KEY
  问题：
  - Secret 泄露 = 永久凭证泄露
  - 权限过大（无法按 repo / branch 限制）
  - 轮换困难（需要手动更新）

OIDC 联邦（✅ 推荐）
  GitHub Actions → 申请 JWT → 换 AWS STS（1 小时有效）
  优势：
  - 无 long-lived Secret
  - 按 repo / branch / tag 精确控制
  - 自动过期
```

## GitHub Actions → AWS OIDC

```yaml
# 1. AWS 创建 OIDC Provider（一次性）
# IAM → Identity providers → Add provider
# Provider URL: token.actions.githubusercontent.com
# Audience: sts.amazonaws.com

# 2. 创建 IAM Role（Trust Policy 限制 repo/branch）
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:myorg/myapp:ref:refs/heads/main"
        }
      }
    }
  ]
}

# 3. Pipeline 使用
permissions:
  id-token: write   # 必须
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123:role/GitHubActionsRole
      aws-region: us-east-1
  - run: aws s3 ls   # 已认证
```

## GitLab CI → Vault OIDC

```yaml
# GitLab 生成 OIDC Token
deploy:
  id_tokens:
    GITLAB_OIDC_TOKEN:
      aud: https://vault.example.com
  script:
    - |
      export VAULT_TOKEN=$(vault login -method=oidc -token-only \\
        role=my-role \\
        jwt=$GITLAB_OIDC_TOKEN)
    - vault kv get secret/myapp
```

```hcl
# Vault Role 配置
vault write auth/oidc/role/my-role \\
  bound_audiences="https://vault.example.com" \\
  user_claim="user_email" \\
  policies="my-policy" \\
  ttl=1h \\
  max_ttl=4h
```

## GitHub Actions → GCP

```yaml
- id: auth
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: projects/123/locations/global/workloadIdentityPools/github/providers/github
    service_account: github-actions@myorg.iam.gserviceaccount.com
```

## GitHub Actions → Azure

```yaml
- uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    enable-OIDC: true
```

## 多云 / 多账号最佳实践

```yaml
# 1. 不同环境不同 Role
permissions:
  id-token: write

steps:
  - if: github.ref == 'refs/heads/main'
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::PROD:role/Deploy
  - if: github.ref == 'refs/heads/develop'
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::STAGING:role/Deploy

# 2. 跨账号（生产部署）
# main → Prod Account
# develop → Staging Account

# 3. GitOps 风格（OIDC + ArgoCD）
# CI 不直接部署，只更新 manifest
# ArgoCD 用 OIDC 拉取 secret
```

## 权限最小化设计

```yaml
# IAM Role Policy（生产部署）
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage"
      ],
      "Resource": "arn:aws:ecr:us-east-1:123:repository/myapp"
    },
    {
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster"
      ],
      "Resource": "arn:aws:eks:us-east-1:123:cluster/prod"
    }
  ]
}
```

## 常见误区

```
❌ 误区 1：OIDC 就能 100% 安全
✅ 正确：OIDC 消除了 long-lived Secret，但仍需 Trust Policy 限制

❌ 误区 2：Trust Policy 写宽（repo:* 任何分支）
✅ 正确：精确到 repo + branch（如 main）

❌ 误区 3：OIDC Role 给 AdministratorAccess
✅ 正确：最小权限（只给必要的 Action + Resource）

❌ 误区 4：OIDC Token 缓存复用
✅ 正确：每次 pipeline 重新申请，TTL 1 小时
```

## 关联章节

- **06-best-practices/secure-pipeline**：Pipeline 安全
- **06-best-practices/secrets-management**：Secret 管理
- **02-auth/oidc** (security)：OIDC 协议深度

## 一句话总结

> **OIDC 联邦 = 现代 Secret 管理的最佳实践**。**何时用：CI/CD 访问云资源 / 需要细粒度权限 / 想消除 long-lived Secret**。
""",

}  # end CONTENT


def main():
    """Write each CONTENT entry to its corresponding md file."""
    print(f"Total pages to generate: {len(CONTENT)}")
    written = 0
    for rel_path, content in CONTENT.items():
        full_path = os.path.join(DOCS_ROOT, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        written += 1
        print(f"  [{written}/{len(CONTENT)}] {rel_path}")
    print(f"\nGenerated: {written}/{len(CONTENT)} pages")


if __name__ == "__main__":
    main()