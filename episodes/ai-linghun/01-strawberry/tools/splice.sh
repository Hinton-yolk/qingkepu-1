#!/bin/sh
# 把重渲的两段帧拼回成片：开头 [0, A) 和片尾 [B, 结束) 用新帧，中间用原成片；音轨原样拷贝（时间轴没动）。
#   sh tools/splice.sh <原成片.mp4> <开头帧目录> <A 帧数> <片尾帧目录> <B 起始帧号> <输出.mp4>
#   例：sh tools/splice.sh film/out/ai01-strawberry-v3.mp4 film/out/patch_a 297 film/out/patch_b 2880 film/out/ai01-strawberry.mp4
set -e
SRC="$1"; PA="$2"; NA="$3"; PB="$4"; SB="$5"; OUT="$6"
TOTAL=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$SRC")
NB=$(ls "$PB"/*.png | wc -l); [ $((SB + NB)) -eq "$TOTAL" ] || { echo "片尾帧数对不上：$SB + $NB != $TOTAL"; exit 1; }
ffmpeg -v error -y -i "$SRC" -framerate 30 -start_number 0 -i "$PA/%05d.png" -framerate 30 -start_number "$SB" -i "$PB/%05d.png" \
  -filter_complex "[1:v]format=yuv420p,setsar=1[a];[0:v]trim=start_frame=$NA:end_frame=$SB,setpts=PTS-STARTPTS,format=yuv420p,setsar=1[m];[2:v]format=yuv420p,setsar=1[b];[a][m][b]concat=n=3:v=1:a=0[v]" \
  -map "[v]" -map 0:a -c:v libx264 -preset slow -crf 16 -profile:v high -r 30 -movflags +faststart -c:a copy "$OUT"
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -show_entries format=duration -of csv=p=0 "$OUT"
