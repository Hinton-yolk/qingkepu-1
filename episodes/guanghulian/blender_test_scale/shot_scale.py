# 一语道破 · Blender 测试镜头三：光在芯片里走的路有多细？（2026-11-10，真实感改造版，按 SHOTPLAN 第四版）
# 竖屏 18 秒，一个连续镜头对数匀速推进：交换机 → 光模块（手机）→ 硅光芯片（米粒）→ 芯片边缘的光纤阵列（头发）
#   → 离边缘约 150 µm 的波导（红细胞）→ 停在「不到 0.5 µm」的波导上。
# 做法：相机不动，整个世界围绕焦点逐帧缩放（单位 µm，网格按真实尺寸）。
# 真实感：Poly Haven HDRI 环境光（只用于打光和反射，相机看到的背景仍是深蓝）、倒角、程序生成的芯片版图贴图、
#         金属粗糙度贴图、浅景深、合成里只给光加辉光（AOV 遮罩）。
# 物体进出用淡入淡出（物体颜色的 alpha），淡完再关渲染；标签保持屏幕上的字号（反向缩放）。
# 默认 EEVEE。用法：
#   blender -b --python-exit-code 1 --python shot_scale.py -- <输出目录> <宽> <高> <采样> [--gpu] [--cycles] [--fps N] [--video] [帧号…]
#   --video：输出 PNG 序列（可续渲：已存在的帧跳过），云端再编码成视频。
import bpy, bmesh, math, sys, json, os, random, time
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

args = sys.argv[sys.argv.index('--') + 1:]; OUT, W, H, SAMP = args[0], int(args[1]), int(args[2]), int(args[3]); rest = args[4:]
GPU = '--gpu' in rest; CYCLES = '--cycles' in rest; VIDEO = '--video' in rest
FPS = int(rest[rest.index('--fps') + 1]) if '--fps' in rest else 30
FRAMES = [int(a) for i, a in enumerate(rest) if a.isdigit() and not (i > 0 and rest[i - 1] == '--fps')]
DUR = 18.0; NF = round(DUR * FPS); F = lambda sec: 1 + round(sec * FPS)
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, 'assets', 'label_font.otf'); LAYOUT = os.path.join(HERE, 'assets', 'chip_layout.png')
HDRI = os.path.join(HERE, 'assets_dl', 'studio_small_09_2k.hdr'); ROUGH = os.path.join(HERE, 'assets_dl', 'metal_plate_rough_2k.jpg')
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; os.makedirs(OUT, exist_ok=True)
print('BLENDER_VERSION', bpy.app.version_string)

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
    if hasattr(ims, 'media_type'): ims.media_type = 'VIDEO' if fmt == 'FFMPEG' else 'IMAGE'
    ims.file_format = fmt

# ---------- 材质 ----------
# 所有材质的透明度都乘上「物体颜色的 alpha」（用来淡入淡出）；需要半透明的用 BLENDED，其余用 DITHERED。
def _fade_alpha(m, base, target_socket):
    N = m.node_tree.nodes; L = m.node_tree.links
    oi = N.new('ShaderNodeObjectInfo'); mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
    if isinstance(base, float): mul.inputs[1].default_value = base
    else: L.new(base, mul.inputs[1])
    L.new(oi.outputs['Alpha'], mul.inputs[0]); L.new(mul.outputs[0], target_socket)
def mat(name, col, metal=0.0, rough=0.5, alpha=1.0, coat=0.0, sss=0.0, rough_tex=None, rough_scale=1.0, bump=0.0, aniso=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat
    if sss: b.inputs['Subsurface Weight'].default_value = sss
    if aniso and 'Anisotropic' in b.inputs: b.inputs['Anisotropic'].default_value = aniso
    if rough_tex or bump:                         # 粗糙度细节：贴图（金属划痕）或程序噪声
        tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (rough_scale, rough_scale * (8 if aniso else 1), rough_scale)
        L.new(tc.outputs['Object'], mp.inputs['Vector'])
        if rough_tex and os.path.exists(rough_tex):
            it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(rough_tex, check_existing=True); it.image.colorspace_settings.name = 'Non-Color'
            it.projection = 'BOX'; L.new(mp.outputs[0], it.inputs[0]); src = it.outputs['Color']
        else:
            nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0; nz.inputs['Detail'].default_value = 8.0; L.new(mp.outputs[0], nz.inputs['Vector']); src = nz.outputs['Fac']
        mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = max(0.02, rough - 0.12); mr.inputs['To Max'].default_value = min(1.0, rough + 0.15)
        L.new(src, mr.inputs['Value']); L.new(mr.outputs[0], b.inputs['Roughness'])
        if bump:
            bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; L.new(src, bp.inputs['Height']); L.new(bp.outputs[0], b.inputs['Normal'])
    _fade_alpha(m, alpha, b.inputs['Alpha'])
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'BLENDED' if alpha < 1 else 'DITHERED'
    return m
def mat_emit(name, col, strength, alpha=1.0, aov=False):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    for n in list(N): N.remove(n)
    o = N.new('ShaderNodeOutputMaterial'); e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*col, 1); e.inputs['Strength'].default_value = strength
    tr = N.new('ShaderNodeBsdfTransparent'); mx = N.new('ShaderNodeMixShader')
    L.new(tr.outputs[0], mx.inputs[1]); L.new(e.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], o.inputs[0])
    _fade_alpha(m, alpha, mx.inputs['Fac'])
    if aov:
        ao = N.new('ShaderNodeOutputAOV'); ao.aov_name = 'lightmask'; ao.inputs['Value'].default_value = 1.0
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'BLENDED' if alpha < 1 else 'DITHERED'
    return m, e
