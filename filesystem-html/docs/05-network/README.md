# 05 · 网络文件协议

<span class="kg-badge kg-badge-network">网络</span>

跨机器访问文件的标准协议。

## 章节目录

| 节点 | 一句话 |
|------|--------|
| [NFS Unix 经典](/05-network/nfs) | 网络文件系统的事实标准 |
| [SMB / CIFS Windows](/05-network/smb) | Windows 共享 / Samba |
| [WebDAV HTTP 文件](/05-network/webdav) | 基于 HTTP 的文件协议 |
| [FTP / SFTP / SCP](/05-network/ftp-sftp) | 老牌文件传输三剑客 |
| [rsync 增量同步](/05-network/rsync) | 增量 + delta-transfer |

## 协议速查

| 协议 | 端口 | 加密 | 典型场景 |
|------|------|------|---------|
| NFS | 2049 | v4+ 支持 Kerberos | Linux 共享 |
| SMB | 445 | v3+ | Windows / macOS |
| WebDAV | 80/443 | HTTPS | 远程协作 |
| FTP | 21 | 无 / FTPS | 老旧系统 |
| SFTP | 22 | SSH | 安全传输 |
| rsync | 873 / 22 | SSH | 备份同步 |