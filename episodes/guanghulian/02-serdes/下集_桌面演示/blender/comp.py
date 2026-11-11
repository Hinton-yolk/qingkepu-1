"""y6 试镜头的合成：后期（高光晕、暗角、颗粒，和 blender_desk_look/post.py 同一套参数，颗粒逐帧换）
+ 字幕 + 两张小签 + 占位声音（鼓 / 啪 / 嗒），输出 mp4。
用法：python3 comp.py <帧目录> <anchors.json> <字体目录> <输出.mp4> [--no-text] [--glow]
--glow：发光信号那一段（rig.py glow=1 渲的帧，只有前 4 秒）：小签贴在小灯和芯片引脚旁，加角注。
字幕时间是估的（这台机器上没有配音文件），只用来对动作；声音是代码合成的占位音。"""
import sys, os, json, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC, ANCH, FONTS, DST = sys.argv[1:5]
TEXT = "--no-text" not in sys.argv
GLOW = "--glow" in sys.argv
A = json.load(open(ANCH)); FPS = A["fps"]
files = sorted(f for f in os.listdir(SRC) if f.startswith("f_") and f.endswith(".png"))
NF = len(files)
TB = 20
SUBS = [(0.0, 1.25, "芯片也一样："), (1.25, 3.3, "信号每跳一下，就是一个鼓点。"), (3.3, 5.0, "它跟着鼓点校准自己，"),
        (5.0, 7.05, "再按节拍一个一个清点："), (7.05, 8.9, "五个，不是四个。")]
SUBS = [x for x in SUBS if x[0] < NF / FPS - 0.3]
EDGES = [f for f in (0, 20, 40, 60, 80, 180) if f < NF]   # 黑白交界过窄缝（鼓）
STAMPS = list(range(10, NF, TB))                 # 盖点（啪）
TICKS = list(range(0, NF, TB))                   # 摆到左头（嗒）


def blur(x, sigma):
    r = int(sigma * 3) | 1
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2); k /= k.sum()
    for ax in (0, 1):
        pad = [(0, 0)] * x.ndim; pad[ax] = (r, r)
        xp = np.pad(x, pad, mode="edge"); out = np.zeros_like(x)
        for i, w in enumerate(k):
            sl = [slice(None)] * x.ndim; sl[ax] = slice(i, i + x.shape[ax])
            out += w * xp[tuple(sl)]
        x = out
    return x


