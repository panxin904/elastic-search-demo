---
title: 蓝绿部署
date: 2026-08-15  # date-auto-injected
---

# 蓝绿部署 (Blue-Green)

蓝绿部署是经典的零停机发布策略，同时维护两套环境（旧=blue，新=green），通过切换流量实现秒级回滚。

## 一句话总结

> **蓝绿 = 流量切换 + 秒级回滚**。**核心：两套等价环境 + Router/LB 切换**。**适用：大版本 / 数据库 schema 变更 / 风险敏感**。**代价：资源 2 倍**。

---

## 工作流

```
时间线：
T0: blue=v1.0（生产），green=v2.0（部署完成但无流量）
T1: Router 切到 green（v2.0 接收 100% 流量）
T2: green=v2.0（生产），blue=v1.0（保留 7 天）
T3: blue 销毁

故障响应：
T1 + 5min: green 错误率飙升
T1 + 6min: Router 切回 blue（秒级回滚）
```

## K8s 实现（Service selector 切换）

```yaml
# blue（旧版本）
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
      version: blue
  template:
    metadata:
      labels:
        app: my-app
        version: blue
    spec:
      containers:
        - name: my-app
          image: my-app:v1.0
---
# green（新版本，先不接流量）
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
      version: green
  template:
    metadata:
      labels:
        app: my-app
        version: green
    spec:
      containers:
        - name: my-app
          image: my-app:v2.0
---
# Service（流量切换 = 改一行 selector）
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  selector:
    app: my-app
    version: green   # 切回 blue 就是改这一行
  ports:
    - port: 80
      targetPort: 8080
```

## Argo Rollouts 实现

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 5
  strategy:
    blueGreen:
      activeService: my-app-active
      previewService: my-app-preview
      autoPromotionEnabled: false   # 手动 promote
      scaleDownDelaySeconds: 600    # blue 保留 10 分钟
```

## 数据库 schema 变更的兼容

```sql
-- 蓝绿场景：DB schema 必须前后兼容

-- 阶段 1：新增字段（双写）
ALTER TABLE users ADD COLUMN new_email TEXT;

-- 阶段 2：旧代码读 old email 写 old + new
-- 阶段 3：新代码读 new email 写 new
UPDATE users SET new_email = email WHERE new_email IS NULL;
ALTER TABLE users ALTER COLUMN new_email SET NOT NULL;

-- 阶段 4：删除旧字段（需要所有实例都升级后才能执行）
ALTER TABLE users DROP COLUMN email;
```

## 适用 vs 不适用

```
✅ 适用
- 大版本变更（v1 → v2）
- 数据库 schema 不兼容变更
- 风险敏感（金融 / 医疗）
- 资源相对充足

❌ 不适用
- 资源敏感（成本）
- 有状态服务（DB 自身无法蓝绿）
- 长期维护两套环境成本高
- 频繁小版本发布（用金丝雀更经济）
```

## 关联章节

- **04-release/overview**：5 大发布策略对比
- **04-release/canary**：金丝雀发布
- **04-release/rollback**：回滚机制

## 一句话总结

> **蓝绿 = 最保险的发布策略**。**优势：秒级回滚 / 完整隔离**。**劣势：资源 2 倍 / DB schema 兼容挑战**。


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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
