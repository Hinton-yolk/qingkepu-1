"""光互连 02 下集 · 桌面演示版：配乐和音效（代码合成）。沿用系列的音色（柔和的铺底、木质拨弦、玻璃琶音），这一集换成 D 小调。
画面上的声音（鼓 = 黑白交界过窄缝，啪 = 盖点，嗒 = 摆到左头，印带器、切刀、盒子落下）都读 film.py 写出的事件，卡在动作上。
结构：开头（提示音 + 乱码的碎响）→ 讲解（拨弦 + 装置自己的声音）→ y5 只留鼓 → y6 发光段玻璃琶音，长黑带上只剩五下「啪」→
代价段换成跳动的低音，嗡声随修字盒升高 → y12 光流前收紧，切手机前停半拍 → 揭晓换成大调的进行 → 收尾。
用法：python3 score.py <锚点目录> <配音轨.wav> <输出目录>   → music.wav、sfx.wav、mix.wav（配音 + 配乐 + 音效，-14 LUFS 由 ffmpeg 再走一遍）"""
import sys, os, json, wave
import numpy as np
from scipy.signal import butter, lfilter

HERE = os.path.dirname(os.path.abspath(__file__))
ANCH, VO, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
SR, FPS, DUR = 48000, 24, 81.75
N = int(SR * (DUR + 1.5))
mus, fx = np.zeros((2, N)), np.zeros((2, N))
rs = np.random.default_rng(7)
# (镜头, 镜头内起帧, 止帧, 全片起帧)
SEGS = [("y1", 0, 59, 0), ("y2", 0, 101, 60), ("y3d", 0, 35, 162), ("s34a", 0, 89, 198), ("s34b", 90, 186, 288), ("y4d", 0, 40, 385),
        ("s34c", 228, 257, 426), ("y5", 0, 119, 456), ("y6g", 0, 95, 576), ("y6c", 96, 269, 672), ("y7", 0, 113, 846), ("y8d", 0, 70, 960),
        ("y8c", 0, 84, 1031), ("y9e", 0, 93, 1116), ("s9a", 0, 61, 1210), ("s9b", 62, 373, 1272), ("y12c", 0, 30, 1584), ("y12g", 0, 54, 1615),
        ("y12a", 0, 75, 1670), ("y13", 0, 119, 1746), ("y14", 0, 95, 1866)]
G0 = {s: g - fs for s, fs, fe, g in SEGS}          # 镜头内第 f 帧 → 全片第 G0[s] + f 帧
EV = {s: json.load(open(os.path.join(ANCH, s + ".json")))["events"] for s, *_ in SEGS}


def sec(shot, f): return (G0[shot] + f) / FPS


def add(buf, sig, t, g=1.0, pan=0.0):
    i0 = int(round(t * SR)); l, r = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
    if i0 >= N or i0 + len(sig) <= 0: return
    a, b = max(0, i0), min(N, i0 + len(sig)); s = sig[a - i0:b - i0]
    buf[0, a:b] += s * g * l; buf[1, a:b] += s * g * r


def T(d): return np.arange(int(d * SR)) / SR
def lp(x, fc, o=2): b, a = butter(o, min(fc, SR / 2 - 100) / (SR / 2)); return lfilter(b, a, x)
def hp(x, fc, o=2): b, a = butter(o, fc / (SR / 2), "high"); return lfilter(b, a, x)
def bp(x, lo, hi, o=2): b, a = butter(o, [lo / (SR / 2), min(hi, SR / 2 - 200) / (SR / 2)], "band"); return lfilter(b, a, x)
def midi(m): return 440 * 2 ** ((m - 69) / 12)
def saw(f, t): return 2 * ((f * t) % 1) - 1


def fade(x, a=0.01, b=0.05):
    ka, kb = int(a * SR), int(b * SR); x = x.copy()
    if ka: x[:ka] *= np.linspace(0, 1, ka)
    if kb: x[-kb:] *= np.linspace(1, 0, kb)
    return x


