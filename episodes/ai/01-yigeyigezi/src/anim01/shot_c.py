# 样片 C：推测解码的完整动作（约 17 秒）
# 小模型提出候选 → 大模型集中验证 → 接受正确前缀 → 第一个不对的位置由大模型纠正 → 继续生成。
# 主角：同一组草稿字块「海 边 吃 饭」（被提出、被验证、被接受或退回）+ 同一条输出托盘上的正式文字。
# 用法：blender -b -P shot_c.py -- --outdir DIR --scale 0.333 --samples 16 --font F.otf [--f0 --f1 | --only ...]
import os, math
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib.py'), encoding='utf-8').read())

DUR = 17.0
S, STEP = 0.6, 0.74
TRAY_Z = 0.06; ZT = TRAY_Z + S / 2
PREFIX = '周末我想去'
PX = [-4.4 + k * STEP for k in range(5)]
OX = [PX[-1] + STEP * (j + 1) for j in range(6)]          # 接下来的正式输出位置
RY, RZ = 1.55, 0.92                                        # 草稿轨：在输出托盘后面、架高
ZR = RZ + 0.03 + S / 2
MOUTH = (-4.05, RY, ZR)                                    # 小模型的出字口
WX = [-3.1 + j * STEP for j in range(4)]                   # 草稿在轨道上等候的位置
VC = 2.75; VX = [VC - 1.5 * STEP + j * STEP for j in range(4)]   # 大模型里的 4 个位置
DRAFT = '海边吃饭'; NEW = '日落'
ACCEPT = 2                                                 # 前 2 个对上了；第 3 个（吃）是第一个对不上的
FIX = '看'

T_PUSH = [1.0 + 0.45 * j for j in range(4)]; PUSH_DUR = 0.55
T_IN = (3.4, 5.1)              # 整组滑进大模型
T_SCAN = (5.2, 6.1)            # 一次扫过 4 个位置（集中验证）
T_RES = [6.3, 6.8, 7.3, 7.65]  # 结果从左往右传：✓ ✓ ✗ （后面的不算）
T_ACC = [(8.0, 9.4), (8.3, 9.7)]
T_EJECT = (9.0, 10.8)
T_FIX = (9.8, 11.6)
T_NEW = [11.9, 12.35]
T_IN2 = (13.4, 15.6)
T_SCAN2 = (15.8, 16.6)

