# 硅光波导测试镜头 · 合成：Blender 画面（显卡电脑渲出的 waveguide.mp4 + anchors.json）→ 叠 2D 字 + 合成音乐/音效 → 成片
# 用法：python3 composite_waveguide.py <目录（含 anchors.json，和 waveguide.mp4 或 f####.png 帧）> <输出 mp4>
#       python3 composite_waveguide.py <目录> --stills     只合成目录里已有的几帧（看排版用，不出视频）
#       python3 composite_waveguide.py <目录> --audio      只合成配乐 score.wav
import sys, json, os, subprocess, math, glob, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC = sys.argv[1]; STILLS = '--stills' in sys.argv; OUT = None if (STILLS or '--audio' in sys.argv) else sys.argv[2]
W, H = 1080, 1920
A = json.load(open(os.path.join(SRC, 'anchors.json'))); FPS, NF, RW, T, AF = A['fps'], A['nf'], A['w'], A['times'], A['frames']
if os.path.exists(os.path.join(SRC, 'waveguide.mp4')) and not os.path.exists(os.path.join(SRC, 'f0001.png')):   # 显卡电脑出的视频：先拆帧
    subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-i', os.path.join(SRC, 'waveguide.mp4'), '-start_number', '1', os.path.join(SRC, 'f%04d.png')], check=True)
K = W / RW
# 系列配色：金 = 电，青 = 光，珊瑚 = 强调
GOLD, CYAN, CORAL, INK, CREAM = (232, 182, 72), (64, 214, 196), (236, 98, 80), (18, 20, 26), (246, 241, 230)
NOTO = '/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc'                       # 思源黑体 SC（和系列的 Noto Sans SC 同一字形；带 µ）
def font(size, heavy=True): return ImageFont.truetype(NOTO.format('Black' if heavy else 'Bold'), size, index=2)
def layer(): return Image.new('RGBA', (W, H), (0, 0, 0, 0))   # PIL 在 RGBA 上直接画会覆盖透明度而不是混合：半透明的东西画在单独一层再叠
def clamp(x): return max(0.0, min(1.0, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(k): s = 1.7; k -= 1; return k * k * ((s + 1) * k + s) + 1

def tag(base, text, x, y, size, bg, fg, t, t0, t1=99, anchor=None):
    """圆角标签：弹出 + 逐字出现；anchor 给出时画引线到实物上的点；t1 之后收起"""
    if t < t0 or t >= t1 + 0.2: return
    out = clamp((t - t1) / 0.2)
    k = clamp((t - t0) / 0.25); n = max(1, math.ceil(len(text) * k)); sc = (0.85 + 0.15 * back(clamp((t - t0) / 0.18))) * (1 - 0.3 * out)
    ft = font(size); tw = ft.getlength(text); pw, ph = int(tw + size * 0.9), int(size * 1.55)
    lay = Image.new('RGBA', (pw + 40, ph + 40), (0, 0, 0, 0))
    sh = Image.new('RGBA', lay.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([20, 26, 20 + pw, 26 + ph], radius=size * 0.28, fill=(0, 0, 0, 120)); sh = sh.filter(ImageFilter.GaussianBlur(8))
    lay = Image.alpha_composite(sh, lay); d = ImageDraw.Draw(lay); d.rounded_rectangle([20, 20, 20 + pw, 20 + ph], radius=size * 0.28, fill=bg)
    d.text((20 + size * 0.45, 20 + ph / 2 + 1), text[:n], font=ft, fill=fg, anchor='lm')
    lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.LANCZOS)
    if out > 0: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * (1 - out))))
    x = min(max(x, lay.width / 2 + 24), W - lay.width / 2 - 24)
    if anchor and out < 1:
        ly = layer(); dl = ImageDraw.Draw(ly); kk = clamp((t - t0) / 0.3); ax, ay = anchor; ex, ey = ax + (x - ax) * kk, ay + (y - ay) * kk
        dl.line([ax, ay, ex, ey], fill=bg[:3] + (int(255 * (1 - out)),), width=5); dl.ellipse([ax - 8, ay - 8, ax + 8, ay + 8], fill=bg[:3] + (int(255 * (1 - out)),)); base.alpha_composite(ly)
    base.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))

