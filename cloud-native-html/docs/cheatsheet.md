---
title: 命令速查
---

# 📋 Docker / Kubernetes 命令速查

> 30+ 高频命令，分组速查。直接复制运行。

## 🐳 Docker

```bash
# 镜像
docker pull nginx:alpine
docker images
docker rmi <image>
docker image prune                # 清 dangling
docker build -t myapp:1.0 .       # 构建
docker tag myapp:1.0 myapp:latest
docker save -o myapp.tar myapp:1.0
docker load -i myapp.tar

# 容器
docker run -d --name web -p 80:80 nginx
docker run -it --rm alpine sh
docker ps -a                      # 全部
docker logs -f web                 # 跟踪日志
docker exec -it web bash          # 进容器
docker stop web && docker rm web
docker restart web
docker top web                    # 看进程

# 系统
docker system df                  # 看磁盘占用
docker system prune -a            # 清无用的镜像 / 容器 / 网络
```

## 🔍 kubectl 基础

```bash
# 节点 / 集群
kubectl get nodes
kubectl cluster-info
kubectl version

# 资源
kubectl get pods -A
kubectl get pods -n kube-system
kubectl get pods --field-selector=status.phase=Running
kubectl get pods -o wide
kubectl get pods -o yaml
kubectl describe pod <name> -n <ns>

# 创建 / 删除
kubectl apply -f deploy.yaml
kubectl apply -k ./overlays/prod
kubectl delete -f deploy.yaml
kubectl delete pod <name> --grace-period=0 --force
```

## 🚀 Deployment / Pod

```bash
# 伸缩
kubectl scale deploy/web --replicas=5

# 镜像更新
kubectl set image deploy/web web=myapp:2.0

# 回滚
kubectl rollout undo deploy/web
kubectl rollout history deploy/web
kubectl rollout status deploy/web
kubectl rollout pause deploy/web
kubectl rollout resume deploy/web

# 进入 Pod
kubectl exec -it pod-name -- bash
kubectl exec -it pod-name -c container-name -- sh
kubectl debug pod/pod-name -it --image=busybox

# 日志
kubectl logs pod-name
kubectl logs pod-name -c container
kubectl logs -f --tail=100 -l app=web
```

## 🌐 Service / 网络

```bash
# Service
kubectl get svc
kubectl get endpoints <svc>
kubectl port-forward svc/web 8080:80
kubectl port-forward pod/web 8080:80
kubectl exec -it pod-name -- curl http://web:80

# Ingress
kubectl get ing
kubectl describe ing web
```

## 💾 存储 / ConfigMap

```bash
# ConfigMap
kubectl get cm
kubectl describe cm app-config

# Secret
kubectl get secret db-pass
kubectl get secret db-pass -o jsonpath='{.data.password}' | base64 -d

# 编辑
kubectl edit cm app-config
kubectl set env deploy/web DEBUG=true
```

## ⛵ Helm

```bash
# 仓库
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm search repo nginx

# 安装
helm install myapp bitnami/nginx
helm install myapp myapp-chart/ -f values.yaml
helm install myapp myapp-chart/ --set replicaCount=3

# 查看
helm list
helm list -A
helm status myapp
helm history myapp
helm get values myapp
helm get manifest myapp

# 升级 / 回滚
helm upgrade myapp myapp-chart/ -f values.yaml
helm rollback myapp 1

# 卸载
helm uninstall myapp
```

## 🛠 排错套路

```bash
# Pod 卡死 / 状态不对
kubectl describe pod <name>
kubectl logs <name> --previous          # 上一个容器实例
kubectl get events --sort-by=.lastTimestamp

# 进容器调试（带 debug 镜像）
kubectl debug -it pod/<name> --image=busybox --target=<container>
kubectl debug -it pod/<name> --image=nicolaka/netshoot

# 网络
kubectl get endpoints <svc>
kubectl run -it --rm debug --image=alpine --restart=Never -- nslookup kubernetes
kubectl run -it --rm debug --image=alpine --restart=Never -- wget -O- http://web

# 节点
kubectl describe node <node>
kubectl top node
kubectl top pod
```

## 📋 资源 / 排错

```bash
# 资源
kubectl get all -A
kubectl get pod -o yaml | less
kubectl top pod
kubectl describe node
kubectl get events --sort-by=.metadata.creationTimestamp

# 节点维护
kubectl cordon <node>      # 标记不可调度
kubectl drain <node>       # 排空 Pod
kubectl uncordon <node>    # 恢复

# 上下文
kubectl config get-contexts
kubectl config use-context prod
kubectl config set-context --current --namespace=demo
```

## 🔒 RBAC

```bash
# 看权限
kubectl auth can-i create pods
kubectl auth can-i '*' '*' --as system:serviceaccount:default:default
kubectl auth can-i list nodes --as alice

# 看 clusterrole
kubectl get clusterrole
kubectl get clusterrolebinding
kubectl describe clusterrole admin
```

## 🔍 节点 / etcd

```bash
# 节点
kubectl get nodes -o wide
kubectl describe node <node>
kubectl cordon / drain / uncordon

# etcd 备份
ETCDCTL_API=3 etcdctl snapshot save /tmp/snap.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key
```

## 🌐 网络诊断

```bash
# 节点内网络
ip addr
ip route
ss -tlnp                          # 看端口

# 服务连通
nslookup web.default.svc.cluster.local
curl http://web:80                # Pod 内
curl http://web.default.svc.cluster.local  # 跨 namespace

# DNS
kubectl run -it --rm debug --image=alpine --restart=Never -- cat /etc/resolv.conf
```

## 🔄 下一步

- [Docker 基础](/01-docker/intro)
- [k8s 架构](/02-k8s-arch/overview)
- [kubectl 命令行](/02-k8s-arch/kubectl)
- [排错](/13-troubleshooting/debug)