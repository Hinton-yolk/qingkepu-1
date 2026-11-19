#!/bin/bash
# 运动测试出片：bash build_motion.sh <工作目录> [scale] [samples]
# 渲 3D 帧 → 叠 2D 层 → 编码 → 动效检查（无声，只验运动）
set -e
here=$(cd "$(dirname "$0")" && pwd); w=$1; scale=${2:-0.6}; spp=${3:-32}
mkdir -p "$w/3d" "$w/comp"
font="$w/NotoSansSC-Bold.otf"
[ -f "$font" ] || python3 -c "
from fontTools.ttLib import TTCollection
TTCollection('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc').fonts[2].save('$font')"
[ -f "$w/3d/f0089.png" ] || blender -b -P "$here/motion.py" -- --outdir "$w/3d" --scale $scale --samples $spp --font "$font" > "$w/blender.log" 2>&1
python3 "$here/motion_overlay.py" "$w/3d" "$w/comp" 30
ffmpeg -nostdin -loglevel error -y -framerate 30 -i "$w/comp/f%04d.png" -c:v libx264 -crf 17 -pix_fmt yuv420p -movflags +faststart "$w/motion_test.mp4"
python3 "$here/../../../../../tools/motion_check.py" "$w/motion_test.mp4" motion_test || true
