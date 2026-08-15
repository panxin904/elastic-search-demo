---
title: 智能指针
---

# 智能指针

智能指针是实现了 Deref + Drop 的数据结构，管理堆内存的所有权与生命周期。

## 一句话总结

> **智能指针 = 实现 Deref + Drop 的指针**。**核心：Box / Rc / Arc / RefCell / Mutex**。

---

## Box\<T\>：堆分配

```rust
let b = Box::new(5);
println!("{}", b);  // 自动 deref

// 递归类型
enum List {
    Cons(i32, Box<List>),
    Nil,
}

let list = Cons(1, Box::new(Cons(2, Box::new(Cons(3, Box::new(Nil))))));

// Trait Object
let shapes: Vec<Box<dyn Draw>> = vec![
    Box::new(Circle { r: 1.0 }),
    Box::new(Square { s: 2.0 }),
];
```

## Rc\<T\>：单线程引用计数

```rust
use std::rc::Rc;

let a = Rc::new(5);
let b = Rc::clone(&a);
let c = Rc::clone(&a);

println!("Count: {}", Rc::strong_count(&a));  // 3
```

## Arc\<T\>：多线程引用计数

```rust
use std::sync::Arc;
use std::thread;

let data = Arc::new(vec![1, 2, 3]);
let mut handles = vec![];

for _ in 0..3 {
    let data = Arc::clone(&data);
    let handle = thread::spawn(move || {
        println!("{:?}", data);
    });
    handles.push(handle);
}

for handle in handles {
    handle.join().unwrap();
}
```

## RefCell\<T\>：单线程内部可变性

```rust
use std::cell::RefCell;

let data = RefCell::new(5);

{
    let mut borrowed = data.borrow_mut();
    *borrowed += 1;
}

println!("{}", data.borrow());
```

## Mutex\<T\>：多线程内部可变性

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..10 {
    let counter = Arc::clone(&counter);
    let handle = thread::spawn(move || {
        let mut num = counter.lock().unwrap();
        *num += 1;
    });
    handles.push(handle);
}

for handle in handles {
    handle.join().unwrap();
}
```

## 4 大智能指针组合

```rust
use std::rc::Rc;
use std::cell::RefCell;

let shared = Rc::new(RefCell::new(vec![1, 2, 3]));
let a = Rc::clone(&shared);
let b = Rc::clone(&shared);

a.borrow_mut().push(4);
b.borrow_mut().push(5);

// Arc<Mutex<T>>：多线程共享可变
use std::sync::{Arc, Mutex};

let shared = Arc::new(Mutex::new(0));
```

## Deref 与 DerefMut

```rust
use std::ops::{Deref, DerefMut};

struct MyBox<T>(T);

impl<T> Deref for MyBox<T> {
    type Target = T;
    fn deref(&self) -> &T {
        &self.0
    }
}

impl<T> DerefMut for MyBox<T> {
    fn deref_mut(&mut self) -> &mut T {
        &mut self.0
    }
}

let x = MyBox(5);
println!("{}", *x);
```

## Weak\<T\>：弱引用

```rust
use std::rc::{Rc, Weak};

struct Node {
    value: i32,
    parent: Weak<Node>,
    children: Vec<Rc<Node>>,
}

let parent = Rc::new(Node { value: 1, parent: Weak::new(), children: vec![] });
let child = Rc::new(Node { value: 2, parent: Rc::downgrade(&parent), children: vec![] });
parent.children.push(Rc::clone(&child));

if let Some(p) = child.parent.upgrade() {
    println!("Parent value: {}", p.value);
}
```

## Drop Trait

```rust
struct CustomSmartPointer {
    data: String,
}

impl Drop for CustomSmartPointer {
    fn drop(&mut self) {
        println!("Dropping with data: {}", self.data);
    }
}
```

## 实战案例：LRU 缓存

```rust
use std::collections::HashMap;
use std::cell::RefCell;
use std::rc::Rc;

struct Node<K, V> {
    key: K,
    value: V,
    prev: Option<Rc<RefCell<Node<K, V>>>>,
    next: Option<Rc<RefCell<Node<K, V>>>>,
}

pub struct LruCache<K, V> {
    capacity: usize,
    map: HashMap<K, Rc<RefCell<Node<K, V>>>>,
}

impl<K: Clone + Eq + std::hash::Hash, V> LruCache<K, V> {
    pub fn new(capacity: usize) -> Self {
        Self { capacity, map: HashMap::new() }
    }

    pub fn get(&mut self, key: &K) -> Option<V> {
        self.map.get(key).map(|node| node.borrow().value.clone())
    }

    pub fn put(&mut self, key: K, value: V) {
        let node = Rc::new(RefCell::new(Node {
            key: key.clone(),
            value,
            prev: None,
            next: None,
        }));
        self.map.insert(key, node);
    }
}
```

## 关联章节

- **02-types-traits/advanced-types**：高级类型
- **04-concurrency/channels**：Channel 与共享状态
- **05-systems/unsafe**：unsafe

## 一句话总结

> **智能指针 = Rust 内存管理的核心抽象**：Box（堆分配）/ Rc/Arc（共享）/ RefCell/Mutex（内部可变）**。
