---
title: 认证与授权协议总览
---

# 认证与授权协议

## 一句话总结

> **认证 = 你是谁**（Authentication）**授权 = 你能做什么**（Authorization）**。**协议族：OAuth 2.0（授权）/ OIDC（身份层）/ JWT（令牌格式）/ SAML（XML SSO）/ Cookie Session（传统 Web）。**本章逐一拆解原理、流图、攻击面、防御**。

---

## 核心概念区分

| 术语 | 英文 | 解决 | 协议 |
|------|------|------|------|
| 认证 | Authentication | 你是谁 | OIDC / SAML / LDAP |
| 授权 | Authorization | 你能做什么 | OAuth 2.0 |
| 身份 | Identity | 你的属性 | OIDC ID Token / SAML Assertion |
| 凭证 | Credential | 证明你是你 | 密码 / Token / 证书 |

## 协议家族地图

```
┌────────────────────────────────────────────────┐
│  应用层（业务代码）                              │
├────────────────────────────────────────────────┤
│  OIDC（身份层）                  SAML 2.0      │
│  ├─ 基于 OAuth 2.0              ├─ XML 断言    │
│  └─ ID Token + UserInfo         └─ 企业 SSO    │
├────────────────────────────────────────────────┤
│  OAuth 2.0（授权框架）                          │
│  └─ 4 种 flow：authorization code / implicit    │
│     / client credentials / password            │
├────────────────────────────────────────────────┤
│  JWT（令牌格式）                                │
│  ├─ JOSE Header + Payload + Signature           │
│  └─ JWS / JWE / JWK                            │
├────────────────────────────────────────────────┤
│  传输 / 密码学                                  │
│  └─ TLS 1.3（防窃听）+ 签名算法（防篡改）       │
└────────────────────────────────────────────────┘
```

## 4 种 OAuth 2.0 Flow

| Flow | 适用 | 客户端类型 |
|------|------|----------|
| **Authorization Code** | Web 应用（最常用） | 服务端 Web App |
| **Authorization Code + PKCE** | 移动 App / SPA | 公共客户端 |
| **Client Credentials** | 服务到服务（M2M） | 后端服务 |
| **Resource Owner Password** | 遗留迁移（不推荐） | 受信第一方 |
| **Device Code** | 智能电视 / IoT | 无浏览器设备 |

## 实战：选型决策

| 场景 | 推荐 |
|------|------|
| **自家 Web 应用登录** | Spring Authorization Server / Keycloak + Authorization Code + PKCE |
| **企业内部 SSO** | OIDC（Keycloak / Auth0 / Okta） |
| **传统企业 SSO** | SAML 2.0（ADFS / Okta） |
| **小程序 / 移动 App** | Authorization Code + PKCE |
| **微服务 M2M** | Client Credentials + JWT |
| **API 第三方授权** | OAuth 2.0 + 后端校验 |

## 关联章节

- **01-web-top10/a01-broken-access**：A01 访问控制失效——授权缺失
- **01-web-top10/a07-auth-failure**：A07 认证失效——密码、Session
- **03-crypto**：JWT 签名算法（HS256 / RS256 / ES256）
- **04-network**：OIDC redirect_uri 的 HTTPS 强制

## 学习路径

1. **OAuth 2.0**（最基础，必须先学）
2. **JWT**（OAuth 2.0 的令牌载体）
3. **OIDC**（OAuth 2.0 + 身份层）
4. **Session 攻击**（传统 Web 背景）
5. **SAML**（企业 SSO 场景）
6. **MFA**（纵深防御最后一公里）

## 一句话总结

> **OAuth 2.0 = 授权标准**（4 种 flow）。**OIDC = OAuth 2.0 + 身份**（ID Token）。**JWT = 令牌格式**（自包含、防篡改）。**SAML = 企业 SSO 标准**（XML 时代遗留）。**MFA = 最后一公里**。