STEPS = [('涂胶', T['coat0'] - 0.4), ('曝光', T['mask0']), ('显影', T['dev0']), ('刻蚀', T['etch0']), ('去胶', T['strip0']), ('导光', T['light0'] - 0.6)]
def process_bar(im, t):
    """顶部工序条：当前一步填色（导光用青色），做过的变暗，没到的只有描边"""
    if t < 0.5: return
    k = ease((t - 0.5) / 0.4); ly = layer(); d = ImageDraw.Draw(ly); ft = font(34, heavy=False)
    cur = max(i for i, (_, s) in enumerate(STEPS) if t >= s) if t >= STEPS[0][1] else -1
    cw, gap = 138, 14; x0 = W / 2 - (6 * cw + 5 * gap) / 2; y = 214 - 30 * (1 - k)
    for i, (name, s) in enumerate(STEPS):
        x = x0 + i * (cw + gap); a = int(255 * k); box = [x, y - 30, x + cw, y + 30]
        if i == cur:
            col = CYAN if name == '导光' else CORAL; pk = 1 + 0.08 * (1 - ease((t - s) / 0.25))   # 切到这一步时轻轻一跳
            cx, cy = x + cw / 2, y; hw, hh = cw / 2 * pk, 30 * pk
            d.rounded_rectangle([cx - hw, cy - hh, cx + hw, cy + hh], radius=14, fill=col + (a,)); d.text((cx, cy + 1), name, font=ft, fill=INK + (a,), anchor='mm')
        elif i < cur:
            d.rounded_rectangle(box, radius=14, fill=(70, 74, 86, int(200 * k))); d.text((x + cw / 2, y + 1), name, font=ft, fill=(170, 172, 180, int(255 * k)), anchor='mm')
        else:
            d.rounded_rectangle(box, radius=14, outline=(255, 255, 255, int(90 * k)), width=2); d.text((x + cw / 2, y + 1), name, font=ft, fill=(255, 255, 255, int(120 * k)), anchor='mm')
    im.alpha_composite(ly)

SUBS = [('先在硅片上涂一层光刻胶', T['coat0'], T['mask0']),
        ('隔着掩模照紫外光，照到的胶会变', T['mask0'], T['dev0']),
        ('显影：照过的胶洗掉，波导那条留下', T['dev0'], T['etch0']),
        ('刻蚀：没胶挡着的硅被削掉', T['etch0'], T['strip0'] - 0.2),
        ('去掉胶，一条硅波导就刻好了', T['strip0'] - 0.2, T['light0']),
        ('光，就沿着这条硅走', T['light0'], 99)]
def subtitle(im, t):
    s = next((x for x in SUBS if x[1] <= t < x[2]), None)
    if not s: return
    ft = font(50); tw = ft.getlength(s[0]); ly = layer(); d = ImageDraw.Draw(ly); y = 1400 + 14 * (1 - ease((t - s[1]) / 0.15))
    d.rounded_rectangle([W / 2 - tw / 2 - 30, y - 44, W / 2 + tw / 2 + 30, y + 44], radius=10, fill=(14, 15, 20, 225))
    d.text((W / 2, y + 2), s[0], font=ft, fill=CREAM, anchor='mm'); im.alpha_composite(ly)

def title(im, t):
    """第一帧就有：实物 + 大字问题；2.4 秒后往上收走"""
    if t > 2.9: return
    k = ease((t - 2.4) / 0.5); ft = font(78); a = int(255 * (1 - k)); dy = -60 * k
    for j, line in enumerate(('光在芯片里走的路', '是怎么刻出来的？')):
        y = 420 + j * 104 + dy
        for dx, dy2, col in ((3, 4, (0, 0, 0, int(a * 0.6))), (0, 0, (CYAN if j == 0 else (255, 255, 255)) + (a,))):
            ly = layer(); ImageDraw.Draw(ly).text((W / 2 + dx, y + dy2), line, font=ft, fill=col, anchor='mm'); im.alpha_composite(ly)

def corners(im, t):
    ly = layer(); d = ImageDraw.Draw(ly); ft = font(28, heavy=False)
    d.text((44, 104), '工艺 · 硅光波导', font=ft, fill=(255, 255, 255, 170), anchor='lm')
    d.text((W - 44, 104), '一语道破 · 白话光互连', font=ft, fill=(255, 255, 255, 170), anchor='rm')
    note = '实际是看不见的红外光，青色为示意' if t >= T['light0'] else '层厚、颜色均为示意'
    d.text((W - 44, 282), note, font=font(26, heavy=False), fill=(255, 255, 255, 140), anchor='rm'); im.alpha_composite(ly)