CYAN = (0.20, 0.95, 0.85)
def mat_light_band():
    """光带：均匀青色；13 秒起叠加相位条纹（间距 0.5 µm，每秒走 1 µm，朝 −y：从调制器往芯片边缘、往光纤方向，发射端）"""
    m, e = mat_emit('light_band', CYAN, 1.6, aov=True); N = m.node_tree.nodes; L = m.node_tree.links
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])
    off = N.new('ShaderNodeValue'); off.name = 'phase_offset'
    add = N.new('ShaderNodeMath'); add.operation = 'ADD'; L.new(sep.outputs['Y'], add.inputs[0]); L.new(off.outputs[0], add.inputs[1])
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 2 * math.pi / 0.5; L.new(add.outputs[0], mul.inputs[0])
    sn = N.new('ShaderNodeMath'); sn.operation = 'SINE'; L.new(mul.outputs[0], sn.inputs[0])
    amp = N.new('ShaderNodeValue'); amp.name = 'stripe_amp'
    a1 = N.new('ShaderNodeMath'); a1.operation = 'MULTIPLY'; L.new(sn.outputs[0], a1.inputs[0]); L.new(amp.outputs[0], a1.inputs[1])
    a2 = N.new('ShaderNodeMath'); a2.operation = 'ADD'; a2.inputs[1].default_value = 1.0; L.new(a1.outputs[0], a2.inputs[0])
    st = N.new('ShaderNodeMath'); st.operation = 'MULTIPLY'; st.inputs[1].default_value = 1.6; L.new(a2.outputs[0], st.inputs[0]); L.new(st.outputs[0], e.inputs['Strength'])
    for fr, v in ((1, 0.0), (NF, (NF - 1) / FPS)): off.outputs[0].default_value = v; off.outputs[0].keyframe_insert('default_value', frame=fr)   # +v：条纹朝 −y 走
    for fr, v in ((1, 0.0), (F(12.6), 0.0), (F(13.4), 0.4), (NF, 0.4)): amp.outputs[0].default_value = v; amp.outputs[0].keyframe_insert('default_value', frame=fr)
    set_interp(m.node_tree, 'LINEAR'); return m
def mat_chip_surface():
    """芯片表面：深蓝氧化层底色；版图贴图 R = 硅器件（钢蓝），G = 金属（金），A = 亮着的光路（青，远景时看得见光走到哪）"""
    m = bpy.data.materials.new('chip_surface'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1 / 5000, 1 / 5000, 1); mp.inputs['Location'].default_value = (0.5, 0.5, 0)
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(LAYOUT, check_existing=True); it.image.colorspace_settings.name = 'Non-Color'; it.interpolation = 'Cubic'
    L.new(mp.outputs[0], it.inputs[0]); sp = N.new('ShaderNodeSeparateColor'); L.new(it.outputs['Color'], sp.inputs[0])
    def mix(fac, a, bcol):
        mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L.new(fac, mx.inputs['Factor'])
        if isinstance(a, tuple): mx.inputs['A'].default_value = (*a, 1)
        else: L.new(a, mx.inputs['A'])
        mx.inputs['B'].default_value = (*bcol, 1); return mx.outputs['Result']
    c1 = mix(sp.outputs['Red'], (0.015, 0.05, 0.20), (0.20, 0.27, 0.40)); c2 = mix(sp.outputs['Green'], c1, (0.95, 0.66, 0.24))
    L.new(c2, b.inputs['Base Color']); L.new(sp.outputs['Green'], b.inputs['Metallic'])
    rg = N.new('ShaderNodeMapRange'); rg.inputs['To Min'].default_value = 0.32; rg.inputs['To Max'].default_value = 0.2; L.new(sp.outputs['Green'], rg.inputs['Value']); L.new(rg.outputs[0], b.inputs['Roughness'])
    b.inputs['Coat Weight'].default_value = 0.5; b.inputs['Emission Color'].default_value = (*CYAN, 1)
    em = N.new('ShaderNodeMath'); em.operation = 'MULTIPLY'; em.inputs[1].default_value = 1.4; L.new(it.outputs['Alpha'], em.inputs[0]); L.new(em.outputs[0], b.inputs['Emission Strength'])
    _fade_alpha(m, 1.0, b.inputs['Alpha'])
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'DITHERED'
    return m