def build():
    global rig, prefix, drafts, news, fix, lamps, sheet_m, sheet, xm, xm_m, small_m, mouth_m, small
    new_scene(); studio_lights((-0.5, 0.8, 0.6)); desk(0.0)
    rbox((OX[4] + 0.6 - (PX[0] - 0.45), 0.95, TRAY_Z * 2), ((OX[4] + 0.6 + PX[0] - 0.45) / 2, 0, 0), bevel=0.04, mat=m_metal('#C9CDD2', 0.42))
    prefix = [Tok(ch, S, f'p{k}') for k, ch in enumerate(PREFIX)]
    # 草稿轨：一条架高的磨砂玻璃（草稿走这里，正式的字在下面的金属托盘上）
    rm = state_mat('rail', '#E6E9EA'); set_state(rm, draft=0.55)
    rbox((9.6, 0.9, 0.05), (0.05, RY, RZ), bevel=0.02, mat=rm)
    for x in (-3.6, 0.0, 4.6):
        rbox((0.08, 0.08, RZ), (x, RY + 0.3, RZ / 2), bevel=0.03, mat=m_metal('#BFC4CA', 0.38))
    # 小模型：一个小巧的金属盒子，出字口在右侧，推字时口子亮一下
    small = rbox((0.95, 0.95, 0.95), (-4.65, RY, RZ + 0.48), bevel=0.14, mat=m_metal('#B9BEC5', 0.32))
    mouth_m = state_mat('mouth', '#3A3D43')
    rbox((0.05, 0.7, 0.7), (-4.17, RY, ZR), bevel=0.03, mat=mouth_m)
    # 大模型：一段跨在草稿轨上的磨砂玻璃通道，金属框，顶上每个位置一盏灯
    vm = state_mat('ver', '#EEF0F0'); set_state(vm, draft=0.62)
    L = 4 * STEP + 0.5; H = 1.55
    rbox((L, 0.05, H), (VC, RY + 0.6, RZ + H / 2), bevel=0.02, mat=vm)            # 后墙
    rbox((L, 1.25, 0.05), (VC, RY, RZ + H), bevel=0.02, mat=vm)                    # 顶
    fm = m_metal('#BFC4CA', 0.36)
    for dx in (-L / 2, L / 2):
        for dy in (-0.62, 0.62):
            rbox((0.09, 0.09, H), (VC + dx, RY + dy, RZ + H / 2), bevel=0.03, mat=fm)
        rbox((0.09, 1.3, 0.09), (VC + dx, RY, RZ + H), bevel=0.03, mat=fm)
    rbox((L, 0.09, 0.09), (VC, RY - 0.62, RZ + H), bevel=0.03, mat=fm)
    lamps = []
    for j in range(4):
        lm = state_mat(f'lamp{j}', '#D9D4CB'); rbox((0.36, 0.2, 0.12), (VX[j], RY - 0.62, RZ + H + 0.1), bevel=0.05, mat=lm); lamps.append(lm)
    sheet_m = state_mat('sheet', '#F4F1EA'); set_state(sheet_m, draft=0.0)
    sheet = rbox((L - 0.2, 1.1, 0.008), (VC, RY, RZ), bevel=0.003, mat=sheet_m)
    drafts = [Tok(ch, S, f'd{j}') for j, ch in enumerate(DRAFT)]
    news = [Tok(ch, S, f'n{j}') for j, ch in enumerate(NEW)]
    fix = Tok(FIX, S, 'fix')
    xm = bpy.data.objects.new('xmark', None); bpy.context.collection.objects.link(xm)
    xm_m = state_mat('xm', GRAPH)
    for a in (math.pi / 4, -math.pi / 4):
        b = rbox((0.62, 0.07, 0.11), (0, 0, 0), bevel=0.04, mat=xm_m, rot=(0, a, 0)); b.parent = xm
    rig = Rig(fstop=3.5)

def tracked():
    d = {f'草稿{ch}': t.root for ch, t in zip(DRAFT, drafts)}
    d['纠正看'] = fix.root; d.update({f'新草稿{ch}': t.root for ch, t in zip(NEW, news)}); d['✕'] = xm
    return d

def chute(j, u, x_from):
    """从大模型里第 j 个位置，沿滑道落到正式输出第 j 个位置（先往前出通道，再落下）"""
    p0 = Vector((x_from, RY, ZR)); p1 = Vector((x_from, RY - 0.95, ZR + 0.35)); p2 = Vector((OX[j], 0.0, ZT + 0.7)); p3 = Vector((OX[j], 0.0, ZT))
    # 三次贝塞尔
    q = (1 - u) ** 3 * p0 + 3 * (1 - u) ** 2 * u * p1 + 3 * (1 - u) * u ** 2 * p2 + u ** 3 * p3
    return tuple(q)

