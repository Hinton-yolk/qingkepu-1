#!/usr/bin/env python3
"""降噪闪烁检查：Cycles 低采样 + 降噪的序列，在雾、散景、暗部容易出现「一团一团在蠕动」的低频闪烁。

做法：相邻三帧先用光流对齐到中间帧（相机在动也能比），再看中间帧和前后帧平均值的差。
  - 只看低频（先模糊掉 2 px 以下的细节）：降噪闪烁是成团的，不是单像素噪点；
  - 光流对不上的地方（遮挡、运动模糊的亮信号）用前后两帧互相的差挡掉。
输出：每帧的闪烁量（亮度的 1/255 为单位）、分区统计（3×6 格）、最闪的 3 帧的热力图和放大对比图。

用法：python3 tools/flicker_check.py <视频或 PNG 目录> <输出目录> [--step 1] [--amp 12]
判读（经验值，要配合亲眼看放大图）：整帧中位数 < 0.6 基本看不出；0.6–1.2 暗部和雾里细看能看到；> 1.2 手机上也看得到。
"""
import sys, os, glob, argparse, subprocess, json
import numpy as np, cv2

def frames(src, tmp):
    if os.path.isdir(src):
        fs = sorted(glob.glob(os.path.join(src, '*.png'))); return fs
    os.makedirs(tmp, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, os.path.join(tmp, '%05d.png')], check=True)
    return sorted(glob.glob(os.path.join(tmp, '*.png')))

def load(p):
    im = cv2.imread(p, cv2.IMREAD_COLOR); return im.astype(np.float32)

def warp(src, flow):
    h, w = flow.shape[:2]; gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    return cv2.remap(src, gx + flow[..., 0], gy + flow[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out'); ap.add_argument('--step', type=int, default=1); ap.add_argument('--amp', type=float, default=12)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    fs = frames(a.src, os.path.join(a.out, '_frames')); n = len(fs)
    if n < 3: sys.exit('帧数不足 3')
    rows = []; acc = None; cnt = None; worst = []
    for i in range(1, n - 1, a.step):
        p, c, q = load(fs[i - 1]), load(fs[i]), load(fs[i + 1])
        g = lambda x: cv2.cvtColor(np.clip(x, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
        gp, gc, gq = g(p), g(c), g(q)
        fp = cv2.calcOpticalFlowFarneback(gc, gp, None, 0.5, 4, 31, 3, 7, 1.5, 0)
        fq = cv2.calcOpticalFlowFarneback(gc, gq, None, 0.5, 4, 31, 3, 7, 1.5, 0)
        wp, wq = warp(p, fp), warp(q, fq)
        lum = lambda x: cv2.GaussianBlur(x @ np.array([0.114, 0.587, 0.299], np.float32), (0, 0), 2.0)
        lp, lc, lq = lum(wp), lum(c), lum(wq)
        r = np.abs(lc - 0.5 * (lp + lq))                      # 中间帧偏离前后平均：闪烁
        bad = np.abs(lp - lq) > 6.0                           # 前后两帧自己都对不上：遮挡 / 光流失败 / 真实的快速变化
        bad |= (np.hypot(fp[..., 0], fp[..., 1]) > 40)        # 运动太大的地方不算
        bad = cv2.dilate(bad.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
        r[bad] = np.nan
        dark = lc < 60                                        # 暗部单独报：降噪闪烁在暗部和雾里最明显
        rows.append(dict(frame=i + 1, med=float(np.nanmedian(r)), p95=float(np.nanpercentile(r, 95)), dark_med=float(np.nanmedian(r[dark])) if dark.any() and np.isfinite(r[dark]).any() else None, masked=float(bad.mean())))
        z = np.nan_to_num(r, nan=0.0); m = (~bad).astype(np.float32)
        acc = z if acc is None else acc + z; cnt = m if cnt is None else cnt + m
        worst.append((rows[-1]['p95'], i, r, c, wp, wq))
        worst = sorted(worst, key=lambda t: -t[0])[:3]
    mean = acc / np.maximum(cnt, 1); h, w = mean.shape
    grid = [[round(float(mean[y * h // 6:(y + 1) * h // 6, x * w // 3:(x + 1) * w // 3].mean()), 2) for x in range(3)] for y in range(6)]
    med = float(np.median([r['med'] for r in rows])); p95 = float(np.median([r['p95'] for r in rows]))
    dm = [r['dark_med'] for r in rows if r['dark_med'] is not None]
    summ = dict(src=a.src, frames=n, med=round(med, 3), p95=round(p95, 3), dark_med=round(float(np.median(dm)), 3) if dm else None,
                worst_frames=[int(t[1] + 1) for t in worst], grid_3x6=grid, per_frame=rows)
    json.dump(summ, open(os.path.join(a.out, 'flicker.json'), 'w'), ensure_ascii=False, indent=1)
    hm = np.clip(mean / 3.0 * 255, 0, 255).astype(np.uint8); hm = cv2.applyColorMap(hm, cv2.COLORMAP_INFERNO)
    cv2.imwrite(os.path.join(a.out, 'heat_mean.jpg'), hm, [cv2.IMWRITE_JPEG_QUALITY, 85])
    for k, (s, i, r, c, wp, wq) in enumerate(worst):          # 最闪的帧：左 = 原帧，右 = 和前后帧平均的差 × amp（灰 = 无差别）
        d = (c - 0.5 * (wp + wq)) * a.amp + 128; side = np.hstack([c, np.clip(d, 0, 255)]).astype(np.uint8)
        cv2.imwrite(os.path.join(a.out, f'worst{k + 1}_f{i + 1:04d}.jpg'), side, [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(f"{a.src}: {n} 帧  闪烁中位数 {med:.2f}  95 分位 {p95:.2f}  暗部 {summ['dark_med']}  最闪的帧 {summ['worst_frames']}")
    print('分区（上→下 6 行 × 左→右 3 列）：'); [print('  ', g_) for g_ in grid]

if __name__ == '__main__': main()