M = dict(
    chip=mat_chip_surface(),
    clad=mat('upper_cladding_glass', (0.6, 0.7, 0.9), 0.0, 0.12, alpha=0.05),
    si_wg=mat('si_waveguide_clear', (0.35, 0.45, 0.62), 0.0, 0.12, alpha=0.30),     # 硅在 1310 nm 透明：画成半透明，看得见芯区里的光
    si_side=mat('si_die_side', (0.10, 0.11, 0.14), 0.7, 0.35, bump=0.2),
    gold=mat('gold_electrode', (0.95, 0.66, 0.24), 1.0, 0.22, rough_tex=ROUGH, rough_scale=0.02),
    light=mat_light_band(),
    tail=mat_emit('evanescent_tail', CYAN, 0.7, alpha=0.10, aov=True)[0],
    glass=mat('fiber_glass', (0.55, 0.65, 0.78), 0.0, 0.06, alpha=0.22, coat=0.3),
    vgroove=mat('v_groove_block', (0.62, 0.64, 0.68), 0.0, 0.25, coat=0.4),         # V 形槽块：浅灰
    ssc=mat('ssc_block', (0.45, 0.55, 0.75), 0.0, 0.2, alpha=0.35),
    rbc=mat('red_blood_cell', (0.26, 0.05, 0.06), 0.0, 0.5, sss=0.1),
    hair=mat('hair', (0.08, 0.055, 0.045), 0.0, 0.35, coat=0.6, bump=0.3),
    rice=mat('rice', (0.92, 0.90, 0.84), 0.0, 0.35, sss=0.6, bump=0.15),
    pcb=mat('pcb_solder_mask', (0.03, 0.14, 0.05), 0.0, 0.35, coat=0.5, bump=0.1),   # 绿色阻焊（不用青蓝）
    copper=mat('pcb_gold_pad', (0.95, 0.66, 0.24), 1.0, 0.25),
    ic=mat('ic_package', (0.05, 0.05, 0.055), 0.2, 0.45, bump=0.05),
    laser=mat('laser_chip', (0.32, 0.33, 0.36), 0.7, 0.3),
    ribbon=mat('fiber_ribbon', (0.55, 0.56, 0.58), 0.0, 0.5),
    mpo=mat('mpo', (0.25, 0.26, 0.28), 0.0, 0.45),
    shell=mat('module_shell', (0.72, 0.74, 0.78), 1.0, 0.3, alpha=0.25, rough_tex=ROUGH, rough_scale=0.0003, aniso=0.6),
    shell_end=mat('module_front', (0.66, 0.68, 0.72), 1.0, 0.3, rough_tex=ROUGH, rough_scale=0.0003, aniso=0.6),
    tab=mat('pull_tab', (0.10, 0.10, 0.11), 0.0, 0.55),
    sw=mat('switch_metal', (0.06, 0.065, 0.075), 0.7, 0.45, rough_tex=ROUGH, rough_scale=0.00005),
    sw_top=mat('switch_cover', (0.10, 0.11, 0.13), 0.0, 0.3, alpha=0.06),
    asic=mat('switch_asic_dim', (0.04, 0.04, 0.045), 0.2, 0.5),
    cage=mat('port_cage', (0.58, 0.60, 0.63), 1.0, 0.3, rough_tex=ROUGH, rough_scale=0.0002),
    led=mat_emit('led_green', (0.2, 1.0, 0.25), 5.0)[0],
    rack=mat('rack_rail', (0.10, 0.11, 0.12), 0.8, 0.4, rough_tex=ROUGH, rough_scale=0.00005),
    other=mat('other_device', (0.045, 0.05, 0.06), 0.6, 0.45),
    patch=mat('patch_cord', (0.42, 0.43, 0.45), 0.0, 0.55),
    phone=mat('phone_body', (0.16, 0.16, 0.18), 0.9, 0.25),
    phone_screen=mat('phone_screen_off', (0.008, 0.008, 0.01), 0.0, 0.06, coat=1.0),
    shelf=mat('shelf', (0.12, 0.13, 0.15), 0.7, 0.45),
    label=mat_emit('label_white', (1.0, 1.0, 1.0), 3.0)[0],
)

# ---------- 几何工具（单位 µm，网格按真实尺寸） ----------
WORLD = bpy.data.objects.new('WORLD', None); sc.collection.objects.link(WORLD)
def link(o, parent=WORLD): sc.collection.objects.link(o); o.parent = parent; return o
def bevel(o, w, seg=3):
    md = o.modifiers.new('bev', 'BEVEL'); md.width = w; md.segments = seg; md.limit_method = 'ANGLE'
    for p in o.data.polygons: p.use_smooth = True
    o.modifiers.new('wn', 'WEIGHTED_NORMAL')
def box(name, cx, cy, cz, sx, sy, sz, m, bev=0.06):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = (cx, cy, cz); o.data.materials.append(m); link(o)
    if bev: bevel(o, bev * min(sx, sy, sz))
    return o
