# 一语道破 · Blender 测试镜头三：光在芯片里走的路有多细？（2026-11-10）
# 竖屏 18 秒，一个连续镜头对数匀速拉远：硅波导（0.5 µm）→ 红细胞 → 光栅耦合器 + 光纤 + 头发 → 硅光芯片 + 米粒 → 光模块 → 交换机。
# 做法：相机不动，整个世界围绕焦点按 10^(−L) 缩小（单位 µm，按真实尺寸建模）；物体小到看不见就隐藏。
# 默认 EEVEE。用法：
#   blender -b --python-exit-code 1 --python shot_scale.py -- <输出目录> <宽> <高> <采样> [--gpu] [--cycles] [--fps N] [--video] [帧号…]
import bpy, bmesh, math, sys, json, os, random, time
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

args = sys.argv[sys.argv.index('--') + 1:]; OUT, W, H, SAMP = args[0], int(args[1]), int(args[2]), int(args[3]); rest = args[4:]
GPU = '--gpu' in rest; CYCLES = '--cycles' in rest; VIDEO = '--video' in rest
FPS = int(rest[rest.index('--fps') + 1]) if '--fps' in rest else 30
FRAMES = [int(a) for i, a in enumerate(rest) if a.isdigit() and not (i > 0 and rest[i - 1] == '--fps')]
DUR = 18.0; NF = round(DUR * FPS); F = lambda sec: 1 + round(sec * FPS)
HERE = os.path.dirname(os.path.abspath(__file__)); FONT = os.path.join(HERE, 'assets', 'label_font.otf')
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; os.makedirs(OUT, exist_ok=True)
print('BLENDER_VERSION', bpy.app.version_string)

# ---------- 版本兼容 ----------
def fcurves_of(o):
    ad = o.animation_data
    if not ad or not ad.action: return []
    act = ad.action
    if hasattr(act, 'fcurves'): return list(act.fcurves)
    try:
        from bpy_extras import anim_utils
        cb = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
        if cb: return list(cb.fcurves)
    except Exception: pass
    out = []
    for layer in act.layers:
        for strip in layer.strips:
            for cb in strip.channelbags: out += list(cb.fcurves)
    return out
def set_interp(o, kind):
    for fc in fcurves_of(o):
        for kp in fc.keyframe_points: kp.interpolation = kind
def set_fmt(fmt):
    ims = sc.render.image_settings
    if hasattr(ims, 'media_type'): ims.media_type = 'VIDEO' if fmt == 'FFMPEG' else 'IMAGE'
    ims.file_format = fmt

