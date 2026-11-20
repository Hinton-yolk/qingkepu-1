# 2D 提示层 + 音效 + 编码 + 轨迹图 + 关键构图帧。
# 用法：python3 post.py <a|b|c> <3D 帧目录> <输出目录>
# 2D 层只放简短提示（标签条），不放大段字幕；提示挂在 3D 物体投影到屏幕的锚点上，跟着物体走。
import sys, os, glob, json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'style3d'))
from overlay import f, NOTO, grain

GR, WARMW, AMB, TEALC = (38, 40, 45), (246, 242, 236), (220, 138, 58), (31, 154, 142)
STY = {'g': (GR, WARMW), 'a': (AMB, (255, 255, 255)), 't': (TEALC, (255, 255, 255)), 'w': (WARMW, GR)}

# (锚点, 文字, 样式, 出现, 消失, 竖直偏移 px)
LABELS = {
    'a': [('slot', '下一个字？', 'a', 0.3, 2.5, -70),
          ('up_end', '一种可能的续写', 'w', 5.4, 9.2, -80), ('dn_end', '另一种可能', 'w', 5.8, 9.2, 80),
          ('up_mid', '采用这一条', 'a', 9.4, 10.9, -95),
          ('row', '写定了', 'g', 12.3, 14.0, -80), ('ghost', '后面的字还要一个一个写', 'w', 12.5, 14.0, -90)],
    'b': [('row', '已经写好的字', 'g', 0.2, 1.5, -70), ('plate', '每个字先变成一串数', 'w', 1.7, 3.8, 70),
          ('gate', '模型的一层（示意，实际有几十层）', 'g', 3.2, 6.9, -40),
          ('pill', '下一个字的候选和分数（示意）', 'w', 7.9, 8.95, -150), ('out', '选中「去」', 'a', 9.7, 10.5, -90)],
    'c': [('small', '小模型', 'g', 0.3, 4.0, -60), ('tray', '正式输出', 'g', 0.3, 3.2, -70),
          ('drafts', '草稿：还没确认', 'w', 2.5, 4.6, -80), ('ver', '大模型：一次验 4 个', 'g', 4.4, 7.9, -40),
          ('fix', '大模型自己给出这一位', 'a', 10.0, 11.8, -80)],
}
LABELS['int'] = [
    ('prefix', '已有文字', 'g', 0.2, 1.6, -70), ('cells', '每个字先变成一串数（示意）', 'w', 1.0, 2.8, 120),
    ('gather', '回看前文（示意）', 'g', 3.0, 4.9, -60), ('pill', '下一个字的候选', 'w', 7.6, 9.3, -60),
    ('fork_u', '一种可能的续写（假设）', 'w', 11.2, 14.4, -80), ('fork_d', '另一种可能', 'w', 11.6, 14.4, 80),
    ('qu', '选定「去」', 'a', 15.6, 17.4, -80),
    ('small', '小模型', 'g', 20.4, 23.0, -60), ('out', '正式输出', 'g', 20.2, 23.0, -80), ('drafts', '草稿（还没确认）', 'w', 21.6, 23.6, -70),
    ('ver', '大模型：集中验证', 'g', 23.6, 26.0, -40), ('acc', '接受', 't', 25.4, 26.4, -70), ('chi', '未接受', 'a', 25.9, 27.0, -70),
    ('kan', '补充候选', 'a', 28.3, 29.9, -70)]
LABELS['int'] = [(k, t, st, a, b, dy) for (k, t, st, a, b, dy) in LABELS['int']]
TITLE = {'c': ('小模型先猜，大模型集中验证', 13.6, 17.0)}

def chip(layer, cx, cy, text, sty, size=42, alpha=1.0):
    bg, fg = STY[sty]; d = ImageDraw.Draw(layer); ft = f(NOTO, size)
    w = d.textlength(text, font=ft); h = size * 1.55
    x0 = min(max(cx - w / 2 - 22, 60), 940 - w - 44)            # 右边缘 ≤ 940（按钮栏）
    y0 = min(max(cy - h / 2, 150), 1500)                         # 不进顶部状态栏和底部文案区
    a = int(255 * alpha)
    d.rounded_rectangle((x0, y0 + 5, x0 + w + 44, y0 + h + 5), h / 2, fill=(30, 30, 40, int(50 * alpha)))
    d.rounded_rectangle((x0, y0, x0 + w + 44, y0 + h), h / 2, fill=(*bg, a))
    d.text((x0 + 22 + w / 2, y0 + h / 2), text, font=ft, fill=(*fg, a), anchor='mm')

