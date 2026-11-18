#!/usr/bin/env bash
# 一语道破 EP01 · DIRECTOR-LOCKED 60s 出片
#   前置：python3 dl60/blender/encode.py final_OPEN final_CLOSE（Blender 底片 → remotion/public/dl60/*.mp4）
#         python3 dl60/audio/dl60_audio.py                      （配乐 + 音效 → remotion/public/dl60/mix.wav）
#   输出：remotion/out/dl60/EP01_DirectorLocked60_v01.mp4（1080×1920，30 fps，1800 帧，-14 LUFS）
#         + 五段转场对比片段、12 个时间点的接触表、动效检查
set -euo pipefail
cd "$(dirname "$0")/../remotion"
O=out/dl60; mkdir -p $O/transitions $O/review
npx tsc --noEmit -p .
npx remotion render src60/index.ts EP01DirectorLocked60 $O/raw.mp4 --crf=16 --jpeg-quality=95 --concurrency=4 --gl=swangle --log=error
J=$(ffmpeg -hide_banner -nostats -i $O/raw.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$J" | python3 -c "import sys,json;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -y -loglevel error -i $O/raw.mp4 -c:v copy \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" \
  -c:a aac -b:a 192k -movflags +faststart $O/EP01_DirectorLocked60_v01.mp4
F=$O/EP01_DirectorLocked60_v01.mp4
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_read_frames -of compact $F
ffmpeg -hide_banner -nostats -i $F -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2
# 五个转场：边界前后各约 1.5–2.5 秒
clip() { ffmpeg -y -loglevel error -ss $2 -t $3 -i $F -c:v libx264 -crf 18 -c:a aac -b:a 160k $O/transitions/$1.mp4; }
clip T1_GPU_to_game_viewport 3.6 2.8
clip T2_game_to_AI 13.6 4.4
clip T3_one_op_to_many 26.8 4.6
clip T4_patterns_to_revelation 40.4 5.0
clip T5_abstract_to_physical_GPU 46.4 5.6
# 12 个检查时间点：原尺寸帧 + 手机尺寸接触表
for s in 0 5 11 17 23 30 36 42 48 51 57 59.966; do
  ffmpeg -y -loglevel error -ss $s -i $F -frames:v 1 $O/review/t$(printf %06.3f $s).png
done
python3 - $O/review <<'PY'
import sys, glob, os
from PIL import Image, ImageDraw
d = sys.argv[1]; fs = sorted(glob.glob(os.path.join(d, 't*.png')))
w, h = 360, 640; S = Image.new('RGB', (6 * (w + 8), 2 * (h + 34)), (30, 30, 30)); D = ImageDraw.Draw(S)
for i, f in enumerate(fs):
    x, y = (i % 6) * (w + 8), (i // 6) * (h + 34)
    S.paste(Image.open(f).resize((w, h), Image.LANCZOS), (x, y + 30)); D.text((x + 6, y + 8), os.path.basename(f)[1:-4] + ' s', fill=(255, 255, 255))
S.save(os.path.join(d, 'contact_sheet_phone_360x640.jpg'), quality=90)
PY
python3 ../../../../tools/motion_check.py $F dl60 --end=59.7 || true
sha256sum $F
