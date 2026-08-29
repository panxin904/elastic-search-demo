---
title: A10 SSRF 服务端请求伪造
date: 2026-08-15  # date-auto-injected
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
aws ec2 modify-instance-metadata-options     --instance-id i-xxx     --http-tokens required     --http-put-response-hop-limit 1
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


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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
