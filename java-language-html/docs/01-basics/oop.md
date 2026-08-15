---
title: OOP / 类与对象
---
# OOP / 类与对象

## 🧬 Encapsulation（封装）

```java
public class User {
    private String name;          // 字段私有
    private int age;

    // 公开 getter / setter
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public int getAge() { return age; }
    public void setAge(int age) {
        if (age < 0) throw new IllegalArgumentException();
        this.age = age;
    }
}
```

## 🧬 Inheritance（继承）

```java
class Animal {
    void eat() { System.out.println("eating"); }
}
class Dog extends Animal {
    void bark() { System.out.println("barking"); }
}
Dog dog = new Dog();
dog.eat();   // from Animal
dog.bark();  // from Dog
```

Java 单继承，多实现。

## 🧬 Polymorphism（多态）

```java
// 编译时多态（重载）
class Calc {
    int add(int a, int b) { return a + b; }
    double add(double a, double b) { return a + b; }
}

// 运行时多态（重写）
Animal a = new Dog();    // 父类引用指向子类对象
a.eat();                 // 调 Dog 的 eat（如果有 @Override）
```

## 🆚 Abstract Class vs Interface

| | Abstract Class | Interface |
|--|----------------|-----------|
| 构造器 | ✅ | ❌ |
| 实例变量 | ✅ | ❌（仅 static final） |
| 默认实现 | ✅ | ✅（default method） |
| 多继承 | ❌ | ✅ |
| 访问修饰 | 任意 | public（Java 9+ private） |
| 何时用 | 共享状态/行为 | 定义契约 |

```java
abstract class Shape {
    abstract double area();
    void print() { System.out.println(area()); }  // 模板方法
}
class Circle extends Shape {
    double r;
    double area() { return Math.PI * r * r; }
}

interface Flyable {
    void fly();
    default void land() { System.out.println("landing"); }
}
```

## 🏛️ SOLID

| 原则 | 含义 |
|------|------|
| **S** | 单一职责 |
| **O** | 开闭原则（对扩展开放，对修改关闭） |
| **L** | 里氏替换（子类能替换父类） |
| **I** | 接口隔离（最小接口） |
| **D** | 依赖倒转（依赖抽象不依赖具体） |

```java
// DIP 示例
interface Repository { User findById(Long id); }
class UserService {
    private final Repository repo;  // 依赖接口
    UserService(Repository repo) { this.repo = repo; }
}
```

## 🔗 下一步

- [数据类型 / 包装类](/01-basics/datatypes)
- [异常处理](/01-basics/exceptions)
- [泛型 / 注解 / 反射](/01-basics/generics)