#!/bin/bash
# 上下集草稿：bash render_part.sh u|d → review/光互连03_小红书_{上,下}集_草稿.mp4（30 fps，540×960）
set -e; cd "$(dirname "$0")"; V=$1; FPS=30; CH=20; NAME=$([ "$V" = u ] && echo 上 || echo 下); OUT=review/光互连02_抖音_${NAME}集_草稿.mp4
DUR=$(python3 -c "import json;print(json.load(open('代码工程/ep2x/desk_$V.json'))['dur'])"); mkdir -p segs_$V review
for A in $(python3 -c "import math;print(' '.join(str(i*$CH) for i in range(math.ceil($DUR/$CH))))"); do
  B=$(python3 -c "print(min($A+$CH,$DUR))"); SEG=segs_$V/seg_$(printf %03d $A).ts; [ -f $SEG ] && continue
  FILM=ep2$V FPS=$FPS node render.mjs $A $B 4 frames_$V > /dev/null
  ffmpeg -y -hide_banner -loglevel error -framerate $FPS -start_number $((A*FPS)) -i frames_$V/%05d.png -frames:v $(python3 -c "print(round(($B-$A)*$FPS))") \
    -vf scale=540:960:flags=lanczos -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p -f mpegts $SEG
  rm -rf frames_$V; echo "$V seg $A–$B"
done
(cd 配乐 && python3 score_x.py $V > /dev/null && python3 mix_x.py $V > /dev/null && ffmpeg -y -loglevel error -i mix_$V.wav -af acompressor=threshold=-20dB:ratio=3:attack=8:release=150:makeup=1 mix_${V}_c.wav)
ffmpeg -y -hide_banner -loglevel error -i "concat:$(ls segs_$V/seg_*.ts | paste -sd'|')" -i 配乐/mix_${V}_c.wav -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 192k -movflags +faststart -t $DUR $OUT
echo "DONE $OUT"
