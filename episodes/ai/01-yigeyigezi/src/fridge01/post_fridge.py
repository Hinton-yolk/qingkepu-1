# 冰箱开场样片：2D 文字层（AI 正在写的故事 + 演示回放标记 + 结尾问题）+ 环境声和动作音效 + 编码。
# 文字都在屏幕平面上（不贴在透视面上），同一时刻只有一处要读的东西。
# 用法：python3 post_fridge.py <帧目录> <输出目录>
import sys, os, glob, json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'style3d'))
from overlay import f, NOTO, NOTO_R, grain

W, Hh = 1080, 1920
INK, SUB, CARD = (34, 36, 40), (120, 116, 110), (255, 253, 250)
SEA_C, FOR_C = (36, 118, 176), (70, 128, 52)
T_SEA, T_RW, T_FOR = 1.75, (7.5, 8.9), 9.7
# 故事句子：按语义片段一段段出来（第一帧已经有「我打开」）
CHUNKS = [('我', -1.0), ('打开', -0.5), ('冰箱', 0.15), ('，', 0.3), ('里面', 0.5), ('竟然', 0.7), ('是', 0.9), ('一片', 1.05)]

def ease(u): u = max(0.0, min(1.0, u)); return u * u * u * (u * (6 * u - 15) + 10)
def sstep(a, b, t): return ease((t - a) / (b - a))
def fade(t, t0, t1, d=0.25): return max(0.0, min(1.0, (t - t0) / d, (t1 - t) / d))
def back_out(u, k=1.7): u = max(0.0, min(1.0, u)); u1 = u - 1; return 1 + (k + 1) * u1 ** 3 + k * u1 ** 2

def seg_state(t):
    """当前续写片段：(文字, 颜色, 出现程度 0..1, 句号出现程度)"""
    if t < T_RW[0] + 0.2:
        return '海洋', SEA_C, back_out(sstep(T_SEA, T_SEA + 0.3, t)) if t >= T_SEA else 0.0, sstep(2.25, 2.4, t)
    if t < T_FOR:
        r = sstep(T_RW[0] + 0.3, T_RW[0] + 1.2, t)                  # 回放：片段从右往左收回到光标处
        return '海洋', SEA_C, 1.0 - r, 1.0 - sstep(T_RW[0] + 0.2, T_RW[0] + 0.4, t)
    return '森林', FOR_C, back_out(sstep(T_FOR, T_FOR + 0.3, t)), sstep(10.2, 10.35, t)

def chat(lay, t, meta):
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = 48, 118, W - 48, 560
    d.rounded_rectangle((x0, y0 + 8, x1, y1 + 8), 40, fill=(40, 30, 20, 40))
    d.rounded_rectangle((x0, y0, x1, y1), 40, fill=(*CARD, 238))
    # 用户的请求
    fq = f(NOTO, 40); q = '帮我写个故事'; qw = d.textlength(q, font=fq)
    d.rounded_rectangle((x1 - 40 - qw - 56, y0 + 32, x1 - 40, y0 + 32 + 74), 37, fill=(234, 228, 219, 255))
    d.text((x1 - 40 - 28 - qw, y0 + 32 + 37), q, font=fq, fill=(*INK, 255), anchor='lm')
    # AI 头像 + 「正在写」
    cx, cy = x0 + 70, y0 + 170
    d.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=(31, 154, 142, 255)); d.text((cx, cy), 'AI', font=f(NOTO, 30), fill=(255, 255, 255, 255), anchor='mm')
    writing = t < 2.6 or (T_RW[1] - 0.2 < t < 10.6)
    d.text((cx + 52, cy), '正在写…' if writing else '写到这里', font=f(NOTO_R, 30), fill=(*SUB, 255), anchor='lm')
    # 正文：第一行「我打开冰箱，」第二行「里面竟然是一片」+ 续写片段 + 句号
    ft = f(NOTO, 62); lx, ly1, ly2 = x0 + 44, y0 + 268, y0 + 368
    line1 = ''.join(c for c, tt in CHUNKS[:4] if t >= tt); line2 = ''.join(c for c, tt in CHUNKS[4:] if t >= tt)
    d.text((lx, ly1), line1, font=ft, fill=(*INK, 255), anchor='lm')
    d.text((lx, ly2), line2, font=ft, fill=(*INK, 255), anchor='lm')
    ex = lx + d.textlength(line2, font=ft) + 8
    seg, col, a, dot = seg_state(t)
    seg_box = None
    if a > 0.01:
        sw = d.textlength(seg, font=ft); s = max(0.3, min(1.15, a)); w = (sw + 36) * min(1.0, a)
        bx0, by0, bx1, by1 = ex, ly2 - 46 * s, ex + w, ly2 + 46 * s
        d.rounded_rectangle((bx0, by0, bx1, by1), 18, fill=(*col, int(255 * min(1, a))))
        tmp = Image.new('RGBA', lay.size, (0, 0, 0, 0)); ImageDraw.Draw(tmp).text((ex + 18, ly2), seg, font=f(NOTO, int(62 * s)), fill=(255, 255, 255, int(255 * min(1, a))), anchor='lm')
        mask = Image.new('L', lay.size, 0); ImageDraw.Draw(mask).rectangle((bx0, 0, bx1, Hh), fill=255)
        lay.alpha_composite(Image.composite(tmp, Image.new('RGBA', lay.size, (0, 0, 0, 0)), mask))
        seg_box = (bx0, by0, bx1, by1); ex = bx1 + 6
        if dot > 0: d.text((ex, ly2), '。', font=ft, fill=(*INK, int(255 * dot)), anchor='lm')
    if (a <= 0.01 or (T_RW[0] < t < T_FOR)) and t >= 1.05 and int(t * 2.4) % 2 == 0 and a < 0.5:     # 光标：停在「一片」后面等下一段
        d.rounded_rectangle((ex, ly2 - 38, ex + 8, ly2 + 38), 3, fill=(*INK, 230))
    return seg_box

