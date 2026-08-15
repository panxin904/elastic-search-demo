---
title: Spring MVC
---
# Spring MVC
- DispatcherServlet flow: HandlerMapping → HandlerAdapter → Handler → ModelAndView → ViewResolver
- @RestController = @Controller + @ResponseBody
- @ExceptionHandler, @ControllerAdvice for global error handling
- HandlerInterceptor: preHandle, postHandle, afterCompletion
```java
@RestController
public class UserController {
  @GetMapping("/users/{id}")
  public User getUser(@PathVariable Long id) { return userService.findById(id); }
  @PostMapping("/users")
  public User create(@Valid @RequestBody UserDto dto) { return userService.create(dto); }
}
```