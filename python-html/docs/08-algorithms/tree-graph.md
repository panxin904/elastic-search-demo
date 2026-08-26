---
title: 树与图
---

# 🌳 树与图

> **树和图**是计算机科学中最重要的**非线性数据结构**。本章详解核心树和图算法。

## 🌳 树基础

### 二叉树节点

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# 创建
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)

#         1
#        / \
#       2   3
#      / \
#     4   5
```

### 树的遍历

```python
def preorder(root):
    """前序：根 → 左 → 右"""
    if not root: return []
    return [root.val] + preorder(root.left) + preorder(root.right)

def inorder(root):
    """中序：左 → 根 → 右（BST 中得到升序）"""
    if not root: return []
    return inorder(root.left) + [root.val] + inorder(root.right)

def postorder(root):
    """后序：左 → 右 → 根"""
    if not root: return []
    return postorder(root.left) + postorder(root.right) + [root.val]

def levelorder(root):
    """层序（BFS）"""
    if not root: return []
    from collections import deque
    result = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        result.append(node.val)
        if node.left: queue.append(node.left)
        if node.right: queue.append(node.right)
    return result
```

## 🌲 二叉搜索树（BST）

```python
class BST:
    def __init__(self):
        self.root = None
    
    def insert(self, val):
        """O(h) h=树高"""
        self.root = self._insert(self.root, val)
    
    def _insert(self, node, val):
        if not node:
            return TreeNode(val)
        if val < node.val:
            node.left = self._insert(node.left, val)
        else:
            node.right = self._insert(node.right, val)
        return node
    
    def search(self, val):
        """O(h)"""
        return self._search(self.root, val)
    
    def _search(self, node, val):
        if not node:
            return False
        if val == node.val:
            return True
        elif val < node.val:
            return self._search(node.left, val)
        else:
            return self._search(node.right, val)
    
    def inorder(self):
        """O(n) 升序"""
        result = []
        self._inorder(self.root, result)
        return result
    
    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.val)
            self._inorder(node.right, result)
```

## ⚖️ 平衡二叉树

### AVL 树

```python
class AVLNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.height = 1

def height(node):
    return node.height if node else 0

def balance_factor(node):
    return height(node.left) - height(node.right) if node else 0

def rotate_right(y):
    x = y.left
    T2 = x.right
    x.right = y
    y.left = T2
    y.height = 1 + max(height(y.left), height(y.right))
    x.height = 1 + max(height(x.left), height(x.right))
    return x

def rotate_left(x):
    y = x.right
    T2 = y.left
    y.left = x
    x.right = T2
    x.height = 1 + max(height(x.left), height(x.right))
    y.height = 1 + max(height(y.left), height(y.right))
    return y

def insert_avl(root, val):
    if not root:
        return AVLNode(val)
    
    if val < root.val:
        root.left = insert_avl(root.left, val)
    else:
        root.right = insert_avl(root.right, val)
    
    root.height = 1 + max(height(root.left), height(root.right))
    balance = balance_factor(root)
    
    # 左左
    if balance > 1 and val < root.left.val:
        return rotate_right(root)
    # 右右
    if balance < -1 and val > root.right.val:
        return rotate_left(root)
    # 左右
    if balance > 1 and val > root.left.val:
        root.left = rotate_left(root.left)
        return rotate_right(root)
    # 右左
    if balance < -1 and val < root.right.val:
        root.right = rotate_right(root.right)
        return rotate_left(root)
    
    return root
```

## 🌲 红黑树

> Python 的 `dict` 和 `set` 底层使用**红黑树**实现（Python 3.7+）。保证最坏 O(log n) 操作。

```python
# 红黑树性质：
# 1. 节点是红或黑
# 2. 根节点是黑
# 3. 叶子节点（NIL）是黑
# 4. 红节点的子节点是黑
# 5. 从任一节点到叶子的所有路径包含相同数量的黑节点

# 实际应用：Java TreeMap、TreeSet、C++ std::map
# 实际实现非常复杂（500+ 行），通常用现成库
```

## 📊 B 树

> B 树是**数据库索引**的核心数据结构。MySQL InnoDB 用 B+ 树。

```python
# B 树特性：
# 1. 每个节点最多 m 个子节点（m 阶 B 树）
# 2. 除根外，每个节点至少 ⌈m/2⌉ 个子节点
# 3. 根节点至少 2 个子节点（除非是叶子）
# 4. 有 k 个子节点的节点包含 k-1 个键
# 5. 所有叶子在同一层

# B+ 树（B 树变种）：
# 1. 数据只存在叶子
# 2. 叶子用链表连接（范围查询快）
# 3. 内节点只存键（导航用）
```

## 📊 Trie 树（字典树）

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word):
        """O(m) m=单词长度"""
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True
    
    def search(self, word):
        """O(m)"""
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end
    
    def starts_with(self, prefix):
        """O(m)"""
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True

# 使用
trie = Trie()
trie.insert("apple")
print(trie.search("apple"))     # True
print(trie.search("app"))        # False
print(trie.starts_with("app"))  # True
```

## 📊 堆（Heap）