def fade(t, t0, t1, d=0.25): return max(0.0, min(1.0, (t - t0) / d, (t1 - t) / d))

def compose(shot, png, meta):
    t = meta['t']
    im = grain(Image.open(png).convert('RGB').resize((1080, 1920), Image.LANCZOS), 3.0, seed=meta['f'])
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    for (k, text, sty, t0, t1, dy) in LABELS[shot]:
        a = fade(t, t0, t1)
        if a <= 0 or k not in meta['anch']: continue
        x, y, z = meta['anch'][k]
        if z <= 0: continue
        chip(lay, x * 1080, y * 1920 + dy, text, sty, alpha=a)
    if shot in TITLE:
        text, t0, t1 = TITLE[shot]; a = fade(t, t0, t1, 0.4)
        if a > 0: chip(lay, 500, 330, text, 'g', size=50, alpha=a)
    ImageDraw.Draw(lay).text((70, 1840), '示意动画', font=f(NOTO, 26), fill=(90, 86, 80, 150))
    im = im.convert('RGBA'); im.alpha_composite(lay); return im.convert('RGB')

# ---------------- 音效（原创合成；没有人声） ----------------
SR = 48000
rng = np.random.default_rng(3)
def tt(d): return np.arange(int(d * SR)) / SR
def blip(fq, d=0.12, g=1.0): t = tt(d); return np.sin(2 * np.pi * fq * t) * np.exp(-t * 32) * g
def thud(g=1.0):
    t = tt(0.35); fq = 60 + 80 * np.exp(-t * 30); return np.sin(2 * np.pi * np.cumsum(fq) / SR) * np.exp(-t * 11) * g
def bell(fq, d=1.6, g=1.0):
    t = tt(d); return sum(a * np.sin(2 * np.pi * fq * r * t) * np.exp(-t * k) for r, a, k in ((1, 1, 2.5), (2.76, .4, 4), (5.4, .2, 7))) * 0.5 * g
def whoosh(d=0.6, up=True, g=1.0):
    t = tt(d); x = rng.standard_normal(len(t)); y = np.zeros_like(x); a = 0.0
    fc = np.linspace(400, 3000, len(t)) if up else np.linspace(3000, 400, len(t))
    k = 2 * np.pi * fc / SR
    for i in range(len(x)): a += k[i] * (x[i] - a); y[i] = a
    return y * np.sin(np.pi * t / d) ** 1.5 * g * 0.6
def hz(m): return 440 * 2 ** ((m - 69) / 12)

def pad(dur, notes, g=0.05):
    t = tt(dur); s = np.zeros(len(t))
    for m in notes:
        for det in (-0.08, 0.08):
            s += np.sin(2 * np.pi * hz(m + det) * t)
    env = np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.0)
    return s * env * (0.85 + 0.15 * np.sin(2 * np.pi * 0.2 * t)) * g / len(notes)

