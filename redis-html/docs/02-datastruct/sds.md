---
title: SDS 简单动态字符串
date: 2026-08-15  # date-auto-injected
---

# SDS 简单动态字符串

SDS（Simple Dynamic String）是 Redis 的字符串实现。键名、命令参数、普通字符串值以及复制缓冲区都可能使用它。SDS 仍以 `\0` 结尾，因此能复用部分 C 字符串函数；但长度与容量由头部记录，不必依赖终止符。

## 一、内存结构

下面是便于理解的统一结构示意。真实源码会根据字符串长度选择不同头部，字段位宽也不完全相同。

```c
struct sdshdr {
    int len;       // buf 中已使用的字节数
    int alloc;     // buf 总容量，不含末尾 \0
    char flags[];  // 低 3 bit 标识头部类型
    char buf[];    // 字节数组，末尾兼容性地保留 \0
};
```

```text
低地址                                              高地址
┌────────┬────────┬───────┬────────────────────┬─────┐
│  len   │ alloc  │ flags │ buf: h e l l o     │ \0  │
└────────┴────────┴───────┴────────────────────┴─────┘
                         ▲ 返回给调用者的 sds 指针
```

`len` 表示逻辑长度，`alloc - len` 是剩余空间。调用者拿到的指针直接指向 `buf`，需要元数据时再向前偏移读取头部。

## 二、五种头部类型

SDS 按容量选择 `sdshdr5/8/16/32/64`，避免短字符串也背负大整数头部。所有类型都通过紧邻 `buf` 的一个字节 `flags` 判型。

| 类型 | len/alloc 位宽 | flags 的作用 | 适用特点 |
|---|---:|---|---|
| `sdshdr5` | 无独立字段 | 低 3 bit 存类型，高 5 bit 直接存长度 | 最多 31 字节，通常只读使用 |
| `sdshdr8` | 8 bit | 低 3 bit 为 `SDS_TYPE_8` | 短字符串，头部紧凑 |
| `sdshdr16` | 16 bit | 低 3 bit 为 `SDS_TYPE_16` | 中等字符串 |
| `sdshdr32` | 32 bit | 低 3 bit 为 `SDS_TYPE_32` | 大字符串 |
| `sdshdr64` | 64 bit | 低 3 bit 为 `SDS_TYPE_64` | 超大字符串，主要用于 64 位平台 |

```c
#define SDS_TYPE_MASK 7
#define SDS_TYPE_5    0
#define SDS_TYPE_8    1
#define SDS_TYPE_16   2
#define SDS_TYPE_32   3
#define SDS_TYPE_64   4

unsigned char type = s[-1] & SDS_TYPE_MASK;
```

`sdshdr5` 是特例：`flags = (len << 3) | SDS_TYPE_5`。其余四类把 `len`、`alloc` 分开保存，扩容时无需把长度塞回 `flags`。

## 三、为什么不直接用 C 字符串

| 能力 | C 字符串 | SDS |
|---|---|---|
| 获取长度 | `strlen` 扫描，O(N) | 读取 `len`，O(1) |
| 内容限制 | 遇到 `\0` 即结束 | 按 `len` 读取，二进制安全 |
| 追加数据 | 调用者自行检查容量 | API 先扩容，杜绝缓冲区溢出 |
| 修改代价 | 常反复分配 | 复用预留空间，减少分配次数 |

SDS 可以保存图片、压缩数据或协议帧中的任意字节。中间即使出现 `\0`，也不会被误判为结尾；末尾额外的 `\0` 只用于兼容需要 C 字符串的只读函数。

```c
// 逻辑内容是 {'A', '\0', 'B'}，长度仍为 3
sds value = sdsnewlen("A\0B", 3);
assert(sdslen(value) == 3);
```

## 四、预分配与惰性释放

追加前，SDS 计算新长度 `newlen`。经典策略是：

```text
newlen < 1 MB   => alloc = 2 * newlen
newlen >= 1 MB  => alloc = newlen + 1 MB
free = alloc - len
```

例如字符串从 100 字节增长到 600 字节，可申请约 1200 字节；增长到 2 MB 时，则申请约 3 MB。这样既降低连续追加时的 `realloc` 次数，又避免超大字符串按两倍扩容造成浪费。

缩短字符串时通常只更新 `len` 并写入新的末尾 `\0`，不立即归还多余空间，这就是**惰性释放**。后续追加可直接复用 `free`；确实需要回收时，再调用压缩容量的 API。预分配优化增长路径，惰性释放优化删改后再增长的路径，两者共同减少内存分配与拷贝。

## 五、记忆要点

SDS 的核心不是“给字符数组加一个头”，而是用类型化头部换来 O(1) 长度、容量感知和二进制安全。面试中可按“`len/alloc/flags/buf` → 五种头部 → 扩缩容策略 → 与 C 字符串对比”的顺序回答。

**下一步：** [🗂️ Dict 哈希表](/02-datastruct/dict)
