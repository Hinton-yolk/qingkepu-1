"""全片合成：各镜头的帧（film.py fs/fe 渲的 <帧目录>/<镜头>/f_####.png）按 timeline 接起来，
加后期、小签、字幕、右上角系列名，配上配音和占位音效（鼓 / 啪 / 嗒 / 印带器），输出 mp4。
用法：python3 comp_film.py <帧目录> <锚点目录> <字体目录> <配音.wav> <输出.mp4> [--only 镜头,镜头] [--step 2] [--audio 成品音轨.wav]
锚点目录：film.py anchors=1 写的 <镜头>.json（屏幕锚点 + 声音事件）。音乐还没做；音效是代码合成的占位音，只用来对动作。"""
import sys, os, json, subprocess, wave
from multiprocessing import Pool
import numpy as np
from PIL import Image
from overlay import Kit, grade

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, ANCH, FONTS, VO, DST = sys.argv[1:6]
ONLY = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
AUDIO = sys.argv[sys.argv.index("--audio") + 1] if "--audio" in sys.argv else None      # 给了就直接用这条成品音轨（配音 + 配乐 + 音效）
STEP = int(sys.argv[sys.argv.index("--step") + 1]) if "--step" in sys.argv else 1     # 草稿隔帧渲的：缺的帧用前一张顶上
FS = {}
FPS = 24
SUBS = json.load(open(os.path.join(HERE, "subs.json"), encoding="utf-8"))
# (镜头, 镜头内起帧, 止帧, 全片起帧)
SEGS = [("y1", 0, 59, 0), ("y2", 0, 101, 60), ("y3d", 0, 35, 162), ("s34a", 0, 89, 198), ("s34b", 90, 186, 288), ("y4d", 0, 40, 385),
        ("s34c", 228, 257, 426), ("y5", 0, 119, 456), ("y6g", 0, 95, 576), ("y6c", 96, 269, 672), ("y7", 0, 113, 846), ("y8d", 0, 70, 960),
        ("y8c", 0, 84, 1031), ("y9e", 0, 93, 1116), ("s9a", 0, 61, 1210), ("s9b", 62, 373, 1272), ("y12c", 0, 30, 1584), ("y12g", 0, 54, 1615),
        ("y12a", 0, 75, 1670), ("y13", 0, 119, 1746), ("y14", 0, 95, 1866)]
TOTAL = 1962
# 小签：镜头 → [(起帧, 止帧, 锚点, 文字, 签的哪个角对着锚点, (dx, dy), 大字?)]
TAGS = {
    "y1": [(0, 60, "phone_top", "芯片怎么数清 0 和 1？", "mb", (0, -10), True)],
    "y2": [(4, 36, "tray", "一排", "mt", (0, 215), False), (62, 102, "tape_mid", "排成一列", "mt", (0, 50), False)],
    "y3d": [(6, 36, "prn_out", "黑 = 1　白 = 0", "lt", (-40, 60), False)],
    "s34a": [(4, 90, "dot1", "数一个", "mt", (0, 60), False)],
    "s34b": [(90, 138, "dot1", "数一个", "mt", (0, 60), False), (140, 187, "ruler", "一格多长 = 节拍", "mt", (0, 70), False)],   # 尺子 132 帧落稳，签跟着出（全片最要紧的一张签，留够 1.9 秒）
    "y5": [(20, 118, "lamp", "鼓点", "lt", (30, 60), False)],
    "y6g": [(30, 94, "pin", "信号跳一下", "rb", (-30, -70), False)],
    "s9a": [(12, 62, "dot", "每条通道：快一倍", "mt", (0, 70), False)],
    "y12g": [(8, 55, "pin", "一条通道 · 上千亿 / 秒", "rb", (-30, -70), False)],
    "y13": [(28, 56, "tape_mid", "排成一列", "mt", (0, 50), False), (58, 78, "metro", "听准节拍", "lt", (40, 40), False), (98, 120, "tray_r", "拆回一排", "mt", (0, 70), False)],
}
NOTES = {"s34a": (0, 90, "示意：只画两种电平")}       # 全片唯一的角注
LOUD = {"s34a": (0, 90), "s34b": (90, 100), "y6c": (146, 234)}     # 要观众数的「啪」：y3–y4 的四下、y6 长黑带上的五下；其余都压低


def fade(f, f0, f1, n=5, hard_in=False):
    """小签淡入淡出各 n 帧。hard_in：不淡入（全片第一帧的大字问题必须一上来就在）。"""
    return max(0.0, min(1.0, 1.0 if hard_in else (f - f0 + 1) / n, (f1 - f) / n)) if f >= f0 else 0.0


