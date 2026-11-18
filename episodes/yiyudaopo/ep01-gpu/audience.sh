#!/usr/bin/env bash
# 「观众」角色：Codex 看逐秒抽帧（每张接触表 12 秒）+ 字幕时间表，扮演抖音 / 小红书普通用户给反馈。它听不到声音。
# 用法：bash audience.sh <成片.mp4> <输出目录>
set -euo pipefail
F="$(realpath "$1")"; O="$(realpath -m "$2")"; SRT="${3:-narration/EP01_Pilot_v03.srt}"; cd "$(dirname "$0")"; mkdir -p "$O/frames"
ffmpeg -loglevel error -y -i "$F" -vf "fps=1,scale=270:480" "$O/frames/s%03d.jpg"
python3 - "$O" <<'PY'
import glob, os, sys
from PIL import Image, ImageDraw
O = sys.argv[1]; fs = sorted(glob.glob(os.path.join(O, 'frames', 's*.jpg'))); per = 12
for k in range(0, len(fs), per):
    ims = [Image.open(f) for f in fs[k:k + per]]
    S = Image.new('RGB', (6 * 276, 2 * 506), (30, 30, 30)); D = ImageDraw.Draw(S)
    for i, im in enumerate(ims):
        x, y = (i % 6) * 276, (i // 6) * 506; S.paste(im, (x, y + 24)); D.text((x + 4, y + 4), f'{k + i}s', fill=(255, 255, 0))
    S.save(os.path.join(O, f'sheet_{k // per:02d}.jpg'), quality=80)
PY
cp "$SRT" "$O/captions.srt"
PROMPT="你是刷抖音 / 小红书的普通用户（不是专家，对芯片和 AI 只有一般了解）。附件是一条约 100 秒竖屏科普视频的逐秒截图（每张接触表 12 秒，左上角标了秒数），下面是字幕时间表（你听不到声音，配音内容就是字幕）。
请像真实观众那样回答，用中文，直白一点：
1. 前 3 秒会不会让你停下来？为什么？
2. 哪一秒你最可能划走？为什么？
3. 看完你能用一句话说出「AI 为什么要用显卡」吗？写出来。
4. 2×4+3×5=23 那段、CPU 和 GPU 对比那段，你看懂了吗？哪里没跟上？
5. 有没有哪个画面看不清、字太小、太快、或者让你误会的地方？给出秒数。
6. 你会点赞 / 收藏 / 关注吗？最想让作者改的 3 件事。
不要客套，说真实感受。

字幕时间表：
$(cat "$SRT")"
IMGS=(); for s in "$O"/sheet_*.jpg; do IMGS+=(-i "$s"); done
codex exec --sandbox read-only --skip-git-repo-check "${IMGS[@]}" -- "$PROMPT" < /dev/null > "$O/audience_feedback.md" 2> "$O/codex.log" || true
tail -c 200 "$O/codex.log"; wc -c "$O/audience_feedback.md"