def pulse(lay, t, meta, seg_box):
    """片段落定的一瞬：一颗同色的光点从这段文字落到冰箱门洞里（文字 → 门里的世界）"""
    for t0, col in ((T_SEA + 0.05, SEA_C), (T_FOR + 0.05, FOR_C)):
        u = (t - t0) / 0.35
        if not (0 <= u <= 1.25) or seg_box is None: continue
        sx, sy = (seg_box[0] + seg_box[2]) / 2, seg_box[3]
        dx, dy = meta['anch']['door'][0] * W, meta['anch']['door'][1] * Hh
        g = Image.new('RGBA', lay.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        for k in range(10):
            v = min(1.0, u) - k * 0.035
            if v < 0: continue
            e = ease(v); x, y = sx + (dx - sx) * e, sy + (dy - sy) * e; r = 18 - k * 1.3; al = int(230 * (1 - k / 10) * (1 - max(0, u - 1) * 4))
            if al > 0: gd.ellipse((x - r, y - r, x + r, y + r), fill=(*col, al))
        if u > 0.9:
            rr = 40 + 260 * (u - 0.9); al = int(160 * max(0, 1 - (u - 0.9) / 0.35))
            gd.ellipse((dx - rr, dy - rr * 1.4, dx + rr, dy + rr * 1.4), outline=(*col, al), width=8)
        lay.alpha_composite(g.filter(ImageFilter.GaussianBlur(3)))

def pill(lay, cy, lines, t, t0, t1, dark=True):
    a = fade(t, t0, t1, 0.3)
    if a <= 0: return
    d = ImageDraw.Draw(lay); fts = [f(NOTO, 50), f(NOTO_R, 34)][:len(lines)]
    w = max(d.textlength(s, font=ft) for s, ft in zip(lines, fts)) + 90; h = 96 if len(lines) == 1 else 150
    x0 = (W - w) / 2; y0 = cy - h / 2
    bg = (34, 36, 40) if dark else (255, 253, 250); fg = (255, 255, 255) if dark else (34, 36, 40)
    d.rounded_rectangle((x0, y0 + 6, x0 + w, y0 + h + 6), h / 2 if len(lines) == 1 else 40, fill=(20, 20, 20, int(50 * a)))
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), h / 2 if len(lines) == 1 else 40, fill=(*bg, int(235 * a)))
    if len(lines) == 1: d.text((W / 2, cy), lines[0], font=fts[0], fill=(*fg, int(255 * a)), anchor='mm')
    else:
        d.text((W / 2, y0 + 52), lines[0], font=fts[0], fill=(*fg, int(255 * a)), anchor='mm')
        d.text((W / 2, y0 + 112), lines[1], font=fts[1], fill=(*((200, 200, 196) if dark else SUB), int(255 * a)), anchor='mm')

