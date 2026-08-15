# sites-hub/scripts/sites.sh
# Scholar's Atlas 子站清单（**唯一真相源**）
#
# 规则：
#  1. 顺序 = 部署顺序；新增站点请追加在末尾。
#  2. SITES 元素 = URL 路径段（如 /es/、/bigdata/），不是项目目录名。
#  3. 项目目录名与 URL 不同的，在 PROJECT_DIR_MAP 字符串里声明（分号分隔）。
#  4. 任何脚本（build-release.sh / deploy-vps.sh / start-hub.py / start.sh / start-all.sh）
#     与 conf/nginx.conf 都从这里读，禁止再硬编码子站列表。
#  5. 校验：bash scripts/check-sites.sh  保证 卡片数 == nginx location 数 == SITES 数。
#
# 兼容性：
#  - macOS 系统 bash 3.2 / zsh 5 都能跑（不依赖 declare -A、mapfile、IFS word splitting）。

# 子站 URL 路径段
SITES=(
  es mysql redis cloud python kafka java tools frontend linux
  cloud-native ai bigdata network video filesystem java-language
  architecture system-design postgresql observability security
  devops rust go clickhouse design-pattern chaos
)

# 项目目录覆盖映射：site:project_dir;site:project_dir;...
PROJECT_DIR_MAP="cloud:springcloud-html;java:java-web-manual"

# site_to_project <site> -> project dir name
# 不依赖 IFS word splitting，bash / zsh / 严格模式都安全
site_to_project() {
  local s="$1"
  local map="$PROJECT_DIR_MAP"
  local entry key val rest
  # 循环：每次取第一个分号前的 entry，剩下的保存为 rest
  while [[ "$map" == *";"* ]]; do
    entry="${map%%;*}"   # 第一个分号前
    rest="${map#*;}"     # 第一个分号后
    map="$rest"
    [[ -z "$entry" ]] && continue
    key="${entry%%:*}"
    val="${entry#*:}"
    if [[ "$key" == "$s" ]]; then
      printf '%s\n' "$val"
      return 0
    fi
  done
  # 处理最后一段（无分号结尾）
  if [[ -n "$map" ]]; then
    key="${map%%:*}"
    val="${map#*:}"
    if [[ "$key" == "$s" ]]; then
      printf '%s\n' "$val"
      return 0
    fi
  fi
  printf '%s\n' "${s}-html"
}

# project_to_site <project> -> site name
project_to_site() {
  local p="$1"
  local s
  for s in "${SITES[@]}"; do
    if [[ "$(site_to_project "$s")" == "$p" ]]; then
      printf '%s\n' "$s"
      return 0
    fi
  done
  return 1
}

export SITES PROJECT_DIR_MAP
