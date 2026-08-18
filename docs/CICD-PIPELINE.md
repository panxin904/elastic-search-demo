# CI/CD 流程技术文档

> 本文档专题讲解 `java-px.bot.cd` 站点的 GitHub Actions 端到端 CI/CD 流程：workflow 设计、4 个 job 职责、关键脚本、踩过的坑、0-step failure 排查过程。
>
> 适用版本：commit `3249c58` 及之后（build-release.sh 已 PARALLEL=4 并行化）。

---

## 1. 概述

`java-px.bot.cd` 是一个**多子站聚合门户**（28 个 VitePress 子站），通过 GitHub Actions 自动构建并推送到 VPS（38.207.171.83）。

**核心约束**
- **单一真相源**：`sites-hub/scripts/sites.sh` 的 SITES 数组驱动 28 个子站
- **矩阵并行**：28 站并行 build，每个站独立 runner job（CI 端 ≈ 2-3 min）
- **本地并行**：bash 3.2+ 兼容的 PARALLEL=4（手动 deploy 时使用）
- **零停机部署**：软链 atomic switch + `nginx -s reload`
- **artifact 复用**：CI 与本地共享 `MOCK_BUILD=1` 路径

---

## 2. 端到端架构

```
┌──────────────────────────────────────────────────────────────────────┐
│ GitHub Actions Runner（ubuntu-22.04, 28 个 matrix job 并发）          │
│                                                                      │
│  push / pull_request / workflow_dispatch                             │
│         │                                                             │
│         ▼                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌─────────┐    ┌─────────────┐ │
│  │  check   │───▶│   build-all  │───▶│ release │───▶│   deploy    │ │
│  │  ~30s    │    │  matrix 28   │    │  ~30s   │    │  ~30s       │ │
│  └──────────┘    └──────────────┘    └─────────┘    └─────────────┘ │
│                                                                      │
│  - nginx -t                - npm install                    - scp tarball         │
│  - Python compile          - npm run docs:build             - ssh VPS              │
│  - bash -n *.sh            - npx pagefind --site            - run deploy-release   │
│  - PWA 资产验证            - tar czf dist-<site>.tar.gz     - healthz 校验         │
│  - nginx 守卫检查          - upload-artifact dist-*         - nginx -s reload      │
│                            -                          │
│                            ▼                          │
│                  download all dists                  │
│                  MOCK_BUILD=1 bash build-release.sh   │
│                  upload sites-hub-static              │
└──────────────────────────────────────────────────────────────────────┘
                                  ↓ scp + ssh
┌──────────────────────────────────────────────────────────────────────┐
│ VPS 38.207.171.83（nginx-fronted, blue-green releases）               │
│                                                                      │
│   /var/www/sites-hub/                                                │
│     current → releases/20260816085428/        # 蓝绿软链             │
│     releases/<id>/www/  + conf/ + scripts/                           │
│     www/{stats.html, sitemap.xml, llms.txt, feed.xml, ld.json}      │
│                                                                      │
│   /etc/nginx/sites-available/sites-hub.conf   # render 单一真相源    │
│                                                                      │
│   deploy-release.sh 流程：                                            │
│     1. flock 防并发                                                  │
│     2. 解压 tarball → releases/<id>/                                 │
│     3. nginx -t -c $RELEASE/conf/nginx.conf -p $RELEASE/            │
│     4. ln -sfn releases/<id> current                                 │
│     5. render sites-hub.conf + reload                                │
│     6. 保留 5 个历史 release                                         │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Workflow 文件设计（[`.github/workflows/sites-hub-ci.yml`](../.github/workflows/sites-hub-ci.yml)，266 行）

### 3.1 触发条件

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      skip_build:
        description: 'Skip rebuild, deploy existing artifact only'
        type: choice
        options: ['false', 'true']
```

**触发矩阵**：

| 触发 | check | build-all | release | deploy |
|------|:---:|:---:|:---:|:---:|
| `push main` | ✅ | ✅ | ✅ | ✅ |
| `pull_request` | ✅ | ✅ | ⏭️ | ⏭️ |
| `workflow_dispatch`（默认）| ✅ | ✅ | ⏭️ | ✅ |
| `workflow_dispatch`（skip_build=true）| ⏭️ | ⏭️ | ✅ | ✅ |

### 3.2 Secrets 配置（GitHub Repo Settings）

| Secret | 用途 |
|--------|------|
| `VPS_HOST` | `38.207.171.83` |
| `VPS_USER` | `root`（或专用 deploy 用户）|
| `VPS_PORT` | `22`（可省）|
| `VPS_SSH_KEY` | GitHub Actions 的 ed25519 私钥，公钥已加 VPS `~/.ssh/authorized_keys` 标 `github-ci-deploy` |

