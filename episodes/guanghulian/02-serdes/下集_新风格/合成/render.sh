#!/bin/bash
# 渲整片：4 个进程分段出 PNG，再和混音合成 mp4。用法：./render.sh <scale> <名字>   例：./render.sh 0.5 draft ；./render.sh 1 final
set -e; cd "$(dirname "$0")"; SC=${1:-0.5}; NAME=${2:-draft}; D=out/frames_$NAME; rm -rf $D; mkdir -p $D
python3 comp.py info out/info.json > /dev/null
N=$(python3 -c "import json;print(int(round(json.load(open('out/info.json'))['end']*30)))"); P=4; STEP=$(( (N + P - 1) / P ))
for i in $(seq 0 $((P-1))); do python3 comp.py frames $D scale=$SC i0=$((i*STEP)) i1=$(((i+1)*STEP)) > out/render_$i.log 2>&1 & done; wait
ls $D | wc -l
python3 score.py && python3 mix.py
ffmpeg -v error -y -framerate 30 -i $D/%05d.png -i out/mix.wav -c:v libx264 -crf ${CRF:-16} -preset slow -pix_fmt yuv420p -c:a aac -b:a 256k -shortest -movflags +faststart out/ep02x_$NAME.mp4
echo done out/ep02x_$NAME.mp4
