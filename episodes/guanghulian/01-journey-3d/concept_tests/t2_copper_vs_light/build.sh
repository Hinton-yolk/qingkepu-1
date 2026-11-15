#!/usr/bin/env bash
# 渲出 T2 的两个文件：静音版（没有字幕）和试听版（临时声音 + 字幕代替口播）。
# 用法：t2_copper_vs_light/build.sh <工作目录>   （视频不进仓库）
set -euo pipefail
OUT="$1"; HERE="$(cd "$(dirname "$0")" && pwd)"; mkdir -p "$OUT"
for mode in silent sound; do
  caps=$([ "$mode" = sound ] && echo true || echo false)
  rm -rf "$OUT/fr_$mode"
  node "$HERE/../render.cjs" "$HERE/t2.html" "$OUT/fr_$mode" 9 "{\"captions\":$caps}"
  f="$OUT/EP01_T2_copper_vs_light_v2_${mode}_540x960_30fps.mp4"
  if [ "$mode" = sound ]; then
    python3 "$HERE/audio_t2.py" "$OUT/t2.wav"
    ffmpeg -v error -y -framerate 30 -i "$OUT/fr_$mode/f_%05d.png" -i "$OUT/t2.wav" -vf scale=540:960:flags=lanczos \
      -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -c:a aac -b:a 128k -shortest -movflags +faststart -map_metadata -1 "$f"
  else
    ffmpeg -v error -y -framerate 30 -i "$OUT/fr_$mode/f_%05d.png" -vf scale=540:960:flags=lanczos \
      -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -an -movflags +faststart -map_metadata -1 "$f"
  fi
done
ls -la "$OUT"/*.mp4