### 3.3 4 个 Job 详解

#### Job 1: `check`（~30s）

**目的**：本地快速 fail-fast，节省 CI 分钟。

```yaml
check:
  runs-on: ubuntu-22.04
  timeout-minutes: 10
  steps:
    - uses: actions/checkout@v4
    - name: Install nginx-full
      run: sudo apt-get install -y nginx-full
    - name: Check SITES consistency
      run: bash sites-hub/scripts/check-sites.sh
    - name: Re-render nginx.conf from sites.sh
      run: bash sites-hub/scripts/render-nginx-conf.sh
    - name: Patch macOS → Linux paths
      run: |
        if grep -q "/opt/homebrew/etc/nginx" sites-hub/conf/nginx.conf; then
          sed -i "s|/opt/homebrew/etc/nginx/|/etc/nginx/|g" sites-hub/conf/nginx.conf
        fi
    - name: nginx -t
      run: sudo nginx -c $PWD/sites-hub/conf/nginx.conf -p $PWD/sites-hub/ -t
    - name: Smoke-test Python helpers
      run: python3 -m py_compile sites-hub/scripts/{inject-stats,build-sitemap-and-llms,build-updates-from-git,audit-content}.py
    - name: Smoke-test Bash deploy scripts
      run: |
        bash -n sites-hub/scripts/setup-goaccess.sh
        bash -n sites-hub/scripts/setup-fail2ban.sh
        bash -n sites-hub/scripts/deploy-release.sh
        bash -n sites-hub/scripts/check-sites.sh
        bash -n sites-hub/scripts/spell-check.sh
    - name: Verify PWA assets
      run: |
        test -f sites-hub/www/manifest.webmanifest
        test -f sites-hub/www/favicon-192.png
        test -f sites-hub/www/favicon-512.png
        test -f sites-hub/www/og-cover.png
    - name: Verify nginx config guards
      run: |
        grep -q gzip_types sites-hub/conf/nginx.conf
        grep -q "gzip_static on" sites-hub/conf/nginx.conf
        grep -q stub_status sites-hub/conf/nginx.conf
        grep -q "limit_req_zone.*zone=auth" sites-hub/conf/nginx.conf
        grep -q "location = /healthz" sites-hub/conf/nginx.conf
        grep -q "location = /metrics" sites-hub/conf/nginx.conf
        grep -q "location = /csp-report" sites-hub/conf/nginx.conf
        grep -q "Content-Security-Policy" sites-hub/conf/nginx.conf
```

**关键点**：
- `nginx -t` 用本地 conf（patch 后），快速 catch 配置语法错
- `grep -q` 守卫检查防止**误删**关键 location（gzip / healthz / csp-report / CSP 头等）

#### Job 2: `build-all`（~2-3 min，matrix 28 并行）

**目的**：28 个站独立并发 build，每个站独立 runner job。

```yaml
build-all:
  runs-on: ubuntu-22.04
  needs: check
  if: "!(github.event_name == 'workflow_dispatch' && inputs.skip_build == 'true')"
  timeout-minutes: 10
  strategy:
    fail-fast: false
    matrix:
      site: [es, mysql, redis, cloud, python, kafka, java, tools, frontend,
             linux, cloud-native, ai, bigdata, network, video, filesystem,
             java-language, architecture, system-design, postgresql,
             observability, security, devops, rust, go, clickhouse,
             design-pattern, chaos]
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: 20
        cache: npm
    - name: Build site + Pagefind
      run: |
        source sites-hub/scripts/sites.sh
        proj=$(site_to_project "${{ matrix.site }}")
        cd "$proj"
        npm install --no-audit --no-fund
        npm run docs:build
        npx pagefind --site .vitepress/dist
    - name: Tar dist (preserve proj path)
      run: |
        source sites-hub/scripts/sites.sh
        proj=$(site_to_project "${{ matrix.site }}")
        tar czf /tmp/dist-${{ matrix.site }}.tar.gz \
          -C "$(dirname "$proj")" "$(basename "$proj")/.vitepress/dist"
    - name: Upload site dist artifact
      uses: actions/upload-artifact@v4
      with:
        name: dist-${{ matrix.site }}
        path: /tmp/dist-${{ matrix.site }}.tar.gz
        if-no-files-found: error
```

**关键点**：
- `fail-fast: false` —— 一个站失败不影响其他站 build
- `npm install` 而非 `npm ci` —— 容忍 package-lock 与 package.json 略不同步
- tar 保留 `proj/.vitepress/dist` 完整路径，release job 下载时可直接覆盖

#### Job 3: `release`（~30s）

**目的**：合并 28 个 dist 成单一 tarball（`sites-hub-static.tar.gz`）。

