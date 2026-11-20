# 样片 B：模型逐层计算（约 10.5 秒）
# 主角：从「周末我想」变出来的一托盘数值（每个字一串数），整段都是同一个托盘、同一批方块。
# 用法：blender -b -P shot_b.py -- --outdir DIR --scale 0.333 --samples 16 --font F.otf [--f0 --f1 | --only ...]
import os, math, random
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib.py'), encoding='utf-8').read())

DUR = 10.5
S, STEP = 0.6, 0.74
TRAY_Z = 0.06; ZT = TRAY_Z + S / 2
PREFIX = '周末我想'
TX = [-1.11 + k * STEP for k in range(4)]          # 字在托盘上的 x（托盘中心在 0）
NC = 6                                              # 每个字变成 6 个数（示意）
CELL, CGAP = 0.17, 0.215
PLATE_Y = -1.15                                     # 数值托盘中心（在字的前面）
GATES = [3.2, 5.2, 7.2]                             # 三道模型层（示意）
X_STOP = 8.7                                        # 托盘停下的位置
PIL_X = [10.3 + k * 0.78 for k in range(4)]; PIL_Y = -1.15
CANDS = [('去', 1.0), ('睡', 0.46), ('看', 0.3), ('出', 0.2)]   # 分数为示意
X_OUT = 13.3                                        # 「去」接到这里的空位

T_CONV = (0.5, 2.4); T_MOVE = (2.3, 7.4); T_SCORE = (7.3, 8.9); T_PICK = (9.0, 10.3)

rnd = random.Random(11)
VAL = [[[rnd.uniform(0.12, 0.62) for j in range(NC)] for k in range(4)] for g in range(len(GATES) + 1)]   # 每过一层，数都变

def build():
    global rig, toks, cells, plate, carrier, gate_tiles, arcs, pillars, cands, slot_m
    new_scene(); studio_lights((4.0, -0.6, 0.4)); desk(0.0)
    rbox((3.2, 0.95, TRAY_Z * 2), (0, 0, 0), bevel=0.04, mat=m_metal('#C9CDD2', 0.42))         # 正式输出托盘（和 A 同一个）
    carrier = bpy.data.objects.new('carrier', None); bpy.context.collection.objects.link(carrier)
    gm = state_mat('plate', '#E8E1D6'); set_state(gm, draft=0.22)
    plate = rbox((3.2, 1.9, 0.06), (0, 0, 0.03), bevel=0.03, mat=gm); plate.parent = carrier
    toks = [Tok(ch, S, f'p{k}') for k, ch in enumerate(PREFIX)]
    cells = []
    for k in range(4):
        row = []
        for j in range(NC):
            m = state_mat(f'c{k}{j}', '#D9C7AE'); c = rbox((CELL, CELL, 1.0), (0, 0, 0), bevel=0.03, mat=m); c.parent = carrier
            row.append((c, m))
        cells.append(row)
    gate_tiles = []
    for gi, gx in enumerate(GATES):          # 一道「层」：金属门框 + 上半截磨砂玻璃，玻璃上是参数块
        gmat = m_metal('#BFC4CA', 0.38)
        for dy in (-1.25, 1.25):
            rbox((0.12, 0.12, 2.3), (gx, PLATE_Y + dy, 1.15), bevel=0.04, mat=gmat)
        rbox((0.12, 2.62, 0.12), (gx, PLATE_Y, 2.3), bevel=0.04, mat=gmat)
        pm = state_mat(f'pane{gi}', '#EEF0F0'); set_state(pm, draft=0.7)
        rbox((0.05, 2.4, 1.25), (gx, PLATE_Y, 1.6), bevel=0.02, mat=pm)
        tiles = []
        for r in range(2):
            for c in range(5):
                tm = state_mat(f't{gi}{r}{c}', '#575B62' if (r + c + gi) % 3 == 0 else '#D9C7AE')
                rbox((0.06, 0.3, 0.22), (gx - 0.05, PLATE_Y - 0.9 + c * 0.45, 1.3 + r * 0.42), bevel=0.04, mat=tm); tiles.append(tm)
        gate_tiles.append(tiles)
    arcs = []                                 # 第一层里「回头看前面的字」：最后一个字连回前面每个字的细线
    for k in range(3):
        am = state_mat(f'arc{k}', TEAL)
        x0, x1 = TX[3], TX[k]
        a = curve_tube([(x0, 0.78, 0.48), ((x0 + x1) / 2, 0.78, 0.95 + 0.18 * (3 - k)), (x1, 0.78, 0.48)], 0.02, am); a.parent = carrier
        arcs.append((a, am))
    pillars = []
    for k, (ch, sc_) in enumerate(CANDS):
        pm = state_mat(f'pil{k}', AMBER if k == 0 else '#D6CBB9'); p = rbox((0.5, 0.5, 1.0), (0, 0, 0), bevel=0.06, mat=pm)
        pillars.append((p, pm))
    cands = [Tok(ch, S, f'cand{k}') for k, (ch, _) in enumerate(CANDS)]
    rbox((1.6, 0.95, TRAY_Z * 2), (X_OUT + 0.2, PIL_Y, 0), bevel=0.04, mat=m_metal('#C9CDD2', 0.42))   # 下一步的输出位
    slot_m = state_mat('slot', AMBER)
    for (sx, sy, dx, dy) in ((0.66, 0.05, 0, 0.33), (0.66, 0.05, 0, -0.33), (0.05, 0.66, 0.33, 0), (0.05, 0.66, -0.33, 0)):
        rbox((sx, sy, 0.03), (X_OUT + dx, PIL_Y + dy, TRAY_Z + 0.015), bevel=0.012, mat=slot_m)
    rig = Rig(fstop=3.5)