def frame(i):
    t = (i - 1) / FPS; im = Image.open(os.path.join(SRC, f'f{i:04d}.png')).convert('RGBA').resize((W, H), Image.LANCZOS)
    a = {k: (v[0] * K, v[1] * K) for k, v in AF[str(i)].items()}
    g = Image.new('RGBA', (W, 640), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)       # 顶部压暗，字更跳
    for y in range(640): gd.line([0, y, W, y], fill=(4, 5, 8, int(150 * (1 - y / 640) ** 1.5)))
    im.alpha_composite(g, (0, 0))
    title(im, t); process_bar(im, t); corners(im, t)
    ts, bx, sb = a['top_si'], a['box'], a['sub']
    tag(im, '顶层硅 220 nm', ts[0] + 290, ts[1] - 80, 42, GOLD + (255,), INK, t, 0.3, 2.5, anchor=ts)
    tag(im, '埋氧层（二氧化硅）约 2 µm', bx[0] + 330, bx[1] + 10, 40, CREAM + (255,), INK, t, 0.55, 2.5, anchor=bx)
    tag(im, '硅衬底', sb[0] + 260, min(sb[1] - 40, 1290), 40, (120, 128, 150, 255), (255, 255, 255), t, 0.8, 2.5, anchor=sb)
    rs = a['resist']; tag(im, '光刻胶', rs[0] - 250, rs[1] - 170, 44, (150, 92, 230, 255), (255, 255, 255), t, T['coat0'] + 1.2, T['mask0'] + 0.5, anchor=rs)
    mk = a['mask']; tag(im, '掩模：中间一条挡光', mk[0] - 120, mk[1] - 150, 42, CREAM + (255,), INK, t, T['mask1'], T['dev0'] - 0.3, anchor=mk)
    rf = a['ridge_front']; tag(im, '波导宽约 0.5 µm', rf[0] + 120, rf[1] + 190, 46, CYAN + (255,), INK, t, T['exit0'] + 0.3, anchor=rf)
    subtitle(im, t)
    return im.convert('RGB')

