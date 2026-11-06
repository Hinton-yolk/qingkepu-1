#!/bin/bash
# 完整版分段出片，60 fps（磁盘额度有限：每段 20 s 的 PNG 帧渲完立刻编码成 .ts 再删帧），最后拼接＋配乐（-14 LUFS）
#   bash render_full.sh            全部重渲
#   bash render_full.sh mux        只重新拼接和混音
set -e; cd "$(dirname "$0")"
DUR=$(python3 -c "import json;print(json.load(open('代码工程/ep3/desk.json'))['dur'])"); OUT=光互连03_Vox_v2.mp4; FPS=60; CH=20
mkdir -p segs
if [ "$1" != "mux" ]; then
  for A in $(python3 -c "import math;print(' '.join(str(i*$CH) for i in range(math.ceil($DUR/$CH))))"); do
    B=$(python3 -c "print(min($A+$CH,$DUR))"); SEG=segs/seg_$(printf %03d $A).ts
    [ -f $SEG ] && continue
    FILM=ep3 FPS=$FPS node render.mjs $A $B 4 frames_full
    ffmpeg -y -hide_banner -loglevel error -framerate $FPS -start_number $((A*FPS)) -i frames_full/%05d.png -frames:v $(python3 -c "print(round(($B-$A)*$FPS))") \
      -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -f mpegts $SEG
    rm -rf frames_full; echo "segment $A–$B done"
  done
fi
I=$(ffmpeg -hide_banner -nostats -i 配乐/score_ep3.wav -af ebur128 -f null - 2>&1 | grep -A3 Summary | grep ' I:' | awk '{print $2}')
G=$(python3 -c "print(round(-14-($I)+0.7,2))")
ffmpeg -y -hide_banner -loglevel error -i "concat:$(ls segs/seg_*.ts | paste -sd'|')" -i 配乐/score_ep3.wav -map 0:v -map 1:a -c:v copy \
  -af "volume=${G}dB,aresample=192000,alimiter=limit=0.60:level=false:attack=5:release=60,aresample=48000" -c:a aac -b:a 256k -movflags +faststart -t $DUR $OUT
ffmpeg -hide_banner -nostats -i $OUT -af ebur128=peak=true -f null - 2>&1 | grep -A16 Summary | grep -E ' I:|Peak:'
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,pix_fmt -of compact $OUT
