#!/bin/bash
# V02 本机 CPU 渲染（只渲改动的段：第一幕 0–8.6 秒，第五、六幕 39.4 秒以后；场景时间）。可断点续渲。
cd "$(dirname "$0")"
F=../style3d/out/motion_v2/NotoSansSC-Bold.otf; O=out/frames_v02/new; mkdir -p $O
export KEPU_SKIP_DONE=1
blender -b -P shot_v02.py -- --outdir $O --scale 0.5 --samples 24 --font $F --f0 0 --f1 260 > out/frames_v02/r1.log 2>&1
blender -b -P shot_v02.py -- --outdir $O --scale 0.5 --samples 24 --font $F --f0 1182 --f1 2160 > out/frames_v02/r2.log 2>&1
echo finished > out/frames_v02/DONE
