---
title: kubectl 命令行
---

# kubectl 命令行

> 与 k8s API Server 交互的瑞士军刀。掌握 80% 的日常运维。

## 🔧 配置

```bash
# kubectl 默认读 ~/.kube/config
ls ~/.kube/config

# 多个集群 / 多个上下文
kubectl config get-contexts
kubectl config use-context prod
kubectl config set-context --current --namespace=demo
```

`config` 包含：
- cluster（API server 地址 + ca）
- user（证书 / token）
- context（cluster + user + namespace）

## 📜 基础语法

```bash
kubectl [command] [TYPE] [NAME] [flags]

# command
get, describe, create, apply, delete, edit, exec, logs, exec, port-forward, cp, top, scale, exec, edit, patch, rollout, port-forward

# TYPE
pod, deploy, svc, ing, cm, secret, pv, pvc, node, ns, job, cronjob, ds, sts, hpa, ...

# 缩写
po, ds, deploy, svc, ing, cm, no, ns
```

## 🪛 最常用

### 查（get / describe）

```bash
# 列表
kubectl get pods                            # 默认 ns
kubectl get pods -A                          # 所有 ns
kubectl get pods -n kube-system
kubectl get pods -l app=web                  # 标签选择
kubectl get pods -o wide                     # 节点 / IP
kubectl get pods -o yaml                     # 完整 yaml
kubectl get pods -o json                     # JSON
kubectl get pods --sort-by=.status.startTime
kubectl get pods -w                          # 监听变化
kubectl get pods --field-selector=status.phase=Running

# 详情
kubectl describe pod <name>
kubectl describe node <node>
kubectl describe svc web
kubectl describe ing web

# 资源
kubectl api-resources                        # 列所有类型
kubectl api-versions                         # 列 API 版本
```

### 创建 / 删除

```bash
kubectl apply -f deploy.yaml
kubectl apply -f ./manifests/         # 目录下所有 yaml
kubectl apply -k ./overlays/prod      # Kustomize

# 命令式
kubectl run nginx --image=nginx
kubectl create deploy web --image=nginx --replicas=3

# 删除
kubectl delete -f deploy.yaml
kubectl delete pod <name>
kubectl delete pod <name> --force --grace-period=0
kubectl delete pods --all -n demo
```

### 编辑

```bash
kubectl edit deploy web                # 打开编辑器（KUBE_EDITOR / EDITOR）
kubectl patch svc web -p '{"spec":{"type":"NodePort"}}'
kubectl annotate pod myapp foo=bar
kubectl label pod myapp app=web
```

### 执行

```bash
# exec
kubectl exec -it pod-name -- bash
kubectl exec -it pod-name -c container -- sh

# 端口转发
kubectl port-forward svc/web 8080:80
kubectl port-forward pod/web 8080:80

# cp
kubectl cp pod-name:/etc/nginx/nginx.conf .
kubectl cp ./file pod-name:/tmp/file

# logs
kubectl logs pod-name
kubectl logs -f pod-name               # 跟踪
kubectl logs -f pod-name -c container
kubectl logs --tail 100 --since 1h pod-name
kubectl logs --previous pod-name      # 上一个容器实例（崩了用）
```

### 排错

```bash
kubectl describe pod <name>            # 看 Events（最常用！）
kubectl get events --sort-by=.lastTimestamp
kubectl get events -n demo
kubectl top pod
kubectl top node
kubectl exec -it pod-name -- bash    # 进容器
```

## 🚀 资源操作

### 伸缩

```bash
kubectl scale deploy/web --replicas=5
kubectl scale --replicas=3 -f deploy.yaml
kubectl autoscale deploy/web --min=2 --max=10 --cpu-percent=80
```

### 镜像更新 / 回滚

```bash
# 改镜像
kubectl set image deploy/web web=myapp:2.0
kubectl set image deploy/web web=myapp:2.0 --record

# 看历史
kubectl rollout history deploy/web
# REVISION  CHANGE-CAUSE
# 1         <none>
# 2         <none>

# 状态
kubectl rollout status deploy/web

# 暂停 / 恢复
kubectl rollout pause deploy/web
kubectl rollout resume deploy/web

# 回滚
kubectl rollout undo deploy/web
kubectl rollout undo deploy/web --to-revision=2
```

### Service

```bash
kubectl expose deploy web --port=80 --type=ClusterIP
kubectl expose deploy web --port=80 --type=NodePort
kubectl expose deploy web --port=80 --type=LoadBalancer
```

## 📋 输出格式

```bash
# 默认：人类可读
# -o yaml / json：完整资源
# -o wide：扩展列
# -o jsonpath='{.items[*].metadata.name}'

# 自定义列
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase

# 按事件排序
kubectl get pods --sort-by=.status.startTime

# label 选择
kubectl get pods -l 'env=prod,tier=frontend'
kubectl get pods -l 'env notin (dev,test)'

# 看 yaml
kubectl get pod web -o yaml | less
```

## 🧩 缩写

```bash
kubectl get po
kubectl get deploy
kubectl get ds              # daemonset
kubectl get sts             # statefulset
kubectl get svc
kubectl get ing
kubectl get cm              # configmap
kubectl get no              # node
kubectl get ns              # namespace

# 组合
kubectl get po,svc -A
```

## 📁 多集群

```bash
# 多 kubeconfig
export KUBECONFIG=~/.kube/prod:~/.kube/dev
kubectl config get-contexts
kubectl config use-context prod

# 看 / 改当前 namespace
kubectl config set-context --current --namespace=demo
kubectl config view --minify
```

## 🪜 插件

```bash
# 装 kubectx（切上下文）
kubectl krew install ctx ns
kubectl ctx prod
kubectl ns demo

# 其他实用插件
# - kubectl-tree（资源层级）
# - kubectl-images（看镜像）
# - kubectl-debug（高级 debug）
# - stern（多 pod 日志聚合）
```

## 🧰 实战

```bash
# 部署
kubectl apply -f deploy.yaml

# 排查
kubectl describe pod myapp | grep -A 10 Events
kubectl logs myapp --tail 100

# 进容器
kubectl exec -it myapp -- sh

# 扩缩
kubectl scale deploy/web --replicas=5

# 回滚
kubectl rollout undo deploy/web

# 端口转发
kubectl port-forward svc/web 8080:80
# 然后访问 localhost:8080

# 查哪些 pod 挂了
kubectl get pods -A --field-selector=status.phase!=Running
```

## 🔗 下一步

- [k8s 是什么](/02-k8s-arch/overview)
- [Pod 最小单元](/03-k8s-workload/pod)
- [排错](/13-troubleshooting/debug)


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
