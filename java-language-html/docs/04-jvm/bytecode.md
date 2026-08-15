---
title: 字节码 / 指令
---
# 字节码
- javap -c classFile: disassemble
- Invocation: invokespecial (`<init>`/private/super), invokevirtual (instance), invokestatic (static), invokeinterface (interface), invokedynamic (lambda)
```bash
javap -c -v MyClass.class
```