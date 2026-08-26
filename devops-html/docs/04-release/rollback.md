---
title: 回滚机制
---

# 回滚机制

发布失败的快速恢复能力，决定 MTTR（Mean Time To Recover）。本章梳理回滚的 4 大要素与最佳实践。

## 一句话总结

> **回滚 = 流量切换 + DB 回退 + 配置回退 + 通知**。**目标：MTTR < 5 分钟（生产事故标准）**。**反模式：靠手工人肉回滚**。

---

## 4 大回滚要素

```
1. 流量切换
   - 蓝绿：秒级（改 Service selector）
   - 金丝雀：分钟级（Argo Rollouts abort）
   - Feature Flag：秒级（关开关）

2. 数据库回退
   - 前向兼容：旧版本代码能读新版本 schema
   - 反向迁移：DB migration 必须有 down()
   - 双写期：新旧版本都写新 schema

3. 配置回退
   - Helm values 回到上一个 Git commit
   - ArgoCD 自动同步

4. 通知
   - 失败自动 @oncall
   - Slack / PagerDuty / Lark
```

## Argo Rollouts 一键回滚

```bash
# 中止金丝雀并回滚
kubectl argo rollouts abort my-app

# 手动回滚到指定版本
kubectl argo rollouts undo my-app --to-revision=3

# 查看历史
kubectl argo rollouts history my-app
```

## GitOps 自动回滚

```yaml
# ArgoCD 检测到失败 sync 自动回滚
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  syncPolicy:
    automated:
      selfHeal: true   # 集群漂移自动修复
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

```bash
# 手动回滚（git revert + 自动 sync）
git revert HEAD
git push
# ArgoCD 自动检测 + sync + 回滚
```

## 数据库 migration 安全回滚

```sql
-- 1. 永远写 forward + backward
-- Up:
ALTER TABLE users ADD COLUMN new_email TEXT;
UPDATE users SET new_email = email;
ALTER TABLE users ALTER COLUMN new_email SET NOT NULL;

-- Down:
ALTER TABLE users ALTER COLUMN new_email DROP NOT NULL;
UPDATE users SET email = new_email;
ALTER TABLE users DROP COLUMN new_email;

-- 2. 大表 ALTER 异步（避免锁表）
-- pt-online-schema-change / gh-ost / pg_repack
gh-ost --alter="ADD COLUMN new_email TEXT" \
  --host=db --table=users --alter-foreign-keys-method=auto

-- 3. 双写期（数据迁移）
-- 阶段 1：旧代码写 old + new
-- 阶段 2：新代码读 new，写 new
-- 阶段 3：删除旧字段
```

## 回滚预案检查清单

```
发布前：
  ✅ 数据库 migration 有 down
  ✅ 上一版本镜像保留（不删除）
  ✅ 配置有 Git 历史
  ✅ oncall 值班明确
  ✅ 回滚 RunBook 文档化
  ✅ 演练过（季度至少 1 次）

发布中：
  ✅ 监控大盘实时观察
  ✅ 异常指标触发 abort
  ✅ oncall 待命
  ✅ 通讯渠道畅通

发布后：
  ✅ 7 天观察期
  ✅ 旧版本保留可快速回滚
  ✅ 故障复盘
```

## MTTR 优化

```yaml
# 1. 自动化（避免人肉操作）
- 告警 → 自动 abort（Argo Rollouts Analysis）
- 自动回滚（selfHeal）
- 通知 oncall（PagerDuty）

# 2. 可观测性
- 发布状态看板
- 异常告警（错误率 / 延迟 / 业务指标）
- 链路追踪（TraceID 贯穿全链路）

# 3. 演练
- Chaos Engineering（Chaos Mesh / Litmus）
- 季度回滚演练
- GameDay 活动
```

## 关联章节

- **04-release/overview**：发布策略总览
- **04-release/blue-green**：蓝绿秒级回滚
- **04-release/canary**：金丝雀自动回滚
- **05-cicd-observability/dora-metrics**：MTTR 作为 DORA 度量

## 一句话总结

> **回滚 = 发布能力的天花板**。**目标：MTTR < 5 分钟**。**核心：自动化 + 预案 + 演练**。


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
