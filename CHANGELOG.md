# CHANGELOG

> 自动生成 by `sites-hub/scripts/build-changelog.sh`
> 范围：`90a83dd6998075b055a0ae122375972ae757e20a..HEAD` · 共 172 个 commit
> 生成时间：2026-08-25

### ✨ Features

  - feat(c2): 跨站内容关联注入 · 30 站 +152 xsite 链接（§8.60）
  - feat(game): 子站章节化完成 · 8 章 39 文件 + sidebar 9 分组（C-6 / §8.59）
  - feat(android): 子站章节化完成 · 6 章 29 文件 + sidebar 7 分组（C-5 / §8.58）
  - feat(iot): 子站章节化完成 · 6 章 35 文件 + sidebar 7 分组（C-4 / §8.57）
  - feat(game): 接入 game 站的全局配置与文档（30 → 31 站）
  - feat(game): 新增游戏开发子站（31 站，首版 6 个骨架页）
  - feat(android): 接入 android 站的全局配置与文档（29 → 30 站）
  - feat(android): 新增安卓 Android 子站（30 站，首版 6 个骨架页）
  - feat(iot): 接入 iot 站的全局配置与文档（28 → 29 站）
  - feat(iot): 新增物联网 IoT 子站（29 站，首版 6 个骨架页）
  - feat(C3): 跨子站重复标题豁免规则（234 → 188，-19.7%）
  - feat(C3): 新增 Mermaid / 标题跳级审计规则 + Dashboard 卡片扩展
  - feat(C3): add content quality trend dashboard
  - feat(C11): 新增图片转 WebP 工具
  - feat(C11): 统一 Mermaid 跨站配置并收尾文档
  - feat(C3): 薄页豁免规则（mindmap/graph/cheatsheet 不再误报）
  - feat(C3): weekly audit-content CI workflow + ROOT 兼容性
  - feat(C1): 子站结构统一化 Phase 2 - 28 站全量迁移到模板
  - feat(C1): 子站结构统一化 Phase 1 - cloud-native + ai 迁移到模板
  - feat(deploy): git remote → CI → VPS 自动部署（push to main 自动 SSH 部署）
  - feat(analytics): GoAccess stats integration (zero-dep, 30MB RAM)
  - feat(c10): PR review checklist + PR template + CONTRIBUTING update
  - feat(mermaid): SSR integration across 28 sites via vitepress-plugin-mermaid
  - feat(c9+1): integrate build-updates-from-git.py into build-release.sh
  - feat(c9): Plausible analytics + git log auto Updates
  - feat(c8): add EN translation for 34 Chinese glossary terms
  - feat(c4): Pagefind full-text search setup + portal search.html
  - feat(c5): add RSS 2.0 feed.xml for 28 sites + portal aggregation
  - feat(c12): build sitemap.xml + llms.txt for 28 sites + portal
  - feat(c6): Giscus comment component + issue templates + CONTRIBUTING.md
  - feat(c7+1): wire setupReadingProgress + shared CSS into 22 more sites
  - feat(c7): add reading progress bar JS to 5 sites
  - feat(c7): enhance reading experience CSS across shared template + 5 sites
  - feat(glossary): add 36 terms covering 6 zero-coverage sites
  - feat(audit): detect Vue prop array missing-comma bug (§8.14 lesson)
  - feat(c2): clean up 8 functional-overlap sections after WhyThisGraph injection
  - feat(c2): fix design-pattern-html double frontmatter + inject WhyThisGraph
  - feat(c2): apply WhyThisGraph to 11 custom-hero sites
  - feat(c2): apply WhyThisGraph + merge existing related-sites sections
  - feat(c2): apply WhyThisGraph + :related-sites to 5 clean sites
  - feat(c2): expand glossary to cover 4 missing sites (cloud/java/tools/devops)
  - feat(c2): add cross-site links via glossary + WhyThisGraph :related-sites
  - feat(c1): scaffold shared VitePress template + render-config tool
  - feat(tools): add spell-check.sh + fix 18 real typos

