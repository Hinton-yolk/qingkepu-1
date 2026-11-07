# 纯动画版（无旁白）时间表：python3 tools/build_nv.py → 代码工程/split/s1n.json
# 不再按配音排时间：所有动作落在 129 BPM 的拍点上。画面代码沿用 k1.js（它用 kw(句号, '词') 取时间），
# 所以这里造一组「虚拟句子」：每句只给几个关键词的时刻（落在拍点上），中间的字按比例插值。
import json
BPM = 129; B = 60 / BPM; bar = 4 * B
at = lambda bars, beats=0: round(bars * bar + beats * B, 3)
S = json.load(open('/home/user/kepu-studio/episodes/guanghulian/02-serdes/douyin-split/script_s1.json', encoding='utf-8'))
TXT = {x['id']: x['text'] for x in S}
# 每句：(t0, t1, {关键词: 时刻}, seg)
CUE = {
 'p01': (0.0, at(1), {}, 'open'),
 'p02': (at(1), at(2), {'芯片': at(1, 1)}, 'open'),
 'p02b': (at(2), at(3), {'快递': at(2, 1)}, 'open'),
 'p03': (at(3), at(4, 2), {'切成': at(3), '一起送': at(3, 3)}, 'explain'),
 'p04': (at(4, 2), at(6), {'慢的时候': at(4, 2), '严丝合缝': at(5, 2)}, 'explain'),
 'p05': (at(6), at(8, 3), {'一快': at(6), '紧跟着': at(6, 2), '长了一点点': at(7), '晚到半步': at(7, 2), '拼进': at(8)}, 'reveal'),
 'p06': (at(9), at(10), {}, 'reveal'),
 'p07': (at(10), at(11, 2), {'错一位': at(10, 2)}, 'reveal'),
 'p08': (at(11, 2), at(12, 2), {}, 'reveal'),
 'p09': (at(12, 2), at(15), {'只修几条路': at(12, 2), '排成一队': at(13, 2), '越跑越快': at(14)}, 'reveal'),
 'p10': (at(15, 1), at(15, 2), {}, 'end'),
 'p11': (at(15, 2), at(16, 2), {'路少': at(15, 2), '不会乱': at(16)}, 'end'),
 'p12': (at(16, 2), at(17, 2), {}, 'end'),
}
lines = []
for i, (t0, t1, kws, seg) in CUE.items():
    text = TXT[i]; n = len(text); anchors = sorted([(text.index(w), t) for w, t in kws.items()] + [(0, t0), (n, t1)])
    ch = []
    for j in range(n):
        a = max((p for p in anchors if p[0] <= j), key=lambda p: p[0]); b = min((p for p in anchors if p[0] > j), key=lambda p: p[0], default=(n, t1))
        ch.append(round(a[1] + (b[1] - a[1]) * (j - a[0]) / max(1, b[0] - a[0]), 3))
    lines.append(dict(id=i, t0=t0, t1=t1, clip=t0, text=text, ch=ch, sub=None, big=None, seg=seg, src=''))
TK = lambda text, line, a=None, b=None: dict(text=text, line=line, **{'from': a}, to=b)
dur = at(17, 2) + 0.4
shots = [dict(kind='photo', t0=0, first='p01'), dict(kind='route', t0=at(2), first='p02b', topic=''), dict(kind='strips', t0=at(3) - 0.1, first='p03'),
         dict(kind='serial', t0=at(12, 2) - 0.2, first='p09'), dict(kind='take', t0=at(15), first='p10', cy=700, type=[TK('一句话带走', 'p10'), TK('路少，', 'p11', '路少', '路少'), TK('反而不会乱。', 'p11', '反而', '不会乱')])]
for s in shots: s['paper'] = s['kind'] == 'take'
for k in range(len(shots)): shots[k]['t1'] = shots[k + 1]['t0'] if k + 1 < len(shots) else dur
# 贴在画面里的短字（只补画面标注没说到的）：[开始, 结束, 字, x, y]
caps = [[0.0, at(1, 2), '照片怎么错位了？', 540, 260], [at(10) + 0.2, at(11, 2), '转账错一位，也一样', 540, 330], [at(12, 2), at(13, 2), '所以：只修几条路', 540, 1300]]
json.dump(dict(name='s1n', dur=round(dur, 3), lines=lines, shots=shots, hudIn=at(3) - 0.3, caps=caps, bpm=BPM, novoice=True), open('代码工程/split/s1n.json', 'w'), ensure_ascii=False)
print('s1n dur', round(dur, 2), 's; beat', round(B, 4))
