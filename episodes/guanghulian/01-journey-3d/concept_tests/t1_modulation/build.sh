#!/usr/bin/env bash
# 渲出 T1 的四个文件：A / B 各一个静音版（没有字幕）和一个试听版（临时声音 + 字幕代替口播）。
# 用法：t1_modulation/build.sh <工作目录>   （在 concept_tests/ 里运行；视频不进仓库）
set -euo pipefail
OUT="$1"; HERE="$(cd "$(dirname "$0")" && pwd)"; mkdir -p "$OUT"
for v in A B; do
  name=$([ "$v" = A ] && echo intuitive || echo step)
  for mode in silent sound; do
    caps=$([ "$mode" = sound ] && echo true || echo false)
    rm -rf "$OUT/fr_${v}_$mode"
    node "$HERE/../render.cjs" "$HERE/t1.html" "$OUT/fr_${v}_$mode" 8 "{\"variant\":\"$v\",\"captions\":$caps}"
    f="$OUT/EP01_T1${v}_${name}_v1_${mode}_540x960_30fps.mp4"
    if [ "$mode" = sound ]; then
      python3 "$HERE/audio_t1.py" "$v" "$OUT/t1_$v.wav"
      ffmpeg -v error -y -framerate 30 -i "$OUT/fr_${v}_$mode/f_%05d.png" -i "$OUT/t1_$v.wav" -vf scale=540:960:flags=lanczos \
        -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -c:a aac -b:a 128k -shortest -movflags +faststart -map_metadata -1 "$f"
    else
      ffmpeg -v error -y -framerate 30 -i "$OUT/fr_${v}_$mode/f_%05d.png" -vf scale=540:960:flags=lanczos \
        -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -an -movflags +faststart -map_metadata -1 "$f"
    fi
  done
done
ls -la "$OUT"/*.mp4