### 🐛 Bug Fixes

  - fix(audit): §8.55 continue bug + xsite_density 检测（§8.60.6/8.61）
  - fix(content): 补 22 篇剩余薄页到 200+ 字，audit baseline 薄页数 22 → 0（C-7 收尾 / §8.56）
  - fix(audit + java-language): 站点级薄页豁免 + 定位调整为速查手册（C-7 / §8.55）
  - fix(game): questions.md 3 处 `<T>` 转义为 `&lt;T>`（C-12 / §8.53.4 解锁 CI）
  - fix(springcloud): 补 WhyThisGraph.vue 组件（C-15 后续按需 → 立即修）
  - fix(audit + updates): C-1 cloud 站 SITES_DIRS 错配 / C-2 cat_map 补 4 站
  - fix(config): 修复 android / iot / game 站 nav /graph broken link + description 节点数
  - fix(CI): 'on' → 'on'（YAML 1.1 布尔陷阱）
  - fix(nginx): robots.txt 直接由 nginx 返回，避免 missing file 401
  - fix(nginx): idempotent symlink 修复 in configure_path
  - fix(nginx): add T18 public metadata locations to render-nginx-conf
  - fix(nginx): add gzip_static + P1 public metadata in deploy-vps.sh
  - fix(nginx): add gzip_static to render-nginx-conf.sh template
  - fix(deploy): create logs/ dir for nginx -t validation
  - fix(release): include conf/ in stage directory
  - fix(release): tarball top-level should be content, not sites-hub/
  - fix(deploy-vps): assets 必须公开（VitePress hydrate 401 → 裸文字）
  - fix(seo): build-sitemap-and-llms.py WWW_DIR path + integrate into build-release
  - fix(deploy-vps): add /stats.html nginx location (GoAccess public report)
  - fix(deploy-vps): non-interactive password + nginx ${CURRENT_LINK} expansion
  - fix(build): VitePress path aliases + WhyThisGraph script setup (P0)
  - fix(c2): copy WhyThisGraph.vue to 22 sites + audit detects component missing
  - fix(content): add missing frontmatter to 27 .md files (filesystem 20 + design-pattern 7)

### ⚡ Performance

  - perf(build): wait_any 替代 head-of-line blocking（PARALLEL 调度优化）
  - perf(build): parallelize build-release.sh with PARALLEL=4 (bash 3.2+ compat)
  - perf(seo): enable nginx gzip_static for pre-compressed metadata

### ♻️ Refactor

  - refactor(nginx): extract sites-hub.conf to single source of truth
  - refactor(content): extract WhyThisGraph Vue component (5 sites)

### 📚 Documentation

  - docs(audit): 更新 content-quality-2026-08-24 baseline（cloud 站 vue_missing 1→0）
  - docs(§8.53): 留底 game 接入期间 CI 失败排查报告（2026-08-23 第四十六次）
  - docs: add C3 审计规则扩展（Mermaid / 标题跳级）实施计划
  - docs: add C3 trend dashboard plan
  - docs: §8.44 + §8.45 文档收尾（薄页豁免 + build 优化）
  - docs: §8.43.6 根因纠正：GH 账户 billing 限制（非后端 incident）
  - docs: §8.43.6 线上验证发现 GH 后端 0-step failure
  - docs: §8.43 C3 weekly audit-content CI workflow + ROOT 兼容性
  - docs: §8.42 C1 子站结构统一化 Phase 1+2+3 文档收尾
  - docs: §7.3 扩展为完整 4 步验证流程（决策树 + 命令 + 期望输出 + 解读 + 决策矩阵）
  - docs: add CICD-PIPELINE.md (652 行) + ARCHITECTURE §11 索引
  - docs: §7.5 记录 2026-08-18 GitHub Actions 0-step failure 排查（后端 incident）
  - docs: §7.2 + §7.4 记录 build-release.sh 并行化
  - docs: add §6.6 manual deploy fallback (CI 0-step 时 scp 兜底)
  - docs: add HTTPS-DEPLOY.md (certificate / nginx render / deploy sync)
  - docs(architecture): mark CODEOWNERS done, note branch protection limit
  - docs: fix P2 Mermaid SSR documentation inconsistency
  - docs(ARCHITECTURE): 架构与开发参考文档（12 节，743 行）
  - docs(OPTIMIZATION-CONTENT): record §8.39 mermaid CSR 真实验证（3 张 SVG 渲染成功）
  - docs(OPTIMIZATION-CONTENT): record §8.38 build-all parallelization (5× CI speedup)
  - docs(OPTIMIZATION-CONTENT): record §8.35 CI debugging 5 commits to green
  - docs(OPTIMIZATION-CONTENT): record §8.29 C11 image optimization
  - docs(OPTIMIZATION-CONTENT): record §8.28 C4 Pagefind setup
  - docs(OPTIMIZATION-CONTENT): record §8.27 C5 RSS feed
  - docs(OPTIMIZATION-CONTENT): record §8.26 C12 sitemap + llms.txt
  - docs(OPTIMIZATION-CONTENT): record §8.25 C6 Giscus + issue templates + CONTRIBUTING
  - docs(OPTIMIZATION-CONTENT): record §8.24 C7 27-site mass migration
  - docs(OPTIMIZATION-CONTENT): record §8.23 C7 reading progress JS
  - docs(OPTIMIZATION-CONTENT): record §8.22 C7 CSS enhancement
  - docs(OPTIMIZATION-CONTENT): record §8.21 C2 component fix + C-task re-prioritization
  - docs(OPTIMIZATION-CONTENT): record §8.20 glossary 6-site zero coverage fix
  - docs(OPTIMIZATION-CONTENT): record §8.19 audit Vue prop bug check
  - docs(OPTIMIZATION-CONTENT): record §8.18 cleanup + C2 full closure
  - docs(OPTIMIZATION-CONTENT): record §8.17 design-pattern fix + C2 complete
  - docs(OPTIMIZATION-CONTENT): record §8.16 :related-sites batch 3 (11 sites)
  - docs(OPTIMIZATION-CONTENT): record §8.15 :related-sites batch 2 (6 sites)
  - docs(OPTIMIZATION-CONTENT): record §8.14 :related-sites batch 1 (5 sites)
  - docs(OPTIMIZATION-CONTENT): record §8.13 glossary 4-site expansion
  - docs(OPTIMIZATION-CONTENT): record §8.12 C2 cross-site links
  - docs(OPTIMIZATION-CONTENT): record §8.11 spell-check baseline
  - docs(OPTIMIZATION-CONTENT): record §8.10 WhyThisGraph extraction
  - docs(OPTIMIZATION-CONTENT): add §8.8/§8.9 fix records (FM + git init)

