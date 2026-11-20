# 样片 A：文字生成与分叉（约 14 秒）
# 主角：一排持续存在的实体汉字「周末我想」+ 下一个位置的两个候选「去 / 睡」和它们各自假设的续写。
# 用法：blender -b -P shot_a.py -- --outdir DIR --scale 0.333 --samples 16 --font F.otf [--f0 --f1 | --only 1.0,5.0]
import os, math
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib.py'), encoding='utf-8').read())

DUR = 14.0
S, STEP = 0.6, 0.74
TRAY_Z = 0.06                       # 正式输出托盘的顶面
ZT = TRAY_Z + S / 2                 # 字块放在托盘上时的中心高度
ZG = 0.065 + 0.025 + S / 2           # 字块放在玻璃轨道上时的中心高度
XS = -0.04                          # 下一个位置（空位）
PREFIX = '周末我想'
PX = [XS - (len(PREFIX) - k) * STEP for k in range(len(PREFIX))]
def _branch(side, L):
    a = math.radians(38) * side; c, n = math.cos(a), math.sin(a)
    p1 = (XS + 0.6, 0.22 * side)
    return Path([(XS, 0, ZG), (XS + 0.3, 0.05 * side, ZG), (p1[0], p1[1], ZG)] + [(p1[0] + c * d, p1[1] + n * d, ZG) for d in (0.8, 1.8, L)])
UP = _branch(1, 4.9)
DN = _branch(-1, 3.4)
SC = 1.05                           # 候选在轨道上的位置（弧长）
FUT_U, FUT_D = '海边看日落', '个懒觉'

# ---------------- 时间表（秒） ----------------
T_RISE = (1.6, 2.6)        # 两个候选从空位里升起来
T_SPLIT = (2.6, 4.0)       # 两条轨道从空位长出去，候选各沿一条滑到岔口后
T_FUT0, T_FUT_GAP, T_FUT_DUR = 4.0, 0.5, 1.1   # 续写的字一个接一个从前一个字后面滑出来
T_CHOOSE = (9.3, 10.4)     # 采用上面一条，下面一条退到背景
T_BACK = (10.6, 12.4)      # 「去」沿轨道退回空位，变成正式的字
T_NEXT = (12.4, 13.2)      # 下一个空位亮起

def build():
    global sc_, rig, prefix, cand_u, cand_d, fut_u, fut_d, strip_u, strip_d, slot_m, slot2_m, tray
    sc_ = new_scene(); studio_lights((0.8, 0, 0.3))
    desk(0.0)
    tray = rbox((XS + 0.45 - (PX[0] - 0.45) + STEP, 0.95, TRAY_Z * 2), ((XS + 0.45 + STEP + PX[0] - 0.45) / 2, 0, 0), bevel=0.04, mat=m_metal('#C9CDD2', 0.42))
    prefix = [Tok(ch, S, f'p{k}') for k, ch in enumerate(PREFIX)]
    cand_u, cand_d = Tok('去', S, 'cand_qu', col=WARM), Tok('睡', S, 'cand_shui', col=WARM)
    fut_u = [Tok(ch, S, f'u{k}') for k, ch in enumerate(FUT_U)]
    fut_d = [Tok(ch, S, f'd{k}') for k, ch in enumerate(FUT_D)]
    gm_u, gm_d = state_mat('strip_u', '#EDEBE6'), state_mat('strip_d', '#EDEBE6')
    set_state(gm_u, draft=0.55, col='#E4E7E8'); set_state(gm_d, draft=0.55, col='#E4E7E8')
    strip_u, strip_d = Grow(UP, 0.84, gm_u, thick=0.025, name='strip_u', z=0.09, s0=0.5), Grow(DN, 0.84, gm_d, thick=0.025, name='strip_d', z=0.13, s0=0.5)
    slot_m = state_mat('slot', AMBER); slot2_m = state_mat('slot2', AMBER)
    for m_, x in ((slot_m, XS), (slot2_m, XS + STEP)):     # 空位：托盘上一个琥珀色的方框
        for (sx, sy, dx, dy) in ((0.66, 0.05, 0, 0.33), (0.66, 0.05, 0, -0.33), (0.05, 0.66, 0.33, 0), (0.05, 0.66, -0.33, 0)):
            rbox((sx, sy, 0.03), (x + dx, dy, TRAY_Z + 0.015), bevel=0.012, mat=m_)
    rig = Rig(fstop=3.2)