# ---------- 材质 ----------
def mat(name, col, metal=0.0, rough=0.5, alpha=1.0, transm=0.0, emit=None, estr=0.0, coat=0.0, sss=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    b.inputs['Alpha'].default_value = alpha; b.inputs['Transmission Weight'].default_value = transm; b.inputs['Coat Weight'].default_value = coat
    if sss: b.inputs['Subsurface Weight'].default_value = sss
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = estr
    if alpha < 1 or transm > 0:
        if hasattr(m, 'surface_render_method'): m.surface_render_method = 'BLENDED'
    return m
def mat_light(name, col, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    for n in list(N): N.remove(n)
    o = N.new('ShaderNodeOutputMaterial'); e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*col, 1); e.inputs['Strength'].default_value = strength
    L.new(e.outputs[0], o.inputs[0]); return m
# 颜色：底色深蓝（样片先试，待用户定）；青色只给光；金色给电（电极、焊盘）
M = dict(
    box=mat('box_oxide', (0.03, 0.10, 0.30), 0.0, 0.35, coat=0.5),           # 芯片表面（埋氧层顶面）：深蓝
    si=mat('si_device', (0.30, 0.42, 0.62), 0.5, 0.3),                       # 硅器件：钢蓝
    si_dark=mat('si_die_side', (0.10, 0.12, 0.16), 0.6, 0.35),               # 芯片侧面（硅衬底）
    gold=mat('gold_pad', (0.95, 0.70, 0.28), 1.0, 0.25),                     # 电极 / 焊盘：金
    light=mat_light('light_core', (0.25, 0.95, 0.88), 9.0),                  # 光：青
    fiber_glass=mat('fiber_cladding', (0.75, 0.85, 0.95), 0.0, 0.08, alpha=0.35, coat=1.0),
    fiber_coat=mat('fiber_coating', (0.85, 0.82, 0.70), 0.0, 0.5),
    rbc=mat('red_blood_cell', (0.55, 0.05, 0.06), 0.0, 0.45, alpha=0.85, sss=0.3),
    hair=mat('hair', (0.10, 0.06, 0.04), 0.0, 0.35, coat=0.6),
    rice=mat('rice', (0.92, 0.90, 0.84), 0.0, 0.35, sss=0.5),
    pcb=mat('module_pcb', (0.03, 0.18, 0.20), 0.0, 0.5, coat=0.3),
    alu=mat('module_shell', (0.70, 0.72, 0.76), 1.0, 0.3, alpha=0.30),
    alu_solid=mat('module_shell_end', (0.66, 0.68, 0.72), 1.0, 0.35),
    pulltab=mat('pull_tab', (0.10, 0.45, 0.85), 0.0, 0.5),
    switch=mat('switch_body', (0.07, 0.08, 0.10), 0.6, 0.4),
    switch_top=mat('switch_cover', (0.10, 0.11, 0.13), 0.6, 0.4, alpha=0.15),
    cage=mat('port_cage', (0.55, 0.57, 0.60), 1.0, 0.35),
    label=mat_light('label_white', (1.0, 1.0, 1.0), 2.2),
)

# ---------- 几何工具（单位 µm） ----------
WORLD = bpy.data.objects.new('WORLD', None); sc.collection.objects.link(WORLD)
def link(o, parent=WORLD): sc.collection.objects.link(o); o.parent = parent; return o
def box(name, cx, cy, cz, sx, sy, sz, m, parent=WORLD, bevel=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = (cx, cy, cz); o.scale = (sx, sy, sz); o.data.materials.append(m); link(o, parent)
    if bevel: md = o.modifiers.new('bev', 'BEVEL'); md.width = bevel; md.segments = 2
    return o
def cyl(name, r, depth, m, loc, rot=(0, 0, 0), verts=48, parent=WORLD):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=depth); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; o.rotation_euler = rot; o.data.materials.append(m); return link(o, parent)
def torus(name, R, r, m, loc, parent=WORLD):
    bm = bmesh.new(); me = bpy.data.meshes.new(name)
    seg, ring = 96, 12
    verts = [[bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b))) for b in [2 * math.pi * j / ring for j in range(ring)]] for a in [2 * math.pi * i / seg for i in range(seg)]]
    for i in range(seg):
        for j in range(ring): bm.faces.new([verts[i][j], verts[(i + 1) % seg][j], verts[(i + 1) % seg][(j + 1) % ring], verts[i][(j + 1) % ring]])
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); o.location = loc; o.data.materials.append(m); return link(o, parent)
def ellipsoid(name, rx, ry, rz, m, loc, rot=(0, 0, 0), parent=WORLD):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=1.0); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; o.scale = (rx, ry, rz); o.rotation_euler = rot; o.data.materials.append(m); return link(o, parent)
def show_between(objs, t_on, t_off=None):
    """在 [t_on, t_off) 秒之间可见（渲染）"""
    for o in objs if isinstance(objs, (list, tuple)) else [objs]:
        o.hide_render = True; o.keyframe_insert('hide_render', frame=1)
        o.hide_render = False; o.keyframe_insert('hide_render', frame=max(1, F(t_on)))
        if t_off is not None: o.hide_render = True; o.keyframe_insert('hide_render', frame=F(t_off))
        set_interp(o, 'CONSTANT')

