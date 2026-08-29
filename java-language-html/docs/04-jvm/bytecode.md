---
title: 字节码 / 指令
date: 2026-08-15  # date-auto-injected
---
# 字节码
- javap -c classFile: disassemble
- Invocation: invokespecial (`<init>`/private/super), invokevirtual (instance), invokestatic (static), invokeinterface (interface), invokedynamic (lambda)
```bash
javap -c -v MyClass.class
```