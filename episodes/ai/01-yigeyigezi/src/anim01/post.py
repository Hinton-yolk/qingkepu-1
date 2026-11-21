# 2D 提示层 + 音效 + 编码 + 轨迹图 + 关键构图帧。
# 用法：python3 post.py <a|b|c> <3D 帧目录> <输出目录>
# 2D 层只放简短提示（标签条），不放大段字幕；提示挂在 3D 物体投影到屏幕的锚点上，跟着物体走。
import sys, os, glob, json, math, subprocess
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v03_time
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
LABELS['int2'] = [
    ('prefix', '已有文字', 'g', 0.2, 1.6, -70), ('cells', '每个字先变成一串数（示意）', 'w', 1.0, 2.8, 120),
    ('gather', '回看前文（示意）', 'g', 3.0, 4.9, -60), ('pill', '下一个字的候选', 'w', 7.9, 9.3, -60),
    ('fork_u', '一种可能的续写（假设）', 'w', 11.2, 14.2, -80), ('fork_d', '另一种可能', 'w', 11.6, 14.2, 80),
    ('qu', '选定「去」', 'a', 15.6, 17.2, -80), ('out', '正式输出', 'g', 18.0, 19.6, -80),
    ('small', '小模型', 'g', 20.4, 21.8, -60), ('drafts', '草稿（还没确认）', 'w', 21.9, 22.9, -70),
    ('ver', '大模型：集中验证', 'g', 22.9, 24.0, -40), ('acc', '接受', 't', 24.2, 24.9, -70), ('chi', '未接受', 'a', 25.0, 26.0, -70),
    ('kan', '补充候选', 'a', 29.1, 30.4, -70)]
LABELS['full'] = [
    ('scr', '真实的生成单位是 token，不一定正好是一个字', 'w', 3.9, 5.4, 0), ('scr', '倒回去：下一个字是怎么来的？', 'a', 5.5, 7.4, 0),
    ('prefix', '已有文字', 'g', 10.2, 11.6, -70), ('cells', '每个字先变成一串数（示意）', 'w', 11.0, 12.8, 120),
    ('gather', '回看前文（示意）', 'g', 13.0, 14.9, -60), ('pill', '下一个位置的候选', 'w', 17.9, 19.3, -60),
    ('fork_u', '一种可能的续写（假设）', 'w', 21.2, 24.2, -80), ('fork_d', '另一种可能', 'w', 21.6, 24.2, 80),
    ('qu', '选定「去」', 'a', 25.6, 27.2, -80), ('ctx', '上下文更新：周末我想去', 'g', 27.6, 29.4, -80),
    ('park', '前面算过的结果留着，不重算（示意）', 'w', 31.2, 32.6, -60), ('c4', '下一个位置的候选', 'w', 33.9, 35.0, -60),
    ('step', '每一步，都要等上一步定下来', 'g', 35.3, 39.6, -90),
    ('small', '小模型：先猜几步', 'g', 43.0, 44.5, -60), ('ver', '大模型：集中验证', 'g', 45.5, 46.6, -40),
    ('acc', '接受', 't', 46.8, 47.5, -70), ('chi', '未接受', 'a', 47.6, 48.6, -70), ('kan', '补充候选', 'a', 51.6, 52.9, -70)]
TITLES = {'full': [('AI 为什么一个字一个字往外蹦？', 0.3, 5.2, 330, 52), ('能不能先猜几步，再一起检查？', 40.6, 42.9, 330, 48),
                   ('每一步，都建立在前一步之上。', 58.7, 64.5, 300, 46), ('但有些步骤，可以先猜、再验证。', 60.3, 64.5, 400, 46)]}