```python
import heapq

# 最小堆
heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 1)
heapq.heappush(heap, 3)
print(heapq.heappop(heap))  # 1
print(heapq.heappop(heap))  # 3

# 最大堆（取负数）
max_heap = []
heapq.heappush(max_heap, -5)
heapq.heappush(max_heap, -1)
print(-heapq.heappop(max_heap))  # 5

# heapq 完整 API
arr = [3, 1, 4, 1, 5, 9, 2, 6]
heapq.heapify(arr)                # 原地堆化 O(n)
heapq.heappushpop(arr, 8)         # 弹一个 + 推一个
heapq.heapreplace(arr, 0)         # 替换堆顶
heapq.nlargest(3, arr)            # 前 3 大
heapq.nsmallest(3, arr)           # 前 3 小

# 实战：Top K 问题
def top_k(nums, k):
    """O(n log k)"""
    return heapq.nlargest(k, nums)

print(top_k([3, 1, 4, 1, 5, 9, 2, 6, 5, 3], 3))  # [9, 6, 5]
```

## 📊 实战：树的应用

### 字典树：单词搜索 II

```python
def find_words(board, words):
    """在字母矩阵中搜索单词"""
    from collections import defaultdict
    
    # 构建 Trie
    trie = {}
    for word in words:
        node = trie
        for ch in word:
            if ch not in node:
                node[ch] = {}
            node = node[ch]
        node["$"] = word  # 单词结尾
    
    rows, cols = len(board), len(board[0])
    result = set()
    
    def dfs(r, c, node):
        if "$" in node:
            result.add(node["$"])
            del node["$"]  # 避免重复
        
        if not (0 <= r < rows and 0 <= c < cols):
            return
        
        ch = board[r][c]
        if ch not in node:
            return
        
        board[r][c] = "#"  # 标记访问
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            dfs(r + dr, c + dc, node[ch])
        board[r][c] = ch  # 恢复
    
    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie)
    
    return list(result)
```

## 📊 图基础

```python
from collections import defaultdict

# 邻接表（推荐）
class Graph:
    def __init__(self):
        self.adj = defaultdict(list)
    
    def add_edge(self, u, v, directed=False):
        self.adj[u].append(v)
        if not directed:
            self.adj[v].append(u)
    
    def get_neighbors(self, u):
        return self.adj[u]

# 加权图
class WeightedGraph:
    def __init__(self):
        self.adj = defaultdict(dict)
    
    def add_edge(self, u, v, w):
        self.adj[u][v] = w
        self.adj[v][u] = w  # 无向

# 邻接矩阵
n = 5
matrix = [[0] * n for _ in range(n)]
def add_edge(u, v, w=1):
    matrix[u][v] = w
    matrix[v][u] = w  # 无向
```

## 🔍 图算法

### BFS（最短路径，无权图）

```python
from collections import deque

def bfs_shortest_path(graph, start, end):
    """无权图最短路径 O(V + E)"""
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        node, path = queue.popleft()
        if node == end:
            return path
        for neighbor in graph.get_neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return None
```

### DFS（连通分量）

```python
def connected_components(graph):
    """O(V + E)"""
    visited = set()
    components = []
    
    for node in graph.adj:
        if node not in visited:
            component = []
            stack = [node]
            while stack:
                curr = stack.pop()
                if curr not in visited:
                    visited.add(curr)
                    component.append(curr)
                    for neighbor in graph.get_neighbors(curr):
                        if neighbor not in visited:
                            stack.append(neighbor)
            components.append(component)
    
    return components
```

### 拓扑排序

```python
from collections import deque

def topological_sort(graph):
    """Kahn 算法 O(V + E)"""
    in_degree = {node: 0 for node in graph.adj}
    for node in graph.adj:
        for neighbor in graph.get_neighbors(node):
            in_degree[neighbor] += 1
    
    queue = deque([node for node, deg in in_degree.items() if deg == 0])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        for neighbor in graph.get_neighbors(node):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if len(result) != len(graph.adj):
        return None  # 有环
    
    return result
```

### 最短路径（Dijkstra）

```python
import heapq

def dijkstra(graph, start):
    """O((V + E) log V)"""
    distances = {node: float('inf') for node in graph.adj}
    distances[start] = 0
    pq = [(0, start)]
    visited = set()
    
    while pq:
        cur_dist, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        
        for neighbor, weight in graph.adj[node].items():
            distance = cur_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return distances
```

## 🎯 总结

**树与图核心要点**：
- ✅ 树的 4 种遍历（前序 / 中序 / 后序 / 层序）
- ✅ BST 操作（插入、查找、删除 O(log n)）
- ✅ AVL 树（自平衡 O(log n)）
- ✅ 红黑树（Python dict 底层）
- ✅ B+ 树（数据库索引）
- ✅ Trie 树（字符串前缀）
- ✅ 堆（优先队列）
- ✅ BFS / DFS 图遍历
- ✅ Dijkstra 最短路径
- ✅ 拓扑排序
- ⚠️ 树的平衡很重要（避免退化为链表）
- ⚠️ 图算法选择（BFS / DFS / Dijkstra）

**下一步：** [🧠 动态规划](/08-algorithms/dp) — 算法进阶


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
