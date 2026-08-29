---
title: Flaky Test
date: 2026-08-15  # date-auto-injected
---

# Flaky Test

Flaky Test（不稳定测试）= 同一份代码、同一个测试，有时通过有时失败。这是研发团队的"隐形税"。

## 一句话总结

> **Flaky Test = 团队的隐形杀手**。**影响：CI 时间翻倍 + 信任崩溃 + 真 bug 被掩盖**。**治理：分类 + 修复 + quarantine + 根因分析**。

---

## Flaky Test 的危害

```
1. 开发者信任崩溃
   "测试又挂了，重跑吧" → 失去信号

2. CI 时间翻倍
   auto-retry 机制 → 实际耗时 × 2-3

3. 真 bug 被掩盖
   Flaky + 新 bug = 都是红，难以分辨

4. 团队 culture 损伤
   "测试不可信" → 失去测试投入动力

5. 部署阻塞
   Required check 不稳定 → PR 阻塞
```

## 常见根因（按比例）

```yaml
# 1. 异步时序问题（40%）
# 测试假设 A 在 B 之前完成，实际并发
test('user flow', async () => {
    const user = await createUser();      // 不等待
    const order = await createOrder(user); // user 还没 ready
    expect(order.userId).toBe(user.id);
});

# 2. 时间相关（20%）
# Date.now() / setTimeout / 缓存 TTL
test('cache expires', () => {
    cache.set('key', 'value', 60);  // 假设 60 秒
    sleep(61);
    expect(cache.get('key')).toBeNull();
});

# 3. 共享状态（15%）
# 测试间共享 DB / 文件 / 全局变量
let user;
beforeAll(() => {
    user = createUser();  // 别的测试也用 user
});

# 4. 网络依赖（10%）
# 真实 HTTP 调用 / DNS / TLS 握手
test('api', async () => {
    const res = await fetch('https://api.real.com/users');
    expect(res.status).toBe(200);
});

# 5. 并发 / 竞态（10%）
# 多线程 / worker / 微服务并发
test('concurrent', async () => {
    const promises = [createOrder(), createOrder(), createOrder()];
    await Promise.all(promises);
    expect(orders.length).toBe(3);  // 可能少了
});

# 6. 环境差异（5%）
# OS / Node 版本 / 时区 / locale
```

## 治理流程

```
发现 → 分类 → 修复 / quarantine → 监控 → 反思

1. 发现
   - CI 报告
   - 开发者主动标记 flaky
   - 自动检测（re-run 后状态变化）

2. 分类
   - Network（外部依赖）
   - Async（时序）
   - State（共享）
   - Time（时间相关）
   - Env（环境）
   - Concurrency（并发）

3. 修复 vs Quarantine
   - 修复优先级：高频 + 阻塞 PR
   - Quarantine：暂时隔离，限期修复

4. 监控
   - Flaky Rate（每个测试）
   - Quarantine 数量
   - Quarantine 时间（最长多久）

5. 反思
   - 每月复盘
   - 写 RunBook
   - 培训团队
```

## Quarantine 实现

```typescript
// Jest Quarantine Plugin
// 标记 flaky 但不阻塞 PR
test.flaky('complex flow', async () => {
    // 跳过：标记为 known-flaky
});

test.skip('complex flow', async () => {
    // 跳过：阻塞但标记原因
});
```

```python
# pytest-flaky
@pytest.mark.flaky(retries=3, delay=1)
def test_complex_flow():
    pass

# pytest -p no:flaky  # 禁用 flaky 装饰器，强制修复
```

```yaml
# GitHub Actions
- name: Detect flaky
  run: |
    npm test
    if [ $? -ne 0 ]; then
      npm test  # 重跑
      if [ $? -ne 0 ]; then
        echo "::warning::Test failed twice, marking flaky"
        exit 0  # 不阻塞
      fi
    fi
```

## 修复模式

```typescript
// 反模式 1：固定等待
test('flow', async () => {
    await sleep(1000);  // ❌ 不可靠
});

// 正确：显式等待
test('flow', async () => {
    await waitFor(() => user.isReady);
});

// 反模式 2：共享状态
let user;
beforeAll(() => {
    user = createUser();
});

// 正确：每个测试独立 setup
beforeEach(() => {
    user = createUser();
});

// 反模式 3：真实网络
test('api', async () => {
    await fetch('https://api.real.com');
});

// 正确：mock
jest.mock('axios');
axios.get.mockResolvedValue({ data: mockData });
```

## 关联章节

- **05-cicd-observability/overview**：流水线可观测性总览
- **01-pipeline/best-practices**：Pipeline 优化
- **observability/**：监控 + 告警体系

## 一句话总结

> **Flaky Test = 必须治理的工程债**。**关键指标：Flaky Rate < 1%、Quarantine 时长 < 30 天**。**行动：分类 + 修复 + 监控 + 反思**。


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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 编排
- [linux](https://java-px.bot.cd/linux/):Linux 运维
- [observability](https://java-px.bot.cd/observability/):监控告警
