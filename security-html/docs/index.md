---
layout: home
title: Security 知识图谱
hero:
  name: Security
  text: Web 安全深度图谱
  tagline: OWASP Top 10 2025 · OAuth 2.0 / OIDC · JWT · 密码学 · TLS · 容器安全 · 零信任
  actions:
    - theme: brand
      text: 🛡️ 进入 OWASP Top 10
      link: /01-web-top10/overview
    - theme: alt
      text: 🔐 认证协议
      link: /02-auth/overview
    - theme: alt
      text: 🔏 密码学
      link: /03-crypto/overview
    - theme: alt
      text: 🔒 零信任
      link: /06-zero-trust/overview
features:
  - title: 🛡️ OWASP Top 10 2025
    details: 业界权威 Web 安全风险清单，10 大类高危漏洞逐条拆解：访问控制失效、注入、设计缺陷、SSRF、供应链等，覆盖攻防两端。
    link: /01-web-top10/overview
    linkText: OWASP 总览
  - title: 🔐 认证与授权
    details: OAuth 2.0 四种授权流程、OIDC 身份层、JWT 结构与攻击面、SAML 企业 SSO、Session 攻击矩阵、MFA 多因素认证。
    link: /02-auth/overview
    linkText: 认证协议地图
  - title: 🔏 密码学基础
    details: 对称加密（AES / ChaCha20）、非对称加密（RSA / ECC）、哈希（SHA-256 / bcrypt）、数字签名、TLS 1.3 握手抓包。
    link: /03-crypto/overview
    linkText: 密码学总览
  - title: 🌐 网络安全
    details: TLS PKI 证书体系、mTLS 双向认证、HSTS / CSP / X-Frame-Options 浏览器安全、CORS 跨域原理与陷阱。
    link: /04-network/tls-pki
    linkText: TLS PKI
  - title: 📦 容器与供应链
    details: 镜像扫描（Trivy / Clair）、运行时安全（Falco）、SBOM 软件物料清单、Sigstore 签名、容器逃逸案例。
    link: /05-container/overview
    linkText: 容器安全总览
  - title: 🔒 零信任架构
    details: BeyondCorp / SDP / SPIFFE / SPIRE 身份联邦、Workload Identity、落地 Google BeyondCorp 实践。
    link: /06-zero-trust/overview
    linkText: 零信任总览
---

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "OWASP Top 10 风险记不全，audit 一个 Web 应用无从下手？",
      "认证 vs 授权、RBAC vs ABAC 模型区别？",
      "密码学（对称 / 非对称 / 哈希 / 数字签名）讲不清？",
      "TLS / HTTPS / 证书体系不熟？",
      "XSS / CSRF / SQL 注入 / SSRF 等 Web 攻击原理？"
    ]
const goals = [
      "安全基础（认证 / 授权 / 密码学 / TLS / 攻击面）",
      "Web 安全（OWASP Top 10 / XSS / CSRF / SSRF / SQL 注入）",
      "Linux / 系统安全（权限 / capabilities / SELinux）",
      "网络安全（TLS / WAF / 防火墙 / IDS / IPS）",
      "应用安全（API 安全 / JWT / OAuth2 / OIDC）",
      "云原生安全（容器安全 / K8s RBAC / Sigstore / SBOM）"
    ]
const relatedSites = [
      { site: "network", path: "/01-fundamentals/tcp-ip", label: "TCP/IP 协议" },
      { site: "linux", path: "/13-net/iptables", label: "Linux 防火墙" },
      { site: "cloud-native", path: "/08-security/overview", label: "云原生安全" },
      { site: "devops", path: "/06-best-practices/secure-pipeline", label: "安全流水线" },
      { site: "frontend", path: "/04-react/hooks", label: "前端安全" }
    ]
</script>

<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>


## 关联站点

- **ai/** → LLM 应用安全（prompt injection / 模型越狱 / 数据泄露）→ 链到 `01-web-top10`
- **cloud-native/** → K8s RBAC / 网络策略 / Service Mesh 安全 → 链到 `05-container`
- **mysql** / **postgresql/** → SQL 注入原理 + 防御 → 链到 `01-web-top10/a03-injection`
- **java/** / **python/** → 框架级安全（Spring Security / Django Auth）→ 链到 `02-auth`
- **system-design/** → API 网关鉴权 / 分布式 Session → 链到 `02-auth/jwt`

## 学习路径建议

| 阶段 | 时长 | 章节 |
|------|------|------|
| 入门 | 1-2 周 | 01-web-top10（OWASP 总览 + A03 注入）→ 02-auth（OAuth 2.0 / JWT）|
| 进阶 | 2-3 周 | 03-crypto → 04-network |
| 高级 | 2-3 周 | 05-container → 06-zero-trust |
| 实战 | 持续 | 配套 Cloud / ai / system-design 实战案例 |

---

**适用读者**：Web 开发者 / 后端工程师 / 安全工程师 / SRE / 架构师 / AI 工程师（关注 LLM 安全）。

**前置知识**：HTTP 协议、Linux 命令行、至少一门后端语言、基础数据库 SQL。
