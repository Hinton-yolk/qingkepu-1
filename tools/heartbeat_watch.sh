#!/usr/bin/env bash
# 心跳监视：盯着若干文件或目录，超过一定时间没有任何变化就退出并说明是谁停了。
# 用途：派出去的角色或后台任务可能中途停下而不发通知。把这个脚本放在后台跑，它一退出主 agent 就会被叫醒。
# 用法：tools/heartbeat_watch.sh <名字> <停滞秒数> <路径> [路径…] [-- <进程关键字>]
#   例：tools/heartbeat_watch.sh "S02/S03 场景" 480 blender/s02_gpu_package.py /tmp/x/v1_s0203 -- "runpod_render.py run"
#   · 路径可以是文件或目录（目录看里面最新的文件）。
#   · 给了「进程关键字」时：那个进程结束就正常退出（退出码 0）；没给就一直盯到停滞为止。
#   · 停滞时退出码 3，并打印最后一次变化的时间和文件。
set -u
name="$1"; stale="$2"; shift 2
paths=(); pat=""
while [ $# -gt 0 ]; do
  if [ "$1" = "--" ]; then shift; pat="${1:-}"; break; fi
  paths+=("$1"); shift
done
newest() {            # 输出：最新修改时间（秒） 文件名
  find "${paths[@]}" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1
}
echo "开始监视「$name」：$(date -u +%H:%M:%S) UTC，停滞门槛 ${stale} 秒"
while true; do
  sleep 30
  if [ -n "$pat" ] && ! pgrep -f "$pat" >/dev/null; then
    echo "「$name」的进程已结束：$(date -u +%H:%M:%S) UTC"; exit 0
  fi
  line="$(newest)"; now=$(date +%s)
  if [ -z "$line" ]; then last=0; file="（还没有任何文件）"; else last=${line%%.*}; file="${line#* }"; fi
  age=$(( now - last ))
  if [ "$last" -ne 0 ] && [ "$age" -gt "$stale" ]; then
    echo "停滞：「$name」已经 $(( age / 60 )) 分 $(( age % 60 )) 秒没有任何变化。"
    echo "最后一次变化：$(date -u -d @"$last" +%H:%M:%S) UTC，文件 $file"
    exit 3
  fi
done