# ---------- 音色 ----------
def pad(notes, d, fc):
    t = T(d); x = sum(np.sin(2 * np.pi * midi(m) * (1 + dt) * t) + 0.25 * saw(midi(m) * (1 + dt), t) for m in notes for dt in (-0.003, 0.003)) / (2 * len(notes))
    return fade(lp(x, fc), 0.35, 0.5)


def pluck(m, d=0.5):                     # 木质拨弦
    t = T(d); f = midi(m)
    x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 14) + 0.12 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t * 22)) * np.exp(-t * 7.5)
    x[:int(0.004 * SR)] += bp(rs.standard_normal(int(0.004 * SR)), 1500, 5000) * 0.5
    return fade(x, 0.002, 0.05)


def glass(m, d=0.7):                     # 玻璃琶音
    t = T(d); f = midi(m)
    return fade((np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2.76 * f * t) * np.exp(-t * 9) + 0.15 * np.sin(2 * np.pi * 5.4 * f * t) * np.exp(-t * 16)) * np.exp(-t * 5.5), 0.002, 0.05)


def bass(m, d=0.22):
    t = T(d); f = midi(m); return fade(lp(saw(f, t) * 0.6 + np.sin(2 * np.pi * f * t), 420) * np.exp(-t * 9), 0.004, 0.03)


t_ = T(0.24); DRUM = (np.sin(2 * np.pi * (62 * t_ + 60 * (1 - np.exp(-t_ * 30)) / 30)) * np.exp(-t_ * 14) + 0.25 * bp(rs.standard_normal(len(t_)), 200, 900) * np.exp(-t_ * 60))
t_ = T(0.09); CLAP = fade(bp(rs.standard_normal(len(t_)), 900, 3800) * np.exp(-t_ * 60) + 0.5 * np.sin(2 * np.pi * 620 * t_) * np.exp(-t_ * 70), 0.001, 0.02)
t_ = T(0.04); TICK = fade(np.sin(2 * np.pi * 1750 * t_) * np.exp(-t_ * 160) + 0.3 * np.sin(2 * np.pi * 2900 * t_) * np.exp(-t_ * 220), 0.0005, 0.01)
t_ = T(0.12); THUNK = fade(np.sin(2 * np.pi * 130 * t_) * np.exp(-t_ * 40) + 0.35 * bp(rs.standard_normal(len(t_)), 300, 1500) * np.exp(-t_ * 80), 0.001, 0.02)
t_ = T(0.35); THUD = fade(np.sin(2 * np.pi * (58 * t_ + 30 * (1 - np.exp(-t_ * 25)) / 25)) * np.exp(-t_ * 11) + 0.3 * bp(rs.standard_normal(len(t_)), 150, 700) * np.exp(-t_ * 35), 0.001, 0.05)
t_ = T(0.10); SNIP = fade(hp(rs.standard_normal(len(t_)), 3000) * np.exp(-t_ * 70) + 0.4 * np.sin(2 * np.pi * 3300 * t_) * np.exp(-t_ * 45), 0.0005, 0.02)
t_ = T(0.5); ERR = fade((np.sin(2 * np.pi * midi(46) * t_) + np.sin(2 * np.pi * midi(47) * t_)) * 0.5 * np.exp(-t_ * 5), 0.01, 0.1)        # 低低的错音（小二度）
t_ = T(0.25); FLIP = fade(bp(rs.standard_normal(len(t_)), 600, 2500) * np.sin(np.pi * t_ / 0.25) ** 2 * 0.5 + np.sin(2 * np.pi * 900 * t_) * np.exp(-((t_ - 0.21) * 90) ** 2) * 0.8, 0.01, 0.02)


def bell(m, d=0.5): t = T(d); f = midi(m); return fade((np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 3.0 * f * t) * np.exp(-t * 12)) * np.exp(-t * 8), 0.001, 0.05)


