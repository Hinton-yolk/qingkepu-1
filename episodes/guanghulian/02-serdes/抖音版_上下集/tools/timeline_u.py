# ======================= 旁白时间表（02 抖音 · 上集：线越多，反而越慢？） =======================
LENS = dict(at=[0, 0], zin=[1e6, 1e6 + 1], open=[1e6, 1e6 + 1], core=1e6, samp=[1e6, 1e6 + 1], lbl=1e6, out=[1e6, 1e6 + 1], zmax=40)   # 没有放大镜头
# --- 第一帧：并口线 vs USB，两根进度条 0 秒就开跑（抖音：第一个演示 ≤ 3 秒） ---
cam(0, PC('P0', -5, 110), 1.06, 'lin')
clabel('P0', '线越多，反而越慢？', 0, -480, 0, size=58, bg='red', r=-0.012, rate=400)
adv(0.125); speak('x1'); after('x1', 0.25)
speak('x2'); a2 = g8(span('x2', '两兆字节')[0]); b2 = g8(span('x2', '几十兆')[0])
clabel('P0', '每秒约 2 兆字节', 470, -365, a2, align='right', size=36); clabel('P0', '每秒几十兆字节', 470, 65, b2, align='right', size=36, bg='red'); sfx(a2, 'thock'); sfx(b2, 'thock')
after('x2', 0.125); CUE['P0'] = dict(t0=0, end=now()); hold(0, 0.03)
# --- 快递路线图：亮第一站「打包出发」；为什么不多修几条路？ ---
string('P0-RT', cbot('P0', 300), ctop('RT', -250)); gocard('RT', 1.15, 0.75)
t0 = g8(now()); speak('x3'); lit = g8(max(t0 + 0.5, span('x3', '最快的路')[0] - 0.25))
clabel('RT', '第一站：打包出发', 0, 250, lit, size=44, bg='red'); sfx(lit, 'thock'); HUD_IN = lit
after('x3', 0.125); speak('x4'); q4 = g8(LINE['x4']); clabel('RT', '为什么不多修几条路？', 0, -330, q4 + 0.25, size=40); after('x4', 0.125)
CUE['RT'] = dict(t0=t0, lit=lit, end=now()); hold(0, 0)
# --- 纸条一拍：直觉上并排走更快 ---
string('RT-w', cbot('RT', -250), edge('W1', 'r')); gost('w', 1.0, 'sine', 0.12)
speak('x5'); fwin('w', ['W1', 'W2'], 'x5'); vmark('W1', 'hl', '并排走似乎更快', 'x5', '直觉上'); vmark('W2', 'hl', '修几十条路，几十件货同时出发', 'x5', '几十件货同时出发')
after('x5', 0.125); hold(0, 0)
# --- 演示：慢的时候对齐 ✓；一快，长一点的那条晚到一步 ✗ ---
string('w-K4', edge('W2'), ctop('K4', -250)); gocard('K4')
t0 = g8(now()); s0 = t0 + 0.25; speak('x6'); f0 = g8(max(s0 + 2.25, span('x6', '速度一快')[0]))
clabel('K4', '慢：每一批都按时到齐', -390, -420, s0 + 1.5, align='left', size=38); clabel('K4', '一快：长一点的那条，晚到一步', -390, 330, f0 + 1.75, align='left', bg='red', size=38)
sfx(s0 + 1.25, 'thock'); sfx(f0 + 1.5, 'wrong')
after('x6', 0.25); adv(max(0, g8(f0 + 2.5 - now()))); CUE['K4'] = dict(t0=t0, slow=[s0], fast=[f0], end=now()); hold(0, 0)
# --- 纸条一拍：运动员同时冲线 ---
string('K4-q', cbot('K4', -250), edge('Q2', 'r')); gost('q', 1.0, 'sine', 0.12)
speak('x7'); fwin('q', ['Q2', 'Q3', 'Q4', 'Q5'], 'x7'); vmark('Q2', 'hl', '同时冲线', 'x7', '同时冲线'); vmark('Q4', 'hl', '晚到一步', 'x7', '越难齐'); vmark('Q5', 'hl', '整排数据就拼错了', 'x7', '越难齐', 0.5)
after('x7', 0.125); hold(0, 0)
# --- 演示：出口不够，每多一条线就多占面积、多耗电 ---
string('q-K3', edge('Q5'), ctop('K3', -250)); gocard('K3')
t0 = g8(now()); speak('x8'); mo = g8(max(t0 + 1.75, span('x8', '每多一条线')[0]))
lines = [t0 + 0.25 + 0.25 * k for k in range(6)] + [mo + 0.375 * k for k in range(4)]
clabel('K3', '引脚就这么多', -230, -330, t0 + 0.5, size=38); clabel('K3', '每多一条线：多占面积、多耗电', 0, 400, mo + 1.0, size=36, bg='red')
for tt in lines: sfx(tt, 'click')
after('x8', 0.25); adv(max(0, g8(mo + 2.0 - now()))); CUE['K3'] = dict(t0=t0, lines=lines, end=now()); hold(0, 0)
# --- 纸条一拍：只修少数几条路，排成一列 ---
string('K3-l', cbot('K3', -250), edge('L1', 'r')); gost('l', 1.0, 'sine', 0.12)
speak('x9'); fwin('l', ['L1', 'L2', 'L3'], 'x9'); vmark('L1', 'hl', '只修少数几条路', 'x9', '只修少数几条路'); vmark('L2', 'hl', '排成一列', 'x9', '排成一列'); vmark('L3', 'hl', '跑到极快', 'x9', '跑到极快')
after('x9', 0.125); hold(0, 0)
# --- 演示：很多条慢路 vs 少数几条快路 ---
string('l-K5', edge('L3'), ctop('K5', -250)); gocard('K5')
t0 = g8(now()); many = t0 + 0.25; speak('x10'); few = g8(max(many + 1.25, span('x10', '一条路')[0] - 0.25)); big = g8(span('x10', '上千亿')[0])
clabel('K5', '很多条慢路', -390, -330, many + 0.25, align='left', size=36); clabel('K5', '少数几条快路：每秒上千亿个比特', -390, 340, big, align='left', size=36, bg='red')
sfx(few, 'whoosh', dur=0.5, g=0.06)
after('x10', 0.25); CUE['K5'] = dict(t0=t0, many=many, few=few, end=now()); hold(0, 0)
# --- 纸条一拍：SerDes 的名字 ---
string('K5-n', cbot('K5', -250), edge('N1', 'r')); gost('n', 1.0, 'sine', 0.12)
speak('x11'); fwin('n', ['N1', 'N2', 'N3', 'N4'], 'x11'); vmark('N1', 'hl', 'Serializer（串行化）', 'x11', 'Ser 是'); vmark('N2', 'hl', '排成一列', 'x11', '排成一列')
vmark('N3', 'hl', 'Deserializer', 'x11', 'Des 是'); vmark('N4', 'hl', '拆回一排', 'x11', '拆回一排')
after('x11', 0.125); hold(0, 0)
# --- 演示：发货口排成一列 → 收货口拆回一排 ---
string('n-K1', edge('N4'), ctop('K1', -250)); gocard('K1')
t0 = g8(now()); ser = t0 + 0.25; speak('x12'); des = g8(max(ser + 2.0, span('x12', '收货口')[0]))
clabel('K1', '发货口：排成一列', 390, -560, ser + 0.5, align='right', size=38); clabel('K1', '收货口：拆回一排', 390, 560, des + 1.5, align='right', size=38, bg='red')
sfx(ser, 'thock'); sfx(des, 'thock')
after('x12', 0.25); adv(max(0, g8(des + 3.25 - now()))); CUE['K1'] = dict(t0=t0, ser=ser, des=des, end=now()); hold(0, 0)
# --- 回到开头那根 USB 线（揭晓：配乐停半拍、换织体） ---
string('K1-P1', cbot('K1', 250), ctop('P1', 300)); go(PC('P1', -5, 110), 1.06, 1.0)
t0 = g8(now()); REV = t0; speak('x13'); rc = g8(t0 + 0.5)
clabel('P1', '线少反而快：数据排成一列', 0, -480, rc + 0.5, size=44, bg='red', r=-0.012); sfx(rc, 'shave', dur=0.75)
after('x13', 0.25); CUE['P1'] = dict(t0=t0 - 4, recall=rc, end=now()); hold(0, 0)
# --- 一句话 + 你在这里 → 下集 ---
ally = [c['at'][1] for c in CLIPS.values()] + [c['at'][1] for c in CARDS.values()]
OVER = dict(x=850, y=round((min(ally) + max(ally)) / 2), z=round(1920 / (max(ally) - min(ally) + 1400), 4))
gost('end', 1.5, 'cubic', 0.10)
speak('x14'); fwin('end', ['E0', 'E1', 'E2'], 'x14')
vmark('E0', 'hl', '一句话带走', 'x14', '一句话带走'); vmark('E1', 'hl', '并排走就难以对齐', 'x14', '并排走就难对齐'); vmark('E2', 'hl', '排成一列出发', 'x14', '排成一列出发')
after('x14', 0.25); hold(0, 0)
he = CARDS['HE']; go([he['at'][0], he['at'][1] - 40], 1.15, 1.0); hq = g8(now() - 0.5); CUE['HE'] = dict(t0=hq, end=hq + 1)
speak('x15'); after('x15', 0.125)
def rightof(cid, gap=50): c = CLIPS[cid]; return [round(c['at'][0] + (c['crop'][2] - c['crop'][0]) * c['k'] / 2 + gap, 1), c['at'][1]]
label('下集：对面怎么数清 0 和 1？', [he['at'][0], round(he['at'][1] + he['h'] / 2 + 60, 1)], LINE['x15'], size=34, r=-0.01)
label('白话光互连 · 02 上', rightof('E0'), LINE['x14'] + 0.5, size=24, align='left', bg='red', r=-0.02)
hold(2.25, 0.02)
