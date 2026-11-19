#!/bin/sh
# cut.sh — the music is composed in internal time; the film skips internal [CUT, CUT+GAP) (timeline.js). Cut the score the
# same way, with 10 ms fades at the join (both sides sit on the beat grid, one bar apart, so the pulse carries on).
set -e
cd "$(dirname "$0")/.."
IN=${1:-music/score-C.wav}; OUT=${2:-music/score.wav}
eval "$(node -e 'const T=require("./timeline.js");console.log(`CUT=${T.CUT} GAP=${T.GAP}`)')"
B=$(python3 -c "print($CUT+$GAP)"); F=$(python3 -c "print($CUT-0.01)")
ffmpeg -v error -y -i "$IN" -filter_complex "[0]atrim=0:$CUT,asetpts=PTS-STARTPTS,afade=t=out:st=$F:d=0.01[a];[0]atrim=start=$B,asetpts=PTS-STARTPTS,afade=t=in:d=0.01[b];[a][b]concat=n=2:v=0:a=1" -ar 48000 "$OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