def grade(a, seed):
    H, W, _ = a.shape
    lin = a ** 2.2
    lum = lin @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    hi = np.clip((lum - 0.62) / 0.38, 0, 1)[..., None] * lin
    lin = lin + 0.22 * blur(hi, W * 0.006) * np.array([1.0, 0.42, 0.18], np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r2 = ((xx - W / 2) / (W / 2)) ** 2 * 0.55 + ((yy - H / 2) / (H / 2)) ** 2 * 0.75
    lin *= (1 - 0.14 * np.clip(r2 / 1.3, 0, 1) ** 1.5)[..., None]
    out = np.clip(lin, 0, 1) ** (1 / 2.2)
    g = blur(np.random.default_rng(seed).normal(0, 1, (H, W)).astype(np.float32), 0.6); g /= g.std()
    l2 = out @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    out += (0.012 * g * (0.35 + 1.3 * l2 * (1 - l2) * 2))[..., None]
    return np.clip(out, 0, 1)


def fade(f, f0, f1, n=6):
    return max(0.0, min(1.0, (f - f0) / n, (f1 - f) / n))


def tag(im, xy, lines, alpha, s, font, anchor="lb"):
    """一张小纸签：米色底、深色字、细边。xy 是签的一个角（lb = 左下角）。"""
    if alpha <= 0: return
    d = ImageDraw.Draw(im)
    pad = int(9 * s); gap = int(5 * s)
    sizes = [d.textbbox((0, 0), t, font=font) for t in lines]
    w = max(b[2] - b[0] for b in sizes) + 2 * pad
    h = sum(b[3] - b[1] for b in sizes) + gap * (len(lines) - 1) + 2 * pad
    x, y = xy
    if "r" in anchor: x -= w
    if "b" in anchor: y -= h
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rectangle([x + 2 * s, y + 3 * s, x + w + 2 * s, y + h + 3 * s], fill=(0, 0, 0, int(70 * alpha)))
    ld.rectangle([x, y, x + w, y + h], fill=(238, 231, 214, int(255 * alpha)), outline=(110, 102, 90, int(255 * alpha)))
    cy = y + pad
    for t, b in zip(lines, sizes):
        ld.text((x + pad - b[0], cy - b[1]), t, font=font, fill=(26, 24, 22, int(255 * alpha)))
        cy += b[3] - b[1] + gap
    im.alpha_composite(lay)


assert all(name == f"f_{i:04d}.png" for i, name in enumerate(files)), "帧不连续"
W, H = Image.open(os.path.join(SRC, files[0])).size
s = W / 1080
f_tag = ImageFont.truetype(f"{FONTS}/NotoSansSC-Bold.otf", int(46 * s))
f_sub = ImageFont.truetype(f"{FONTS}/NotoSansSC-Bold.otf", int(54 * s))
f_note = ImageFont.truetype(f"{FONTS}/NotoSansSC-Bold.otf", int(30 * s))

# ---- 占位声音：鼓（交界）、啪（盖点）、嗒（左头，很轻）----
SR = 48000
aud = np.zeros(int(SR * NF / FPS) + SR // 2, np.float32)


def hit(t0, sig, gain):
    i = int(t0 * SR); n = min(len(sig), len(aud) - i); aud[i:i + n] += gain * sig[:n]


t = np.arange(int(0.22 * SR)) / SR
drum = np.sin(2 * np.pi * (70 * t + 55 * (1 - np.exp(-t * 28)) / 28)) * np.exp(-t * 16)
rng = np.random.default_rng(1)
t2 = np.arange(int(0.07 * SR)) / SR
clap = (rng.normal(0, 1, len(t2)) * np.exp(-t2 * 75) + 0.6 * np.sin(2 * np.pi * 1900 * t2) * np.exp(-t2 * 110))
t3 = np.arange(int(0.03 * SR)) / SR
tick = np.sin(2 * np.pi * 2600 * t3) * np.exp(-t3 * 260)
for f in EDGES: hit(f / FPS, drum, 0.8)
for f in STAMPS: hit(f / FPS, clap, 0.32 if f <= 170 else 0.10)   # 出长黑带以后的「啪」压低，五下才数得清
for f in TICKS: hit(f / FPS, tick, 0.06)
aud = np.clip(aud, -1, 1)
wav = DST.replace(".mp4", ".wav")
with wave.open(wav, "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((aud * 32767).astype(np.int16).tobytes())

ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-c:a", "aac", "-b:a", "128k", "-shortest", DST],
                      stdin=subprocess.PIPE)
P = A["pts"]
for f, name in enumerate(files):
    a = np.asarray(Image.open(os.path.join(SRC, name)).convert("RGB")).astype(np.float32) / 255
    im = Image.fromarray((grade(a, 100 + f) * 255 + 0.5).astype(np.uint8)).convert("RGBA")
    if TEXT and GLOW:
        lx, ly = P["lamp"][f][0] * W, P["lamp"][f][1] * H
        px_, py_ = P["pin"][f][0] * W, P["pin"][f][1] * H
        # 同屏小签最多 2 张：实物纸签算一张，这里只留引脚旁这一张（审核 11-11）
        tag(im, (px_ + 10 * s, py_ + 50 * s), ["信号跳一下"], fade(f, 30, NF - 4), s, f_tag, "rt")
        # 不加「示意」角注（用户 11-11：「示意不需要加了，本来就是为了示范，大家的常识不会觉得电信号会发光」）
    if TEXT and not GLOW:
        lx, ly = P["lamp"][f][0] * W, P["lamp"][f][1] * H
        # 「鼓点」从 y5 留下来；「= 信号跳一下」在说到这半句时出现，长黑带进来前一起淡掉
        a1 = fade(f, -10, 74); a2 = fade(f, 30, 74)
        if a1 > 0:
            # 小签放在纸带下方的桌面上（上方是计数器和纸签，不能挡），一根细线连到小灯
            if a1 > 0.5:
                ImageDraw.Draw(im).line([(lx, ly + 10 * s), (lx + 16 * s, ly + 52 * s)], fill=(238, 231, 214, 255), width=max(1, int(3 * s)))
            tag(im, (lx - 10 * s, ly + 50 * s), ["鼓点", "= 信号跳一下"] if a2 > 0.5 else ["鼓点"], a1, s, f_tag, "lt")   # 下沿不超过 y = 1320
        a3 = fade(f, 176, 10 ** 6)
        if a3 > 0:
            bx = (P["band_l"][f][0] + P["band_r"][f][0]) / 2 * W; by = P["band_l"][f][1] * H
            tag(im, (bx - 150 * s, by + 36 * s), ["五个，不是四个"], a3, s, f_tag, "lt")
    if TEXT:
        tsec = f / FPS
        for t0, t1, txt in SUBS:
            if t0 <= tsec < t1:
                d = ImageDraw.Draw(im); b = d.textbbox((0, 0), txt, font=f_sub)
                x, y = (W - (b[2] - b[0])) / 2 - b[0], H * 0.735
                d.text((x, y), txt, font=f_sub, fill=(255, 255, 255, 255), stroke_width=max(2, int(5 * s)), stroke_fill=(20, 20, 20, 255))
    ff.stdin.write(im.convert("RGB").tobytes())
ff.stdin.close(); ff.wait()
print("ok", DST)