### 🔧 Chore

  - chore(C3): 删除 cloud-html 孤儿残站 + §8.54 治理留底（2026-08-24 第四十七次）
  - chore: dist + www build refresh (wait_any 优化后)
  - chore: dist + www build refresh (C1 后全量重建)
  - chore(C3): audit baseline + audit-content.py 三处检测修复 + bigdata lineage 内容扩充
  - chore: dist + www build refresh (Updates + lastBuildDate 刷新)
  - chore: gitignore hc-test.conf (nginx -t 临时文件)
  - chore: add CODEOWNERS for path-based reviewer assignment
  - chore(P2): retire build-with-pagefind.sh
  - chore(es-html): remove 10 unused PNG screenshots

### 📦 Other

  - diag: remove test workflows (GitHub backend incident, not our config)
  - diag: minimal workflow test
  - diag: test which runner pool works (ubuntu-22/latest/24)
  - ci: try ubuntu-latest + timeout [skip ci]
  - ci: simplify vps-fix to test SSH channel [skip ci]
  - ci: one-off VPS fix - add missing .gz locations via base64 [skip ci]
  - ci: diag - add missing .gz locations via sed
  - ci: list VPS gz locations
  - ci: add missing .gz locations via simple sed
  - ci: check VPS gz aliases
  - ci: add missing .gz locations + dedupe sitemap default_type
  - ci: fix all .gz aliases
  - ci: merge two if conditions in release job
  - ci: simplify release if to success()
  - ci: quote if expression to avoid YAML/expr parsing issue
  - ci: release runs even when build-all skipped
  - ci: release no longer needs build-all
  - ci: add default_type application/gzip
  - ci: add application/gzip mime
  - ci: dump mime types
  - ci: check VPS mime types
  - ci: verify VPS sed effect
  - ci: one-off diag to fix VPS alias paths
  - ci: one-off diag to check alias path
  - ci: one-off diag to inspect VPS nginx config
  - ci: one-off diag for gzip_static verification
  - ci: add one-off VPS diag workflow (workflow_dispatch)
  - ci: trigger deploy with checkout step
  - ci(deploy): add checkout step for scp deploy-release.sh
  - ci(deploy): scp latest deploy-release.sh to VPS
  - ci(release): patch macOS Homebrew paths before tar
  - ci(deploy): split SCP and SSH into separate steps
  - ci(deploy): merge SCP + SSH into single ssh-action
  - ci: quote if expression to avoid YAML !tag parsing
  - ci: fix workflow_dispatch skip_build semantics
  - ci(github): fix pagefind verify (`-d` on file always false → `-d dir -a -f file`)
  - ci(github): properly preserve proj path in matrix tar
  - ci(github): fix tar path in matrix build (preserve proj/.vitepress/dist)
  - ci(github): use npm install (not npm ci) for lockfile tolerance
  - ci(github): parallelize build-all via 28-job matrix (CI ~25min → ~3min)
  - ci(github): use tar to bundle dists (glob upload-artifact 找不到文件)
  - ci(github): pass dists via artifact (build-all → release)
  - ci(github): minimal viable workflow (check + build-all + release, drop lighthouse)
  - ci(github): simplify upload-artifact (multiline path → single glob)
  - ci: retrigger
  - ci(github): fix lighthouse url → urls array
  - ci(github): install nginx-full instead of nginx-light
  - ci(github): patch nginx.conf macOS → Linux paths in check job
  - ci(github): enable 4-job pipeline with 28-site build + Pagefind verification

---

**说明**：基于 Conventional Commits（feat/fix/docs/refactor/chore/perf）自动分类。
Updates 列表（首页）仅展示 `feat` / `fix` / `refactor`。