def sub_at(t):
    for a, b, txt in SUBS:                                # 正在说的那一句优先
        if a <= t < b: return txt
    for a, b, txt in SUBS:                                # 句间的空隙里，上一句多留 0.12 秒，免得字幕一闪一闪
        if b <= t < b + 0.12: return txt
    return ""


def frame_job(job):
    shot, f, g = job
    fr = f - (f - FS[shot]) % STEP
    p = os.path.join(SRC, shot, f"f_{fr:04d}.png")
    im = grade(Image.open(p), seed=g)
    kit = Kit(FONTS, im.size[0]); s = kit.s
    A = ANC[shot]["pts"][f]
    for f0, f1, anc, text, corner, (dx, dy), big in TAGS.get(shot, []):
        a = fade(f, f0, f1, hard_in=(shot == "y1" and f0 == 0))
        if a > 0:
            ax, ay = A[anc][0] * kit.W, A[anc][1] * kit.H
            kit.tag(im, (ax + dx * s, ay + dy * s), text, alpha=a, anchor=corner, big=big, line_to=None if big else (ax, ay))
    if shot in NOTES and NOTES[shot][0] <= f < NOTES[shot][1]: kit.note(im, NOTES[shot][2])
    kit.chrome(im)
    kit.subtitle(im, sub_at(g / FPS))
    return im.convert("RGB").tobytes()


ANC = {}
segs = [s_ for s_ in SEGS if not ONLY or s_[0] in ONLY]
for shot, fs_, *_ in segs: ANC[shot] = json.load(open(os.path.join(ANCH, shot + ".json"))); FS[shot] = fs_

if __name__ == "__main__":
    jobs = [(shot, f, g0 + (f - fs)) for shot, fs, fe, g0 in segs for f in range(fs, fe + 1)]
    g_first = jobs[0][2]
    W, H = Image.open(os.path.join(SRC, jobs[0][0], f"f_{jobs[0][1]:04d}.png")).size
    # ---- 声音：配音 + 占位音效 ----
    SR = 48000
    n = int(SR * (len(jobs) / FPS)) + SR
    aud = np.zeros(n, np.float32)
    w = wave.open(VO); vo = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32) / 32768
    if w.getnchannels() == 2: vo = vo.reshape(-1, 2).mean(1)
    assert w.getframerate() == SR
    a0 = int(g_first / FPS * SR); seg = vo[a0:a0 + n]; aud[:len(seg)] += seg * 1.6

    def hit(t0, sig, gain):
        i = int(t0 * SR)
        if 0 <= i < n: m = min(len(sig), n - i); aud[i:i + m] += gain * sig[:m]
    t = np.arange(int(0.22 * SR)) / SR
    drum = np.sin(2 * np.pi * (70 * t + 55 * (1 - np.exp(-t * 28)) / 28)) * np.exp(-t * 16)
    rng = np.random.default_rng(1); t2 = np.arange(int(0.07 * SR)) / SR
    clap = rng.normal(0, 1, len(t2)) * np.exp(-t2 * 75) + 0.6 * np.sin(2 * np.pi * 1900 * t2) * np.exp(-t2 * 110)
    t4 = np.arange(int(0.09 * SR)) / SR
    thunk = np.sin(2 * np.pi * 140 * t4) * np.exp(-t4 * 45) + 0.3 * rng.normal(0, 1, len(t4)) * np.exp(-t4 * 90)
    for shot, fs, fe, g0 in segs:
        ev = ANC[shot].get("events", {})
        if shot in ("y1", "y12a", "y14", "y9e"): continue                      # 手机镜头和全景里不放装置的声音
        sender = shot in ("y2", "y3d", "y4d", "y8d")
        for f, wd, gain in ev.get("edges", []):
            if fs <= f <= fe and not sender: hit((g0 + f - fs - g_first) / FPS, drum, 0.5 * gain * min(1.0, wd / 20) ** 0.5)
        for f, solid, per in ev.get("stamps", []):
            if fs <= f <= fe and not sender:
                loud = shot in LOUD and LOUD[shot][0] <= f < LOUD[shot][1]
                hit((g0 + f - fs - g_first) / FPS, clap, (0.30 if loud else 0.07) * min(1.0, per / 20))
        for f, wd in ev.get("press", []):
            if fs <= f <= fe and sender: hit((g0 + f - fs - g_first) / FPS, thunk, 0.25 * min(1.0, wd / 20))
    aud = np.clip(aud, -1, 1)
    wav = DST.replace(".mp4", ".wav")
    with wave.open(wav, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((aud * 32767).astype(np.int16).tobytes())
    if AUDIO: wav = AUDIO
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "slow", "-c:a", "aac", "-b:a", "192k", "-shortest", DST], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for buf in pool.imap(frame_job, jobs, chunksize=8): ff.stdin.write(buf)
    ff.stdin.close(); ff.wait()
    print("ok", DST, len(jobs), "frames")