def cyl(name, r, depth, m, loc, rot=(0, 0, 0), verts=40):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=depth); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; o.rotation_euler = rot; o.data.materials.append(m); return link(o)
def tube(name, pts, r, m):
    """沿控制点生成圆管（跳线用）"""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 3
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts): bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); o.data.materials.append(m); return link(o)
def ellipsoid(name, rx, ry, rz, m, loc, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=20, radius=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * rx, v.co.y * ry, v.co.z * rz))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; o.rotation_euler = rot; o.data.materials.append(m); return link(o)
def rbc_mesh(name, D, m, loc):
    """红细胞：双凹圆盘（Evans–Fung 截面形状），直径 D"""
    R = D / 2; prof = []
    for j in range(25):
        rr = R * j / 24; x = rr / R
        h = 0.5 * R * math.sqrt(max(0.0, 1 - x * x)) * (0.207 + 2.003 * x * x - 1.123 * x ** 4)
        prof.append((rr, max(h, 0.0)))
    bm = bmesh.new(); seg = 48
    top = [[bm.verts.new((rr * math.cos(2 * math.pi * i / seg), rr * math.sin(2 * math.pi * i / seg), h)) for i in range(seg)] for rr, h in prof[:-1]]
    bot = [[bm.verts.new((rr * math.cos(2 * math.pi * i / seg), rr * math.sin(2 * math.pi * i / seg), -h)) for i in range(seg)] for rr, h in prof[:-1]]
    rim = [bm.verts.new((R * math.cos(2 * math.pi * i / seg), R * math.sin(2 * math.pi * i / seg), 0)) for i in range(seg)]
    for layer, flip in ((top, False), (bot, True)):
        rows = layer + [rim]
        for j in range(1, len(rows) - 1):
            for i in range(seg):
                q = [rows[j][i], rows[j][(i + 1) % seg], rows[j + 1][(i + 1) % seg], rows[j + 1][i]]
                bm.faces.new(q[::-1] if flip else q)
        cen = rows[0]
        for i in range(seg):
            t = [cen[i], cen[(i + 1) % seg], rows[1][(i + 1) % seg], rows[1][i]]
            try: bm.faces.new(t[::-1] if flip else t)
            except ValueError: pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; o.data.materials.append(m); return link(o)

