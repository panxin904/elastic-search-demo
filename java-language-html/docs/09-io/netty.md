---
title: Netty 框架
date: 2026-08-15  # date-auto-injected
---
# Netty
- EventLoopGroup: boss (accept) + worker (IO)
- ChannelPipeline: chain of ChannelHandlers
- ChannelHandler: ChannelInboundHandler (read) / ChannelOutboundHandler (write)
- ByteBuf: pooled memory, reference counting
```java
var boss = new NioEventLoopGroup(1);
var worker = new NioEventLoopGroup();
try {
  var b = new ServerBootstrap();
  b.group(boss, worker).channel(NioServerSocketChannel.class)
   .childHandler(new ChannelInitializer<SocketChannel>() {
     protected void initChannel(SocketChannel ch) {
       ch.pipeline().addLast(new MyHandler());
     }
   });
  b.bind(8080).sync().channel().closeFuture().sync();
} finally { boss.shutdownGracefully(); worker.shutdownGracefully(); }
```