def pose(t):
    for k, tk in enumerate(prefix): tk.put((PX[k], 0, ZT)); tk.look()
    # 小模型：每推一个字，口子亮一下、盒子轻轻一顿
    push_flash = sum(math.exp(-((t - (tp + 0.05)) / 0.12) ** 2) for tp in T_PUSH + T_NEW)
    set_state(mouth_m, glow=3.0 * push_flash, glow_col=AMBER_L)
    sq = 1 - 0.05 * push_flash; small.scale = (sq, 1, 1 + 0.03 * push_flash)

    gin = sstep(*T_IN, t)
    for j, tk in enumerate(drafts):
        up = sstep(T_PUSH[j], T_PUSH[j] + PUSH_DUR, t)
        if t < T_PUSH[j]: tk.put(MOUTH, scale=0.001); tk.look(alpha=0.0); continue
        x = lerp(MOUTH[0], WX[j], up); x = lerp(x, VX[j], gin)
        pos = (x, RY, ZR + (0.55 + 0.25 * j) * math.sin(math.pi * up))     # 抛一道弧线，越过前面已经排好的字
        alpha = 1.0; draft = 1.0; glow = 0.0; gcol = TEAL; scale = lerp(0.55, 1.0, sstep(T_PUSH[j], T_PUSH[j] + 0.2, t))
        res = sstep(T_RES[j], T_RES[j] + 0.25, t)
        if j < ACCEPT:
            glow = 1.3 * res; gcol = TEAL
            if t > T_ACC[j][0]:
                u = sstep(*T_ACC[j], t); pos = chute(j, u, VX[j]); draft = 1.0 - sstep(T_ACC[j][0] + 0.3, T_ACC[j][1], t)
                glow = 1.3 * (1 - u) + 0.4 * (1 - sstep(T_ACC[j][1], T_ACC[j][1] + 0.6, t))
                if u > 0.9: pos = (pos[0], pos[1], ZT + 0.12 * (1 - back_out(sstep(T_ACC[j][1] - 0.1, T_ACC[j][1] + 0.25, t))))
        else:
            # 第一个对不上的（吃）和它后面的（饭）：不进正式输出，沿草稿轨退回小模型
            if j == ACCEPT: glow = 1.6 * res; gcol = AMBER
            dim = sstep(T_RES[3], T_RES[3] + 0.3, t)
            alpha = 1.0 - 0.45 * dim * (j > ACCEPT)
            ej = sstep(T_EJECT[0] + 0.15 * (j - ACCEPT), T_EJECT[1], t)
            if ej > 0:
                pos = (lerp(VX[j], MOUTH[0] + 0.1, ej), RY, ZR + 0.25 * math.sin(math.pi * ej))
                scale *= 1 - 0.85 * sstep(0.7, 1.0, ej); alpha *= 1 - sstep(0.8, 1.0, ej)
        tk.put(pos, scale=scale); tk.look(draft=draft, glow=glow, glow_col=gcol, alpha=alpha)
    # ✕：落在「吃」上，跟着它一起退走
    xr = sstep(T_RES[ACCEPT], T_RES[ACCEPT] + 0.3, t)
    dp = drafts[ACCEPT].root.location
    xm.location = (dp[0], dp[1] - 0.36, dp[2] + 0.05); xm.rotation_euler = (math.pi / 2 * 0, 0, 0)
    xs = back_out(xr) * (1 - sstep(T_EJECT[0] + 0.6, T_EJECT[0] + 1.2, t)); xm.scale = (max(0.001, xs),) * 3
    for c in xm.children: c.hide_render = xs < 0.02
    # 大模型：草稿进来后灯亮；一道光同时扫过 4 个位置；结果从左往右逐个亮
    on = sstep(T_IN[0] + 0.8, T_IN[1], t)
    for j, lm in enumerate(lamps):
        r = sstep(T_RES[j], T_RES[j] + 0.25, t)
        if j < ACCEPT: col, g = TEAL, 1.8 * r
        elif j == ACCEPT: col, g = AMBER, 2.2 * r
        else: col, g = '#D9D4CB', 0.0
        base = 0.5 * on * (1 - r) * (1 - sstep(T_EJECT[1], T_EJECT[1] + 1.0, t))
        fade = 1 - sstep(T_FIX[1], T_FIX[1] + 1.2, t)
        set_state(lm, glow=(g + base) * fade, glow_col=col if r > 0.05 else '#FFF6E8')
    for (a, b) in (T_SCAN, T_SCAN2):
        if a <= t <= b + 0.1:
            u = sstep(a, b, t); sheet.location = (VC, RY, lerp(RZ + 0.05, RZ + 1.45, u)); sheet.hide_render = False
            set_state(sheet_m, glow=2.0 * math.sin(math.pi * u), glow_col='#EAF6F3', alpha=0.45 * math.sin(math.pi * u))
            break
    else:
        sheet.hide_render = True
    # 纠正：大模型自己给出这个位置的字「看」，从通道里升起，沿滑道补到第 3 个位置
    fu = sstep(*T_FIX, t)
    if t < T_FIX[0]: fix.put((VX[ACCEPT], RY, RZ - 0.4), scale=0.001); fix.look(alpha=0.0)
    else:
        rise = sstep(T_FIX[0], T_FIX[0] + 0.6, t)
        if t < T_FIX[0] + 0.6: fix.put((VX[ACCEPT], RY, lerp(RZ - 0.2, ZR, rise)), scale=lerp(0.5, 1.0, rise))
        else:
            u = sstep(T_FIX[0] + 0.6, T_FIX[1], t); p = chute(ACCEPT, u, VX[ACCEPT])
            if u > 0.9: p = (p[0], p[1], ZT + 0.12 * (1 - back_out(sstep(T_FIX[1] - 0.1, T_FIX[1] + 0.25, t))))
            fix.put(p)
        fix.look(draft=0.0, glow=2.0 * (1 - 0.7 * sstep(T_FIX[1], T_FIX[1] + 0.8, t)), glow_col=AMBER, alpha=min(1.0, rise * 3))
    # 继续：小模型从新的前缀接着猜（日 落），排队进大模型
    g2 = sstep(*T_IN2, t)
    for j, tk in enumerate(news):
        if t < T_NEW[j]: tk.put(MOUTH, scale=0.001); tk.look(alpha=0.0); continue
        up = sstep(T_NEW[j], T_NEW[j] + PUSH_DUR, t)
        x = lerp(MOUTH[0], WX[j], up); x = lerp(x, VX[j], g2)
        tk.put((x, RY, ZR + (0.55 + 0.25 * j) * math.sin(math.pi * up)), scale=lerp(0.55, 1.0, sstep(T_NEW[j], T_NEW[j] + 0.2, t))); tk.look(draft=1.0)

    ANCH['small'] = (-4.65, RY, RZ + 1.25); ANCH['tray'] = (PX[1], -0.2, ZT + 0.75); ANCH['drafts'] = (lerp(WX[1], VX[1], gin) + 0.37, RY, ZR + 0.75)
    ANCH['ver'] = (VC, RY - 0.6, RZ + 2.15); ANCH['fix'] = fix.root.location.copy() + Vector((0, 0, 0.62))
    ANCH['title'] = (-0.6, 0.8, 3.4)

    # 相机：开场看小模型和输出；跟着草稿往右进大模型；看验证；跟着被接受的字落到输出；最后拉远看全局
    k1 = sstep(1.0, 3.2, t); k2 = sstep(3.4, 5.4, t); k3 = sstep(7.8, 9.4, t); k4 = sstep(11.4, 14.0, t)
    tgt = mix3((-3.3, 0.7, 0.8), (-2.6, 1.0, 1.1), k1); tgt = mix3(tgt, (2.5, 1.15, 1.25), k2); tgt = mix3(tgt, (1.4, 0.65, 0.75), k3); tgt = mix3(tgt, (0.0, 0.9, 0.8), k4)
    loc = mix3((-3.4, -4.9, 3.5), (-3.0, -5.0, 3.6), k1); loc = mix3(loc, (1.9, -4.3, 3.4), k2); loc = mix3(loc, (0.4, -5.6, 4.2), k3); loc = mix3(loc, (-5.0, -4.6, 4.8), k4)
    rig.set(loc, tgt, lens=lerp(lerp(lerp(36, 38, k2), 31, k3), 33, k4))

SHOT = {'DUR': DUR, 'pose': pose, 'tracked': tracked}
build()
run(SHOT)
