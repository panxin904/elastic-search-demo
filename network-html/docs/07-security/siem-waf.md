---
title: SIEM 与 WAF
---

# SIEM 与 WAF

<div class="nt-badge nt-badge-security">网络安全</div>
<div class="nt-badge nt-badge-cloud">运营</div>

SIEM（安全信息与事件管理）和 WAF（Web 应用防火墙）是企业安全运营的核心组件，分别从**全局事件**和**应用层攻击**两个维度提供防护。

## 1. SIEM 概念

**SIEM = SI（M） + EM**

- **SIM**（Security Information Management）：日志收集、规范化、存储
- **SEM**（Security Event Management）：实时关联分析、告警、响应

## 2. SIEM 核心能力

| 能力 | 说明 |
| --- | --- |
| 日志收集 | 防火墙、IDS、服务器、APP |
| 范式化 | 不同源统一为标准字段 |
| 关联分析 | 跨源事件匹配规则 |
| 威胁检测 | 已知 IOC / 行为分析 |
| 告警 | 邮件 / 短信 / 工单 |
| 报告 | 合规、统计 |
| 取证 | 事件回溯 |

## 3. 主流 SIEM

| 产品 | 厂商 |
| --- | --- |
| Splunk | Splunk |
| QRadar | IBM |
| ArcSight | Micro Focus |
| Elastic Security | Elastic |
| Sentinel | Microsoft |
| Chronicle | Google Cloud |
| 360 安全运营 | 360 |
| 安恒 | 安恒信息 |

## 4. SIEM 部署

```
各类日志源 → 日志采集器（Beats/Fluentd/Agent）
                          ↓
                     消息队列（Kafka）
                          ↓
                  解析/范式化（Logstash/Stream）
                          ↓
                     存储（ES/ClickHouse）
                          ↓
                 关联分析（规则引擎 + ML）
                          ↓
                 告警 → SOC 团队
```

## 5. 检测用例

```yaml
# 例：暴力破解登录
rule:
  name: ssh_bruteforce
  condition: |
    event.action == "auth.failed"
    AND event.app == "ssh"
    AND count(event.target_user, 5m) > 10
  severity: high
  actions:
    - alert
    - block_ip
```

```yaml
# 例：横向移动
rule:
  name: lateral_movement
  condition: |
    event.action == "auth.success"
    AND event.app == "smb"
    AND count(event.source_ip, 1h) > 5
    AND count(distinct event.target_host, 1h) > 3
  severity: critical
```

## 6. 威胁情报（CTI）

- **IOC**：IP、域名、Hash、URL
- **TTP**：战术、技术、过程
- 来源：MISP、AlienVault OTX、ThreatBook、微步在线

## 7. SOAR

- **S**ecurity **O**rchestration, **A**utomation, **R**esponse
- 自动响应剧本（Playbook）
- 厂商：Cortex XSOAR（Demisto）、Splunk SOAR、Phantom

## 8. WAF 概念

**WAF**（Web Application Firewall）专门保护 Web 应用，识别应用层攻击。

## 9. WAF 部署模式

| 模式 | 说明 |
| --- | --- |
| 反向代理 | WAF 在前端 |
| 透明桥接 | 串联 |
| 云 WAF | CDN/云厂商服务 |
| RASP | 应用内嵌（如 OpenRASP） |

## 10. 检测模式

| 模式 | 描述 |
| --- | --- |
| 签名检测 | 正则匹配已知攻击 |
| 行为分析 | 偏离基线报警 |
| 机器学习 | 异常流量识别 |
| 信誉库 | 拦截已知恶意 IP |

## 11. 主流 WAF

| 产品 | 类型 |
| --- | --- |
| ModSecurity | 开源，规则库 OWASP CRS |
| Cloudflare WAF | 云端 |
| AWS WAF | 云端 |
| Azure WAF | 云端 |
| 长亭雷池 | 国内开源 |
| 阿里云 WAF | 国内云端 |
| F5 ASM | 硬件 |

## 12. ModSecurity 示例

```apache
SecRuleEngine On
SecRule REQUEST_METHOD "@streq POST" \
    "id:1001,\
     phase:1,\
     deny,\
     status:403,\
     log,\
     msg:'POST to /admin blocked'"
```

## 13. 误报与漏报

| 指标 | 说明 |
| --- | --- |
| 误报（FPR） | 正常流量被拦 |
| 漏报（FNR） | 攻击未拦 |
| 平衡 | 调规则、灰度 |

## 14. 应急响应流程

```
1. 告警触发
2. 一线 SOC 初步判断
3. 升级 → 二线分析
4. 遏制（隔离 / 限速 / 封 IP）
5. 根除（清除后门 / 修复漏洞）
6. 恢复（监控 / 验证）
7. 复盘（写报告 / 加固）
```

## 15. 合规框架

| 框架 | 适用 |
| --- | --- |
| ISO 27001 | 通用信息安全管理 |
| 等保 2.0 | 中国等级保护 |
| GDPR | 欧盟数据保护 |
| PCI DSS | 支付卡 |
| HIPAA | 美国医疗 |
| SOC 2 | 服务业 |
| NIST CSF | 美国框架 |

## 16. 常见面试题

1. **SIEM 核心？** 日志收集、范式化、关联分析、告警、报告。
2. **SOAR 干什么？** 自动化响应剧本。
3. **WAF 模式？** 反向代理、透明、云、RASP。
4. **ModSecurity 是什么？** 开源 WAF + OWASP CRS 规则。
5. **如何平衡误报漏报？** 调规则、灰度、机器学习。
6. **应急响应流程？** 告警 → 判断 → 遏制 → 根除 → 恢复 → 复盘。
