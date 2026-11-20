#!/bin/bash
# 整合片出片：合成 → 三个局部转场 → 接触表 → 轨迹图 → 交付目录
set -e
cd "$(dirname "$0")"
python3 post.py int out/frames_int/int out/post_int
D=out/deliver_int; mkdir -p $D
M=out/post_int/EP01_IntegratedAnimation_Test01.mp4; cp $M $D/
cut() { ffmpeg -nostdin -loglevel error -y -ss $2 -to $3 -i $M -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k $D/$1.mp4; }
cut Transition_B_to_A 7.6 11.0
cut Transition_A_to_C 15.2 21.4
cut Transition_C_Reject_Replace 25.4 30.6
python3 - <<'PY'
from PIL import Image, ImageDraw
import glob
fs = sorted(glob.glob('out/post_int/comp_int/*.jpg')); idx = list(range(0, len(fs), 30))
W, H, cols = 216, 384, 9; rows = -(-len(idx) // cols)
S = Image.new('RGB', (W * cols, H * rows), 'white')
for n, i in enumerate(idx):
    im = Image.open(fs[i]).resize((W, H)); ImageDraw.Draw(im).text((5, 5), f'{i / 30:.0f}s', fill=(220, 0, 0)); S.paste(im, ((n % cols) * W, (n // cols) * H))
S.save('out/deliver_int/EP01_IntegratedAnimation_Test01_接触表_每秒.jpg', quality=88)
PY
python3 traj_plot.py int
cp out/post_int/EP01_IntegratedAnimation_Test01_轨迹.* $D/
echo done