# ---------- 尺度时间线（先定义：可见性、标签都要用） ----------
KEYS = [(0.0, 600000.0), (2.0, 400000.0), (4.5, 120000.0), (7.0, 12000.0), (9.0, 1000.0), (11.5, 100.0), (13.5, 25.0), (16.0, 4.0), (18.0, 3.0)]
def log_width(t):
    for (t0, w0), (t1, w1) in zip(KEYS, KEYS[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            if t1 == KEYS[-1][0]: u = 1 - (1 - u) ** 2
            return math.log10(w0) + u * (math.log10(w1) - math.log10(w0))
    return math.log10(KEYS[-1][1])
view_w = lambda t: 10 ** log_width(t)
def t_at_width(w):
    for f in range(1, NF + 1):
        if view_w((f - 1) / FPS) <= w: return (f - 1) / FPS
    return DUR

# ---------- 芯片（5 mm 示例），表面 z = 0，前边缘 y = −2500 ----------
DIE = 5000.0; EDGE = -DIE / 2
WG_W, WG_H = 0.40, 0.22
SSC_L = 100.0                                       # 模斑转换器（示意）长 100 µm；焦点在它后面 50 µm
FOCUS = Vector((0.0, EDGE + 150.0, WG_H / 2))
die_top = box('die_surface', 0, 0, -0.01, DIE, DIE, 0.02, M['chip'], bev=0)
die_body = box('die_body', 0, 0, -375.5, DIE, DIE, 749.0, M['si_side'], bev=0.01)
clad = box('upper_cladding', 0, 0, 1.25, DIE - 2, DIE - 2, 2.5, M['clad'], bev=0)     # 整片上包层：很淡的玻璃面
FX = [250.0 * (i - 3) for i in range(8)]
WG_Y0, WG_Y1 = EDGE + SSC_L, EDGE + 1600
wgs, bands, tails, sscs, ssc_bands, electrodes = [], [], [], [], [], []
for i, x in enumerate(FX):
    cy, ly = (WG_Y0 + WG_Y1) / 2, WG_Y1 - WG_Y0
    wgs.append(box(f'wg_{i}', x, cy, WG_H / 2, WG_W, ly, WG_H, M['si_wg'], bev=0.08))
    bands.append(box(f'band_{i}', x, cy, WG_H / 2, WG_W * 0.62, ly, WG_H * 0.58, M['light'], bev=0))
    tails.append(box(f'tail_{i}', x, cy, WG_H / 2 + 0.001, WG_W * 2.0, ly, WG_H * 1.7, M['tail'], bev=0))
    sscs.append(box(f'ssc_{i}', x, EDGE + SSC_L / 2, 1.5, 8.0, SSC_L, 3.0, M['ssc'], bev=0.1))
    ssc_bands.append(box(f'ssc_band_{i}', x, EDGE + SSC_L / 2, 1.5, 3.0, SSC_L, 1.2, M['light'], bev=0))   # 模斑转换器里也有光（示意）
    for sgn in (-1, 1): electrodes.append(box(f'mzm_{i}_{sgn}', x + sgn * 9.0, EDGE + 665, 1.0, 10.0, 1000, 2.0, M['gold'], bev=0.15))
# 光纤阵列（端面耦合）：V 形槽块抵着芯片边缘，光纤躺在槽里，纤芯和波导同高；盖板省略
VG_L = 4000.0
vg = box('v_groove_block', 375.0, EDGE - VG_L / 2 - 5, -500.0, 2600, VG_L, 1000, M['vgroove'], bev=0.02)
fibers, cores = [], []
for i, x in enumerate(FX):
    fibers.append(cyl(f'fiber_{i}', 62.5, VG_L, M['glass'], (x, EDGE - VG_L / 2 - 5, 0.0), (math.radians(90), 0, 0)))
    cores.append(cyl(f'fiber_core_{i}', 4.1, VG_L, M['light'], (x, EDGE - VG_L / 2 - 5, 0.0), (math.radians(90), 0, 0), verts=16))
hair = cyl('human_hair', 37.5, 3000.0, M['hair'], (300.0, EDGE - 450, 62.5 + 37.5), (0, math.radians(90), math.radians(8)), verts=24)
rbc = rbc_mesh('red_blood_cell', 7.5, M['rbc'], (6.0, FOCUS.y + 4.0, 2.5 + 1.1))

# ---------- 光模块（QSFP-DD）----------
MOD_W, MOD_H = 18350.0, 8500.0
MOD_FRONT, MOD_BACK = -40000.0, 38000.0
PCB_Z = -750.0 - 500.0; PCB_TOP = PCB_Z + 500
pcb = box('module_pcb', 0, (MOD_FRONT + MOD_BACK) / 2, PCB_Z, MOD_W - 1200, MOD_BACK - MOD_FRONT - 2000, 1000, M['pcb'], bev=0.05)
fingers = [box(f'gold_finger_{k}', -7000 + k * 760, MOD_BACK - 3000, PCB_TOP + 15, 500, 3000, 30, M['copper'], bev=0) for k in range(19)]
dsp = box('dsp', 0, 18000, PCB_TOP + 600, 12000, 12000, 1200, M['ic'], bev=0.05)
dsp_lid = box('dsp_lid', 0, 18000, PCB_TOP + 1300, 9000, 9000, 200, M['shell_end'], bev=0.2)
driver = box('driver_tia', -5200, 2000, PCB_TOP + 400, 3000, 3000, 800, M['ic'], bev=0.05)
laser = box('laser', 4200, 1200, PCB_TOP + 300, 1000, 2000, 600, M['laser'], bev=0.05)
ribbon = box('fiber_ribbon', 375.0, (EDGE - VG_L + MOD_FRONT + 4500) / 2, 0.0, 2400, (EDGE - VG_L) - (MOD_FRONT + 4500), 250, M['ribbon'], bev=0.1)
mpo = box('mpo', 0, MOD_FRONT + 3500, PCB_TOP + 2300, 9000, 5000, 4000, M['mpo'], bev=0.05)
rice = ellipsoid('rice_grain', 1300, 3200, 950, M['rice'], (6000, -6000, PCB_TOP + 950), (0, 0, math.radians(15)))
SHELL_Z = PCB_Z - 1500 + MOD_H / 2
shell = box('module_shell', 0, (MOD_FRONT + MOD_BACK) / 2, SHELL_Z, MOD_W, MOD_BACK - MOD_FRONT, MOD_H, M['shell'], bev=0.04)
shell_front = box('module_front', 0, MOD_FRONT + 1000, SHELL_Z, MOD_W, 2000, MOD_H, M['shell_end'], bev=0.04)
tab = box('pull_tab', 0, MOD_FRONT - 7500, SHELL_Z - 2500, 9000, 15000, 1200, M['tab'], bev=0.2)

# ---------- 交换机（1U，2 排 × 16 个 QSFP-DD）+ 机柜 + 托板 + 手机 ----------
U = 44450.0
FACE_Y = MOD_FRONT + 6000
SW_ZC = SHELL_Z - 9000
SW_W, SW_D = 440000.0, 420000.0
PITCH = 23000.0
OUR_COL = 7                                                                     # 我们的模块在上排中间（第 7 列），画面居中
port_x = lambda col, row: (col - OUR_COL) * PITCH + (PITCH / 2 if row else 0.0)
sw_xc = port_x(7.5, 0)                                                         # 机箱中心：32 个端口都在面板里
sw = [box('sw_face', sw_xc, FACE_Y, SW_ZC, SW_W, 2500, U, M['sw'], bev=0.03),
      box('sw_bottom', sw_xc, FACE_Y + SW_D / 2, SW_ZC - U / 2 + 1000, SW_W, SW_D, 2000, M['sw'], bev=0.1),
      box('sw_cover', sw_xc, FACE_Y + SW_D / 2, SW_ZC + U / 2 - 600, SW_W, SW_D, 1200, M['sw_top'], bev=0),
      box('sw_asic', sw_xc, FACE_Y + 200000, SW_ZC - U / 2 + 4000, 70000, 70000, 4000, M['asic'], bev=0.05)]
leds, others = [], []
for row in range(2):
    for col in range(16):
        x = port_x(col, row); z = SW_ZC + (9000 if row == 0 else -9000)
        sw.append(box(f'cage_{row}_{col}', x, FACE_Y - 1500, z, 21000, 1500, 11000, M['cage'], bev=0.06))
        leds.append(box(f'led_{row}_{col}', x + 8000, FACE_Y - 2400, z + (6200 if row == 0 else -6200), 1500, 400, 900, M['led'], bev=0.1))
        if row == 0 and col == OUR_COL: continue
        others += [box(f'mod_{row}_{col}', x, FACE_Y - 3000, z, MOD_W, 6000, MOD_H, M['shell_end'], bev=0.04),
                   box(f'tab_{row}_{col}', x, FACE_Y - 6000 - 7500, z - 2500, 9000, 15000, 1200, M['tab'], bev=0.2)]
        p0 = Vector((x, FACE_Y - 6000, z))             # 跳线：从模块前端的 MPO 头出来，向下弯进理线
        others.append(tube(f'cord_{row}_{col}', [p0, p0 + Vector((0, -25000, -2000)), p0 + Vector((0, -45000, -30000)), p0 + Vector((0, -50000, -120000))], 1500, M['patch']))
rack = [box('rail_l', sw_xc - SW_W / 2 - 15000, FACE_Y + 5000, SW_ZC, 25000, 30000, 6 * U, M['rack'], bev=0.02),
        box('rail_r', sw_xc + SW_W / 2 + 15000, FACE_Y + 5000, SW_ZC, 25000, 30000, 6 * U, M['rack'], bev=0.02),
        box('device_below', sw_xc, FACE_Y + SW_D / 2, SW_ZC - U, SW_W, SW_D, U - 800, M['other'], bev=0.02),
        box('device_below2', sw_xc, FACE_Y + SW_D / 2, SW_ZC - 2 * U, SW_W, SW_D, U - 800, M['other'], bev=0.02)]
# 上方空 U 位：一条浅托板只在模块左边（不盖住我们的模块），手机横放（长边沿 x），完全在托板上
SHELF_X0, SHELF_X1 = -210000.0, -45000.0
shelf = box('shelf_empty_u', (SHELF_X0 + SHELF_X1) / 2, FACE_Y + 40000, SW_ZC + U / 2 + 1500, SHELF_X1 - SHELF_X0, 80000, 2000, M['shelf'], bev=0.05)
PHONE = Vector((-120000.0, FACE_Y + 40000, SW_ZC + U / 2 + 2500 + 4000))
phone = box('phone', PHONE.x, PHONE.y, PHONE.z, 150000, 71000, 8000, M['phone'], bev=0.12)
phone_scr = box('phone_screen', PHONE.x, PHONE.y, PHONE.z + 4005, 144000, 66000, 20, M['phone_screen'], bev=0)

# ---------- 可见性：每个物体只登记一个区间；淡入淡出用物体颜色 alpha，淡完关渲染 ----------
VIS = {}
def vis(objs, t_in=None, t_out=None, fade=0.4):
    for o in objs if isinstance(objs, (list, tuple)) else [objs]:
        VIS[o.name] = (o, t_in, t_out, fade)
def appear(objs, size, px=1.0, fade=0.5):           # 物体约 px 像素大时开始淡入
    t = t_at_width(size * W / px); vis(objs, t if t > 0.01 else None, None, fade)
appear(wgs + bands + tails, WG_W * 3, 1.0)           # 单根波导太细时，由芯片贴图里的光路代替
appear(sscs + ssc_bands, 8.0, 1.5); appear(electrodes, 10.0, 1.5)
vis(fibers + cores, None, 11.0, 0.5); vis([hair], 7.0, 9.8, 0.4); vis([vg], None, 10.6, 0.5)
vis([clad], 8.0, None, 1.0); vis([rbc], 11.2, 14.8, 0.4)
vis([phone, phone_scr, shelf], None, 4.6, 0.4)
vis(sw + leds + others + rack, None, 4.3, 0.6)
vis([shell, shell_front, tab], None, 5.4, 0.6)
vis([dsp, dsp_lid, driver, laser, mpo, pcb, ribbon] + fingers, None, 9.4, 0.6)
vis([rice], 4.4, 8.0, 0.4)

# ---------- 3D 标签：字保持屏幕大小（反向缩放），尺寸箭头跟着物体真实大小 ----------
FNT = bpy.data.fonts.load(FONT)
LABEL_FRAC = 0.05                                    # 字高约占画面宽的比例（默认 5%，短标签可以更大）
labels = {}
def label(key, text, loc, t_in, t_out, arrow=None, arrow_z=None, frac=LABEL_FRAC):
    t_mid = t_in + 0.3; h0 = frac * view_w(t_mid)
    cu = bpy.data.curves.new('lbl_' + key, 'FONT'); cu.body = text; cu.font = FNT; cu.size = 1.0; cu.align_x = 'CENTER'; cu.extrude = 0.04   # 字号放在物体缩放里（Blender 文字字号上限 10000）
    o = bpy.data.objects.new('lbl_' + key, cu); o.data.materials.append(M['label']); link(o); o.location = loc
    for f in range(max(1, F(t_in) - 1), min(NF, F(t_out if t_out else DUR) + 1) + 1):
        k = h0 * view_w((f - 1) / FPS) / view_w(t_mid); o.scale = (k, k, k); o.keyframe_insert('scale', frame=f)
    vis([o], t_in if t_in > 0 else None, t_out, 0.25); parts = [o]
    if arrow:                                        # 双箭头横跨被量的东西（真实尺寸）
        az = arrow_z if arrow_z is not None else loc[2] - h0 * 0.6; th = arrow * 0.02
        parts.append(box('lbl_' + key + '_shaft', loc[0], loc[1], az, arrow * 0.84, th, th, M['label'], bev=0))
        for sgn in (-1, 1):
            bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=arrow * 0.05, radius2=0, depth=arrow * 0.08); me = bpy.data.meshes.new('tip'); bm.to_mesh(me); bm.free()
            tip = bpy.data.objects.new('lbl_' + key + f'_tip{sgn}', me); tip.data.materials.append(M['label']); link(tip)
            tip.location = (loc[0] + sgn * arrow * 0.46, loc[1], az); tip.rotation_euler = (0, sgn * math.radians(90), 0); parts.append(tip)
        vis(parts[1:], t_in if t_in > 0 else None, t_out, 0.25)
    labels[key] = o; return parts
label('switch', '交换机', (0, FACE_Y - 30000, SW_ZC + 60000), 0.0, 2.2, frac=0.09)
label('module', '光模块 约 9 cm（含拉环）', (0, MOD_FRONT - 4000, SHELL_Z + 16000), 2.4, 4.8, frac=0.055)
label('chip', '硅光芯片 约 5 mm（示例）', (0, -400, 900), 5.0, 7.6, arrow=DIE, arrow_z=300, frac=0.06)
label('fiber', '光纤 125 µm', (-250, EDGE - 250, 260), 7.4, 9.2, arrow=125, arrow_z=90, frac=0.055)
label('hair', '头发 约 0.07–0.08 mm', (420, EDGE - 700, 120), 7.8, 9.4, frac=0.045)
label('rbc', '红细胞 约 7.5 µm', (6.0, FOCUS.y + 5.0, 9.0), 11.8, 14.0, arrow=7.5, arrow_z=5.6, frac=0.055)
label('wg', '不到 0.5 µm', (0.0, FOCUS.y, 0.55), 16.0, None, arrow=WG_W, arrow_z=WG_H + 0.05, frac=0.07)   # 放在焦平面上，不被景深虚掉
for name, (o, t_in, t_out, fade) in VIS.items():
    def key(t, a, hide):
        fr = max(1, F(t)); o.color[3] = a; o.keyframe_insert('color', index=3, frame=fr); o.hide_render = hide; o.keyframe_insert('hide_render', frame=fr)
    if t_in: key(0.0, 0.0, True); key(t_in, 0.0, False); key(t_in + fade, 1.0, False)
    else: key(0.0, 1.0, False)
    if t_out: key(t_out - fade, 1.0, False); key(t_out, 0.0, False); key(t_out + 1 / FPS, 0.0, True)
    for fc in fcurves_of(o):
        if fc.data_path in ('hide_render', 'color'):
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT' if fc.data_path == 'hide_render' else 'LINEAR'

# ---------- 世界缩放（逐帧关键帧）；焦点路径 ----------
CPATH = [(0.0, Vector((sw_xc * 0.35, FACE_Y + 30000, SW_ZC))), (2.0, Vector((-20000, FACE_Y + 15000, SW_ZC + 6000))),
         (4.5, Vector((0, MOD_FRONT + 25000, SHELL_Z))), (7.0, Vector((0, EDGE - 800, 0))), (9.0, Vector((0, EDGE + 100, 0))),
         (11.5, Vector((2.0, FOCUS.y, 1.0))), (18.0, FOCUS)]
def center(t):
    for (t0, c0), (t1, c1) in zip(CPATH, CPATH[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0); u = u * u * (3 - 2 * u); return c0.lerp(c1, u)
    return CPATH[-1][1]
VIEW0 = 3.0
for f in range(1, NF + 1):
    t = (f - 1) / FPS; s = VIEW0 / view_w(t); c = center(t)
    WORLD.scale = (s, s, s); WORLD.location = -c * s
    WORLD.keyframe_insert('scale', frame=f); WORLD.keyframe_insert('location', frame=f)
set_interp(WORLD, 'LINEAR')

# ---------- 相机、灯光、环境 ----------
rig = bpy.data.objects.new('cam_rig', None); sc.collection.objects.link(rig)
bpy.ops.object.camera_add(); cam = bpy.context.object; cam.parent = rig; sc.camera = cam
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.lens = 35
hfov = 2 * math.atan((24 * W / H) / 2 / 35); DIST = (VIEW0 / 2) / math.tan(hfov / 2)
EL = math.radians(26)                                # 俯角放低：看得到远处
cam.location = (0, -DIST * math.cos(EL), DIST * math.sin(EL)); cam.rotation_euler = (math.radians(90) - EL, 0, 0)
cam.data.clip_start = DIST * 0.05; cam.data.clip_end = DIST * 3000
cam.data.dof.use_dof = True; cam.data.dof.focus_distance = DIST
# 场景 1 单位 = 1 µm，但 Blender 按 1 单位 = 1 m 算景深，所以光圈值要很小才有浅景深
for t, fs in ((0.0, 1.2), (4.5, 0.6), (9.0, 0.18), (13.5, 0.08), (18.0, 0.06)):
    cam.data.dof.aperture_fstop = fs; cam.data.dof.keyframe_insert('aperture_fstop', frame=F(t))
rig.rotation_euler = (0, 0, math.radians(-12)); rig.keyframe_insert('rotation_euler', index=2, frame=1)
rig.rotation_euler = (0, 0, math.radians(14)); rig.keyframe_insert('rotation_euler', index=2, frame=NF)
for o in labels.values():
    tc = o.constraints.new('TRACK_TO'); tc.target = cam; tc.track_axis = 'TRACK_Z'; tc.up_axis = 'UP_Y'
def area(name, loc, energy, size, col):
    L = bpy.data.lights.new(name, 'AREA'); L.energy = energy; L.size = size; L.color = col; o = bpy.data.objects.new(name, L); sc.collection.objects.link(o)
    o.parent = rig; o.location = loc; tc = o.constraints.new('TRACK_TO'); tc.target = rig; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'; return o
k2 = DIST ** 2
area('key', (-DIST * 1.2, -DIST * 0.9, DIST * 1.6), 90 * k2, DIST * 1.4, (1.0, 0.95, 0.88))
area('rim', (DIST * 1.4, DIST * 1.3, DIST * 0.7), 70 * k2, DIST * 1.0, (0.60, 0.72, 1.0))
# 环境：HDRI 只用来打光和出反射；相机直接看到的背景是深蓝
wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True; N = wd.node_tree.nodes; L = wd.node_tree.links
for n in list(N): N.remove(n)
out = N.new('ShaderNodeOutputWorld'); bg_hdr = N.new('ShaderNodeBackground'); bg_col = N.new('ShaderNodeBackground'); mx = N.new('ShaderNodeMixShader'); lp = N.new('ShaderNodeLightPath')
bg_col.inputs['Color'].default_value = (0.006, 0.018, 0.07, 1); bg_hdr.inputs['Strength'].default_value = 0.9
if os.path.exists(HDRI):
    env = N.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(HDRI, check_existing=True); L.new(env.outputs['Color'], bg_hdr.inputs['Color'])
else:
    print('没找到 HDRI：', HDRI, '—— 用纯色环境代替'); bg_hdr.inputs['Color'].default_value = (0.5, 0.55, 0.65, 1)
L.new(bg_hdr.outputs[0], mx.inputs[1]); L.new(bg_col.outputs[0], mx.inputs[2]); L.new(lp.outputs['Is Camera Ray'], mx.inputs['Fac']); L.new(mx.outputs[0], out.inputs[0])

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
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.3
sc.view_settings.view_transform = 'AgX'
for lk in ('AgX - Medium High Contrast', 'Medium High Contrast'):
    try: sc.view_settings.look = lk; break
    except Exception: pass
# 合成：只给「光」加辉光（AOV 遮罩 × 自发光层 → 辉光 → 叠加回去）
try:
    vl = sc.view_layers[0]; vl.use_pass_emit = True; aov = vl.aovs.add(); aov.name = 'lightmask'; aov.type = 'VALUE'
    ng = bpy.data.node_groups.new('comp', 'CompositorNodeTree'); sc.compositing_node_group = ng
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new('CompositorNodeRLayers'); rl.scene = sc
    emit = rl.outputs.get('Emit') or rl.outputs.get('Emission'); mask = rl.outputs.get('lightmask')
    print('RLAYER_OUTPUTS', [o.name for o in rl.outputs])
    mul = ng.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1.0
    ng.links.new(emit, mul.inputs['A']); ng.links.new(mask, mul.inputs['B'])
    gl = ng.nodes.new('CompositorNodeGlare'); ng.links.new(mul.outputs['Result'], gl.inputs['Image'])
    for k, v in (('Type', 'Fog Glow'), ('Threshold', 0.0), ('Strength', 0.9), ('Quality', 'High')):
        try: gl.inputs[k].default_value = v
        except Exception as e: print('辉光参数跳过', k, e)
    add = ng.nodes.new('ShaderNodeMix'); add.data_type = 'RGBA'; add.blend_type = 'ADD'; add.inputs['Factor'].default_value = 1.0
    ng.links.new(rl.outputs['Image'], add.inputs['A']); ng.links.new(gl.outputs['Glare'], add.inputs['B'])
    go = ng.nodes.new('NodeGroupOutput'); ng.links.new(add.outputs['Result'], go.inputs[0])
    print('COMPOSITOR 辉光已接上（只作用于光）')
except Exception as e: print('COMPOSITOR 跳过：', e)
set_fmt('PNG'); sc.render.use_overwrite = False; sc.render.use_placeholder = True

# ---------- 每帧锚点（给 2D 合成） ----------
anchors = {}
for f in range(1, NF + 1):
    sc.frame_set(f); fr = {}
    for k, p in (('focus', FOCUS), ('module', Vector((0, MOD_FRONT + 20000, SHELL_Z))), ('chip', Vector((0, 0, 0)))):
        v = world_to_camera_view(sc, cam, WORLD.matrix_world @ p); fr[k] = [round(v.x * W, 1), round((1 - v.y) * H, 1)]
    fr['view_um'] = round(view_w((f - 1) / FPS), 3); anchors[f] = fr
json.dump({'fps': FPS, 'nf': NF, 'w': W, 'frames': anchors}, open(os.path.join(OUT, 'anchors.json'), 'w'))
if VIDEO and not FRAMES:                              # PNG 序列：中途停了可以续渲
    sc.render.filepath = os.path.join(OUT, 'frames', 'f'); bpy.ops.render.render(animation=True)
else:
    sc.render.use_overwrite = True
    for i, f in enumerate(FRAMES or range(1, NF + 1)):
        sc.frame_set(f); sc.render.filepath = os.path.join(OUT, f'f{f:04d}.png'); t0 = time.time(); bpy.ops.render.render(write_still=True)
        print(f'FRAME_TIME 第 {f} 帧：{time.time() - t0:.1f} 秒')
        if i == 0:
            try: import gpu; print('EEVEE_GPU', gpu.platform.vendor_get(), '|', gpu.platform.renderer_get())
            except Exception as e: print('EEVEE_GPU 未知', e)
print('DONE', OUT)
