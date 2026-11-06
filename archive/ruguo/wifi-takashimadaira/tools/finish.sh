#!/bin/sh
# Unattended finish: wait for the running final render, render the frames still missing (the corrected opening),
# encode (H.264 yuv420p CRF 16 + mix), then run the delivery checks. Log: review/finish.log
cd "$(dirname "$0")/.."
export LIB=${LIB:-/root/lemo-opuscar}
echo "finish: render done, filling missing frames + encoding ($(date -u +%H:%M))"
node render.mjs --workers 2 --q "pr=1&ssaa=1.5" 2>&1 | grep -v "GL Driver\|\[note\]"
F="out/如果眼睛能看见WiFi_高岛平团地.mp4"
[ -f "$F" ] || { echo "finish: FAILED, no film"; exit 1; }
"$LIB/.venv/bin/python" tools/finalcheck.py "$F" 2>&1 | grep -v Warning
echo "finish: DONE ($(date -u +%H:%M))"