# ---------- 第 0 级：硅波导（0.5 × 0.22 µm）+ 稀疏的硅光版图 ----------
WG_W, WG_H = 0.5, 0.22
DIE = 5000.0                                     # 示例芯片 5 mm
GC_Y = -40.0                                     # 光栅耦合器位置（波导往 -y 走到这里）
die_top = box('die_top_surface', 0, 0, -0.01, DIE, DIE, 0.02, M['box'])                       # 埋氧层顶面
die_body = box('die_body', 0, 0, -375.0, DIE, DIE, 750.0, M['si_dark'])                         # 芯片本体（示意厚 0.75 mm）
wg = box('main_waveguide', 0, (GC_Y + 600) / 2 + 15, WG_H / 2, WG_W, 600 - GC_Y - 30, WG_H, M['si'])   # 主波导：从 y=+600 到耦合器前
# 光脉冲：在芯区里沿 -y 跑（光从芯片里出去，经耦合器进光纤）；画成芯区内一段亮带，不外溢
pulses = []
for k in range(14):
    p = box(f'light_pulse_{k}', 0, 0, WG_H / 2, WG_W * 0.62, 1.6, WG_H * 0.6, M['light']); pulses.append(p)
    y0 = 14 - 3.2 * k
    for fr in (1, NF):
        t = (fr - 1) / FPS; p.location.y = y0 - 4.0 * t; p.keyframe_insert('location', index=1, frame=fr)   # 慢放：画面里每秒 4 µm
    set_interp(p, 'LINEAR')
# 光栅耦合器：从 0.5 µm 线性展宽到 12 µm 的锥形 + 一排刻线（周期约 0.6 µm）
taper = bpy.data.meshes.new('gc_taper'); bm = bmesh.new()
pts = [(-WG_W / 2, GC_Y + 30), (WG_W / 2, GC_Y + 30), (6, GC_Y), (-6, GC_Y)]
vb = [bm.verts.new((x, y, 0)) for x, y in pts]; vt = [bm.verts.new((x, y, WG_H)) for x, y in pts]
bm.faces.new(vb[::-1]); bm.faces.new(vt)
for i in range(4): bm.faces.new([vb[i], vb[(i + 1) % 4], vt[(i + 1) % 4], vt[i]])
bm.to_mesh(taper); bm.free(); gco = bpy.data.objects.new('gc_taper', taper); gco.data.materials.append(M['si']); link(gco)
for k in range(22): box(f'gc_line_{k}', 0, GC_Y - 0.3 - 0.62 * k, WG_H / 2, 12.0, 0.31, WG_H, M['si'])
# 稀疏版图：分支波导、微环、调制器电极、焊盘（确定性随机）
rnd = random.Random(20261110); layout = []
for k in range(5):                                # 主波导附近几条平行 / 弯曲的波导
    x = rnd.choice([-1, 1]) * rnd.uniform(18, 60); layout.append(box(f'wg_side_{k}', x, rnd.uniform(-100, 300), WG_H / 2, WG_W, rnd.uniform(150, 500), WG_H, M['si']))
ring = torus('micro_ring', 10.0, 0.25, M['si'], (-12.0, 120.0, WG_H / 2)); ring.scale.z = WG_H / 0.5; layout.append(ring)
for k in range(260):                              # 整颗芯片上散布的器件（中等尺度才看得见）
    x, y = rnd.uniform(-DIE / 2 + 80, DIE / 2 - 80), rnd.uniform(-DIE / 2 + 80, DIE / 2 - 80)
    if abs(x) < 120 and -150 < y < 700: continue
    kind = rnd.random()
    if kind < 0.45: layout.append(box(f'wg_far_{k}', x, y, WG_H / 2, WG_W, rnd.uniform(200, 900), WG_H, M['si']))
    elif kind < 0.6: layout.append(box(f'wg_far_h_{k}', x, y, WG_H / 2, rnd.uniform(200, 900), WG_W, WG_H, M['si']))
    elif kind < 0.75: r_ = torus(f'ring_far_{k}', rnd.uniform(5, 20), 0.25, M['si'], (x, y, WG_H / 2)); r_.scale.z = WG_H / 0.5; layout.append(r_)
    elif kind < 0.9: layout.append(box(f'mzm_electrode_{k}', x, y, 1.0, 30, rnd.uniform(800, 1800), 2.0, M['gold']))   # 调制器电极（金）
    else: layout.append(box(f'pad_{k}', x, y, 1.5, 80, 80, 3.0, M['gold']))
