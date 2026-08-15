---
title: Listpack 紧凑列表
---

# 📦 Listpack 紧凑列表

> Listpack 是 Redis 5.0 引入的紧凑列表结构，作为 ziplist 的继任者。它通过把"前一项长度"存放在当前项尾部（`backlen`），彻底解决了 ziplist 的**级联更新**性能陷阱，是 Hash/Set/ZSet 小数据量编码的共同底层容器。

<ClientOnly>
  <DataStructureViz />
</ClientOnly>

## 一、为什么需要替代 ziplist

ziplist 自 Redis 2.0 起服役，本质上是一块连续内存上紧密排列的小 entry。它的头部只有 `zlbytes / zltail / zllen` 三个元数据，遍历时通过 `prevrawlen`（前一项的字节数）反向定位。问题恰恰出在这里：

```text
   entry1                entry2                entry3
┌─────────────┐    ┌──────────────────┐    ┌───────────┐
│ ... value 5 │    │ prevrawlen=11    │    │ prevrawlen │
│             │    │ ... value 100    │    │ ...        │
└─────────────┘    └──────────────────┘    └───────────┘
       │                    │
       └──── prevrawlen 指向 ───┘
```

当 `entry1` 的长度从 253 byte **恰好变为 254 byte** 时（触发 1 byte → 5 byte 编码切换），`entry2.prevrawlen` 就要从 1 byte 变成 5 byte，自己膨胀 4 byte；连锁反应下 `entry3.prevrawlen` 也得重写，依次向后传播——这就是**级联更新**（cascade update）。最坏情况下，一次 `LPUSH` 的时间复杂度是 O(N²)，N 越大越糟。

listpack 的设计核心正是切断这条依赖链：**每项只记录自己的状态，不再依赖前一项的长度**。

## 二、listpack 整体结构

源码 `src/listpack.h`：

```c
typedef struct listpack {
    uint32_t bytes;      // 占用的总字节数（含自身头部）
    uint16_t num_elements; // entry 数量
    // entry[] 紧跟在结构体后面
    // 末尾有 1 byte 标识结束（FF）
} listpack;
```

物理布局：

```text
┌─────────┬─────────────┬──────┬─────┬─────┬──────┬─────┬─────┬──────┐
│ bytes(4)│ num_elem(2) │ enc  │val  │back │ enc  │val  │back │  FF  │
│   25    │      2      │ 0x01 │"hi" │0x02 │ 0x05 │42   │0x01 │ 0xFF │
└─────────┴─────────────┴──────┴─────┴─────┴──────┴─────┴─────┴──────┘
                        └──── entry1 ─────┘└──── entry2 ─────┘  结束符
```

- **`bytes`**：整个 listpack 占用的字节数，分配内存时一次性写入。
- **`num_elements`**：entry 计数，2 byte 即可表示 65535，远超 listpack 实际承载量（一般单 entry 上限约 1 KB）。
- **`entry[]`**：连续紧密排列。
- **`FF`**：末尾的 0xFF 字节作为哨兵，方便反向遍历时检查越界。

## 三、entry 编码格式

每个 entry 由三段组成：

```text
┌───────────┬─────────────┬──────────┐
│ encoding  │   value     │ backlen  │
│ (1~5 byte)│ (任意长度)  │ (1~5 byte)│
└───────────┴─────────────┴──────────┘
       │            │           │
       │            │           └─ 记录"前一项"的字节数（关键创新）
       │            └─ 实际数据（整数、字符串）
       └─ 编码字节：高位标识类型，低位存值或长度
```

`encoding` 字节含义：

| 高位 | 含义 | 例子 |
|------|------|------|
| `0xxxxxxx` | 直接存 7 bit 整数 | `0x05` 表示 `5` |
| `10xxxxxx xxxxxxxx` | 6 bit 整数 + 1 byte | `0xC0 0x00` 表示 `0` |
| `110xxxxx ...` (3 byte) | 13 bit 整数 | `0xC0 0x00 0x00` |
| `1110xxxx ...` (5 byte) | 32 bit 整数 | `0xC0 ...` |
| `1111xxxx` | 字符串，长度由 xxxx + 后跟长度字节决定 | 小字符串 vs 大字符串分流 |

