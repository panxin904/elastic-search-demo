---
title: 编码开发
---

# 编码开发

编码是将设计落地为代码的阶段，遵循规范和流程能显著提升代码质量。

## 分支管理

```
main ─────●──────────●──────────●────── 生产分支
           \        /          /
develop ────●──────●──────────●──────── 开发分支
             \    /  \      /
feature-a ────●──●    \    /            功能分支
                       \  /
feature-b ──────────────●──●            功能分支
```

| 分支 | 用途 | 命名 |
|---|---|---|
| main | 生产环境代码 | main |
| develop | 开发环境集成 | develop |
| feature/* | 功能开发 | feature/user-login |
| hotfix/* | 紧急修复 | hotfix/order-crash |
| release/* | 发布分支 | release/v1.2.0 |

## 编码规范

### 分层职责

```java
// Controller: 只做参数校验和结果封装，不写业务逻辑
@RestController
@RequestMapping("/api/users")
public class UserController {
    @Autowired
    private UserService userService;

    @PostMapping
    public Result<UserVO> create(@Valid @RequestBody UserCreateDTO dto) {
        return Result.success(userService.createUser(dto));
    }
}

// Service: 业务逻辑，事务管理
@Service
public class UserServiceImpl implements UserService {
    @Override
    @Transactional(rollbackFor = Exception.class)
    public UserVO createUser(UserCreateDTO dto) {
        // 1. 业务校验
        // 2. 数据转换
        // 3. 调用 Mapper
        // 4. 发送事件/消息
        return userVO;
    }
}

// Mapper: 只做数据访问
@Mapper
public interface UserMapper extends BaseMapper<User> {
    User selectByUsername(@Param("username") String username);
}
```

<div class="kg-note kg-note-tip">
<strong>核心原则</strong>：Controller 不写业务、Service 不操作 Request/Response、Mapper 只做数据操作。
</div>

### 提交规范

```bash
git commit -m "feat: 新增用户注册接口"
git commit -m "fix: 修复订单金额计算精度问题"
git commit -m "refactor: 重构支付模块，提取公共方法"
```

| 前缀 | 含义 |
|---|---|
| feat | 新功能 |
| fix | Bug 修复 |
| refactor | 重构 |
| docs | 文档 |
| test | 测试 |
| chore | 构建/工具 |

### 自测清单

提交代码前确保：
- [ ] 本地启动正常，接口能调通
- [ ] 正常流程走通了
- [ ] 异常情况处理了（空值、边界值）
- [ ] 没有打印敏感信息（密码、token）
- [ ] 没有遗留 TODO / 调试代码
- [ ] 关键逻辑写了单元测试

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="coding" :height="400" />
