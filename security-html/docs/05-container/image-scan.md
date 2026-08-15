---
title: 镜像扫描
---

# 容器镜像扫描

## 一句话总结

> **镜像扫描 = 静态分析镜像 layer 中的 CVE**。**主流工具：Trivy（全能）/ Grype（简洁）/ Clair（API 集成）**。**集成：CI 阻断 + 准入控制 + 持续运行时扫描**。

---

## 扫描工具对比

| 工具 | 特性 | 输出格式 | 速度 |
|------|------|---------|------|
| **Trivy** | 全能（CVE / IaC / SBOM）| CycloneDX / SPDX / JSON | 快 |
| **Grype** | 简洁、CycloneDX | CycloneDX / JSON | 快 |
| **Clair** | 静态分析、API | JSON | 中 |
| **Snyk Container** | 商业、深度 | 报告 + 修复建议 | 快 |
| **Docker Scan** | 内置（基于 Snyk）| 报告 | 中 |
| **Anchore** | 深度策略 | JSON | 慢 |

## 实战：Trivy 扫描

```bash
# 扫描本地镜像
trivy image nginx:1.25

# 输出
nginx:1.25 (debian 12.4)
==========================
Total: 47 (HIGH: 12, CRITICAL: 3)

+---------+------------------+----------+-------------------+-------------------+
| LIBRARY | VULNERABILITY ID | SEVERITY | INSTALLED VERSION | FIXED VERSION     |
+---------+------------------+----------+-------------------+-------------------+
| openssl | CVE-2024-XXXXX   | CRITICAL | 3.0.11-1~deb12u1  | 3.0.13-1~deb12u1  |
| glibc   | CVE-2023-XXXXX   | HIGH     | 2.36-9+deb12u7    | 2.36-9+deb12u8    |
+---------+------------------+----------+-------------------+-------------------+

# 严重度过滤
trivy image --severity CRITICAL,HIGH nginx:1.25

# 输出 SBOM
trivy image --format cyclonedx --output sbom.json nginx:1.25

# 扫描文件系统
trivy fs /path/to/project

# 扫描 IaC
trivy config /path/to/terraform
```

## 实战：CI 集成（GitHub Actions）

```yaml
name: container-scan
on:
  push:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .

      - name: Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: myapp:${{ github.sha }}
          severity: CRITICAL,HIGH
          exit-code: 1  # 严重漏洞时失败
          format: table
```

## 实战：Grype

```bash
# 安装
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh

# 扫描
grype nginx:1.25

# 输出 SBOM
grype nginx:1.25 -o cyclonedx-json > sbom.json
```

## 实战：Snyk Container

```bash
# 安装
npm install -g snyk

# 认证
snyk auth

# 扫描
snyk container test nginx:1.25

# 监控
snyk container monitor nginx:1.25
```

## 实战：K8s 准入控制

```yaml
# Kyverno 策略：拒绝含 CRITICAL 漏洞的镜像
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: scan-image
spec:
  validationFailureAction: Enforce
  rules:
    - name: scan-image
      match:
        any:
          - resources:
              kinds: ["Pod"]
      validate:
        message: "Image failed CVE scan"
        pattern:
          metadata:
            labels:
              scan-status: "passed"
```

## 实战：Trivy Operator（K8s 集群扫描）

```bash
# 安装
helm install trivy-operator trivy-operator     --namespace trivy-system --create-namespace

# 自动扫描所有工作负载
# 漏洞报告存为 CRD
kubectl get vulnerabilityreports -A
```

## 实战：镜像修复

```bash
# 升级基础镜像
docker pull python:3.12-slim  # 替代 3.11-slim

# 重建
docker build -t myapp:1.0.1 .

# 重新扫描
trivy image myapp:1.0.1
```

## 实战：多阶段构建减漏洞

```dockerfile
# ❌ 漏洞多
FROM ubuntu:latest
RUN apt install -y python3

# ✅ 多阶段
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS runtime
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin /usr/local/bin
COPY app /app
USER 1000
CMD ["python", "/app/main.py"]
```

## 扫描策略

```yaml
# 阶段 1：本地开发
trivy fs .

# 阶段 2：CI 流水线
- name: Scan
  run: trivy image --exit-code 1 --severity CRITICAL myapp:${{ github.sha }}

# 阶段 3：镜像推送
# 必须在镜像推送到 registry 之前完成

# 阶段 4：K8s 准入
# Kyverno / Connaisseur 阻断

# 阶段 5：运行时
# Trivy Operator 持续扫描
```

## 关联章节

- **05-container/overview**：容器安全总览
- **05-container/supply-chain**：SBOM + 签名
- **05-container/runtime-security**：Falco 运行时
- **01-web-top10/a06-vulnerable-component**：A06 组件漏洞

## 一句话总结

> **镜像扫描 = Trivy（首选）/ Grype / Snyk**。**CI 阻断 + 准入控制 + 持续扫描**。**多阶段构建 + 最小基础镜像 = 减漏洞**。
