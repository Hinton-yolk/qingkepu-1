#!/usr/bin/env python3
"""blender/out/<镜头>/*.png → remotion/public/plates/<镜头>.mp4，并更新 remotion/src/plates.json。
缺尾帧时用最后一帧补齐到镜头长度（并记在 plates_status.json 里，镜头清单据此标「未完成」）。"""
import glob, json, os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); RM = os.path.join(os.path.dirname(HERE), 'remotion')
SHOTS = {'DC': 135, 'MACRO': 135, 'CHIP': 300}
os.makedirs(os.path.join(RM, 'public', 'plates'), exist_ok=True)
avail, status = {}, {}
for s, n in SHOTS.items():
    fs = sorted(glob.glob(os.path.join(HERE, 'out', s, f'{s}_*.png')))
    nums = [int(re.search(r'_(\d+)\.png', f).group(1)) for f in fs]
    contig = 0
    while contig + 1 in nums: contig += 1
    status[s] = dict(rendered=len(fs), contiguous=contig, needed=n)
    if contig < 2: avail[s] = False; continue
    out = os.path.join(RM, 'public', 'plates', f'{s}.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '30', '-start_number', '1', '-i', os.path.join(HERE, 'out', s, f'{s}_%04d.png'),
                    '-frames:v', str(contig), '-vf', f'tpad=stop_mode=clone:stop={n - contig},format=yuv420p', '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', out], check=True)
    avail[s] = True
json.dump(avail, open(os.path.join(RM, 'src', 'plates.json'), 'w'))
json.dump(status, open(os.path.join(HERE, 'plates_status.json'), 'w'), indent=1)
print(status)
