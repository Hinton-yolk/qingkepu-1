#!/usr/bin/env bash
# 渲出 T4 的两个文件：静音版（没有字幕条）和试听版（临时声音 + 字幕条代替口播）。
# 用法：t4_film/build.sh <工作目录>   （视频不进仓库）
# 并行：每个版本拆成 4 个 Chromium 进程；试听版只重渲「字幕条正在显示」的帧，其余帧复制自静音版。
set -euo pipefail
OUT="$1"; HERE="$(cd "$(dirname "$0")" && pwd)"; mkdir -p "$OUT"
N=930; K=4; T0=$(date +%s)
rm -rf "$OUT/fr_silent" "$OUT/fr_sound"; mkdir -p "$OUT/fr_silent" "$OUT/fr_sound"
for w in $(seq 0 $((K-1))); do node "$HERE/render_par.cjs" "$HERE/t4.html" "$OUT/fr_silent" '{"captions":false}' $N $w $K & done; wait
T1=$(date +%s); echo "静音版 $N 帧渲染用时 $((T1-T0)) 秒"
for w in $(seq 0 $((K-1))); do node "$HERE/render_par.cjs" "$HERE/t4.html" "$OUT/fr_sound" '{"captions":true}' $N $w $K --caps-only & done; wait
for f in "$OUT"/fr_silent/f_*.png; do b=$(basename "$f"); [ -e "$OUT/fr_sound/$b" ] || cp "$f" "$OUT/fr_sound/$b"; done
T2=$(date +%s); echo "试听版补渲 + 复制用时 $((T2-T1)) 秒；两版合计 $((T2-T0)) 秒"
node "$HERE/dump_events.cjs" "$OUT/events.json"
python3 "$HERE/audio_t4.py" "$OUT/events.json" "$OUT/t4.wav"
enc() { # enc <帧目录> <crf> <输出> [音频]
  local a=(); [ -n "${4:-}" ] && a=(-i "$4" -c:a aac -b:a 96k -shortest) || a=(-an)
  ffmpeg -v error -y -framerate 30 -i "$1/f_%05d.png" "${a[@]}" -vf scale=540:960:flags=lanczos \
    -c:v libx264 -preset slow -crf "$2" -pix_fmt yuv420p -movflags +faststart -map_metadata -1 "$3"
}
# 响度：量一次，调到约 -15 LUFS（不削波）
I=$(ffmpeg -nostats -i "$OUT/t4.wav" -af ebur128=peak=true -f null - 2>&1 | grep -A1 'Integrated loudness' | grep 'I:' | awk '{print $2}' | tail -1)
G=$(python3 -c "print(round(-15.0-(${I:- -23.0}),2))")
ffmpeg -v error -y -i "$OUT/t4.wav" -af "volume=${G}dB,alimiter=limit=0.89" "$OUT/t4_norm.wav"
echo "响度 ${I} LUFS → 增益 ${G} dB"
S="$OUT/EP01_T4_story_v1_silent_540x960_30fps.mp4"; V="$OUT/EP01_T4_story_v1_sound_540x960_30fps.mp4"
for pair in "silent:$S:" "sound:$V:$OUT/t4_norm.wav"; do
  IFS=: read -r mode f aud <<<"$pair"
  for crf in 20 22 24 27 30; do
    enc "$OUT/fr_$mode" $crf "$f" "$aud"
    sz=$(stat -c %s "$f"); echo "$mode crf=$crf $sz 字节"
    [ "$sz" -lt 3000000 ] && break
  done
done
ls -la "$OUT"/*.mp4
