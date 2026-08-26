---
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