TITLE = {'c': ('小模型先猜，大模型集中验证', 13.6, 17.0)}
# ---- V02：时间都写成「场景时间」（shot_v02.py 的时间）；成片里第二、四幕被压紧，提示跟着压紧 ----
LABELS['v02'] = [
    ('scr', '生成单位其实是 token（不一定正好一个字）', 'w', 2.6, 4.6, 260), ('scr', '倒回去：下一个字是怎么来的？', 'a', 5.5, 7.4, 0),
    ('prefix', '已有文字', 'g', 10.2, 11.6, -70), ('cells', '每个字先变成一串数（示意）', 'w', 11.0, 12.8, 120),
    ('gather', '回看前文（示意）', 'g', 13.0, 14.9, -60), ('pill', '下一个位置的候选', 'w', 17.9, 19.3, -60),
    ('fork_u', '一种可能的续写（假设）', 'w', 21.2, 24.2, -80), ('fork_d', '另一种可能', 'w', 21.6, 24.2, 80),
    ('qu', '选定「去」', 'a', 25.6, 27.2, -80), ('ctx', '上下文更新：周末我想去', 'g', 27.6, 29.4, -80),
    ('park', '前面算过的结果留着，不重算（示意）', 'w', 31.2, 32.6, -60), ('c4', '下一个位置的候选', 'w', 33.9, 34.7, -60),
    ('step', '大模型第 1 轮 → 海', 'g', 34.8, 36.3, -90), ('step', '第 2 轮：等「海」写定 → 边', 'g', 36.3, 37.8, -90),
    ('step', '第 3 轮：等「边」写定 → 看', 'g', 37.8, 39.5, -90),
    ('ctx', '起点：周末我想去', 'a', 40.9, 43.2, -80),
    ('small', '小模型：先猜几步', 'g', 45.3, 47.0, -60), ('drafts', '草稿：还不算数', 'w', 47.0, 48.5, -80),
    ('ver', '大模型：一轮处理，评估 4 个位置', 'g', 48.6, 51.2, -40), ('under', '每个位置只看它前面的字', 't', 49.2, 51.2, 40),
    ('acc', '接受', 't', 51.5, 52.9, -70), ('chi', '未接受', 'a', 52.4, 53.8, -70), ('fan', '跟着作废', 'w', 52.7, 53.8, -165),
    ('res', '写进正式输出', 'g', 54.4, 55.6, -60), ('kan', '这一位用大模型自己的结果', 'a', 57.4, 58.9, -70)]
TITLES['v02'] = [('AI 为什么一个字一个字往外蹦？', 0.3, 4.6, 330, 52),
                 ('做法一：一步一步，每步等上一步写定', 34.6, 39.5, 300, 40),
                 ('回到同一个起点，换一种办法。', 40.3, 43.4, 330, 46), ('做法二：先猜几步，再一起验收', 43.6, 48.4, 300, 40),
                 ('接受与否按两个模型的概率规则（示意），不看意思通不通', 51.3, 53.9, 1420, 32),
                 ('一步一步：大模型 3 轮 → 海 边 看', 59.1, 62.7, 300, 42), ('先猜再验：大模型 1 轮 → 海 边 看', 59.7, 62.7, 390, 42),
                 ('另加小模型猜草稿；条件合适时，整体更快', 60.4, 62.7, 470, 34),
                 ('每一步，都建立在前一步之上。', 66.5, 72.0, 300, 46), ('但可以先猜几步，再一起验收。', 68.1, 72.0, 400, 46)]

