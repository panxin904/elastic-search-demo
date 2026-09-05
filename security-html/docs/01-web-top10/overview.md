---
title: OWASP Top 10 2025 概览
date: 2026-08-15  # date-auto-injected
---

# OWASP Top 10 2025 概览

![Owasp Top10 2025](/owasp-top10-2025.svg)

## 一句话总结

> **OWASP Top 10 = 业界权威 Web 安全风险清单**。**2025 版涵盖访问控制失效、注入、不安全设计、SSRF 等 10 大类**。**每条都给出"原理 + 危害 + 防御 + 实战代码"**。

---

## 什么是 OWASP

**OWASP**（Open Worldwide Application Security Project）是一个**非营利组织**，专注于改善软件安全。自 2003 年起每 3-4 年发布 **OWASP Top 10**——基于行业数据和社区共识的"最危险的 Web 应用安全风险"清单。

### 2025 版 10 大类

| ID | 名称 | 中文 | 核心风险 |
|----|------|------|----------|
| A01 | Broken Access Control | 访问控制失效 | 越权访问、IDOR |
| A02 | Cryptographic Failures | 加密机制失效 | 明文存密码、弱算法 |
| A03 | Injection | 注入攻击 | SQL/NoSQL/命令注入 |
| A04 | Insecure Design | 不安全设计 | 缺乏威胁建模 |
| A05 | Security Misconfiguration | 安全配置错误 | 默认密码、目录遍历 |
| A06 | Vulnerable & Outdated Components | 易受攻击组件 | Log4Shell 级别 |
| A07 | Identification & Authentication Failures | 认证失效 | 弱口令、Session 缺陷 |
| A08 | Software & Data Integrity Failures | 软件数据完整性 | 不安全反序列化、供应链 |
| A09 | Security Logging & Monitoring Failures | 日志与监控失效 | 攻击痕迹丢失 |
| A10 | Server-Side Request Forgery (SSRF) | SSRF | 内网探测、元数据窃取 |

## 2025 vs 2021 主要变化

| 变化 | 详情 |
|------|------|
| **新增** | A04 Insecure Design（"设计阶段"独立成类） |
| **新增** | A08 Software & Data Integrity Failures（合并旧版 A8+A10） |
| **新增** | A10 SSRF（独立成类，旧版只是 A10:2021 的一部分） |
| **调整** | A07 改名（从 Auth Failures 到 Identification & Auth Failures） |
| **降级** | XML External Entity (XXE) 不再独立（合并到 A05） |

## 为什么 OWASP Top 10 重要

1. **行业基准**：PCI-DSS（支付卡行业标准）要求审计时引用 OWASP Top 10
2. **招聘必备**：安全工程师面试必考 Top 10
3. **开发清单**：每条都是"必做"清单（"我有没有防 A03？"）
4. **风险沟通**：技术 / 非技术人都能理解的"通用语言"

## 实战：审计一个 Web 应用

```bash
# 1. 静态扫描（找代码层漏洞）
npm install -g snyk
snyk test

# 2. 动态扫描（找运行时漏洞）
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://example.com

# 3. 依赖扫描（找 A06 漏洞）
npm audit
pip-audit
```

## 防御总原则

| 原则 | 落地 |
|------|------|
| **白名单优于黑名单** | 输入校验、权限控制 |
| **最小权限** | API scope、数据库用户权限 |
| **纵深防御** | WAF + RASP + 代码层 + 框架层 |
| **默认安全** | 安全配置 hardening、加固清单 |
| **可观测** | 关键操作日志 + 异常告警 |

## 关联章节

- **02-auth**：A01 / A07 详细攻防
- **03-crypto**：A02 加密算法选型
- **04-network**：A05 TLS 配置
- **05-container**：A06 / A08 供应链
- **06-zero-trust**：A04 不安全设计 → 零信任架构

## 一句话总结

> **OWASP Top 10 2025 = 10 大类风险 + 每条原理 + 危害 + 防御 + 实战**。**从最常见的 A03 注入开始学，逐步覆盖 A01 访问控制 / A02 加密 / A10 SSRF**。
