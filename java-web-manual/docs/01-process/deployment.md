---
title: 部署上线
---

# 部署上线

将开发完成的功能安全、可靠地发布到生产环境。

## 部署流程

```
代码合并 → 构建打包 → 部署测试环境 → 冒烟测试
    → 生产发布（灰度/全量）→ 线上验证 → 监控观察
```

## 环境管理

| 环境 | 用途 | 配置 |
|---|---|---|
| dev | 本地开发 | application-dev.yml |
| test | 测试环境 | application-test.yml |
| staging | 预发布环境 | application-staging.yml |
| prod | 生产环境 | application-prod.yml |

## 部署策略

### 滚动发布
```
实例1: 停旧 → 启新 → 健康检查 ✓
实例2:          停旧 → 启新 → 健康检查 ✓
实例3:                   停旧 → 启新 → 健康检查 ✓
```

### 灰度发布（金丝雀）
```
用户流量: ── 90% ──→ 旧版本
          ── 10% ──→ 新版本 (观察5分钟)
                     → 无异常 → 逐步扩大比例
```

## 上线检查清单

- [ ] 代码已通过 Code Review
- [ ] 单元测试和集成测试全部通过
- [ ] 数据库变更脚本已准备（DDL/DML）
- [ ] 配置项已确认（环境变量、Nacos/Apollo）
- [ ] 依赖服务都已就绪
- [ ] 回滚方案已准备（代码回滚、数据回滚）
- [ ] 上线时间窗口已通知相关方
- [ ] 监控告警已配置

## 紧急回滚

```bash
# 1. 切回旧版本
kubectl rollout undo deployment/order-service

# 2. 或使用 Docker 指定旧镜像
docker run -d my-app:v1.2.0

# 3. 数据库回滚（执行反向 SQL）
# 4. 通知相关人员
# 5. 排查根因，修复后再次发布
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="deployment" :height="400" />
