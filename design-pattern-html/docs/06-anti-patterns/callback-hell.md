---
title: Callback Hell 回调地狱
description: 症状 + 病因 + 药方 + async/await + Promise + RxJS
---

# Callback Hell 回调地狱

## 症状

```javascript
// 嵌套 8 层回调，可读性为 0
getData(function(a) {
    {
        getMoreData(a, function(b) {
            {
                getMoreData(b, function(c) {
                    {
                        getMoreData(c, function(d) {
                            {
                                getMoreData(d, function(e) {
                                    {
                                        getMoreData(e, function(f) {
                                            // 最终在这里写业务逻辑
                                            console.log(f);
                                        }, errorHandler);
                                    }
                                }, errorHandler);
                            }
                        }, errorHandler);
                    }
                }, errorHandler);
            }
        }, errorHandler);
    }
}, errorHandler);
```

**典型表现**：
1. 嵌套层级 > 5
2. 每个回调都可能失败（errorHandler 重复）
3. 业务逻辑被埋到最深处
4. 错误处理复杂（多层 try-catch）
5. 难以追踪异步流程

## 病因

1. **JavaScript 早期没有 Promise / async-await**
   - ES5 之前只能用 callback
   - Node.js 早期 API 都是 callback 风格

2. **不熟悉现代异步原语**
   - 团队仍在用 callback 写新代码

3. **强行用回调解决异步问题**
   - 该用 Promise 的场景用了 callback
   - 该用 async/await 的场景用了 Promise.then

4. **第三方库 callback 嵌套（库设计问题）**
   - 某些库（如早期 fs / mongoose）API 就是 callback
   - 但现在都有 Promise 版本

5. **缺少 Async / Await 培训**
   - 团队没学过现代异步写法

## 药方

## 1. Promise 链

```javascript
// ✅ Promise 链（ES6+）
getData()
    .then(a => getMoreData(a))
    .then(b => getMoreData(b))
    .then(c => getMoreData(c))
    .then(d => getMoreData(d))
    .then(e => getMoreData(e))
    .then(f => {
        // 业务逻辑
        console.log(f);
    })
    .catch(err => {
        // 统一错误处理
        console.error(err);
    });
```

## 2. async/await（最现代）

```javascript
// ✅ async/await（ES2017+）
async function process() {
    try {
        const a = await getData();
        const b = await getMoreData(a);
        const c = await getMoreData(b);
        const d = await getMoreData(c);
        const e = await getMoreData(d);
        const f = await getMoreData(e);
        // 业务逻辑
        console.log(f);
    } catch (err) {
        // 统一错误处理
        console.error(err);
    }
}
```

## 3. 并行执行

```javascript
// ✅ 并行（如果任务独立）
const [a, b, c] = await Promise.all([
    getData1(),
    getData2(),
    getData3(),
]);
```

## 4. RxJS / Observables

```javascript
// ✅ RxJS（复杂异步流）
import { of, from, forkJoin } from 'rxjs';
import { mergeMap, catchError } from 'rxjs/operators';

from(initialData$).pipe(
    mergeMap(a => from(getMoreData(a))),
    mergeMap(b => from(getMoreData(b))),
    catchError(err => of({ error: err }))
).subscribe(result => console.log(result));
```

## 5. Coroutine（Kotlin / Python）

```kotlin
// Kotlin coroutine
suspend fun process() {
    try {
        val a = getData()
        val b = getMoreData(a)
        // ...
    } catch (e: Exception) {
        // 错误处理
    }
}
```

```python
# Python asyncio
async def process():
    try:
        a = await get_data()
        b = await get_more_data(a)
        # ...
    except Exception as e:
        # 错误处理
        pass
```

## 实战：Node.js 异步演进

```javascript
// ❌ 早期 Node.js (2010)
fs.readFile('file1.txt', function(err, data1) {
    if (err) throw err;
    fs.readFile('file2.txt', function(err, data2) {
        if (err) throw err;
        fs.readFile('file3.txt', function(err, data3) {
            if (err) throw err;
            console.log(data1 + data2 + data3);
        });
    });
});

// ✅ Node.js 现代（util.promisify）
const fs = require('fs').promises;
const data1 = await fs.readFile('file1.txt', 'utf-8');
const data2 = await fs.readFile('file2.txt', 'utf-8');
const data3 = await fs.readFile('file3.txt', 'utf-8');
console.log(data1 + data2 + data3);

// ✅ Promise.all 并行
const [data1, data2, data3] = await Promise.all([
    fs.readFile('file1.txt', 'utf-8'),
    fs.readFile('file2.txt', 'utf-8'),
    fs.readFile('file3.txt', 'utf-8'),
]);
```

## Go 也曾经有回调地狱

```go
// ❌ Go 早期（callback）
func process(cb func(result string, err error)) {
    go func() {
        // 嵌套回调
        fetch1(func(a string, err error) {
            if err != nil { cb("", err); return }
            fetch2(a, func(b string, err error) {
                if err != nil { cb("", err); return }
                fetch3(b, func(c string, err error) {
                    if err != nil { cb("", err); return }
                    cb(c, nil)
                })
            })
        })
    }()
}

// ✅ Go channel + goroutine
func process(ctx context.Context) (string, error) {
    a, err := fetch1(ctx)
    if err != nil { return "", err }
    b, err := fetch2(ctx, a)
    if err != nil { return "", err }
    c, err := fetch3(ctx, b)
    if err != nil { return "", err }
    return c, nil
}
```

## 异步错误处理

```javascript
// ❌ 异步 callback 错误处理（每层都要检查）
asyncTask1(function(err, result1) {
    if (err) return callback(err);
    asyncTask2(result1, function(err, result2) {
        if (err) return callback(err);
        asyncTask3(result2, function(err, result3) {
            if (err) return callback(err);
            callback(null, result3);
        });
    });
});

// ✅ async/await：try-catch 一处搞定
async function process() {
    try {
        const r1 = await asyncTask1();
        const r2 = await asyncTask2(r1);
        const r3 = await asyncTask3(r2);
        return r3;
    } catch (err) {
        // 任何一层出错都会被捕获
        console.error('Process failed:', err);
        throw err;
    }
}
```

## Promise 错误处理

```javascript
// .catch() 在链尾
getData()
    .then(a => getMoreData(a))
    .then(b => getMoreData(b))
    .catch(err => console.error(err));  // 任何 .then() 抛错都被捕获
```

## Go error 显式处理

```go
result, err := process(ctx)
if err != nil {
    log.Printf("process failed: %v", err)
    return err
}
```

Go 没有 try-catch，但每个调用都显式 err 判断，避免「忘了检查」。

## 适用边界

✅ **使用 async/await**：
- 所有现代 JavaScript / TypeScript 项目
- Node.js 12+ / 浏览器 ES2017+

✅ **使用 Promise**：
- 需要并行多个异步任务（Promise.all）
- 需要链式调用但不一定用 await

✅ **使用 RxJS**：
- 复杂异步流（debounce / throttle / 复杂合并）

✅ **使用 Coroutine**：
- Python（asyncio）
- Kotlin / Swift

❌ **避免 callback**：
- 新写的代码（用 Promise / async）
- ES2017+ 环境（用 async/await）
- 可以用 Promise 化的库（`util.promisify`）

💡 **最佳实践**：
- **优先 async/await**（最现代、可读性最好）
- **并行用 Promise.all**（而不是顺序 await）
- **try-catch 兜底**（一处处理所有错误）
- **超时处理**：`AbortController` / `Promise.race`
- **库选择**：选有 Promise 版本的库（不用 callback 版）
