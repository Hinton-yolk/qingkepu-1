#!/bin/bash
# Full Motion Draft V02 出片：帧表 → 合成 → 两段局部视频 → 每秒接触表 → 交付目录（含压缩的分享版）
set -e
cd "$(dirname "$0")"
python3 assemble_v02.py
rm -rf out/post_v02/comp_v02
python3 post.py v02 out/frames_v02/film out/post_v02
D=out/deliver_v02; mkdir -p $D/share
M=out/post_v02/EP01_FullMotionDraft_v02.mp4; cp $M $D/
cut() { ffmpeg -nostdin -loglevel error -y -ss $2 -to $3 -i $M -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k $D/$1.mp4; }
cut V02_Stepwise_SameStart_Speculative 30.4 47.6      # 逐步生成 → 回到同一起点 → 推测解码（连续）
cut V02_ParallelVerification 41.4 55.4                # 集中验证机制：草稿 → 一轮评估 → 接受 / 作废 / 补充
python3 - <<'PY'
from PIL import Image, ImageDraw
import glob
fs = sorted(glob.glob('out/post_v02/comp_v02/*.jpg')); idx = list(range(0, len(fs), 30))
W, H, cols = 180, 320, 14; rows = -(-len(idx) // cols)
S = Image.new('RGB', (W * cols, H * rows), 'white')
for n, i in enumerate(idx):
    im = Image.open(fs[i]).resize((W, H)); ImageDraw.Draw(im).text((5, 5), f'{i / 30:.0f}s', fill=(220, 0, 0)); S.paste(im, ((n % cols) * W, (n // cols) * H))
S.save('out/deliver_v02/EP01_FullMotionDraft_v02_接触表_每秒.jpg', quality=88)
PY
for f in $D/*.mp4; do ffmpeg -nostdin -loglevel error -y -i $f -c:v libx264 -crf 24 -preset slow -pix_fmt yuv420p -c:a aac -b:a 160k $D/share/$(basename $f); done
python3 ../../../../../tools/motion_check.py $M v02 --end=63.0 | tail -2
echo done
