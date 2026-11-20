#!/bin/bash
# Full Motion Draft V01 出片：合成 → 五处转场片段 → 每秒接触表 → 交付目录
set -e
cd "$(dirname "$0")"
python3 post.py full out/frames_full/full out/post_full
D=out/deliver_full; mkdir -p $D
M=out/post_full/EP01_FullMotionDraft_v01.mp4; cp $M $D/
cut() { ffmpeg -nostdin -loglevel error -y -ss $2 -to $3 -i $M -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k $D/$1.mp4; }
cut T1_Phone_to_ModelInput 5.0 11.5
cut T2_Candidates_to_Branch 17.4 21.6
cut T3_Choice_to_ContextUpdate 25.0 35.2
cut T4_Stepwise_to_DraftVerify 37.8 45.0
cut T5_Result_to_Phone 52.6 59.6
python3 - <<'PY'
from PIL import Image, ImageDraw
import glob
fs = sorted(glob.glob('out/post_full/comp_full/*.jpg')); idx = list(range(0, len(fs), 30))
W, H, cols = 180, 320, 13; rows = -(-len(idx) // cols)
S = Image.new('RGB', (W * cols, H * rows), 'white')
for n, i in enumerate(idx):
    im = Image.open(fs[i]).resize((W, H)); ImageDraw.Draw(im).text((5, 5), f'{i / 30:.0f}s', fill=(220, 0, 0)); S.paste(im, ((n % cols) * W, (n // cols) * H))
S.save('out/deliver_full/EP01_FullMotionDraft_v01_接触表_每秒.jpg', quality=88)
PY
echo done
