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