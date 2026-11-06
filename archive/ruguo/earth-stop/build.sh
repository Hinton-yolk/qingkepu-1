#!/bin/sh
# One command: voice layout (grid-snapped cues) → sound (score, effects, mix at -14 LUFS) → beat-grid check → full render.
# The Fish voice lines in voice/fish/ are generated once with the 「科普」 voice and kept.
set -e
cd "$(dirname "$0")"
python3 tools/layout.py
python3 tools/sound.py
python3 tools/beats.py
node render.mjs --video --workers=4 --tmp=frames --audio=audio/mix_full.wav --out=out/如果地球突然停止自转.mp4
rm -rf frames
python3 /root/lemo-opuscar/core/render/srt.py cues.json out/如果地球突然停止自转.srt
python3 tools/cover.py
