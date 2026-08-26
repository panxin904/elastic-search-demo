---
title: NWR 仲裁模型
---

# NWR 仲裁模型

> 写 W 副本、读 R 副本，通过 R + W > N 保证至少读到最新值。

## 1. 基本概念

```
N：副本总数
W：写入时需要确认的副本数（write quorum）
R：读取时需要查询的副本数（read quorum）

R + W > N 是关键：
  → 任意读 quorum 和写 quorum 必有交集
  → 一定能读到最近一次写入
```

## 2. 直觉

```
场景：N = 5，W = 3，R = 3

写 x = 1：
  - 写入 3 个副本（哪 3 个由协调者决定）
  - 假设副本 {A, B, C} 收到写入
  - 返回成功

读 x：
  - 从 3 个副本读（哪 3 个随机）
  - 假设读 {C, D, E}
  - C 是最新值 1，D 和 E 是旧值 0
  - 取最新 → 1 ✓

为什么一定能读到？
  - 写 quorum = {A, B, C}（3 个）
  - 读 quorum = {C, D, E}（3 个）
  - 交集 = {C} 至少 1 个
  → 必然包含写 quorum 的至少一个节点
```

## 3. 参数组合

### 3.1 常见配置

| N | W | R | 行为 | 一致性 |
|---|---|---|---|---|
| 3 | 1 | 1 | 全异步，无一致性 | Eventual |
| 3 | 2 | 2 | 经典 Quorum | Strong |
| 3 | 3 | 1 | 写全确认，读任意 | Strong Read |
| 3 | 1 | 3 | 写快速，读全查 | Strong Read |
| 5 | 3 | 3 | 更强容错 | Strong |
| 5 | 5 | 1 | 写严格，读快速 | Strong |

### 3.2 强一致条件

```
R + W > N  → 强一致（一定能读到最新写入）
W > N / 2  → 写入无歧义（多数写入）
R > N / 2  → 读一定能找到最新

📌 三者同时满足：
  R + W > N  AND  W > N / 2  AND  R > N / 2
  → 最严格的 quorum
```

### 3.3 弱一致模式

```
W + R ≤ N：
  - 可能读到旧值
  - 但性能高（写读都很快）

例 N=3：
  W=1, R=1 → 写读都快，可能读到旧值
  W=2, R=1 → 写要等多数，读快速
  W=1, R=2 → 写快速，读要等多数
```

## 4. Sloppy Quorum

### 4.1 严格 Quorum 的问题

```
N = 5，W = 3

如果某次写只能联系到 2 个节点（其他 3 个挂了 / 网络断）：
  → 写入失败（只到 2 < W = 3）
  → 即使其他节点恢复，写入也不会自动恢复

📌 在大规模集群中，这种"小故障"很常见
   → 严格 quorum 的可用性差
```

### 4.2 Sloppy Quorum 思路

```
W 不再要求"原始 N 中的 W 个"
改为"任意可用的 W 个节点（包括替补）"

例：
  - 原本节点 A, B, C 挂了
  - 替补节点 A', B', C'（不在原始 N 中）
  - 写入 A', B', C'（任意 3 个可用节点）
  → 写入成功

📌 牺牲强一致，换高可用
   - 等真节点恢复后，把数据迁回
   - DynamoDB / Cassandra 默认行为
```

## 5. Hinted Handoff

### 5.1 解决 Sloppy Quorum 的"数据归属"问题

```
Sloppy Quorum 写到了替补节点
真节点恢复后怎么办？

答：Hinted Handoff（提示移交）
  - 替补节点保存"这个 key 应该属于 X 节点的提示"
  - X 节点恢复时，主动从替补节点拉数据
  - 拉完后，替补节点删除提示
```

### 5.2 流程

```
1. 写入 x=1 到替补 A'（真节点 A 不可达）
2. A' 存储：x=1 + hint "should belong to A"
3. A 节点恢复
4. A' 把 x=1 推给 A
5. A' 删除本地副本和 hint
```

## 6. 读修复（Read Repair）

### 6.1 解决 Sloppy Quorum 的副本不一致

```
读 quorum 时发现多副本版本不一致：
  副本 {A, B, C}：
    A: x=1
    B: x=0
    C: x=0

读 quorum 选择读 {A, B}：
  → 返回 x=1（取最新）
  → 发现 B 是旧的
  → 后台异步把 x=1 推到 B（read repair）

📌 异步修复，不阻塞读
   - 下次读 B 时就一致了
   - Cassandra / DynamoDB 默认行为
```

## 7. 反熵（Anti-Entropy）

### 7.1 主动修复

```
定期对比所有副本：
  - 用 Merkle Tree 比较数据指纹
  - 发现不一致 → 同步差异

📌 比 Read Repair 更彻底（覆盖所有副本）
📌 代价：周期性 IO 开销
```

### 7.2 Merkle Tree 同步

```
根哈希
  ├── 左子树哈希
  │   ├── ...
  │   └── ...
  └── 右子树哈希
      ├── ...
      └── ...

1. 计算两副本的根哈希
2. 不一致 → 递归下钻到不同子树
3. 只同步不同的叶节点（实际数据块）

📌 高效：O(log N) 同步差异
```

## 8. Cassandra 中的 NWR

### 8.1 一致性级别

```
ONE      ：写读都只接触 1 节点（最快）
QUORUM   ：R/W = 多数（N/2 + 1）
ALL      ：写读都等所有节点（最慢）
LOCAL_ONE：本 DC 内 1 节点
LOCAL_QUORUM：本 DC 内多数
EACH_QUORUM：每个 DC 都满足 quorum
```

### 8.2 实战配置

```
Cassandra 默认：
  - 写入：LOCAL_QUORUM（同一 DC 多数）
  - 读取：LOCAL_QUORUM

场景选择：
  - 写多读少、允许旧值 → ONE
  - 金融账务 → QUORUM
  - 跨 DC 强一致 → EACH_QUORUM
```

## 9. 仲裁与 CAP 的关系

```
NWR 是工程上把"一致性强度"做成可调参数：
  - R + W > N → 强一致（CP）
  - R + W ≤ N → 最终一致（AP）

📌 业务侧按需选择：
  - 写用户资料：ONE（快）
  - 写订单：QUORUM（不能丢）
```

## 10. 一句话总结

```
📌 NWR：通过调整 R + W 关系控制一致性与可用性的取舍
📌 强一致条件：R + W > N
📌 严格 quorum 在大集群里可用性差 → sloppy quorum + hinted handoff
� Sloppy quorum 牺牲强一致换可用性，修复靠 read repair + anti-entropy
📌 Cassandra / DynamoDB 默认 sloppy quorum + read repair
📌 金融场景：W = R = N（最严格）；互联网场景：ONE/QUORUM 混合
```

## 11. 参考资料

- Dynamo: Amazon's Highly Available Key-value Store (SOSP 2007)
- Cassandra Architecture (Avinash Lakshman, 2010)
- Consistent Hashing and Random Trees (Karger et al., 1997)
- Merkle Tree 同步原理
- DDIA 第 5 章


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