# ---- V03（观众优先重剪）：时间都写成场景时间（shot_v03.py）；成片时间由 v03_time 映射 ----
# 信息分三级：一级 = 画面上方的大字（同一时刻只有一句）；二级 = 挂在物体上的短标签；三级 = 底部的小字限定（不和主要动作抢）
_S5, _E0 = 49.6, 49.6 + 15.4; _EB = _E0 + 3.6; _TC = 49.6 + 25.0; _DUR = 79.0
LABELS['v03'] = [
    ('pill', '候选和分数：模型现算的（示意）', 'w', 7.9, 9.4, -150),
    ('cells', '每个字先变成一串数（示意）', 'w', 11.0, 12.8, 120), ('gate', '大模型', 'g', 11.7, 13.6, -40),
    ('gather', '回看前文（示意）', 'g', 13.0, 14.9, -60), ('pill', '下一个字的候选', 'w', 17.9, 19.4, -60),
    ('fork_u', '出门：去海边看日落', 'w', 21.6, 24.3, -90), ('fork_d', '宅家：睡个懒觉', 'w', 21.9, 24.3, 100),
    ('qu', '选定「去」', 'a', 25.4, 27.2, -80), ('ctx', '上下文：周末我想去', 'g', 27.4, 29.4, -80),
    ('park', '算过的留着，不重算（示意）', 'w', 31.2, 32.6, -60),
    ('step', '第 1 步 → 海', 'g', 34.9, 35.6, -90), ('ctx', '「海」并进上下文', 't', 35.6, 37.3, -80),
    ('c4', '候选整组换了', 'w', 37.5, 38.6, -70), ('step', '第 2 步 → 边', 'g', 38.1, 38.9, -90),
    ('ctx', '「边」也并进上下文', 't', 38.9, 39.6, -80), ('step', '第 3 步 → 看', 'g', 40.4, 41.2, -90),
    ('ctx', '起点：周末我想去', 'a', 45.2, 47.0, -80),
    ('small', '小模型（更小，也要算）', 'g', 49.3, 51.7, -70), ('drafts', '草稿：还不算数', 'w', 51.0, 52.6, -90),
    ('park5', '每个位置只看它前面的字', 't', _S5 + 4.4, _S5 + 5.9, -60),
    ('picks', '大模型每一位的首选', 'a', _S5 + 6.9, _S5 + 8.2, -60),
    ('d0', '一致 → 接受', 't', _S5 + 8.5, _S5 + 9.25, -70), ('d1', '一致 → 接受', 't', _S5 + 9.2, _S5 + 9.95, -70),
    ('d2', '不一致', 'a', _S5 + 10.0, _S5 + 11.0, 190), ('d3', '后面的跟着作废', 'w', _S5 + 10.3, _S5 + 11.6, 270),
    ('d2', '用大模型的首选', 'a', _S5 + 11.9, _S5 + 13.0, -170),
    ('rowA', '一步一步', 'g', _E0 - 0.3, _E0 + 9.5, 0), ('rowB', '先猜再验', 'g', _EB - 0.6, _E0 + 9.5, 0),
    ('talA', '大模型 3 轮', 'a', _E0 + 3.3, _E0 + 9.5, 0), ('talB', '小模型 4 步 + 大模型 1 轮', 'a', _EB + 3.0, _E0 + 9.5, 0)]
TITLES['v03'] = [('AI 的下一个字，还没定？', 3.6, 7.7, 300, 64),
                 ('倒回去看：候选怎么算出来的？', 9.3, 11.2, 300, 50),
                 ('选不同，后面也不同', 22.4, 25.1, 300, 60),
                 ('下一步，要等上一步确定。', 41.3, 43.8, 300, 58),
                 ('回到同一个起点，换一种办法。', 44.0, 46.9, 300, 52),
                 ('既然要一步步来，能不能先猜几步？', 47.1, 49.6, 300, 48),
                 ('小模型：先猜 4 步', 49.7, 51.9, 300, 56),
                 ('大模型：一趟，4 个位置一起算', _S5 + 2.3, _S5 + 5.7, 300, 50),
                 ('大模型算 1 轮，写下 3 个字', _S5 + 12.8, _S5 + 15.0, 300, 52),
                 ('两种做法，大模型各算几轮？', _E0 - 0.2, _EB + 2.8, 300, 50),
                 ('大模型少等几轮，才有机会更快', _EB + 3.0, _E0 + 9.6, 300, 48),
                 ('每一步，都建立在前一步之上。', _TC + 0.8, _DUR + 1, 300, 50), ('但可以先猜几步，再一起验收。', _TC + 2.0, _DUR + 1, 400, 50),
                 # 三级：底部小字
                 ('示意：生成单位是 token，不一定正好一个字', 17.9, 20.6, 1480, 34),
                 ('示意：按「取最高分」对照；按概率采样时，用概率规则验收', _S5 + 8.2, _S5 + 12.7, 1480, 32),
                 ('小模型也要算；草稿常猜错时，就省不下来', _EB + 3.0, _E0 + 9.6, 1480, 34)]
