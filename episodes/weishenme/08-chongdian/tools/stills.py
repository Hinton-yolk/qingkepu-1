#!/usr/bin/env python3
"""List the still stretches (>= 0.4 s) of the body, like motion_check.py (diff < 0.15 on a 135x240 grey copy)."""
import subprocess, sys, numpy as np
f, end = sys.argv[1], float(sys.argv[2]); w, h = 135, 240
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', f, '-vf', f'fps=30,scale={w}:{h},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
a = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(float); d = np.abs(np.diff(a, axis=0)).mean(axis=(1, 2)); st = d < 0.15
r = 0
for i, x in enumerate(list(st[:int(end * 30)]) + [False]):
    if x: r += 1
    else:
        if r >= 12: print(f"{(i - r) / 30:.2f}s +{r / 30:.2f}s")
        r = 0
