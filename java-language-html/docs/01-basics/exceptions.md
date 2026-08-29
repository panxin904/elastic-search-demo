---
title: 异常处理
date: 2026-08-15  # date-auto-injected
---
# 异常处理
- Checked (IOException/SQLException) vs Unchecked (RuntimeException)
- try-with-resources (AutoCloseable) for auto cleanup
- Custom exceptions: extend RuntimeException for unchecked, Exception for checked
- finally always runs (except System.exit)
```java
try (var conn = DriverManager.getConnection(url)) {
  var rs = conn.createStatement().executeQuery("SELECT 1");
} catch (SQLException e) {
  throw new DataAccessException("DB error", e);
}
```