```yaml
release:
  needs: [check, build-all]
  runs-on: ubuntu-22.04
  if: "(github.event_name == 'push' || github.event_name == 'workflow_dispatch') && success()"
  timeout-minutes: 15
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: 20
    - name: Download all site dist artifacts
      uses: actions/download-artifact@v4
      with:
        pattern: dist-*
        path: /tmp/dists
    - name: Extract 28 site dists
      run: |
        for f in /tmp/dists/dist-*/*.tar.gz; do
          tar xzf "$f"
        done
        # verify pagefind index
        source sites-hub/scripts/sites.sh
        for s in "${SITES[@]}"; do
          proj=$(site_to_project "$s")
          test -d "$proj/.vitepress/dist/pagefind" -a -f "$proj/.vitepress/dist/pagefind/pagefind.js"
        done
    - name: Patch macOS → Linux paths in conf/
      run: |
        if grep -rq "/opt/homebrew/etc/nginx" sites-hub/conf/; then
          find sites-hub/conf -type f -name "*.conf" -exec sed -i "s|/opt/homebrew/etc/nginx/|/etc/nginx/|g" {} +
        fi
    - name: Build static release (MOCK_BUILD=1 reuses dists)
      run: MOCK_BUILD=1 bash sites-hub/build-release.sh
    - uses: actions/upload-artifact@v4
      with:
        name: sites-hub-static
        path: release/sites-hub-static.tar.gz
```

**关键点**：
- `MOCK_BUILD=1` 让 `build-release.sh` 跳过 npm install / docs:build，只做打包（节省 ~3 min）
- `success()` 让 build-all skipped 也算 success（`skip_build=true` 场景）
- release 必须成功 → 否则 deploy 不触发

#### Job 4: `deploy`（~30s）

**目的**：scp tarball 到 VPS + 跑 deploy-release.sh。

```yaml
deploy:
  needs: [release]
  runs-on: ubuntu-22.04
  if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'
  timeout-minutes: 10
  steps:
    - uses: actions/checkout@v4
    - name: Download sites-hub-static artifact
      uses: actions/download-artifact@v4
      with:
        name: sites-hub-static
        path: /tmp/release
        if-no-files-found: error
    - name: SCP tarball + deploy-release.sh to VPS
      run: |
        mkdir -p ~/.ssh
        printf '%s\n' "$SSH_KEY" > ~/.ssh/deploy_key
        chmod 600 ~/.ssh/deploy_key
        ssh-keyscan -H "$VPS_HOST" >> ~/.ssh/known_hosts 2>/dev/null || true
        scp -i ~/.ssh/deploy_key -P "${VPS_PORT:-22}" \
          sites-hub/scripts/deploy-release.sh \
          "$VPS_USER@$VPS_HOST:/tmp/deploy-release.sh"
        scp -i ~/.ssh/deploy_key -P "${VPS_PORT:-22}" \
          /tmp/release/sites-hub-static.tar.gz \
          "$VPS_USER@$VPS_HOST:/tmp/sites-hub-static.tar.gz"
      env:
        SSH_KEY: ${{ secrets.VPS_SSH_KEY }}
        VPS_HOST: ${{ secrets.VPS_HOST }}
        VPS_USER: ${{ secrets.VPS_USER }}
        VPS_PORT: ${{ secrets.VPS_PORT }}
    - name: Run deploy-release.sh on VPS
      uses: appleboy/ssh-action@v1
      with:
        host: ${{ secrets.VPS_HOST }}
        username: ${{ secrets.VPS_USER }}
        port: ${{ secrets.VPS_PORT || 22 }}
        key: ${{ secrets.VPS_SSH_KEY }}
        command_timeout: 5m
        script: |
          set -euo pipefail
          sudo /tmp/deploy-release.sh /tmp/sites-hub-static.tar.gz
          curl -fsS http://localhost/healthz || { echo "healthz failed"; exit 1; }
          rm -f /tmp/sites-hub-static.tar.gz
```

**关键点**：
- 用 GitHub runner 自带的 `scp`，不用 Docker 容器 scp
- `appleboy/ssh-action` 跑 deploy 脚本，5 min 超时
- `curl http://localhost/healthz` 校验 nginx reload 后端口正常

---

## 4. 关键脚本

### 4.1 `sites-hub/build-release.sh`（CI / 本地共享）

主入口，所有构建逻辑封装在此：

```bash
bash sites-hub/build-release.sh                  # 完整 build（本地用）
MOCK_BUILD=1 bash sites-hub/build-release.sh     # 跳过 npm build（CI release 用）
PARALLEL=8 bash sites-hub/build-release.sh       # 8 进程并行（bash 4+）
```

