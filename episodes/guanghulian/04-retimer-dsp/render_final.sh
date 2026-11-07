#!/bin/bash
# 上下集终版：bash render_final.sh u|d → output/光互连04_小红书_{上,下}集.mp4（60 fps，1080×1920，CRF 16，-14 LUFS）
set -e; cd "$(dirname "$0")"; V=$1; FPS=60; CH=4; NAME=$([ "$V" = u ] && echo 上 || echo 下); OUT=output/光互连04_小红书_${NAME}集.mp4
DUR=$(python3 -c "import json;print(json.load(open('代码工程/ep4/desk_$V.json'))['dur'])"); mkdir -p segs_f$V output
for A in $(python3 -c "import math;print(' '.join(str(i*$CH) for i in range(math.ceil($DUR/$CH))))"); do
  B=$(python3 -c "print(min($A+$CH,$DUR))"); SEG=segs_f$V/seg_$(printf %03d $A).ts; [ -f $SEG ] && continue
  FILM=ep4$V FPS=$FPS node render.mjs $A $B 4 frames_f$V > /dev/null
  ffmpeg -y -hide_banner -loglevel error -framerate $FPS -start_number $((A*FPS)) -i frames_f$V/%05d.png -frames:v $(python3 -c "print(round(($B-$A)*$FPS))") \
    -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -f mpegts $SEG
  rm -rf frames_f$V; echo "$V final seg $A–$B"
done
(cd 配乐 && python3 score_x.py $V > /dev/null && python3 mix_x.py $V > /dev/null && ffmpeg -y -loglevel error -i mix_$V.wav -af acompressor=threshold=-20dB:ratio=3:attack=8:release=150:makeup=1 mix_${V}_c.wav)
I=$(ffmpeg -hide_banner -nostats -i 配乐/mix_${V}_c.wav -af ebur128 -f null - 2>&1 | grep -A3 Summary | grep ' I:' | awk '{print $2}')
G=$(python3 -c "print(round(-14-($I)+1.6,2))")
ffmpeg -y -hide_banner -loglevel error -i "concat:$(ls segs_f$V/seg_*.ts | paste -sd'|')" -i 配乐/mix_${V}_c.wav -map 0:v -map 1:a -c:v copy \
  -af "volume=${G}dB,aresample=192000,alimiter=limit=0.60:level=false:attack=5:release=60,aresample=48000" -c:a aac -b:a 256k -movflags +faststart -t $DUR $OUT
ffmpeg -hide_banner -nostats -i $OUT -af ebur128=peak=true -f null - 2>&1 | grep -A16 Summary | grep -E ' I:|Peak:'
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,pix_fmt,r_frame_rate -of compact $OUT
