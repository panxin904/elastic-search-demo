---
title: Singleton 单例模式
description: 全局唯一实例 + 多语言实现 + 线程安全 + 序列化攻击 + 分布式陷阱
---

# Singleton 单例模式

## 核心问题

保证一个类只有一个实例，并提供全局访问点。

**动机**：当系统中需要「全局唯一的资源」时（如配置管理器、日志器、线程池），用全局变量污染代码，又会被多线程并发问题反复纠缠。

**真实场景**：
- 应用配置（`application.properties` / `app.yaml`）：整个 JVM 一份
- 日志器（Logger）：所有业务代码共享一个，避免重复 IO
- 硬件抽象（GPU / 打印机）：物理资源只允许一个 wrapper

## 核心思想

将「对象是否已存在」的判断逻辑放在类内部，对外只暴露一个 `getInstance()` 方法。

**实现三要点**：
1. **私有构造器**：外部无法 `new`
2. **静态实例变量**：类自己持有唯一实例
3. **静态访问方法**：第一次调用时创建，后续直接返回

## Java 实现

## 双重检查锁（DCL，推荐）

```java
public final class Singleton {
    // volatile 防止指令重排导致返回未初始化对象
    private static volatile Singleton instance;

    private Singleton() {
        // 防止反射攻击
        if (instance != null) {
            throw new RuntimeException("Singleton already constructed");
        }
    }

    public static Singleton getInstance() {
        if (instance == null) {                          // 第一次检查（无锁）
            synchronized (Singleton.class) {
                if (instance == null) {                  // 第二次检查（加锁）
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }

    // 防止反序列化创建新对象
    protected Object readResolve() {
        return getInstance();
    }
}
```

## 静态内部类（最优雅）

```java
public class Singleton {
    private Singleton() {}

    private static class Holder {
        private static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return Holder.INSTANCE;  // 类加载时初始化，JVM 保证线程安全
    }
}
```

## 枚举（Effective Java 作者 Josh Bloch 推荐）

```java
public enum Singleton {
    INSTANCE;
    private final Config config;

    Singleton() {
        this.config = loadConfig();
    }

    public Config getConfig() { return config; }
}
// 用法：Singleton.INSTANCE.getConfig();
```

## 多语言实现

## Go：sync.Once 是事实标准

```go
package config

import "sync"

var (
    cfg  *Config
    once sync.Once
)

func Get() *Config {
    once.Do(func() {
        cfg = &Config{ApiKey: loadFromEnv()}
    })
    return cfg
}
```

`sync.Once` 底层使用 atomic + mutex，保证 `loadConfig()` 在并发下只执行一次。

## TypeScript：ES Module 单例

```typescript
// config.ts
class Config {
    public readonly apiKey = process.env.API_KEY!;
}

export const config = new Config();
// 任何地方 import { config } from './config' 都拿到同一个实例
```

ES Module 的 import 缓存机制天然就是单例。

## Python：`__new__` 重写

```python
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # True
```

## 实战陷阱

## 1. 分布式陷阱

单 JVM 的单例 ≠ 集群的单例。集群下每个 JVM 都有自己的「单例」，导致 N 个实例。

**解法**：用 Redis / ZooKeeper 实现分布式单例（但其实没必要——分布式场景通常用无状态服务 + 集中存储）。

## 2. 测试陷阱

单例难以替换 mock，导致单元测试无法隔离。

**解法**：
- 使用 DI 容器（Spring 默认单例，但可以被覆盖）
- 测试时 `@MockBean` 替换单例
- 或单例自身实现 `IConfig` 接口，测试时注入 fake

## 3. 序列化攻击

```java
// 如果 Singleton 实现 Serializable，反序列化会创建新对象
Singleton s1 = Singleton.getInstance();
ObjectOutputStream oos = new ObjectOutputStream(...);
oos.writeObject(s1);
// 反序列化得到新对象，破坏单例
```

**解法**：实现 `readResolve()` 返回原单例（见上面 Java 示例）。

## 4. 反射攻击

```java
Constructor<Singleton> ctor = Singleton.class.getDeclaredConstructor();
ctor.setAccessible(true);
Singleton hacked = ctor.newInstance();  // 绕过私有构造器
```

**解法**：在构造器中检查 `instance != null`（见上面 Java 示例）。

## 适用边界

✅ **使用场景**：
- 无状态资源（Logger / Config / ThreadPool）
- 全局缓存（带 TTL 的进程内缓存）
- 硬件抽象（GPU / 打印机）

❌ **避免场景**：
- 业务实体（User / Order 必须多例）
- 有状态对象（会引发并发问题）
- 需要测试替身的场景
- 集群服务（用无状态 + Redis 替代）

🔄 **替代方案**：
- **Spring 容器**：`@Scope("singleton")` + DI（推荐）
- **Go sync.Once**：替代手写单例
- **Python 模块级变量**：本身就是单例
- **TypeScript ES Module**：天然单例

📚 **与其他模式关系**：
- **Factory Method**：工厂方法返回的可以是单例
- **Abstract Factory**：抽象工厂的每个具体工厂通常实现为单例
- **Facade**：外观类经常用单例实现


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->
