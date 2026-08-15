---
title: CompletableFuture
---
# CompletableFuture
- thenApply (sync map), thenApplyAsync (async)
- thenCompose (flatMap), thenCombine (zip two futures)
- allOf (wait all), anyOf (first done)
- exceptionally (handle error), handle (map + error)
```java
var f1 = CompletableFuture.supplyAsync(() -> fetchUser(1));
var f2 = CompletableFuture.supplyAsync(() -> fetchOrders(1));
var result = f1.thenCombine(f2, (user, orders) -> new Result(user, orders));
result.join();
```