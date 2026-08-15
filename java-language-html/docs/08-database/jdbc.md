---
title: JDBC / HikariCP
---
# JDBC / HikariCP
- JDBC: DriverManager → DataSource (connection pooling)
- PreparedStatement: prevent SQL injection, pre-compiled
- HikariCP: fastest pool, defaults: pool-size=10, idle-timeout=600s, max-lifetime=1800s
```java
var ds = new HikariDataSource();
ds.setJdbcUrl("jdbc:postgresql://localhost/db");
ds.setUsername("user");
ds.setMaximumPoolSize(20);

try (var conn = ds.getConnection();
     var ps = conn.prepareStatement("SELECT * FROM users WHERE id = ?")) {
  ps.setLong(1, 1L);
  var rs = ps.executeQuery();
  while (rs.next()) System.out.println(rs.getString("name"));
}
```