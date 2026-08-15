---
title: 开发流程 总览
---

# 开发流程

从"拿到一个需求"到"系统上线稳定运行"，完整的 Java Web 开发流程分为 13 个关键环节。

## 流程全景图

<div class="flowchart">
  <div class="step">
    <div class="step-box" style="background:#3b82f6">📋</div>
    <div class="step-label">需求分析</div>
    <div class="step-desc">理解业务</div>
  </div>
  <div class="step-arrow">→</div>
  <div class="step">
    <div class="step-box" style="background:#2563eb">📐</div>
    <div class="step-label">技术方案</div>
    <div class="step-desc">架构设计</div>
  </div>
  <div class="step-arrow">→</div>
  <div class="step">
    <div class="step-box" style="background:#1d4ed8">🗄️</div>
    <div class="step-label">数据库设计</div>
    <div class="step-desc">表结构</div>
  </div>
  <div class="step-arrow">→</div>
  <div class="step">
    <div class="step-box" style="background:#1e40af">🔌</div>
    <div class="step-label">接口设计</div>
    <div class="step-desc">API定义</div>
  </div>
  <div class="step-arrow">→</div>
  <div class="step">
    <div class="step-box" style="background:#3b82f6">💻</div>
    <div class="step-label">编码开发</div>
    <div class="step-desc">写代码</div>
  </div>
  <div class="step-arrow">→</div>
  <div class="step">
    <div class="step-box" style="background:#2563eb">🔍</div>
    <div class="step-label">代码评审</div>
    <div class="step-desc">Code Review</div>
  </div>
</div>

<div class="flowchart">
  <div class="step">
    <div class="step-box" style="background:#10b981">🧪</div>
    <div class="step-label">单元测试</div>
    <div class="step-desc">JUnit</div>
  </div>
  <div class="step-arrow">→</div>
  <div class="step">
    <div class="step-box" style="background:#059669">🔄</div>
    <div class="step-label">集成测试</div>
    <div class="step-desc">联调</div>
  </div>
  <div class="step-arrow">→</div>
  <div class="step">
    <div class="step-box" style="background:#047857">🚀</div>
    <div class="step-label">部署上线</div>
    <div class="step-desc">发布</div>
  </div>
  <div class="step-arrow">→</div>
  <div class="step">
    <div class="step-box" style="background:#a855f7">📊</div>
    <div class="step-label">监控运维</div>
    <div class="step-desc">告警</div>
  </div>
  <div class="step-arrow">→</div>
  <div class="step">
    <div class="step-box" style="background:#7c3aed">🔄</div>
    <div class="step-label">迭代优化</div>
    <div class="step-desc">改进</div>
  </div>
  <div class="step-arrow">→</div>
  <div class="step">
    <div class="step-box" style="background:#6d28d9">📝</div>
    <div class="step-label">文档沉淀</div>
    <div class="step-desc">知识库</div>
  </div>
</div>

## 核心环节

### 📋 需求阶段

| 环节 | 关键产出 | 核心问题 |
|---|---|---|
| [需求分析](/01-process/requirement-analysis) | 需求文档、验收标准 | 做什么？边界在哪？优先级？ |
| [技术方案](/01-process/tech-solution) | 技术方案文档、排期 | 怎么做？用什么技术？多久？ |

### 🏗️ 设计阶段

| 环节 | 关键产出 | 核心问题 |
|---|---|---|
| [数据库设计](/01-process/database-design) | ER图、DDL、索引设计 | 数据怎么存？怎么查得快？ |
| [接口设计](/01-process/api-design) | API文档、Mock配置 | 前后端怎么约定？入参出参？ |

### 💻 实现阶段

| 环节 | 关键产出 | 核心问题 |
|---|---|---|
| [编码开发](/01-process/coding) | 功能代码、单元测试 | 怎么写？怎么组织代码？ |
| [代码评审](/01-process/code-review) | Review意见、修正代码 | 写得对不对？好不好？ |

### ✅ 测试阶段

| 环节 | 关键产出 | 核心问题 |
|---|---|---|
| [单元测试](/01-process/unit-test) | 测试报告、覆盖率 | 每个方法对吗？边界情况？ |
| [集成测试](/01-process/integration-test) | 联调报告、回归结果 | 模块间协作对吗？ |

### 🚀 上线与运维

| 环节 | 关键产出 | 核心问题 |
|---|---|---|
| [部署上线](/01-process/deployment) | 上线检查清单、回滚预案 | 怎么发布？出问题怎么办？ |
| [监控运维](/01-process/monitoring) | 监控面板、告警规则 | 系统正常吗？有异常吗？ |
| [迭代优化](/01-process/iteration) | 优化方案、重构计划 | 哪里可以更好？技术债务？ |
| [文档沉淀](/01-process/documentation) | 知识库、操作手册 | 下次怎么做？新人怎么学？ |

## 本层在图谱中的位置

<KnowledgeGraph mode="full" :height="500" />

## 拿到需求第一件事做什么？

1. **理解业务背景**：这个需求解决什么问题？涉及哪些角色？
2. **明确验收标准**：什么状态算"做完了"？
3. **确认依赖关系**：有没有前置需求？有没有外部系统依赖？
4. **评估工作量**：前端、后端、数据库、测试分别要多少时间？
5. **拉通相关方**：前端同学、产品经理、测试同学都对齐了吗？

更多细节请看 [需求分析](/01-process/requirement-analysis)。
