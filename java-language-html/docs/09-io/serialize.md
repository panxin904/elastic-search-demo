---
title: 序列化 / JSON / ProtoBuf
date: 2026-08-15  # date-auto-injected
---
# 序列化
- Serializable: writeObject/readObject, serialVersionUID, transient fields
- Jackson: @JsonProperty, @JsonIgnore, @JsonFormat, ObjectMapper
- ProtoBuf: binary, schema-first, smaller/faster than JSON
- Kryo: fast binary serialization (used by Spark/Dubbo)
```java
var mapper = new ObjectMapper();
String json = mapper.writeValueAsString(user);
User u = mapper.readValue(json, User.class);
```