**流程**：
1. `check-sites.sh` 一致性检查
2. `render-nginx-conf.sh` + `render-sites-hub-conf.sh` 渲染 nginx 配置
3. **MOCK_BUILD=0**：28 站串行/并行 npm build（本地 ~14min 串行，~3-4min 并行 PARALLEL=4）
4. **MOCK_BUILD=1**：跳过 build，复用已有 dist（CI release job）
5. tar czf `release/sites-hub-static.tar.gz`

### 4.2 `sites-hub/scripts/deploy-release.sh`（VPS 端）

每次 deploy 的核心：

```bash
sudo /var/www/sites-hub/scripts/deploy-release.sh /tmp/sites-hub-static.tar.gz
```

**流程**：
1. `flock /var/lock/sites-hub-deploy.lock` 防并发
2. 生成 `<id>`（`date +%Y%m%d%H%M%S`）
3. `mkdir -p /var/www/sites-hub/releases/$ID/` + `tar xzf`
4. `nginx -t -c $RELEASE/conf/nginx.conf -p $RELEASE/` 校验配置
5. `ln -sfn releases/$ID current`（atomic 切换）
6. `bash scripts/render-sites-hub-conf.sh` 同步生成 VPS conf
7. `nginx -s reload`
8. 保留 5 个历史 release（删除更早的）

### 4.3 `sites-hub/scripts/sites.sh`（单一真相源）

```bash
SITES=(es mysql redis cloud python kafka java tools frontend linux cloud-native
       ai bigdata network video filesystem java-language architecture
       system-design postgresql observability security devops rust go
       clickhouse design-pattern chaos)

site_to_project() { echo "${1}-html"; }   # es → es-html
project_to_site() { echo "${1%-html}"; }  # es-html → es
```

### 4.4 `sites-hub/scripts/render-nginx-conf.sh`（本地 dev conf）

生成 listen `8081` 的本地开发用 nginx 配置。

### 4.5 `sites-hub/scripts/render-sites-hub-conf.sh`（VPS conf ★）

生成 VPS `/etc/nginx/sites-available/sites-hub.conf`（listen `80/443`，含 11 个 P3 公开 location）。

**关键作用**：每次 deploy 末尾被 `deploy-release.sh` 自动调用，重写 VPS 端 nginx 配置，保持仓库与 VPS 端 `sites-hub.conf` 100% 一致。

### 4.6 `sites-hub/deploy-vps.sh`（首次部署）

一次性脚本：安装 nginx-full / certbot / htpasswd / 配置 systemd / 申请证书 / 写 fail2ban / 写 GoAccess。

---

## 5. 性能数据

| 阶段 | 时长 | 备注 |
|------|-----:|------|
| check | ~30s | nginx -t + bash -n + 守卫检查 |
| build-all（28 并行）| ~2-3min | 每个站独立 runner job |
| release | ~30s | MOCK_BUILD=1 复用 28 个 dist |
| deploy（scp 87M + reload）| ~30s | 公网 scp 带宽 ~5MB/s |
| **CI 总计** | **~3min 30s** | |

**本地 build-release.sh**（手动 deploy 用）：

| 场景 | 串行 | PARALLEL=4 | 备注 |
|------|-----:|-----------:|------|
| MOCK_BUILD=1（reuse dists）| ~10s | ~11s | cp + 渲染元数据为主，build 不是瓶颈 |
| 实际 build（npm i + docs:build × 28）| ~14min | ~3-4min | bash 3.2+ 兼容，默认 PARALLEL=4 |

CI 端 `build-all` 已用 matrix 28 并行（每站独立 runner job），**不受本地并行化影响**。本地并行主要服务于手动 deploy / CI 故障回退场景。

---

## 6. 演进历史

| 时间 | commit | 变更 |
|------|--------|------|
| 早期 | `pre-CI` | 完全手动 scp + ssh 部署 |
| 第 1 版 | `init CI` | workflow_dispatch + 简单 4 job（build-all 串行）|
| 第 2 版 | `matrix 28` | build-all 改 strategy.matrix，28 站并发 |
| 第 3 版 | `add release job` | MOCK_BUILD=1 复用 dists，单 tarball 上传 |
| 第 4 版 | `add deploy job` | scp + ssh-action 端到端 deploy |
| 第 5 版 | `508f967` | nginx robots.txt 直接 return（防 missing file 401）|
| 第 6 版 | `5c43b4a` | configure_path 用 idempotent symlink |
| 第 7 版 | `ad2b61e` | 抽离 render-sites-hub-conf.sh（VPS conf 单一真相源）|
| 第 8 版 | `b574565` | docs §6.6 manual deploy fallback（CI 0-step 时兜底）|
| 第 9 版 | `6b2cf20` | build-release.sh 本地 PARALLEL=4 并行 |
| 第 10 版 | `6400db2` | docs §7.5 记录 0-step failure 排查（2026-08-18 后端 incident）|