# ---------- 声音：代码合成（120 BPM；涂胶/曝光 → 显影/刻蚀 → 停半拍 → 导光揭晓 换织体） ----------
SR = 48000
def synth(path):
    n = int(SR * NF / FPS) + SR // 2; out = np.zeros(n); tt = np.arange(n) / SR; rng = np.random.default_rng(11)
    def env(t0, a, d, length):
        e = np.zeros(n); i0 = int(t0 * SR); m = min(n - i0, int(length * SR)); x = np.arange(m) / SR
        e[i0:i0 + m] = np.minimum(1, x / max(a, 1e-4)) * np.exp(-x / d); return e
    def tone(f0, t0, a, d, length, amp, harm=(1,), det=0.0):
        e = env(t0, a, d, length); s = sum(np.sin(2 * np.pi * f0 * h * (1 + det * j) * tt) / (j + 1) for j, h in enumerate(harm)); return amp * e * s
    def noise(t0, a, d, length, amp, lp=0.15):
        e = env(t0, a, d, length); w = rng.standard_normal(n); y = np.zeros(n); acc = 0.0
        w = np.convolve(w, np.ones(int(1 / lp)) / int(1 / lp), mode='same'); return amp * e * w
    mid = lambda m: 440 * 2 ** ((m - 69) / 12)
    # 第一段（0–5.3）：D 小调低垫音，慢起
    for m in (50, 57, 62, 65): out += tone(mid(m), 0.0, 1.2, 4.0, 5.6, 0.05, harm=(1, 2), det=0.002)
    # 第二段（5.3–11.0）：Bb – C，八分音符脉冲（刻蚀的节奏）
    for k, ch in enumerate(((46, 53, 58, 62), (48, 55, 60, 64))):
        for m in ch: out += tone(mid(m), 5.3 + k * 2.8, 0.3, 2.4, 3.0, 0.04, harm=(1, 2))
    for b in range(int((10.9 - 5.5) / 0.25)):
        tb = 5.5 + b * 0.25; out += tone(mid(74 if b % 4 == 0 else 69), tb, 0.003, 0.07, 0.2, 0.05, harm=(1, 3))
    # 揭晓前停半拍（11.0–11.4 静），然后 F 大调明亮织体 + 上行琶音
    for m in (53, 60, 65, 69, 72): out += tone(mid(m), T['light0'], 0.05, 3.5, 3.0, 0.045, harm=(1, 2, 3))
    for j, m in enumerate((77, 81, 84, 88, 89)): out += tone(mid(m), T['light0'] + 0.25 * j, 0.004, 0.6, 1.2, 0.05, harm=(1, 2))
    # 音效（卡在画面动作上）
    td = T['coat0'] + 0.4; out += 0.25 * env(td, 0.002, 0.08, 0.3) * np.sin(2 * np.pi * (900 - 2000 * np.clip(tt - td, 0, 0.2)) * tt)   # 胶滴落下
    out += noise(T['coat0'] + 0.45, 0.3, 0.8, 1.6, 0.06)                                     # 旋涂铺开
    out += noise(T['mask0'], 0.25, 0.3, 0.7, 0.10)                                           # 掩模滑入
    hum = env(T['uv0'], 0.15, 9, T['uv1'] - T['uv0']) * (np.sin(2 * np.pi * 110 * tt) + 0.5 * np.sin(2 * np.pi * 220 * tt)) * (0.7 + 0.3 * np.sin(2 * np.pi * 6 * tt))
    out += 0.07 * hum                                                                         # 紫外灯嗡声
    out += noise(T['dev0'], 0.2, 0.5, 1.1, 0.05)                                              # 显影冲洗
    r = np.random.default_rng(7)
    for k in range(36):                                                                        # 离子落下：和画面同一套时刻
        t0 = T['etch0'] + (T['etch1'] - T['etch0'] - 0.4) * k / 36 + 0.35
        out += tone(2400 + 300 * (k % 5), t0, 0.001, 0.025, 0.08, 0.03)
    out += noise(T['strip0'], 0.2, 0.4, 0.9, 0.05)                                            # 去胶
    out += tone(mid(96), T['exit0'] + 0.1, 0.002, 1.2, 2.0, 0.07, harm=(1, 2.01))              # 出光：叮
    out[int(10.95 * SR):int(T['light0'] * SR)] *= np.linspace(1, 0, int(T['light0'] * SR) - int(10.95 * SR))   # 停半拍
    out = np.tanh(out * 1.6) / 1.6; out /= max(1e-6, np.abs(out).max()) / 0.8
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((out * 32767).astype(np.int16).tobytes())

if '--audio' in sys.argv:                                                     # 只出声音（试听用）
    synth(os.path.join(SRC, 'score.wav')); print('wrote', os.path.join(SRC, 'score.wav'))
elif STILLS:
    have = sorted(int(os.path.basename(p)[1:5]) for p in glob.glob(os.path.join(SRC, 'f[0-9][0-9][0-9][0-9].png')))
    os.makedirs(os.path.join(SRC, 'comp'), exist_ok=True)
    ims = [frame(i) for i in have]
    for i, im in zip(have, ims): im.save(os.path.join(SRC, 'comp', f'{i:04d}.jpg'), quality=92)
    tw, th = 270, 480; cols = min(6, len(ims)); rows = math.ceil(len(ims) / cols)
    sheet = Image.new('RGB', (cols * tw, rows * (th + 30)), (30, 30, 30)); d = ImageDraw.Draw(sheet)
    for j, (i, im) in enumerate(zip(have, ims)):
        x, y = (j % cols) * tw, (j // cols) * (th + 30); sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + 30)); d.text((x + 6, y + 6), f'{(i - 1) / FPS:.1f}s', font=font(20, False), fill=(255, 220, 0))
    sheet.save(os.path.join(SRC, 'comp_sheet.png')); print('wrote', os.path.join(SRC, 'comp_sheet.png'))
else:
    os.makedirs(os.path.join(SRC, 'comp'), exist_ok=True)
    for i in range(1, NF + 1): frame(i).save(os.path.join(SRC, 'comp', f'{i:04d}.jpg'), quality=95)
    wav = os.path.join(SRC, 'score.wav'); synth(wav)
    subprocess.run(['ffmpeg', '-nostdin', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(SRC, 'comp', '%04d.jpg'), '-i', wav,
                    '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', '-shortest', OUT], check=True)
    print('wrote', OUT)
