#!/usr/bin/env bash
# 「观众」角色（Codex）：看逐秒截图（每张接触表 12 秒）+ 屏幕文字时间表，扮演抖音 / 小红书普通用户。它听不到声音（片子本来也没有旁白）。
# 用法：bash dl60/audience60.sh <成片.mp4> <输出目录>
set -euo pipefail
F="$(realpath "$1")"; O="$(realpath -m "$2")"; cd "$(dirname "$0")"; mkdir -p "$O/frames"
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
PROMPT="你是刷抖音 / 小红书的普通用户（不是专家，对芯片和 AI 只有一般了解）。附件是一条 60 秒竖屏科普短片的逐秒截图（每张接触表 12 秒，左上角标了秒数）。这条片子没有旁白、没有字幕，只有画面、少量屏幕文字和配乐（你听不到声音）。下面是屏幕文字的时间表。
请像真实观众那样回答，用中文，直白一点：
1. 前 3 秒会不会让你停下来？为什么？
2. 哪一秒你最可能划走？为什么？
3. 看完你能用一句话说出「AI 为什么要用显卡」吗？写出来。
4. 小岛那段（方块算地块）、2×4+3×5=23 那段、最后方块落进芯片那段，你看懂了吗？哪里没跟上？
5. 整条片子感觉是一条连贯的镜头，还是几段拼起来的？哪一处最像「换了一个片子」？给出秒数。
6. 有没有看不清、字太小、太快、或者让你误会的地方？给出秒数。
7. 你会点赞 / 收藏 / 关注吗？最想让作者改的 3 件事。
不要客套，说真实感受。

屏幕文字时间表：
$(grep '^|' docs/屏幕文字与时间表_v01.md)"
IMGS=(); for s in "$O"/sheet_*.jpg; do IMGS+=(-i "$s"); done
codex exec --sandbox read-only --skip-git-repo-check "${IMGS[@]}" -- "$PROMPT" < /dev/null > "$O/audience_feedback.md" 2> "$O/codex.log" || true
tail -c 200 "$O/codex.log"; wc -c "$O/audience_feedback.md"
