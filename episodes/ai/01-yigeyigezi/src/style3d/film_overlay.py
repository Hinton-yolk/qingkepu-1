# EP.01 新画风 2D 层：字幕（照用户确认的脚本 v2.1 原文）、小字、「类比」标签、标签条、大字问题、片尾大字、片尾卡、细颗粒。
# 用法：python3 film_overlay.py <3D 帧目录> <输出目录>        （帧名 bNN.png / tTTT.TT.png，旁边有同名 .json）
import sys, os, json, glob
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overlay import f, NOTO, NOTO_R, SMILEY, INK, YEL, grain, chip

ORANGE = (255, 154, 60)
# 字幕、小字从 script.md「逐句字幕 v3」表直接读（照用户确认的原文，避免抄错）；〔类比〕→ 挂「类比」标签
import re
def load_caps():
    md = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'script.md'), encoding='utf-8').read()
    sec = md[md.index('## 逐句字幕 v3'):]
    caps = {}
    for l in sec.split('\n'):
        if not re.match(r'^\| \d+ \|', l): continue
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        cap = c[3]; analog = '〔类比〕' in cap
        cap = cap.replace('〔类比〕', '').replace(' / ', '/').strip()
        caps[int(c[0])] = (cap, c[4], analog)
    return caps
CAPS = load_caps()

def parse(line):
    out = []; buf = ''; y = False
    for ch in line:
        if ch == '{': out.append((buf, y)); buf = ''; y = True
        elif ch == '}': out.append((buf, y)); buf = ''; y = False
        else: buf += ch
    out.append((buf, y)); return [(s, c) for s, c in out if s]

def wrap_note(d, text, ft, maxw=740):   # 小字条右边缘 ≤ 940：540 + 740/2 + 22 ≈ 932
    """小字：最多两行；按「 · 」或按宽度断开"""
    parts = text.split(' · ')
    if len(parts) == 2 and all(d.textlength(p, font=ft) <= maxw for p in parts): return parts
    if d.textlength(text, font=ft) <= maxw: return [text]
    lines = ['']
    for ch in text.replace(' · ', '，'):
        if d.textlength(lines[-1] + ch, font=ft) > maxw: lines.append('')
        lines[-1] += ch
    return lines[:2]

def caption(im, text, note, analog):
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    fc = f(NOTO, 60); lh = 80; cy = 1480
    lines = [parse(l) for l in text.split('/')]
    widths = [sum(d.textlength(s, font=fc) for s, _ in l) for l in lines]
    bw = max(widths) + 80; bh = lh * len(lines) + 40
    d.rounded_rectangle((540 - bw / 2, cy - bh / 2, 540 + bw / 2, cy + bh / 2), 26, fill=(20, 24, 48, 205))
    for i, l in enumerate(lines):
        x = 540 - widths[i] / 2; y = cy - (len(lines) - 1) * lh / 2 + i * lh
        for s, c in l:
            d.text((x, y), s, font=fc, fill=YEL + (255,) if c else (255, 255, 255, 255), anchor='lm'); x += d.textlength(s, font=fc)
    if analog:   # 「类比」标签：字幕条右侧的橙框
        fa = f(NOTO, 34); ax = 540 + bw / 2 + 14; aw = d.textlength('类比', font=fa) + 28
        if ax + aw > 1020: ax = 540 + bw / 2 - aw - 10; ay = cy - bh / 2 - 34
        else: ay = cy
        d.rounded_rectangle((ax, ay - 26, ax + aw, ay + 26), 12, outline=ORANGE + (255,), width=4, fill=(20, 24, 48, 205))
        d.text((ax + aw / 2, ay), '类比', font=fa, fill=ORANGE + (255,), anchor='mm')
    if note:
        for fs in (32, 30, 28):   # 最多两行；放不下就把字缩小一点，不截断
            fn = f(NOTO_R, fs); nl = wrap_note(d, note, fn)
            if len(''.join(nl)) >= len(note.replace(' · ', '')) - 1: break
        nh = 44 * len(nl) + 14; ny1 = cy - bh / 2 - 16; ny0 = ny1 - nh
        nw = max(d.textlength(t, font=fn) for t in nl)
        d.rounded_rectangle((540 - nw / 2 - 22, ny0, 540 + nw / 2 + 22, ny1), 18, fill=(20, 24, 48, 150))
        for i, t in enumerate(nl):
            d.text((540, ny0 + 7 + 22 + i * 44), t, font=fn, fill=(222, 226, 245, 255), anchor='mm')
    im.paste(layer, (0, 0), layer); return im

def title(im):
    d = ImageDraw.Draw(im); l1, l2 = 'AI 为什么', '一个字一个字往外蹦？'
    size = 132
    while d.textlength(l2, font=f(SMILEY, size)) > 800: size -= 2
    ft = f(SMILEY, size); w2 = d.textlength(l2, font=ft); x0 = 540 - w2 / 2; kw = d.textlength('一个字一个字', font=ft)
    d.rounded_rectangle((x0 - 8, 340, x0 + kw + 8, 400), 14, fill=YEL)
    d.text((540, 225), l1, font=ft, fill=INK, anchor='mm'); d.text((540, 365), l2, font=ft, fill=INK, anchor='mm')

def big_end(im):
    d = ImageDraw.Draw(im); ft = f(SMILEY, 104)
    for i, (t, k) in enumerate([('写，要一个字一个字写；', '一个字一个字'), ('批改，可以一起批', '一起批')]):
        y = 300 + i * 150; w = d.textlength(t, font=ft); x0 = 540 - w / 2
        kx = x0 + d.textlength(t[:t.index(k)], font=ft); kw = d.textlength(k, font=ft)
        d.rounded_rectangle((kx - 6, y + 8, kx + kw + 6, y + 50), 12, fill=YEL)
        d.text((540, y), t, font=ft, fill=INK, anchor='mm')

