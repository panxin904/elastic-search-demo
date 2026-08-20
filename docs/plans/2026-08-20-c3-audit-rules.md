# C3 审计规则扩展实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在不破坏现有薄页豁免和代码示例豁免的前提下，检测 Mermaid 代码块未闭合与 h2→h4 标题跳级。

**Architecture:** 在 `audit-content.py` 增加两个纯函数 `check_mermaid_fences` 和 `check_heading_order`，并在每篇文档扫描时、进入薄页豁免分支前调用。报告 Summary、子站表、问题清单和控制台同步输出两个指标；Dashboard 解析相同 Summary 字段形成长期趋势。

**Tech Stack:** Python 3 标准库、Markdown 报告、现有 C3 weekly workflow、静态趋势 Dashboard。

---

## 规则

1. ` ```mermaid` 未被同字符代码围栏关闭时记录起始行。
2. 只有 `h2` 之后直接出现 `h4` 或更深层级才报警；页面 `h1` 后经过 h2、h3 视为正常目录结构。
3. fenced code block 内的标题不参与检测。
4. 现有 Vue prop 数组检测已经存在，本次不重复实现。

## 验证

- 临时契约覆盖闭合/未闭合 Mermaid、h2→h4、h1→h3 和代码块内标题。
- 全量审计生成新 baseline，确认 1430 个 Markdown 文件下新指标为 0/0。
- 检查报告包含 Summary、子站表和 console summary 三个位置。
- 更新 `build-audit-dashboard.py`，确保新报告字段能被趋势页解析。
