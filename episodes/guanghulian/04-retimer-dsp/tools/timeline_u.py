# ======================= 旁白时间表（04 小红书 · 上集：芯片里，也装着均衡器？） =======================
def cardview(cid, z=1.12):
    h = CARDS[cid]['h']; z = min(z, 1205 / h); dy = max(0, h / 2 - 470 / z)
    if 960 - (h / 2 + dy) * z < 215: dy = (960 - 215) / z - h / 2
    return PC(cid, 0, round(dy)), round(z, 3)
LENS = dict(at=[0, 0], zin=[1e6, 1e6 + 1], open=[1e6, 1e6 + 1], core=1e6, samp=[1e6, 1e6 + 1], lbl=1e6, out=[1e6, 1e6 + 1], zmax=40)   # 上集没有放大镜头
# --- 第一帧：手机均衡器；0.5 秒推子一推，旁边的信号从糊变清楚 ---
cam(0, PC('P0', 0, 20), 1.0, 'lin')
clabel('P0', '芯片里，也装着均衡器？', 0, -560, 0, size=56, bg='red', r=-0.012, rate=400)
push = 0.5; sfx(push, 'shave', dur=0.75)
adv(0.125); speak('u1'); after('u1', 0.25)
speak('u2'); hi_ = g8(span('u2', '高音')[0]); clabel('P0', '高音推上去', 270, -230, hi_, size=40); clabel('P0', '信号变清楚了', 270, 270, hi_ + 0.5, size=40, bg='#7fd6b4')
after('u2', 0.125); CUE['P0'] = dict(t0=0, push=push, end=now()); hold(0, 0.03)
# --- 快递路线图：亮「路上」 ---
string('P0-RT', cbot('P0', 300), ctop('RT', -250)); gocard('RT', 1.15, 0.75)
t0 = g8(now()); speak('u3'); lit = g8(max(t0 + 0.5, span('u3', '路上')[0]))
clabel('RT', '第二站：路上', 0, 250, lit, size=44, bg='red'); sfx(lit, 'thock'); HUD_IN = lit
after('u3', 0.125); CUE['RT'] = dict(t0=t0, lit=lit, end=now()); hold(0, 0)
# --- 糊掉的信号怎么修？（糊的进、清楚的出） ---
string('RT-H0', cbot('RT', 250), ctop('H0', 250)); gocard('H0', 1.12, 0.5)
t0 = g8(now()); speak('u4'); clabel('H0', '进站：糊的', -390, 210, t0 + 0.5, align='left', bg='red'); clabel('H0', '出站：又清楚了', 390, 210, t0 + 1.5, align='right')
sfx(t0 + 0.5, 'blur'); sfx(t0 + 1.5, 'dsp')
after('u4', 0.25); adv(max(0, g8(t0 + 2.5 - now()))); CUE['H0'] = dict(t0=t0, e0=t0, end=now()); hold(0, 0)
# --- 纸条一拍：铜线削弱快速跳变最厉害 ---
string('H0-eq', cbot('H0', 250), edge('A1', 'l')); gost('eq', 1.0, 'sine', 0.12)
speak('u5'); fwin('eq', ['A1', 'A2'], 'u5'); vmark('A1', 'hl', '快速跳变削弱得更厉害', 'u5', '削弱快速跳变最厉害'); vmark('A2', 'hl', '棱角被削掉', 'u5', '棱角被削掉'); vmark('A2', 'hl', '拖出了尾巴', 'u5', '拖出了尾巴')
after('u5', 0.125); hold(0, 0)
# --- 演示：均衡（不补 / 发送端加强 / 接收端补回） ---
string('eq-K2', edge('A2'), ctop('K2', 250)); gocard('K2')
t0 = g8(now()); r0 = t0 + 0.25; speak('u6'); r1 = g8(max(r0 + 1.0, span('u6', '加强一点')[0] - 0.5)); r2 = g8(max(r1 + 1.0, span('u6', '补回来')[0] - 0.5))
clabel('K2', '不补：棱角被削掉，拖出尾巴', -390, -520, r0 + 0.5, align='left', bg='red', size=36); clabel('K2', '发送端：先把跳变加强一点', -390, -130, r1 + 0.75, align='left', size=36)
clabel('K2', '接收端：再补回来，接近方正', -390, 270, r2 + 0.75, align='left', size=36)
for tt in (r0, r1, r2): sfx(tt, 'thock')
after('u6', 0.25); adv(max(0, g8(r2 + 1.5 - now()))); CUE['K2'] = dict(t0=t0, rows=[r0, r1, r2], end=now()); hold(0, 0)
# --- 演示：整体放大 ✗ vs 只补被吞的 ✓ ---
string('K2-WH', cbot('K2', -250), ctop('WH', 250)); gocard('WH')
t0 = g8(now()); wa = t0 + 0.25; speak('u7'); wb = g8(max(wa + 1.0, span('u7', '而是')[0])); sfx(wa + 0.8, 'wrong'); sfx(wb + 0.8, 'dsp')
after('u7', 0.25); adv(max(0, g8(wb + 1.0 - now()))); CUE['WH'] = dict(t0=t0, a=wa, b=wb, end=now()); hold(0, 0)
# --- 纸条一拍：业内叫它均衡 ---
string('WH-nm', cbot('WH', 250), edge('B5', 'l')); gost('nm', 1.0, 'sine', 0.12)
speak('u8'); fwin('nm', ['B5'], 'u8'); vmark('B5', 'hl', '均衡', 'u8', '均衡', 0.5)
after('u8', 0.125); hold(0, 0)
# --- 纸条一拍：路太长，就在中间设检修站 ---
string('nm-ret', edge('B5'), edge('C1', 'l')); gost('ret', 1.0, 'sine', 0.12)
speak('u9'); fwin('ret', ['C1', 'C2'], 'u9'); vmark('C1', 'hl', '两头均衡不够用', 'u9', '两头补不过来'); vmark('C2', 'hl', '路中间设一个检修站', 'u9', '路中间设一个检修站')
after('u9', 0.125); hold(0, 0)
# --- 演示：检修站（认清、打节拍、重发） → 转运中心 → 回到检修站：后半程重新出发；认错的救不回来 ---
string('ret-K3', edge('C2'), ctop('K3', 250)); gocard('K3')
t3 = g8(now()); ok = t3 + 0.25; speak('u10'); clabel('K3', '检修站：认清、打准节拍、重新发送', -390, -470, ok + 1.25, align='left', size=36); sfx(ok + 1.25, 'dsp')
after('u10', 0.25); hold(0, 0)
string('K3-HB', cbot('K3', -250), ctop('HB', 250)); gocard('HB', 1.12, 0.75)
t0 = g8(now()); speak('u11'); after('u11', 0.25); CUE['HB'] = dict(t0=t0, end=now()); hold(0, 0)
gocard('K3', 1.12, 0.75); speak('u12'); after('u12', 0.125)
speak('u13'); bad = g8(span('u13', '已经认错')[0] - 0.25); clabel('K3', '先认错了：清楚地发出错的', -390, 470, bad + 1.25, align='left', bg='red', size=36); sfx(bad + 1.25, 'wrong')
after('u13', 0.25); adv(max(0, g8(bad + 2.5 - now()))); CUE['K3'] = dict(t0=t3, ok=ok, bad=bad, end=now()); hold(0, 0)
# --- 纸条一拍：Retimer = 重新打节拍 ---
string('K3-rname', cbot('K3', -250), edge('R1', 'r')); gost('rname', 1.0, 'sine', 0.12)
speak('u14'); fwin('rname', ['R1', 'R2'], 'u14'); vmark('R1', 'hl', 'Retimer', 'u14', 'Retimer'); vmark('R2', 'hl', '“重新打节拍”', 'u14', '重新打节拍')
after('u14', 0.125); hold(0, 0)
# --- 演示：Redriver vs Retimer ---
string('rname-K4', edge('R2'), ctop('K4', -250)); gocard('K4')
t0 = g8(now()); rd = t0 + 0.25; speak('u15'); rt = g8(max(rd + 1.75, span('u15', '只做均衡')[0])); me = g8(max(rt + 1.25, span('u15', '更省电')[0] - 0.25))
clabel('K4', 'Redriver：只做均衡', -390, -420, rd + 0.25, align='left', size=38); clabel('K4', 'Retimer：均衡＋认数据＋打节拍', -390, -20, rt + 0.25, align='left', size=38)
sfx(rd, 'thock'); sfx(rt, 'thock'); sfx(me, 'reach')
after('u15', 0.25); adv(max(0, g8(me + 1.25 - now()))); CUE['K4'] = dict(t0=t0, rd=rd, rt=rt, meters=me, end=now()); hold(0, 0)
# --- 回到开头那个均衡器（揭晓：配乐停半拍、换织体） ---
string('K4-P1', cbot('K4', -250), ctop('P1', 300)); go(PC('P1', 0, 20), 1.0, 1.0)
t0 = g8(now()); REV = t0; speak('u16'); ag = g8(t0 + 0.5); clabel('P1', '每秒上千亿个比特，也这样被调、被修', 0, 520, g8(span('u16', '每秒')[0]), size=38, bg='#7fd6b4'); sfx(ag, 'shave', dur=0.75)
after('u16', 0.25); CUE['P1'] = dict(t0=t0, again=ag, end=now()); hold(0, 0)
# --- 一句话 + 你在这里 → 下一篇 ---
ally = [c['at'][1] for c in CLIPS.values()] + [c['at'][1] for c in CARDS.values()]
OVER = dict(x=850, y=round((min(ally) + max(ally)) / 2), z=round(1920 / (max(ally) - min(ally) + 1400), 4))
gost('end', 1.5, 'cubic', 0.10)
speak('u17'); fwin('end', ['E0', 'E1', 'E2', 'E3', 'E7'], 'u17')
vmark('E0', 'hl', '一句话带走', 'u17', '一句话带走'); vmark('E1', 'hl', '修信号分两步', 'u17', '修信号分两步'); vmark('E2', 'hl', '先均衡', 'u17', '先均衡'); vmark('E3', 'hl', 'Retimer认清数据', 'u17', 'Retimer 认清'); vmark('E7', 'hl', '任何检修都有边界', 'u17', '修不回来')
after('u17', 0.25); hold(0, 0)
he = CARDS['HE']; go([he['at'][0], he['at'][1] - 40], 1.15, 1.0); hq = g8(now() - 0.5); CUE['HE'] = dict(t0=hq, end=hq + 1)
speak('u18'); after('u18', 0.125)
def rightof(cid, gap=50): c = CLIPS[cid]; return [round(c['at'][0] + (c['crop'][2] - c['crop'][0]) * c['k'] / 2 + gap, 1), c['at'][1]]
label('下一篇：光模块一半的电，花在哪？', [he['at'][0], round(he['at'][1] + he['h'] / 2 + 60, 1)], LINE['u18'], size=34, r=-0.01)
label('白话光互连 · 04 上', rightof('E0'), LINE['u17'] + 0.5, size=24, align='left', bg='red', r=-0.02)
hold(2.25, 0.02)