def note(lay, text, t, t0, t1):
    a = fade(t, t0, t1, 0.3)
    if a <= 0: return
    d = ImageDraw.Draw(lay); ft = f(NOTO_R, 32); w = d.textlength(text, font=ft) + 48
    d.rounded_rectangle(((W - w) / 2, 1748, (W + w) / 2, 1748 + 56), 28, fill=(255, 253, 250, int(200 * a)))
    d.text((W / 2, 1776), text, font=ft, fill=(*SUB, int(255 * a)), anchor='mm')

def compose(png, meta):
    t = meta['t']
    im = grain(Image.open(png).convert('RGB').resize((W, Hh), Image.LANCZOS), 2.5, seed=meta['f']).convert('RGBA')
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    sb = chat(lay, t, meta); pulse(lay, t, meta, sb)
    # 回放标记：这是我们为了讲解倒回去重演，不是 AI 改了已经写出的字
    if T_RW[0] - 0.3 < t < T_FOR + 0.1:
        pill(lay, 1600, ['演示回放：回到同一个起点', '（为了讲解重演，不是 AI 改掉已经写出的字）'], t, T_RW[0] - 0.3, T_FOR + 0.1)
        a = fade(t, T_RW[0] - 0.3, T_FOR + 0.1, 0.3); d = ImageDraw.Draw(lay)
        u = sstep(T_RW[0] + 0.2, T_RW[1], t)                       # 回放进度条：往回走
        d.rounded_rectangle((250, 1700, 830, 1710), 5, fill=(255, 255, 255, int(120 * a)))
        x = 830 - 580 * u; d.rounded_rectangle((250, 1700, x, 1710), 5, fill=(31, 154, 142, int(230 * a)))
        d.ellipse((x - 14, 1691, x + 14, 1719), fill=(255, 255, 255, int(255 * a)))
    note(lay, '示意：门里的画面是我们对文字含义的想象，不是模型生成的图像', t, 3.8, 7.2)
    note(lay, '示意：这里按词语演示；实际生成单位是 token，一个词可能是一个或几个 token', t, 12.6, 15.9)
    pill(lay, 1600, ['为什么后一步，要接着前一步生成？'], t, 16.4, 21.0)
    im.alpha_composite(lay); return im.convert('RGB')

# ---------------- 声音（原创合成：环境声 + 动作音效；没有人声） ----------------
SR = 48000
rng = np.random.default_rng(11)
def tt(dur): return np.arange(int(dur * SR)) / SR
def lp(x, fc):
    a = 1 - math.exp(-2 * math.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i in range(len(x)): s += a * (x[i] - s); y[i] = s
    return y
def lp_fast(x, fc, n=2):
    from scipy.signal import butter, lfilter
    b, a = butter(n, fc / (SR / 2)); return lfilter(b, a, x)
def bp(x, f0, f1):
    from scipy.signal import butter, lfilter
    b, a = butter(2, [f0 / (SR / 2), f1 / (SR / 2)], btype='band'); return lfilter(b, a, x)
def env(n, a, r): e = np.ones(n); ka = int(a * SR); kr = int(r * SR); e[:ka] = np.linspace(0, 1, ka) if ka else 1; e[n - kr:] = np.linspace(1, 0, kr) if kr else 1; return e
def tick(g=0.25): t = tt(0.05); return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 160) * g + rng.standard_normal(len(t)) * np.exp(-t * 300) * g * 0.3
def clunk(g=0.5): t = tt(0.25); return (np.sin(2 * np.pi * 90 * t) * np.exp(-t * 25) + rng.standard_normal(len(t)) * np.exp(-t * 60) * 0.3) * g
def bell(fq, d=1.6, g=0.3): t = tt(d); return sum(a * np.sin(2 * np.pi * fq * r * t) * np.exp(-t * k) for r, a, k in ((1, 1, 2.5), (2.0, .3, 4), (3.0, .15, 6))) * g
def whoosh(d, up=True, g=0.3):
    t = tt(d); x = rng.standard_normal(len(t)); y = bp(x, 300, 2500) if up else bp(x, 200, 1600)
    sh = np.sin(np.pi * t / d) ** 2; return y * sh * g
