# C3 内容质量趋势 Dashboard 设计与实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 C3 每周 Markdown 审计报告转换成可公开访问的静态趋势 Dashboard，帮助快速识别内容质量指标随时间的变化。

**Architecture:** 新增 `sites-hub/scripts/build-audit-dashboard.py`，只使用 Python 标准库，扫描 `sites-hub/reports/content-quality-*.md`，解析 Summary 表的指标并生成内联 SVG 与 HTML。`build-release.sh` 在门户静态文件复制后生成 `www/audit-dashboard.html`，VPS nginx 增加公开 location，门户 footer 增加入口。

**Tech Stack:** Python 3 标准库、静态 HTML/CSS、inline SVG、Bash 3.2 兼容脚本。

---

## 方案取舍

### 采用：静态 HTML + inline SVG

- 每次 release 从本地报告重新生成，不依赖 GitHub Pages、CDN 或第三方图表库。
- 页面可被 nginx 静态托管，VPS 资源占用接近零。
- 使用最近 12 份报告；报告不足 2 份时显示最新指标与空状态，不伪造趋势。

### 不采用

- **Chart.js / ECharts**：会增加网络请求、依赖和 CSP 兼容工作。
- **GitHub Pages**：与当前 VPS 部署模型重复，billing 受限时会拖慢发布。
- **合并 `/stats.html`**：现有页面是 GoAccess 访问统计，内容质量趋势应保持独立。

## 数据流

```text
sites-hub/reports/content-quality-*.md
        │
        ▼
build-audit-dashboard.py
  ├── 文件名日期排序
  ├── Summary 表指标解析
  ├── 最近 12 份报告截断
  └── HTML + inline SVG
        │
        ▼
sites-hub/www/audit-dashboard.html
        │
        ├── build-release.sh 自动生成
        ├── nginx /audit-dashboard.html 公开
        └── 门户 footer 入口
```

## 展示指标

| 指标键 | 页面含义 | 数据来源 |
|---|---|---|
| `files` | Markdown 文件数 | `总文件数` |
| `words` | 中英混合字数 | `总字数（中英混合）` |
| `thin` | 扣除结构豁免后的薄页数 | `薄页` |
| `no_fm` | 缺少 frontmatter 的页面 | `缺 frontmatter` |
| `broken` | 内部死链数量 | `内部死链` |
| `xsite` | 跨站引用数量 | `跨站引用` |
| `dups` | 跨子站重复标题数量 | `跨子站重复标题` |

同时在最新值卡片中展示 `no_date`（frontmatter 缺 date）和 `imgs`（图片总数），不把百分比或健康状态误当作普通数值。

## 错误处理与验证

1. 报告文件名必须符合 `content-quality-YYYY-MM-DD.md`，不合法文件不进入时间序列。
2. 某项指标缺失时跳过对应 SVG；页面不生成空坐标或 `NaN`。
3. 0 份报告显示空状态；1 份报告显示最新卡片但不画趋势。
4. CLI 接受 `--reports-dir`、`--output`、`--max-weeks`，可本地重现 build-release 产物。
5. 验证命令：Python 编译、临时报告夹具 smoke test、HTML 结构断言、`build-release.sh MOCK_BUILD=1` 专项检查。

## 实施步骤

### Task 1: 实现报告解析与静态 Dashboard

**Files:**
- Create: `sites-hub/scripts/build-audit-dashboard.py`

实现报告发现、日期解析、Summary 指标解析、趋势 SVG、Delta 卡片和空状态。保持单文件、无第三方依赖。

### Task 2: 接入 release 生成

**Files:**
- Modify: `sites-hub/build-release.sh`

在 `cp -R www` 后、归档前调用 Dashboard 生成器；失败时输出 WARN，但不让非关键内容页面阻断主 release。

### Task 3: 公开 Dashboard 并增加入口

**Files:**
- Modify: `sites-hub/scripts/render-sites-hub-conf.sh`
- Modify: `sites-hub/www/index.html`

增加 `/audit-dashboard.html` 公开 location；在门户 footer 增加“内容趋势”链接。

### Task 4: 更新技术文档

**Files:**
- Modify: `sites-hub/OPTIMIZATION-CONTENT.md`

新增 §8.47，记录数据流、指标、验证结果和 billing 外部限制。

## 不在本次范围

- 不新增 GitHub Actions 定时任务；已有 `audit-content.yml`。
- 不自动把 artifact 下载到仓库；Dashboard 读取随 release 保留的本地报告。
- 不引入 Docker、Plausible self-host、Lighthouse 或额外 JS 运行时。
