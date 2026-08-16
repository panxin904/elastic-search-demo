# PR Review Checklist

> Scholar's Atlas sites-hub 仓库的 PR 审核清单。
>
> 适用于所有改动：内容 / 数据 / 脚本 / 配置 / 文档。

## 🧪 技术合规（自动 + 手动）

### CI（自动）

- [ ] **check job** 通过（nginx sanity / Python 编译 / PWA 资产）
- [ ] **build-all job** 通过（28 站 npm install + vitepress build + Pagefind 全部成功）
- [ ] **release job** 通过（如改 build-release.sh）

如果任意 CI job 红，自己改完再加 review 标签。

### 本地验证（手动，作者负责）

- [ ] 作者在 PR 描述勾选了所有本地验证项
- [ ] 改动 build 链路时，作者本地跑过 `bash sites-hub/scripts/build-with-pagefind.sh`
- [ ] 没引入新 audit 错误（`python3 sites-hub/scripts/audit-content.py`）

## 📚 内容质量（人工 review）

### frontmatter

- [ ] 新增/修改 .md 有完整 frontmatter：`title` / `description` (≤120 字) / `date`
- [ ] 没在 README.md / index.md 误用（这两文件 frontmatter 是 VitePress 自动生成的）

### 跨站关联

- [ ] 新增术语 → 已 grep 确认 glossary 没同义词
- [ ] 新术语 → 已加进 `shared-assets/glossary/keywords.json`（含 en 字段）
- [ ] 修改术语关联 → 检查 5+ 站点的 reverse 引用是否合理

### 图片 / 资源

- [ ] 没新增 PNG（用 WebP 替代）
- [ ] 图片放 `<site>-html/docs/public/images/`
- [ ] md 用 `![alt](./images/xxx.webp)` 引用
- [ ] 没新增未引用图片到根目录（已多次清理，见 §8.29）

### 主题 / 样式

- [ ] 没 hard-code 颜色（用 CSS 变量：`--vp-c-brand-1` 等）
- [ ] 没 hard-code 路径（用 `@shared/...` alias）
- [ ] Vue 组件 props 数组带逗号（漏逗号 audit 会报）

## 📐 提交规范

### commit message（Conventional Commits）

- [ ] `<type>(<scope>): <subject>` 格式
- [ ] type ∈ `feat` / `fix` / `refactor` / `docs` / `chore` / `style` / `test` / `build` / `ci` / `perf`
- [ ] scope 是子站 ID（如 `es-html`）或任务编号（如 `c2`）或组件名（如 `glossary`）
- [ ] subject 中文 ≤ 30 字，英文 ≤ 50 字符
- [ ] body（可选）解释「为什么」而非「做了什么」

### branch 命名

- [ ] `feat/<short-desc>` / `fix/<short-desc>` / `docs/<short-desc>`
- [ ] 从 `main` fork
- [ ] 不直接在 `main` 上 commit

### PR 描述

- [ ] 用了 `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] 「改了什么」具体到文件路径
- [ ] 「为什么改」有背景 / 关联 issue
- [ ] 「影响范围」勾选了所有适用项
- [ ] 「本地验证」所有 checkbox 已勾

## 🔍 数据层检查（glossary / metadata）

- [ ] `shared-assets/glossary/keywords.json` JSON 合法（`python3 -m json.tool < ...`）
- [ ] `shared-assets/glossary/keywords.json` 新术语有 `en` 字段（C8 规范）
- [ ] sitemap.xml / llms.txt / feed.xml 没人为编辑（自动生成）

## 📦 脚本 / 配置

- [ ] `sites-hub/scripts/*.py` 用 Python 3.9 兼容（不写 `str | None`）
- [ ] macOS bash 3.2 兼容（不写 `declare -A` / `mapfile`）
- [ ] 新脚本有 `--help` 和 `--dry-run`
- [ ] CI workflow 改动 → push 后看 CI log，不是看本地 yaml 解析

## 📖 文档同步

- [ ] 涉及功能改动 → 更新 `sites-hub/OPTIMIZATION-CONTENT.md` 对应章节
- [ ] 涉及 nginx 改动 → 更新 `sites-hub/OPTIMIZATION.md`
- [ ] 新增文件 → 在 `CONTRIBUTING.md` 仓库结构里登记
- [ ] 文档 commit 不写 `feat:`，用 `docs:`（不进 Updates 列表）

## ✅ 审核者责任

### SLA

- [ ] 24 小时内首次响应（即使 "先 hold，晚点看"）
- [ ] 单文件改动 → 1 个 maintainer approve
- [ ] 跨 5+ 站改动 → 2 个 maintainer approve
- [ ] 改 CI / nginx / deploy 脚本 → 必须 2 个 approve

### 沟通

- [ ] 留具体行号反馈（"第 38 行建议改成..." 而非 "这段不太好"）
- [ ] 提问而不是命令（"考虑过 X 吗？" vs "改成 X"）
- [ ] approve 后等 CI 全绿再 merge
- [ ] squash merge（保留单 commit 历史，便于 git log 生成 Updates）

### 拒绝 PR

仅在以下情况：

- 引入安全漏洞（XSS / npm 依赖漏洞）
- 故意破坏 build（删除必要文件）
- 违反 CC-BY-NC-SA 协议（内容不是原创 / 商业化）

其它情况（代码风格 / 命名）通过 review 反馈而非拒绝。

## 🚦 Merge 后

- [ ] CI 自动跑 release job → tar.gz artifact
- [ ] 手动 deploy 到 VPS（暂未自动化，见 §8.35）
- [ ] 在 Issues / Discussions 通知相关人

---

**TL;DR**：CI 全绿 + 内容规范 + commit 规范 + 文档同步 = 通过。
