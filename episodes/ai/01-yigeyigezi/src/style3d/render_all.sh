#!/bin/bash
# 出三张样张：bash render_all.sh <输出目录> [scale] [samples]
set -e
here=$(cd "$(dirname "$0")" && pwd); out=$1; scale=${2:-1.0}; spp=${3:-64}
mkdir -p "$out"
font="$out/NotoSansSC-Bold.otf"
[ -f "$font" ] || python3 -c "
from fontTools.ttLib import TTCollection
TTCollection('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc').fonts[2].save('$font')"
python3 "$here/overlay.py" ui "$out/ui.png"
for k in 1 2 3; do
  blender -b -P "$here/scene.py" -- --shot $k --out "$out/3d_$k.png" --scale $scale --samples $spp --font "$font" --ui "$out/ui.png" > "$out/log_$k.txt" 2>&1
  python3 "$here/overlay.py" comp "$out/3d_$k.png" "$out/shot$k.png" $k
done
