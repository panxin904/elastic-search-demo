---
title: 容器供应链安全
---

# 容器供应链安全

## 一句话总结

> **供应链 = 镜像 → SBOM → 签名 → 准入 → 审计**。**核心：SBOM（CycloneDX）+ Sigstore（Cosign）+ SLSA L3 框架**。**实战：Trivy 生成 SBOM + Cosign 签名 + Kyverno 准入**。

---

## 供应链 5 个阶段

```
Developer                CI/CD                  Registry              K8s               Runtime
    │                       │                      │                   │                   │
    │  1. Code (Git)       │                      │                   │                   │
    │ ──────────────────→  │                      │                   │                   │
    │                       │  2. Build            │                   │                   │
    │                       │  + SBOM (Trivy)      │                   │                   │
    │                       │  + Sign (Cosign)     │                   │                   │
    │                       │ ──────────────────→  │                   │                   │
    │                       │                      │  3. Push           │                   │
    │                       │                      │ ──────────────→   │                   │
    │                       │                      │                   │  4. Deploy        │
    │                       │                      │                   │  + Verify (Policy)│
    │                       │                      │                   │ ──────────────→   │
    │                       │                      │                   │                   │
    │                       │                      │                   │                   │  5. Audit
    │                       │                      │                   │                   │  (Policy)
```

## 实战：SBOM 生成

```bash
# Trivy 生成 CycloneDX
trivy image --format cyclonedx --output sbom.json myapp:1.0.0

# Syft 生成（更通用）
syft myapp:1.0.0 -o cyclonedx-json > sbom.json

# SPDX 格式
trivy image --format spdx-json --output sbom.spdx.json myapp:1.0.0
```

```json
// CycloneDX 样例
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "version": 1,
  "components": [
    {
      "type": "library",
      "name": "log4j-core",
      "version": "2.17.0",
      "purl": "pkg:maven/org.apache.logging.log4j/log4j-core@2.17.0",
      "licenses": [{"license": {"name": "Apache-2.0"}}]
    }
  ]
}
```

## 实战：Cosign 签名

```bash
# 1. 生成密钥对
cosign generate-key-pair

# 2. 签名镜像
cosign sign --key cosign.key myregistry.io/myapp:1.0.0

# 3. 验证签名
cosign verify --key cosign.pub myregistry.io/myapp:1.0.0

# 4. 与 Rekor（透明日志）集成
cosign sign --key cosign.key myregistry.io/myapp:1.0.0
# 默认上传到 sigstore public Rekor
```

## 实战：Keyless 签名（基于 OIDC）

```bash
# 用短期 OIDC token 签名（无需密钥）
cosign sign myregistry.io/myapp:1.0.0

# 验证
cosign verify     --certificate-identity email@company.com     --certificate-oidc-issuer https://accounts.google.com     myregistry.io/myapp:1.0.0
```

## 实战：Kyverno 验签策略

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signature
spec:
  validationFailureAction: Enforce
  rules:
    - name: verify-cosign-signature
      match:
        any:
          - resources:
              kinds: ["Pod"]
      verifyImages:
        - attestors:
            - entries:
                - keys:
                    publicKeys: |-
                      -----BEGIN PUBLIC KEY-----
                      MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...
                      -----END PUBLIC KEY-----
          imageReferences:
            - "myregistry.io/*"
```

## 实战：SLSA 框架

```
┌────────────────────────────────────────┐
│  SLSA Levels（Supply-chain Levels for  │
│  Software Artifacts）                   │
├────────────────────────────────────────┤
│  L0：无 SLSA                            │
│  L1：构建过程文档化 + 签名              │
│  L2：构建服务签名 + 完整来源追溯        │
│  L3：来源防篡改 + 防泄露 + 双签        │
└────────────────────────────────────────┘
```

Google SLSA 实践：
- **L1**：基础 CI（GitHub Actions）+ 签名
- **L2**：Hermetic build（隔离构建）+ 来源 provenance
- **L3**：两方签名 + 硬件密钥

## 实战：npm / PyPI 供应链

```bash
# npm 安装审计
npm audit --production

# 锁定依赖
npm ci  # 仅安装 lockfile 中版本

# PyPI 哈希验证
pip install --require-hashes -r requirements.txt
```

```yaml
# GitHub Actions audit
- name: Audit
  run: |
    npm audit --audit-level=high
    pip-audit --strict
```

## 实战：依赖镜像投毒防御

```bash
# 内部 npm registry 代理 + 镜像签名
# Verdaccio / Sonatype Nexus

# npm 配置
npm config set registry https://npm.internal.company.com
```

## 实战：in-toto 验证（学术级）

```bash
# in-toto：保护整个供应链
in-toto-verify --layout layout.root.json --public-key root.pub
```

## 实战：Sigstore 全家桶

| 工具 | 作用 |
|------|------|
| **Cosign** | 镜像 / 二进制签名 |
| **Rekor** | 透明日志（不可篡改）|
| **Fulcio** | 短期 OIDC 证书 |
| **The Update Framework (TUF)** | 软件更新 |

## 关联章节

- **05-container/overview**：容器安全总览
- **05-container/image-scan**：镜像扫描
- **05-container/runtime-security**：运行时
- **01-web-top10/a08-software-data-integrity**：A08 数据完整性

## 一句话总结

> **供应链 = SBOM + 签名 + 准入 + 透明日志**。**工具链：Trivy（SBOM）+ Cosign（签名）+ Kyverno（准入）+ Rekor（审计）**。**SLSA L3 = 业界最高标准**。
