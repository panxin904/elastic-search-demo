---
title: 搜索算法
---

# 🔎 搜索算法

> 搜索是**在数据集合中查找特定元素**的算法。本章详解**二分搜索、DFS、BFS**等核心搜索算法。

## 🎯 搜索算法分类

```
按数据结构：
  - 数组搜索：顺序 / 二分 / 插值
  - 树搜索：BST / 平衡树 / 红黑树
  - 图搜索：DFS / BFS / Dijkstra

按目标：
  - 精确匹配：找某个元素
  - 范围查询：找区间
  - 模糊匹配：正则、通配符
  - 近似匹配：编辑距离、KNN
```

## 🔍 顺序搜索

```python
def linear_search(arr, target):
    """O(n) 时间，O(1) 空间"""
    for i, x in enumerate(arr):
        if x == target:
            return i
    return -1

# 使用
arr = [3, 1, 4, 1, 5, 9, 2, 6]
print(linear_search(arr, 5))  # 4
```

## 🔍 二分搜索

### 基础实现

```python
def binary_search(arr, target):
    """O(log n) 时间，O(1) 空间（迭代）"""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

# 递归版
def binary_search_recursive(arr, target, lo=0, hi=None):
    if hi is None:
        hi = len(arr) - 1
    if lo > hi:
        return -1
    mid = (lo + hi) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, hi)
    else:
        return binary_search_recursive(arr, target, lo, mid - 1)
```

### bisect 模块

```python
import bisect

arr = [1, 3, 4, 4, 5, 7, 9, 10]

# 查找插入位置（保持有序）
print(bisect.bisect_left(arr, 4))    # 2（左侧插入位置）
print(bisect.bisect_right(arr, 4))   # 4（右侧插入位置）
print(bisect.bisect(arr, 4))         # 默认 bisect_right

# 插入
bisect.insort_left(arr, 4)
print(arr)  # [1, 3, 4, 4, 4, 5, 7, 9, 10]

# 实战：成绩等级
def grade(score):
    breakpoints = [60, 70, 80, 90]
    grades = "EDCBA"
    i = bisect.bisect(breakpoints, score)
    return grades[i]

print(grade(85))  # B
print(grade(95))  # A
```

### 二分搜索变体

```python
# 1. 找第一个 ≥ target 的位置
def lower_bound(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

# 2. 找第一个 > target 的位置
def upper_bound(arr, target):
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo

# 3. 找最后一个 ≤ target 的位置
def find_last_le(arr, target):
    return upper_bound(arr, target) - 1
```

## 🔍 插值搜索

```python
def interpolation_search(arr, target):
    """O(log log n) 平均，O(n) 最坏（数据均匀分布时）"""
    lo, hi = 0, len(arr) - 1
    while lo <= hi and arr[lo] <= target <= arr[hi]:
        # 估算目标位置
        if lo == hi:
            return lo if arr[lo] == target else -1
        pos = lo + ((target - arr[lo]) * (hi - lo)) // (arr[hi] - arr[lo])
        
        if arr[pos] == target:
            return pos
        elif arr[pos] < target:
            lo = pos + 1
        else:
            hi = pos - 1
    return -1
```

## 🔍 图搜索

### 深度优先搜索（DFS）

```python
from collections import defaultdict

class Graph:
    def __init__(self):
        self.adj = defaultdict(list)
    
    def add_edge(self, u, v):
        self.adj[u].append(v)
        self.adj[v].append(u)  # 无向图

# 创建图
g = Graph()
g.add_edge(0, 1)
g.add_edge(0, 2)
g.add_edge(1, 3)
g.add_edge(1, 4)
g.add_edge(2, 5)
g.add_edge(2, 6)

# 1. 递归 DFS
def dfs_recursive(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    print(start, end=" ")
    for neighbor in graph.adj[start]:
        if neighbor not in visited:
            dfs_recursive(graph, neighbor, visited)
    return visited

print("DFS (recursive):")
dfs_recursive(g, 0)
# 0 1 3 4 2 5 6

# 2. 迭代 DFS
def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            print(node, end=" ")
            for neighbor in reversed(graph.adj[node]):
                if neighbor not in visited:
                    stack.append(neighbor)

print("\nDFS (iterative):")
dfs_iterative(g, 0)
```

### 广度优先搜索（BFS）

```python
from collections import deque

def bfs(graph, start):
    """O(V + E) 时间"""
    visited = {start}
    queue = deque([start])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        
        for neighbor in graph.adj[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return result

print("BFS:")
print(bfs(g, 0))
# [0, 1, 2, 3, 4, 5, 6]
```

### 实战：迷宫最短路径

