#!/bin/bash
# Test02 出片：合成 → 三个局部镜头 → 每秒接触表 → 交付目录
set -e
cd "$(dirname "$0")"
python3 post.py int2 out/frames_t2/int2 out/post_t2
D=out/deliver_t2; mkdir -p $D
M=out/post_t2/EP01_IntegratedAnimation_Test02.mp4; cp $M $D/
cut() { ffmpeg -nostdin -loglevel error -y -ss $2 -to $3 -i $M -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k $D/$1.mp4; }
cut Local_06-08s_ModelOutput 5.4 9.4
cut Local_11-20s_Branch_to_Output 9.6 19.8
cut Local_24-30s_Verification 22.4 31.0
python3 - <<'PY'
from PIL import Image, ImageDraw
import glob
fs = sorted(glob.glob('out/post_t2/comp_int2/*.jpg')); idx = list(range(0, len(fs), 30))
W, H, cols = 216, 384, 8; rows = -(-len(idx) // cols)
S = Image.new('RGB', (W * cols, H * rows), 'white')
for n, i in enumerate(idx):
    im = Image.open(fs[i]).resize((W, H)); ImageDraw.Draw(im).text((5, 5), f'{i / 30:.0f}s', fill=(220, 0, 0)); S.paste(im, ((n % cols) * W, (n // cols) * H))
S.save('out/deliver_t2/EP01_IntegratedAnimation_Test02_接触表_每秒.jpg', quality=88)
PY
echo done
