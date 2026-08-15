# check-links.py — 死链扫描器使用说明

## 用途
BFS 扫描 sites-hub 内部链接（仅同源），输出 dead link 列表。
适用场景：
1. CI 自动检测（推荐在 release job 跑，扫描 release 产物）
2. 本地预发布验证
3. 生产环境巡检（需注意 limit_req）

## 用法

### 1) 本地离线扫描（推荐）
```bash
# 起静态服务（无 nginx，无 limit_req）
cd release/sites-hub/www && python3 -m http.server 8083 &

# 跑扫描（concurrency=2, delay=0.1s 足够）
python3 sites-hub/scripts/check-links.py \
  --base http://localhost:8083 \
  --depth 2 \
  --concurrency 2 \
  --delay-ms 0.1
```

### 2) 生产 nginx 巡检（受 limit_req 限制）
```bash
# limit_req zone=auth rate=10r/m burst=20
# 要穿透限流，每个请求至少间隔 6 秒
python3 sites-hub/scripts/check-links.py \
  --base https://java-px.bot.cd \
  --depth 1 \
  --concurrency 1 \
  --delay-ms 6 \
  --user "$SITES_HUB_USER:$SITES_HUB_PASS"
```

### 3) JSON 输出（接 CI / 监控）
```bash
python3 sites-hub/scripts/check-links.py --json > dead-links.json
# exit code: 0=全 OK, 1=有 dead link
```

## 输出字段
```json
{
  "base": "http://localhost:8083",
  "checked": 191,
  "by_status": {"200": 188, "404": 3},
  "dead": [
    {"url": "...", "status": 404, "ms": 1.2, "error": "Not Found"}
  ]
}
```

## 限制
- **只扫同源链接**：跨域 href 跳过
- **跳过 fragment / javascript: / mailto: / tel:**：这些不是 dead link
- **depth=N**：BFS 深度；depth=1 = 仅 28 子站根 + 首页
- **默认排除 noindex**：尊重页面 robots meta
- **不扫静态资源**（assets/）：有 long cache 不需要

## 性能
- 静态环境：约 2-5 秒扫完首页 + 28 子站 + BFS 1 层
- 受限流环境：depth=1 约 28 × 6s = 3 分钟

## 与 nginx limit_req 协同
T3 防爆破配置 `limit_req zone=auth burst=20 nodelay` 会拒绝高频请求。
扫描器两种应对：
1. **降速**：`--concurrency 1 --delay-ms 6`（默认单线程 6s/请求，匹配 10r/m）
2. **CI 跑静态服务**：本工具最常见场景，CI 用 `python3 -m http.server` 跑 release 产物，无 limit_req

## 已知场景
- MOCK_BUILD 后子站 `.vitepress/dist/` 缺失 → 28 子站全 503（这是 build 问题不是 link 问题，先跑 `MOCK_BUILD=0 bash build-release.sh` 重新 build）
