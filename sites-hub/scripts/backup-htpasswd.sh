#!/usr/bin/env bash
# sites-hub/scripts/backup-htpasswd.sh
# 异地备份 sites-hub 的 htpasswd 文件（basic auth 凭据）。
#
# 用法：
#   1) 第一次跑：交互式输入目标 SSH 主机（默认 backup@backup.example.com:~/sites-hub-backups/）
#      htpasswd 会用 GPG 加密后 scp 上去，文件名带日期。
#   2) cron 跑（建议 cron.daily）：读取 /etc/sites-hub-backup.conf 里的 SSH 配置。
#
# 配置 /etc/sites-hub-backup.conf（chmod 600，仅 root 可读）：
#   HTPASSWD_SRC="/etc/nginx/.sites-hub.htpasswd"
#   BACKUP_USER="backup"
#   BACKUP_HOST="backup.example.com"
#   BACKUP_DIR="~/sites-hub-backups"
#   GPG_RECIPIENT="ops@example.com"   # 可选；空 = 不加密（不推荐）
#
# 安全：
#   - 默认 GPG 公钥加密；无 GPG 则明文（部署前必配）
#   - 备份保留 90 天，过期自动清理
#   - 备份结果写入 syslog，failure 触发 systemd unit alert

set -euo pipefail
PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
LOG_TAG="sites-hub-backup"

CONF="${HTPASSWD_BACKUP_CONF:-/etc/sites-hub-backup.conf}"
[[ -f "$CONF" ]] && source "$CONF"

HTPASSWD_SRC="${HTPASSWD_SRC:-/etc/nginx/.sites-hub.htpasswd}"
BACKUP_USER="${BACKUP_USER:-backup}"
BACKUP_HOST="${BACKUP_HOST:-}"
BACKUP_DIR="${BACKUP_DIR:-~/sites-hub-backups}"
GPG_RECIPIENT="${GPG_RECIPIENT:-}"
RETAIN_DAYS="${RETAIN_DAYS:-90}"

log() { logger -t "$LOG_TAG" -- "$*"; echo "[$(date -Iseconds)] $*" >&2; }

[[ -r "$HTPASSWD_SRC" ]] || { log "FATAL: cannot read $HTPASSWD_SRC"; exit 1; }
[[ -n "$BACKUP_HOST"  ]] || { log "FATAL: BACKUP_HOST not set (configure $CONF)"; exit 1; }

stamp="$(date -u +%Y%m%dT%H%M%SZ)"
hostname_short="$(hostname -s 2>/dev/null || hostname)"
base_name="htpasswd-${hostname_short}-${stamp}"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

src_copy="$tmpdir/$base_name"
cp -p "$HTPASSWD_SRC" "$src_copy"

# SHA256 用于完整性校验
( cd "$tmpdir" && sha256sum "$base_name" > "${base_name}.sha256" )

# 加密（如果有 GPG_RECIPIENT）
if [[ -n "$GPG_RECIPIENT" ]]; then
  gpg --batch --yes --trust-model always --recipient "$GPG_RECIPIENT" \
      --output "${src_copy}.gpg" --encrypt "$src_copy"
  rm -f "$src_copy"
  payload="${src_copy}.gpg"
else
  log "WARN: GPG_RECIPIENT empty, backup is UNENCRYPTED"
  payload="$src_copy"
fi

# scp 上传
ssh_dest="${BACKUP_USER}@${BACKUP_HOST}:${BACKUP_DIR}/"
log "uploading $payload -> $ssh_dest"
scp -q "$payload" "${tmpdir}/${base_name}.sha256" "$ssh_dest" || {
  log "FATAL: scp failed (host=$BACKUP_HOST)"; exit 2;
}

# 远程清理过期备份
ssh "${BACKUP_USER}@${BACKUP_HOST}" "find ${BACKUP_DIR} -type f -mtime +${RETAIN_DAYS} -name 'htpasswd-*' -delete" \
  || log "WARN: remote retention cleanup failed (non-fatal)"

log "OK: backup complete (${base_name}, retain=${RETAIN_DAYS}d)"
