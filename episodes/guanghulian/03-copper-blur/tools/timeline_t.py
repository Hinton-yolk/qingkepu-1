# ======================= 旁白时间表（抖音第 1 条：线长一点，速度砍半？ ≤ 55 秒） =======================
# 机制演示长在第一帧：两根线的出口从第 0 秒就冒出信号（短线方正、长线糊了）。纸条一拍、演示一拍；结尾回到开头那根线。
def cardview(cid, z=1.12):
    h = CARDS[cid]['h']; z = min(z, 1010 / h); return PC(cid, 0, round(145 / z)), round(z, 3)
def gocab(cid, d=1.0): go(PC(cid, 0, 40), 1.1, d)
LENS = dict(at=[0, 0], zin=[1e6, 1e6 + 1], open=[1e6, 1e6 + 1], sharp=1e6, shave=[1e6, 1e6 + 1], lbl=1e6, lbl2=1e6, out=[1e6, 1e6 + 1], zmax=40)
# --- 第一帧：两根雷电线 + 大字；出口的信号已经在动 ---
cam(0, PC('C0', 30, 40), 1.0, 'lin')
clabel('C0', '长一点，速度砍半？', 0, -470, 0, size=60, bg='red', r=-0.012, rate=400)
adv(0.125); speak('X1'); after('X1', 0.25)
speak('X2'); a_ = g8(span('X2', '0.8 米')[0]); b_ = g8(max(a_ + 0.75, span('X2', '2 米')[0]))
clabel('C0', '0.8 米 · 40G', -150, -290, a_, size=44); clabel('C0', '2 米 · 20G', -150, 300, b_, size=44, bg='red')
after('X2', 0.125)
speak('T3'); r2 = g8(max(LINE['T3'] + 0.25, span('T3', '糊了')[0] - 0.5))
clabel('C0', '清楚', 330, -330, r2, size=40); clabel('C0', '糊了', 345, 235, r2 + 0.25, size=40, bg='red'); sfx(r2, 'blur')
after('T3', 0.125); CUE['C0'] = dict(t0=0, out=1, ring2=r2, end=now()); hold(0, 0.02)
# --- 快递路线图：亮「路上」 ---
string('C0-RT', cbot('C0', 300), ctop('RT', -250)); gocard('RT', 1.15, 0.75)
t0 = g8(now()); speak('X4'); lit = g8(max(t0 + 0.5, span('X4', '也卡在')[0] - 0.25))
clabel('RT', '第二站：路上', 0, 250, lit, size=44, bg='red'); sfx(lit, 'thock'); HUD_IN = lit
after('X4', 0.125); CUE['RT'] = dict(t0=t0, lit=lit, end=now()); hold(0, 0)
# --- 纸条一拍：每个比特都拖出一条尾巴 ---
string('RT-tail', cbot('RT', -250), edge('B6', 'r')); gost('tail', 0.75, 'sine', 0.12)
speak('T5'); fwin('tail', ['B6', 'B7'], 'T5'); vmark('B6', 'hl', '拖出一条尾巴', 'T5', '拖出一条尾巴')
after('T5', 0.125); hold(0, 0)
# --- 演示：一个比特拖尾 → 尾巴叠在一起（车库回音） ---
string('tail-K4', edge('B7'), ctop('K4', 250)); gocard('K4', 1.1, 0.75)
t0 = g8(now()); single = t0; m0 = t0 + 0.25; speak('X16')
seq = g8(max(m0 + 1.0, span('X16', '下一个字已经出口')[0])); sm = g8(max(seq + 0.75, span('X16', '糊成一片')[0])); ask = sm + 0.75
clabel('K4', '一个比特：拖出一条尾巴', -390, -440, m0 + 0.5, align='left'); clabel('K4', '尾巴压到后面的比特上', -390, 30, seq + 0.25, align='left', bg='red')
clabel('K4', '像车库回音：糊成一片', 390, 470, sm + 0.25, align='right', bg='red')
sfx(single, 'thock'); sfx(m0, 'shave', dur=0.75); sfx(seq, 'pairs'); sfx(sm, 'blur')
after('X16', 0.125); adv(max(0, g8(ask + 0.5 - now()))); CUE['K4'] = dict(t0=t0, single=single, morph=[m0, m0 + 0.75], seq=seq, sum=sm, ask=ask, end=now()); hold(0, 0)
# --- 演示：认错一个 → 照片花了、消息乱码 ---
string('K4-G1', cbot('K4', -250), ctop('G1', 250)); gocard('G1', 1.12, 0.75)
t0 = g8(now()); speak('X20'); ph = g8(max(t0 + 0.25, span('X20', '照片花了一块')[0])); ms = g8(max(ph + 0.75, span('X20', '乱码')[0] - 0.25))
clabel('G1', '照片花了一块', -210, 240, ph + 0.25, bg='red'); clabel('G1', '消息冒出乱码', 220, 0, ms + 0.25, bg='red'); sfx(ph, 'wrong'); sfx(ms, 'wrong')
after('X20', 0.25); adv(max(0, g8(ms + 0.75 - now()))); CUE['G1'] = dict(t0=t0, photo=ph, msg=ms, end=now()); hold(0, 0)
# --- 纸条一拍：越快，台阶越窄 ---
string('G1-far', cbot('G1', 250), edge('F3', 'l')); gost('far', 0.75, 'sine', 0.12)
speak('U16'); fwin('far', ['F3', 'F4', 'F5'], 'U16'); vmark('F3', 'hl', '越快', 'U16', '越快'); vmark('F4', 'hl', '时间减半', 'U16', '时间减半'); vmark('F5', 'hl', '变得更窄', 'U16', '变窄')
after('U16', 0.125); hold(0, 0)
# --- 演示：台阶变窄，同一条尾巴盖住两个比特 ---
string('far-K6', edge('F5'), ctop('K6', 250)); gocard('K6', 1.12, 0.75)
t0 = g8(now()); rowA = t0 + 0.125; hitA = rowA + 0.75; speak('X24'); rowB = g8(t0 + 1.0); hitB = g8(max(rowB + 1.0, span('X24', '压到更多后面的比特上')[0]))
clabel('K6', '原来', -390, -400, rowA, align='left'); clabel('K6', '快一倍：台阶更窄，尾巴还那么长', -390, 0, rowB + 0.25, align='left', size=38)
clabel('K6', '压到更多比特上', 390, 400, hitB + 0.25, align='right', bg='red', size=40)
sfx(rowA, 'thock'); sfx(rowB, 'thock'); sfx(hitB, 'wrong')
after('X24', 0.25); CUE['K6'] = dict(t0=t0, rowA=rowA, rowB=rowB, hitA=hitA, hitB=hitB, end=now()); hold(0, 0)
# --- 回到开头那根线（揭晓：配乐在这里停半拍） ---
string('K6-C1', cbot('K6', 250), ctop('C1', -300)); go(PC('C1', 30, 40), 1.0, 0.75)
t0 = g8(now()); speak('X28'); rg = g8(max(t0 + 0.25, span('X28', '长到 2 米')[0]))
clabel('C1', '0.8 米 · 40G', -150, -290, t0, size=44); clabel('C1', '2 米：只剩 20G', -150, 330, rg + 0.25, size=48, bg='red'); sfx(rg, 'thock')
after('X28', 0.125); CUE['C1'] = dict(t0=t0, out=1, ring=rg, end=now()); hold(0, 0)
REV = CUE['C1']['t0']
# --- 所以要换成光 ---
string('C1-K7', cbot('C1', -300), ctop('K7', 250)); gocard('K7', 1.15, 0.75)
t0 = g8(now()); slow, fast = t0, t0 + 0.75; speak('T11'); so = g8(max(fast + 0.75, span('T11', '换成光')[0]))
clabel('K7', '慢：能可靠地跑很远', -400, -235, slow, align='left', size=38); clabel('K7', '快：没多远就糊了', -400, 5, fast, align='left', bg='red', size=38)
clabel('K7', '所以：换成光', 400, 245, so, align='right', size=40); sfx(slow, 'reach'); sfx(fast, 'reach2')
after('T11', 0.25); adv(max(0, g8(so + 0.75 - now()))); CUE['K7'] = dict(t0=t0, slow=slow, fast=fast, end=now()); hold(0, 0)
# --- 一句话 + 你在这里 ---
ally = [c['at'][1] for c in CLIPS.values()] + [c['at'][1] for c in CARDS.values()]
OVER = dict(x=850, y=round((min(ally) + max(ally)) / 2), z=round(1920 / (max(ally) - min(ally) + 1400), 4))
gost('end', 1.0, 'cubic', 0.10)
speak('T12'); fwin('end', ['E0', 'E2'], 'T12'); vmark('E0', 'hl', '一句话带走', 'T12', '一句话'); vmark('E2', 'hl', '跑得越快', 'T12', '越快')
after('T12', 0.125); hold(0, 0)
he = CARDS['HE']; go([he['at'][0], he['at'][1] - 40], 1.15, 0.75); hq = g8(now() - 0.5); CUE['HE'] = dict(t0=hq, end=hq + 1)
def rightof(cid, gap=50): c = CLIPS[cid]; return [round(c['at'][0] + (c['crop'][2] - c['crop'][0]) * c['k'] / 2 + gap, 1), c['at'][1]]
label('白话光互连 · 03', rightof('E0'), LINE['T12'] + 0.5, size=24, align='left', bg='red', r=-0.02)
hold(1.0, 0.02)