# ---------- 装置自己的声音（读事件） ----------
LOUD = {"s34a": (0, 90), "s34b": (90, 100), "y6c": (146, 234)}          # 要观众数的「啪」
QUIET_SHOTS = {"y1": 0.0, "y12a": 0.0, "y14": 0.0, "y9e": 0.35, "y6g": 0.6, "y12g": 0.5}
SENDER = {"y2", "y3d", "y4d", "y8d"}
for shot, fs, fe, g0 in SEGS:
    ev = EV[shot]; k = QUIET_SHOTS.get(shot, 1.0)
    if k == 0: continue
    y2_recv = shot == "y2"                                               # y2 后半镜头到了读带口：读带口的声音渐入
    stamps = [s_ for s_ in ev["stamps"]]
    for f, wd, gain in ev["edges"]:
        if not fs <= f <= fe: continue
        if shot in SENDER and not (y2_recv and f > 70): continue
        add(fx, DRUM, sec(shot, f), 0.55 * k * gain * min(1.0, wd / 20) ** 0.6, -0.1)
        if shot in ("y6g", "y12g"): add(fx, bell(86 if wd > 8 else 91, 0.3), sec(shot, f), 0.10 * min(1.0, wd / 12), 0.25)      # 引脚上金色闪一下
    for i, (f, solid, per) in enumerate(stamps):
        if not fs <= f <= fe: continue
        if shot in SENDER and not (y2_recv and f > 70): continue
        loud = shot in LOUD and LOUD[shot][0] <= f < LOUD[shot][1]
        add(fx, CLAP, sec(shot, f), (0.50 if loud else 0.10) * k * min(1.0, per / 20) ** 0.8, 0.12)
        if i + 1 < len(stamps):                                          # 半个周期后摆到左头：很轻的「嗒」
            fl = (f + stamps[i + 1][0]) / 2
            if fs <= fl <= fe: add(fx, TICK, sec(shot, fl), 0.16 * k * min(1.0, per / 20), -0.25)
    for f, wd in ev["press"]:
        if fs <= f <= fe and (shot in SENDER and not (y2_recv and f > 60)): add(fx, THUNK, sec(shot, f), 0.30 * min(1.0, wd / 20), -0.35)
# 其它动作
add(fx, ERR, sec("s34b", 104), 0.30)                                     # y4：停在 4，数错了
add(fx, THUNK, sec("s34b", 132), 0.20, 0.2)                              # 尺子落下
add(fx, THUD, sec("y4d", 11), 0.45, -0.2)                                # 挡片落下
add(fx, FLIP, sec("y6g", 10), 0.30, 0.3)                                 # 纸签翻面
add(fx, ERR, sec("y7", 104), 0.30)                                       # y7：滑过格边，少数一个
add(fx, THUD, sec("y9e", 69), 0.35)                                      # 「整套 = SerDes」落下
for f in (62 + 95, 62 + 125, 62 + 144): add(fx, THUD, sec("s9b", f), 0.55)       # 三只修字盒：咚
for k_ in range(5): add(fx, SNIP, sec("y13", 28.33 + 20 * k_), 0.22 if k_ < 3 else 0.42, 0.3)   # 切刀：一格切一段
add(fx, THUNK, sec("y14", 16), 0.30, -0.1)                               # 路线图小卡落下
# 手机：提示音；乱码蔓延的碎响；变回来时一个字一声
add(fx, bell(81, 0.5), 0.02, 0.30); add(fx, bell(86, 0.6), 0.14, 0.30)
for i in range(7):
    for j in range(3): add(fx, fade(bp(rs.standard_normal(int(0.02 * SR)), 2000, 7000), 0.001, 0.008), (i * 4.5 + j * 3) / FPS + 0.05, 0.10, rs.uniform(-0.5, 0.5))
