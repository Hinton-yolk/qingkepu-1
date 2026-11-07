# ======================= 旁白时间表（小红书改版 · 下集：最先进的 AI 机柜，为什么塞满铜线？） =======================
def cardview(cid, z=1.12):
    h = CARDS[cid]['h']; z = min(z, 1205 / h); dy = max(0, h / 2 - 470 / z)
    if 960 - (h / 2 + dy) * z < 215: dy = (960 - 215) / z - h / 2
    return PC(cid, 0, round(dy)), round(z, 3)
def gocab(cid, d=1.0): go(PC(cid, 0, 40), 1.1, d)
LENS = dict(at=[0, 0], zin=[1e6, 1e6 + 1], open=[1e6, 1e6 + 1], sharp=1e6, shave=[1e6, 1e6 + 1], lbl=1e6, lbl2=1e6, out=[1e6, 1e6 + 1], zmax=40)   # 下集没有放大镜头
# --- 钩子：第一帧是 AI 机柜背面 + 贴在铜缆上的大字问题 ---
cam(0, PC('RK', 0, -20), 1.08, 'lin')
clabel('RK', '最先进的 AI 机柜，为什么塞满铜线？', 0, -570, 0, size=46, bg='red', r=-0.012, rate=400)
adv(0.125); speak('D1'); after('D1', 0.25)
speak('D2'); mag = g8(LINE['D2']); k_ = g8(span('D2', '几千根铜缆')[0]); clabel('RK', '几千根铜缆', 300, 380, k_, size=46, r=-0.02); after('D2', 0.125)
clabel('RK', '柜里距离短：信号还清楚', 120, 100, mag + 0.5, size=40); sfx(mag, 'thock')        # 用户 2026-11-07：第一个演示太晚，2 秒放大镜钻进一根铜缆
speak('D3'); fb_ = g8(span('D3', '换成光')[0]); clabel('RK', '不是要换成光吗？', 300, -520, fb_, size=40, bg='#3fb5a5'); sfx(fb_, 'laser')
after('D3', 0.125); CUE['RK'] = dict(t0=0, mag=mag, fiber=fb_, end=now()); hold(0, 0.05)
# --- 快递路线图：亮第二站「路上」 ---
string('RK-RT', cbot('RK', 300), ctop('RT', -250)); gocard('RT', 1.15, 0.75)
t0 = g8(now()); speak('D4'); lit = g8(max(t0 + 0.5, span('D4', '铜线这一段路')[0]))
clabel('RT', '第二站：路上', 0, 250, lit, size=44, bg='red'); sfx(lit, 'thock'); HUD_IN = lit
after('D4', 0.125); CUE['RT'] = dict(t0=t0, lit=lit, end=now()); hold(0, 0)
# --- 铜线的死穴（第一个机制演示） ---
string('RT-H0', cbot('RT', 250), ctop('H0', 250)); gocard('H0', 1.12, 0.5)
e0 = g8(now()); speak('D5'); lA = g8(e0 + 1.0); lB = g8(max(lA + 1.0, span('D5', '就越糊')[0]))
clabel('H0', '出发时：清楚', -330, 210, lA, align='left'); clabel('H0', '跑远了：糊了', 380, 210, lB, bg='red', align='right')
sfx(e0, 'thock'); sfx(lB, 'blur')
after('D5', 0.375); adv(max(0, g8(lB + 1.0 - now()))); CUE['H0'] = dict(t0=e0, e0=e0, end=now()); hold(0, 0)
# --- 怎么办：三类（纸条一句）→ 修短、修好（演示） ---
string('H0-fix', cbot('H0', 250), edge('X0', 'l')); gost('fix', 1.0, 'sine', 0.12)
speak('X30'); fwin('fix', ['X0'], 'X30'); vmark('X0', 'hl', '怎么办', 'X30', '怎么办'); vmark('X0', 'hl', '三种思路', 'X30', '大致三类')
after('X30', 0.25); hold(0, 0)
string('fix-K8', edge('X0', 'l'), ctop('K8', 250)); gocard('K8')
t0 = g8(now()); r0 = t0 + 0.25; speak('X31'); r1 = g8(max(r0 + 1.0, span('X31', '把路修短')[0])); after('X31'); speak('X32'); r2 = g8(max(r1 + 1.0, span('X32', '把路修好')[0]))
clabel('K8', '原来：路长，到了就糊', -390, -440, r0 + 0.25, align='left', bg='red', size=38); clabel('K8', '修短：芯片离得更近', -390, -110, r1 + 0.25, align='left', size=38)
clabel('K8', '修好：损耗更低的板材、铜缆', -390, 220, r2 + 0.25, align='left', size=38)
for tt in (r0, r1, r2): sfx(tt, 'thock')
after('X32', 0.375); CUE['K8'] = dict(t0=t0, rows=[r0, r1, r2], end=now()); hold(0, 0)
# --- 三，在路上修信号（纸条一句）→ 带芯片的雷电线 → 检修站也有极限 ---
string('K8-fix3', cbot('K8', 250), edge('X5', 'l')); gost('fix3', 1.0, 'sine', 0.12)
speak('D9'); fwin('fix3', ['X5', 'X6', 'X7'], 'D9'); vmark('X5', 'hl', '在路上修信号', 'D9', '在路上修信号'); vmark('X6', 'hl', '中途设检修站', 'D9', '设一个检修站'); vmark('X7', 'hl', '重新认出来、整理干净', 'D9', '重新认出来、整理干净')
after('D9', 0.25); hold(0, 0)
string('fix3-C2', edge('X7', 'l'), ctop('C2', 300)); gocab('C2')
t0 = g8(now()); speak('D10'); cr = g8(max(t0 + 0.5, span('D10', '检修站')[0])); full = g8(max(cr + 0.75, span('D10', '2 米')[0]))
clabel('C2', '线里的芯片：一个小检修站', 0, -510, cr + 0.25, size=44, bg='red'); clabel('C2', '2 米的线，也能跑满 40G', 0, 430, full, size=46)
sfx(t0 + 0.25, 'dsp'); sfx(full, 'thock')
after('D10', 0.25); CUE['C2'] = dict(t0=t0, chip=t0 + 0.25, chipRing=cr, inset=cr, noshort=1, end=now()); hold(0, 0)
string('C2-K9', cbot('C2', -300), ctop('K9', 250)); gocard('K9')
t0 = g8(now()); ok = t0 + 0.25; speak('X36'); bad = g8(max(ok + 2.0, span('X36', '信号糊到一定程度')[0]))
clabel('K9', '中途设检修站：认出来、整理干净', -390, -420, ok + 1.0, align='left', size=38); clabel('K9', '糊到一定程度：修不回来', -390, 400, bad + 1.25, align='left', bg='red', size=38)
sfx(ok + 1.0, 'dsp'); sfx(bad + 1.25, 'wrong')
after('X36', 0.375); adv(max(0, g8(bad + 2.5 - now()))); CUE['K9'] = dict(t0=t0, ok=ok, bad=bad, end=now()); hold(0, 0)
# --- 所以铜线没被淘汰（纸条一句）→ 回到开头的机柜 → 光接手的那一段 ---
string('K9-copper', cbot('K9', -250), edge('Y1', 'r')); gost('copper', 1.0, 'sine', 0.12)
speak('D12'); fwin('copper', ['Y1', 'Y2', 'Y3s', 'Y4s'], 'D12')
vmark('Y1', 'hl', '并没有被淘汰', 'D12', '没被淘汰'); vmark('Y2', 'hl', '便宜、可靠', 'D12', '便宜、可靠'); vmark('Y2', 'hl', '不需要电光转换', 'D12', '不用电光转换'); vmark('Y3s', 'hl', '机柜内', 'D12', '机柜里'); vmark('Y4s', 'hl', '依然大量使用', 'D12', '依然大量使用')
after('D12', 0.25); hold(0, 0)
string('copper-RK2', edge('Y4s'), ctop('RK2', -300)); go(PC('RK2', 0, -20), 1.08, 1.0)
t0 = g8(now()); speak('D13'); rg = g8(max(t0 + 0.25, span('D13', '几千根铜缆')[0]))
clabel('RK2', '柜内：几千根铜缆', 260, 380, rg + 0.25, size=50, bg='red', r=-0.02); sfx(rg, 'thock')
after('D13', 0.25); CUE['RK2'] = dict(t0=t0, ring=rg, end=now()); hold(0, 0)
REV = CUE['RK2']['t0']                  # 揭晓：回到开头那个机柜（配乐在这里停半拍、换织体）
string('RK2-K10', cbot('RK2', -300), ctop('K10', 250)); gocard('K10')
t0 = g8(now()); cp = t0 + 0.25; speak('X40'); light = g8(max(cp + 1.0, span('X40', '光要接手')[0])); lim = g8(max(cp + 0.5, light - 0.75))
clabel('K10', '柜内短距离：铜线', -390, -260, cp + 0.25, align='left', size=38); clabel('K10', '光：接手铜线力不从心的那一段', 390, 230, light + 0.25, align='right', size=36)
sfx(cp, 'thock'); sfx(lim, 'blur'); sfx(light, 'laser')
after('X40', 0.375); adv(max(0, g8(light + 1.5 - now()))); CUE['K10'] = dict(t0=t0, copper=cp, limit=lim, light=light, end=now()); hold(0, 0)
# --- 收尾：一句话带走 → 你在这里 → 下一篇 ---
ally = [c['at'][1] for c in CLIPS.values()] + [c['at'][1] for c in CARDS.values()]
OVER = dict(x=850, y=round((min(ally) + max(ally)) / 2), z=round(1920 / (max(ally) - min(ally) + 1400), 4))
gost('end', 1.5, 'cubic', 0.10)
speak('D19'); fwin('end', ['E0', 'E3', 'E4'], 'D19')
vmark('E0', 'hl', '一句话带走', 'D19', '一句话带走'); vmark('E3', 'hl', '把路修短、把路修好', 'D19', '把路修短、把路修好'); vmark('E4', 'hl', '在路上修信号', 'D19', '在路上修信号')
after('D19', 0.25); hold(0, 0)
he = CARDS['HE']; go([he['at'][0], he['at'][1] - 40], 1.15, 1.0); hq = g8(now() - 0.5); CUE['HE'] = dict(t0=hq, end=hq + 1)
speak('X48'); after('X48', 0.125)
def rightof(cid, gap=50): c = CLIPS[cid]; return [round(c['at'][0] + (c['crop'][2] - c['crop'][0]) * c['k'] / 2 + gap, 1), c['at'][1]]
label('下一篇：路上的检修站', [he['at'][0], round(he['at'][1] + he['h'] / 2 + 60, 1)], LINE['X48'], size=34, r=-0.01)
label('白话光互连 · 03 下', rightof('E0'), LINE['D19'] + 0.5, size=24, align='left', bg='red', r=-0.02)
hold(2.25, 0.02)
