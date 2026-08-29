---
title: CDN 全站加速
date: 2026-08-15  # date-auto-injected
---

# CDN 全站加速

<div class="nt-badge nt-badge-cases">企业案例</div>
<div class="nt-badge nt-badge-cloud">CDN</div>

通过 CDN 全站加速，将静态资源、API 动态请求优化到极致，是中大型网站的标配。

## 1. 业务背景

| 场景 | 问题 |
| --- | --- |
| 跨地域访问 | 海外慢、延迟 500ms+ |
| 静态资源 | 占带宽大头 |
| 突发流量 | 源站被打挂 |
| 移动弱网 | 连接失败率高 |

## 2. 架构设计

```
用户 → 智能 DNS → 边缘节点 → 缓存 / 回源
                          ↓
                    源站（多机房）
```

## 3. 静态资源加速

| 优化 | 做法 |
| --- | --- |
| 资源 Hash | 永久缓存 |
| 域名分片 | img1.cdn / img2.cdn |
| 合并 | sprite / 雪碧图 |
| 压缩 | gzip / brotli |
| WebP / AVIF | 现代格式 |
| 字体子集 | 减小字体文件 |
| 长缓存 | 1 年 + 哈希文件名 |
| 预连接 | `<link rel="preconnect">` |

### HTTP 头配置

```
Cache-Control: public, max-age=31536000, immutable
Content-Encoding: br
```

## 4. 动态加速（CDN-Dynamic）

适合 API、个性化内容：

| 技术 | 描述 |
| --- | --- |
| 智能选路 | 选择最佳回源路径 |
| 协议优化 | HTTP/2、HTTP/3、TLS 1.3 |
| 预连接 | 边缘预连源站 |
| 长连接复用 | 减少握手 |
| 智能压缩 | 按客户端能力 |

## 5. HTTPS 全站

```nginx
# 强制 HTTPS
server {
    listen 80;
    return 301 https://$host$request_uri;
}

# HSTS
add_header Strict-Transport-Security "max-age=63072000; preload";
```

## 6. 边缘计算

```js
// Cloudflare Workers
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  // 鉴权
  // A/B
  // 限流
  // 改写
  return fetch(request);
}
```

## 7. 性能数据

| 场景 | 改造前 | 改造后 |
| --- | --- | --- |
| 首屏 | 3.2s | 0.9s |
| LCP | 4.5s | 1.4s |
| 跳出率 | 60% | 35% |
| 带宽成本 | 100 万/月 | 30 万/月 |

## 8. 容灾

| 策略 | 描述 |
| --- | --- |
| 多 CDN | 主 + 备 |
| 智能解析 | 故障自动切换 |
| 源站多活 | 多 Region |
| 健康检查 | 实时剔除 |
| 限流 | 防止雪崩 |

## 9. 监控

| 指标 | 工具 |
| --- | --- |
| 命中率 | CDN 控制台 |
| 5xx 比例 | 实时监控 |
| 边缘节点状态 | 拨测 |
| 回源带宽 | 流量图 |

## 10. 关键决策

| 决策点 | 建议 |
| --- | --- |
| 自建 vs 云 | 流量小云 CDN，大流量混合 |
| 单一厂商 vs 多 CDN | 高可用多 CDN |
| 边缘计算 | 简单逻辑可边缘，复杂回源 |
| 协议 | HTTP/3 必开 |
| 回源策略 | 协议跟随 + Range |

## 11. 常见面试题

1. **CDN 改造的收益？** 延迟、带宽、可用性、用户体验。
2. **静态缓存怎么做？** Hash 文件名 + 长缓存。
3. **动态 CDN 怎么优化？** 智能选路、协议优化、长连接复用。
4. **多 CDN 怎么调度？** 智能 DNS + 权重 + 故障切换。
5. **CDN 改造的难点？** 缓存一致性、回源策略、HTTPS 证书。
6. **HTTP/3 在 CDN 价值？** 弱网体验显著提升。