`backlen` 反向记录前一项总字节数，采用变长编码：

```c
// 1 byte 表示：0~127
// 2 byte 表示：128~16383（首字节 0x80~0xBF）
// 5 byte 表示：>16383
```

反向遍历从 `FF` 往左数即可重新定位每一项的起始位置。

## 四、与 ziplist 的关键对比

| 维度 | ziplist | listpack |
|------|---------|----------|
| 反向定位字段 | `prevrawlen` 在 entry **头部** | `backlen` 在 entry **尾部** |
| 前项长度变更影响 | 后项必须级联改写 | 不影响任何其他 entry |
| 最坏插入复杂度 | O(N²) | O(N)（仅单点 memmove） |
| 字段读取 | `encoding + value + prevrawlen` | `encoding + value + backlen` |
| 长度上限 | 单 entry 64 KB | 单 entry 1 GB（受 `max_encoding` 限制） |
| 是否仍在使用 | Redis 7 已基本废弃 | Hash / Set / ZSet / QuickList 默认编码 |

核心差异的图示：

```text
       ziplist 插入超长 entry：
   ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐
   │ A │ │ B │ │ C │ │ D │ │ E │     初始
   └───┘ └───┘ └───┘ └───┘ └───┘
                     ↓ 在 B 前插入 254 byte
   ┌──────┐ ┌────────┐ ┌──────┐ ┌──────┐ ┌──────┐
   │  A   │ │ 新entry│ │  C'  │ │  D'  │ │  E'  │   prevrawlen 全部重写
   └──────┘ └────────┘ └──────┘ └──────┘ └──────┘
                                            ↑ 级联更新

       listpack 插入超长 entry：
   ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
   │ A  │ │ B  │ │ C  │ │ D  │ │ E  │     初始（各自 backlen 独立）
   └────┘ └────┘ └────┘ └────┘ └────┘
            ↓ 在 B 前插入 254 byte
   ┌────┐ ┌────────┐ ┌────┐ ┌────┐ ┌────┐
   │ A  │ │ 新entry│ │ C  │ │ D  │ │ E  │   只有新 entry 内部的 backlen 需要写
   └────┘ └────────┘ └────┘ └────┘ └────┘
                                       ↑ 无级联
```

## 五、listpack 的局限性

listpack 并非万能。它假设**整体小**才划算，一旦元素数或单 entry 体积超阈值就会被替换为更通用的结构：

- Hash：`OBJ_HASH_MAX_LISTPACK_ENTRIES=128`，`OBJ_HASH_MAX_LISTPACK_VALUE=64`
- ZSet：`OBJ_ZSET_MAX_LISTPACK_ENTRIES=128`，`OBJ_ZSET_MAX_LISTPACK_VALUE=64`
- QuickList 中的节点：每个 listpack 节点不超过 `list-max-listpack-size`（默认 -2 即 8 KB）

超出后编码升级由 Redis 自动完成，对客户端透明。

## 六、操作复杂度速查

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| `lpInsert` 头部/尾部 | O(1) | 仅涉及 memmove |
| `lpInsert` 中间位置 | O(N) | 线性扫描定位 |
| `lpDelete` | O(N) | 需要把后续 entry 整体前移 |
| `lpLength` | O(1) | 直接读 `num_elements` |
| `lpFind` | O(N) | 顺序遍历 |

## 七、面试要点

- **backlen 为什么能解决级联更新**？因为它记录的是"前一项"长度，且写在当前 entry 尾部；前一项膨胀时不会改变自己 entry 的字节数，自然不会向后传染。
- **backlen 放尾部还有什么好处**？可以让 listpack 单次分配连续内存时不需要预留扩展空间，与 ziplist 同样的内存紧凑度。
- **为什么 Redis 7 不彻底干掉 ziplist**？AOF 重写、Stream 早期版本、部分 Cluster bus 消息仍然依赖 ziplist 的兼容性，新模块一律用 listpack。

## 八、下一步

listpack 是所有紧凑容器的"心脏"。但单个 listpack 不能太长，于是 Redis 又把它装进了双向链表——这就是 QuickList。

**下一步：** [🔗 QuickList](/02-datastruct/quicklist)