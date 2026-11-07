# ======================= 旁白时间表（04 小红书 · 下集：光模块一半的电，花在哪？） =======================
def cardview(cid, z=1.12):
    h = CARDS[cid]['h']; z = min(z, 1205 / h); dy = max(0, h / 2 - 470 / z)
    if 960 - (h / 2 + dy) * z < 215: dy = (960 - 215) / z - h / 2
    return PC(cid, 0, round(dy)), round(z, 3)
# --- 第一帧：机房里的交换机，插满光模块、光纤里光在跑；圈出一个 → 推进光模块透视 ---
cam(0, PC('RM', 30, 10), 1.08, 'lin')
clabel('RM', '光模块一半的电，花在哪？', 0, -590, 0, size=56, bg='red', r=-0.012, rate=400)
adv(0.125); speak('d1'); after('d1', 0.25)
speak('d2'); fb = g8(span('d2', '大多数')[0]); pk = g8(max(fb + 1.0, span('d2', '都插着')[0]))
clabel('RM', '一个光模块', 130, -118, pk + 0.25, size=40, bg='red'); sfx(fb, 'laser'); sfx(pk, 'thock'); CUE['RM'] = dict(t0=0, fib=fb, pick=pk, end=pk + 2)
T[0] = pk + 0.5; hold(0, 0.04); string('RM-M0', PC('RM', 130, 40), ctop('M0', 0)); go(PC('M0', 30, 0), 1.0, 0.75)
adv(max(0, g8(lend('d2') + 0.125 - now())))
speak('d3'); la = g8(span('d3', '激光器')[0]); ds = g8(max(la + 0.5, span('d3', 'DSP')[0] - 0.25))
clabel('M0', '激光器：小小一个', -285, -330, la, size=36); clabel('M0', 'DSP：最费电', 80, 50, ds, size=40, bg='red'); sfx(ds, 'thock')
after('d3', 0.125); CUE['M0'] = dict(t0=0, end=now()); hold(0, 0.03)
# --- 快递路线图：亮「路上」 ---
string('M0-RT', cbot('M0', 300), ctop('RT', -250)); gocard('RT', 1.15, 0.75)
t0 = g8(now()); speak('d4'); lit = g8(max(t0 + 0.5, span('d4', '检修站')[0] - 0.5))
clabel('RT', '第二站：路上', 0, 250, lit, size=44, bg='red'); sfx(lit, 'thock'); HUD_IN = lit
after('d4', 0.125); CUE['RT'] = dict(t0=t0, lit=lit, end=now()); hold(0, 0)
# --- 纸条一拍：高速采样 → 钻进「高速采样」 ---
string('RT-samp', cbot('RT', -250), edge('S1', 'r')); gost('samp', 1.0, 'sine', 0.12)
speak('d5'); after('d5', 0.125)
speak('d6'); fwin('samp', ['S1'], 'd6'); vmark('S1', 'hl', '高速采样', 'd6', '高速采样')
after('d6', 0.125); hold(0, 0)
ZC = (lambda r: P('S1', (r[0][1] + r[-1][2]) / 2, r[0][3] - 4.5))(runs(2, '高速采样')[0])
a = g8(now()); cam(a + 0.5, ZC, 2.7, 'sine'); cam(a + 1.5, ZC, 40, 'cubic'); T[0] = a + 0.5
speak('d7'); T[0] = a + 1.5
o0 = g8(max(lend('d7') + 0.25, a + 5.0))
LENS = dict(at=ZC, zin=[a + 0.5, a + 1.5], open=[a + 0.75, a + 1.25], core=a + 1.5, samp=[a + 2.0, a + 3.5], lbl=a + 3.75, out=[o0, o0 + 1.0], zmax=40)
sfx(a + 0.5, 'riser', dur=1.0); sfx(a + 1.25, 'boom'); sfx(o0, 'pullout', dur=1.0)
for k_ in range(12): sfx(a + 2.0 + k_ * 0.125, 'click')
string('samp-K5', edge('S3'), ctop('K5', 250))
xy_, z_ = cardview('K5'); cam(o0, ZC, 40, 'lin'); cam(o0 + 1.0, xy_, z_, 'cubic'); T[0] = o0 + 1.0; hold(0.125, 0)
# --- 演示：两种数字（采样的 / 算出来的） → 糊掉的字条 → 回来：前后很多个比特一起算 ---
t5 = g8(now()); wave = t5; s0 = t5 + 0.25; speak('d8'); bt = g8(max(s0 + 1.5, span('d8', '算出来的')[0]))
clabel('K5', '采样得到的数字：描述波形', -390, -110, s0 + 1.0, align='left', size=36); clabel('K5', '算出来的：原本的数据', -390, 450, bt + 0.5, align='left', size=36)
for k_ in range(8): sfx(s0 + k_ * 0.125, 'click')
after('d8', 0.25); hold(0, 0)
string('K5-NT', cbot('K5', -250), ctop('NT', 250)); gocard('NT', 1.12, 0.75)
t0 = g8(now()); speak('d9'); ctx = g8(span('d9', '前后几个字')[0]); gs = g8(max(ctx + 0.75, span('d9', '猜出')[0]))
clabel('NT', '结合前后文', -250, 230, ctx + 0.25, size=40); clabel('NT', '猜出中间那个', 250, -240, gs + 0.25, size=40, bg='red'); sfx(gs, 'click')
after('d9', 0.25); CUE['NT'] = dict(t0=t0, ctx=ctx, guess=gs, end=now()); hold(0, 0)
gocard('K5', 1.12, 0.75); speak('d10'); win = g8(span('d10', '前后很多个比特')[0]); clabel('K5', '把前后几个比特一起算', 390, 120, win + 0.25, align='right', size=36, bg='red'); sfx(win, 'pairs')
after('d10', 0.25); adv(max(0, g8(win + 1.5 - now()))); CUE['K5'] = dict(t0=t5, wave=wave, samples=[s0, s0 + 1.25], win=win, bits=[bt, bt + 1.5], end=now()); hold(0, 0)
# --- 纸条一拍：DSP 不是第三种检修站 → 演示：DSP 在哪 ---
string('K5-where', cbot('K5', 250), edge('W1', 'l')); gost('where', 1.0, 'sine', 0.12)
speak('d11'); fwin('where', ['W1', 'W2'], 'd11'); vmark('W1', 'hl', '不是第三种检修站', 'd11', '不是第三种检修站'); vmark('W2', 'hl', '检修站里的一种工具', 'd11', '检修站里的工具')
after('d11', 0.125); hold(0, 0)
string('where-K6', edge('W2'), ctop('K6', 250)); gocard('K6')
t0 = g8(now()); speak('d12'); bl = [g8(span('d12', 'SerDes')[0]), g8(span('d12', 'Retimer')[0]), g8(span('d12', '光模块')[0])]
clabel('K6', 'DSP：检修站里的一种工具', -390, -380, t0 + 0.25, align='left', size=38)
for tt in bl: sfx(tt, 'stick', n=3)
after('d12', 0.25); CUE['K6'] = dict(t0=t0, blocks=bl, end=now()); hold(0, 0)
# --- 纸条一拍：处理越多，代价越大 → 演示：三级台阶 → 成千上万 ---
string('K6-cost', cbot('K6', 250), edge('X0', 'l')); gost('cost', 1.0, 'sine', 0.12)
speak('d13'); fwin('cost', ['X0'], 'd13'); vmark('X0', 'hl', '处理得越多，代价越大', 'd13', '处理得越多，代价越大')
after('d13', 0.125); hold(0, 0)
string('cost-K7', edge('X0'), ctop('K7', 250)); gocard('K7')
t0 = g8(now()); rows = [t0 + 0.25, t0 + 1.5, t0 + 2.75]; speak('d14'); cl = g8(max(rows[-1] + 0.5, span('d14', '所以系统')[0]))
clabel('K7', '路况越差，处理越重：多花电、多一点延迟', 0, 420, cl, size=34, bg='red')
for tt in rows: sfx(tt, 'thock')
after('d14', 0.25); CUE['K7'] = dict(t0=t0, rows=rows, end=now()); hold(0, 0)
string('K7-MY', cbot('K7', 250), ctop('MY', 250)); gocard('MY', 1.12, 0.75)
t0 = g8(now()); speak('d15'); clabel('MY', '成千上万个，电就累积起来', 0, 360, g8(span('d15', '成千上万')[0]), size=40, bg='red')
after('d15', 0.25); CUE['MY'] = dict(t0=t0, grow=t0 + 0.25, end=now()); hold(0, 0)
# --- 回到开头的光模块（揭晓）：拿掉 DSP，功耗降一半；修信号的活挪到主芯片 ---
string('MY-M1', cbot('MY', -250), ctop('M1', 300)); go(PC('M1', 0, 175), 1.02, 1.0)
t0 = g8(now()); REV = t0; speak('d16'); lp = g8(span('d16', '拿掉')[0]); clabel('M1', '拿掉 DSP：光模块功耗降到一半左右', 0, 230, lp + 1.0, size=38, bg='#7fd6b4'); sfx(lp, 'shave', dur=0.75)
after('d16', 0.125); speak('d17'); mv = g8(max(lp + 2.0, span('d17', '挪到')[0] - 0.5)); clabel('M1', '修信号的活：挪到主芯片', 0, 590, mv + 1.0, size=38, bg='red'); sfx(mv, 'whoosh', dur=0.5, g=0.06)
after('d17', 0.25); adv(max(0, g8(mv + 1.5 - now()))); CUE['M1'] = dict(t0=t0, lpo=lp, move=mv, end=now()); hold(0, 0)
# --- 一句话 + 你在这里 → 下一篇 ---
ally = [c['at'][1] for c in CLIPS.values()] + [c['at'][1] for c in CARDS.values()]
OVER = dict(x=850, y=round((min(ally) + max(ally)) / 2), z=round(1920 / (max(ally) - min(ally) + 1400), 4))
gost('end', 1.5, 'cubic', 0.10)
speak('d18'); fwin('end', ['E0', 'E5', 'E6'], 'd18')
vmark('E0', 'hl', '一句话带走', 'd18', '一句话带走'); vmark('E5', 'hl', 'DSP是用数字算法完成这些处理的工具', 'd18', 'DSP 是用算法修信号的工具'); vmark('E6', 'hl', '处理得越多，代价越大', 'd18', '修得越多，越费电')
after('d18', 0.25); hold(0, 0)
he = CARDS['HE']; go([he['at'][0], he['at'][1] - 40], 1.15, 1.0); hq = g8(now() - 0.5); CUE['HE'] = dict(t0=hq, end=hq + 1)
speak('d19'); after('d19', 0.125)
def rightof(cid, gap=50): c = CLIPS[cid]; return [round(c['at'][0] + (c['crop'][2] - c['crop'][0]) * c['k'] / 2 + gap, 1), c['at'][1]]
label('下一篇：第三站 换乘', [he['at'][0], round(he['at'][1] + he['h'] / 2 + 60, 1)], LINE['d19'], size=34, r=-0.01)
label('白话光互连 · 04 下', rightof('E0'), LINE['d18'] + 0.5, size=24, align='left', bg='red', r=-0.02)
hold(2.25, 0.02)
