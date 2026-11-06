#!/bin/bash
# 帧序列 + 配乐 → 成片（H.264 yuv420p CRF 16，响度 -14 LUFS）。用法：bash encode.sh [输出文件名]
set -e; cd "$(dirname "$0")"; OUT=${1:-光互连_Vox样片.mp4}; DUR=$(python3 -c "import json;print(json.load(open('代码工程/vox/cues.json'))['dur'])")
I=$(ffmpeg -hide_banner -nostats -i 配乐/score.wav -af ebur128 -f null - 2>&1 | grep -A3 Summary | grep ' I:' | awk '{print $2}')
G=$(python3 -c "print(round(-14-($I)+1.2,2))")
ffmpeg -y -hide_banner -loglevel error -framerate 30 -i frames/%05d.png -i 配乐/score.wav \
  -af "volume=${G}dB,aresample=192000,alimiter=limit=0.60:level=false:attack=5:release=60,aresample=48000" \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 256k -t $DUR "$OUT"
ffmpeg -hide_banner -nostats -i "$OUT" -af ebur128=peak=true -f null - 2>&1 | grep -A16 Summary | grep -E ' I:|Peak:'
