---
title: NestJS
---

# NestJS

## 🎯 NestJS 是什么

**类 Spring / Angular 风格的 Node 框架**：DI + 模块化 + 装饰器 + 强类型。适合大型工程。

```
NestJS = Express / Fastify + TypeScript + DI + AOP + OpenAPI
```

```bash
npm i -g @nestjs/cli
nest new my-app
cd my-app
npm run start:dev
```

## 🧱 核心概念

| 概念 | 作用 |
|------|------|
| Module | 一组 Provider / Controller 的容器 |
| Controller | 路由 + 请求处理 |
| Provider（Service） | 业务逻辑、可注入 |
| Pipe | 转换 / 校验请求 |
| Guard | 鉴权 |
| Interceptor | AOP 切面 |
| Filter | 异常处理 |
| Middleware | Express 风格的中间件 |

## 🔄 Controller

```ts
@Controller('users')
export class UsersController {
  constructor(private readonly users: UsersService) {}

  @Get()
  list() { return this.users.findAll() }

  @Post()
  @UsePipes(new ValidationPipe())
  create(@Body() input: CreateUserDto) {
    return this.users.create(input)
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.users.findOne(id)
  }
}
```

## 📦 DTO + Validation

```ts
// create-user.dto.ts
import { IsString, IsEmail, MinLength } from 'class-validator'

export class CreateUserDto {
  @IsString() name: string
  @IsEmail() email: string
  @MinLength(8) password: string
}
```

需要全局 `ValidationPipe`：

```ts
app.useGlobalPipes(new ValidationPipe({ whitelist: true }))
```

## 🪛 Service（Provider）

```ts
@Injectable()
export class UsersService {
  constructor(private readonly db: PrismaService) {}

  findAll() { return this.db.user.findMany() }
  findOne(id: string) { return this.db.user.findUnique({ where: { id } }) }
  create(input: CreateUserDto) {
    return this.db.user.create({ data: input })
  }
}
```

## 🛡️ Guard（鉴权）

```ts
@Injectable()
export class AuthGuard implements CanActivate {
  canActivate(ctx: ExecutionContext): boolean {
    const req = ctx.switchToHttp().getRequest()
    return req.headers.authorization === 'Bearer xxx'
  }
}

@UseGuards(AuthGuard)
@Controller('admin')
export class AdminController {}
```

## 🔌 Module 组织

```ts
@Module({
  imports: [PrismaModule, AuthModule],
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService]
})
export class UsersModule {}
```

主模块：

```ts
@Module({ imports: [UsersModule, OrdersModule] })
export class AppModule {}
```

## 🗺 配置 / 环境变量

```ts
import { ConfigModule } from '@nestjs/config'

@Module({
  imports: [ConfigModule.forRoot({ isGlobal: true })]
})
export class AppModule {}

// 注入
constructor(@Inject('DATABASE_URL') private url: string) {}
```

## 🛠 Microservices

NestJS 不只 Web，也做 microservice：

- TCP / Redis / NATS / Kafka / gRPC transport
- Server-sent events / WebSocket gateway

## 🆚 NestJS vs Express vs Fastify

| | NestJS | Express | Fastify |
|--|--------|---------|---------|
| 心智 | DI / Module | callback | plugin |
| TS | 一等 | 适配 | 一等 |
| 装饰器 | 多 | 少 | 少 |
| 文档 | 极好 | 一般 | 好 |
| 启动 | 慢 | 极快 | 快 |
| 大型项目 | ✅ | ⚠ | ⚠ |

## 🎯 适合场景

- 中大型团队（结构清晰）
- 需要 OpenAPI 文档
- 需要 GraphQL / Microservices
- TS 重度使用

## 🔗 下一步

- [Fastify / Hono](/11-node/fastify)
- [Express / Koa](/11-node/express)
- [Serverless](/11-node/serverless)