def events(shot):
    E = []
    if shot == 'a':
        E += [(0.15, thud(0.5)), (1.6, whoosh(0.9, True, 0.5)), (2.6, whoosh(0.7, True, 0.6))]
        E += [(4.0 + k * 0.5, blip(hz(74 + 2 * k), g=0.35)) for k in range(5)] + [(4.25 + k * 0.5, blip(hz(69 + 2 * k), g=0.3)) for k in range(3)]
        E += [(9.3, bell(hz(81), g=0.5)), (10.6, whoosh(0.8, False, 0.5)), (12.3, thud(0.7)), (12.45, blip(hz(86), g=0.3))]
        P = pad(14.0, [50, 57, 62, 66])
    elif shot == 'b':
        E += [(0.5 + 0.28 * k + 0.4, blip(hz(71 + 3 * k), g=0.35)) for k in range(4)] + [(2.3, whoosh(1.2, True, 0.4))]
        for gx, tc in ((3.2, 3.95), (5.2, 4.95), (7.2, 6.2)): E += [(tc, bell(hz(78), 0.8, 0.35)), (tc + 0.08, blip(hz(83), g=0.25))]
        E += [(7.3 + 0.12 * j, blip(hz(86 - j), 0.08, 0.25)) for j in range(6)] + [(8.2, whoosh(0.7, True, 0.4)), (9.0, bell(hz(83), g=0.5)), (10.25, thud(0.7))]
        P = pad(10.5, [47, 54, 59, 62])
    elif shot == 'int':
        E += [(0.4 + 0.25 * k + 0.3, blip(hz(71 + 3 * k), g=0.3)) for k in range(4)] + [(1.9, whoosh(1.0, True, 0.35))]
        E += [(3.0 + 0.12 * k, blip(hz(83 + k), 0.1, 0.25)) for k in range(3)] + [(3.55, bell(hz(79), 0.8, 0.3))] + [(3.9 + 0.1 * k, blip(hz(90 - k), 0.08, 0.25)) for k in range(3)]
        E += [(4.45, bell(hz(86), 1.2, 0.45)), (4.95, whoosh(1.0, True, 0.3)), (5.3, blip(hz(78), g=0.25)), (5.7, blip(hz(81), g=0.25)), (5.9, whoosh(1.3, False, 0.35))]
        E += [(7.1 + 0.07 * j, blip(hz(86 - j), 0.08, 0.25)) for j in range(6)] + [(7.6, whoosh(0.7, True, 0.4)), (8.3, bell(hz(81), 1.0, 0.35))]
        E += [(8.7, whoosh(1.2, True, 0.35)), (10.0, thud(0.4)), (10.25, thud(0.35))] + [(10.3 + k * 0.42, blip(hz(74 + 2 * k), g=0.28)) for k in range(5)] + [(10.5 + k * 0.42, blip(hz(69 + 2 * k), g=0.24)) for k in range(3)]
        E += [(14.0, bell(hz(81), g=0.45)), (14.6, whoosh(1.4, False, 0.35)), (15.4, whoosh(1.2, False, 0.35)), (16.7, thud(0.7)), (17.4, whoosh(1.0, False, 0.25))]
        E += [(18.6, whoosh(1.4, True, 0.3)), (19.3, thud(0.4)), (19.6, thud(0.45))]
        E += [(20.9 + 0.4 * j, blip(hz(84 + j), 0.1, 0.4)) for j in range(4)] + [(22.7, whoosh(1.2, True, 0.4)), (24.0, whoosh(0.7, True, 0.35))]
        E += [(24.9, bell(hz(83), g=0.45)), (25.3, bell(hz(86), g=0.45)), (25.7, thud(0.8)), (26.2, whoosh(0.8, False, 0.35)), (27.5, thud(0.6)), (27.75, thud(0.6))]
        E += [(26.6, whoosh(1.6, False, 0.35)), (28.15, thud(0.5)), (27.6, bell(hz(74), 0.6, 0.3)), (27.9, whoosh(0.6, True, 0.35)), (29.7, thud(0.8)), (31.2, blip(hz(84), 0.1, 0.4))]
        N = int(34.0 * SR); P = np.zeros(N)
        for t0, d, ch in ((0.0, 10.0, [47, 54, 59, 62]), (8.8, 10.5, [50, 57, 62, 66]), (19.4, 14.6, [43, 50, 55, 59])):
            x = pad(d, ch); i = int(t0 * SR); n = min(len(x), N - i); P[i:i + n] += x[:n]
    else:
        E += [(1.0 + 0.45 * j, blip(hz(84 + j), 0.1, 0.4)) for j in range(4)] + [(3.4, whoosh(1.4, True, 0.45)), (5.2, whoosh(0.9, True, 0.35))]
        E += [(6.3, bell(hz(83), g=0.45)), (6.8, bell(hz(86), g=0.45)), (7.3, thud(0.8)), (7.65, blip(hz(62), 0.2, 0.3))]
        E += [(8.0, whoosh(0.8, False, 0.4)), (9.4, thud(0.6)), (9.7, thud(0.6)), (9.0, whoosh(1.2, False, 0.3)), (9.8, whoosh(0.6, True, 0.4)), (11.6, thud(0.8))]
        E += [(11.9, blip(hz(84), 0.1, 0.4)), (12.35, blip(hz(86), 0.1, 0.4)), (13.4, whoosh(1.6, True, 0.35)), (13.6, bell(hz(74), 2.4, 0.3)), (15.8, whoosh(0.8, True, 0.3))]
        P = pad(17.0, [43, 50, 55, 59]) + np.pad(pad(5.0, [50, 57, 62, 66]), (int(12.0 * SR), 0))[:int(17.0 * SR)]
    return E, P