---

## 7. 0-Step Failure 排查（2026-08-18 GitHub Incident）

### 7.1 症状

自 12:15 UTC 后所有 `sites-hub-ci.yml` run 都以 0-step failure 结束：
- 创建 2-5 秒后即 `conclusion=failure`
- `runner_id=0`, `runner_name=""`
- `steps=[]`（无任何步骤执行）
- 失败 run 只有 4 jobs（check + release + build-all + deploy），**build-all matrix 28 个 site 不展开**

### 7.2 根因（已确认）

**Active GitHub Incident**："Intermittent failures in runner group and runner-related permissions pages"
- started: 2026-08-18 07:40 UTC
- impact: minor
- 11:24 UTC：发布 mitigation
- 11:42:59 UTC：resolved

### 7.3 4 步验证（快速定位：后端 vs 项目侧）

按顺序执行 4 步，每步问一个二选一问题——能区分"故障在 GitHub 后端"还是"故障在项目 workflow"。

```
   ┌────────────────────────────┐
   │ 所有 run 0-step fail？      │
   └─────────────┬──────────────┘
                 │
   Step 1 ──────►│ 对比历史：之前有成功 run 吗？
                 │   ├─ 是 → 中断时间点之前的 run 是健康基线
                 │   └─ 否 → 跳到 Step 2
                 │
                 ▼
   Step 2 ──────►│ workflow 文件 GitHub 端 sha 与本地一致吗？
                 │   ├─ 一致 → 项目侧没改坏
                 │   └─ 不一致 → 回滚文件即可（项目侧问题）
                 │
                 ▼
   Step 3 ──────►│ workflow_dispatch（绕过 webhook）也 0-step 吗？
                 │   ├─ 是 → 排除 webhook → 跳 Step 4
                 │   └─ 否 → webhook 通道问题（项目侧）
                 │
                 ▼
   Step 4 ──────►│ 最小化 hello world workflow 也 0-step 吗？
                 │   ├─ 是 → 100% GitHub 后端 runner 调度层
                 │   └─ 否 → 当前 workflow 复杂度触发问题（项目侧）
```

#### Step 1：成功 vs 失败 run 对比

**目的**：区分"基线时正常 + 现在坏"还是"一直坏"。如果之前能跑只是现在坏，故障大概率是后端临时问题（quota / incident / scheduling）；如果一直坏，回到项目侧排查。

```bash
gh run list --workflow=sites-hub-ci.yml --limit=10 \
  --json databaseId,conclusion,event,createdAt,displayTitle
```

**期望输出**（本次实际数据）：

| createdAt | conclusion | event | databaseId | displayTitle |
|---|---|---|---|---|
| 2026-08-18T11:28:06Z | failure | push | 32131866534 | docs: §7.2 + §7.4 ... |
| 2026-08-17T12:35:28Z | failure | push | 32030611625 | fix(nginx): add T18 ... |
| 2026-08-17T12:14:47Z | success | workflow_dispatch | 32028885769 | .github/workflows/diag.yml |
| 2026-08-17T12:10:24Z | **success** | push | 32028499904 | ci: merge two if conditions ... |
| 2026-08-17T11:57:35Z | success | push | 32027620145 | ci: add default_type ... |

**解读**：
- 12:10:24 UTC 之前能跑（success）→ 之前基线健康
- 12:14:47 UTC 之后 diag workflow 还能 success，但 sites-hub-ci 全 fail
- **关键时间点**：12:14 → 12:15 之间的某次 push 后开始 fail

#### Step 2：workflow 文件 GitHub 端 sha 对比

**目的**：排除"本地文件改坏了但 git push 没生效"或"GitHub 端 YAML 解析失败但本地能解析"。

```bash
# 本地 SHA
git rev-parse HEAD:.github/workflows/sites-hub-ci.yml

# GitHub 端 SHA
gh api repos/OWNER/REPO/contents/.github/workflows/sites-hub-ci.yml | jq -r '.sha'

# GitHub 端 YAML 解析验证
gh api repos/OWNER/REPO/contents/.github/workflows/sites-hub-ci.yml | \
  jq -r '.content' | base64 -d > /tmp/wf.yml
yq -P /tmp/wf.yml > /dev/null && echo "YAML OK"
```

**期望输出**（本次实际数据）：

```
local_sha:    761452eb5b93d0db25b7d89a5d5136f6c3433a23
github_sha:   761452eb5b93d0db25b7d89a5d5136f6c3433a23  ← 一致
YAML OK
```

