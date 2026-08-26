---
title: xattr 扩展属性
---

# xattr — 扩展属性，给文件打 metadata

> <span class="kg-badge kg-badge--security">安全权限</span>
> user / trusted / system / security · 实战标签

xattr（Extended Attributes）是文件的**额外元数据**，以 `key=value` 形式存在。

```
POSIX 权限 + 时间戳 + 大小  =  inode 标准属性
xattr                  =  inode 扩展属性
```

## 1. xattr 命名空间

| 命名空间 | 含义 | 谁可读写 |
|----------|------|---------|
| `user.*` | 用户自定义 | 文件 owner 或特权进程 |
| `trusted.*` | 特权进程 | root |
| `system.*` | 内核使用 | 内核 |
| `security.*` | 安全模块（SELinux） | SELinux |

## 2. 常用命令

```bash
# 看
getfattr -d file
getfattr -n user.author file

# 设
setfattr -n user.author -v "Alice" file
setfattr -n user.tags -v "important" file

# 删
setfattr -x user.author file

# 全部
getfattr -m '' -d file
```

## 3. xattr 的限制

```bash
# ext4 / xfs 默认 64 KB
# 一个 xattr 名最长 255 bytes
# 值大小不限
```

## 4. 实战：手动给文件打 tag

```bash
# 给脚本加版本标签
setfattr -n user.version -v "v2.1" /usr/local/bin/myscript

# 给 doc 加作者
setfattr -n user.author -v "Alice" /report.pdf

# 用 getfattr 看
getfattr -d /report.pdf
```

## 5. 系统常见 xattr

### 5.1 SELinux

```bash
getfattr -n security.selinux /usr/sbin/nginx
# security.selinux="system_u:object_r:httpd_exec_t:s0"
```

### 5.2 capabilities

```bash
getfattr -n security.capability /usr/bin/ping
# security.capability=0s......Y2WAQ==
```

### 5.3 systemd

```bash
getfattr -d /usr/bin/somebinary
# systemd 存 unit 文件路径等
```

### 5.4 AFS / CIFS

AFS / CIFS 在 xattr 里存 ACL。

### 5.5 AppArmor

AppArmor 当前不在 xattr 存标签（独立机制）。

## 6. 编程 API

```c
#include <sys/xattr.h>

// 读
ssize_t len = listxattr("/file", buf, sizeof(buf));
char value[256];
ssize_t vlen = getxattr("/file", "user.author", value, sizeof(value));

// 写
setxattr("/file", "user.author", "Alice", 5, 0);

// 删
removexattr("/file", "user.author");
```

## 7. 备份 xattr

```bash
# rsync 保留 xattr
rsync -aX /src/ /dst/

# tar 保留
tar --xattrs -czf backup.tar.gz /home
tar --xattrs -xzf backup.tar.gz -C /restore

# cp 保留
cp --preserve=all /src/file /dst/
```

## 8. 实战：基于 xattr 的访问控制

```bash
# 写一个简单的"安全标签"脚本
SECRET_FILE=/tmp/secret.txt

# 写入内容
echo "Hello" > $SECRET_FILE

# 加 xattr 标记
setfattr -n user.classification -v "confidential" $SECRET_FILE

# 写 wrapper 检查
check_secret() {
    local file="$1"
    local cls=$(getfattr -n user.classification --absolute-names "$file" 2>/dev/null | grep -oP '="\K[^"]+')
    if [ "$cls" = "confidential" ]; then
        echo "BLOCKED: This file is confidential"
        return 1
    fi
    cat "$file"
}
```

## 9. 实战：容器镜像层元数据

Docker 用 xattr 存镜像层 ID：

```bash
getfattr -n user.tar.something /var/lib/docker/overlay2/...
```

容器镜像 layer 关系依赖 xattr。

## 10. 大小优化

```bash
# ext4 单文件 xattr 上限（默认 64KB）
tune2fs -l /dev/sda1 | grep "Inode size"
# 一个 inode 默认 256 bytes，xattr 占用 inode 之后

# xattr 太多会撑爆 inode 空间
# 解决方案：少打 xattr
```

## 11. 工具集成

| 工具 | 是否支持 |
|------|---------|
| lsattr / chattr | 看 / 改 FS-level flag |
| `cp --preserve=xattr` | ✅ |
| `cp --preserve=all` | ✅ |
| `rsync -X` | ✅ |
| `tar --xattrs` | ✅ |
| `zip` | ❌ |
| `git` | ❌ |

## 12. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| xattr = key=value | "xattr=属性" |
| user.* 普通用户可写 | "user=普通" |
| trusted.* 只 root | "trusted=root" |
| 备份用 --xattrs | "备份=带属性" |
| SELinux / capabilities 都在这 | "SELinux=xattr" |

## 参考

- getfattr(1) / setfattr(1) 手册
- Linux xattr 内核文档
- POSIX ACL 与 xattr 关系


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
