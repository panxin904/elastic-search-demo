# 10 · 安全与权限

<span class="kg-badge kg-badge-security">安全</span>

文件系统层面的访问控制、加密、审计。

## 章节目录

| 节点 | 一句话 |
|------|--------|
| [POSIX 权限位](/10-security/posix-perm) | rwx 三组九位 |
| [ACL 访问控制列表](/10-security/acl) | 细粒度权限 |
| [xattr 扩展属性](/10-security/xattr) | SELinux / capabilities 依赖 |
| [加密静态 / 传输](/10-security/encryption) | LUKS / TLS |
| [auditd 审计](/10-security/auditd) | 跟踪谁动了文件 |

## 纵深防御层次

```
应用层（业务权限）
  ↓
文件系统层（POSIX / ACL）
  ↓
内核层（SELinux / AppArmor）
  ↓
存储层（加密静态 LUKS）
  ↓
网络层（TLS / IPsec）
```

任何一层失守，下一层仍能阻止攻击。
## 🎯 本章学习路径

1. **了解场景**：每个协议都有它的设计目标（NFS = Unix 共享、SMB = Windows、FTP = 老系统）
2. **掌握配置**：端口 / 加密方式 / 性能调优
3. **安全加固**：防火墙规则 / TLS 配置 / 用户认证
4. **监控告警**：连接数 / 延迟 / 错误率

详细各协议配置见子节点文章。