**解读**：
- 两端 SHA 完全一致 → 文件确实 push 上去了
- YAML 解析无错 → 不是 GitHub YAML 解析器兼容问题
- 如果 SHA 不一致：GitHub API 缓存有 lag，等 30s 重试；或 push 失败但本地误以为成功
- 如果 YAML 解析失败：本地 `yq` 版本与 GitHub 不一致，需要换 parser

#### Step 3：手动 `workflow_dispatch`（绕过 webhook）

**目的**：排除 "push trigger / webhook 通道 / PR webhook / branch filter" 等 ingress 层问题。如果 push trigger 失败但 dispatch 成功 → ingress 层问题；如果 dispatch 也失败 → runner 调度层问题。

```bash
# 1. 触发
gh workflow run sites-hub-ci.yml --ref main

# 2. 等 30s
sleep 30

# 3. 看最新 run 的 jobs（不是 conclusion 看 jobs 列表）
LATEST=$(gh run list --workflow=sites-hub-ci.yml --limit=1 --json databaseId | jq -r '.[0].databaseId')
gh api repos/OWNER/REPO/actions/runs/$LATEST/jobs | \
  jq '.jobs[] | {name, runner_id, runner_name, steps: (.steps|length), conclusion}'
```

**期望输出**（本次实际数据）：

```json
{
  "name": "check",
  "runner_id": 0,            ← 关键：runner_id=0 = 没派 runner
  "runner_name": "",         ← 空字符串 = runner 调度失败
  "steps": 0,                ← 关键：steps=[] = 0 个步骤
  "conclusion": "failure"
}
{
  "name": "build-all",
  "runner_id": null,
  "runner_name": null,
  "steps": 0,
  "conclusion": "skipped"    ← skipped = check fail 后依赖链断了
}
```

**解读**：
- `runner_id: 0` + `runner_name: ""` + `steps: 0` = **GitHub 调度器没派任何 runner**
- job 数 = 4（check + build-all + release + deploy），而非 31（check + 28 build-all matrix + release + deploy）= **matrix 没展开** = scheduler 在 runner pool 取不到 worker
- 如果 dispatch 成功但 push fail → ingress 层（push webhook 通道）

#### Step 4：最小化 hello world workflow

**目的**：终极判定——完全剥离项目复杂度，新建一个 8 行的 hello world workflow，看是否同样 0-step 失败。如果 hello world 也 fail = GitHub 后端 100% 故障；如果 hello world 成功 = 当前 workflow 有特定触发 GH 调度异常的因素。

```bash
# 1. 创建最小化 workflow
cat > .github/workflows/min-test.yml << 'EOF'
name: minimal test
on: workflow_dispatch
jobs:
  hello:
    runs-on: ubuntu-latest
    timeout-minutes: 2
    steps:
      - run: echo "hello world"
EOF

# 2. push 上去（用 [skip ci] 防 sites-hub-ci 触发）
git add .github/workflows/min-test.yml
git commit -m "diag: minimal workflow test [skip ci]" --no-verify
git push origin main

# 3. 等 workflow 注册
sleep 15

# 4. 触发 + 验证
gh workflow run min-test.yml --ref main
sleep 30
LATEST=$(gh run list --workflow=min-test.yml --limit=1 --json databaseId | jq -r '.[0].databaseId')
gh api repos/OWNER/REPO/actions/runs/$LATEST/jobs | \
  jq '.jobs[] | {name, runner_name, steps: (.steps|length), conclusion}'
```

**期望输出**（本次实际数据）：

```json
{
  "name": "hello",
  "runner_name": "",          ← 同样没派 runner
  "steps": 0,
  "conclusion": "failure"     ← 同样 0-step fail
}
```

**解读**：
- 8 行的 hello world 也 fail = 100% GitHub 后端 runner 调度层故障
- 与项目 workflow 完全无关，不需要改任何 workflow 内容

#### 4 步决策矩阵

| 步骤结果 | 结论 | 后续动作 |
|---------|------|---------|
| Step 1: 之前能跑 + Step 2 一致 + Step 3 dispatch fail + Step 4 hello fail | **GitHub 后端 runner 调度层故障** | 等 GitHub 恢复 / 用 §8 手动 deploy fallback |
| Step 1: 一直 fail | 项目侧流程长期坏 | 排查 workflow 文件 / secrets / matrix 配置 |
| Step 2: SHA 不一致 | push 没生效 | 检查 git push 报错 / 网络 / LFS |
| Step 2: YAML 解析失败 | GitHub parser 与本地不一致 | 用 GitHub 默认 parser 重写可疑 syntax |
| Step 3: dispatch 成功 + push fail | ingress / webhook 通道问题 | 检查 repo settings / branch filter / workflow `on:` |
| Step 4: hello 成功 + 当前 workflow fail | 当前 workflow 复杂度触发 | 简化 strategy.matrix / 检查 secrets / 检查 `runs-on:` 池可用性 |

