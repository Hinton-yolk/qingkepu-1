#!/bin/sh
# 核对用户传回的成片：规格、响度、动效（本系列放宽门槛），并和当前源码重渲的几帧逐像素比较，确认是最新画面。
#   sh tools/verify_upload.sh <成片.mp4>
set -e
F="$1"; HERE=$(cd "$(dirname "$0")/.." && pwd); REPO=$(cd "$HERE/../../.." && pwd)
echo "== 规格"; ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,sample_rate,channels -show_entries format=duration,size -of default=nw=1 "$F"
echo "== 响度（目标 -14 LUFS）"; ffmpeg -v info -i "$F" -map 0:a -af ebur128=peak=true -f null - 2>&1 | grep -A12 "Summary:" | grep -E "I:|Peak:|LRA:" || echo "（没有音轨）"
END=$(node -e "console.log(require('$HERE/timeline.js').END_CARD)")
echo "== 动效（本系列门槛：--max-still=1.2 --max-win=0.45，片尾卡 $END 秒起不计）"; python3 "$REPO/tools/motion_check.py" "$F" ep01 --end="$END" --max-still=1.2 --max-win=0.45 | tail -2
