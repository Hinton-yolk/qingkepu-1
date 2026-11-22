#!/bin/sh
# Blender 混合成片：three.js 整片 + 几段 Blender（film/blender/out/hyb/<帧号>.png，三维画面），
# Blender 段在页面里套同一套调色、标注和字幕（index.html ?bg=hyb），覆盖进 three.js 的帧，再和音轨一起编码。
#   sh tools/hybrid.sh <three.js 整片.mp4> <音轨.wav> <输出.mp4> <段 1 首帧:尾帧> [<段 2 首帧:尾帧> …]
#   例：sh tools/hybrid.sh film/out/ai01-strawberry-v4-picture.mp4 music/out/mix_v4.wav film/out/ai01-strawberry.mp4 0:239 414:497 2100:2279 2457:2531
# （在集目录 episodes/ai-linghun/01-strawberry 下运行；需要 NODE_PATH 指向全局 node_modules 里的 playwright）
set -e
SRC="$1"; WAV="$2"; OUT="$3"; shift 3
FR=film/out/frames_hyb; rm -rf "$FR" film/out/hyb_comp; mkdir -p "$FR"
ffmpeg -v error -y -i "$SRC" -start_number 0 "$FR/%05d.png"
TOTAL=$(ls "$FR" | wc -l)
for seg in "$@"; do
  a=${seg%:*}; b=${seg#*:}
  (cd film && node render.mjs --bg=hyb --frames=out/hyb_comp --start=$(node -e "console.log(($a - 0.5) / 30)") --end=$(node -e "console.log(($b + 0.6) / 30)") --noencode --resume --workers=4 | tail -1)
  n=$(ls film/out/hyb_comp | wc -l); echo "segment $a–$b composited ($n frames so far)"
done
cp film/out/hyb_comp/*.png "$FR"/
DUR=$(node -e "console.log($TOTAL / 30)")   # pad the audio to the last frame (-shortest dropped one frame before)
ffmpeg -v error -y -framerate 30 -start_number 0 -i "$FR/%05d.png" -i "$WAV" -map 0:v -map 1:a -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -profile:v high -r 30 \
  -af apad -t "$DUR" -c:a aac -aac_coder fast -b:a 256k -ar 48000 -movflags +faststart "$OUT"
echo "$OUT: $TOTAL frames in, $(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$OUT") out"
