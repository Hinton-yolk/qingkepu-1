#!/usr/bin/env python3
"""Blender 段的影调对齐到 three.js：Blender 用 AgX 出图，比 three.js 灰（暗部抬高、中高调压低），接口处一眼能看出来。
在接口附近的帧上，把「合成后的 Blender 帧」和「同一帧的 three.js 画面」逐通道按分位数配对，拟合一条单调曲线，
套到 Blender 原始帧上（原始帧先备份到 <hyb>_orig，只读它，可以反复重拟）。

  python3 hyb_tone.py fit   <three.js 整片.mp4> <合成帧目录> <曲线.json> <首帧:尾帧> [...] [--prev 曲线.json]
  python3 hyb_tone.py apply <曲线.json> <Blender 帧目录>
  python3 hyb_tone.py check <three.js 整片.mp4> <合成帧目录> <首帧:尾帧> [...]
fit 用每段两头各一帧（跳过 12 帧淡化区）；--prev 时把新拟合的残差曲线叠在旧曲线上（第二轮微调）。
只看画面上部 1250 px（字幕和标注两边一样，不参与拟合）。
"""
import io, json, os, shutil, subprocess, sys
import numpy as np
from PIL import Image

Q = np.arange(5, 96, 5)            # 5 % … 95 %
TOP = 1250


def frame(mp4, f):
    out = subprocess.run(["ffmpeg", "-v", "error", "-i", mp4, "-vf", f"select=eq(n\\,{f})", "-vsync", "0", "-frames:v", "1",
                          "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    return np.asarray(Image.open(io.BytesIO(out)).convert("RGB"), dtype=np.float32)


def seam_frames(segs):
    return [f for s0, s1 in segs for f in (([] if s0 == 0 else [s0 + 14]) + [s1 - 14])]


def pairs(mp4, comp, segs):
    """per-channel quantiles (three.js, composite), averaged over the seam frames"""
    T, C = [], []
    for f in seam_frames(segs):
        t = frame(mp4, f)[:TOP].reshape(-1, 3); c = np.asarray(Image.open(os.path.join(comp, f"{f:05d}.png")).convert("RGB"), dtype=np.float32)[:TOP].reshape(-1, 3)
        T.append(np.percentile(t, Q, axis=0)); C.append(np.percentile(c, Q, axis=0))
    return np.mean(T, 0), np.mean(C, 0)     # (len(Q), 3)


def lut_from(xs, ys):
    """monotone 0..255 LUT through (0,0), the pairs, (255,255)"""
    x = np.concatenate([[0], xs, [255]]); y = np.maximum.accumulate(np.concatenate([[0], ys, [255]]))
    keep = np.concatenate([[True], np.diff(x) > 1]); return np.clip(np.interp(np.arange(256), x[keep], y[keep]), 0, 255)


def main():
    a = sys.argv[1:]; cmd = a[0]
    if cmd == "fit":
        prev = json.load(open(a[a.index("--prev") + 1])) if "--prev" in a else None
        if prev: i = a.index("--prev"); del a[i:i + 2]
        mp4, comp, out = a[1], a[2], a[3]; segs = [tuple(map(int, s.split(":"))) for s in a[4:]]
        t, c = pairs(mp4, comp, segs)
        L = []
        for ch in range(3):
            r = lut_from(c[:, ch], t[:, ch])                                  # composite -> three.js (residual)
            base = np.array(prev["lut"][ch]) if prev else np.arange(256, dtype=float)
            L.append(np.round(np.interp(base, np.arange(256), r), 2).tolist())   # raw -> base -> residual
        json.dump(dict(lut=L, q=Q.tolist(), three=t.round(1).tolist(), comp=c.round(1).tolist(), segs=segs), open(out, "w"))
        for ch, n in enumerate("RGB"):
            print(n, "comp", c[:, ch].round(0)[::3], "-> three", t[:, ch].round(0)[::3])
    elif cmd == "apply":
        L = np.array(json.load(open(a[1]))["lut"]); d = a[2].rstrip("/"); orig = d + "_orig"
        if not os.path.isdir(orig): shutil.copytree(d, orig)                  # keep the untouched renders once
        fs = sorted(f for f in os.listdir(orig) if f.endswith(".png"))
        for f in fs:
            im = np.asarray(Image.open(os.path.join(orig, f)).convert("RGB"))
            Image.fromarray(np.stack([L[ch][im[..., ch]] for ch in range(3)], -1).round().astype(np.uint8)).save(os.path.join(d, f))
        print(f"{len(fs)} frames: {orig} -> {d}")
    elif cmd == "check":
        mp4, comp = a[1], a[2]; segs = [tuple(map(int, s.split(":"))) for s in a[3:]]
        for f in seam_frames(segs):
            t = frame(mp4, f)[:TOP].reshape(-1, 3); c = np.asarray(Image.open(os.path.join(comp, f"{f:05d}.png")).convert("RGB"), dtype=np.float32)[:TOP].reshape(-1, 3)
            print(f, "mean three", t.mean(0).round(1), "blender", c.mean(0).round(1), " p10/p90 three", np.percentile(t.mean(1), [10, 90]).round(0), "blender", np.percentile(c.mean(1), [10, 90]).round(0))


if __name__ == "__main__":
    main()
