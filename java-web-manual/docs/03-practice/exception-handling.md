---
title: 异常处理
---

# 异常处理

统一的异常处理是系统稳定的基石，确保错误信息清晰、可追踪、不泄露敏感信息。

## 全局异常处理

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    // 业务异常
    @ExceptionHandler(BusinessException.class)
    public Result<Void> handleBusiness(BusinessException e) {
        log.warn("业务异常: code={}, msg={}", e.getCode(), e.getMessage());
        return Result.error(e.getCode(), e.getMessage());
    }

    // 参数校验异常
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<Void> handleValidation(MethodArgumentNotValidException e) {
        String msg = e.getBindingResult().getFieldErrors().stream()
            .map(f -> f.getField() + ": " + f.getDefaultMessage())
            .collect(Collectors.joining("; "));
        return Result.error(1001, "参数校验失败: " + msg);
    }

    // 兜底异常（不暴露细节给前端）
    @ExceptionHandler(Exception.class)
    public Result<Void> handleUnknown(Exception e) {
        log.error("系统异常: ", e);
        return Result.error(5000, "系统繁忙，请稍后重试");
    }
}
```

## 自定义业务异常

```java
public class BusinessException extends RuntimeException {
    private final int code;

    public BusinessException(int code, String message) {
        super(message);
        this.code = code;
    }

    // 常用异常快捷方法
    public static BusinessException notFound(String resource) {
        return new BusinessException(2004, resource + "不存在");
    }
}
```

## 异常处理原则

| 原则 | 说明 |
|---|---|
| 不吞异常 | finally 块不要 return，catch 后要记录日志 |
| 不暴露细节 | 生产环境不返回堆栈信息给前端 |
| 分层处理 | ControllerAdvice 统一拦截，Service 层只管抛 |
| 异常转换 | 第三方异常转为业务异常再抛出 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="exception-handling" :height="400" />