def tracked():
    d = {'托盘': carrier, '去': cands[0].root}
    d.update({f'字{ch}': t.root for ch, t in zip(PREFIX, toks)})
    d['想的数(第1个)'] = cells[3][0][0]
    return d

def carrier_x(t):
    return lerp(0.0, X_STOP, sstep(*T_MOVE, t))

def cell_val(k, j, xw):
    v = VAL[0][k][j]
    for gi, gx in enumerate(GATES):
        u = sstep(gx - 0.12, gx + 0.22, xw)
        v += (VAL[gi + 1][k][j] - VAL[gi][k][j]) * u
    return v

def pose(t):
    xc = carrier_x(t); carrier.location = (xc, PLATE_Y, 0.0)
    conv = [sstep(T_CONV[0] + 0.28 * k, T_CONV[0] + 0.28 * k + 1.0, t) for k in range(4)]
    score = sstep(*T_SCORE, t); pick = sstep(*T_PICK, t)
    # 字：往前倒到托盘后沿，缩成小牌子，从此跟着托盘走（不消失）
    for k, tk in enumerate(toks):
        u = conv[k]
        p_tray = (TX[k], 0, ZT)
        p_plate = (xc + TX[k], PLATE_Y + 0.78, 0.06 + S * 0.62 / 2 + 0.01)
        hop = 0.35 * math.sin(math.pi * u)
        pos = mix3(p_tray, p_plate, u); pos = (pos[0], pos[1], pos[2] + hop)
        tk.put(pos, pitch=-0.35 * math.sin(math.pi * u), scale=lerp(1.0, 0.62, u))
        tk.look(alpha=1.0 - 0.45 * score * (k < 3))
    # 数：从字的脚下往前滑出来，一边长高；过每一层，高度变一次
    for k in range(4):
        u = conv[k]
        for j in range(NC):
            c, m = cells[k][j]
            uj = sstep(0.15 + 0.1 * j, 0.55 + 0.1 * j, u)
            xw = xc + TX[k]
            v = cell_val(k, j, xw)
            h = max(0.01, v * uj)
            y_local = lerp(0.78, 0.45 - j * CGAP, uj)
            c.location = (TX[k], y_local, 0.06 + h / 2); c.scale = (lerp(0.4, 1, uj), lerp(0.4, 1, uj), h)
            shade = clamp((v - 0.12) / 0.5)
            col = tuple(hex3('#E3D6C2')[i] + (hex3('#4F535A')[i] - hex3('#E3D6C2')[i]) * shade for i in range(3))
            glow = 0.0
            for gx in GATES: glow += 1.4 * math.exp(-((xw - gx) / 0.25) ** 2)
            set_state(m, col=col, glow=glow, glow_col=AMBER_L, alpha=1.0 if uj > 0.01 else 0.0)
            c.hide_render = uj < 0.01
            # 最后一个字（「想」所在的位置）的数：出了最后一层，飞向分数柱
            if k == 3 and t > T_SCORE[0]:
                tgt = 0 if j < 3 else j - 2
                uf = sstep(T_SCORE[0] + 0.12 * j, T_SCORE[0] + 0.12 * j + 0.8, t)
                start = Vector((xc + TX[3], PLATE_Y + 0.45 - j * CGAP, 0.06 + h / 2))
                end = Vector((PIL_X[tgt], PIL_Y, 0.15))
                p = start.lerp(end, uf); p.z += 1.2 * math.sin(math.pi * uf)
                c.location = Vector(p) - Vector(carrier.location)
                sq = 1 - sstep(0.85, 1.0, uf); c.scale = (sq, sq, h * sq + 0.001)
                c.hide_render = sq < 0.02
    # 层：托盘经过时，门上的参数块亮一下（这一层在拿数和参数相乘、相加）
    for gi, gx in enumerate(GATES):
        near = math.exp(-((xc - gx) / 1.2) ** 2)
        for i, tm in enumerate(gate_tiles[gi]):
            set_state(tm, glow=1.6 * near * (0.6 + 0.4 * math.sin(t * 9 + i)), glow_col=AMBER_L)
    # 第一层里：最后一个字连回前面的字（回头看）
    a1 = math.exp(-((xc - GATES[0]) / 0.9) ** 2)
    for k, (a, am) in enumerate(arcs):
        set_state(am, glow=2.2 * a1, glow_col=TEAL, alpha=clamp(a1 * 1.6)); a.hide_render = a1 < 0.05
    # 分数柱：数飞进来，柱子长到各自的分数；候选字坐在柱顶（半透明 = 还没定）
    for k, ((p, pm), (ch, scv)) in enumerate(zip(pillars, CANDS)):
        g = sstep(T_SCORE[0] + 0.5, T_SCORE[1], t); H = max(0.02, 1.7 * scv * g)
        p.location = (PIL_X[k], PIL_Y, H / 2); p.scale = (1, 1, H); p.hide_render = g < 0.01
        set_state(pm, glow=1.2 * pick if k == 0 else 0.0, glow_col=AMBER, alpha=1.0 - 0.5 * pick * (k > 0))
        tk = cands[k]
        top = (PIL_X[k], PIL_Y, H + S / 2 + 0.02)
        if k == 0 and t > T_PICK[0]:
            # 「去」被选中：离开柱顶，继续往右，落进下一个空位，变成正式的字
            u = sstep(T_PICK[0] + 0.15, T_PICK[1], t)
            dst = (X_OUT, PIL_Y, ZT)
            pos = mix3(top, dst, u); pos = (pos[0], pos[1], pos[2] + 0.9 * math.sin(math.pi * u))
            tk.put(pos, pitch=0.0); tk.look(draft=1 - u, glow=1.8 * (1 - 0.6 * u), glow_col=AMBER)
        else:
            tk.put(top, scale=max(0.001, g)); tk.look(draft=1.0, alpha=g * (1.0 - 0.5 * pick * (k > 0)))
    set_state(slot_m, glow=(1.0 + 0.6 * math.sin(t * 4)) * sstep(T_SCORE[1] - 0.5, T_SCORE[1], t) * (1 - sstep(T_PICK[1] - 0.2, T_PICK[1], t)),
              alpha=sstep(T_SCORE[1] - 0.5, T_SCORE[1], t) * (1 - sstep(T_PICK[1] - 0.2, T_PICK[1], t)))

    ANCH['row'] = (TX[1], 0, ZT + 0.7); ANCH['plate'] = (xc - 0.6, PLATE_Y - 1.0, 0.1)
    ANCH['gate'] = (GATES[0], PLATE_Y, 2.6); ANCH['pill'] = (PIL_X[1], PIL_Y, 1.6); ANCH['out'] = (X_OUT, PIL_Y, ZT + 0.75)
    ANCH['qu'] = cands[0].root.location.copy() + Vector((0, 0, 0.6))
    # 相机：先看字和托盘，然后跟着托盘穿过三层（同一个侧后方的位置跟着走），最后跟着「去」往右
    kf = sstep(0.0, 2.6, t); kp = sstep(7.2, 9.0, t); ko = sstep(9.2, 10.5, t)
    follow = (xc + 0.4, PLATE_Y + 0.2, 0.5)
    tgt = mix3((0.0, -0.55, 0.55), follow, kf); tgt = mix3(tgt, (PIL_X[1] - 0.1, PIL_Y, 0.85), kp); tgt = mix3(tgt, (X_OUT - 1.3, PIL_Y, 0.7), ko)
    off = mix3((-1.4, -4.6, 3.0), (-2.2, -4.4, 2.3), kf); off = mix3(off, (-1.6, -5.4, 2.8), kp)
    loc = (tgt[0] + off[0], tgt[1] + off[1], tgt[2] + off[2])
    rig.set(loc, tgt, lens=lerp(40, 38, kp))

SHOT = {'DUR': DUR, 'pose': pose, 'tracked': tracked}
build()
run(SHOT)
