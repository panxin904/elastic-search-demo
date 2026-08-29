---
title: 知识图谱
date: 2026-08-15  # date-auto-injected
---

# 🌐 Spring Cloud 知识图谱

> 全局可视化展示 Spring Cloud Alibaba 的 **20+ 核心概念** 与它们之间的关系。
> 💡 提示：拖动节点调整布局，点击节点跳转对应文档，悬停查看高亮关系。

<KnowledgeGraph :height="700" src="/graph.json" />

## 📊 节点分类统计

| 分类 | 节点数 | 代表概念 |
|---|---|---|
| 🍃 Spring Boot | 5 | 快速开始 / 自动配置 / 事务 |
| ☁️ Spring Cloud Alibaba | 1 | 总览 |
| 🌐 Nacos | 3 | 服务发现 / 配置中心 / 命名空间 |
| 🚪 Gateway | 3 | 基础 / 路由 / 过滤器 |
| ⚖️ 负载均衡 | 2 | LoadBalancer / 策略 |
| 🔐 认证授权 | 3 | Security / OAuth2 / 认证中心 |
| 🛡️ Sentinel + Seata | 2 | 流控 / 分布式事务 |

## 💡 学习路径建议

按照知识图谱的依赖关系，推荐学习顺序：

1. **Spring Boot 基础** → 自动配置原理 → Web → 数据访问 → 事务
2. **Spring Cloud Alibaba 总览** → Nacos 服务发现 → Nacos 配置中心
3. **Gateway 网关** → 路由与断言 → 过滤器
4. **负载均衡** → 策略
5. **认证授权** → Security → OAuth2 + JWT → 统一认证中心
6. **Sentinel + Seata** → 综合实战

每学完一个节点，点击图谱上对应节点即可跳转到详细文档。