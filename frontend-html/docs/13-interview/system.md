---
title: 系统设计题
---

# 系统设计题

> 面试常考的"大型"题：电商 / 内容 / 协作 / 实时。

## 🧭 答题套路

```
1. 需求澄清（3-5 questions）
   - 规模（DAU / QPS）
   - 核心场景
   - 一致性要求
2. 高层架构
   - 客户端 → CDN/Edge → LB → 服务 → 存储
3. 数据模型
4. API 设计
5. 关键问题深入
6. 监控 / 容错 / 扩展
```

## 📦 1. 短链系统 (TinyURL)

```
用户输入 https://example.com/blog/long-article-id-12345
  │ Hash / Base62
  ▼
短链 https://t.cn/aBcDeF
  │
  ▼ 用户访问时
重定向到长链
```

**关键设计**：
- **发号器**：自增 ID / 雪花 / Hash
- **Hash 算法**：MD5 → 取前 N 位 / CRC32
- **冲突处理**：追加 1 字符再 Hash
- **存储**：MySQL / Redis（缓存）+ 异步落库
- **301 vs 302**：301 永久（缓存到浏览器），302 临时（每次查，便于统计）

**进阶**：
- 限流（同 IP 每分钟 < 100）
- 风控（恶意 URL 拦截）
- 分析：地区 / 设备 / 时间点击分布
- 自定义短链

## 💬 2. 评论系统

```
树形评论（一级 / 二级）
批量展示（按时间倒序 / 热门）
点赞 / 反对
敏感词过滤
```

**数据模型**：
```
Comment { id, postId, userId, parentId, content, createdAt }
Like   { commentId, userId, createdAt }
```

**关键问题**：
- **分页**：cursor-based (createdAt + id)
- **树形渲染**：限制深度 2-3，过深降级
- **总数缓存**：在 Redis 缓存 `post:{id}:commentCount`
- **大 V 热门评论**：单独走"热门评论"表，先展示热门

## 📡 3. 实时协作（多人编辑）

```
Google Docs / Notion / Figma 都属于此类
```

**架构**：
```
Client A 编辑 → OT/CRDT 转换 → WebSocket → Server
                                       │
                                       ▼
                                 广播给 Client B
```

**关键技术**：
- **CRDT**：Yjs / Automerge（数据结构合并）
- **OT**：Operational Transformation
- **WebSocket**：全双工
- **Presence**：在线光标 / 状态
- **持久化**：每次编辑增量写 + 定期快照

**简化版**：把文档切分为 chunk，操作 = chunk 引用列表。

## 🔍 4. 全站搜索

```
用户搜索 "Elaticsearch"  →  自动补全 + 高亮
```

**架构**：
```
Ingest → 分词 → 倒排索引 → 存储
         Elasticsearch / OpenSearch / Meilisearch / Typesense
Query  → 拼 DSL → 命中 → 高亮
```

**实战**：
- 中文分词：`ik-analyzer`
- 同义词：业务词表
- 实时索引：变更通过 MQ 异步索引
- 自动补全：prefix query + Suggest API
- 热门搜索：Redis ZSet

## 📰 5. Feed 流（推 / 拉）

**Twitter / 微博 时间线**

**三种方案**：

| 模型 | 实现 | 一致性 | 读延迟 |
|------|------|--------|--------|
| Push 写扩散 | 发推 → 推到所有粉丝 inbox | 强 | 极快 |
| Pull 读扩散 | 读 → fanout merge | 最终 | 慢 |
| Hybrid | 活跃用户 push，长期粉丝 pull | 折中 | 中 |

代表方案：**新浪微博读扩散 → 你看前 1000 条关注的合并**。

**关键**：
- **TimelineStore**：每个用户的 inbox（push 模式）
- **Materialized View**（DB）：定期把用户时间线物化
- **分页**：cursor 模式
- **过滤**：屏蔽 / 折叠 / 已读

## 📦 6. 抢购 / 库存系统

```
库存 -1 是双写一致性问题
```

**关键**：
- **乐观锁 / Redis Lua**：`DECR` + 保留库存
- **预扣库存**：下单先扣，正向减；取消订单再回补
- **排队**：MQ 串行化
- **限流**：令牌桶 / 漏桶
- **风控**：黑名单 / 黄牛识别

**幂等**：
- 订单唯一 ID = `userId + skuId + timestamp`，Redis SETNX

## 🛒 7. 电商商品详情页

```
性能优先：高峰 100w QPS
```

**架构**：
- 多级缓存：CDN → Nginx → Redis → DB
- 静态化：商品详情静态化 + 异步刷新价格库存
- 异步加载：评价 / 推荐 / 相似商品走独立接口

**关键**：
- **三级缓存**：CDN / Redis / JVM Cache
- **雪崩**：单 key 失效 → 设置随机 TTL
- **穿仓**：缓存空值占位
- **数据一致性**：写 DB 后失效缓存（不是更新）

## 📊 8. 直播系统

```
推流 → CDN → 拉流
聊天 → IM → WebSocket / SSE
```

**架构**：
- 推流端：RTMP / WebRTC
- CDN：HLS / LL-HLS
- IM：Netty / 自研（千万级并发）
- 礼物 / 红包：MQ 异步 + 对账

## 💳 9. 支付系统

```
订单 → 第三方支付（微信/支付宝/Stripe）→ 回调
```

**关键**：
- **幂等**：商户订单号 + 唯一键约束
- **对账**：每日下载第三方账单 + T+1 核对
- **资金安全**：分布式事务（TCC / Saga）
- **状态机**：订单只能向前流转

## 🛠 10. 微前端 / 大型工程

```
多个团队 → 一份大应用
```

**方案**：
- **qiankun**：自实现沙箱 + iframe
- **Module Federation**：Webpack 5 / Vite 原生
- **micro-app**：京东方案
- **Single-SPA**：老牌

**关注点**：
- 样式隔离（CSS Module、BEM prefix）
- JS 沙箱（Proxy snapshot）
- 路由联动
- 通信（postMessage / 全局 store）
- 独立构建 + 集成发布

## 🎤 通用技巧

```
1. 先问 3-5 个澄清问题
2. 给一个 3-5k QPS 假设（便于计算）
3. 画图（画 > 说）
4. 写最关键的伪代码（核心算法 / 数据结构）
5. 列出 3 个 trade-off
6. 监控 + 容灾 + 扩容
```

## 🔗 下一步

- [高频面试题](/13-interview/basic)
- [手写代码题](/13-interview/coding)
- [Microservices / 微前端](/14-tools/micro-frontend)