for k in range(36):                               # 芯片边缘一排焊盘
    layout.append(box(f'edge_pad_{k}', -DIE / 2 + 150 + k * 130, DIE / 2 - 150, 1.5, 90, 90, 3.0, M['gold']))

# ---------- 第 1 级：红细胞（直径 7.5 µm，双凹圆盘，示意） ----------
rbc = torus('red_blood_cell', 2.6, 1.15, M['rbc'], (6.5, 6.0, 1.15)); rbc.scale = (1.0, 1.0, 0.8)
rbc_mid = ellipsoid('rbc_center', 1.7, 1.7, 0.45, M['rbc'], (6.5, 6.0, 1.0))

# ---------- 第 2 级：光纤（包层 125 µm、纤芯 8.2 µm）斜对光栅耦合器 + 一根头发 ----------
TILT = math.radians(9)                            # 光纤和法线约成 9°（待核）
FIB_L = 6000.0
fdir = Vector((0, -math.sin(TILT), math.cos(TILT)))       # 光纤轴：往 +z、略向 -y 倾斜
fbase = Vector((0, GC_Y - 7, 6.0))                        # 光纤端面中心，略高于耦合器
fc = fbase + fdir * (FIB_L / 2); rot = (TILT, 0, 0)
fiber = cyl('fiber_cladding', 62.5, FIB_L, M['fiber_glass'], fc, rot)
fiber_core = cyl('fiber_core_light', 4.1, FIB_L, M['light'], fc, rot, verts=24)            # 纤芯里有光（青）
fiber_coat = cyl('fiber_coating', 121.0, FIB_L - 900, M['fiber_coat'], fbase + fdir * (900 + (FIB_L - 900) / 2), rot)   # 涂覆层从 0.9 mm 外开始
hair = cyl('human_hair', 40.0, 4200.0, M['hair'], (-160.0, 220.0, 40.0), (0, math.radians(90), math.radians(28)), verts=32)

# ---------- 第 3 级：整颗芯片放在模块电路板上，旁边一粒米 ----------
PCB_T = 1000.0
MOD_W, MOD_L, MOD_H = 18350.0, 89000.0, 8500.0          # QSFP-DD：宽 18.35 mm、长约 89 mm（不含拉环）、高 8.5 mm
MOD_CY = -30000.0                                        # 模块中心（芯片在模块后部）
pcb = box('module_pcb', 0, MOD_CY, -750 - PCB_T / 2, MOD_W - 1200, MOD_L - 4000, PCB_T, M['pcb'])
rice = ellipsoid('rice_grain', 1400, 3300, 1000, M['rice'], (4300, 600, -750 + 1000 - 650), (0, 0, math.radians(18)))

# ---------- 第 4 级：光模块外壳（半透明，看得见里面） ----------
shell = box('module_shell', 0, MOD_CY, -750 - PCB_T - 1200 + MOD_H / 2, MOD_W, MOD_L, MOD_H, M['alu'])
shell_front = box('module_front', 0, MOD_CY - MOD_L / 2 + 1500, -750 - PCB_T - 1200 + MOD_H / 2, MOD_W, 3000, MOD_H, M['alu_solid'])
pull = box('pull_tab', 0, MOD_CY - MOD_L / 2 - 9000, -750 - PCB_T - 1200 + 2500, 9000, 18000, 1200, M['pulltab'])

# ---------- 第 5 级：交换机（1U，前面板一排 32 个端口，上盖半透明） ----------
SW_W, SW_D, SW_H = 440000.0, 400000.0, 44450.0
FACE_Y = MOD_CY - MOD_L / 2 + 6000                       # 前面板位置（模块前端伸出面板）
SW_Z = -750 - PCB_T - 1200 + MOD_H / 2 - 9000            # 让模块在上排端口
sw_parts = [box('switch_body_bottom', -SW_W / 2 + 30000, FACE_Y + SW_D / 2, SW_Z - SW_H / 2 + 1500, SW_W, SW_D, 3000, M['switch']),
            box('switch_top_cover', -SW_W / 2 + 30000, FACE_Y + SW_D / 2, SW_Z + SW_H / 2 - 600, SW_W, SW_D, 1200, M['switch_top']),
            box('switch_face', -SW_W / 2 + 30000, FACE_Y, SW_Z, SW_W, 2500, SW_H, M['switch'])]
