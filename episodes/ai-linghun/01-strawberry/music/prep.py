#!/usr/bin/env python3
"""把 ACE-Step 生成的整首音乐对齐到片子的时间轴（music/brief.md）：
  1. 拍点对齐：测出拍点相位，整体平移，让拍点落在 0.6 秒（100 BPM）的格子上；
  2. 揭晓前停半拍：76.5–76.8 秒静音（前后 25 ms 淡入淡出）；
  3. 分段增益：讲解段让给字幕（-2 dB），揭晓段抬起（+1.5 dB），下期预告收回（-1.5 dB），片尾卡淡出到片尾（v6：92.0 秒）；
  4. 整体响度到 -14 LUFS：增益 + 限幅器（样本峰值 -1.6 dBFS，真峰值约 -1 dBTP），之后加音效再统一量一次。
用法：python3 prep.py <输入.wav> <输出前缀> [--dur 92.0]   → <前缀>.wav + <前缀>.mp3
v6（用户 11-23 删掉 S7 后两句、片尾提前）：对齐后在小节线上剪掉 81.6–86.445 秒（两小节，和画面提前的 4.8 秒一样；后端多 45 ms，因为 A1 实际约 99 BPM、拍子到这里已漂了约 50 ms），
接口 60 ms 等功率交叉淡化；剪点按色度 / 音色相似度在 77.4–82.2 秒的拍点里挑（81.6 在小节线上、得分第二）。v5 及以前：不剪，dur 99.29，分段见注释。
"""
import subprocess, sys
import numpy as np, soundfile as sf, librosa, pyloudnorm as pyln

BEAT = 0.6
# (起, 止, 增益 dB)：段落之间 0.3 秒线性过渡
# v5: [(0.0, 9.6, 0.0), (9.6, 76.5, -2.0), (76.8, 86.4, 1.5), (86.4, 96.0, -1.5), (96.0, 120.0, -1.5)], no cut, dur 99.29
SECTIONS = [(0.0, 9.6, 0.0), (9.6, 76.5, -2.0), (76.8, 82.2, 1.5), (82.2, 88.8, -1.5), (88.8, 120.0, -1.5)]   # times after the cut; 88.8 = end card
PAUSE = (76.5, 76.8)
CUT = (81.6, 86.445)   # aligned-music seconds removed (v6); None for no cut. The end is 45 ms past the 100-BPM grid: A1 really runs at ~99 BPM, so by 86.4 the beat has drifted (审核 11-23: with 86.4 the first beat after the join came ~50 ms late); 0.045 = best onset-envelope match of the bars on both sides


def loud(y, sr, target, pre):
    """gain to the target loudness, then a look-ahead limiter at -1.6 dBFS sample peak (≈ -1 dBTP true peak; ffmpeg alimiter); twice, since the limiter takes a little off"""
    meter = pyln.Meter(sr); tmp = pre + '.tmp.wav'
    for _ in range(3):
        y = y * 10 ** ((target - meter.integrated_loudness(y.T)) / 20)
        sf.write(tmp, y.T, sr, subtype='FLOAT')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-af', 'alimiter=limit=0.83:attack=3:release=80:level=0', '-c:a', 'pcm_f32le', pre + '.lim.wav'], check=True)
        y = sf.read(pre + '.lim.wav', always_2d=True)[0].T
        if abs(meter.integrated_loudness(y.T) - target) < 0.3: break
    import os; os.remove(tmp); os.rename(pre + '.lim.wav', pre + '.wav')
    sf.write(pre + '.wav', np.clip(y, -1, 1).T, sr, subtype='PCM_24')
    return y


def main():
    src, pre = sys.argv[1], sys.argv[2]
    dur = float(sys.argv[sys.argv.index('--dur') + 1]) if '--dur' in sys.argv else 92.0
    y, sr = sf.read(src, always_2d=True); y = y.T.astype(np.float64)
    m = librosa.resample(y.mean(0), orig_sr=sr, target_sr=22050)
    _, beats = librosa.beat.beat_track(y=m, sr=22050, start_bpm=100, units='time')
    ph = np.median(((np.asarray(beats) + BEAT / 2) % BEAT) - BEAT / 2)      # beats sit at k*0.6 + ph
    shift = -ph                                                              # the nearer way (|shift| <= 0.3 s): delay, or trim the start
    n = int(round(shift * sr)); y = (np.pad(y, ((0, 0), (n, 0))) if n >= 0 else y[:, -n:])
    if CUT:                                                                  # drop two bars on the bar line, 60 ms equal-power cross-fade
        a, b, k = int(CUT[0] * sr), int(CUT[1] * sr), int(0.03 * sr); w = np.sin(np.linspace(0, np.pi / 2, 2 * k))
        y = np.concatenate([y[:, :a - k], y[:, a - k:a + k] * w[::-1] + y[:, b - k:b + k] * w, y[:, b + k:]], axis=1)
    y = y[:, :int(dur * sr)]
    if y.shape[1] < int(dur * sr): y = np.pad(y, ((0, 0), (0, int(dur * sr) - y.shape[1])))
    t = np.arange(y.shape[1]) / sr
    g = np.zeros_like(t)
    for a, b, db in SECTIONS:
        w = np.clip((t - a) / 0.3 + 0.5, 0, 1) * np.clip((b - t) / 0.3 + 0.5, 0, 1); g = np.where(w > 0, db * w + g * (1 - w), g)
    gain = 10 ** (g / 20)
    fi = np.clip(t / 0.05, 0, 1)                                            # click-free start after the pad
    p0, p1 = PAUSE; gate = np.clip(np.maximum((p0 - t) / 0.025, (t - p1) / 0.025), 0, 1)
    fo = np.clip((dur - t) / 2.5, 0, 1) ** 1.5                              # fade over the end card
    y = y * gain * fi * gate * fo
    lufs = pyln.Meter(sr).integrated_loudness(y.T)
    y = loud(y, sr, -14.0, pre)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', pre + '.wav', '-c:a', 'libmp3lame', '-b:a', '192k', pre + '.mp3'], check=True)
    print(f'{src}: beat phase {ph:+.3f}s -> shifted {shift:+.3f}s; LUFS {lufs:.1f} -> {pyln.Meter(sr).integrated_loudness(y.T):.1f}; peak {20 * np.log10(np.max(np.abs(y))):.1f} dBFS -> {pre}.wav/.mp3')


if __name__ == '__main__':
    main()
