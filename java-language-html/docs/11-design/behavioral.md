---
title: 行为型设计模式
---
# 行为型模式
- Strategy: interchangeable algorithms (Comparator)
- Observer: publish/subscribe (EventListener)
- Chain of Responsibility: pass request along chain (Servlet Filters)
- Template Method: define skeleton, subclasses fill in details
- Command: encapsulate request as object (Runnable/Callable)
- State: change behavior based on internal state
```java
// Strategy
List<String> names = Arrays.asList("Bob", "Alice");
names.sort(String::compareToIgnoreCase);

// Template Method
abstract class DataProcessor {
  public final void process() { read(); transform(); write(); }
  abstract void read(); abstract void transform(); abstract void write();
}
```