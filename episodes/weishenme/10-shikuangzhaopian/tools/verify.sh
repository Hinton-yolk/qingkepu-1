#!/bin/sh
# verify.sh — checks on the finished film: stream facts, loudness/true peak of the encoded audio, black frames,
# and determinism (frames rendered on their own must match the full render byte for byte).
set -e
cd "$(dirname "$0")/.."
F=out/ep10-shikuangzhaopian.mp4
ffprobe -v error -show_entries stream=codec_name,pix_fmt,width,height,r_frame_rate,nb_frames:format=duration,size -of compact "$F"
ffmpeg -hide_banner -nostats -i "$F" -map 0:a -af ebur128=peak=true:framelog=quiet -f null - 2>&1 | grep -E "^\s+(I|Peak):"
echo "black frames:"; ffmpeg -hide_banner -nostats -i "$F" -vf blackdetect=d=0.05:pix_th=0.06 -an -f null - 2>&1 | grep -c black_start || true
node render.mjs --stills=4.1,20.233333333333334,37.7 --out=qa/det-v4 >/dev/null
for pair in "4.10 00123" "20.23 00607" "37.70 01131"; do
  set -- $pair
  if cmp -s "qa/det-v4/t$1.png" "out/frames/$2.png"; then echo "frame $2: identical"; else echo "frame $2: DIFFERENT"; fi
done
echo "AAC spikes:"; python3 tools/aacspikes.py audio/mix.wav "$F"