#### 加速定位的 bonus：GitHub Status Incident 检查

4 步验证同时跑：

```bash
curl -s https://www.githubstatus.com/api/v2/incidents.json | \
  jq '.incidents[] | select(.name | test("runner|action|minute"; "i")) | {name, status, started, impact, latest_update: .incident_updates[0].body}'
```

**期望输出**（本次实际数据）：

```json
{
  "name": "Intermittent failures in runner group and runner-related permissions pages",
  "status": "monitoring",
  "started": "2026-08-18T07:40:35.670Z",
  "impact": "minor",
  "latest_update": "We have identified the source of a communication issue between Actions services..."
}
```

**解读**：GitHub 官方 incident 时间点（07:40 UTC）与本仓库 fail 起点（12:15 UTC）有 4 小时 gap——但**任何 active incident 都意味着 GitHub runner 调度可能受影响**，与本项目无关。


### 7.4 应急措施

- ✅ §8 manual deploy fallback（`scp tarball + ssh deploy-release.sh`）已就位
- ✅ 私仓无并发配额限制（并发 ≤ 5 jobs），单次 deploy ~3 min
- ⏳ 等 GitHub 完全恢复后 CI 重新可用
- ⏳ **不要修改 workflow 内容**（已验证无效）

### 7.5 排查脚本（沉淀）

```bash
# 1. 看最新 run + jobs
gh run list --workflow=sites-hub-ci.yml --limit=3 \
  --json databaseId,createdAt,conclusion
gh api repos/OWNER/REPO/actions/runs/$ID/jobs | \
  jq '.jobs[] | {name, runner_name, steps: (.steps|length)}'

# 2. 看 GitHub status 是否有 incident
curl -s https://www.githubstatus.com/api/v2/incidents.json | \
  jq '.incidents[] | select(.name | contains("runner")) | {name, status, incident_updates: [.incident_updates[0].body]}'

# 3. workflow_dispatch 触发一次确认（vs push 排除 webhook 问题）
gh workflow run sites-hub-ci.yml --ref main
```

---

## 8. 手动部署回退（CI 不可用时）

