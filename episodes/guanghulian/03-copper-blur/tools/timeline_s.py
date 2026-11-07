# ======================= 旁白时间表（抖音第 2 条：最贵的 AI 机柜，为什么塞满铜线？ ≤ 55 秒） =======================
# 2.5 秒放大镜钻进一根铜缆（柜里距离短，信号还清楚）；三种自救；带芯片的雷电线；回到机柜；一句话。
def cardview(cid, z=1.12):
    h = CARDS[cid]['h']; z = min(z, 1010 / h); return PC(cid, 0, round(145 / z)), round(z, 3)
def gocab(cid, d=1.0): go(PC(cid, 0, 40), 1.1, d)
LENS = dict(at=[0, 0], zin=[1e6, 1e6 + 1], open=[1e6, 1e6 + 1], sharp=1e6, shave=[1e6, 1e6 + 1], lbl=1e6, lbl2=1e6, out=[1e6, 1e6 + 1], zmax=40)
RKZ = 0.88; rkcam = lambda cid: PC(cid, 0, round(-30 + 145 / RKZ))
# --- 第一帧：AI 机柜背面 + 大字；2.5 秒放大镜钻进一根铜缆 ---
cam(0, rkcam('RK'), RKZ, 'lin')
clabel('RK', '最先进的 AI 机柜，为什么塞满铜线？', 0, -570, 0, size=46, bg='red', r=-0.012, rate=400)
adv(0.125); speak('D1'); after('D1', 0.125)
speak('D2'); mag = g8(LINE['D2']); k_ = g8(span('D2', '几千根铜缆')[0])
clabel('RK', '柜里距离短：信号还清楚', 120, 100, mag + 0.5, size=40); clabel('RK', '几千根铜缆', 300, 380, k_, size=46, r=-0.02); sfx(mag, 'zoomstep')
after('D2', 0.125)
speak('D3'); fb_ = g8(span('D3', '换成光')[0]); clabel('RK', '不是要换成光吗？', 300, -500, fb_, size=40, bg='#3fb5a5'); sfx(fb_, 'laser')
after('D3', 0.125); CUE['RK'] = dict(t0=0, mag=mag, fiber=fb_, end=now()); hold(0, 0.04)
# --- 快递路线图：亮「路上」 ---
string('RK-RT', cbot('RK', 300), ctop('RT', -250)); gocard('RT', 1.15, 0.75)
t0 = g8(now()); speak('D4'); lit = g8(max(t0 + 0.5, span('D4', '铜线这一段路')[0]))
clabel('RT', '第二站：路上', 0, 250, lit, size=44, bg='red'); sfx(lit, 'thock'); HUD_IN = lit
after('D4', 0.125); CUE['RT'] = dict(t0=t0, lit=lit, end=now()); hold(0, 0)
# --- 演示：修短、修好 ---
string('RT-K8', cbot('RT', -250), ctop('K8', 250)); gocard('K8', 1.12, 0.75)
t0 = g8(now()); r0 = t0 + 0.125; speak('S5'); r1 = g8(max(r0 + 0.75, span('S5', '把路修短')[0])); after('S5', 0.125); speak('S6'); r2 = g8(max(r1 + 0.75, span('S6', '把路修好')[0]))
clabel('K8', '原来：路长，到了就糊', -390, -440, r0 + 0.25, align='left', bg='red', size=38); clabel('K8', '修短：芯片离得更近', -390, -110, r1 + 0.25, align='left', size=38)
clabel('K8', '修好：损耗更低的板材、铜缆', -390, 220, r2 + 0.25, align='left', size=38)
for tt in (r0, r1, r2): sfx(tt, 'thock')
after('S6', 0.25); CUE['K8'] = dict(t0=t0, rows=[r0, r1, r2], end=now()); hold(0, 0)
# --- 纸条一拍：在路上修信号 ---
string('K8-fix3', cbot('K8', 250), edge('X5', 'l')); gost('fix3', 0.75, 'sine', 0.12)
speak('S7'); fwin('fix3', ['X5', 'X6', 'X7'], 'S7'); vmark('X5', 'hl', '在路上修信号', 'S7', '在路上修信号'); vmark('X6', 'hl', '中途设检修站', 'S7', '设个检修站'); vmark('X7', 'hl', '认出来、整理干净', 'S7', '认出来、整理干净')
after('S7', 0.125); hold(0, 0)
# --- 演示：带芯片的雷电线，插头里就是检修站 ---
string('fix3-C2', edge('X7', 'l'), ctop('C2', 300)); gocab('C2', 0.75)
t0 = g8(now()); speak('D10'); cr = g8(max(t0 + 0.5, span('D10', '检修站')[0])); full = g8(max(cr + 0.75, span('D10', '2 米')[0]))
clabel('C2', '线里的芯片：一个小检修站', 0, -510, cr + 0.25, size=44, bg='red'); clabel('C2', '2 米的线，也能跑满 40G', 0, 350, full, size=46)
sfx(t0 + 0.25, 'dsp'); sfx(full, 'thock')
after('D10', 0.125); CUE['C2'] = dict(t0=t0, chip=t0 + 0.25, chipRing=cr, inset=cr, noshort=1, end=now()); hold(0, 0)
# --- 纸条一拍：所以铜线没被淘汰 ---
string('C2-copper', cbot('C2', 300), edge('Y1', 'l')); gost('copper', 0.75, 'sine', 0.12)
speak('S9'); fwin('copper', ['Y1', 'Y2', 'Y3s', 'Y4s'], 'S9')
vmark('Y1', 'hl', '并没有被淘汰', 'S9', '没被淘汰'); vmark('Y2', 'hl', '便宜、可靠', 'S9', '便宜、可靠'); vmark('Y3s', 'hl', '机柜内', 'S9', '机柜里'); vmark('Y4s', 'hl', '依然大量使用', 'S9', '照样用它')
after('S9', 0.125); hold(0, 0)
# --- 回到开头那个机柜（揭晓） → 光接手的那一段 ---
string('copper-RK2', edge('Y4s', 'l'), ctop('RK2', 300)); go(rkcam('RK2'), RKZ, 0.75)
t0 = g8(now()); speak('D13'); rg = g8(max(t0 + 0.25, span('D13', '几千根铜缆')[0]))
clabel('RK2', '柜内：几千根铜缆', 260, 380, rg + 0.25, size=50, bg='red', r=-0.02); sfx(rg, 'thock')
after('D13', 0.125); CUE['RK2'] = dict(t0=t0, ring=rg, end=now()); hold(0, 0)
REV = CUE['RK2']['t0']
string('RK2-K10', cbot('RK2', -300), ctop('K10', 250)); gocard('K10', 1.12, 0.75)
t0 = g8(now()); cp = t0 + 0.125; speak('X40'); light = g8(max(cp + 0.75, span('X40', '光要接手')[0])); lim = g8(max(cp + 0.5, light - 0.5))
clabel('K10', '柜内短距离：铜线', -390, -260, cp + 0.25, align='left', size=38); clabel('K10', '光：接手铜线力不从心的那一段', 390, 230, light + 0.25, align='right', size=36)
sfx(cp, 'thock'); sfx(lim, 'blur'); sfx(light, 'laser')
after('X40', 0.25); adv(max(0, g8(light + 1.0 - now()))); CUE['K10'] = dict(t0=t0, copper=cp, limit=lim, light=light, end=now()); hold(0, 0)
# --- 一句话 + 你在这里 ---
ally = [c['at'][1] for c in CLIPS.values()] + [c['at'][1] for c in CARDS.values()]
OVER = dict(x=850, y=round((min(ally) + max(ally)) / 2), z=round(1920 / (max(ally) - min(ally) + 1400), 4))
gost('end', 1.0, 'cubic', 0.10)
speak('S12'); fwin('end', ['E0', 'E3', 'E4'], 'S12')
vmark('E0', 'hl', '一句话带走', 'S12', '一句话'); vmark('E3', 'hl', '把路修短、把路修好', 'S12', '修短、修好'); vmark('E4', 'hl', '在路上修信号', 'S12', '路上修')
after('S12', 0.125); hold(0, 0)
he = CARDS['HE']; go([he['at'][0], he['at'][1] - 40], 1.15, 0.75); hq = g8(now() - 0.5); CUE['HE'] = dict(t0=hq, end=hq + 1)
def rightof(cid, gap=50): c = CLIPS[cid]; return [round(c['at'][0] + (c['crop'][2] - c['crop'][0]) * c['k'] / 2 + gap, 1), c['at'][1]]
label('白话光互连 · 03', rightof('E0'), LINE['S12'] + 0.5, size=24, align='left', bg='red', r=-0.02)
hold(1.75, 0.02)
