# 抖音拆解版时间表：python3 tools/build_split.py s1 → 代码工程/split/s1.json
# 口播句子按 align 结果排上时间轴（同段句间 0.25 s，换段 0.45 s，开头两句之间 0.4 s 放慢）；
# 每个字给一个时间（按句内停顿切分句，分句里按字数线性分配），画面用 kw(id, '词') 取「说到这个词」的时刻。
import json, sys, re
N = sys.argv[1]; SRC = '/home/user/kepu-studio/episodes/guanghulian/02-serdes/douyin-split'
S = json.load(open(f'{SRC}/script_{N}.json')); A = json.load(open(f'{SRC}/align_{N}.json'))
TK = lambda text, line, a=None, b=None: dict(text=text, line=line, **{'from': a}, to=b)
SHOTS = {
 's1': [('tunnel', 'w01'), ('race', 'w05'), ('serial', 'w09'),
        ('take', 'w10', [TK('一句话带走', 'w10'), TK('速度一高，「一起到」', 'w11', '速度', '一起到'), TK('比「路多」更难。', 'w11', '比', '更难')])],
 's2': [('ribbon', 'v01'), ('beat', 'v05'), ('scramble', 'v09'),
        ('take', 'v11', [TK('一句话带走', 'v11'), TK('芯片不是在看 0 和 1，', 'v12', '芯片', '0 和 1'), TK('是在听节拍。', 'v12', '是在', '节拍')])],
 's3': [('x2', 'u01'), ('road', 'u05'), ('power', 'u07'), ('ppt', 'u09'),
        ('take', 'u11', [TK('一句话带走', 'u11'), TK('什么路？多少电？', 'u12', '什么路', '多少电'), TK('测过没有？', 'u12', '测过', '没有')])],
}[N]
HOLD = {'w07': 1.1, 'v07': 0.9, 'u09': 0.8}   # 高潮后的停顿（慢动作 / 咔一下 / 碎掉），秒
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
    lines.append(dict(id=s['id'], t0=round(t0, 3), t1=round(t1, 3), clip=round(t0 - a['on'], 3), text=''.join(cl), ch=ch, sub=s['sub'], big=s['big'], seg=s['seg'], src=s.get('src', '')))
    t = t1 + HOLD.get(s['id'], 0); prev = s
dur = round(t + TAIL, 2)
L = {x['id']: x for x in lines}; shots = []
for k, (kind, first, *rest) in enumerate(SHOTS):
    a = 0 if k == 0 else round(L[first]['t0'] - 0.3, 3)
    sh = dict(kind=kind, t0=a, paper=kind in ('desk', 'take'), first=first)
    if rest: sh['type'] = rest[0]
    if kind == 'take': sh['cy'] = 700
    shots.append(sh)
for k in range(len(shots)): shots[k]['t1'] = shots[k + 1]['t0'] if k + 1 < len(shots) else dur
json.dump(dict(name=N, dur=dur, lines=lines, shots=shots, hudIn=round(next(l['t0'] for l in lines if l['seg'] != 'open') - 0.3, 3)), open(f'/home/user/vox-ep02s/代码工程/split/{N}.json', 'w'), ensure_ascii=False)
print(N, 'dur', dur, [(s['kind'], s['t0']) for s in shots])