TIMEMAP = None   # [(成片时间, 场景时间)]，由 __main__ 读入

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
    for (text, t0, t1, y, sz) in TITLES.get(shot, []):
        a = fade(t, t0, t1, 0.4)
        if a > 0: chip(lay, 540, y, text, 'w' if y > 1400 else 'g', size=sz, alpha=a)
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
    elif shot == 'full':
        E0, _ = events('int2')
        E = [(t0 + (10.0 if t0 < 18.0 else 22.6), sig) for t0, sig in E0 if t0 < 17.9 or t0 >= 18.2]
        E += [(0.8 + 0.32 * i, blip(hz(84 + (i % 5)), 0.08, 0.3)) for i in range(10)] + [(5.4 + 0.12 * k, blip(hz(76 - k), 0.06, 0.25)) for k in range(6)]
        E += [(6.4 + 0.25 * k, whoosh(1.0, True, 0.25)) for k in range(4)] + [(8.0 + 0.25 * k, thud(0.35)) for k in range(4)]
        E += [(28.6, blip(hz(78), g=0.3)), (29.5, whoosh(1.4, True, 0.3)), (31.0, bell(hz(79), 0.8, 0.3)), (31.6, blip(hz(90), 0.08, 0.25)), (32.1, bell(hz(86), 1.0, 0.4)),
              (32.5, whoosh(1.1, False, 0.3)), (33.6, whoosh(0.7, True, 0.35)), (34.4, bell(hz(81), 0.9, 0.35))]
        for i, c0 in enumerate([34.9 + 1.5 * k for k in range(3)]): E += [(c0, whoosh(0.5, False, 0.25)), (c0 + 0.6, thud(0.4)), (c0 + 0.7, blip(hz(74 + 2 * i), 0.1, 0.3))]
        E += [(39.6, whoosh(1.1, False, 0.3)), (40.6, bell(hz(88), 1.4, 0.35))]
        E += [(55.0 + 0.2 * i, blip(hz(74 + i), 0.08, 0.28)) for i in range(8)] + [(58.0, blip(hz(84), 0.08, 0.3)), (58.35, blip(hz(86), 0.08, 0.3)), (58.7, bell(hz(74), 2.6, 0.4)), (60.3, bell(hz(81), 2.4, 0.35))]
        N = int(64.5 * SR); P = np.zeros(N)
        for t0, d, ch in ((0.0, 10.4, [50, 57, 62, 66]), (10.0, 10.0, [47, 54, 59, 62]), (18.8, 10.5, [50, 57, 62, 66]), (28.4, 12.6, [45, 52, 57, 61]), (40.6, 14.2, [43, 50, 55, 59]), (54.6, 9.9, [50, 57, 62, 66])):
            x = pad(d, ch); i = int(t0 * SR); n = min(len(x), N - i); P[i:i + n] += x[:n]
    elif shot == 'v02':
        E0, _ = events('full')
        S = [(t0, sig) for t0, sig in E0 if 5.3 <= t0 < 39.5]                       # 第一幕倒回之后到第四幕结束：和 V01 相同
        S += [(T, blip(hz(84 + (i % 5)), 0.08, 0.3)) for i, T in enumerate([0.6 + 0.08 * i for i in range(4)] + [1.3 + 0.38 * i for i in range(6)])]
        S += [(40.3, bell(hz(81), 1.6, 0.3))] + [(41.2 + 0.12 * k, blip(hz(74 + 2 * k), 0.08, 0.25)) for k in range(5)]
        S += [(43.0, whoosh(1.8, True, 0.3)), (45.0, thud(0.5))]
        S += [(45.4 + 0.4 * j, blip(hz(84 + j), 0.1, 0.4)) for j in range(4)] + [(45.5 + 0.4 * j, whoosh(1.2, False, 0.15)) for j in range(4)]
        S += [(48.6, whoosh(0.8, True, 0.35))] + [(49.35, bell(hz(m), 1.4, 0.3)) for m in (79, 83, 86, 91)]   # 4 个位置一个和弦：同一轮
        S += [(51.4, bell(hz(83), g=0.45)), (51.9, bell(hz(86), g=0.45)), (52.4, thud(0.8)), (52.5, blip(hz(55), 0.3, 0.3)), (52.75, blip(hz(50), 0.25, 0.25))]
        S += [(53.8, whoosh(1.2, False, 0.3)), (55.2, thud(0.6)), (55.45, thud(0.6)), (55.6, whoosh(1.3, True, 0.3)), (56.95, thud(0.45))]
        S += [(56.9, bell(hz(74), 0.6, 0.3)), (57.2, whoosh(0.8, True, 0.35)), (58.8, thud(0.8))]
        S += [(59.1, blip(hz(79), 0.12, 0.35)), (59.7, blip(hz(86), 0.12, 0.35)), (60.4, bell(hz(91), 1.6, 0.3))]
        S += [(62.8 + 0.2 * i, blip(hz(74 + i), 0.08, 0.28)) for i in range(8)] + [(65.8, blip(hz(84), 0.08, 0.3)), (66.15, blip(hz(86), 0.08, 0.3)), (66.5, bell(hz(74), 2.6, 0.4)), (68.1, bell(hz(81), 2.4, 0.35))]
        ft, st = np.array(TIMEMAP).T
        sc2f = lambda x: float(np.interp(x, st, ft))
        E = [(sc2f(t0), sig) for t0, sig in S]
        N = int(ft[-1] * SR) + SR; P = np.zeros(N)
        for a, b, ch in ((0.0, 10.4, [50, 57, 62, 66]), (10.0, 20.0, [47, 54, 59, 62]), (18.8, 29.3, [50, 57, 62, 66]), (28.4, 40.2, [45, 52, 57, 61]),
                         (40.0, 48.6, [43, 50, 55, 59]), (48.3, 53.9, [45, 52, 57, 60]), (53.6, 63.0, [41, 48, 53, 57]), (62.6, 72.0, [50, 57, 62, 66])):
            fa, fb = sc2f(a), sc2f(b); x = pad(fb - fa, ch); i = int(fa * SR); n = min(len(x), N - i); P[i:i + n] += x[:n]
    elif shot == 'v03':
        S = []
        for k in range(6): S += [(4.4 + 0.35 + 0.59 * k, blip(hz(76 if k % 2 == 0 else 71), 0.1, 0.3))]   # 钩子：两个候选轮流往空位里探
        S += [(4.45, thud(0.45)), (7.0, whoosh(1.1, True, 0.35)), (7.9, bell(hz(81), 1.2, 0.35)), (8.9, whoosh(1.0, False, 0.3))]
        E0_, _ = events('int2')
        S += [(t0 + 10.0, sig) for t0, sig in E0_ if 0.3 < t0 < 17.9]                          # 第二幕 + 分叉（和 V01 同一套）
        S += [(22.25, blip(hz(62), 0.3, 0.25)), (22.4, bell(hz(86), 1.2, 0.3))]               # 「觉」躺下；揭晓
        E1_, _ = events('full')
        S += [(t0, sig) for t0, sig in E1_ if 28.5 <= t0 < 34.8]                               # 「去」进模型
        for i, c0 in enumerate([34.9, 38.1, 40.5]): S += [(c0, whoosh(0.5, False, 0.25)), (c0 + 0.6, thud(0.45)), (c0 + 0.65, blip(hz(74 + 3 * i), 0.1, 0.3))]
        for a in (35.55, 38.7): S += [(a, bell(hz(79), 0.9, 0.3)), (a + 0.4, whoosh(0.9, True, 0.25))]
        for a in (37.45, 39.85): S += [(a + 0.1 * k, blip(hz(81 + 2 * k), 0.08, 0.25)) for k in range(3)]
        S += [(41.3 + 0.35 * i, bell(hz(m), 1.4, 0.35)) for i, m in enumerate((74, 78, 81))]
        S += [(43.8 + 0.25 * k, whoosh(0.8, False, 0.22)) for k in range(3)] + [(45.3 + 0.14 * k, blip(hz(74 + 2 * k), 0.08, 0.25)) for k in range(5)]
        S += [(47.1, bell(hz(88), 1.6, 0.3)), (47.3, whoosh(1.4, False, 0.3)), (48.6, thud(0.4))]
        S += [(_S5 + 0.26 * j, blip(hz(91 + j), 0.07, 0.3)) for j in range(4)] + [(_S5 + 0.26 * j + 0.7, thud(0.25)) for j in range(4)]
        S += [(_S5 + 2.0 + 0.1 * k, blip(hz(83 + k), 0.06, 0.2)) for k in range(4)] + [(_S5 + 2.9, whoosh(1.4, True, 0.35))] + [(_S5 + 3.3 + 0.4 * g, thud(0.35)) for g in range(3)]
        S += [(_S5 + 4.4, whoosh(0.6, True, 0.2))] + [(_S5 + 5.25, bell(hz(m), 1.8, 0.32)) for m in (72, 76, 79, 84)]   # 同一趟：4 个位置一个和弦
        S += [(_S5 + 5.7, whoosh(1.2, False, 0.3)), (_S5 + 6.9, bell(hz(81), 1.2, 0.3)), (_S5 + 6.95, bell(hz(88), 1.2, 0.25))]
        S += [(_S5 + 8.65, bell(hz(83), g=0.45)), (_S5 + 9.35, bell(hz(86), g=0.45)), (_S5 + 10.0, thud(0.8)), (_S5 + 10.1, blip(hz(55), 0.3, 0.3)), (_S5 + 10.35, blip(hz(50), 0.25, 0.25))]
        S += [(_S5 + 10.6, whoosh(1.2, True, 0.3)), (_S5 + 11.7, whoosh(0.7, False, 0.3)), (_S5 + 12.4, thud(0.7)), (_S5 + 12.8, bell(hz(79), 2.0, 0.35)), (_S5 + 13.1, bell(hz(86), 2.0, 0.3))]
        for k in range(3): a = _E0 + 0.4 + 1.0 * k; S += [(a + 0.2, thud(0.5)), (a + 0.3, bell(hz(74), 0.8, 0.3)), (a + 0.8, blip(hz(79 + 2 * k), 0.08, 0.3))]
        S += [(_EB + 0.3 * j + 0.1, blip(hz(93), 0.05, 0.25)) for j in range(4)] + [(_EB + 1.8, thud(0.5)), (_EB + 1.9, bell(hz(74), 0.8, 0.3)), (_EB + 2.2, bell(hz(83), 1.2, 0.35)), (_EB + 2.5, blip(hz(55), 0.25, 0.25)), (_EB + 3.0, bell(hz(86), 1.6, 0.3))]
        S += [(_TC + 0.1, whoosh(1.2, False, 0.3)), (_TC + 0.9, blip(hz(76), 0.1, 0.3)), (_TC + 1.05, blip(hz(71), 0.1, 0.3)), (_TC + 0.8, bell(hz(74), 2.6, 0.35)), (_TC + 2.0, bell(hz(81), 2.4, 0.3))]
        sc2f = lambda x: v03_time.scene_to_film(x)
        E = [(sc2f(t0), sig) for t0, sig in S if t0 >= 4.4]
        N = int(v03_time.FILM_DUR * SR) + SR; P = np.zeros(N)
        for a, b, ch in ((4.4, 10.6, [45, 52, 57, 60]), (10.4, 19.8, [47, 54, 59, 62]), (19.6, 28.6, [50, 57, 62, 66]), (28.4, 41.0, [45, 52, 57, 61]),
                         (41.3, 47.2, [43, 50, 55, 59]), (47.1, _S5 + 5.0, [48, 55, 60, 64]), (_S5 + 5.25, _S5 + 12.6, [41, 48, 53, 57]),
                         (_S5 + 12.8, _E0 + 0.2, [53, 60, 65, 69]), (_E0, _TC + 0.4, [50, 57, 62, 66]), (_TC + 0.2, _DUR + 0.5, [45, 52, 57, 64])):
            fa, fb = sc2f(a), sc2f(b); x = pad(fb - fa, ch); i = int(fa * SR); n = min(len(x), N - i); P[i:i + n] += x[:n]
    elif shot == 'int2':
        E += [(0.4 + 0.25 * k + 0.3, blip(hz(71 + 3 * k), g=0.3)) for k in range(4)] + [(1.9, whoosh(1.0, True, 0.35))]
        E += [(3.0 + 0.12 * k, blip(hz(83 + k), 0.1, 0.25)) for k in range(3)] + [(3.55, bell(hz(79), 0.8, 0.3))] + [(3.9 + 0.1 * k, blip(hz(90 - k), 0.08, 0.25)) for k in range(3)]
        E += [(4.45, bell(hz(86), 1.2, 0.45)), (4.95, whoosh(1.0, True, 0.3)), (5.9, whoosh(1.3, False, 0.35))]
        E += [(7.1 + 0.07 * j, blip(hz(86 - j), 0.08, 0.25)) for j in range(6)] + [(7.6, whoosh(0.7, True, 0.4)), (8.3, bell(hz(81), 1.0, 0.35))]
        E += [(8.7, whoosh(1.2, True, 0.35)), (10.0, thud(0.4)), (10.25, thud(0.35))] + [(10.3 + k * 0.42, blip(hz(74 + 2 * k), g=0.28)) for k in range(5)] + [(10.5 + k * 0.42, blip(hz(69 + 2 * k), g=0.24)) for k in range(3)]
        E += [(14.0, bell(hz(81), g=0.45)), (14.6, whoosh(1.4, False, 0.35)), (15.4, whoosh(1.2, False, 0.35)), (16.7, thud(0.7)), (17.4, whoosh(1.0, False, 0.25)), (18.2, whoosh(1.8, True, 0.25))]
        E += [(20.4 + 0.4 * j, blip(hz(84 + j), 0.1, 0.4)) for j in range(4)] + [(20.5 + 0.4 * j, whoosh(1.2, False, 0.15)) for j in range(4)]
        E += [(22.9, whoosh(1.0, True, 0.45)), (23.6, bell(hz(88), 1.0, 0.3))]
        E += [(24.1, bell(hz(83), g=0.5)), (24.5, bell(hz(86), g=0.5)), (24.9, thud(0.9)), (25.0, blip(hz(55), 0.3, 0.35))]
        E += [(25.6, whoosh(1.2, False, 0.35)), (27.0, thud(0.6)), (27.25, thud(0.6)), (27.3, whoosh(1.3, True, 0.3)), (28.55, thud(0.45))]
        E += [(28.4, bell(hz(74), 0.6, 0.3)), (28.8, whoosh(0.8, True, 0.35)), (30.3, thud(0.8)), (30.6, bell(hz(86), 1.4, 0.3))]
        N = int(32.0 * SR); P = np.zeros(N)
        for t0, d, ch in ((0.0, 10.0, [47, 54, 59, 62]), (8.8, 10.5, [50, 57, 62, 66]), (18.2, 13.8, [43, 50, 55, 59])):
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
    tmp = os.path.join(src, '..', 'timemap.json')
    if shot == 'v02': TIMEMAP = json.load(open(tmp))
    from multiprocessing import Pool
    def job(i):
        o = os.path.join(out, 'comp_' + shot, f'f{i:05d}.jpg')
        if not os.path.exists(o): compose(shot, pngs[i], metas[i]).save(o, quality=92)
    with Pool(4) as pool: pool.map(job, range(len(pngs)))
    dur = len(pngs) / 30.0
    name = {'a': 'AnimationTest_A_Branch', 'b': 'AnimationTest_B_ModelFlow', 'c': 'AnimationTest_C_SpeculativeDecoding', 'int': 'EP01_IntegratedAnimation_Test01', 'int2': 'EP01_IntegratedAnimation_Test02', 'full': 'EP01_FullMotionDraft_v01', 'v02': 'EP01_FullMotionDraft_v02', 'v03': 'EP01_AudienceFirst_v03'}[shot]
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
