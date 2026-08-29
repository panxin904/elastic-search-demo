---
title: 动态规划
date: 2026-08-15  # date-auto-injected
---

# 🧠 动态规划

> **动态规划（Dynamic Programming, DP）**是解决**重叠子问题**和**最优子结构**问题的利器，是面试和算法竞赛的高频考点。

## 🎯 DP 思想

```
动态规划 = 记忆化 + 递推

核心思想：
  1. 把大问题拆成小问题
  2. 记录小问题的解（避免重复计算）
  3. 递推得到大问题的解

适用场景：
  ✅ 最优子结构：问题的最优解包含子问题的最优解
  ✅ 重叠子问题：子问题被多次重复计算
```

## 🔍 入门示例：斐波那契

```python
# 1. 朴素递归（O(2ⁿ)）
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

# 2. 记忆化（O(n)）
def fib_memo(n, memo={}):
    if n < 2:
        return n
    if n not in memo:
        memo[n] = fib_memo(n-1, memo) + fib_memo(n-2, memo)
    return memo[n]

# 3. DP 递推（O(n) O(1) 空间）
def fib_dp(n):
    if n < 2: return n
    a, b = 0, 1
    for _ in range(n-1):
        a, b = b, a + b
    return b
```

## 🪜 经典 1：爬楼梯

```python
def climb_stairs(n):
    """爬 n 阶，每次 1 或 2 步，多少种方法？"""
    if n <= 1: return 1
    dp = [0] * (n + 1)
    dp[0] = dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]

# 空间优化
def climb_stairs_opt(n):
    if n <= 1: return 1
    a, b = 1, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
```

## 💰 经典 2：打家劫舍

```python
def rob(nums):
    """O(n) 时间，O(1) 空间"""
    if not nums: return 0
    if len(nums) == 1: return nums[0]
    
    prev2, prev1 = 0, 0
    for num in nums:
        prev1, prev2 = max(prev2 + num, prev1), prev1
    return prev1

# 示例
print(rob([2, 7, 9, 3, 1]))  # 12
# 偷 2、9、1 = 12
```

## 💼 经典 3：背包问题

### 0-1 背包

```python
def knapsack_01(weights, values, capacity):
    """O(n * capacity) 时间，O(capacity) 空间"""
    n = len(weights)
    dp = [0] * (capacity + 1)
    
    for i in range(n):
        # 倒序遍历（避免重复使用物品）
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    
    return dp[capacity]

# 示例
weights = [2, 3, 4, 5]
values = [3, 4, 5, 6]
capacity = 5
print(knapsack_01(weights, values, capacity))  # 7
# 选物品 0（w=2, v=3）和 1（w=3, v=4）= 7
```

### 完全背包

```python
def knapsack_complete(weights, values, capacity):
    """O(n * capacity)"""
    n = len(weights)
    dp = [0] * (capacity + 1)
    
    for i in range(n):
        # 正序遍历（允许重复使用物品）
        for w in range(weights[i], capacity + 1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    
    return dp[capacity]
```

## 📈 经典 4：最长递增子序列（LIS）

```python
def length_of_lis(nums):
    """O(n²) DP"""
    if not nums: return 0
    n = len(nums)
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)

# 二分优化 O(n log n)
def length_of_lis_binary(nums):
    tails = []
    for num in nums:
        lo, hi = 0, len(tails)
        while lo < hi:
            mid = (lo + hi) // 2
            if tails[mid] < num:
                lo = mid + 1
            else:
                hi = mid
        tails.insert(lo, num)
    return len(tails)

# 示例
print(length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]))  # 4
# [2, 3, 7, 18] 或 [2, 3, 7, 101]
```

## ✏️ 经典 5：编辑距离

```python
def edit_distance(word1, word2):
    """O(m * n) 时间，O(n) 空间"""
    m, n = len(word1), len(word2)
    dp = list(range(n + 1))
    
    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            temp = dp[j]
            if word1[i-1] == word2[j-1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(prev, dp[j], dp[j-1])
            prev = temp
    
    return dp[n]

# 示例
print(edit_distance("horse", "ros"))  # 3
# horse -> rorse (替换h->r) -> rose (删除r) -> ros (删除e)
```

## 💰 经典 6：最长公共子序列（LCS）

```python
def longest_common_subsequence(text1, text2):
    """O(m * n) 时间，O(n) 空间"""
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(2)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i % 2][j] = dp[(i-1) % 2][j-1] + 1
            else:
                dp[i % 2][j] = max(dp[(i-1) % 2][j], dp[i % 2][j-1])
    
    return dp[m % 2][n]

# 示例
print(longest_common_subsequence("abcde", "ace"))  # 3
# "ace"
```

## 🎯 经典 7：最长回文子序列

```python
def longest_palindromic_subseq(s):
    """O(n²) 时间，O(n²) 空间"""
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = dp[i+1][j-1] + 2
            else:
                dp[i][j] = max(dp[i+1][j], dp[i][j-1])
    
    return dp[0][n-1]

# 示例
print(longest_palindromic_subseq("bbbab"))  # 4
# "bbbb"
```

## 🎯 经典 8：零钱兑换

```python
def coin_change(coins, amount):
    """O(amount * n) 时间，O(amount) 空间"""
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    
    for i in range(1, amount + 1):
        for coin in coins:
            if i - coin >= 0 and dp[i - coin] + 1 < dp[i]:
                dp[i] = dp[i - coin] + 1
    
    return dp[amount] if dp[amount] != float('inf') else -1

# 示例
print(coin_change([1, 5, 10, 25], 41))  # 4
# 25 + 10 + 5 + 1
```

