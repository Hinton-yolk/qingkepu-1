# ======================= 旁白时间表（小红书改版 · 上集：线长一点，速度砍半？） =======================
def cardview(cid, z=1.12):
    h = CARDS[cid]['h']; z = min(z, 1205 / h); dy = max(0, h / 2 - 470 / z)
    if 960 - (h / 2 + dy) * z < 215: dy = (960 - 215) / z - h / 2
    return PC(cid, 0, round(dy)), round(z, 3)
# --- 钩子：第一帧就是桌上的两根雷电线 + 贴在线上的大字问题 ---
def gocab(cid, d=1.0): go(PC(cid, 0, 40), 1.1, d)       # 雷电线：镜头对准线的中间，放大一点，下面不留空
cam(0, PC('C0', 0, 40), 1.1, 'lin')
clabel('C0', '长一点，速度砍半？', 0, -470, 0, size=60, bg='red', r=-0.012, rate=400)   # 第一帧就是完整的大字问题，不打字
adv(0.125); speak('X1'); after('X1', 0.25)
speak('X2'); a_ = g8(span('X2', '0.8 米')[0]); b_ = g8(max(a_ + 0.75, span('X2', '2 米')[0]))
clabel('C0', '0.8 米 · 40G', 0, -350, a_, size=46); clabel('C0', '2 米 · 20G', 0, 420, b_, size=46, bg='red')
after('X2', 0.125)
speak('X3'); ch_ = g8(span('X3', '带芯片')[0]); fb_ = g8(max(ch_ + 0.75, span('X3', '光纤线')[0]))
clabel('C0', '带芯片的线', 290, 30, ch_, size=40); clabel('C0', '光纤线', -290, 30, fb_, size=40, bg='#3fb5a5')
sfx(ch_, 'dsp'); sfx(fb_, 'laser')
after('X3', 0.125); CUE['C0'] = dict(t0=0, chip=ch_, fiber=fb_, end=now()); hold(0, 0.05)
# --- 快递路线图：亮第二站「路上」 ---
string('C0-RT', cbot('C0', 300), ctop('RT', -250)); gocard('RT', 1.15, 0.75)
t0 = g8(now()); speak('X4'); lit = g8(max(t0 + 0.5, span('X4', '也卡在')[0] - 0.25))
clabel('RT', '第二站：路上', 0, 250, lit, size=44, bg='red'); sfx(lit, 'thock'); HUD_IN = lit
after('X4', 0.125); CUE['RT'] = dict(t0=t0, lit=lit, end=now()); hold(0, 0)
# --- 电信号在铜线上遭遇了什么：清楚的台阶跑过铜线变糊（第一个机制演示） ---
string('RT-H0', cbot('RT', 250), ctop('H0', 250)); gocard('H0', 1.12, 0.5)
e0 = g8(now()); speak('X5'); lA = g8(e0 + 1.0); lB = g8(max(lA + 1.0, span('X5', '遭遇了什么')[0]))
clabel('H0', '出发时：清楚', -330, 210, lA, align='left'); clabel('H0', '跑过铜线：糊了', 380, 210, lB, bg='red', align='right')
sfx(e0, 'thock'); sfx(lB, 'blur')
after('X5', 0.375); adv(max(0, g8(lB + 1.0 - now()))); CUE['H0'] = dict(t0=e0, e0=e0, end=now()); hold(0, 0)
# --- 出发时：方方正正的台阶 ---
string('H0-ideal', cbot('H0', 250), edge('W1', 'l')); gost('ideal', 1.0, 'sine', 0.12)
speak('X6'); fwin('ideal', ['W1', 'W2', 'W3', 'W4'], 'X6')
vmark('W1', 'hl', '高、低两种电平', 'X6', '高电平是 1'); vmark('W1', 'hl', '1和0', 'X6', '低电平是 0'); vmark('W4', 'hl', '方方正正的台阶', 'X6', '方方正正的台阶')
after('X6', 0.375); hold(0, 0)
# --- 第一，变弱 → 楼道里喊人 → 高低差距被压缩 ---
gost('weak')
speak('X8'); fwin('weak', ['A1', 'A2', 'A3'], 'X8'); vmark('A1', 'hl', '变弱', 'X8', '变弱'); vmark('A2', 'hl', '有损耗', 'X8', '有损耗'); vmark('A3', 'hl', '力气就越小', 'X8', '力气越小')
after('X8'); hold(0, 0)
string('weak-K1', edge('A3'), ctop('K1', 250)); gocard('K1')
t0 = g8(now()); W_ = [t0 + 0.25 + 0.5 * i for i in range(6)]
speak('X9'); far_ = g8(max(t0 + 1.0, span('X9', '离得越远')[0]))
clabel('K1', '楼道里喊人：越远，声音越小', -390, -260, far_, align='left')
for tt in W_: sfx(tt, 'shout')
after('X9', 0.25); adv(max(0, g8(W_[-1] + 1.0 - now()))); CUE['K1'] = dict(t0=t0, words=W_, fast=t0 + 3.5, end=now()); hold(0, 0)
string('K1-K3', cbot('K1', -250), ctop('K3', -250)); gocard('K3')
t0 = g8(now()); wave = t0 + 0.25; speak('X10'); env = g8(max(wave + 1.25, span('X10', '差距被压缩')[0]))
clabel('K3', '出发：方方正正的台阶', -390, -330, wave, align='left'); clabel('K3', '跑远了：高低差距被压缩', 390, 280, env + 0.5, align='right', bg='red')
sfx(wave, 'thock'); sfx(env, 'envE')
after('X10', 0.375); adv(max(0, g8(env + 1.5 - now()))); CUE['K3'] = dict(t0=t0, wave=wave, env=env, end=now()); hold(0, 0)
# --- 第二，拖尾（纸条读一句）→ 钻进「棱角」→ 直接到拖尾卡片（不再回纸条） ---
string('K3-tail', cbot('K3', 250), edge('B1', 'l')); gost('tail', 1.0, 'sine', 0.12)
speak('X11'); fwin('tail', ['B1', 'B2', 'B3'], 'X11'); vmark('B1', 'hl', '拖尾', 'X11', '拖尾'); vmark('B2', 'hl', '削弱快速跳变的力度', 'X11', '削弱快速跳变'); vmark('B3', 'hl', '更厉害', 'X11', '更厉害')
after('X11', 0.125); hold(0, 0)
ZC = (lambda r: P('B4', (r[0][1] + r[-1][2]) / 2, r[0][3] - 4.5))(runs(1, '棱角')[0])
a = g8(now()); cam(a + 0.5, ZC, 2.7, 'sine'); cam(a + 1.5, ZC, 40, 'cubic'); T[0] = a + 0.5
speak('X13'); T[0] = a + 1.5
sharp = a + 1.5; s0 = g8(max(sharp + 0.5, span('X13', '棱角一点点被磨圆')[0])); shave = [s0, s0 + 1.5]
lbl = s0 + 0.75; lbl2 = shave[1] + 0.25; o0 = g8(max(lend('X13') + 0.5, lbl2 + 1.0))
LENS = dict(at=ZC, zin=[a + 0.5, a + 1.5], open=[a + 0.75, a + 1.25], sharp=sharp, shave=shave, lbl=lbl, lbl2=lbl2, out=[o0, o0 + 1.0], zmax=40)
sfx(a + 0.5, 'riser', dur=1.0); sfx(a + 1.25, 'boom'); sfx(s0, 'shave', dur=1.5); sfx(o0, 'pullout', dur=1.0)
for txt_, at_ in [('方方正正的台阶', sharp), ('棱角被削掉', lbl), ('跳变变得迟缓', lbl2)]: SFX.append(dict(t=at_, kind='label', text=txt_, rate=14))
string('tail-K4', edge('B7'), ctop('K4', 250))
xy_, z_ = cardview('K4', 1.1); cam(o0, ZC, 40, 'lin'); cam(o0 + 1.0, xy_, z_, 'cubic'); T[0] = o0 + 1.0; hold(0.125, 0)
# 卡片：一个比特拖出尾巴 → 一串比特的尾巴叠在一起（车库回音；这时还不报名字）
t0 = g8(now()); single = t0; speak('X14b'); m0 = g8(max(t0 + 0.5, span('X14b', '拖出一条尾巴')[0])); after('X14b', 0.25)
speak('X15'); after('X15', 0.25); speak('X16')
seq = g8(max(m0 + 1.25, span('X16', '下一个字已经出口')[0])); sm = g8(max(seq + 1.0, span('X16', '糊成一片')[0])); ask = sm + 1.0
clabel('K4', '一个比特：拖出一条尾巴', -390, -440, m0 + 0.75, align='left'); clabel('K4', '尾巴压到后面的比特上', -390, 30, seq + 0.5, align='left', bg='red')
clabel('K4', '像车库回音：糊成一片', 390, 470, sm + 0.25, align='right', bg='red')
sfx(single, 'thock'); sfx(m0, 'shave', dur=0.75); sfx(seq, 'pairs'); sfx(sm, 'blur'); sfx(ask, 'wrong')
after('X16', 0.25); adv(max(0, g8(ask + 1.0 - now()))); CUE['K4'] = dict(t0=t0, single=single, morph=[m0, m0 + 0.75], seq=seq, sum=sm, ask=ask, end=now()); hold(0, 0)
string('K4-tail', cbot('K4', 250), edge('B8', 'l')); gost('tail', 1.0)
speak('X17'); fwin('tail', ['B8', 'B9'], 'X17'); vmark('B8', 'hl', '前后比特互相干扰', 'X17', '前后比特互相干扰'); vmark('B9', 'hl', '码间干扰', 'X17', '码间干扰', 0.5)
after('X17', 0.25); hold(0, 0)
# --- 认错一个：照片花了、消息乱码 ---
string('tail-G1', edge('B9'), ctop('G1', 250)); gocard('G1')
t0 = g8(now()); speak('X20'); ph = g8(max(t0 + 0.25, span('X20', '照片花了一块')[0])); ms = g8(max(ph + 0.75, span('X20', '乱码')[0] - 0.25))
clabel('G1', '照片花了一块', -210, 240, ph + 0.25, bg='red'); clabel('G1', '消息冒出乱码', 220, 0, ms + 0.25, bg='red')
sfx(ph, 'wrong'); sfx(ms, 'wrong')
after('X20', 0.375); adv(max(0, g8(ms + 1.25 - now()))); CUE['G1'] = dict(t0=t0, photo=ph, msg=ms, end=now()); hold(0, 0)
# --- 为什么越快就越糟（纸条一句）→ 卡片 ---
string('G1-far', cbot('G1', -250), edge('F3', 'r')); gost('far', 1.0, 'sine', 0.12)
speak('U16'); fwin('far', ['F3', 'F4', 'F5'], 'U16'); vmark('F3', 'hl', '越快', 'U16', '越快'); vmark('F4', 'hl', '时间减半', 'U16', '时间减半'); vmark('F5', 'hl', '变得更窄', 'U16', '变窄')
after('U16'); hold(0, 0)
string('far-K6', edge('F5'), ctop('K6', 250)); gocard('K6')
t0 = g8(now()); rowA = t0 + 0.25; hitA = rowA + 0.75; adv(0.75); speak('X24'); rowB = g8(LINE['X24'] + 0.125); hitB = g8(max(rowB + 1.0, span('X24', '压到更多后面的比特上')[0]))
clabel('K6', '原来', -390, -400, rowA, align='left'); clabel('K6', '快一倍：台阶更窄，尾巴还那么长', -390, 0, rowB + 0.25, align='left', size=38)
clabel('K6', '压到更多比特上，尾巴也更重', 390, 400, hitB + 0.25, align='right', bg='red', size=38)
sfx(rowA, 'thock'); sfx(rowB, 'thock'); sfx(hitB, 'wrong')
after('X24'); speak('X25'); after('X25', 0.375); CUE['K6'] = dict(t0=t0, rowA=rowA, rowB=rowB, hitA=hitA, hitB=hitB, end=now()); hold(0, 0)
# --- 越快，可靠距离越短 → 回到开头那根线 → 换乘光 ---
string('K6-reach', cbot('K6', 250), edge('R1', 'l')); gost('reach', 1.0, 'sine', 0.12)
speak('X27'); fwin('reach', ['R1', 'R2'], 'X27'); vmark('R1', 'hl', '跑得越快', 'X27', '跑得越快'); vmark('R2', 'hl', '距离就越短', 'X27', '距离就越短')
after('X27'); hold(0, 0)
string('reach-C1', edge('R2', 'r'), ctop('C1', -300)); gocab('C1')
t0 = g8(now()); speak('X28'); rg = g8(max(t0 + 0.25, span('X28', '长到 2 米')[0]))
clabel('C1', '0.8 米 · 40G', 0, -350, t0, size=46); clabel('C1', '2 米：只剩 20G', 0, 430, rg + 0.25, size=50, bg='red')
sfx(rg, 'thock')
after('X28', 0.25); CUE['C1'] = dict(t0=t0, ring=rg, end=now()); hold(0, 0)
REV = CUE['C1']['t0']                  # 揭晓：回到开头那根线（配乐在这里停半拍、换织体）
string('C1-K7', cbot('C1', -300), ctop('K7', 250)); gocard('K7', 1.15)
t0 = g8(now()); slow, fast = t0, t0 + 1.0; speak('X29'); so = g8(max(fast + 0.75, span('X29', '换乘光')[0]))
clabel('K7', '慢：能可靠地跑很远', -400, -235, slow, align='left', size=38); clabel('K7', '快：没多远就糊了', -400, 5, fast, align='left', bg='red', size=38)
clabel('K7', '所以：换乘光', 400, 245, so, align='right', size=40)
sfx(slow, 'reach'); sfx(fast, 'reach2')
after('X29', 0.375); adv(max(0, g8(so + 1.0 - now()))); CUE['K7'] = dict(t0=t0, slow=slow, fast=fast, end=now()); hold(0, 0)
# --- 收尾：一句话带走 → 小路线图「你在这里」→ 下一篇 ---
ally = [c['at'][1] for c in CLIPS.values()] + [c['at'][1] for c in CARDS.values()]
OVER = dict(x=850, y=round((min(ally) + max(ally)) / 2), z=round(1920 / (max(ally) - min(ally) + 1400), 4))
gost('end', 1.5, 'cubic', 0.10)
speak('U22'); fwin('end', ['E0', 'E1', 'E2'], 'U22')
vmark('E0', 'hl', '一句话带走', 'U22', '一句话带走'); vmark('E1', 'hl', '变弱、拖尾', 'U22', '变弱、拖尾'); vmark('E2', 'hl', '跑得越快', 'U22', '跑得越快')
after('U22', 0.25); hold(0, 0)
he = CARDS['HE']; go([he['at'][0], he['at'][1] - 40], 1.15, 1.0); hq = g8(now() - 0.5); CUE['HE'] = dict(t0=hq, end=hq + 1)
speak('U23'); after('U23', 0.125)
def rightof(cid, gap=50): c = CLIPS[cid]; return [round(c['at'][0] + (c['crop'][2] - c['crop'][0]) * c['k'] / 2 + gap, 1), c['at'][1]]
label('下一篇：AI 机柜为什么塞满铜线？', [he['at'][0], round(he['at'][1] + he['h'] / 2 + 60, 1)], LINE['U23'], size=34, r=-0.01)
label('白话光互连 · 03 上', rightof('E0'), LINE['U22'] + 0.5, size=24, align='left', bg='red', r=-0.02)
hold(2.25, 0.02)
