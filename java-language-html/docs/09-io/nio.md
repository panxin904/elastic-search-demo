---
title: BIO / NIO / AIO
date: 2026-08-15  # date-auto-injected
---
# BIO / NIO / AIO
- BIO: blocking I/O, one thread per connection
- NIO: non-blocking, Buffer (position/limit/capacity), Channel (FileChannel/SocketChannel), Selector (multiplex)
- AIO: asynchronous, callback or Future
- Zero-copy: FileChannel.transferTo (sendfile syscall)
```java
// NIO selector
var selector = Selector.open();
var channel = ServerSocketChannel.open();
channel.configureBlocking(false);
channel.register(selector, SelectionKey.OP_ACCEPT);
while (true) {
  selector.select();
  for (var key : selector.selectedKeys()) {
    if (key.isAcceptable()) { /* accept */ }
    if (key.isReadable())   { /* read */ }
  }
}
```