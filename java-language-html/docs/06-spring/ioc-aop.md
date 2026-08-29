---
title: IoC / DI / AOP
date: 2026-08-15  # date-auto-injected
---
# IoC / DI / AOP
- IoC: container manages bean lifecycle, not you
- DI: constructor injection (recommended), field injection (@Autowired), setter injection
- AOP: JDK dynamic proxy (interface-based) vs CGLIB proxy (class-based)
- Bean scopes: singleton (default), prototype, request, session
```java
@Service
public class UserService {
  private final UserRepository repo;  // constructor injection
  public UserService(UserRepository repo) { this.repo = repo; }
}
@Aspect @Component
class LogAspect {
  @Around("@annotation(Log)")
  Object log(ProceedingJoinPoint pjp) throws Throwable {
    long start = System.currentTimeMillis();
    Object result = pjp.proceed();
    System.out.println(pjp.getSignature() + " took " + (System.currentTimeMillis() - start));
    return result;
  }
}
```