## 🪜 经典 9：完全平方数

```python
def num_squares(n):
    """O(n * sqrt(n))"""
    dp = [float('inf')] * (n + 1)
    dp[0] = 0
    
    for i in range(1, n + 1):
        j = 1
        while j * j <= i:
            dp[i] = min(dp[i], dp[i - j*j] + 1)
            j += 1
    
    return dp[n]

# 示例
print(num_squares(12))  # 3
# 4 + 4 + 4
```

## 📊 经典 10：最长回文子串

```python
def longest_palindromic_substr(s):
    """O(n²) 时间，O(n²) 空间（可优化到 O(1)）"""
    n = len(s)
    if n < 2: return s
    
    dp = [[False] * n for _ in range(n)]
    start, max_len = 0, 1
    
    for i in range(n):
        dp[i][i] = True
    
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                if length == 2:
                    dp[i][j] = True
                else:
                    dp[i][j] = dp[i+1][j-1]
            if dp[i][j] and length > max_len:
                start = i
                max_len = length
    
    return s[start:start + max_len]

# 中心扩展法 O(n²) O(1) 空间
def longest_palindromic_substr_v2(s):
    n = len(s)
    start, max_len = 0, 1
    
    def expand(left, right):
        while left >= 0 and right < n and s[left] == s[right]:
            left -= 1
            right += 1
        return left + 1, right - left - 1
    
    for i in range(n):
        l1, len1 = expand(i, i)         # 奇数
        l2, len2 = expand(i, i + 1)     # 偶数
        if len1 > max_len:
            start, max_len = l1, len1
        if len2 > max_len:
            start, max_len = l2, len2
    
    return s[start:start + max_len]
```

## 📊 经典 11：股票买卖

```python
def max_profit(prices):
    """O(n) 时间，O(1) 空间"""
    if not prices: return 0
    min_price = prices[0]
    max_profit = 0
    for price in prices[1:]:
        min_price = min(min_price, price)
        max_profit = max(max_profit, price - min_price)
    return max_profit

# 含冷冻期
def max_profit_cooldown(prices):
    n = len(prices)
    if n < 2: return 0
    hold = [-prices[0], 0]  # [持有, 不持有]
    for i in range(1, n):
        hold[1] = max(hold[1], hold[0] + prices[i])
        hold[0] = max(hold[0], -prices[i] if i < 2 else 
                    max(hold[1] if i == 2 else 0, -prices[i]))
    return hold[1]
```

## 📊 DP 解题框架

### 1. 确定状态

```
状态 = dp[i] / dp[i][j] 表达什么
- 一维：dp[i] = 前 i 个元素的最优解
- 二维：dp[i][j] = 字符串 s1 前 i 个 / s2 前 j 个的最优解
```

### 2. 找转移方程

```
dp[i] = f(dp[i-1], dp[i-2], ...) + 当前选择
```

### 3. 确定初始状态和边界

```python
dp[0] = base_case_value
dp[n] = 最终答案
```

### 4. 选择迭代方向

```python
# 从前向后
for i in range(1, n + 1):
    dp[i] = ...

# 从后向前
for i in range(n - 1, -1, -1):
    dp[i] = ...
```

## 📊 DP 优化技巧

### 空间优化（滚动数组）

```python
# 二维 DP 压缩到一维
# 例：最长回文子序列
def longest_palindromic_subseq_opt(s):
    n = len(s)
    dp = [0] * n
    
    for i in range(n - 1, -1, -1):
        new_dp = [0] * n
        new_dp[i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                new_dp[j] = dp[j-1] + 2
            else:
                new_dp[j] = max(dp[j], new_dp[j-1])
        dp = new_dp
    
    return dp[n-1]
```

## 🎯 DP 题目分类

```
线性 DP（一维）：
  - 斐波那契、爬楼梯、打家劫舍、最大子序和

背包 DP（二维）：
  - 0-1 背包、完全背包、多重背包
  - 分割等和子集、目标和

区间 DP（二维）：
  - 最长回文子序列、最长回文子串
  - 戳气球、矩阵乘法

字符串 DP（二维）：
  - 编辑距离、最长公共子序列
  - 不同的子序列

状态机 DP：
  - 股票买卖（冷冻期、手续费）
  - 打家劫舍（环形）

树形 DP：
  - 二叉树路径和
  - 树的直径
```

## 🎯 总结

**动态规划核心要点**：
- ✅ DP 适用：最优子结构 + 重叠子问题
- ✅ 三个关键：状态定义、转移方程、初始状态
- ✅ 空间优化：滚动数组降维
- ✅ 经典题目：背包、LIS、LCS、编辑距离
- ✅ 股票问题（DP 经典）
- ✅ 字符串问题（编辑距离、LCS）
- ⚠️ 找状态定义是难点
- ⚠️ 大多数 DP 题目可优化空间

**下一步：** [🏗️ 项目结构](/09-enterprise/structure) — 企业级项目组织


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读 · 08 算法

<!-- xlink-subpage-injected:do-not-edit -->

本页（08 算法）相关主题的跨站入口:

- [java](https://java-px.bot.cd/java-web-manual/):Java 对比
- [ai](https://java-px.bot.cd/ai/):AI / 机器学习
- [bigdata](https://java-px.bot.cd/bigdata/):大数据 / 数据处理
