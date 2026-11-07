#!/bin/bash
# 纯动画版 v2 草稿：bash render_nv2.sh 724 → review/s1m_724.mp4（30 fps，540×960）
set -e; cd "$(dirname "$0")"; N=s1m_$1; FPS=30; CH=16
DUR=$(python3 -c "import json;print(json.load(open('代码工程/split/$N.json'))['dur'])"); mkdir -p segs_$N
for A in $(python3 -c "import math;print(' '.join(str(i*$CH) for i in range(math.ceil($DUR/$CH))))"); do
  B=$(python3 -c "print(min($A+$CH,$DUR))"); SEG=segs_$N/seg_$(printf %03d $A).ts; [ -f $SEG ] && continue
  FILM=$N FPS=$FPS node render.mjs $A $B 4 frames_$N > /dev/null
  ffmpeg -y -hide_banner -loglevel error -framerate $FPS -start_number $((A*FPS)) -i frames_$N/%05d.png -frames:v $(python3 -c "print(round(($B-$A)*$FPS))") \
    -vf scale=540:960:flags=lanczos -c:v libx264 -preset medium -crf 22 -pix_fmt yuv420p -f mpegts $SEG
  rm -rf frames_$N
done
python3 tools/mix_nv2.py $N
ffmpeg -y -hide_banner -loglevel error -i "concat:$(ls segs_$N/seg_*.ts | paste -sd'|')" -i audio/${N}_mix.wav -map 0:v -map 1:a -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 192k -movflags +faststart -t $DUR review/$N.mp4
echo "$N done"
