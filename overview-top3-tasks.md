# Top 3 任务完成报告（2026-08-13）

## 任务摘要

| # | 任务 | 状态 | 验证 |
|---|------|------|------|
| 1 | 19 站启用 search | ✅ | 19/19 站 HTML 含 `id="local-search"` |
| 2 | 修复 portal chip bug | ✅ | `cnt-backend=9`、`cnt-arch=1` |
| 3 | 5 站补跨链 3-5 条 | ✅ | chaos/postgresql/clickhouse=5、devops=6、rust=5 |

**最终烟测**：28/28 站点 HTTP 200 + 门户/页脚/hero 检查全通过。

## 任务 1：19 站启用 local search

修改 `*-html/.vitepress/config.mts` 19 个，在 `themeConfig: { ... }` 内加入 `search: { provider: 'local' }`。

**踩坑**：
1. 第一次脚本 insertion 把 comma 吃掉了 → 19 站 config 全部破
2. 部分修复后还残留 orphan `  ,docFooter:` 和前一行无逗号导致 esbuild 编译失败
3. 最终用 `/tmp/restore-configs-v2.py`（3 步法）+ `/tmp/add-missing-commas.py` 全修

**build/deploy**：
- 每站 `npm run docs:build` ~10s
- 增量 stage 到 `release/sites-hub/<target>/`
- 部署后 curl 验证 19 站均含 `id="local-search"`

## 任务 2：修复 portal chip bug

**Bug**：`architecture` 卡片用 `data-cat="arch"` 但 chip 列表里没这个 cat → 点非"全部"看不到 architecture 站；`cnt-backend=8` 实际 9（chaos 加入未更新）。

**修复**（`sites-hub/www/index.html`）：
- `cnt-backend`: 8 → 9
- 新增 chip：`<button class="chip" data-cat="arch">企业架构<span class="chip-count" id="cnt-arch">1</span></button>`

**JS 自动支持**：filter 用 `cat === activeCat` 通用匹配，新 cat 自动生效。

## 任务 3：5 站补跨链

所有编辑在 `docs/index.md` 的 `## 关联站点` 段（devops/rust 是增强已有的）。

| 站 | 链接数 | 目标站点 |
|----|--------|---------|
| chaos | 5 | observability / system-design / postgresql / devops / architecture |
| postgresql | 5 | mysql / clickhouse / redis / observability / architecture |
| clickhouse | 5 | kafka / observability / mysql / postgresql / architecture |
| devops | 6 (was 5) | + chaos |
| rust | 5 (was 4) | + chaos |

**模板**：` **<site>/** → <why it's related> → 链到 \`<internal-link>\``

## 部署链路修复

**双密码问题**：之前用户改 htpasswd 为 `admin` 但 SSH 密码没改；keychain 里我又误存了 `admin`。今天用旧 SSH 密码 `8G8P47w3D7gHB1vr` 恢复后，再手动把 htpasswd 重置为 `admin`。

**关键修复**：
1. **tar 命令前缀**：必须用 `tar -czf release/sites-hub-static.tar.gz -C release sites-hub` 保留 `sites-hub/` 前缀，否则远端 `mkdir -p` 找不到路径
2. **deploy-fs.sh [5/5] htpasswd 重置 bug**：heredoc + SSHPASS 串接有问题，部署后手动 `htpasswd -b -i` 重置

## 关键脚本（沉淀到 /tmp/）

- `/tmp/restore-configs-v2.py` — VitePress config.mts 大规模 search 启用
- `/tmp/add-missing-commas.py` — search 前一行补逗号
- `/tmp/stage-changes.sh` — 增量 stage（避 30+ 分钟完整 build-release.sh）

## 量化前后对比

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| search 覆盖 | 9/28 (32%) | 28/28 (100%) |
| 跨链覆盖（5 站） | 4+0+0+5+4 = 13 | 5+5+5+6+5 = 26 |
| chip 数据一致 | 7/8 | 8/8 |