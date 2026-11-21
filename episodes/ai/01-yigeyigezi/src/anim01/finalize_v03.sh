#!/bin/bash
# AUDIENCE-FIRST V03 出片：合成（提示层 + 音效）→ 三段局部视频 → 每秒接触表 → 手机尺寸接触表 → 动效检查
set -e
cd "$(dirname "$0")"
rm -rf out/post_v03/comp_v03
python3 post.py v03 out/frames_v03/v03 out/post_v03
D=out/deliver_v03; mkdir -p $D/share
M=out/post_v03/EP01_AudienceFirst_v03.mp4; cp $M $D/
cut() { ffmpeg -nostdin -loglevel error -y -ss $2 -to $3 -i $M -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k $D/$1.mp4; }
cut V03_First5s 0 5                       # 前 5 秒
cut V03_Fork_Climax 12.4 22.4             # 分叉：同一个前缀，两种未来 → 选定「去」
cut V03_Speculative_Climax 37.8 56.2      # 先猜再验：小模型草稿 → 大模型一趟 → 对照 → 接受 / 退回 / 补上
python3 - <<'PY'
from PIL import Image, ImageDraw
import glob
fs = sorted(glob.glob('out/post_v03/comp_v03/*.jpg')); idx = list(range(0, len(fs), 30))
W, H, cols = 180, 320, 12; rows = -(-len(idx) // cols)
S = Image.new('RGB', (W * cols, H * rows), 'white')
for n, i in enumerate(idx):
    im = Image.open(fs[i]).resize((W, H)); ImageDraw.Draw(im).text((5, 5), f'{i / 30:.0f}s', fill=(220, 0, 0)); S.paste(im, ((n % cols) * W, (n // cols) * H))
S.save('out/deliver_v03/EP01_AudienceFirst_v03_接触表_每秒.jpg', quality=88)
# 手机尺寸检查：360×640（不放大）
idx = list(range(0, len(fs), 60)); W, H, cols = 360, 640, 6; rows = -(-len(idx) // cols)
S = Image.new('RGB', (W * cols, H * rows), 'white')
for n, i in enumerate(idx):
    im = Image.open(fs[i]).resize((W, H), Image.LANCZOS); ImageDraw.Draw(im).text((5, 5), f'{i / 30:.0f}s', fill=(220, 0, 0)); S.paste(im, ((n % cols) * W, (n // cols) * H))
S.save('out/deliver_v03/EP01_AudienceFirst_v03_手机尺寸_每2秒.jpg', quality=85)
PY
for f in $D/*.mp4; do ffmpeg -nostdin -loglevel error -y -i $f -c:v libx264 -crf 24 -preset slow -pix_fmt yuv420p -c:a aac -b:a 160k $D/share/$(basename $f); done
python3 ../../../../../tools/motion_check.py $M v03 --end=70.5 | tail -2
echo done
