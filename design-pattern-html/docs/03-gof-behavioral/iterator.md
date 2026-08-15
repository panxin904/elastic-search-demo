---
title: Iterator 迭代器模式
description: 顺序访问聚合对象 + Java Iterator / Go range / TypeScript Iterable / Rust IntoIterator
---

# Iterator 迭代器模式

## 核心问题

需要**顺序访问**聚合对象中的元素，但不暴露聚合对象的**内部表示**（数组 / 列表 / 树）。

**真实场景**：
- Java Collection（List / Set / Map 都有 Iterator）
- JavaScript for-of（任何实现 Iterable 的对象）
- Rust `for x in vec`（任何实现 IntoIterator 的对象）
- 数据库游标（cursor）

## 核心思想

提供一种方法顺序访问聚合对象中的各个元素，而不暴露其内部表示。

**关键角色**：
- **Iterator**：迭代器接口（`hasNext()` / `next()`）
- **ConcreteIterator**：具体迭代器（持有游标 + 聚合引用）
- **Aggregate**：聚合接口（创建迭代器）
- **ConcreteAggregate**：具体聚合（返回具体迭代器）

## Java 实现

```java
interface Iterator<E> {
    boolean hasNext();
    E next();
}

interface Iterable<E> {
    Iterator<E> iterator();
}

// 具体迭代器
class ListIterator<E> implements Iterator<E> {
    private final List<E> list;
    private int cursor = 0;

    public ListIterator(List<E> list) { this.list = list; }

    @Override public boolean hasNext() { return cursor < list.size(); }
    @Override public E next() { return list.get(cursor++); }
}

// 具体聚合
class MyList<E> implements Iterable<E> {
    private Object[] elements = new Object[10];
    private int size = 0;

    public void add(E e) { elements[size++] = e; }

    @Override public Iterator<E> iterator() { return new ListIterator<>(Arrays.asList((E[]) elements)); }
}

// 用法
MyList<String> list = new MyList<>();
list.add("a"); list.add("b"); list.add("c");

for (Iterator<String> it = list.iterator(); it.hasNext(); ) {
    System.out.println(it.next());
}

// 或 Java 5+ foreach（语法糖）
for (String s : list) {
    System.out.println(s);
}
```

## Java 8+ Stream API

```java
list.stream()
    .filter(s -> s.length() > 1)
    .map(String::toUpperCase)
    .forEach(System.out::println);
```

## Go range 与 自定义迭代器

```go
// 基本类型直接用 range
for i, v := range []string{"a", "b", "c"} {
    fmt.Println(i, v)
}

// Map
m := map[string]int{"a": 1, "b": 2}
for k, v := range m {
    fmt.Println(k, v)
}

// 自定义迭代器（Go 1.23+ range over func）
type Counter struct{ max int }

func (c *Counter) Yield() func() (int, bool) {
    i := 0
    return func() (int, bool) {
        if i < c.max {
            i++
            return i, true
        }
        return 0, false
    }
}

// Go 1.23+
c := &Counter{max: 5}
for v := range c.Yield() {
    fmt.Println(v)
}
// 1 2 3 4 5

// Go 1.22 及更早：用 callback 模拟
type Iter[T any] struct {
    next func() (T, bool)
}

func (it Iter[T]) ForEach(fn func(T)) {
    for v, ok := it.next(); ok; v, ok = it.next() {
        fn(v)
    }
}
```

## TypeScript Iterable Protocol

```typescript
// 实现 Symbol.iterator 协议
class Range implements Iterable<number> {
    constructor(private from: number, private to: number) {}

    *[Symbol.iterator]() {
        for (let i = this.from; i <= this.to; i++) {
            yield i;
        }
    }
}

// 用法：for-of
for (const n of new Range(1, 5)) {
    console.log(n);  // 1 2 3 4 5
}

// 用法：spread
const arr = [...new Range(1, 5)];  // [1, 2, 3, 4, 5]

// 用法：Array.from
const arr2 = Array.from(new Range(1, 5));  // [1, 2, 3, 4, 5]

// 用法：解构
const [first, second, ...rest] = new Range(1, 5);
// first=1, second=2, rest=[3,4,5]

// 异步迭代器
class AsyncStream implements AsyncIterable<number> {
    async *[Symbol.asyncIterator]() {
        yield 1;
        await new Promise(r => setTimeout(r, 1000));
        yield 2;
        yield 3;
    }
}

for await (const n of new AsyncStream()) {
    console.log(n);  // 1 (1s 后) 2 3
}
```

## 实战：数据库游标

数据库游标是迭代器的天然案例：

```java
// JDBC ResultSet 就是迭代器
try (Connection conn = dataSource.getConnection();
     Statement stmt = conn.createStatement();
     ResultSet rs = stmt.executeQuery("SELECT * FROM users")) {
    while (rs.next()) {  // 迭代
        long id = rs.getLong("id");
        String name = rs.getString("name");
        // 处理一行
    }
}

// Spring JdbcTemplate + RowCallbackHandler
jdbcTemplate.query("SELECT * FROM large_table", rs -> {
    // 每行回调
});

// 流式 API（避免一次性加载到内存）
@Query("SELECT u FROM User u")
Stream<User> findAllStream();  // Hibernate stream

try (Stream<User> stream = repo.findAllStream()) {
    stream.forEach(user -> {
        // 处理一行
    });
}
```

流式迭代器只把当前行加载到内存，PB 级数据也能处理。

## 适用边界

✅ **使用场景**：
- 集合遍历（List / Set / Map）
- 数据库游标（流式查询）
- 树形结构遍历（DFS / BFS）
- 自定义顺序访问

❌ **避免场景**：
- 直接用 for-each / range 更简单
- 随机访问为主（迭代器是单向的）
- 业务需要并行遍历（迭代器通常不是线程安全的）

🔄 **与 for-each 关系**：
- Java 的 for-each 就是 Iterator 的语法糖
- Python 的 for-in 也是迭代器协议
- JavaScript 的 for-of 调用 Symbol.iterator

💡 **最佳实践**：
- 迭代器应该是单向的（next() 不支持 previous）
- 用 fail-fast（检测到结构性修改抛 ConcurrentModificationException）
- Go 1.23+ 可以直接 range over function
- TypeScript 用 Generator (`function*`) 实现最简洁
