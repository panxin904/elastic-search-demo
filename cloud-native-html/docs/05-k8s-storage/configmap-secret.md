---
title: ConfigMap / Secret
date: 2026-08-15  # date-auto-injected
---

# ConfigMap / Secret - 配置与敏感数据

> 配置文件 / 密钥 不要硬编码到镜像。ConfigMap + Secret 让"代码"和"配置"分离。

## 🤔 为什么需要

```
❌ 硬编码：
  - 不同环境（dev / prod）要改代码 → 重建镜像
  - 密钥进镜像 → 镜像泄露 = 密钥泄露
  - 多容器共享配置 → N 份重复

✅ ConfigMap / Secret：
  - 配置外置，注入环境
  - 密钥单独管理
  - 多个 Pod 共享一份
  - 改配置不用重建镜像
```

## 📜 ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: prod
data:
  # 整个文件
  nginx.conf: |
    server {
      listen 80;
      root /var/www/html;
    }

  # 单个 key-value（字符串）
  app.name: "MyApp"
  app.log.level: "info"
  app.cache.ttl: "300"
```

### 4 种使用方式

```yaml
spec:
  containers:
  - name: app
    image: myapp:1.0

    # 1. 单个环境变量
    env:
    - name: LOG_LEVEL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: app.log.level

    # 2. 全部作为环境变量
    envFrom:
    - configMapRef:
        name: app-config

    # 3. 挂载为文件（key 是文件名）
    volumeMounts:
    - name: config
      mountPath: /etc/config
  volumes:
  - name: config
    configMap:
      name: app-config

    # 4. 挂载单个文件
    volumeMounts:
    - name: single-config
      mountPath: /etc/log.conf
      subPath: nginx.conf
  volumes:
  - name: single-config
    configMap:
      name: app-config
      items:
      - key: nginx.conf
        path: nginx.conf
```

更新 ConfigMap：文件**不会自动热加载**（需要 reload Pod 或用 Reloader）。

## 📜 Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
  namespace: prod
type: Opaque                       # 通用
data:
  # base64 编码（**不加密**！）
  DB_PASSWORD: YWRtaW5fcGFzc3dvcmQ=
  API_KEY: c2stbGl2ZS0xMjM0NTY3ODkw
```

### 常见 type

| type | 用途 |
|------|------|
| `Opaque` | 通用 |
| `kubernetes.io/tls` | TLS 证书 |
| `kubernetes.io/dockerconfigjson` | 私有仓库密钥 |
| `kubernetes.io/service-account-token` | SA token（k8s 自动） |
| `kubernetes.io/basic-auth` | Basic Auth |
| `kubernetes.io/ssh-auth` | SSH key |

### 创建

```bash
# 命令式
kubectl create secret generic db-pass \
  --from-literal=password=secret

kubectl create secret docker-registry my-registry \
  --docker-server=registry.example.com \
  --docker-username=alice \
  --docker-password=xxx

# TLS
kubectl create secret tls app-tls \
  --cert=tls.crt --key=tls.key
```

### 使用

```yaml
spec:
  containers:
  - name: app
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: DB_PASSWORD
    envFrom:
    - secretRef:
        name: app-secret
    volumeMounts:
    - name: secret
      mountPath: /etc/secret
  volumes:
  - name: secret
    secret:
      secretName: app-secret
```

## 🔐 Secret 加密

**默认 Secret 不加密**，仅 base64。生产必开加密：

```bash
# 装 EncryptionConfiguration
cat > /etc/kubernetes/encryption-config.yaml <<EOF
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: $(head -c 32 /dev/urandom | base64)
      - identity: {}
EOF

# 改 apiserver flags
# --encryption-provider-config=/etc/kubernetes/encryption-config.yaml
sudo systemctl restart kube-apiserver
```

新写入的 Secret 会加密；**已有 Secret 不会被自动加密**（kubectl get secret + apply）。

## ☁️ 外部 Secret 管理

生产推荐：Secret 不存在 etcd 里。

| 方案 | 特点 |
|------|------|
| **HashiCorp Vault** | 业界标准，动态密钥 |
| **AWS Secrets Manager** | AWS 集成 |
| **GCP Secret Manager** | GCP 集成 |
| **Azure Key Vault** | Azure 集成 |
| **External Secrets Operator** | k8s 同步外部 secret |

```yaml
# ExternalSecret
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-cred
spec:
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  data:
  - secretKey: password
    remoteRef:
      key: secret/data/db
```

## 🆚 ConfigMap vs Secret

| | ConfigMap | Secret |
|--|-----------|--------|
| 用途 | 非密配置 | 敏感数据 |
| 编码 | 原文 | base64（默认）/ 加密（开启后） |
| 大小 | 无严格限制 | < 1MB（etcd 限制） |
| 适合 | 配置文件 / 参数 | 密码 / token / 证书 |

## 🛠 实战

```bash
# 创建 ConfigMap
kubectl create configmap app-config \
  --from-file=app.properties \
  --from-literal=DEBUG=true

# 创建 Secret
kubectl create secret generic db-pass \
  --from-literal=password=secret

# 看
kubectl get cm
kubectl get secret

# 改
kubectl edit cm app-config
kubectl edit secret db-pass

# 看明文（仅 base64，env 也能看）
kubectl get secret db-pass -o jsonpath='{.data.DB_PASSWORD}' | base64 -d

# 删
kubectl delete cm app-config
kubectl delete secret db-pass
```

## 🔗 下一步

- [PV / PVC](/05-k8s-storage/pv-pvc)
- [StorageClass / CSI](/05-k8s-storage/storageclass)
- [Secret 管理](/11-security/secret)