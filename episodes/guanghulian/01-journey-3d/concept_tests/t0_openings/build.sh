#!/usr/bin/env bash
# 渲出 T0 的两个静音版（各 4 秒，540×960，30 fps）。
# 用法：t0_openings/build.sh <工作目录>   （视频不进仓库）
set -euo pipefail
OUT="$1"; HERE="$(cd "$(dirname "$0")" && pwd)"; mkdir -p "$OUT"
for v in A B; do
  name=$([ "$v" = A ] && echo glass_fiber || echo will_it_arrive)
  rm -rf "$OUT/fr_$v"
  node "$HERE/../render.cjs" "$HERE/t0.html" "$OUT/fr_$v" 4 "{\"variant\":\"$v\"}"
  ffmpeg -v error -y -framerate 30 -i "$OUT/fr_$v/f_%05d.png" -vf scale=540:960:flags=lanczos \
    -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -an -movflags +faststart -map_metadata -1 "$OUT/EP01_T0${v}_${name}_v2_silent_540x960_30fps.mp4"
done
ls -la "$OUT"/*.mp4