def audio(shot, dur, out):
    E, P = events(shot); N = int(dur * SR); buf = np.zeros(N); buf[:len(P)] += P[:N]
    for t0, sig in E:
        i = int(t0 * SR); n = min(len(sig), N - i)
        if n > 0: buf[i:i + n] += sig[:n]
    buf = buf / (np.abs(buf).max() + 1e-9) * 0.7
    from scipy.io import wavfile
    wavfile.write(out, SR, np.stack([buf, buf], 1).astype(np.float32))

# ---------------- 轨迹图 ----------------
COLS = [(220, 138, 58), (31, 154, 142), (80, 84, 92), (180, 120, 60), (60, 140, 200), (150, 90, 160), (120, 160, 70), (200, 80, 80), (90, 90, 160), (170, 150, 60)]
def trajectories(metas, base_png, out_png, out_json):
    names = list(metas[0]['objs'].keys()); paths = {k: [] for k in names}
    for m in metas:
        for k in names:
            o = m['objs'][k]; x, y, z = o['screen']
            paths[k].append((m['t'], o['world'], x, y))
    json.dump({k: [{'t': t, 'world': w, 'screen': [round(x, 4), round(y, 4)]} for t, w, x, y in v] for k, v in paths.items()},
              open(out_json, 'w'), ensure_ascii=False)
    im = Image.open(base_png).convert('RGB').resize((1080, 1920)); im = Image.blend(im, Image.new('RGB', im.size, (255, 255, 255)), 0.45)
    d = ImageDraw.Draw(im); ft = f(NOTO, 30)
    for i, k in enumerate(names):
        pts = [(x * 1080, y * 1920) for t, w, x, y in paths[k] if -0.2 < x < 1.2 and -0.2 < y < 1.2]
        if len(pts) < 2: continue
        c = COLS[i % len(COLS)]; d.line(pts, fill=c, width=5)
        for j in range(0, len(pts), 15): d.ellipse((pts[j][0] - 5, pts[j][1] - 5, pts[j][0] + 5, pts[j][1] + 5), fill=c)
        d.text((pts[-1][0] + 8, pts[-1][1] - 14), k, font=ft, fill=c)
    d.text((40, 40), '屏幕上的运动轨迹（相机也在动，所以是「看到的」轨迹；点间隔 0.5 秒）', font=f(NOTO, 28), fill=(40, 40, 40))
    im.save(out_png, quality=88)

if __name__ == '__main__':
    shot, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(os.path.join(out, 'comp_' + shot), exist_ok=True)
    pngs = sorted(glob.glob(os.path.join(src, 'f*.png'))); metas = [json.load(open(p[:-4] + '.json')) for p in pngs]
    from multiprocessing import Pool
    def job(i):
        o = os.path.join(out, 'comp_' + shot, f'f{i:05d}.jpg')
        if not os.path.exists(o): compose(shot, pngs[i], metas[i]).save(o, quality=92)
    with Pool(4) as pool: pool.map(job, range(len(pngs)))
    dur = len(pngs) / 30.0
    name = {'a': 'AnimationTest_A_Branch', 'b': 'AnimationTest_B_ModelFlow', 'c': 'AnimationTest_C_SpeculativeDecoding', 'int': 'EP01_IntegratedAnimation_Test01'}[shot]
    wav = os.path.join(out, f'{shot}_sfx.wav'); audio(shot, dur, wav)
    mp4 = os.path.join(out, name + '.mp4')
    r = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-i', wav, '-af', 'loudnorm=I=-16:TP=-2:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    j = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
    af = (f"loudnorm=I=-16:TP=-2:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-framerate', '30', '-i', os.path.join(out, 'comp_' + shot, 'f%05d.jpg'), '-i', wav,
                    '-af', af, '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
                    '-shortest', '-movflags', '+faststart', mp4], check=True)
    mid = pngs[len(pngs) // 2]
    trajectories(metas, mid, os.path.join(out, f'{name}_轨迹.jpg'), os.path.join(out, f'{name}_轨迹.json'))
    print('ok', mp4)
