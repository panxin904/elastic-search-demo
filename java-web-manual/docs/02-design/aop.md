---
title: AOP 切面
date: 2026-08-15  # date-auto-injected
---

# AOP 切面编程

AOP（Aspect-Oriented Programming）在不修改原有代码的前提下，通过"切面"横向织入增强逻辑。

## 典型应用场景

| 场景 | 说明 |
|---|---|
| 日志记录 | 自动记录方法入参、出参、耗时 |
| 事务管理 | @Transactional 就是 AOP 实现 |
| 权限校验 | 方法执行前校验权限 |
| 缓存处理 | 方法结果自动缓存 |
| 异常处理 | 统一拦截异常并转换 |
| 接口限流 | 方法级别限流 |

## 自定义切面

```java
@Aspect
@Component
@Slf4j
public class LogAspect {

    @Around("@annotation(apiOperation)")
    public Object around(ProceedingJoinPoint point, ApiOperation apiOperation)
            throws Throwable {
        String method = point.getSignature().getName();
        Object[] args = point.getArgs();
        log.info("方法开始: {}, 参数: {}", method, args);

        long start = System.currentTimeMillis();
        try {
            Object result = point.proceed();
            log.info("方法结束: {}, 耗时: {}ms", method,
                System.currentTimeMillis() - start);
            return result;
        } catch (Exception e) {
            log.error("方法异常: {}, 错误: {}", method, e.getMessage());
            throw e;
        }
    }
}
```

## 通知类型

| 类型 | 注解 | 时机 |
|---|---|---|
| 前置 | @Before | 方法执行前 |
| 后置 | @After | 方法执行后（正常+异常） |
| 返回后 | @AfterReturning | 方法正常返回后 |
| 异常后 | @AfterThrowing | 方法抛出异常后 |
| 环绕 | @Around | 包裹整个方法，最强大 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="aop" :height="400" />
