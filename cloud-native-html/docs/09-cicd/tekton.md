---
title: Tekton / JenkinsX
---

# Tekton / JenkinsX

> Tekton = k8s 原生 CI/CD 框架（基础）。Jenkins X = Jenkins + Tekton + GitOps（包装）。

## 🤔 为什么需要 Tekton

```
传统 CI（Jenkins / GitHub Actions / GitLab CI）：
  ❌ 运维 Jenkins 服务
  ❌ 不 k8s 原生（"agent"概念）
  ❌ 流水线定义在 Jenkins / YAML 里
  ❌ 难跨环境

Tekton：
  ✅ Pipeline = k8s CRD（TaskRun / PipelineRun）
  ✅ Pipeline 跑在 k8s 集群里
  ✅ 一次定义，跨 k8s 集群跑
  ✅ 与 ArgoCD 集成（CI → GitOps）
```

## 🏗️ 核心 CRD

```
PipelineRun ──► Pipeline ──► Task(s) ──► Step(s)
  (一次跑)      (流水线)     (任务)         (步骤)

每个 Task 是一个 Pod
每个 Step 是 Pod 里的 container
```

| CRD | 含义 |
|-----|------|
| **Task** | 步骤的模板（"git clone" / "mvn test" / "docker build"） |
| **TaskRun** | 跑一次 Task → 一个 Pod |
| **Pipeline** | 多个 Task 串起来 |
| **PipelineRun** | 跑一次 Pipeline → 一组 TaskRun |
| **Workspace** | Task 间共享存储（PVC） |
| **Step** | Task 内的具体命令（容器） |

## 📜 简单例子

```yaml
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: echo-hello
spec:
  steps:
    - name: echo
      image: alpine:3
      script: |
        echo "Hello World!"
---
apiVersion: tekton.dev/v1beta1
kind: TaskRun
metadata:
  generateName: echo-hello-run-
spec:
  taskRef:
    name: echo-hello
```

```bash
kubectl apply -f task.yaml
kubectl apply -f taskrun.yaml
kubectl get taskrun
kubectl logs echo-hello-run-xxxx -f
```

## 🔧 Pipeline

```yaml
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: build-and-push
spec:
  workspaces:
  - name: source
  tasks:
  - name: fetch-source
    taskRef:
      name: git-clone
    workspaces:
    - name: output
      workspace: source
  - name: build
    runAfter: [fetch-source]      # 依赖
    taskRef: { name: kaniko-build }
    params:
    - name: IMAGE
      value: registry.example.com/myorg/myapp:${{params.tag}}
    workspaces:
    - name: source
      workspace: source
---
apiVersion: tekton.dev/v1beta1
kind: PipelineRun
metadata:
  generateName: myapp-build-
spec:
  pipelineRef:
    name: build-and-push
  workspaces:
  - name: source
    persistentVolumeClaim: { claimName: shared-pvc }
  params:
  - name: tag
    value: "1.0.0"
```

## 🚀 安装 Tekton

```bash
kubectl apply -f https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml

# 看
kubectl get pods -n tekton-pipelines
```

## 🪜 任务库

| 任务 | 用途 |
|------|------|
| git-clone | 拉代码 |
| kaniko-build / buildah | 构建镜像（无 Docker daemon） |
| dockerfile-build | 多阶段构建 |
| golangci-lint | Go lint |
| trivy-scanner | 安全扫描 |
| git-creds-writer | 写 Git 凭据 |

```bash
# 装 tekton catalog
kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/clustertask/git-clone/0.6/git-clone.yaml
```

## 🔐 凭据

```bash
# 创建 SSH 密钥 secret
kubectl create secret generic git-ssh \
  --from-file=ssh-privatekey=$HOME/.ssh/id_rsa

# 在 PipelineRun 引用
workspaces:
- name: source
  secret:
    secretName: git-ssh
```

## 🆚 Tekton vs Jenkins X

| | Tekton | Jenkins X |
|--|--------|------------|
| 上层 | 框架 | 完整产品 |
| 包含 | 引擎 + CRD | Jenkins + Tekton + ArgoCD + Skaffold + Lighthouse |
| 适合 | 已有 k8s 平台要建 CI | 一站式云原生 CI/CD |

**Jenkins X = Tekton + UX 包装**。从 Jenkins 迁移的团队偏好。

## 🚀 Jenkins X 装

```bash
# CLI
curl -L "https://repo1.jenkins.org/jenkins-x/jx/install-jx.sh" | bash -

# 装到 k8s
jx gitops add              # 加 jx 仓库
jx boot                   # 引导集群
jx pipeline                # 跑 pipeline
jx preview                 # 看 PR 预览
```

| 命令 | 作用 |
|------|------|
| `jx gitops` | GitOps（用 ArgoCD） |
| `jx pipeline` | 触发 pipeline |
| `jx preview` | PR 预览环境 |
| `jx promote` | 跨环境提升 |
| `jx git operator` | GitOps operator |

## 🛠 实战

```bash
# 1. 装 Tekton
kubectl apply -f https://storage.googleapis.com/tekton-releases/pipeline/latest/release.yaml

# 2. 装社区 catalog
kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/git-clone/0.9/git-clone.yaml
kubectl apply -f https://raw.githubusercontent.com/tektoncd/catalog/main/task/buildah/0.5/buildah.yaml

# 3. 写 Pipeline
# build-and-push.yaml
# ...

# 4. 触发
kubectl create -f pipelinerun.yaml
kubectl logs -f $(kubectl get pod -l tekton.dev/taskRun=build-and-push-xxx -o name)
```

## 🔄 与 ArgoCD 集成

```
Tekton (CI: build + push image)
  ↓ 更新 image tag
Git commit (Helm value 更新)
  ↓
ArgoCD (CD: 同步到集群)
```

详见 [ArgoCD](/09-cicd/argocd) + [GitOps](/09-cicd/gitops)。

## 🆚 主流 CI / CD

| 工具 | 类型 | 适合 |
|------|------|------|
| Jenkins X | 完整云原生 | 大团队、传统 Jenkins 转型 |
| Tekton | 框架 | 自建 / 高度定制 |
| GitHub Actions | SaaS | 开源项目 |
| GitLab CI | SaaS / 自托管 | GitLab 用户 |
| CircleCI | SaaS | 商业项目 |
| Drone | 自托管 | Docker 原生 |
| Buildkite | SaaS | 商业项目 |
| Drone / Gitea Actions | 自托管 | 轻量 |

## 🔗 下一步

- [GitOps 思想](/09-cicd/gitops)
- [ArgoCD](/09-cicd/argocd)
- [Chart 结构](/06-helm/chart)