others = []
for row in range(2):
    for col in range(16):
        x = -col * 24000.0 - (12000.0 if row else 0) + 0.0; z = SW_Z + (9000 if row == 0 else -9000)
        if row == 0 and col == 0: continue                                  # 我们那个模块的位置
        cage = box(f'cage_{row}_{col}', x, FACE_Y - 1500, z, 21000, 1200, 11000, M['cage']); sw_parts.append(cage)
        m_ = box(f'other_module_{row}_{col}', x, FACE_Y - 6000, z, MOD_W, 12000, MOD_H, M['alu_solid']); others.append(m_)
        others.append(box(f'other_tab_{row}_{col}', x, FACE_Y - 16000, z - 2500, 9000, 18000, 1200, M['pulltab']))

# ---------- 3D 标签：白色立体字 + 双箭头 ----------
FNT = bpy.data.fonts.load(FONT)
def label(name, text, size, loc, arrow=None):
    """size：字高（µm）；arrow：箭头总长（µm），横跨在字下方"""
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = text; cu.font = FNT; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = size * 0.06
    o = bpy.data.objects.new(name, cu); o.data.materials.append(M['label']); link(o); o.location = loc
    parts = [o]
    if arrow:
        sh = box(name + '_shaft', loc[0], loc[1], loc[2] - size * 0.45, arrow * 0.86, size * 0.06, size * 0.06, M['label']); parts.append(sh)
        for sgn in (-1, 1):
            bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=size * 0.16, radius2=0, depth=arrow * 0.07); me = bpy.data.meshes.new(name + '_tip'); bm.to_mesh(me); bm.free()
            tip = bpy.data.objects.new(name + f'_tip{sgn}', me); tip.data.materials.append(M['label']); link(tip)
            tip.location = (loc[0] + sgn * arrow * 0.465, loc[1], loc[2] - size * 0.45); tip.rotation_euler = (0, sgn * math.radians(90), 0); parts.append(tip)
    return parts
LB = {
    'wg': label('lbl_wg', '0.5 µm', 0.32, (0.0, 1.6, 0.9), arrow=WG_W),
    'rbc': label('lbl_rbc', '红细胞 约 7.5 µm', 1.6, (6.5, 6.0, 5.2), arrow=7.5),
    'fiber': label('lbl_fiber', '光纤 125 µm', 26.0, (0.0, GC_Y - 60, 230.0), arrow=125.0),
    'hair': label('lbl_hair', '头发 约 0.1 mm', 30.0, (-160.0, 380.0, 160.0)),
    'die': label('lbl_die', '硅光芯片 约 5 mm（示例）', 520.0, (0.0, -200.0, 1400.0), arrow=DIE),
    'mod': label('lbl_mod', '光模块 约 9 cm', 4200.0, (0.0, MOD_CY, 16000.0), arrow=None),
}
# 标签面向相机（约束放在 Track To 上，世界缩放不影响朝向）