def end_card(im):
    d = ImageDraw.Draw(im)
    d.text((540, 520), '（系列名待定）· EP.01', font=f(NOTO, 44), fill=(40, 48, 90), anchor='mm')
    ft = f(SMILEY, 96)
    d.text((540, 680), 'AI 为什么', font=ft, fill=INK, anchor='mm'); d.text((540, 800), '一个字一个字往外蹦？', font=ft, fill=INK, anchor='mm')
    d.text((540, 1010), '芯片与光', font=f(NOTO, 52), fill=INK, anchor='mm')
    d.text((540, 1080), '剑桥材料学博士 · 半导体', font=f(NOTO_R, 38), fill=(40, 48, 90), anchor='mm')

def sketch_frame(im):
    """结尾聊天气泡放进「示意」框，不暗示是你手机里的 App"""
    d = ImageDraw.Draw(im); x0, y0, x1, y1 = 120, 470, 960, 1300
    for k in range(0, int(x1 - x0), 28):
        d.line((x0 + k, y0, min(x0 + k + 14, x1), y0), fill=(255, 255, 255), width=5); d.line((x0 + k, y1, min(x0 + k + 14, x1), y1), fill=(255, 255, 255), width=5)
    for k in range(0, int(y1 - y0), 28):
        d.line((x0, y0 + k, x0, min(y0 + k + 14, y1)), fill=(255, 255, 255), width=5); d.line((x1, y0 + k, x1, min(y0 + k + 14, y1)), fill=(255, 255, 255), width=5)
    chip(im, x0 + 90, y0, '示意', (255, 255, 255), INK)

CHIPS = {   # 拍的函数名 → [(锚点, 文字, 底色, 字色)]
    'o1': [('qu', '一个字', (253, 251, 246), INK), ('q', '下一个字', (255, 196, 40), INK)],
    'o3': [('q', '下一个字', (255, 196, 40), INK)],
    'o4': [('model', '模型：一层一层', (75, 63, 140), (255, 255, 255))],
    'n_strip': [('strip', '一串数', (29, 35, 80), (143, 227, 255))],
    'n_mult': [('layer', '一层：参数表', (75, 63, 140), (255, 255, 255))],
    'o11': [('q', '下一个字', (255, 196, 40), INK), ('gray', '还没法写', (169, 165, 188), (255, 255, 255))],
    'o12': [('gpu', '显卡：上万个小核', (31, 94, 68), (255, 255, 255))],
    'o16': [('small', '小模型', (75, 63, 140), (255, 255, 255))],
    'o17': [('big', '大模型', (75, 63, 140), (255, 255, 255))],
    'o18': [('w1', '写 1 个字', (255, 196, 40), INK), ('w4', '批改 4 个字', (253, 251, 246), INK)],
    'o19': [('mem', '显存：存着参数', (111, 134, 201), (255, 255, 255)), ('core', '计算核心', (31, 94, 68), (255, 255, 255))],
    'o20': [('core', '计算核心', (31, 94, 68), (255, 255, 255))],
    'o21': [('own', '大模型自己的', (255, 196, 40), INK)],
    'n_easy': [('small', '小模型', (75, 63, 140), (255, 255, 255)), ('easy', '好猜', (253, 251, 246), INK)],
    'n_hard': [('hard', '难猜：海边做什么？', (253, 251, 246), INK), ('count', '这一步出了 3 个', (255, 196, 40), INK)],
    'n_accept': [('top', '投机解码写的', (253, 251, 246), INK), ('bot', '大模型自己写的', (75, 63, 140), (255, 255, 255))],
    'n_timing': [('move', '搬：约 16 毫秒', (111, 134, 201), (255, 255, 255)), ('calc', '算：约 0.1 毫秒（放大）', (31, 94, 68), (255, 255, 255))],
}

def compose(png, js):
    meta = json.load(open(js)); b, u = meta['beat'], meta['u']; fn = meta.get('fn', '')
    im = grain(Image.open(png).convert('RGB').resize((1080, 1920), Image.LANCZOS), 5.0, seed=b)
    P = {k: (v[0] * 1080, (1 - v[1]) * 1920) for k, v in meta['anch'].items()}
    for (k, text, bg, fg) in CHIPS.get(fn, []):
        if fn == 'o1' and k == 'qu' and u < 0.35: continue   # 「去」还没浮出来时不挂标签
        if k in P: chip(im, P[k][0], P[k][1], text, bg, fg)
    if fn == 'o4' and 'row' in P:
        chip(im, P['row'][0], P['row'][1], '第一轮：整句送进去' if u < 0.4 else '之后：只送新写的那个字', (253, 251, 246), INK)
    if fn in ('o6', 'n_tail'):   # 观众要读的数字一屏最多 3 个：只标前三名
        for i, pct in enumerate(['41%', '18%', '12%']):
            if f'p{i}' in P: chip(im, P[f'p{i}'][0] + 30, P[f'p{i}'][1], pct, (255, 196, 40) if i == 0 else (253, 251, 246), INK, size=34)
    if fn == 'o1': title(im)
    if fn == 'o23': sketch_frame(im)
    if fn == 'o24': big_end(im)
    if fn == 'o25': end_card(im)
    text, note, analog = CAPS[b]
    if fn != 'o24' or u > 0.15:   # 片尾大字先出，字幕晚 0.6 秒
        caption(im, text, note, analog)
    return im

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]; os.makedirs(dst, exist_ok=True)
    for png in sorted(glob.glob(os.path.join(src, '*.png'))):
        js = png[:-4] + '.json'
        if os.path.exists(js): compose(png, js).save(os.path.join(dst, os.path.basename(png)))
