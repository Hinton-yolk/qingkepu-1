#!/bin/sh
# One command: voice layout → speech check → score + beats (cuecheck) → mix → picture → encode → subtitles.
# The Fish voice lines (voice/fish/L*.wav) are generated once with the Fish Audio 「科普」 voice and kept; the rest is rebuilt here.
set -e
LIB=${LIB:-/root/lemo-opuscar}
export LIB
HERE=$(cd "$(dirname "$0")" && pwd)
cd "$HERE"
[ -f data/A/model.json ] || { python3 tools/fetch.py && python3 tools/prep.py A; }
[ -f data/A/glow.png ] || python3 tools/glow.py
python3 tools/layout.py
"$LIB/.venv/bin/python" "$LIB/core/tts/asr_check.py" voice/asr_lines.json voice/fish --lang zh
python3 tools/score.py
python3 tools/beats.py
python3 tools/mix.py
node render.mjs --workers ${WORKERS:-2} --q "${QUALITY:-pr=1&ssaa=1.5}"
python3 "$LIB/core/render/srt.py" cues.json "out/如果眼睛能看见WiFi_高岛平团地.srt"