def tracked():
    d = {'周': prefix[0].root, '想': prefix[3].root, '去': cand_u.root, '睡': cand_d.root}
    d.update({ch: t.root for ch, t in zip(FUT_U, fut_u)}); d.update({ch: t.root for ch, t in zip(FUT_D, fut_d)})
    return d

def on_path(tok, path, s, z_lift=0.0, scale=1.0):
    p = path.at(s); tok.put((p[0], p[1], p[2] + z_lift), yaw=yaw_of(path.tan(s)) * 0.35, scale=scale)

def pose(t):
    # 前面的字：稳定，只有「想」在开头刚落位（轻轻回弹）
    for k, tk in enumerate(prefix):
        z = ZT
        if k == 3: z = ZT + 0.5 * (1 - back_out(lin(0.0, 0.7, t)))
        tk.put((PX[k], 0, z)); tk.look()
    # 空位：一直在呼吸；候选升起后变暗；「去」落进来后消失
    pulse = 0.5 + 0.5 * math.sin(t * 4.0)
    set_state(slot_m, glow=(1.2 + 1.0 * pulse) * (1 - 0.6 * sstep(*T_RISE, t)) * (1 - sstep(T_BACK[1] - 0.4, T_BACK[1], t)), alpha=1 - sstep(T_BACK[1] - 0.3, T_BACK[1], t))
    set_state(slot2_m, glow=(1.2 + 1.0 * pulse) * sstep(*T_NEXT, t), alpha=sstep(*T_NEXT, t))
    # 轨道：从空位长出去
    g = sstep(*T_SPLIT, t)
    strip_u.show(0.55 + g * (UP.L - 0.55) if g > 0 else 0); strip_d.show(0.55 + g * (DN.L - 0.55) if g > 0 else 0)
    ch_ = sstep(*T_CHOOSE, t)
    set_state(strip_d.mat, alpha=1 - 0.75 * ch_); set_state(strip_u.mat, glow=0.25 * ch_ * (1 - sstep(*T_BACK, t)), glow_col=AMBER_L)

    # 两个候选：先一起从空位升起（并排、半透明 = 还没定），再各沿一条轨道滑到岔口后面
    r = sstep(*T_RISE, t); sp = sstep(*T_SPLIT, t)
    for tok, path, side in ((cand_u, UP, 1), (cand_d, DN, -1)):
        if t < T_SPLIT[0]:
            z = lerp(ZT - 0.75, ZT + 0.75, r); tok.put((XS + 0.12 * side * r, side * 0.6 * r, z), scale=lerp(0.6, 1.0, r))
        else:
            # 从空位上方落到轨道上，沿轨道滑到 SC
            s = SC * sp; lift = 0.75 * (1 - sstep(T_SPLIT[0], T_SPLIT[0] + 0.7, t)) + 0.15 * math.sin(math.pi * sp)
            p0 = (XS + 0.12 * side, side * 0.6, ZT + 0.75); p1 = path.at(s)
            u = sstep(T_SPLIT[0], T_SPLIT[0] + 0.5, t)
            pos = mix3(p0, (p1[0], p1[1], p1[2] + lift), u)
            tok.put(pos, yaw=yaw_of(path.tan(s)) * 0.35 * u)
        tok.look(draft=1.0, alpha=r if t < T_RISE[1] else 1.0)
    # 被采用的「去」：发琥珀光，沿上面的轨道退回空位，一路从玻璃变成陶瓷，落进空位
    b = sstep(*T_BACK, t)
    if t >= T_BACK[0]:
        s = SC * (1 - b); p = UP.at(s); hop = 0.45 * math.sin(math.pi * b)
        z = p[2] + hop if b < 0.85 else lerp(ZG, ZT, sstep(T_BACK[0] + 0.85 * (T_BACK[1] - T_BACK[0]), T_BACK[1], t))
        cand_u.put((p[0], p[1], z), yaw=yaw_of(UP.tan(s)) * 0.35 * (1 - b))
    cand_u.look(draft=1.0 - b, glow=1.6 * ch_ * (1 - 0.7 * b), glow_col=AMBER, alpha=1.0 if t >= T_RISE[1] else r)

    # 续写：每个字从前一个字后面滑出来，沿轨道走到自己的位置，一路转向（不弹出）
    for path, toks, lead, k0 in ((UP, fut_u, cand_u, 0), (DN, fut_d, cand_d, 1)):
        for k, tok in enumerate(toks):
            t0 = T_FUT0 + (k + k0 * 0.5) * T_FUT_GAP
            u = sstep(t0, t0 + T_FUT_DUR, t)
            s_from, s_to = SC + k * STEP, SC + (k + 1) * STEP
            if t < t0: tok.put((0, 0, -5), scale=0.0); tok.look(alpha=0.0); continue
            on_path(tok, path, lerp(s_from, s_to, u), z_lift=0.1 * math.sin(math.pi * u), scale=lerp(0.55, 1.0, sstep(t0, t0 + 0.4, t)))
            fade_bg = ch_ if path is DN else 0.0
            tok.look(draft=1.0, alpha=min(1.0, lin(t0, t0 + 0.25, t)) * (1 - 0.7 * fade_bg), glow=0.35 * ch_ * (1 - b) if path is UP else 0.0, glow_col=AMBER_L)
    for tok in [cand_d]:
        tok.look(draft=1.0, alpha=(r if t < T_RISE[1] else 1.0) * (1 - 0.7 * ch_))
    for tok in [cand_d] + fut_d:
        x, y, z = tok.root.location; tok.root.location = (x, y, z - 0.12 * ch_)

    # 2D 提示的锚点
    ANCH['slot'] = (XS, 0, ZT + 0.9); ANCH['up_end'] = UP.at(SC + 5 * STEP + 0.2); ANCH['dn_end'] = DN.at(SC + 3 * STEP + 0.2)
    ANCH['up_mid'] = UP.at(SC + 2.5 * STEP); ANCH['row'] = (PX[1], 0, ZT + 0.75); ANCH['next'] = (XS + STEP, 0, ZT + 0.65)
    ANCH['ghost'] = UP.at(SC + 3 * STEP)

    # 相机：开头从斜上方看这排字；候选出来后跟着它们往右、拉开看两条路；采用后跟着「去」回到正式输出
    k1 = sstep(1.8, 5.5, t); k2 = sstep(6.0, 9.0, t); k3 = sstep(10.2, 12.8, t)
    tgt = mix3((-1.2, 0.1, 0.35), (0.8, 0.0, 0.35), k1); tgt = mix3(tgt, (1.6, 0.0, 0.3), k2); tgt = mix3(tgt, (-0.5, 0.25, 0.35), k3)
    loc = mix3((-1.9, -3.6, 5.6), (0.3, -4.2, 6.8), k1); loc = mix3(loc, (1.3, -4.6, 7.8), k2); loc = mix3(loc, (-1.1, -3.7, 5.8), k3)
    loc = (loc[0] + 0.15 * math.sin(t * 0.6), loc[1], loc[2])
    rig.set(loc, tgt, lens=lerp(40, 36, k2) + 4 * k3)

SHOT = {'DUR': DUR, 'pose': pose, 'tracked': tracked}
build()
run(SHOT)
