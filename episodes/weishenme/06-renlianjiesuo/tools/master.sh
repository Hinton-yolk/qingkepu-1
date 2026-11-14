#!/bin/sh
# score.wav -> audio/mix.wav : 32 Hz high-pass, two-pass loudnorm to -14 LUFS, 4x-oversampled limiter so AAC stays <= -1 dBTP
# EP.06: the loudnorm target is -13.3 so that, after the limiter, the mix lands on -14 LUFS (measured).
set -e
cd "$(dirname "$0")/.."
IN=${1:-music/score.wav}; OUT=${2:-audio/mix.wav}
MI=$(ffmpeg -hide_banner -nostats -i "$IN" -af highpass=f=32,loudnorm=I=-13.3:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p' | python3 -c "import json,sys;d=json.load(sys.stdin);print(f\"measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}\")")
ffmpeg -v error -y -i "$IN" -af "highpass=f=32,loudnorm=I=-13.3:TP=-1.5:LRA=9:$MI:linear=true,aresample=192000,alimiter=limit=0.68:level=false:attack=1:release=50,aresample=48000" -ar 48000 "$OUT"
ffmpeg -hide_banner -nostats -i "$OUT" -af ebur128=peak=true:framelog=quiet -f null - 2>&1 | grep -E "^\s+(I|Peak):"
