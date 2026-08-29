---
title: template / values
date: 2026-08-15  # date-auto-injected
---

# template / values

> 模板 + values = 同一份 Chart 部署到任意环境。

## 🧬 template 语法

### 基础

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config     # Release 名
  labels:
    app: {{ .Values.appName }}          # 来自 values
    env: {{ .Values.environment | default "dev" }}
data:
  log_level: {{ .Values.log.level }}
  replicas: {{ .Values.replicaCount }}
```

### 流程控制

```yaml
# if / else
{{- if eq .Values.environment "prod" }}
replicas: 5
{{- else if eq .Values.environment "staging" }}
replicas: 2
{{- else }}
replicas: 1
{{- end }}

# 循环（遍历 list）
{{- range .Values.hosts }}
- {{ . }}
{{- end }}

# 循环（带 key/value）
{{- range $key, $value := .Values.labels }}
{{ $key }}: {{ $value | quote }}
{{- end }}

# with（限定 scope）
{{- with .Values.service }}
port: {{ .port }}
{{- end }}
```

### 内置对象

| 对象 | 含义 |
|------|------|
| `.Values` | values.yaml |
| `.Chart` | Chart.yaml |
| `.Release` | 当前 release（name / namespace / revision / service） |
| `.Files` | Chart 内文件 |
| `.Template` | 当前模板信息 |
| `.Capabilities` | k8s API 能力 |

### 实用函数

```yaml
# 默认值
{{ .Values.image.tag | default "latest" }}

# 引号
apiUrl: {{ .Values.apiUrl | quote }}

# 渲染嵌套 yaml
env:
  {{- toYaml .Values.env | nindent 4 }}

# base64（Secret 数据必须 base64）
data:
  password: {{ .Values.password | b64enc | quote }}

# 字符串 / 整数
replicas: {{ .Values.replicaCount | int }}
name: {{ .Values.name | default "myapp" | lower | quote }}

# lookup（在 map 里取）
image: {{ .Values.images | default dict | dig "name" "myapp" }}

# 文件内容
data:
  nginx.conf: {{ .Files.Get "config/nginx.conf" | nindent 4 }}
```

## 📜 values.yaml 层级

```yaml
# values.yaml - 默认值
image:
  repository: myapp
  tag: 1.0.0
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

# 用户覆盖：
# helm install myapp ./chart -f my-values.yaml
```

```yaml
# my-values.yaml - 用户自定义
image:
  tag: 2.0.0          # 覆盖
service:
  type: LoadBalancer  # 覆盖
```

合并规则：
- **后传入覆盖先传入**（`my-values.yaml` 覆盖 `values.yaml`）
- 默认值 = `helm install -f values.yaml` 链
- `--set` 最优先

## 🔧 注入到 Pod

```yaml
spec:
  containers:
  - name: app
    image: myapp:1.0
    env:
    # 单个值
    - name: LOG_LEVEL
      value: {{ .Values.log.level | quote }}

    # 来自 ConfigMap / Secret（推荐）
    - name: DB_HOST
      valueFrom:
        configMapKeyRef:
          name: {{ include "myapp.fullname" . }}-config
          key: db.host

    # 整个 ConfigMap
    envFrom:
    - configMapRef:
        name: {{ include "myapp.fullname" . }}-config

    # 模板渲染 Secret
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: {{ include "myapp.fullname" . }}-secret
          key: password
```

## 📚 常用模板

### 模板辅助函数（_helpers.tpl）

```gotemplate
{{/* 通用名称 */}}
{{- define "myapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/* 通用 labels */}}
{{- define "myapp.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/name: {{ include "myapp.fullname" . }}
{{- end }}

{{/* selector labels */}}
{{- define "myapp.selectorLabels" -}}
app.kubernetes.io/name: {{ include "myapp.fullname" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

用法：

```yaml
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
```

## 🧩 完整例子

```yaml
# templates/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "myapp.fullname" . }}-config
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
data:
  {{- range $key, $value := .Values.config }}
  {{ $key }}: {{ $value | quote }}
  {{- end }}
```

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "myapp.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        envFrom:
        - configMapRef:
            name: {{ include "myapp.fullname" . }}-config
        ports:
        - containerPort: {{ .Values.service.port }}
        resources:
          {{- toYaml .Values.resources | nindent 10 }}
```

## 🪛 实战

```bash
# 调试模板
helm template myapp ./myapp --debug

# 渲染到文件
helm template myapp ./myapp > /tmp/rendered.yaml
cat /tmp/rendered.yaml

# 测试特定 values
helm template myapp ./myapp \
  --set replicaCount=3 \
  --set image.tag=2.0 \
  -f my-prod.yaml

# 验证
helm install myapp ./myapp --dry-run --debug
```

## ⚠️ 常见错误

```
1. 模板缩进错误
   {{ toYaml .Values.x | nindent 4 }}  ← 注意 nindent
2. 没引号的字符串
   value: {{ .Values.x }}    ← 如果 x 含空格会断
   value: {{ .Values.x | quote }}
3. nil 访问
   {{ .Values.undefined.x }}   ← 报错
   {{ .Values.undefined | default dict | x }}
```

## 🔗 下一步

- [Chart 结构](/06-helm/chart)
- [Chart 仓库](/06-helm/repository)
- [Helmfile / Kustomize](/10-iac/helmfile)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud](https://java-px.bot.cd/cloud/):Spring Cloud 微服务
- [linux](https://java-px.bot.cd/linux/):Linux 内核基础
- [devops](https://java-px.bot.cd/devops/):DevOps 流程
