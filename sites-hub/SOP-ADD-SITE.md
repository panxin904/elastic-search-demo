# SOP — 新增站点到 sites-hub

> 本文档替代旧的 "sed 增量改 nginx" 流程。
> 自 2026-08-13 起，所有脚本（build-release.sh / deploy-vps.sh / start.sh / start-all.sh / start-hub.py / conf/nginx.conf）
> 都从 `scripts/sites.sh` 读 SITES 数组作为**唯一真相源**。

## 1. 改动清单（3 处）

| # | 文件 | 改动 |
|---|------|------|
| 1 | `sites-hub/scripts/sites.sh` | 在 `SITES=(...)` 数组末尾追加新站点 URL 路径段 |
| 2 | `sites-hub/www/index.html` | 在合适分类（backend/data/frontend/ai 等）下加一张 `.card` |
| 3 | `~/work_space/elastic-search-demo/<新>-html/` | 新建 VitePress 项目（含 `.vitepress/config.mts` 与 `docs/`） |

> 例外：如果 VitePress 项目目录名 ≠ URL 路径段，在 `sites.sh` 的 `PROJECT_DIR_MAP` 里声明，如 `cloud:springcloud-html`。

## 2. 校验（必做）

```bash
bash sites-hub/scripts/check-sites.sh
```

期望输出：`✓ check-sites: all consistency checks passed`。

校验内容（12 项）：

- SITES 数组长度 == 28
- `www/index.html` 卡片数 == SITES 长度
- `conf/nginx.conf` location 块数 == SITES 长度
- `deploy-vps.sh` source 了 `sites.sh` 且使用 `${SITES[@]}`
- `start-hub.py` 使用 `SITES_CSV` 环境变量
- `start.sh` / `start-all.sh` source 了 `sites.sh`
- 卡片 href / nginx path 与 SITES 完全匹配
- 所有 SITES 对应的项目目录存在

## 3. 本地预览（可选）

```bash
# 渲染 nginx 配置（含 28 个 location + 6 个安全头）
bash sites-hub/scripts/render-nginx-conf.sh

# 启动 nginx + 本地预览
bash sites-hub/start.sh            # 优先用 nginx（端口 8081），失败回退 Python（端口 8080）
# 或: bash sites-hub/start-all.sh  # 纯 nginx 一键启动
```

## 4. 发布到 VPS

```bash
# 1. 本地构建（28 站全部 build；MOCK_BUILD=1 复用已有 dist 仅用于 dry-run）
cd ~/work_space/elastic-search-demo
bash sites-hub/build-release.sh

# 2. 上传 release/sites-hub-static.tar.gz 到 VPS（参考 deploying-vps-sites-hub skill）
SSHPASS='<root-password>'
sshpass -p "$SSHPASS" scp release/sites-hub-static.tar.gz \
    root@38.207.171.83:/tmp/

# 3. 在 VPS 上 stage + 原子切换 current 软链 + nginx reload
sshpass -p "$SSHPASS" ssh root@38.207.171.83 bash << 'REMOTE'
set -e
mkdir -p /tmp/sites-hub-stage
cd /tmp/sites-hub-stage
tar xzf /tmp/sites-hub-static.tar.gz

RELEASE_BASE=/var/www/sites-hub/releases
CURRENT=/var/www/sites-hub/current
NEW="$(date +%Y%m%d%H%M%S)"
NEW_DIR="$RELEASE_BASE/$NEW"

mkdir -p "$NEW_DIR"
cp -a "$CURRENT/." "$NEW_DIR/"                 # 复制其他 27 个站
for s in $(bash -c "source /tmp/sites-hub-stage/scripts/sites.sh; echo \"\${SITES[*]}\""); do
  cp -a "/tmp/sites-hub-stage/sites-hub/$s" "$NEW_DIR/$s"
done
ln -sfn "$NEW_DIR" "$CURRENT"

# overlay freshly built www/
cd /var/www/sites-hub/current
tar xzf /tmp/sites-hub-stage/sites-hub/www.tar.gz 2>/dev/null || \
    rsync -a /tmp/sites-hub-stage/sites-hub/www/ www/

# 老版本清理（保留最近 5 个）
ls -1dt "$RELEASE_BASE"/*/ 2>/dev/null | tail -n +6 | xargs -r rm -rf

nginx -t && nginx -s reload
REMOTE

# 4. 验证
AUTH='admin:<password>'
for p in "/" "/<新站点>/"; do
  printf "%-50s " "$p"; curl -s -o /dev/null -w "%{http_code}\n" \
    -u "$AUTH" "https://java-px.bot.cd$p"
done
```

## 5. 踩过的坑（历史记录）

| 症状 | 原因 | 现在怎么防 |
|------|------|------------|
| `401` 全站 | 旧 admin 密码不匹配 | 用 `htpasswd -b -i` 覆盖；deploy-vps.sh 加 `chown root:www-data` |
| `500` 全站 | `chmod 640` 后 www-data 读不到 htpasswd | deploy-vps.sh 已经 `chown root:www-data /etc/nginx/.sites-hub.htpasswd` |
| 首页看不到新卡片 | `cp -a "$CURRENT/."` 覆盖了新 www/ | overlay freshly built www/ 那一步必须做 |
| 从首页点新站 404 | nginx 缺 location | 现在不可能 — sites.sh 是唯一来源，render-nginx-conf.sh 自动生成 |

## 6. 回滚

```bash
sshpass -p "$SSHPASS" ssh root@38.207.171.83 "
  CURRENT=/var/www/sites-hub/current
  PREV=\$(ls -1dt /var/www/sites-hub/releases/*/ | sed -n '2p')
  ln -sfn \"\$PREV\" \"\$CURRENT\"
  nginx -s reload
"
```