for i in range(2, 9): add(fx, bell([74, 77, 81, 82, 86, 89, 93][i - 2], 0.5), sec("y12a", 8 + (i - 2) * 7), 0.16, (i - 5) / 8)
# 修字盒的嗡声：每落一只高一点、响一点（y10 3.95 秒起），y12 切手机时收掉
h0, h1 = sec("s9b", 157), sec("y12a", 0)
t = np.arange(int((h1 - h0) * SR)) / SR
lvl = 0.35 + 0.3 * (t > sec("s9b", 187) - h0) + 0.35 * (t > sec("s9b", 206) - h0); lvl = lp(lvl, 4)
hum = (np.sin(2 * np.pi * 100 * t) + 0.5 * np.sin(2 * np.pi * 200 * t) + 0.25 * np.sin(2 * np.pi * 300 * t + 1)) * lvl
add(fx, fade(hum, 0.3, 0.25), h0, 0.035)

# ---------- 配乐：D 小调；讲解 Dm–C–B♭–C，代价段 Gm–Dm–B♭–A，揭晓 F–C–Dm–B♭，结尾落 F ----------
BEAT = 20 / FPS                                                          # 一拍 = 纸带上一格（0.833 秒，72 拍 / 分）
CH = {"Dm": [50, 57, 62, 65], "C": [48, 55, 60, 64], "Bb": [46, 53, 58, 62], "Gm": [43, 55, 58, 62], "A": [45, 57, 61, 64], "F": [41, 53, 57, 60], "Fadd9": [41, 53, 57, 60, 67]}
T_Y2, T_Y5, T_Y6, T_Y6C, T_Y7, T_Y8, T_Y9, T_Y12, T_PHONE, T_Y13, T_Y14 = 2.5, 19.0, 24.0, 28.0, 35.25, 40.0, 46.5, 66.0, 69.58, 72.75, 77.75


