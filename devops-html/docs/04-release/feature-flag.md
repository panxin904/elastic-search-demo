---
title: Feature Flag
date: 2026-08-15  # date-auto-injected
---

# Feature Flag（特性开关）

Feature Flag 是代码内的开关，通过配置中心动态启用 / 关闭 / 灰度功能，不需要重新部署。

## 一句话总结

> **Feature Flag = 配置驱动的代码开关**。**核心：代码内置 + 配置中心 + 用户分群**。**适用：新功能试用 / 多变体 / Kill Switch**。**挑战：Flag 治理（清理过期 Flag）**。

---

## 4 大使用场景

```
1. Kill Switch（紧急关闭）
   新功能出问题，秒级关闭，不需要回滚

2. Canary Release（用户分群）
   内部用户 / Beta 用户先体验，逐步放量

3. A/B Testing（多变体）
   对比不同实现的转化率 / 性能

4. Trunk-Based Development
   主干开发，Flag 控制未完成功能
```

## 自建 Feature Flag 模式

```typescript
// 简单实现：基于配置文件 + 缓存
import { featureFlags } from './flags';

async function checkout(req: Request) {
    if (await featureFlags.isEnabled('new-checkout', {
        userId: req.user.id,
        attributes: { country: req.user.country },
    })) {
        return newCheckoutFlow(req);
    } else {
        return legacyCheckoutFlow(req);
    }
}
```

```typescript
// flags.ts
const flags: Record<string, RolloutStrategy> = {
    'new-checkout': {
        type: 'percentage',
        percentage: 10,             // 10% 用户
        userWhitelist: [1, 2, 3],   // 内部用户强制开启
    },
    'beta-feature': {
        type: 'attribute',
        attribute: 'user.tier',
        values: ['beta', 'enterprise'],
    },
};

// 缓存（避免每次请求查 DB）
const cache = new Map<string, { value: boolean; expires: number }>();

async function isEnabled(flag: string, context: Context): Promise<boolean> {
    const key = `${flag}:${context.userId}`;
    const cached = cache.get(key);
    if (cached && cached.expires > Date.now()) {
        return cached.value;
    }

    const value = evaluate(flags[flag], context);
    cache.set(key, { value, expires: Date.now() + 60000 });
    return value;
}
```

## 商业方案

| 方案 | 特点 |
|------|------|
| **LaunchDarkly** | SaaS / 功能完整 / 价格高 |
| **Unleash** | 开源 / 自托管 / 功能丰富 |
| **Split.io** | 企业级 / A/B 测试集成 |
| **Statsig** | 新兴 / 现代化 / 实验功能强 |
| **自建** | 简单场景 / 节省成本 |

## Unleash 自托管示例

```typescript
import { UnleashClient } from 'unleash-proxy-client';

const unleash = new UnleashClient({
    url: 'https://unleash.example.com/api/frontend',
    clientKey: 'xxx',
    appName: 'my-app',
});

unleash.on('ready', () => {
    if (unleash.isEnabled('new-checkout')) {
        // 启用
    }
});
```

```yaml
# Unleash Toggle 配置（Web UI）
name: new-checkout
type: gradual-rollout
rollout: 100%           # 启用 100%
stickiness: userId       # 按用户稳定分桶
```

## Flag 治理

```
# 1. Flag 生命周期
created → in-use → (deprecated) → removed

# 2. Owner 制度
每个 Flag 必须有 owner（团队或个人）

# 3. 过期时间
创建时强制设置过期时间（如 90 天），过期前提醒

# 4. 死代码清理
定期 grep 未使用 Flag，PR 移除

# 5. 度量
- Flag 总数（越少越好）
- Flag 存活时间
- 死代码比例
```

## 反模式

```
❌ 反模式 1：Flag 嵌套（if(flagA) { if(flagB) {} }）
✅ 正确：扁平 Flag，避免组合爆炸

❌ 反模式 2：长期 Flag（超过 6 个月还在）
✅ 正确：定期清理，过期前 promote 或删除

❌ 反模式 3：Flag 没有 owner
✅ 正确：每个 Flag 都有 owner，Slack 提醒

❌ 反模式 4：测试不覆盖 Flag 分支
✅ 正确：Flag 各分支都要测（包括灰度比例）

❌ 反模式 5：滥用 Flag 做权限控制
✅ 正确：权限用 RBAC，Flag 做产品功能
```

## 关联章节

- **04-release/overview**：5 大发布策略
- **04-release/canary**：金丝雀发布
- **04-release/blue-green**：蓝绿发布

## 一句话总结

> **Feature Flag = 产品发布的瑞士军刀**。**何时用：频繁发布 / 多变体 / 需要 Kill Switch**。**何时不用：变更极少 / 团队小 / 治理能力弱**。


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
