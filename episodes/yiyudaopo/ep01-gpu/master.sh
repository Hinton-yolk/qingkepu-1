#!/usr/bin/env bash
# 出成片：Remotion 1080×1920 → 响度两遍归一到 -14 LUFS（真峰值 -1.5 dBTP）→ remotion/out/EP01_Pilot_v02.mp4
# 用法：bash master.sh            （先跑过 narration/tts.py、audio/music.py、blender/encode_plates.py）
set -euo pipefail
cd "$(dirname "$0")/remotion"
npx tsc --noEmit
npx remotion render src/index.ts EP01Pilot out/EP01_Pilot_v02_raw.mp4 --crf=17 --jpeg-quality=92 --concurrency=4 --gl=swangle --log=error
J=$(ffmpeg -hide_banner -nostats -i out/EP01_Pilot_v02_raw.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$J" | python3 -c "import sys,json;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -loglevel error -i out/EP01_Pilot_v02_raw.mp4 -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" \
  -c:a aac -b:a 192k -movflags +faststart out/EP01_Pilot_v02.mp4
ffmpeg -hide_banner -nostats -i out/EP01_Pilot_v02.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of compact out/EP01_Pilot_v02.mp4
sha256sum out/EP01_Pilot_v02.mp4
