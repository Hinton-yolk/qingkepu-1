#!/usr/bin/env python3
"""dl60/blender/out/<目录>/<镜头>_<片子帧号>.png → remotion/public/dl60/<镜头>.mp4（1080×1920，30 fps，帧数 = 镜头帧数），更新 src60/plates.json。
隔帧渲染的（文件名帧号有间隔）用 minterpolate 补帧；分辨率不足的放大到 1080×1920（lanczos）。
用法：python3 encode.py <目录名> [<目录名> ...]     例：python3 encode.py draft_OPEN draft_CLOSE"""
import glob, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); RM = os.path.join(HERE, '..', '..', 'remotion')
SHOT = {'OPEN': (0, 165), 'CLOSE': (1455, 1799)}
os.makedirs(os.path.join(RM, 'public', 'dl60'), exist_ok=True)
pj = os.path.join(RM, 'src60', 'plates.json'); avail = json.load(open(pj))
for d in sys.argv[1:]:
    fs = sorted(glob.glob(os.path.join(HERE, 'out', d, '*.png')))
    shot = os.path.basename(fs[0]).split('_')[0]; f0, f1 = SHOT[shot]; n = f1 - f0 + 1
    nums = [int(re.search(r'_(\d+)\.png$', f).group(1)) for f in fs]
    lst = os.path.join(HERE, 'out', f'{d}.txt')
    with open(lst, 'w') as o:
        for i, f in enumerate(fs):
            dur = ((nums[i + 1] if i + 1 < len(nums) else f1 + 1) - nums[i]) / 30
            o.write(f"file '{f}'\nduration {dur:.6f}\n")
        o.write(f"file '{fs[-1]}'\n")
    step = nums[1] - nums[0] if len(nums) > 1 else 1
    vf = 'scale=1080:1920:flags=lanczos'
    if step > 1: vf = f'fps={30 / step},minterpolate=fps=30:mi_mode=blend,' + vf
    out = os.path.join(RM, 'public', 'dl60', f'{shot}.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-vf', vf + ',tpad=stop_mode=clone:stop=30,format=yuv420p',
                    '-frames:v', str(n), '-r', '30', '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', out], check=True)
    r = subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-show_entries', 'stream=nb_read_frames,width,height', '-of', 'csv=p=0', out], capture_output=True, text=True)
    print(shot, d, 'frames in', len(fs), 'step', step, '→', r.stdout.strip())
    avail[shot] = True
json.dump(avail, open(pj, 'w'))
