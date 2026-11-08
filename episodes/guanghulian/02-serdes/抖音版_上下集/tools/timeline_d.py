# ======================= 旁白时间表（02 抖音 · 下集：少数一个比特，整句话就乱了） =======================
LENS = dict(at=[0, 0], zin=[1e6, 1e6 + 1], open=[1e6, 1e6 + 1], core=1e6, samp=[1e6, 1e6 + 1], lbl=1e6, out=[1e6, 1e6 + 1], zmax=40)   # 没有放大镜头
# --- 第一帧：聊天消息，线上少了一位，0.5 秒起整句变乱码（抖音：第一个演示 ≤ 3 秒） ---
cam(0, PC('P0', 0, 104), 1.25, 'lin')
clabel('P0', '芯片是怎么数清 0 和 1 的？', 0, -470, 0, size=46, bg='red', r=-0.012, rate=400)
adv(0.125); speak('y1'); clabel('P0', '少数一个', 0, 290, 1.0, size=34, bg='red'); sfx(0.5, 'wrong'); after('y1', 0.25)
CUE['P0'] = dict(t0=0, drop=0.5, end=now()); hold(0, 0.03)
# --- 快递路线图：第一站「打包出发」，对面要一个一个数清 ---
string('P0-RT', cbot('P0', 200), ctop('RT', -250)); gocard('RT', 1.15, 0.75)
t0 = g8(now()); speak('y2'); lit = g8(max(t0 + 0.5, span('y2', '到了对面')[0] - 0.25))
clabel('RT', '第一站：打包出发', 0, 250, lit, size=44, bg='red'); sfx(lit, 'thock'); HUD_IN = lit
after('y2', 0.125); CUE['RT'] = dict(t0=t0, lit=lit, end=now()); hold(0, 0)
# --- 演示：连续五个 1 是一段平的高电平：四个，还是五个？ ---
string('RT-K6', cbot('RT', 250), ctop('K6', 250)); gocard('K6')
k6 = g8(now()); wave = k6 + 0.25; speak('y3'); ask = g8(max(wave + 1.0, span('y3', '四个')[0] - 0.25))
ED_ = None
clabel('K6', '四个？还是五个？', 0, 190, ask + 0.25, size=40, bg='red'); sfx(ask, 'wrong'); ASK_L = CARD_LABELS['K6'][-1]
after('y3', 0.25); hold(0, 0.04)
# --- 纸条一拍：节拍 ---
string('K6-o', cbot('K6', 250), edge('O8', 'l')); gost('o', 1.0, 'sine', 0.12)
speak('y4'); fwin('o', ['O8', 'O9'], 'y4'); vmark('O8', 'hl', '数清这里有几个1', 'y4', '要数清'); vmark('O9', 'hl', '这就是“节拍”', 'y4', '这就是节拍')
after('y4', 0.125); hold(0, 0.04)
# --- 演示：跟着一首歌拍手，没人打拍子也跟得上 ---
string('o-CL', edge('O9', 'l'), ctop('CL', 250)); gocard('CL', 1.12, 0.75)
t0 = g8(now()); speak('y5'); clabel('CL', '没人打拍子：听着鼓点就跟上了', 0, 330, g8(span('y5', '听着鼓点')[0]), size=36)
for k_ in range(int((ALIGN['y5']['dur'] + 0.5) / 0.5)): sfx(t0 + k_ * 0.5, 'click')
after('y5', 0.25); CUE['CL'] = dict(t0=t0, end=now()); hold(0, 0)
# --- 回到节拍卡：每次跳变是一个鼓点 → 推算节拍 → 一拍一拍清点：五个 ---
gocard('K6', 1.12, 0.75); speak('y6'); ed = g8(max(now(), span('y6', '每跳一下')[0] - 0.25)); gr = g8(max(ed + 0.75, span('y6', '校准')[0] - 0.25)); ct = g8(max(gr + 1.25, span('y6', '一个一个清点')[0] - 0.25))
clabel('K6', '每次跳变 = 一个鼓点', -390, -370, ed + 0.25, align='left', size=36); clabel('K6', '按节拍清点：5 个', 0, 270, ct + 1.0, size=40, bg='red'); ASK_L['dim'] = ed
sfx(ed, 'thock'); [sfx(ct + k_ * 0.125, 'click') for k_ in range(6)]
after('y6', 0.25); adv(max(0, g8(ct + 2.0 - now()))); CUE['K6'] = dict(t0=k6, wave=wave, ask=ask, edges=ed, grid=[gr, gr + 1.0], count=[ct, ct + 1.5], end=now()); hold(0, 0.04)
# --- 演示：一长串 1，拍子跑偏 → 先打乱，鼓点一直在 → 收到再还原 ---
string('K6-SC', cbot('K6', 250), ctop('SC', -250)); gocard('SC')
t0 = g8(now()); fl = t0 + 0.25; speak('y7'); after('y7', 0.125)
speak('y8'); mx = g8(max(fl + 3.0, span('y8', '打乱')[0] - 0.25)); bk = g8(max(mx + 1.5, span('y8', '还原')[0] - 0.5))
sfx(fl + 1.5, 'blur'); sfx(mx, 'dsp'); sfx(bk, 'thock')
after('y8', 0.25); adv(max(0, g8(bk + 1.25 - now()))); CUE['SC'] = dict(t0=t0, flat=fl, mix=mx, back=bk, end=now()); hold(0, 0.04)
# --- 纸条一拍：速度每过几年翻一倍 ---
string('SC-h', cbot('SC', -250), edge('H2', 'r')); gost('h', 1.0, 'sine', 0.12)
speak('y9'); fwin('h', ['H2'], 'y9'); vmark('H2', 'hl', '每过几年就要翻一倍', 'y9', '每过几年就要翻一倍')
after('y9', 0.125); hold(0, 0.04)
# --- 演示：越快越糊 → 自带修信号的电路 → 耗电、占面积 ---
string('h-K7', edge('H2'), ctop('K7', -250)); gocard('K7')
t0 = g8(now()); rows = [t0 + 0.25, t0 + 1.25, t0 + 2.25]; speak('y10'); eq = g8(max(rows[2] + 0.75, span('y10', '修信号的电路')[0] - 0.25)); co = g8(max(eq + 0.75, span('y10', '耗电')[0] - 0.25))
clabel('K7', '越快，信号越糊', 390, -440, rows[2] + 0.5, align='right', size=36, bg='red')
for tt in rows: sfx(tt, 'thock')
sfx(eq, 'dsp'); sfx(co, 'reach')
after('y10', 0.25); adv(max(0, g8(co + 1.25 - now()))); CUE['K7'] = dict(t0=t0, rows=rows, eq=eq, cost=co, end=now()); hold(0, 0)
# --- 纸条一拍：每个比特少花一点电 ---
string('K7-h6', cbot('K7', -250), edge('H6', 'r')); gost('h6', 1.0, 'sine', 0.12)
speak('y11'); fwin('h6', ['H6'], 'y11'); vmark('H6', 'hl', '每送出一个比特少花一点电', 'y11', '每送一个比特')
after('y11', 0.125); hold(0, 0.04)
# --- 回到开头那句话（揭晓：配乐停半拍、换织体）：一格格还原 ---
string('h6-P1', edge('H6'), ctop('P1', 200)); go(PC('P1', 0, 20), 1.0, 1.0)
t0 = g8(now()); REV = t0; speak('y12'); fx = g8(max(t0 + 0.5, span('y12', '一个都不能数错')[0] - 0.25))
clabel('P1', '每秒上千亿个比特，一个都不能数错', 0, -455, t0 + 0.25, size=38, bg='#7fd6b4', r=-0.012); sfx(fx, 'shave', dur=0.75)
after('y12', 0.25); adv(max(0, g8(fx + 2.0 - now()))); CUE['P1'] = dict(t0=t0, drop=t0 - 4, fix=fx, end=now()); hold(0, 0)
# --- 一句话 + 你在这里 → 下一篇 ---
ally = [c['at'][1] for c in CLIPS.values()] + [c['at'][1] for c in CARDS.values()]
OVER = dict(x=850, y=round((min(ally) + max(ally)) / 2), z=round(1920 / (max(ally) - min(ally) + 1400), 4))
gost('end', 1.5, 'cubic', 0.10)
speak('y13'); fwin('end', ['E0', 'X4', 'X5'], 'y13')
vmark('E0', 'hl', '一句话带走', 'y13', '一句话带走'); vmark('X4', 'hl', '发出去时排成一列', 'y13', '发出去排成一列'); vmark('X5', 'hl', '收进来时听准节拍、拆回一排', 'y13', '收进来听准节拍')
after('y13', 0.25); hold(0, 0)
he = CARDS['HE']; go([he['at'][0], he['at'][1] - 40], 1.15, 1.0); hq = g8(now() - 0.5); CUE['HE'] = dict(t0=hq, end=hq + 1)
speak('y14'); after('y14', 0.125)
def rightof(cid, gap=50): c = CLIPS[cid]; return [round(c['at'][0] + (c['crop'][2] - c['crop'][0]) * c['k'] / 2 + gap, 1), c['at'][1]]
label('下一篇：第二站 路上，信号为什么越跑越模糊？', [he['at'][0], round(he['at'][1] + he['h'] / 2 + 60, 1)], LINE['y14'], size=32, r=-0.01)
label('白话光互连 · 02 下', rightof('E0'), LINE['y13'] + 0.5, size=24, align='left', bg='red', r=-0.02)
hold(2.25, 0.02)
