---
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