def section(t0, t1, prog, texture, g=1.0):
    bar = 4 * BEAT; nb = int(np.ceil((t1 - t0) / bar))
    for b in range(nb):
        ch = CH[prog[b % len(prog)]]; tb = t0 + b * bar; d = min(bar, t1 - tb)
        if d <= 0.2: continue
        add(mus, pad(ch, d + 0.4, 900 if texture != "glass" else 1700), tb - 0.05, 0.085 * g, -0.3)
        add(mus, pad(ch, d + 0.4, 800 if texture != "glass" else 1500), tb - 0.04, 0.07 * g, 0.3)
        for s in range(16):                                              # 十六分音符的格子
            ts = tb + s * BEAT / 4
            if ts >= t1 - 0.05: break
            if texture == "pluck" and s % 4 in (0, 2) and not (s % 8 == 6):
                add(mus, pluck(ch[[1, 2, 3, 2, 1, 3, 2, 1][(s // 2) % 8]] + 12), ts, 0.13 * g, 0.2 if s % 4 else -0.2)
            if texture == "glass":
                add(mus, glass(ch[[1, 2, 3, 2][s % 4]] + 24 + (12 if s % 8 == 7 else 0), 0.5), ts, 0.055 * g, np.sin(s) * 0.5)
            if texture == "pulse" and s % 2 == 0:
                add(mus, bass(ch[0] - 12 if s % 8 else ch[0]), ts, 0.16 * g)
                if s % 4 == 2: add(mus, pluck(ch[[2, 3, 1, 3][(s // 4) % 4]] + 12, 0.3), ts, 0.07 * g, 0.3)
            if texture == "reveal" and s % 2 == 0:
                add(mus, pluck(ch[[1, 3, 2, 3, 1, 2, 3, 2][(s // 2) % 8]] + 12), ts, 0.14 * g, 0.2 if s % 4 else -0.2)
                if s % 8 == 0: add(mus, glass(ch[-1] + 24, 1.2), ts, 0.07 * g)


add(mus, pad(CH["Dm"], 3.2, 600), -0.05, 0.10)                                         # 开头：一口低低的铺底
section(T_Y2, T_Y5, ["Dm", "C", "Bb", "C"], "pluck")                                   # 讲解
section(T_Y5, T_Y6, ["Dm", "Bb"], "none", 0.6)                                         # y5：配乐只留铺底，鼓是装置自己的
section(T_Y6, T_Y6C, ["Bb", "C"], "glass")                                             # y6 发光段：玻璃琶音
add(mus, pad([50, 57], 5.9, 500), T_Y6C, 0.05)                                         # 长黑带：几乎全空，只剩啪
add(mus, pad(CH["Fadd9"], 2.6, 1800), 24.0 + 9.62, 0.13); add(mus, glass(81, 1.5), 24.0 + 9.62, 0.10)     # 「五个，不是四个」
t = T(4.6); drift = np.sin(2 * np.pi * np.cumsum(midi(62) * 2 ** (-0.35 * t / 4.6 / 12)) / SR) * 0.5 + np.sin(2 * np.pi * midi(50) * t) * 0.5
add(mus, fade(lp(drift, 900), 0.4, 0.4), T_Y7, 0.085)                                  # y7：一个慢慢走低的长音（跑偏）
section(T_Y8, T_Y9, ["Dm", "C", "Bb", "C"], "pluck")                                   # y8：鼓点回来
section(T_Y9, 51.9, ["Gm", "Dm"], "pluck", 0.9)                                        # y9 前半
section(51.9, T_Y12, ["Gm", "Dm", "Bb", "A"], "pulse")                                 # 「翻一倍」起：跳动的低音，代价段
section(T_Y12, 69.05, ["Bb", "C"], "glass", 1.15)                                      # y12：收紧
# 69.05–69.58 停半拍
section(T_PHONE, T_Y14, ["F", "C", "Dm", "Bb"], "reveal")                              # 揭晓：换成大调的进行
t = T(4.5); end = sum(np.sin(2 * np.pi * midi(m) * t) for m in CH["F"] + [69, 72]) / 6 * np.exp(-t / 1.9)
add(mus, fade(lp(end, 2400), 0.02, 0.9), T_Y14, 0.20); add(mus, pluck(77, 1.0), T_Y14, 0.12); add(mus, pluck(84, 1.2), T_Y14 + BEAT, 0.10)
k0, k1 = int(69.03 * SR), int(T_PHONE * SR)                                            # 切手机前的半拍：配乐收干净
mus[:, k0:k1] *= np.linspace(1, 0, k1 - k0) ** 3; mus[:, k1 - int(0.3 * SR):k1] *= 0.0

# ---------- 混音：配音在上，配乐在人声下方约 12 dB，说话时再压一点 ----------
w = wave.open(VO); vo = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64) / 32768
if w.getnchannels() == 2: vo = vo.reshape(-1, 2).mean(1)
vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
envl = lp(np.abs(vo), 6); duck = 1 - 0.45 * np.clip(envl / (envl.max() * 0.25), 0, 1)
mus *= duck


def rms_db(x): return 20 * np.log10(np.sqrt(np.mean(x[np.abs(x) > 1e-4] ** 2)) + 1e-9)


gm = 10 ** ((rms_db(vo) - 13 - rms_db(mus.mean(0))) / 20)                               # 配乐的整体电平放到人声下面 13 dB
mus *= gm
mix = np.stack([vo, vo]) * 1.0 + mus + fx * 0.8
mix = np.tanh(mix * 1.5) / 1.5 * 1.2


def save(name, x):
    x = np.clip(x[:, :int(DUR * SR)], -1, 1)
    with wave.open(os.path.join(OUT, name), "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((x.T * 32767).astype(np.int16).tobytes())


save("music.wav", mus); save("sfx.wav", fx); save("mix.wav", mix)
print("ok", "配乐比人声低 %.1f dB" % (rms_db(vo) - rms_db(mus.mean(0))), "音效峰值 %.2f" % np.abs(fx).max())
