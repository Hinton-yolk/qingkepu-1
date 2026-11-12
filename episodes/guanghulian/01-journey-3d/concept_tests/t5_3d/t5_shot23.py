# T5 第 2、3 拍（3D）：「电把消息写到光上」+「窄门」，脚本内 0–12 s（片中 6.5–18.5 s），30 fps，360 帧。
# 正常的相机运动（不再缩放世界）。单位 u：示意尺度（波导宽 0.6 u，光纤纤芯 3 u），画面加注「结构为示意」。
# 坐标：光沿 +Y 走；z 向上；芯片表面 z=0，上包层玻璃面 z=1。
#   激光器端面 y=-14 → 调制器金电极 y=-1..11 → 出射光带 → 芯片边缘 y=40（模斑转换器）→ 光纤端面 y=40.4 → 纤芯一路到 y≈350 的连接器
# 「消息」：沿路径流动的亮暗段，PATTERN=[1,1,0,1,0,0,1,0] 八位循环；亮位强、暗位 20%；金（电）/ 青（光）。
#   同一个相位函数 m(ℓ − v·t)：金色在焊线/电极上的 ℓ 沿路径累计，到电极出口 ℓ=11 与出射光带的 y 一致，所以出口处金色的那一位和光的那一位同步。
# 用法：
#   blender -b --python-exit-code 1 --python t5_shot23.py -- <输出目录> --res 540x960 --samples N [--gpu] [--times 0.5,2,…] [--frames a-b]
import bpy, bmesh, math, sys, json, os, time
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index('--') + 1:]
OUT = argv[0]
def opt(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default
W, H = [int(v) for v in opt('--res', '540x960').split('x')]
SAMP = int(opt('--samples', '64')); GPU = '--gpu' in argv
TIMES = [float(v) for v in opt('--times').split(',')] if opt('--times') else None
FR = opt('--frames'); FRANGE = tuple(int(v) for v in FR.split('-')) if FR else None
THREADS = int(opt('--threads', '2'))
FPS = 30; DUR = 12.0; NF = round(DUR * FPS); F = lambda sec: 1 + round(sec * FPS)
HERE = os.path.dirname(os.path.abspath(__file__))
LAYOUT = os.path.join(HERE, 'assets', 't5_layout.png')
ASSETS = os.path.normpath(os.path.join(HERE, '..', '..', 'blender', 'assets_dl'))
HDRI = os.path.join(ASSETS, 'studio_small_09_2k.hdr'); ROUGH = os.path.join(ASSETS, 'metal_plate_rough_2k.jpg')
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; os.makedirs(OUT, exist_ok=True)

PATTERN = [1, 1, 0, 1, 0, 0, 1, 0]
VSPEED = 9.0            # 消息流速 u/s
BITLEN = 2.5            # 一位（含暗隙）长度 u  → 约 3.6 位/秒
Y_EXIT = 11.0           # 电极出口：此后光带带消息
GOLD = (0.887, 0.468, 0.051); CYAN = (0.05, 0.79, 0.87)
Y_EDGE = 40.0; Y_FACE = 40.4

# ---------- 版本兼容 ----------
def fcurves_of(idb):
    ad = idb.animation_data
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
def set_interp(idb, kind):
    for fc in fcurves_of(idb):
        for kp in fc.keyframe_points: kp.interpolation = kind
def set_fmt(fmt):
    ims = sc.render.image_settings
    if hasattr(ims, 'media_type'): ims.media_type = 'IMAGE'
    ims.file_format = fmt

# ---------- 材质 ----------
VALUE_NODES = []            # (node_tree, node, 名字)：每帧写关键帧
def value_node(m, name, init=0.0):
    n = m.node_tree.nodes.new('ShaderNodeValue'); n.name = name; n.outputs[0].default_value = init; VALUE_NODES.append((m, n, name)); return n
def mat(name, col, metal=0.0, rough=0.5, alpha=1.0, coat=0.0, rough_tex=None, rough_scale=1.0, bump=0.0, ior=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat; b.inputs['Alpha'].default_value = alpha
    if rough_tex and os.path.exists(rough_tex):
        tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (rough_scale,) * 3
        L.new(tc.outputs['Object'], mp.inputs['Vector'])
        it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(rough_tex, check_existing=True); it.image.colorspace_settings.name = 'Non-Color'; it.projection = 'BOX'
        L.new(mp.outputs[0], it.inputs[0]); mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = max(0.02, rough - 0.12); mr.inputs['To Max'].default_value = min(1.0, rough + 0.15)
        L.new(it.outputs['Color'], mr.inputs['Value']); L.new(mr.outputs[0], b.inputs['Roughness'])
    if bump:
        nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 40.0; bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump
        L.new(nz.outputs['Fac'], bp.inputs['Height']); L.new(bp.outputs[0], b.inputs['Normal'])
    return m

# 消息图样：8x1 贴图（最近邻、重复）
pat_img = bpy.data.images.new('pattern8', 8, 1, alpha=False)
px = []
for v in PATTERN: px += [v, v, v, 1.0]
pat_img.pixels = px; pat_img.colorspace_settings.name = 'Non-Color'; pat_img.pack()
def pattern_nodes(m, ell_socket):
    """返回 (level, 本地 T 节点)：level = 位间暗隙 × (0.2 + 0.8×位值)，随 T 向 +ℓ 流动"""
    N = m.node_tree.nodes; L = m.node_tree.links
    T = value_node(m, 'T', 0.0)
    def math_(op, a, b=None, val=None):
        n = N.new('ShaderNodeMath'); n.operation = op
        for i, x in enumerate((a, b)):
            if x is None: continue
            if isinstance(x, (int, float)): n.inputs[i].default_value = x
            else: L.new(x, n.inputs[i])
        return n.outputs[0]
    s = math_('DIVIDE', math_('SUBTRACT', ell_socket, math_('MULTIPLY', T.outputs[0], VSPEED)), BITLEN)
    f = math_('SUBTRACT', s, math_('FLOOR', s))
    u = N.new('ShaderNodeCombineXYZ'); u.inputs['Y'].default_value = 0.5
    fl = math_('FLOOR', s); L.new(math_('DIVIDE', math_('ADD', fl, 0.5), 8.0), u.inputs['X'])
    it = N.new('ShaderNodeTexImage'); it.image = pat_img; it.interpolation = 'Closest'; it.extension = 'REPEAT'; L.new(u.outputs[0], it.inputs[0])
    bitv = it.outputs['Color']
    sp = N.new('ShaderNodeSeparateColor'); L.new(bitv, sp.inputs[0]); bit = sp.outputs['Red']
    lvl = math_('ADD', 0.2, math_('MULTIPLY', bit, 0.8))
    # 暗隙：f 在 [0,0.12] 为暗（柔边 0.05）
    g1 = N.new('ShaderNodeMapRange'); g1.inputs['From Min'].default_value = 0.07; g1.inputs['From Max'].default_value = 0.13; L.new(f, g1.inputs['Value'])
    return math_('MULTIPLY', lvl, g1.outputs[0]), T
def ell_node(m, P0, d, l0):
    """路径坐标 ℓ = ℓ0 + dot(世界位置 − P0, 方向)"""
    N = m.node_tree.nodes; L = m.node_tree.links
    g = N.new('ShaderNodeNewGeometry'); sub = N.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = P0; L.new(g.outputs['Position'], sub.inputs[0])
    dt = N.new('ShaderNodeVectorMath'); dt.operation = 'DOT_PRODUCT'; dt.inputs[1].default_value = d; L.new(sub.outputs[0], dt.inputs[0])
    ad = N.new('ShaderNodeMath'); ad.operation = 'ADD'; ad.inputs[1].default_value = l0; L.new(dt.outputs['Value'], ad.inputs[0]); return ad.outputs[0]
def mat_gold(name, P0, d, l0, emis=2.2):
    """金（电）：金属底 + 自发光的消息；暗位 ≈ 亮位 20%，隙里不发光"""
    m = mat(name, GOLD, 1.0, 0.22, rough_tex=ROUGH, rough_scale=0.08)
    b = m.node_tree.nodes['Principled BSDF']; L = m.node_tree.links
    lvl, T = pattern_nodes(m, ell_node(m, P0, d, l0))
    b.inputs['Emission Color'].default_value = (*GOLD, 1)
    mul = m.node_tree.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = emis; L.new(lvl, mul.inputs[0]); L.new(mul.outputs[0], b.inputs['Emission Strength'])
    return m
def mat_light(name, mode, emis=5.0, y_ell=None):
    """光（青）：mode 'steady' 满亮；'msg' 全程带消息（y>Y_EXIT 才有图样，之前满亮）；'core' 同 msg × 耦合系数 cpl"""
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    for n in list(N): N.remove(n)
    o = N.new('ShaderNodeOutputMaterial'); e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*CYAN, 1)
    ao = N.new('ShaderNodeOutputAOV'); ao.aov_name = 'lightmask'; ao.inputs['Value'].default_value = 1.0
    L.new(e.outputs[0], o.inputs[0])
    if mode == 'steady':
        e.inputs['Strength'].default_value = emis; return m
    g = N.new('ShaderNodeNewGeometry'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(g.outputs['Position'], sep.inputs[0])
    lvl, T = pattern_nodes(m, sep.outputs['Y'])
    gt = N.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; L.new(sep.outputs['Y'], gt.inputs[0]); gt.inputs[1].default_value = Y_EXIT
    mx = N.new('ShaderNodeMix'); mx.data_type = 'FLOAT'; L.new(gt.outputs[0], mx.inputs[0]); mx.inputs[2].default_value = 1.0; L.new(lvl, mx.inputs[3])
    res = mx.outputs[0]
    if mode == 'core':
        cp = value_node(m, 'cpl', 1.0); mc = N.new('ShaderNodeMath'); mc.operation = 'MULTIPLY'; L.new(res, mc.inputs[0]); L.new(cp.outputs[0], mc.inputs[1]); res = mc.outputs[0]
    st = N.new('ShaderNodeMath'); st.operation = 'MULTIPLY'; st.inputs[1].default_value = emis; L.new(res, st.inputs[0]); L.new(st.outputs[0], e.inputs['Strength'])
    return m
def mat_leak():
    """偏移时包层里漏出的淡光：体积发光，沿轴向外变淡、径向变淡（受约束的雾，不是球）"""
    m = bpy.data.materials.new('leak_haze'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    for n in list(N): N.remove(n)
    o = N.new('ShaderNodeOutputMaterial'); e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*CYAN, 1); L.new(e.outputs[0], o.inputs['Volume'])
    ao = N.new('ShaderNodeOutputAOV'); ao.aov_name = 'lightmask'; ao.inputs['Value'].default_value = 1.0
    g = N.new('ShaderNodeNewGeometry'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(g.outputs['Position'], sep.inputs[0])
    def mn(op, a, b):
        n = N.new('ShaderNodeMath'); n.operation = op
        for i, x in enumerate((a, b)):
            if isinstance(x, (int, float)): n.inputs[i].default_value = x
            else: L.new(x, n.inputs[i])
        return n.outputs[0]
    t = mn('DIVIDE', mn('SUBTRACT', sep.outputs['Y'], Y_FACE), 9.0)
    ax = mn('POWER', mn('MAXIMUM', mn('SUBTRACT', 1.0, t), 0.0), 2.0)
    r = mn('POWER', mn('ADD', mn('POWER', sep.outputs['X'], 2.0), mn('POWER', mn('SUBTRACT', sep.outputs['Z'], 0.5), 2.0)), 0.5)
    R_ = mn('ADD', 1.4, mn('MULTIPLY', mn('SUBTRACT', sep.outputs['Y'], Y_FACE), 0.28))
    rad = mn('POWER', mn('MAXIMUM', mn('SUBTRACT', 1.0, mn('DIVIDE', r, R_)), 0.0), 2.0)
    lk = value_node(m, 'leak', 0.0)
    st = mn('MULTIPLY', mn('MULTIPLY', ax, rad), mn('MULTIPLY', lk.outputs[0], 0.9)); L.new(st, e.inputs['Strength'])
    return m

# 芯片表面
def mat_chip():
    m = bpy.data.materials.new('chip_surface'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); L.new(tc.outputs['Object'], mp.inputs['Vector'])
    mp.inputs['Scale'].default_value = (1 / 100.0, 1 / 100.0, 1); mp.inputs['Location'].default_value = (0.5, 0.5, 0)   # x∈[-50,50]→0..1；y 在平面里另行偏移
    it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(LAYOUT, check_existing=True); it.image.colorspace_settings.name = 'Non-Color'; it.interpolation = 'Cubic'; it.extension = 'EXTEND'
    L.new(mp.outputs[0], it.inputs[0]); sp = N.new('ShaderNodeSeparateColor'); L.new(it.outputs['Color'], sp.inputs[0])
    def mix(fac, a, bcol):
        mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L.new(fac, mx.inputs['Factor'])
        if isinstance(a, tuple): mx.inputs['A'].default_value = (*a, 1)
        else: L.new(a, mx.inputs['A'])
        mx.inputs['B'].default_value = (*bcol, 1); return mx.outputs['Result']
    c1 = mix(sp.outputs['Red'], (0.02, 0.07, 0.30), (0.20, 0.30, 0.52)); c2 = mix(sp.outputs['Green'], c1, GOLD)
    L.new(c2, b.inputs['Base Color']); L.new(sp.outputs['Green'], b.inputs['Metallic'])
    b.inputs['Roughness'].default_value = 0.3; b.inputs['Coat Weight'].default_value = 0.4
    return m

M = dict(
    chip=mat_chip(),
    clad=mat('upper_cladding_glass', (0.7, 0.8, 1.0), 0.0, 0.08, alpha=0.07, coat=0.5),
    si_wg=mat('si_waveguide', (0.35, 0.45, 0.65), 0.0, 0.1, alpha=0.35),
    die_side=mat('die_side', (0.09, 0.10, 0.14), 0.7, 0.35, bump=0.1),
    steady=mat_light('light_steady', 'steady'),
    msg=mat_light('light_msg', 'msg'),
    core=mat_light('light_core', 'core', emis=5.0),
    tail=mat_light('tail', 'steady', emis=0.5),
    leak=mat_leak(),
    glass=mat('fiber_glass', (0.75, 0.85, 0.95), 0.0, 0.05, alpha=0.14, coat=0.6),
    vgroove=mat('v_groove', (0.16, 0.17, 0.21), 0.5, 0.3, bump=0.05),
    ssc=mat('ssc', (0.5, 0.6, 0.8), 0.0, 0.2, alpha=0.35),
    pcb=mat('pcb_mask', (0.03, 0.16, 0.06), 0.0, 0.35, coat=0.5, bump=0.05),
    ic=mat('ic', (0.05, 0.05, 0.06), 0.2, 0.4, bump=0.05),
    laser=mat('laser', (0.34, 0.35, 0.38), 0.8, 0.28),
    shell=mat('shell', (0.7, 0.73, 0.78), 1.0, 0.25, alpha=0.10),
    ribbon=mat('ribbon', (0.5, 0.52, 0.55), 0.0, 0.5, alpha=0.5),
    mpo=mat('mpo', (0.14, 0.15, 0.17), 0.4, 0.4, bump=0.05),
    finger=mat('finger', GOLD, 1.0, 0.25),
)

# ---------- 几何 ----------
def link(o): sc.collection.objects.link(o); return o
def bevel(o, w, seg=2):
    md = o.modifiers.new('bev', 'BEVEL'); md.width = w; md.segments = seg; md.limit_method = 'ANGLE'
    for p in o.data.polygons: p.use_smooth = True
def box(name, x0, x1, y0, y1, z0, z1, m, bev=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * (x1 - x0), v.co.y * (y1 - y0), v.co.z * (z1 - z0)))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); o.data.materials.append(m); link(o)
    if bev: bevel(o, bev)
    return o
def cyl_y(name, x, z, y0, y1, r, m, verts=32, smooth=True):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=(y1 - y0)); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = smooth
    o = bpy.data.objects.new(name, me); o.location = (x, (y0 + y1) / 2, z); o.rotation_euler = (math.radians(90), 0, 0); o.data.materials.append(m); return link(o)
