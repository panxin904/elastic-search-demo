---
title: CDN 内容分发网络
date: 2026-08-15  # date-auto-injected
---

# CDN 内容分发网络

<div class="nt-badge nt-badge-app">应用层</div>
<div class="nt-badge nt-badge-cloud">基础设施</div>

CDN（Content Delivery Network）通过在**全球部署边缘节点**，让用户从**最近的节点**获取内容，显著降低延迟、减轻源站压力。

## 1. 为什么需要 CDN

| 问题 | CDN 解决 |
| --- | --- |
| 跨地域延迟高 | 边缘节点就近服务 |
| 源站带宽压力大 | 边缘节点承担大部分流量 |
| 突发流量（DDoS / 秒杀） | 边缘吸收 + 限速 |
| 静态资源传输慢 | 多节点 + 链路优化 |

## 2. CDN 工作原理

```
用户 → DNS 智能解析 → 最近边缘节点 → （缓存未命中）→ 源站
                                  ↓
                          缓存返回用户
```

1. 智能 DNS 返回**最近节点** IP
2. 浏览器访问边缘节点
3. 节点有缓存 → 直接返回
4. 无缓存 → 回源拉取 + 缓存

## 3. CDN 关键组件

| 组件 | 作用 |
| --- | --- |
| 边缘节点（Edge） | 离用户最近，提供内容 |
| 二级节点（Mid-tier） | 中间层缓存 |
| 源站（Origin） | 原始内容 |
| 调度系统（GSLB） | 全局负载均衡 |
| 配置中心 | 缓存规则、HTTPS、回源策略 |

## 4. 调度方式

| 方式 | 原理 |
| --- | --- |
| DNS 调度 | 智能 DNS 解析到最近节点 |
| HTTP 302 | 客户端第一次访问，返回 302 跳到边缘 |
| Anycast BGP | 多机房同 IP，路由选最近 |
| 客户端 SDK | APP 内置调度 |

## 5. 缓存策略

### 5.1 缓存维度

| 维度 | 粒度 |
| --- | --- |
| URL | 同一资源缓存 |
| 参数 | 区分 `?v=1` / `?v=2` |
| Host | 不同域名独立缓存 |
| Cookie | 按用户区分（一般不缓存） |

### 5.2 缓存控制

```
Cache-Control: max-age=3600              客户端缓存
Cache-Control: s-maxage=7200            CDN 缓存
Cache-Control: public / private         公开 / 私有
Cache-Control: no-cache / no-store      不缓存
Cache-Control: stale-while-revalidate   后台刷新
```

### 5.3 主动刷新

- **URL 刷新**：CDN 控制台/API 清除指定 URL
- **目录刷新**：批量清理
- **预热（Push）**：主动把资源推送到边缘

## 6. 回源策略

| 策略 | 说明 |
| --- | --- |
| 优先回源 | 主源站可用时直接回源 |
| 备源回源 | 主源失败回备源 |
| 回源协议 | HTTPS / HTTP / 跟随 |
| 回源 Host | 指定回源域名 |
| Range 回源 | 支持分片 |
| 304 协商 | 带 If-Modified-Since 节省带宽 |

## 7. 动静分离

- **静态资源**（HTML、CSS、JS、图片、字体、视频）走 CDN
- **动态请求**（API、表单提交）走源站
- 大型站点常用"动静分离"：动态 ASP.NET 走源站，静态资源走 CDN

## 8. HTTPS 与 CDN

| 问题 | 方案 |
| --- | --- |
| 证书部署 | CDN 平台统一签 / 上传自有证书 |
| 性能 | 启用 TLS 1.3、HTTP/2、HTTP/3 |
| 回源 HTTPS | 源站也配证书 |
| OCSP Stapling | 边缘预取 OCSP，加速握手 |

## 9. 常见 CDN 服务商

| 厂商 | 特点 |
| --- | --- |
| Cloudflare | 全球 Anycast，免费 + 企业版 |
| Akamai | 老牌，CDN 之父 |
| AWS CloudFront | 与 AWS 深度集成 |
| 阿里云 CDN | 国内市场份额大 |
| 腾讯云 CDN | 音视频场景强 |
| Fastly | 边缘计算（Edge Compute） |

## 10. 边缘计算（Edge Computing）

现代 CDN 不止缓存，还能在边缘运行代码：

- **Cloudflare Workers**：JS / WASM
- **Fastly Compute@Edge**：WASM
- **Deno Deploy**：JS

应用：AB 测试、灰度、鉴权、限流、个性化

## 11. 性能指标

| 指标 | 目标 |
| --- | --- |
| 命中率 | 静态资源 > 95% |
| 首字节时间（TTFB） | < 100ms |
| 回源率 | 越低越好 |
| 边缘可用性 | > 99.99% |

## 12. CDN 调试

```bash
# 查询调度
dig www.example.com +short
nslookup www.example.com 8.8.8.8

# 查请求来源
curl -I -H "Host: example.com" https://1.2.3.4/index.html

# 看是否回源
curl -I -H "Cache-Control: no-cache" https://example.com/
```

## 13. 常见面试题

1. **CDN 解决了什么问题？** 延迟、源站压力、抗攻击。
2. **CDN 命中过程？** 客户端 → DNS → 边缘节点 →（未命中）→ 回源 → 缓存。
3. **怎么判断命中？** 看响应头 `X-Cache: HIT` / `Via`。
4. **CDN 回源怎么配置？** 协议、HTTPS 证书、回源 Host、Range。
5. **CDN 缓存更新怎么办？** 主动刷新 URL / 目录 / 预热。
6. **动静分离原则？** 静态走 CDN，动态回源。

<!-- svg-injected:do-not-edit -->

![cdn flow](/cdn-flow.svg)
