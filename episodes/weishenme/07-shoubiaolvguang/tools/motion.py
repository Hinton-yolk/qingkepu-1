#!/usr/bin/env python3
"""motion.py — how much the picture moves, second by second (mean absolute frame difference at 10 fps, 108×192 grey).
   python3 tools/motion.py film.mp4 [film2.mp4 ...]
Series rule (为什么系列): median per-second change >= 5, no still stretch longer than 1.5 s except deliberate pauses."""
import subprocess, sys, numpy as np
def measure(path, fps=10, w=108, h=192):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h},format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    sec = d[: len(d) // fps * fps].reshape(-1, fps).mean(axis=1)
    still = d < 0.15; run = best = 0; at = 0
    for i, s in enumerate(still):
        run = run + 1 if s else 0
        if run > best: best, at = run, i
    return sec, still.mean(), best / fps, (at - best + 1) / fps
for p in sys.argv[1:]:
    sec, frac, longest, where = measure(p)
    print(f"{p}: {len(sec)} s | mean {sec.mean():.2f} | median {np.median(sec):.2f} | still {100 * frac:.0f}% | longest still {longest:.1f} s at {where:.1f} s")
    print("  per second:", " ".join(f"{v:.1f}" for v in sec))