def prism_x(name, poly, x0, x1, m):
    """沿 x 挤出的多边形（poly 为 (y,z) 点）"""
    bm = bmesh.new(); vs0 = [bm.verts.new((x0, y, z)) for y, z in poly]; vs1 = [bm.verts.new((x1, y, z)) for y, z in poly]
    bm.faces.new(vs0[::-1]); bm.faces.new(vs1)
    for i in range(len(poly)): j = (i + 1) % len(poly); bm.faces.new((vs0[i], vs0[j], vs1[j], vs1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.data.materials.append(m); return link(o)
def prism_poly_xz(name, poly, y0, y1, m):
    """沿 y 挤出的多边形（poly 为 (x,z) 点）"""
    bm = bmesh.new(); vs0 = [bm.verts.new((x, y0, z)) for x, z in poly]; vs1 = [bm.verts.new((x, y1, z)) for x, z in poly]
    bm.faces.new(vs0); bm.faces.new(vs1[::-1])
    for i in range(len(poly)): j = (i + 1) % len(poly); bm.faces.new((vs0[j], vs0[i], vs1[i], vs1[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.data.materials.append(m); return link(o)
def wire(name, pts, r, m):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 4; cu.resolution_u = 16
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts): bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); o.data.materials.append(m); return link(o)

# 芯片：x ±50，y -45..40，表面 z=0
die_top = box('die_top', -50, 50, -45, 40, -0.02, 0.0, M['chip'])
# 芯片表面物体坐标：中心 (0,-2.5)；贴图覆盖 x∈[-50,50]、y∈[-55,45] → v = 0.525 + y_local/100
for n in M['chip'].node_tree.nodes:
    if n.type == 'MAPPING': n.inputs['Location'].default_value = (0.5, 0.525, 0)
die_body = box('die_body', -50, 50, -45, 40, -8, -0.02, M['die_side'], bev=0.1)
clad = box('upper_cladding', -50, 50, -13.5, 40, 0.0, 1.0, M['clad'])
WG_W, WG_H, WG_Z = 0.6, 0.4, 0.4
wg_si = box('wg_si', -WG_W / 2, WG_W / 2, -14, 36, WG_Z - WG_H / 2, WG_Z + WG_H / 2, M['si_wg'], bev=0.05)
band_in = box('band_in', -0.19, 0.19, -14, Y_EXIT, WG_Z - 0.12, WG_Z + 0.12, M['steady'])
band_out = box('band_out', -0.19, 0.19, Y_EXIT, 36, WG_Z - 0.12, WG_Z + 0.12, M['msg'])
tail_in = box('tail_in', -0.55, 0.55, -14, 36, WG_Z - 0.2, WG_Z + 0.2, M['tail'])
ssc = box('ssc', -0.9, 0.9, 36, Y_EDGE, 0.1, 0.8, M['ssc'], bev=0.04)
ssc_band = box('ssc_band', -0.5, 0.5, 36, Y_EDGE, 0.25, 0.55, M['msg'])
# 激光器（在芯片上，端面 y=-14 朝 +y）
laser = box('laser', -4, 4, -28, -14, 0.0, 3.2, M['laser'], bev=0.15)
laser_face = box('laser_face', -0.7, 0.7, -14.02, -13.98, WG_Z - 0.3, WG_Z + 0.3, M['steady'])
# 金电极夹着波导，x=±1.7，y -1..11（z 1.0..1.5，在上包层面上）
EX = 1.7
elec = []
for s in (-1, 1):
    m = mat_gold(f'gold_el_{s}', Vector((0, 0, 0)), Vector((0, 1, 0)), 0.0)
    elec.append(box(f'electrode_{s}', s * EX - 0.55, s * EX + 0.55, -1.2, 11.0, 1.0, 1.5, m, bev=0.06))
    # 驱动芯片（黑）+ 焊线 + 走线
    dx0, dx1 = sorted((s * 8, s * 14)); drv = box(f'driver_{s}', dx0, dx1, -11, -3, 1.0, 3.2, M['ic'], bev=0.12)
    P_start = Vector((s * 8.2, -7.0, 3.2)); P_end = Vector((s * 1.9, -1.0, 1.5)); d = (P_end - P_start); Ld = d.length; dn = d.normalized()
    mw = mat_gold(f'gold_wire_{s}', P_start, dn, -1.0 - Ld, emis=2.6)
    wire(f'bond_{s}', [P_start, (P_start + P_end) / 2 + Vector((0, 0, 1.8)), P_end], 0.14, mw)
    # 走线：从 x=±45 流向驱动器，ℓ 在 |x|=14 处为 -1.0-Ld-6
    l14 = -1.0 - Ld - 6.0
    mt = mat_gold(f'gold_trace_{s}', Vector((s * 14, -7, 1)), Vector((-s, 0, 0)), l14, emis=2.2)
    box(f'trace_{s}', min(s * 14, s * 46), max(s * 14, s * 46), -7.4, -6.6, 1.0, 1.1, mt)
# 光纤阵列：V 形槽块抵着芯片边缘，5 根光纤，中间那根带光（x 由 fiber_x 控制）
FIB_R, CORE_R = 7.0, 1.5; PITCH = 20.0; FIB_Y1 = 350.0
poly = [(-60, -16)]
for k in range(-2, 3): pass
pts = [(-60, -16), (60, -16), (60, -1.5)]
for k in range(2, -3, -1):
    cx = k * PITCH; pts += [(cx + 9.2, -1.5), (cx, -8.0), (cx - 9.2, -1.5)]
pts += [(-60, -1.5)]
# 去掉相邻 V 间重复点（相邻 V 在 cx±10 处各有 -1.5 点，间隔 20-18.4=1.6）
vgroove = prism_poly_xz('v_groove', pts, Y_FACE + 0.2, 95, M['vgroove'])
fibers = []; cores = []; fib_center = None
for k in range(-2, 3):
    gl = cyl_y(f'fiber_{k}', k * PITCH, 0.5, Y_FACE, FIB_Y1, FIB_R, M['glass'], verts=40)
    mc = M['core'] if k == 0 else mat('dark_core', (0.1, 0.2, 0.25), 0.0, 0.2, alpha=0.5)
    co = cyl_y(f'core_{k}', k * PITCH, 0.5, Y_FACE, FIB_Y1, CORE_R, mc, verts=20)
    fibers.append(gl); cores.append(co)
    if k == 0: fib_center = (gl, co)
ribbon = box('ribbon', -62, 62, 150, 340, -9, 9, M['ribbon'], bev=0.5)
mpo = box('mpo', -52, 52, 340, 420, -24, 24, M['mpo'], bev=1.0)
leak_vol = None
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.4, radius2=6.0, depth=10.0); me = bpy.data.meshes.new('leak_cone'); bm.to_mesh(me); bm.free()
leak_vol = bpy.data.objects.new('leak_cone', me); leak_vol.data.materials.append(M['leak']); link(leak_vol)
leak_vol.location = (0, Y_FACE + 5.0, 0.5); leak_vol.rotation_euler = (math.radians(-90), 0, 0)    # 锥尖在端面，向 +y 张开

# 模块内部（背景环境）
pcb = box('pcb', -110, 110, -170, 430, -10, -8, M['pcb'], bev=0.2)
dsp = box('dsp', 40, 100, -130, -70, -8, -2, M['ic'], bev=0.3)
for k in range(24): box(f'finger_{k}', -85 + k * 7.4, -85 + k * 7.4 + 4.0, -168, -150, -8, -7.9, M['finger'])
for k in range(5): box(f'cap_{k}', -95 + k * 9, -90 + k * 9, -60, -55, -8, -5.5, M['ic'], bev=0.1)
# 驱动芯片到 PCB 的粗线条略（驱动 IC 通过走线接入）
shell = box('shell', -118, 118, -175, 440, -20, 82, M['shell'])

# ---------- 灯光、环境 ----------
rig = None
def area(name, loc, energy, size, col, target):
    Lg = bpy.data.lights.new(name, 'AREA'); Lg.energy = energy; Lg.size = size; Lg.color = col; o = bpy.data.objects.new(name, Lg); sc.collection.objects.link(o)
    o.location = loc; tc = o.constraints.new('TRACK_TO'); tc.target = target; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'; return o
tgt = bpy.data.objects.new('cam_target', None); sc.collection.objects.link(tgt)
bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.lens = 32
tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
cam.data.clip_start = 0.3; cam.data.clip_end = 3000
cam.data.dof.use_dof = True; cam.data.dof.focus_object = tgt
key_l = area('key', (-60, -60, 90), 40000, 60, (1.0, 0.95, 0.88), tgt)
fill_l = area('rim', (70, 60, 50), 22000, 50, (0.6, 0.72, 1.0), tgt)
# 灯光跟着相机目标走
for l in (key_l, fill_l):
    cp = l.constraints.new('COPY_LOCATION'); cp.target = tgt; cp.use_offset = True
wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True; N = wd.node_tree.nodes; L = wd.node_tree.links
for n in list(N): N.remove(n)
out = N.new('ShaderNodeOutputWorld'); bg_hdr = N.new('ShaderNodeBackground'); bg_col = N.new('ShaderNodeBackground'); mx = N.new('ShaderNodeMixShader'); lp = N.new('ShaderNodeLightPath')
bg_col.inputs['Color'].default_value = (0.008, 0.025, 0.10, 1); bg_hdr.inputs['Strength'].default_value = 0.9
if os.path.exists(HDRI):
    env = N.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(HDRI, check_existing=True); L.new(env.outputs['Color'], bg_hdr.inputs['Color'])
else: bg_hdr.inputs['Color'].default_value = (0.5, 0.55, 0.65, 1)
L.new(bg_hdr.outputs[0], mx.inputs[1]); L.new(bg_col.outputs[0], mx.inputs[2]); L.new(lp.outputs['Is Camera Ray'], mx.inputs['Fac']); L.new(mx.outputs[0], out.inputs[0])

# ---------- 镜头 ----------
def hermite(keys, t):
    """keys: [(t, Vector)]；Catmull-Rom 型 Hermite，非均匀时间"""
    n = len(keys)
    if t <= keys[0][0]: return keys[0][1].copy()
    if t >= keys[-1][0]: return keys[-1][1].copy()
    i = max(j for j in range(n - 1) if keys[j][0] <= t)
    t1, p1 = keys[i]; t2, p2 = keys[i + 1]
    def tan(k):
        a, b = max(k - 1, 0), min(k + 1, n - 1)
        return (keys[b][1] - keys[a][1]) / (keys[b][0] - keys[a][0])
    dt = t2 - t1; u = (t - t1) / dt; m1 = tan(i) * dt; m2 = tan(i + 1) * dt
    h00 = 2 * u ** 3 - 3 * u ** 2 + 1; h10 = u ** 3 - 2 * u ** 2 + u; h01 = -2 * u ** 3 + 3 * u ** 2; h11 = u ** 3 - u ** 2
    return h00 * p1 + h10 * m1 + h01 * p2 + h11 * m2
V = Vector
EYE = [(0.0, V((-46, -118, 58))), (0.5, V((-7.5, -31, 12.5))), (2.0, V((-6.5, -23, 11))), (4.0, V((-5.5, -6, 9.5))), (6.0, V((-6, 13, 8))),
       (7.0, V((-6.5, 22, 6.5))), (8.2, V((-8, 29, 4.8))), (10.6, V((-9, 31, 4.4))), (11.1, V((-4, 55, 5))), (11.6, V((-1, 150, 5.5))), (12.0, V((0, 300, 5)))]
TGT = [(0.0, V((0, -8, -3))), (0.5, V((0, -6, 0.5))), (2.0, V((0, -1, 0.5))), (4.0, V((0, 17, 0.5))), (6.0, V((0, 34, 0.6))),
       (7.0, V((0.2, 38, 0.7))), (8.2, V((0.8, 41, 0.8))), (10.6, V((0.6, 41, 0.7))), (11.1, V((0, 85, 0.5))), (11.6, V((0, 200, 0.5))), (12.0, V((0, 340, 0.5)))]
FST = [(0.0, 0.05), (0.5, 0.04), (4.0, 0.03), (7.0, 0.02), (8.2, 0.012), (10.6, 0.012), (11.5, 0.008), (12.0, 0.008)]
def lin(keys, t):
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t0 <= t <= t1: return a + (b - a) * (t - t0) / (t1 - t0)
    return keys[-1][1]
sstep = lambda a, b, x: (lambda u: u * u * (3 - 2 * u))(min(max((x - a) / (b - a), 0.0), 1.0))
def fiber_dx(t):
    return 3.2 * (sstep(8.5, 9.2, t) - sstep(9.8, 10.6, t))
def coupling(dx): return max(0.08, math.exp(-(dx / 2.1) ** 2))

# 每帧关键帧（运动模糊要用）
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    cam.location = hermite(EYE, t); cam.keyframe_insert('location', frame=f)
    tgt.location = hermite(TGT, t); tgt.keyframe_insert('location', frame=f)
    cam.data.dof.aperture_fstop = lin(FST, t); cam.data.dof.keyframe_insert('aperture_fstop', frame=f)
    dx = fiber_dx(t)
    for o in fibers[2:3] + cores[2:3]: o.location.x = dx; o.keyframe_insert('location', index=0, frame=f)
    for (m, n, name) in VALUE_NODES:
        if name == 'T': n.outputs[0].default_value = t
        elif name == 'cpl': n.outputs[0].default_value = coupling(dx)
        elif name == 'leak': n.outputs[0].default_value = max(0.0, 1.0 - coupling(dx) / 1.0) if dx > 0.05 else 0.0
        else: continue
        n.outputs[0].keyframe_insert('default_value', frame=f)
for m in set(m for m, _, _ in VALUE_NODES): set_interp(m.node_tree, 'LINEAR')
for o in (cam, tgt, fibers[2], cores[2]): set_interp(o, 'LINEAR')
set_interp(cam.data, 'LINEAR')

# ---------- 渲染设置 ----------
sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMP; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 6; sc.cycles.transparent_max_bounces = 16
sc.cycles.volume_bounces = 0; sc.cycles.volume_step_rate = 2.0; sc.cycles.use_adaptive_sampling = True
sc.render.threads_mode = 'FIXED'; sc.render.threads = THREADS
if GPU:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for dt in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = dt; prefs.refresh_devices()
            if [d for d in prefs.devices if d.type == dt]:
                for d in prefs.devices: d.use = d.type == dt
                sc.cycles.device = 'GPU'; print('GPU_DEVICE', dt); break
        except Exception: pass
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.resolution_percentage = 100; sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, NF
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.4
sc.view_settings.view_transform = 'AgX'
for lk in ('AgX - Medium High Contrast', 'Medium High Contrast'):
    try: sc.view_settings.look = lk; break
    except Exception: pass
# 合成：辉光只给「光」
try:
    vl = sc.view_layers[0]; vl.use_pass_emit = True; aov = vl.aovs.add(); aov.name = 'lightmask'; aov.type = 'VALUE'
    ng = bpy.data.node_groups.new('comp', 'CompositorNodeTree'); sc.compositing_node_group = ng
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new('CompositorNodeRLayers'); rl.scene = sc
    emit = rl.outputs.get('Emit') or rl.outputs.get('Emission'); mask = rl.outputs.get('lightmask')
    mul = ng.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1.0
    ng.links.new(emit, mul.inputs['A']); ng.links.new(mask, mul.inputs['B'])
    gl = ng.nodes.new('CompositorNodeGlare'); ng.links.new(mul.outputs['Result'], gl.inputs['Image'])
    for k, v in (('Type', 'Fog Glow'), ('Threshold', 0.0), ('Strength', 0.7), ('Quality', 'High'), ('Size', 0.55)):
        try: gl.inputs[k].default_value = v
        except Exception as e: print('辉光参数跳过', k, e)
    add = ng.nodes.new('ShaderNodeMix'); add.data_type = 'RGBA'; add.blend_type = 'ADD'; add.inputs['Factor'].default_value = 1.0
    ng.links.new(rl.outputs['Image'], add.inputs['A']); ng.links.new(gl.outputs['Glare'], add.inputs['B'])
    go = ng.nodes.new('NodeGroupOutput'); ng.links.new(add.outputs['Result'], go.inputs[0])
except Exception as e: print('COMPOSITOR 跳过：', e)
set_fmt('PNG'); sc.render.use_overwrite = True

# ---------- 锚点（给 2D 合成贴标签） ----------
ANCH = {'laser_label': V((0.9, -9.0, 1.3)), 'electric_label': V((4.2, 5.0, 1.6)), 'offset_label': V((1.5, 40.7, 4.0)), 'core_face': V((0, Y_FACE, 0.5))}
def anchors_for(f):
    sc.frame_set(f); bpy.context.view_layer.update(); fr = {}
    for k, p in ANCH.items():
        if k == 'offset_label': p = p + Vector((fiber_dx((f - 1) / FPS) * 0.5, 0, 0))
        v = world_to_camera_view(sc, cam, p); fr[k] = [round(v.x * W, 1), round((1 - v.y) * H, 1), round(v.z, 1)]
    fr['t'] = round((f - 1) / FPS, 3); return fr
anch = {}
if TIMES: todo = [(F(t), f't{t:05.2f}') for t in TIMES]
else:
    a, b = FRANGE if FRANGE else (1, NF); todo = [(f, f'f{f:04d}') for f in range(a, b + 1)]
for f in range(1, NF + 1): anch[f] = anchors_for(f)
json.dump({'fps': FPS, 'nf': NF, 'w': W, 'h': H, 'frames': anch}, open(os.path.join(OUT, 'anchors.json'), 'w'))
for f, name in todo:
    path = os.path.join(OUT, name + '.png')
    if os.path.exists(path) and not TIMES: continue
    sc.frame_set(f); sc.render.filepath = path; t0 = time.time(); bpy.ops.render.render(write_still=True)
    print(f'FRAME_TIME {name} {time.time() - t0:.1f}s samples={SAMP} {W}x{H}', flush=True)
print('DONE', OUT)