def audio(dur, out):
    N = int(dur * SR); buf = np.zeros(N)
    def put(t0, sig):
        i = int(t0 * SR); n = min(len(sig), N - i)
        if n > 0 and i >= 0: buf[i:i + n] += sig[:n]
    t = tt(dur)
    # 厨房：冰箱压缩机的低嗡声（全程很轻）
    buf += (np.sin(2 * np.pi * 58 * t) * 0.6 + np.sin(2 * np.pi * 116 * t) * 0.25) * 0.02
    # 门开：门封松开的「噗」+ 门轴
    put(0.02, clunk(0.35)); put(0.1, whoosh(0.9, False, 0.12))
    for c, t0 in CHUNKS:
        if t0 >= 0: put(t0, tick(0.18))
    put(10.7, tick(0.0))
    # 海：片段落定 → 一声明亮的音 + 海浪（低通噪声，慢慢涌）
    put(T_SEA, bell(880, 1.4, 0.18)); put(T_SEA + 0.05, whoosh(1.2, True, 0.25))
    wave = lp_fast(rng.standard_normal(N), 700) * 0.9
    swell = 0.55 + 0.45 * np.sin(2 * np.pi * 0.17 * t - 1.2)
    sea_env = np.clip((t - 2.0) / 1.0, 0, 1) * np.clip((T_RW[0] + 0.6 - t) / 0.8, 0, 1)
    buf += wave * swell * sea_env * 0.22
    # 回放：倒带声（往上走的滤波噪声 + 几下反向的滴答）
    put(T_RW[0] + 0.1, whoosh(1.2, True, 0.28))
    for k in range(5): put(T_RW[0] + 0.25 + 0.18 * k, tick(0.12))
    # 森林：片段落定 → 另一个音 + 风吹树叶 + 鸟叫
    put(T_FOR, bell(660, 1.6, 0.18)); put(T_FOR + 0.05, whoosh(1.4, True, 0.22))
    leaves = bp(rng.standard_normal(N), 1800, 6000)
    gust = 0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t) * np.sin(2 * np.pi * 0.07 * t + 1)
    buf += leaves * gust * np.clip((t - 10.2) / 1.5, 0, 1) * 0.06
    for t0, f0 in ((12.4, 3200), (12.62, 3600), (14.9, 2800), (15.1, 3300), (15.25, 3000), (17.8, 3400), (18.0, 3800)):
        tb = tt(0.12); put(t0, np.sin(2 * np.pi * np.cumsum(f0 + 900 * np.sin(np.pi * tb / 0.12)) / SR) * np.sin(np.pi * tb / 0.12) * 0.06)
    put(16.4, bell(523, 2.4, 0.14)); put(16.45, bell(784, 2.4, 0.08))
    buf = buf / (np.abs(buf).max() + 1e-9) * 0.8
    from scipy.io import wavfile
    wavfile.write(out, SR, np.stack([buf, buf], 1).astype(np.float32))

if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]; os.makedirs(os.path.join(out, 'comp'), exist_ok=True)
    pngs = sorted(glob.glob(os.path.join(src, 'f*.png'))); metas = [json.load(open(p[:-4] + '.json')) for p in pngs]
    from multiprocessing import Pool
    def job(i):
        o = os.path.join(out, 'comp', f'f{i:05d}.jpg'); compose(pngs[i], metas[i]).save(o, quality=93)
    with Pool(4) as pool: pool.map(job, range(len(pngs)))
    dur = len(pngs) / 30.0; wav = os.path.join(out, 'sfx.wav'); audio(dur, wav)
    mp4 = os.path.join(out, 'EP01_Fridge_OpeningConcept.mp4')
    r = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-i', wav, '-af', 'loudnorm=I=-16:TP=-2:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
    af = (f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-framerate', '30', '-i', os.path.join(out, 'comp', 'f%05d.jpg'), '-i', wav, '-af', af,
                    '-c:v', 'libx264', '-crf', '20', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', mp4], check=True)
    print('ok', mp4)
