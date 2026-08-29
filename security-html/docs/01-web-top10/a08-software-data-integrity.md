---
title: A08 软件数据完整性
date: 2026-08-15  # date-auto-injected
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
