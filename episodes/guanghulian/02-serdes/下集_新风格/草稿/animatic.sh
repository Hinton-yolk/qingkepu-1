#!/bin/bash
# 带配音的草稿样片：每句按原稿字幕分段，每段一帧；分段时长按字数在这句配音里分配
set -e; cd "$(dirname "$0")"; V=../配音; rm -rf seg && mkdir -p seg; : > list.txt
python3 - <<'PY'
import json, subprocess
man = json.load(open('beats/manifest.json')); by = {}
for m in man: by.setdefault(m['id'], []).append(m)
for k, segs in by.items():
    d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'../配音/{k}.mp3']).decode()) + 0.3
    n = sum(len(s['seg']) for s in segs); t = 0
    with open('seg/' + k + '.txt', 'w') as fo:
        for s in segs:
            dur = d * len(s['seg']) / n; fo.write(f"file '../beats/{s['file']}'\nduration {dur:.3f}\n")
        fo.write(f"file '../beats/{segs[-1]['file']}'\n")
PY
for i in $(seq 1 14); do
  ffmpeg -v error -y -f concat -safe 0 -i seg/y$i.txt -i $V/y$i.mp3 -af "apad=pad_dur=0.3,loudnorm=I=-20:TP=-2" -r 30 -c:v libx264 -pix_fmt yuv420p -c:a aac -ar 48000 -shortest seg/s$i.mp4
  echo "file 'seg/s$i.mp4'" >> list.txt
done
ffmpeg -v error -y -f concat -safe 0 -i list.txt -c copy 下集_草稿样片_配音_v2.mp4; echo done
