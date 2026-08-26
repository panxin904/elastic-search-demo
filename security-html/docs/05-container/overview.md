---
title: 容器安全总览
---

# 容器安全

## 一句话总结

> **容器安全 = 镜像 + 运行时 + 供应链 + 编排**。**镜像扫描（Trivy / Clair）+ 运行时检测（Falco / Tracee）+ SBOM 软件物料清单 + Sigstore 签名 + 容器逃逸加固**。**K8s 时代容器安全是零信任的最后一公里**。

---

## 4 层防护

```
┌────────────────────────────────────────────┐
│  Layer 1 · 镜像安全（Build-Time）           │
│  - 多阶段构建、基础镜像最小化                │
│  - Trivy / Grype / Clair 扫描 CVE         │
│  - Cosign 签名 + SLSA 供应链 L3            │
├────────────────────────────────────────────┤
│  Layer 2 · 运行时安全（Runtime）            │
│  - Falco / Tracee 异常检测                 │
│  - Seccomp / AppArmor / SELinux            │
│  - 不可变基础设施 + 只读文件系统            │
├────────────────────────────────────────────┤
│  Layer 3 · 编排安全（K8s）                  │
│  - RBAC 最小权限                            │
│  - Network Policy 默认拒绝                  │
│  - Pod Security Standards (restricted)     │
│  - Service Mesh mTLS 自动注入              │
├────────────────────────────────────────────┤
│  Layer 4 · 供应链安全（Supply Chain）       │
│  - SBOM（SPDX / CycloneDX）                │
│  - Sigstore 签名（Cosign / Rekor）         │
│  - SLSA L3 框架                             │
└────────────────────────────────────────────┘
```

## 镜像扫描工具

| 工具 | 语言 | 特性 | 速度 |
|------|------|------|------|
| **Trivy** | Go | 全能（CVE / IaC / SBOM） | 快 |
| **Grype** | Go | 简洁、CycloneDX 输出 | 快 |
| **Clair** | Go | 静态分析、API 集成 | 中 |
| **Snyk Container** | - | 商业版、市场领先 | 快 |
| **Docker Scan** | Go | 内置（基于 Snyk） | 中 |

### 实战：扫描本地镜像

```bash
# Trivy
trivy image nginx:1.25
# 输出：CVE ID / 严重等级 / 修复版本 / 路径

# 输出 SBOM
trivy image --format cyclonedx --output sbom.json nginx:1.25

# 与 CI 集成（fail 当严重漏洞）
trivy image --exit-code 1 --severity CRITICAL nginx:1.25
```

## 运行时检测

### Falco 默认规则

```yaml
# 检测容器内执行 shell
- rule: Terminal shell in container
  desc: Alert if a shell is spawned in a container
  condition: >
    container.id != host and
    proc.name = bash
  output: >
    Shell spawned in container (user=%user.name command=%proc.cmdline)
  priority: WARNING

# 检测敏感文件读取
- rule: Read sensitive file
  condition: >
    open_read and fd.name startswith /etc/shadow
  output: Sensitive file read
  priority: CRITICAL
```

## 容器逃逸典型案例

| 漏洞 | 原理 | 修复 |
|------|------|------|
| **CVE-2022-0492** | cgroups v1 release_agent | 升级 cgroups v2 |
| **CVE-2022-0185** | namespace 整数溢出 | 升级 Linux 5.16.2 |
| **CVE-2022-0494** | Ubuntu 特权容器 | 升级 runc |
| **特权容器** | `--privileged` 禁用保护 | 禁止使用 |
| **Docker Socket 挂载** | 容器可控制宿主 Docker | 绝对禁止 |

## 实战：K8s Pod Security

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  securityContext:
    runAsNonRoot: true               # 禁止 root
    runAsUser: 1000                  # 固定 UID
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault          # 默认 seccomp
  containers:
    - name: app
      image: myapp:1.0.0
      securityContext:
        allowPrivilegeEscalation: false  # 禁止提权
        readOnlyRootFilesystem: true     # 只读文件系统
        capabilities:
          drop: ["ALL"]                  # 禁用所有 capabilities
      resources:
        limits:
          cpu: 500m
          memory: 512Mi
```

## 关联章节

- **01-web-top10/a06-vulnerable-component**：A06 易受攻击组件 = 镜像扫描
- **01-web-top10/a08-software-data-integrity**：A08 软件完整性 = SBOM + Sigstore
- **06-zero-trust/spiffe**：容器身份 = SPIFFE Workload Identity
- **cloud-native** → K8s RBAC / NetworkPolicy 详细内容

## 一句话总结

> **镜像扫描 = 静态 CVE**（Trivy）。**运行时检测 = 异常行为**（Falco）。**SBOM = 物料清单**（CycloneDX）。**签名 = 防篡改**（Cosign）。**K8s restricted Pod = 默认安全**。


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
