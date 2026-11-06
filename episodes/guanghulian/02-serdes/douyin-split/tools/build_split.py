# 抖音拆解版时间表：python3 tools/build_split.py s1 → 代码工程/split/s1.json
# 口播句子按 align 结果排上时间轴（同段句间 0.25 s，换段 0.45 s，开头两句之间 0.4 s 放慢）；
# 每个字给一个时间（按句内停顿切分句，分句里按字数线性分配），画面用 kw(id, '词') 取「说到这个词」的时刻。
import json, sys, re
N = sys.argv[1]; SRC = '/home/user/kepu-studio/episodes/guanghulian/02-serdes/douyin-split'
S = json.load(open(f'{SRC}/script_{N}.json')); A = json.load(open(f'{SRC}/align_{N}.json'))
ST = lambda i, l, a=None, b=None: dict(id=i, line=l, **{'from': a}, to=b)
SHOTS = {
 's1': [('bga', 'a01'), ('parallel', 'a04'), ('serdes', 'a05'), ('desk', 'a10', [ST('W0', 'a10', '为什么', '并排走'), ST('R1', 'a10', '第一', '不够')]), ('pins', 'a11'),
        ('desk', 'a13', [ST('Q1', 'a13', '第二', '到达')]), ('race', 'a14'), ('serial', 'a17'),
        ('take', 'a19', [ST('E0', 'a19'), ST('E1', 'a20', '速度', '对齐'), ST('E2', 'a20', '所以', '出发')])],
 's2': [('scope', 'b01'), ('stream', 'b04'), ('zoom', 'b07'), ('unpack', 'b09'), ('desk', 'b11', [ST('O5', 'b11', '连续', '1'), ST('O6', 'b11', '就是', '一起'), ST('O7', 'b11', '没有', '电平')]),
        ('level', 'b12'), ('cdr', 'b14'), ('take', 'b19', [ST('E0', 'b19'), ST('E3', 'b20', 'SerDes', '排队'), ST('E4', 'b20', '收到', '听准'), ST('E5', 'b20', '节拍', '一排')])],
 's3': [('spec', 'c01'), ('lanes', 'c04'), ('blur', 'c06'), ('seesaw', 'c09'), ('desk', 'c10', [ST('V1', 'c10', '很少', '出售')]), ('inside', 'c11'), ('three', 'c13'),
        ('take', 'c19', [ST('E0', 'c19'), ST('E6', 'c20', '难在', '读得准'), ST('Y2', 'c20', '路况', '路况'), ST('Y3', 'c20', '每比特', '的电'), ST('Y4', 'c20', '真实芯片', '没有')])],
}[N]
LEAD, TAIL = 0.35, 1.6
t = LEAD; lines = []; prev = None
for i, s in enumerate(S):
    a = A[s['id']]
    if prev is not None:
        t += 0.4 if i <= 2 else (0.45 if s['seg'] != prev['seg'] or s['id'] in [x[1] for x in SHOTS] else 0.25)
    t0 = t; t1 = t0 + (a['off'] - a['on'])
    # 分句时间：停顿数和分句边界数对得上就按停顿切，否则按字数比例
    cl = a['clauses']; n = [len(re.sub(r'\s', '', c)) for c in cl]; span = a['off'] - a['on']
    if len(a['pauses']) == len(cl) - 1:
        b = [a['on']] + [x for p in a['pauses'] for x in p] + [a['off']]; segs = [(b[2 * k], b[2 * k + 1]) for k in range(len(cl))]
    else:
        tot = sum(n); acc = 0; segs = []
        for k in n: segs.append((a['on'] + span * acc / tot, a['on'] + span * (acc + k) / tot)); acc += k
    ch = []
    for c, (u0, u1) in zip(cl, segs):
        cs = list(c)
        for j, _ in enumerate(cs): ch.append(round(t0 + (u0 - a['on']) + (u1 - u0) * j / max(1, len(cs)), 3))
    lines.append(dict(id=s['id'], t0=round(t0, 3), t1=round(t1, 3), clip=round(t0 - a['on'], 3), text=''.join(cl), ch=ch, sub=s['sub'], big=s['big'], seg=s['seg'], src=s['src']))
    t = t1; prev = s
dur = round(t + TAIL, 2)
L = {x['id']: x for x in lines}; shots = []
for k, (kind, first, *rest) in enumerate(SHOTS):
    a = 0 if k == 0 else round(L[first]['t0'] - 0.3, 3)
    sh = dict(kind=kind, t0=a, paper=kind in ('desk', 'take'), first=first)
    if rest: sh['strips'] = rest[0]
    if kind == 'take': sh['cy'] = 700
    if N == 's3' and kind == 'desk': sh['tape'] = dict(text='从投资角度')
    shots.append(sh)
for k in range(len(shots)): shots[k]['t1'] = shots[k + 1]['t0'] if k + 1 < len(shots) else dur
json.dump(dict(name=N, dur=dur, lines=lines, shots=shots, hudIn=shots[1]['t0']), open(f'/home/user/vox-ep02s/代码工程/split/{N}.json', 'w'), ensure_ascii=False)
print(N, 'dur', dur, [(s['kind'], s['t0']) for s in shots])
