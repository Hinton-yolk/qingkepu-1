#!/bin/bash
# build.sh <版本> <输出目录>：渲画面 + 配乐 + 两遍 loudnorm 到 -14 LUFS + 动效检查
# 例：./build.sh v5 /tmp/out   → /tmp/out/ai-xianka_v5.mp4
set -e
V=$1; OUT=${2:-$(pwd)/out}; NAME=${3:-ai-xianka}
HERE=$(cd "$(dirname "$0")" && pwd); REPO=$(cd "$HERE" && git rev-parse --show-toplevel)
mkdir -p "$OUT"
cd "$HERE"
node render.mjs film "$OUT/${V}_silent.mp4" 30 3 | tail -1
python3 music.py "$OUT/music_${V}.wav" > /dev/null
cd "$OUT"
J=$(ffmpeg -hide_banner -i music_${V}.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p')
P=$(echo "$J" | python3 -c "import json,sys;d=json.load(sys.stdin);print(f\"measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}\")")
ffmpeg -y -loglevel error -i ${V}_silent.mp4 -i music_${V}.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:$P:linear=true,aresample=48000" -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart ${NAME}_${V}.mp4
ffmpeg -hide_banner -i ${NAME}_${V}.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
python3 "$REPO/tools/motion_check.py" "$OUT/${NAME}_${V}.mp4" $V --end=57 | tail -1
