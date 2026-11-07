#!/bin/bash
# 小红书改版草稿（内容关卡 2）：30 fps 渲 1080×1920、缩成 540×960 编码，分段渲完即编码删帧。bash render_draft_x.sh
set -e; cd "$(dirname "$0")"; FPS=30; CH=20; OUT=review/光互连03_小红书改版_草稿.mp4
DUR=$(python3 -c "import json;print(json.load(open('代码工程/ep3/desk_x.json'))['dur'])"); mkdir -p segs_x review
for A in $(python3 -c "import math;print(' '.join(str(i*$CH) for i in range(math.ceil($DUR/$CH))))"); do
  B=$(python3 -c "print(min($A+$CH,$DUR))"); SEG=segs_x/seg_$(printf %03d $A).ts; [ -f $SEG ] && continue
  FILM=ep3x FPS=$FPS node render.mjs $A $B 4 frames_x > /dev/null
  ffmpeg -y -hide_banner -loglevel error -framerate $FPS -start_number $((A*FPS)) -i frames_x/%05d.png -frames:v $(python3 -c "print(round(($B-$A)*$FPS))") \
    -vf scale=540:960:flags=lanczos -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p -f mpegts $SEG
  rm -rf frames_x; echo "seg $A–$B"
done
(cd 配乐 && python3 score_x.py > /dev/null && python3 mix_x.py > /dev/null && ffmpeg -y -loglevel error -i mix_x.wav -af acompressor=threshold=-20dB:ratio=3:attack=8:release=150:makeup=1 mix_x_c.wav)
ffmpeg -y -hide_banner -loglevel error -i "concat:$(ls segs_x/seg_*.ts | paste -sd'|')" -i 配乐/mix_x_c.wav -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 192k -movflags +faststart -t $DUR $OUT
ffprobe -v error -show_entries format=duration -of csv=p=0 $OUT