# ---------- 尺度时间线：画面宽度（µm）的 log10 对时间分段线性 ----------
KEYS = [(0.0, 3.0), (2.0, 4.0), (4.5, 30.0), (7.5, 300.0), (9.0, 3000.0), (11.5, 30000.0), (14.5, 200000.0), (18.0, 600000.0)]
CENTER = [(0.0, (0, 0, 0.11)), (4.5, (2.0, 2.0, 0.5)), (7.5, (0, -20, 10)), (11.5, (0, -2000, -500)), (14.5, (0, MOD_CY + 8000, -3000)), (18.0, (-60000, FACE_Y + 20000, SW_Z))]
def log_width(t):
    for (t0, w0), (t1, w1) in zip(KEYS, KEYS[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            if t1 == KEYS[-1][0]: u = 1 - (1 - u) ** 2.2                       # 最后一段减速落地
            elif t0 == 0.0: u = u ** 1.6                                         # 起步慢一点
            return math.log10(w0) + u * (math.log10(w1) - math.log10(w0))
    return math.log10(KEYS[-1][1])
def center(t):
    pts = CENTER
    for (t0, c0), (t1, c1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0); u = u * u * (3 - 2 * u)
            # 在对数尺度上插值偏移量太复杂；这里线性插值位置，镜头中心随尺度移动
            return Vector(c0).lerp(Vector(c1), u)
    return Vector(pts[-1][1])
VIEW0 = 3.0                                       # 初始画面宽度（µm），对应世界缩放 1
for f in range(1, NF + 1):
    t = (f - 1) / FPS; s = VIEW0 / (10 ** log_width(t)); c = center(t)
    WORLD.scale = (s, s, s); WORLD.location = -c * s
    WORLD.keyframe_insert('scale', frame=f); WORLD.keyframe_insert('location', frame=f)
set_interp(WORLD, 'LINEAR')
def t_at_width(w):                                # 画面宽度达到 w µm 的时刻
    lw = math.log10(w)
    for f in range(1, NF + 1):
        if log_width((f - 1) / FPS) >= lw: return (f - 1) / FPS
    return DUR
# 物体按尺度出现 / 消失：画面宽度超过物体尺寸约 400 倍就隐藏（小于约 3 像素）；大物体在镜头会钻进去之前隐藏
def hide_when_small(objs, size):
    t_off = t_at_width(size * 400)
    for o in objs: show_between(o, 0.0, t_off if t_off < DUR else None)
hide_when_small([wg, gco] + pulses + layout[:6], 0.5)
hide_when_small([o for o in sc.objects if o.name.startswith('gc_line_')], 0.6)
hide_when_small([rbc, rbc_mid], 7.5)
hide_when_small([fiber, fiber_core, fiber_coat], 125)
hide_when_small(layout[6:], 25)
show_between([shell, shell_front, pull], 9.6)
show_between(sw_parts + others, 12.8)
# 标签：进场时间、退场时间（秒）
for key, (t_on, t_off) in dict(wg=(0.2, 3.2), rbc=(2.4, 5.6), fiber=(5.0, 8.4), hair=(5.6, 8.4), die=(9.4, 12.6), mod=(12.0, 16.5)).items():
    show_between([o for o in LB[key] if o], t_on, t_off)

# ---------- 相机（固定，绕焦点慢慢转）、灯光（跟相机走，不随世界缩放） ----------
rig = bpy.data.objects.new('cam_rig', None); sc.collection.objects.link(rig)
bpy.ops.object.camera_add(); cam = bpy.context.object; cam.parent = rig; sc.camera = cam
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.lens = 35
hfov = 2 * math.atan((24 * W / H) / 2 / 35); DIST = (VIEW0 / 2) / math.tan(hfov / 2)
EL = math.radians(36)
cam.location = (0, -DIST * math.cos(EL), DIST * math.sin(EL)); cam.rotation_euler = (math.radians(90) - EL, 0, 0)
cam.data.clip_start = DIST * 0.02; cam.data.clip_end = DIST * 400
cam.data.dof.use_dof = True; cam.data.dof.focus_distance = DIST
for fr, fs in ((1, 1.2), (F(9.0), 1.8), (F(14.0), 4.0), (NF, 8.0)):
    cam.data.dof.aperture_fstop = fs; cam.data.dof.keyframe_insert('aperture_fstop', frame=fr)
rig.rotation_euler = (0, 0, math.radians(-25)); rig.keyframe_insert('rotation_euler', index=2, frame=1)
rig.rotation_euler = (0, 0, math.radians(20)); rig.keyframe_insert('rotation_euler', index=2, frame=NF)
for o in [o for v in LB.values() for o in v if o and o.type == 'FONT']:
    tc = o.constraints.new('TRACK_TO'); tc.target = cam; tc.track_axis = 'TRACK_Z'; tc.up_axis = 'UP_Y'
def area(name, loc, energy, size, col):
    L = bpy.data.lights.new(name, 'AREA'); L.energy = energy; L.size = size; L.color = col; o = bpy.data.objects.new(name, L); sc.collection.objects.link(o)
    o.parent = rig; o.location = loc; tc = o.constraints.new('TRACK_TO'); tc.target = rig; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'; return o
# 灯光单位随相机距离走：能量 ∝ 距离²
k2 = DIST ** 2
area('key', (-DIST * 1.2, -DIST * 0.8, DIST * 1.6), 180 * k2, DIST * 1.2, (1.0, 0.95, 0.88))
area('rim', (DIST * 1.4, DIST * 1.2, DIST * 0.6), 120 * k2, DIST * 1.0, (0.55, 0.75, 1.0))
area('fill', (0, -DIST * 1.6, DIST * 0.3), 40 * k2, DIST * 2.0, (0.7, 0.8, 1.0))
wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True
bg = wd.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.010, 0.030, 0.085, 1); bg.inputs['Strength'].default_value = 1.0

# ---------- 渲染设置 ----------
if CYCLES:
    sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMP; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 4
    if GPU:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for dt in ('OPTIX', 'CUDA'):
            try:
                prefs.compute_device_type = dt; prefs.refresh_devices()
                if [d for d in prefs.devices if d.type == dt]:
                    for d in prefs.devices: d.use = d.type == dt
                    sc.cycles.device = 'GPU'; print('GPU_DEVICE', dt); break
            except Exception: pass
else:
    ENG = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    sc.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in ENG else 'BLENDER_EEVEE_NEXT'
    for k, v in (('taa_render_samples', SAMP), ('use_raytracing', True), ('use_shadows', True), ('use_fast_gi', True)):
        try: setattr(sc.eevee, k, v)
        except Exception as e: print('EEVEE 设置跳过', k, e)
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, NF
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.35
sc.view_settings.view_transform = 'AgX'
for lk in ('AgX - Medium High Contrast', 'Medium High Contrast'):
    try: sc.view_settings.look = lk; break
    except Exception: pass
set_fmt('PNG')

# ---------- 每帧锚点（给 2D 合成） ----------
ANCH = {'wg': wg, 'rbc': rbc, 'fiber_end': None, 'die': die_top, 'module': shell}
anchors = {}
for f in range(1, NF + 1):
    sc.frame_set(f); fr = {}
    for k, o in ANCH.items():
        p = (WORLD.matrix_world @ fbase) if o is None else o.matrix_world.translation
        v = world_to_camera_view(sc, cam, p); fr[k] = [round(v.x * W, 1), round((1 - v.y) * H, 1)]
    fr['view_um'] = round(10 ** log_width((f - 1) / FPS), 2); anchors[f] = fr
json.dump({'fps': FPS, 'nf': NF, 'w': W, 'frames': anchors}, open(os.path.join(OUT, 'anchors.json'), 'w'))
if VIDEO and not FRAMES:
    set_fmt('FFMPEG'); sc.render.ffmpeg.format = 'MPEG4'; sc.render.ffmpeg.codec = 'H264'
    for k, v in (('constant_rate_factor', 'PERC_LOSSLESS'), ('ffmpeg_preset', 'GOOD')):
        try: setattr(sc.render.ffmpeg, k, v)
        except Exception as e: print('ffmpeg 设置跳过', k, e)
    sc.render.filepath = os.path.join(OUT, 'scale.mp4'); bpy.ops.render.render(animation=True)
else:
    for f in (FRAMES or range(1, NF + 1)):
        sc.frame_set(f); sc.render.filepath = os.path.join(OUT, f'f{f:04d}.png'); t0 = time.time(); bpy.ops.render.render(write_still=True)
        print(f'FRAME_TIME 第 {f} 帧：{time.time() - t0:.1f} 秒')
print('DONE', OUT)