```python
from collections import deque

def shortest_path_maze(maze, start, end):
    """0=可通过, 1=墙, 返回最短路径"""
    rows, cols = len(maze), len(maze[0])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        (r, c), path = queue.popleft()
        
        if (r, c) == end:
            return path
        
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and maze[nr][nc] == 0 and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), path + [(nr, nc)]))
    
    return None  # 无路径

# 迷宫示例
maze = [
    [0, 0, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 0, 0],
    [1, 1, 0, 1]
]
path = shortest_path_maze(maze, (0, 0), (3, 2))
print(path)
# [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 2)]
```

### 实战：岛屿数量

```python
def num_islands(grid):
    """0=水, 1=陆地, 计算岛屿数量"""
    if not grid:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    visited = set()
    count = 0
    
    def dfs(r, c):
        if (r < 0 or r >= rows or c < 0 or c >= cols or
            grid[r][c] == 0 or (r, c) in visited):
            return
        visited.add((r, c))
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and (r, c) not in visited:
                dfs(r, c)
                count += 1
    
    return count

# 测试
grid = [
    ["1", "1", "0", "0", "0"],
    ["1", "1", "0", "0", "0"],
    ["0", "0", "1", "0", "0"],
    ["0", "0", "0", "1", "1"]
]
print(num_islands(grid))  # 3
```

### 实战：单词接龙

```python
from collections import deque, defaultdict

def ladder_length(begin_word, end_word, word_list):
    """BFS 找最短转换序列"""
    if end_word not in word_list:
        return 0
    
    # 预处理：建立邻接关系
    L = len(begin_word)
    all_combo_dict = defaultdict(list)
    for word in word_list:
        for i in range(L):
            key = word[:i] + "*" + word[i+1:]
            all_combo_dict[key].append(word)
    
    # BFS
    queue = deque([(begin_word, 1)])
    visited = {begin_word}
    
    while queue:
        current_word, level = queue.popleft()
        
        for i in range(L):
            intermediate = current_word[:i] + "*" + current_word[i+1:]
            for word in all_combo_dict[intermediate]:
                if word == end_word:
                    return level + 1
                if word not in visited:
                    visited.add(word)
                    queue.append((word, level + 1))
            all_combo_dict[intermediate] = []  # 优化：清空已访问
    
    return 0

# 测试
print(ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"]))
# 5
```

## 🔍 Dijkstra 最短路径

```python
import heapq
from collections import defaultdict

def dijkstra(graph, start):
    """O((V + E) log V) 时间"""
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    visited = set()
    
    while pq:
        cur_dist, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        
        for neighbor, weight in graph[node].items():
            distance = cur_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))
    
    return distances

# 图
graph = {
    'A': {'B': 1, 'C': 4},
    'B': {'A': 1, 'C': 2, 'D': 5},
    'C': {'A': 4, 'B': 2, 'D': 1},
    'D': {'B': 5, 'C': 1}
}
print(dijkstra(graph, 'A'))
# {'A': 0, 'B': 1, 'C': 3, 'D': 4}
```

## 🔍 A* 启发式搜索

```python
import heapq

def heuristic(a, b):
    """曼哈顿距离"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(grid, start, end):
    """A* 寻路"""
    rows, cols = len(grid), len(grid[0])
    open_set = {start}
    came_from = {}
    
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}
    
    pq = [(f_score[start], start)]
    
    while pq:
        _, current = heapq.heappop(pq)
        
        if current == end:
            # 重建路径
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = current[0] + dr, current[1] + dc
            neighbor = (nr, nc)
            
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                tentative_g = g_score[current] + 1
                
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, end)
                    heapq.heappush(pq, (f_score[neighbor], neighbor))
                    open_set.add(neighbor)
    
    return None
```

## 🔍 实战：搜索算法对比

| 场景 | 算法 | 时间复杂度 |
|------|------|----------|
| 有序数组查找 | 二分搜索 | O(log n) |
| 均匀分布数据 | 插值搜索 | O(log log n) |
| 图的遍历 | DFS / BFS | O(V + E) |
| 最短路径 | Dijkstra | O((V + E) log V) |
| 启发式搜索 | A* | 取决于启发函数 |
| KNN 搜索 | KD-Tree / Ball-Tree | O(log n) |
| 文本搜索 | 倒排索引 | O(1) |

## 🎯 总结

**搜索算法核心要点**：
- ✅ 二分搜索（O(log n)）是基础
- ✅ bisect 模块（实际项目用）
- ✅ DFS（深度优先，适合路径问题）
- ✅ BFS（广度优先，适合最短路径）
- ✅ Dijkstra（单源最短路径）
- ✅ A*（启发式搜索，更智能）
- ⚠️ 选择合适的搜索算法
- ⚠️ DFS 用栈 / BFS 用队列

**下一步：** [🌳 树与图](/08-algorithms/tree-graph) — 树结构与图算法