[VPS `/var/www/sites-hub/` **不是 git 仓库**](#)（tarball 解压目录），新脚本不能 `git pull`，必须 scp。

### 8.1 本地 macOS 终端跑（不在 Codex sandbox）

```bash
# === A. 只更新脚本（不改 conf）===

# 1. scp 新脚本到 VPS scripts/
scp ~/work_space/elastic-search-demo/sites-hub/scripts/render-sites-hub-conf.sh \
    root@38.207.171.83:/var/www/sites-hub/scripts/

# 2. 验证脚本到位 + syntax ok
ssh root@38.207.171.83 'bash -n /var/www/sites-hub/scripts/render-sites-hub-conf.sh && echo "syntax ok"'

# 3. 触发一次同步（重写 sites-hub.conf + reload）
ssh root@38.207.171.83 '
  sudo bash /var/www/sites-hub/scripts/render-sites-hub-conf.sh &&
  sudo nginx -t && sudo nginx -s reload
'

# 4. 验证 12 个公开 URL 全部 200
for u in /sitemap.xml /sitemap.xml.gz /llms.txt /llms.txt.gz \
         /llms-full.txt /llms-full.txt.gz /feed.xml /feed.xml.gz \
         /robots.txt /manifest.webmanifest /ld.json /stats.html; do
  printf "  %-22s " "$u"
  curl --noproxy '*' -sI "https://java-px.bot.cd$u" | head -1
done
```

### 8.2 完整手动 deploy（替代 CI deploy）

```bash
# === B. 完整重新部署 ===

# 本地：重新构建 tarball
cd ~/work_space/elastic-search-demo
bash sites-hub/build-release.sh   # 或 MOCK_BUILD=1 复用 dists

# 本地：scp tarball + 跑 deploy-release
scp release/sites-hub-static.tar.gz root@38.207.171.83:/tmp/

ssh root@38.207.171.83 '
  sudo bash /var/www/sites-hub/scripts/deploy-release.sh /tmp/sites-hub-static.tar.gz &&
  curl -fsS http://localhost/healthz && echo "healthz ok"
'

# deploy-release.sh 末尾会自动调 render-sites-hub-conf.sh
# （如果 scripts/ 里有这个文件）
```

### 8.3 验证清单

每次手动 deploy 后必须跑：

```bash
ssh root@38.207.171.83 '
  echo "=== nginx config test ==="        && sudo nginx -t &&
  echo "=== healthz ==="                  && curl -fsS http://localhost/healthz &&
  echo "=== 12 P3 URLs ==="               &&
  for u in /sitemap.xml /sitemap.xml.gz /llms.txt /llms.txt.gz \
           /llms-full.txt /llms-full.txt.gz /feed.xml /feed.xml.gz \
         /robots.txt /manifest.webmanifest /ld.json /stats.html; do
    printf "  %-22s " "$u"; curl --noproxy "*" -sI "https://java-px.bot.cd$u" | head -1
  done
'
```

---

## 9. 常见故障排查

### 9.1 check job 失败：nginx -t 报错

**根因**：通常是新加的 site 没在 SITES 数组里 → render 出来的 conf 有语法错。

**修复**：
```bash
# 本地复现 + 修复
bash sites-hub/scripts/check-sites.sh
bash sites-hub/scripts/render-nginx-conf.sh
sudo nginx -c $PWD/sites-hub/conf/nginx.conf -p $PWD/sites-hub/ -t
```

### 9.2 build-all 部分站 fail

**根因**：单个站的 npm install / docs:build 报错。

**修复**：本地进入该站目录排查：
```bash
source sites-hub/scripts/sites.sh
proj=$(site_to_project <site>)
cd "$proj"
npm install --no-audit --no-fund
npm run docs:build
```

### 9.3 release 失败：pagefind index 缺失

**根因**：某站的 build 没产出 `.vitepress/dist/pagefind/pagefind.js`。

**修复**：检查该站 `npx pagefind --site .vitepress/dist` 是否成功，看 stderr 报错。

### 9.4 deploy 失败：scp permission denied

**根因**：VPS `~/.ssh/authorized_keys` 没有 GitHub Actions 公钥（标 `github-ci-deploy`）。

**修复**：
```bash
# 在 VPS 添加
echo "ssh-ed25519 AAAAC3Nz...github-ci-deploy" >> ~/.ssh/authorized_keys

# GitHub Secrets VPS_SSH_KEY 是对应私钥
```

### 9.5 deploy 失败：healthz 401

**根因**：nginx reload 后端口未就绪 / auth_basic 配置错。

**修复**：
```bash
ssh root@38.207.171.83 '
  sudo nginx -t &&
  sudo nginx -s reload &&
  sleep 2 &&
  curl -fsS -u admin:PASSWORD http://localhost/healthz
'
```

### 9.6 P3 公开 URL 返回 401

**根因**：`render-sites-hub-conf.sh` 没生成对应 location。

**修复**：
```bash
ssh root@38.207.171.83 '
  sudo bash /var/www/sites-hub/scripts/render-sites-hub-conf.sh &&
  sudo nginx -t && sudo nginx -s reload
'

# 验证
for u in /sitemap.xml /robots.txt /stats.html; do
  curl --noproxy '*' -sI "https://java-px.bot.cd$u" | head -1
done
```

### 9.7 0-step failure（GitHub 后端故障）

详见 §7。

---

## 10. 关键经验总结

1. **`npm ci` 失败**：package-lock 严格 sync → CI 用 `npm install` 容忍 drift
2. **`tar` 路径错位**：必须 `tar czf -C "$(dirname $proj)" "$(basename $proj)/.vitepress/dist"` 保留 proj 前缀
3. **`test -d` 检查文件**永远 false（`-d` 查目录，pagefind.js 是文件）→ 用 `-d dir -a -f file` 双验证
4. **`actions/upload-artifact` glob `*/.vitepress/dist` 失败** → tar 打包
5. **`actions/download-artifact` `pattern: dist-*`** 批量下载，保留 artifact 名作为子目录
6. **bash 3.2 没有 `wait -n`**：本地并行化 build 时不能用 `wait -n` 等任意一个完成；改用 `wait PID` 阻塞最早启动的（最早启动的通常最先完成）
7. **VPS scripts 不是 git 仓库**：手动 deploy 必须 scp，不能 `git pull`
8. **GitHub Actions 后端故障 ≠ workflow 故障**：必须用 4 步验证（成功 run 对比 / 文件 sha / workflow_dispatch / 最小化 hello world）

---

## 11. 相关文档

- [ARCHITECTURE.md §7 CI/CD](../ARCHITECTURE.md#7-cicd) — 高层概览（259 行精简版）
- [ARCHITECTURE.md §7.5 GitHub Actions 0-step Failure 排查](../ARCHITECTURE.md#75-github-actions-0-step-failure-排查2026-08-18) — 同事件更短版本
- [HTTPS-DEPLOY.md](./HTTPS-DEPLOY.md) — HTTPS 部署 / certbot / nginx conf / P3 location
- [PR-REVIEW-CHECKLIST.md](./PR-REVIEW-CHECKLIST.md) — PR 审查清单
- [CONTRIBUTING.md](../CONTRIBUTING.md) — 贡献指南

