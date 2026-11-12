#!/usr/bin/env bash
# T5 合成一条命令：bash t5_comp_build.sh <帧根> <输出目录>
# 帧根下：shot1/ shot23/ arrive/（Blender 渲出的 PNG）。缺帧会用最近的已有帧补，写进 <输出目录>/comp_log.txt。
# 锚点：<输出目录>/anchors/{shot1,shot23,arrive}.json，缺哪个就自己跑 Blender --anchors 生成（几秒）。
# 环境变量：BLENDER（Blender 路径）、THREADS（默认 2）、MAXMB（默认 2.9，每个 mp4 的大小上限）
set -euo pipefail
ROOT="${1:?帧根}"; OUT="${2:?输出目录}"; HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLENDER="${BLENDER:-/tmp/claude-0/-home-user-kepu-studio/4daddf6d-cedd-56c3-84f6-9e329c1f853a/scratchpad/blender/blender-5.2.3-linux-x64/blender}"
THREADS="${THREADS:-2}"; MAXMB="${MAXMB:-2.9}"; mkdir -p "$OUT/anchors"
SIL="$OUT/EP01_T5_preview_v1_silent_540x960_30fps.mp4"; SND="$OUT/EP01_T5_preview_v1_sound_540x960_30fps.mp4"
step() { echo "== $(date +%T) $*"; }

step 锚点
gen() {  # <名字> <脚本>
  [ -s "$OUT/anchors/$1.json" ] && return 0
  d="$OUT/anchors/_tmp_$1"; mkdir -p "$d"
  "$BLENDER" -b --python-exit-code 1 --python "$HERE/$2" -- "$d" --res 540x960 --threads "$THREADS" --anchors | grep -E 'ANCHORS_DONE|Error' || true
  mv "$d/anchors.json" "$OUT/anchors/$1.json"; rm -rf "$d"
}
gen shot1 t5_shot1.py; gen shot23 t5_shot23.py; gen arrive t5_arrive.py

step 时间表
python3 "$HERE/t5_comp_timeline.py"

step 画面（转场 + 叠加层 → 无损中间文件）
python3 "$HERE/t5_comp_render.py" "$ROOT" "$OUT/anchors" "$OUT"

step 声音
python3 "$HERE/t5_comp_audio.py" "$OUT/temp_audio_raw.wav"

enc() {  # <输入.mkv> <输出.mp4> [音频.wav]
  local crf=22 size
  while :; do
    if [ -n "${3:-}" ]; then
      ffmpeg -y -loglevel error -i "$1" -i "$3" -map 0:v -map 1:a -t 21.5 -c:v libx264 -preset slow -crf $crf -pix_fmt yuv420p -r 30 -c:a aac -b:a 128k -ar 44100 -movflags +faststart "$2"
    else
      ffmpeg -y -loglevel error -i "$1" -t 21.5 -c:v libx264 -preset slow -crf $crf -pix_fmt yuv420p -r 30 -an -movflags +faststart "$2"
    fi
    size=$(stat -c %s "$2"); echo "  crf=$crf size=$size"
    python3 -c "import sys; sys.exit(0 if $size < $MAXMB*1024*1024 else 1)" && break; crf=$((crf+2))
  done
}

step 静音版编码
enc "$OUT/lossless_silent.mkv" "$SIL"

step 试听版响度（loudnorm 两遍，目标 -15 LUFS、true peak ≤ -2 dBTP，编码后再实测）
TP=-2.0
for attempt in 1 2 3; do
  J=$(ffmpeg -hide_banner -nostats -i "$OUT/temp_audio_raw.wav" -af "loudnorm=I=-15:TP=$TP:LRA=7:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g() { echo "$J" | python3 -c "import sys,json; print(json.load(sys.stdin)['$1'])"; }
  ffmpeg -y -loglevel error -i "$OUT/temp_audio_raw.wav" -af "loudnorm=I=-15:TP=$TP:LRA=7:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,alimiter=limit=0.84:level=false,apad=whole_dur=21.5" -ar 44100 "$OUT/temp_audio_norm.wav"
  step "试听版编码（TP 目标 $TP）"; enc "$OUT/lossless_sound.mkv" "$SND" "$OUT/temp_audio_norm.wav"
  M=$(ffmpeg -hide_banner -nostats -i "$SND" -vn -af ebur128=peak=true -f null - 2>&1 | tail -14)
  PK=$(echo "$M" | grep -A1 'True peak' | grep Peak | awk '{print $2}')
  python3 -c "import sys; sys.exit(0 if float('$PK') <= -1.5 else 1)" && break; TP=$(python3 -c "print($TP-1.0)")
done

step 规格
for f in "$SIL" "$SND"; do
  echo "--- $(basename "$f")"; ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames,duration,bit_rate,sample_rate,channels -of default=nw=1 "$f" | tr '\n' ' '; echo
  echo "size: $(stat -c %s "$f") bytes"; sha256sum "$f"
done
echo "--- 试听版实测（ffmpeg ebur128，编码后的 AAC）"; echo "$M" | grep -E "I:|LRA:|Peak:"
rm -f "$OUT/lossless_silent.mkv" "$OUT/lossless_sound.mkv" "$OUT/temp_audio_raw.wav" "$OUT/temp_audio_norm.wav"
step 完成; cat "$OUT/comp_log.txt"
