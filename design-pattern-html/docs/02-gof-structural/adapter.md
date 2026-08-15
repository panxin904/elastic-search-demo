---
title: Adapter 适配器模式
description: 接口不兼容 + 对象适配 vs 类适配 + Java IO 适配器 + Spring HandlerAdapter
---

# Adapter 适配器模式

## 核心问题

系统中已经存在两个独立开发的模块，它们的接口不兼容，但需要一起工作。直接改源码成本太高（可能破坏现有调用方）。

**真实场景**：
- 旧系统接入新 SDK（旧的 logger 接口 vs 新的 SLF4J）
- 集成第三方库（库 v1 vs 库 v2 接口不同）
- 跨平台（macOS 文件路径 vs Windows 文件路径）

## 核心思想

把一个类的接口转换成客户端期望的另一种接口。让原本不兼容的类可以合作，而无需修改它们的源码。

**两种适配器**：
| 类型 | 实现 | 推荐 |
|---|---|---|
| 对象适配器 | 组合（持有被适配者） | ✅ |
| 类适配器 | 继承（多重继承） | ❌（Java / C# 不支持）

## Java 实现

## 对象适配器（推荐）

```java
// 目标接口（客户端期望的）
public interface MediaPlayer {
    void play(String audioType, String fileName);
}

// 被适配者（已存在的接口）
public class AdvancedMediaPlayer {
    public void playVlc(String fileName) { /* VLC 播放逻辑 */ }
    public void playMp4(String fileName) { /* MP4 播放逻辑 */ }
}

// 适配器
public class MediaAdapter implements MediaPlayer {
    private final AdvancedMediaPlayer advanced;

    public MediaAdapter(String audioType) {
        this.advanced = new AdvancedMediaPlayer();
    }

    @Override
    public void play(String audioType, String fileName) {
        if (audioType.equalsIgnoreCase("vlc")) {
            advanced.playVlc(fileName);
        } else if (audioType.equalsIgnoreCase("mp4")) {
            advanced.playMp4(fileName);
        }
    }
}

// 客户端使用
MediaPlayer player = new MediaAdapter("vlc");
player.play("vlc", "movie.vlc");  // 实际调用 AdvancedMediaPlayer.playVlc
```

## 类适配器（不推荐）

需要 Java 支持多重继承，目前用 `extends` + `implements` 模拟：

```java
public class MediaAdapter extends AdvancedMediaPlayer implements MediaPlayer {
    @Override
    public void play(String audioType, String fileName) {
        if (audioType.equalsIgnoreCase("vlc")) {
            playVlc(fileName);
        }
    }
}
```

C++ / Python 支持多重继承，但 Java / C# 只能走对象适配器。

## 实战案例

## Java IO 适配器

```java
// 把字节流适配成字符流
Reader reader = new InputStreamReader(
    new FileInputStream("data.txt"), StandardCharsets.UTF_8);

// 反过来，把字符流转成字节流
Writer writer = new OutputStreamWriter(
    new FileOutputStream("out.txt"), StandardCharsets.UTF_8);
```

`InputStreamReader` 就是经典的适配器，把 `InputStream`（字节）适配成 `Reader`（字符）。

## Arrays.asList（数组 → List）

```java
String[] arr = {"a", "b", "c"};
List<String> list = Arrays.asList(arr);  // 数组 → List
list.add("d");  // UnsupportedOperationException！是固定大小 List
```

## Spring HandlerAdapter

Spring MVC 用 HandlerAdapter 适配各种类型的 Controller：

```java
public interface HandlerAdapter {
    boolean supports(Object handler);
    ModelAndView handle(HttpServletRequest req, HttpServletResponse resp, Object handler);
}

// SimpleControllerHandlerAdapter 适配实现 Controller 接口的类
// HttpRequestHandlerAdapter 适配实现 HttpRequestHandler 接口的类
// RequestMappingHandlerAdapter 适配 @RequestMapping 注解方法
```

Spring 通过 HandlerAdapter 把不同形态的 Controller 统一适配成 `handle()` 调用。

## Go 适配器实战

```go
// 旧接口（第三方库）
type OldLogger interface {
    LogMessage(level, msg string)
}

// 新接口（我们的项目标准）
type Logger interface {
    Debug(msg string)
    Info(msg string)
    Warn(msg string)
    Error(msg string)
}

// 适配器
type OldToNewAdapter struct {
    old OldLogger
}

func (a *OldToNewAdapter) Debug(msg string) {
    a.old.LogMessage("DEBUG", msg)
}

func (a *OldToNewAdapter) Info(msg string) {
    a.old.LogMessage("INFO", msg)
}

func (a *OldToNewAdapter) Warn(msg string) {
    a.old.LogMessage("WARN", msg)
}

func (a *OldToNewAdapter) Error(msg string) {
    a.old.LogMessage("ERROR", msg)
}
```

## TypeScript：跨浏览器 API 适配

```typescript
// 旧浏览器没有 fetch
declare const fetch: (input: RequestInfo, init?: RequestInit) => Promise<Response>;

// 适配到统一接口
interface Http {
    get(url: string): Promise<any>;
    post(url: string, body: any): Promise<any>;
}

class FetchHttp implements Http {
    async get(url: string) {
        const r = await fetch(url);
        return r.json();
    }
    async post(url: string, body: any) {
        const r = await fetch(url, {
            method: 'POST',
            body: JSON.stringify(body)
        });
        return r.json();
    }
}

class XMLHttpRequestHttp implements Http {
    // 老浏览器实现
    async get(url: string) {
        return new Promise((resolve) => {
            const xhr = new XMLHttpRequest();
            xhr.open('GET', url);
            xhr.onload = () => resolve(JSON.parse(xhr.responseText));
            xhr.send();
        });
    }
}
```

## 适用边界

✅ **使用场景**：
- 接入第三方库（旧版本升级）
- 跨平台 / 跨语言集成
- 系统演进（保护现有代码）
- 单元测试（适配真实对象到 mock 接口）

❌ **避免场景**：
- 双方接口都你可控（直接改一边）
- 只是临时代码（一次性脚本不需要适配器）
- 适配链超过 3 层（说明接口设计本身有问题）

🔄 **与相关模式区别**：
- **Adapter**：转换现有接口
- **Bridge**：从设计开始就解耦抽象与实现
- **Decorator**：增强已有接口（不转换）
- **Facade**：简化子系统（多个 → 一个）

💡 **最佳实践**：
- 用对象适配器（组合），不用类适配器（继承）
- 适配器不暴露被适配者的方法（否则客户端会绕过适配器）
- 双适配器（两个接口互转）：考虑是否能合并成一个通用接口
