# EP.01 新画风 2D 层：字幕（照用户确认的脚本 v2.1 原文）、小字、「类比」标签、标签条、大字问题、片尾大字、片尾卡、细颗粒。
# 用法：python3 film_overlay.py <3D 帧目录> <输出目录>        （帧名 bNN.png / tTTT.TT.png，旁边有同名 .json）
import sys, os, json, glob
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overlay import f, NOTO, NOTO_R, SMILEY, INK, YEL, grain, chip

ORANGE = (255, 154, 60)
# 每拍：(字幕两行，{} = 黄色关键词；小字；是否挂「类比」标签)
CAPS = {
    1: ('它不是在打字给你看', '', False),
    2: ('你以为它早就写好了整段，/故意一个字一个字放给你看？', '', False),
    3: ('不是。/它真的只能{一个字一个字}地写', '有的 App 会再匀速显示，但模型确实是一个个生成的', False),
    4: ('每写一个字，/都要把模型{从头到尾}过一遍', '动辄几百亿个参数 · 混合专家模型每个字只用其中一部分，但每一层都要过', False),
    5: ('还要回头看一遍/{前面所有的字}', '前面的字算过的结果存着，不重算；但每次都要再看一遍 · 句子越长，线越多', False),
    6: ('给每个可能的下一个字/{打个分}', '分数为示意', False),
    7: ('{抽}一个，接上，再来一遍', '通常按分数抽签（也可以设成总选第一名）', False),
    8: ('为什么不能/{几个字一起写}？', '', False),
    9: ('这里选了「海」，/后面是「边看日落」', '', False),
    10: ('选了「睡」，/后面就成了「个懒觉」', '', False),
    11: ('前一个字没定，/后面的字{没法写}', '', False),
    12: ('显卡再多核，/也只能{一个字接一个字}', '每层里的乘加并行算；同一句话里，字和字只能排队 · 实际服务会把很多人的请求拼在一起算', False),
    13: ('可 AI {学说话}的时候，/一整段能同时算', '学说话 = 训练', True),
    14: ('因为整段话是{现成的}：/不用等它自己选下一个字', '训练时拿现成的文章让它逐字猜，猜完一起对答案', False),
    15: ('那就先造一段/{「现成的」话}', '', False),
    16: ('让一个小模型/先{抢答}几个字', '小模型参数少得多，写得快，但没那么准', True),
    17: ('大模型{一次全部批改}', '这种方法叫投机解码（speculative decoding）', True),
    18: ('批改 4 个字，/和写 1 个字{差不多快}', '单条对话时', False),
    19: ('因为最慢的不是算，/是把参数{从显存搬过来}', '一个字一个字写的时候，显卡大多在等参数搬过来', False),
    20: ('搬一趟，/就能{顺便批好几个字}', '', False),
    21: ('对得上的全收下，/从第一个对不上的{接着来}', '对不上的字后面的草稿，是接着它猜的，一起作废', False),
    22: ('一步就出好几个字，/快 {2–3 倍}', '论文实测，单条对话，因模型而异 · 数学上保证和大模型自己逐字写的一样（标准做法）', False),
    23: ('一个字一个字蹦，是因为/{下一个字要等上一个}', '示意：用了投机解码后的效果', False),
    24: ('用这个办法，它可以/{几个字几个字}地蹦了', '', False),
    25: ('你还想知道 AI 的什么？/评论区告诉我', '', False),
}

def parse(line):
    out = []; buf = ''; y = False
    for ch in line:
        if ch == '{': out.append((buf, y)); buf = ''; y = True
        elif ch == '}': out.append((buf, y)); buf = ''; y = False
        else: buf += ch
    out.append((buf, y)); return [(s, c) for s, c in out if s]

def wrap_note(d, text, ft, maxw=900):
    """小字：最多两行；按「 · 」或按宽度断开"""
    parts = text.split(' · ')
    if len(parts) == 2 and all(d.textlength(p, font=ft) <= maxw for p in parts): return parts
    if d.textlength(text, font=ft) <= maxw: return [text]
    lines = ['']
    for ch in text:
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
        fn = f(NOTO_R, 32); nl = wrap_note(d, note, fn)
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

CHIPS = {   # 拍 → [(锚点, 文字, 底色, 字色, 条件 u)]
    1: [('qu', '一个字', (253, 251, 246), INK), ('q', '下一个字', (255, 196, 40), INK)],
    3: [('q', '下一个字', (255, 196, 40), INK)],
    4: [('model', '模型：一层一层', (75, 63, 140), (255, 255, 255))],
    11: [('q', '下一个字', (255, 196, 40), INK), ('gray', '还没法写', (169, 165, 188), (255, 255, 255))],
    12: [('gpu', '显卡：上万个小核', (31, 94, 68), (255, 255, 255))],
    16: [('small', '小模型', (75, 63, 140), (255, 255, 255))],
    17: [('big', '大模型', (75, 63, 140), (255, 255, 255))],
    18: [('w1', '写 1 个字', (255, 196, 40), INK), ('w4', '批改 4 个字', (253, 251, 246), INK)],
    19: [('mem', '显存：存着参数', (111, 134, 201), (255, 255, 255)), ('core', '计算核心', (31, 94, 68), (255, 255, 255))],
    20: [('core', '计算核心', (31, 94, 68), (255, 255, 255))],
}

def compose(png, js):
    meta = json.load(open(js)); b, u = meta['beat'], meta['u']
    im = grain(Image.open(png).convert('RGB').resize((1080, 1920), Image.LANCZOS), 5.0, seed=b)
    P = {k: (v[0] * 1080, (1 - v[1]) * 1920) for k, v in meta['anch'].items()}
    for (k, text, bg, fg) in CHIPS.get(b, []):
        if k in P: chip(im, P[k][0], P[k][1], text, bg, fg)
    if b == 4 and 'row' in P:
        chip(im, P['row'][0], P['row'][1], '第一轮：整句送进去' if u < 0.4 else '之后：只送新写的那个字', (253, 251, 246), INK)
    if b == 6:   # 观众要读的数字一屏最多 3 个：只标前三名
        for i, pct in enumerate(['41%', '18%', '12%']):
            if f'p{i}' in P: chip(im, P[f'p{i}'][0] + 30, P[f'p{i}'][1], pct, (255, 196, 40) if i == 0 else (253, 251, 246), INK, size=34)
    if b == 1: title(im)
    if b == 23: sketch_frame(im)
    if b == 24: big_end(im)
    if b == 25: end_card(im)
    text, note, analog = CAPS[b]
    if b != 24 or u > 0.15:   # 第 24 拍：片尾大字先出，字幕晚 0.6 秒
        caption(im, text, note, analog)
    return im

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]; os.makedirs(dst, exist_ok=True)
    for png in sorted(glob.glob(os.path.join(src, '*.png'))):
        js = png[:-4] + '.json'
        if os.path.exists(js): compose(png, js).save(os.path.join(dst, os.path.basename(png)))
