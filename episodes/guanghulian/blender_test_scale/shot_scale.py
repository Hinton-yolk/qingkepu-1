# 一语道破 · Blender 测试镜头三：光在芯片里走的路有多细？（2026-11-10，按 SHOTPLAN 第四版）
# 竖屏 18 秒，一个连续镜头对数匀速推进：交换机 → 光模块（手机作比例）→ 硅光芯片（米粒）→ 芯片边缘的光纤阵列（头发）
#   → 离边缘约 150 µm 的波导（红细胞）→ 停在「不到 0.5 µm」的波导上。
# 做法：相机不动，整个世界围绕焦点逐帧缩放（单位 µm，按真实尺寸建模，网格直接用真实尺寸，物体缩放 = 1）。
# 默认 EEVEE。用法：
#   blender -b --python-exit-code 1 --python shot_scale.py -- <输出目录> <宽> <高> <采样> [--gpu] [--cycles] [--fps N] [--video] [帧号…]
import bpy, bmesh, math, sys, json, os, random, time
from mathutils import Vector
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
def blended(m):
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'BLENDED'
    return m
def mat(name, col, metal=0.0, rough=0.5, alpha=1.0, coat=0.0, sss=0.0, emit=None, estr=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    b.inputs['Alpha'].default_value = alpha; b.inputs['Coat Weight'].default_value = coat
    if sss: b.inputs['Subsurface Weight'].default_value = sss
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = estr
    return blended(m) if alpha < 1 else m
def mat_emit(name, col, strength, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    for n in list(N): N.remove(n)
    o = N.new('ShaderNodeOutputMaterial'); e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*col, 1); e.inputs['Strength'].default_value = strength
    if alpha < 1:
        tr = N.new('ShaderNodeBsdfTransparent'); mx = N.new('ShaderNodeMixShader'); mx.inputs['Fac'].default_value = alpha
        L.new(tr.outputs[0], mx.inputs[1]); L.new(e.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], o.inputs[0]); blended(m)
    else: L.new(e.outputs[0], o.inputs[0])
    return m
CYAN = (0.25, 0.95, 0.88)
def mat_light_band():
    """光带：均匀青色；13 秒起叠加沿 y 往前走的相位条纹（间距 0.5 µm，每秒走 1 µm）"""
    m = bpy.data.materials.new('light_band'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    for n in list(N): N.remove(n)
    o = N.new('ShaderNodeOutputMaterial'); e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*CYAN, 1)
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])
    off = N.new('ShaderNodeValue'); off.name = 'phase_offset'
    sub = N.new('ShaderNodeMath'); sub.operation = 'ADD'; L.new(sep.outputs['Y'], sub.inputs[0]); L.new(off.outputs[0], sub.inputs[1])
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 2 * math.pi / 0.5; L.new(sub.outputs[0], mul.inputs[0])
    sn = N.new('ShaderNodeMath'); sn.operation = 'SINE'; L.new(mul.outputs[0], sn.inputs[0])
    amp = N.new('ShaderNodeValue'); amp.name = 'stripe_amp'
    a1 = N.new('ShaderNodeMath'); a1.operation = 'MULTIPLY'; L.new(sn.outputs[0], a1.inputs[0]); L.new(amp.outputs[0], a1.inputs[1])
    a2 = N.new('ShaderNodeMath'); a2.operation = 'ADD'; a2.inputs[1].default_value = 1.0; L.new(a1.outputs[0], a2.inputs[0])
    st = N.new('ShaderNodeMath'); st.operation = 'MULTIPLY'; st.inputs[1].default_value = 3.2; L.new(a2.outputs[0], st.inputs[0])
    L.new(st.outputs[0], e.inputs['Strength']); L.new(e.outputs[0], o.inputs[0])
    for fr, v in ((1, 0.0), (NF, (NF - 1) / FPS * 1.0)): off.outputs[0].default_value = -v; off.outputs[0].keyframe_insert('default_value', frame=fr)
    for fr, v in ((1, 0.0), (F(12.6), 0.0), (F(13.4), 0.35), (NF, 0.35)): amp.outputs[0].default_value = v; amp.outputs[0].keyframe_insert('default_value', frame=fr)
    set_interp(m.node_tree, 'LINEAR'); return m
M = dict(
    box=mat('box_oxide_surface', (0.02, 0.07, 0.24), 0.0, 0.35, coat=0.6),          # 芯片表面（埋氧层顶面）：深蓝
    clad=mat('upper_cladding_glass', (0.55, 0.65, 0.85), 0.0, 0.15, alpha=0.035),   # 上包层：几乎透明，只留一层淡玻璃面
    si=mat('si_device', (0.16, 0.22, 0.34), 0.5, 0.3),
    si_wg=mat('si_waveguide_clear', (0.35, 0.45, 0.60), 0.0, 0.15, alpha=0.30),     # 亮着的波导：硅画成半透明，看得见芯区里的光（示意）
    si_side=mat('si_die_side', (0.08, 0.09, 0.12), 0.6, 0.35),
    gold=mat('gold_electrode', (0.95, 0.68, 0.25), 1.0, 0.25),
    light=mat_light_band(),
    tail=mat_emit('evanescent_tail', CYAN, 0.8, alpha=0.08),                         # 倏逝尾：很淡
    glass=mat('fiber_glass', (0.78, 0.86, 0.95), 0.0, 0.05, alpha=0.28, coat=1.0),
    vgroove=mat('v_groove_block', (0.20, 0.22, 0.26), 0.4, 0.4),
    cover=mat('v_groove_cover', (0.75, 0.85, 0.95), 0.0, 0.1, alpha=0.06),
    ssc=mat('ssc_block', (0.45, 0.55, 0.75), 0.0, 0.2, alpha=0.45),
    rbc=mat('red_blood_cell', (0.28, 0.06, 0.07), 0.0, 0.5, sss=0.1),              # 低饱和暗红，不像珊瑚
    hair=mat('hair', (0.09, 0.06, 0.05), 0.0, 0.35, coat=0.6),
    rice=mat('rice', (0.92, 0.90, 0.84), 0.0, 0.35, sss=0.5),
    pcb=mat('module_pcb', (0.04, 0.12, 0.16), 0.0, 0.5, coat=0.3),
    ic=mat('ic_package', (0.06, 0.06, 0.07), 0.2, 0.45),
    laser=mat('laser_chip', (0.35, 0.36, 0.40), 0.6, 0.3),
    ribbon=mat('fiber_ribbon', (0.55, 0.56, 0.58), 0.0, 0.5),                        # 光纤带：中性灰
    mpo=mat('mpo', (0.30, 0.31, 0.33), 0.0, 0.45),
    shell=mat('module_shell', (0.72, 0.74, 0.78), 1.0, 0.3, alpha=0.22),
    shell_end=mat('module_front', (0.66, 0.68, 0.72), 1.0, 0.35),
    tab=mat('pull_tab', (0.12, 0.12, 0.13), 0.0, 0.5),                              # 拉环：黑（不用蓝）
    sw=mat('switch_metal', (0.08, 0.09, 0.11), 0.6, 0.4),
    sw_top=mat('switch_cover', (0.10, 0.11, 0.13), 0.0, 0.3, alpha=0.05),
    asic=mat('switch_asic_dim', (0.05, 0.05, 0.06), 0.3, 0.5),
    cage=mat('port_cage', (0.55, 0.57, 0.60), 1.0, 0.35),
    led=mat_emit('led_green', (0.2, 1.0, 0.25), 6.0),
    rack=mat('rack_rail', (0.12, 0.13, 0.15), 0.7, 0.4),
    other=mat('other_device', (0.05, 0.055, 0.065), 0.5, 0.45),
    patch=mat('patch_cord', (0.45, 0.46, 0.48), 0.0, 0.55),
    phone=mat('phone_body', (0.18, 0.18, 0.20), 0.8, 0.3),
    phone_screen=mat('phone_screen_off', (0.01, 0.01, 0.012), 0.0, 0.08, coat=1.0),
    shelf=mat('shelf', (0.14, 0.15, 0.17), 0.6, 0.45),
    label=mat_emit('label_white', (1.0, 1.0, 1.0), 2.2),
)

# ---------- 几何工具（单位 µm，网格按真实尺寸，物体缩放 = 1） ----------
WORLD = bpy.data.objects.new('WORLD', None); sc.collection.objects.link(WORLD)
def link(o): sc.collection.objects.link(o); o.parent = WORLD; return o
def box(name, cx, cy, cz, sx, sy, sz, m):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = (cx, cy, cz); o.data.materials.append(m); return link(o)
def cyl(name, r, depth, m, loc, rot=(0, 0, 0), verts=40):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=depth); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; o.rotation_euler = rot; o.data.materials.append(m); return link(o)
def ellipsoid(name, rx, ry, rz, m, loc, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=20, radius=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * rx, v.co.y * ry, v.co.z * rz))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; o.rotation_euler = rot; o.data.materials.append(m); return link(o)
def torus(name, R, r, m, loc, zscale=1.0):
    bm = bmesh.new(); seg, ring = 64, 14
    vv = [[bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), zscale * r * math.sin(b))) for b in [2 * math.pi * j / ring for j in range(ring)]] for a in [2 * math.pi * i / seg for i in range(seg)]]
    for i in range(seg):
        for j in range(ring): bm.faces.new([vv[i][j], vv[(i + 1) % seg][j], vv[(i + 1) % seg][(j + 1) % ring], vv[i][(j + 1) % ring]])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; o.data.materials.append(m); return link(o)
VIS = []                                           # (物体, 出现秒, 消失秒)
def visible(objs, t_on=None, t_off=None):
    for o in objs if isinstance(objs, (list, tuple)) else [objs]: VIS.append((o, t_on, t_off))

# ---------- 芯片（5 mm 示例），表面 z = 0，前边缘 y = −2500 ----------
DIE = 5000.0; EDGE = -DIE / 2
WG_W, WG_H = 0.40, 0.22
FOCUS = Vector((0.0, EDGE + 150.0, WG_H / 2))     # 最终焦点：离边缘约 150 µm 的波导
die_top = box('die_surface', 0, 0, -0.01, DIE, DIE, 0.02, M['box'])
die_body = box('die_body', 0, 0, -375.0, DIE, DIE, 749.0, M['si_side'])
clad = box('upper_cladding', 0, EDGE + 400, 1.25, 1600, 800, 2.5, M['clad'])   # 只在焦点附近画一块淡玻璃面（远处看不出）
SSC_L = 100.0                                       # 模斑转换器长度（示意，取倒锥长度范围的下限，焦点在它后面 50 µm）
wg_main = box('target_waveguide', 0, EDGE + SSC_L + 600, WG_H / 2, WG_W, 1200, WG_H, M['si_wg'])     # 从模斑转换器往里走
band = box('light_band_main', 0, EDGE + SSC_L + 600, WG_H / 2, WG_W * 0.65, 1200, WG_H * 0.6, M['light'])
tail = box('evanescent_tail', 0, EDGE + SSC_L + 600, WG_H / 2, WG_W * 2.2, 1200, WG_H * 1.8, M['tail'])
# 每根光纤对面一个模斑转换器（示意方块）和一条亮着的波导
FX = [250.0 * (i - 3) for i in range(8)]          # 光纤 x 位置（含 x = 0）
ssc_blocks, other_wg = [], []
for i, x in enumerate(FX):
    ssc_blocks.append(box(f'ssc_{i}', x, EDGE + SSC_L / 2, 1.5, 8.0, SSC_L, 3.0, M['ssc']))
    if x != 0:
        other_wg.append(box(f'wg_{i}', x, EDGE + SSC_L + 600, WG_H / 2, WG_W, 1200, WG_H, M['si_wg']))
        other_wg.append(box(f'band_{i}', x, EDGE + SSC_L + 600, WG_H / 2, WG_W * 0.65, 1200, WG_H * 0.6, M['light']))
# 调制器金电极（MZM，示例），沿波导两侧
electrodes = []
for i, x in enumerate(FX):
    for sgn in (-1, 1): electrodes.append(box(f'mzm_{i}_{sgn}', x + sgn * 9.0, EDGE + SSC_L + 950, 1.2, 10.0, 600, 2.4, M['gold']))
# 稀疏版图（示例）：芯片上其它地方的波导、电极、焊盘
rnd = random.Random(20261110); layout = []
for k in range(220):
    x, y = rnd.uniform(-DIE / 2 + 100, DIE / 2 - 100), rnd.uniform(EDGE + 1600, DIE / 2 - 100)
    r = rnd.random()
    if r < 0.45: layout.append(box(f'far_wg_{k}', x, y, WG_H / 2, 3.0, rnd.uniform(200, 900), WG_H, M['si']))     # 远处画粗一点，免得缩成闪烁的细线
    elif r < 0.6: layout.append(box(f'far_wg_h_{k}', x, y, WG_H / 2, rnd.uniform(200, 900), 3.0, WG_H, M['si']))
    elif r < 0.85: layout.append(box(f'far_mzm_{k}', x, y, 1.2, 30, rnd.uniform(600, 1500), 2.4, M['gold']))
    else: layout.append(box(f'pad_{k}', x, y, 1.5, 80, 80, 3.0, M['gold']))
for k in range(30): layout.append(box(f'edge_pad_{k}', -DIE / 2 + 200 + k * 150, DIE / 2 - 150, 1.5, 90, 90, 3.0, M['gold']))

# ---------- 芯片边缘的光纤阵列（端面耦合，光纤沿 −y 躺在 V 形槽里） ----------
FIB_L = 30000.0
vg = box('v_groove_block', 375.0, EDGE - 2000, -400.0, 2600, 4000, 700, M['vgroove'])
cover = box('v_groove_cover', 375.0, EDGE - 2000, 140.0, 2600, 4000, 300, M['cover'])
fibers, cores = [], []
for i, x in enumerate(FX):
    fibers.append(cyl(f'fiber_{i}', 62.5, FIB_L, M['glass'], (x, EDGE - FIB_L / 2 - 5, 0.0), (math.radians(90), 0, 0)))
    cores.append(cyl(f'fiber_core_{i}', 4.1, FIB_L, M['light'], (x, EDGE - FIB_L / 2 - 5, 0.0), (math.radians(90), 0, 0), verts=16))
hair = cyl('human_hair', 37.5, 3000.0, M['hair'], (300.0, EDGE - 450, 62.5 + 37.5), (0, math.radians(90), math.radians(8)), verts=24)   # 搭在光纤上
# 红细胞：放在上包层顶面（z = 2.5），波导旁边
rbc = torus('red_blood_cell', 2.6, 1.1, M['rbc'], (5.5, FOCUS.y + 3.0, 2.5 + 0.9), zscale=0.8)
rbc_mid = ellipsoid('rbc_center', 1.7, 1.7, 0.4, M['rbc'], (5.5, FOCUS.y + 3.0, 2.5 + 0.7))

# ---------- 光模块（QSFP-DD：宽 18.35 mm、高 8.5 mm、本体约 78 mm + 拉环），芯片在模块里 ----------
MOD_W, MOD_H = 18350.0, 8500.0
MOD_FRONT, MOD_BACK = -40000.0, 38000.0
PCB_Z = -750.0 - 500.0
pcb = box('module_pcb', 0, (MOD_FRONT + MOD_BACK) / 2, PCB_Z, MOD_W - 1200, MOD_BACK - MOD_FRONT - 2000, 1000, M['pcb'])
dsp = box('dsp', 0, 18000, PCB_Z + 500 + 600, 12000, 12000, 1200, M['ic'])
driver = box('driver_tia', -5200, 2000, PCB_Z + 500 + 400, 3000, 3000, 800, M['ic'])
laser = box('laser', 4200, 1200, PCB_Z + 500 + 300, 1000, 2000, 600, M['laser'])
ribbon = box('fiber_ribbon', 375.0, (EDGE - 4000 + MOD_FRONT + 4000) / 2, -300.0, 2400, (EDGE - 4000) - (MOD_FRONT + 4000), 300, M['ribbon'])
mpo = box('mpo', 0, MOD_FRONT + 2500, PCB_Z + 2500, 9000, 5000, 4500, M['mpo'])
rice = ellipsoid('rice_grain', 1300, 3200, 950, M['rice'], (6000, -6000, PCB_Z + 500 + 950), (0, 0, math.radians(15)))
SHELL_Z = PCB_Z - 1500 + MOD_H / 2
shell = box('module_shell', 0, (MOD_FRONT + MOD_BACK) / 2, SHELL_Z, MOD_W, MOD_BACK - MOD_FRONT, MOD_H, M['shell'])
shell_front = box('module_front', 0, MOD_FRONT + 1500, SHELL_Z, MOD_W, 3000, MOD_H, M['shell_end'])
tab = box('pull_tab', 0, MOD_FRONT - 7500, SHELL_Z - 2500, 9000, 15000, 1200, M['tab'])

# ---------- 交换机（1U，32 个 QSFP-DD 端口两排）+ 机柜环境 + 手机 ----------
U = 44450.0
FACE_Y = MOD_FRONT + 6000                          # 模块前端伸出面板约 6 mm
SW_ZC = SHELL_Z - 9000                              # 我们的模块在上排
SW_W, SW_D = 440000.0, 420000.0
sw_x0 = -SW_W / 2 + 40000                           # 让我们的模块在面板偏左
sw = [box('sw_face', sw_x0, FACE_Y, SW_ZC, SW_W, 2500, U, M['sw']),
      box('sw_bottom', sw_x0, FACE_Y + SW_D / 2, SW_ZC - U / 2 + 1000, SW_W, SW_D, 2000, M['sw']),
      box('sw_cover', sw_x0, FACE_Y + SW_D / 2, SW_ZC + U / 2 - 600, SW_W, SW_D, 1200, M['sw_top']),
      box('sw_asic', sw_x0 + 60000, FACE_Y + 200000, SW_ZC - U / 2 + 4000, 70000, 70000, 4000, M['asic'])]
leds, others = [], []
for row in range(2):
    for col in range(16):
        x = col * 23000.0 + (11500.0 if row else 0.0); z = SW_ZC + (9000 if row == 0 else -9000)
        sw.append(box(f'cage_{row}_{col}', x, FACE_Y - 1500, z, 21000, 1500, 11000, M['cage']))
        leds.append(box(f'led_{row}_{col}', x + 8000, FACE_Y - 2400, z + (6200 if row == 0 else -6200), 1500, 400, 900, M['led']))
        if row == 0 and col == 0: continue
        others += [box(f'mod_{row}_{col}', x, FACE_Y - 3000, z, MOD_W, 6000, MOD_H, M['shell_end']),
                   box(f'tab_{row}_{col}', x, FACE_Y - 6000 - 7500, z - 2500, 9000, 15000, 1200, M['tab']),
                   box(f'cord_{row}_{col}', x, FACE_Y - 9000 - 60000, z - 1000 - 30000, 3000, 120000, 3000, M['patch'])]
rack = [box('rail_l', sw_x0 - SW_W / 2 - 15000, FACE_Y + 5000, SW_ZC, 25000, 30000, 6 * U, M['rack']),
        box('rail_r', sw_x0 + SW_W / 2 + 15000, FACE_Y + 5000, SW_ZC, 25000, 30000, 6 * U, M['rack']),
        box('device_below', sw_x0, FACE_Y + SW_D / 2, SW_ZC - U, SW_W, SW_D, U - 800, M['other']),
        box('device_below2', sw_x0, FACE_Y + SW_D / 2, SW_ZC - 2 * U, SW_W, SW_D, U - 800, M['other']),
        box('device_above2', sw_x0, FACE_Y + SW_D / 2, SW_ZC + 2 * U, SW_W, SW_D, U - 800, M['other'])]
shelf = box('shelf_empty_u', sw_x0, FACE_Y + 40000, SW_ZC + U / 2 + 1500, SW_W, 80000, 2000, M['shelf'])   # 上方空 U 位的一条浅托板
PHONE = Vector((-62000.0, FACE_Y + 70000, SW_ZC + U / 2 + 2500 + 4000))
phone = box('phone', PHONE.x, PHONE.y, PHONE.z, 71000, 150000, 8000, M['phone'])
phone_scr = box('phone_screen', PHONE.x, PHONE.y, PHONE.z + 4010, 66000, 144000, 20, M['phone_screen'])

# ---------- 3D 标签（白色立体字；尺寸类配双箭头），朝向相机 ----------
FNT = bpy.data.fonts.load(FONT)
def label(name, text, size, loc, arrow=None):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = text; cu.font = FNT; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = size * 0.05
    o = bpy.data.objects.new(name, cu); o.data.materials.append(M['label']); link(o); o.location = loc; parts = [o]
    if arrow:
        parts.append(box(name + '_shaft', loc[0], loc[1], loc[2] - size * 0.5, arrow * 0.84, size * 0.05, size * 0.05, M['label']))
        for sgn in (-1, 1):
            bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=size * 0.14, radius2=0, depth=arrow * 0.08); me = bpy.data.meshes.new(name + '_tip'); bm.to_mesh(me); bm.free()
            tip = bpy.data.objects.new(name + f'_tip{sgn}', me); tip.data.materials.append(M['label']); link(tip)
            tip.location = (loc[0] + sgn * arrow * 0.46, loc[1], loc[2] - size * 0.5); tip.rotation_euler = (0, sgn * math.radians(90), 0); parts.append(tip)
    return parts
LB = dict(
    switch=(label('lbl_switch', '交换机', 26000, (sw_x0, FACE_Y - 30000, SW_ZC + 60000)), 0.0, 2.2),
    module=(label('lbl_module', '光模块 约 9 cm（含拉环）', 7000, (0, MOD_FRONT + 20000, SHELL_Z + 16000)), 2.4, 4.8),
    chip=(label('lbl_chip', '硅光芯片 约 5 mm（示例）', 600, (0, 0, 1500), arrow=DIE), 5.0, 7.6),
    fiber=(label('lbl_fiber', '光纤 125 µm', 45, (-250, EDGE - 300, 260), arrow=125), 7.4, 9.2),
    hair=(label('lbl_hair', '头发 约 0.07–0.08 mm（因人而异）', 50, (300, EDGE - 450, 330)), 7.8, 9.4),
    rbc=(label('lbl_rbc', '红细胞 约 7.5 µm', 1.5, (5.5, FOCUS.y + 3.0, 7.5), arrow=7.5), 11.8, 14.0),
    wg=(label('lbl_wg', '不到 0.5 µm', 0.28, (0.0, FOCUS.y + 0.6, 1.0), arrow=WG_W), 16.0, None),
)
for key, (parts, t_on, t_off) in LB.items(): visible(parts, t_on, t_off)

# ---------- 尺度时间线：画面宽度（µm）的 log10 对时间分段线性 ----------
KEYS = [(0.0, 600000.0), (2.0, 400000.0), (4.5, 120000.0), (7.0, 12000.0), (9.0, 1000.0), (11.5, 100.0), (13.5, 25.0), (16.0, 4.0), (18.0, 3.0)]
def log_width(t):
    for (t0, w0), (t1, w1) in zip(KEYS, KEYS[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            if t1 == KEYS[-1][0]: u = 1 - (1 - u) ** 2                          # 最后一段减速落地
            return math.log10(w0) + u * (math.log10(w1) - math.log10(w0))
    return math.log10(KEYS[-1][1])
# 焦点路径（世界坐标 µm）。平移按当时画面宽度换算：用 log 宽度做插值参数，避免大尺度时的小平移被放大成抖动
CPATH = [(0.0, Vector((sw_x0 + 20000, FACE_Y + 30000, SW_ZC))), (2.0, Vector((-15000, FACE_Y + 15000, SW_ZC + 4000))),
         (4.5, Vector((0, MOD_FRONT + 25000, SHELL_Z))), (7.0, Vector((0, EDGE - 800, 0))), (9.0, Vector((0, EDGE + 100, 0))),
         (11.5, Vector((2.0, FOCUS.y, 1.0))), (18.0, FOCUS)]
def center(t):
    for (t0, c0), (t1, c1) in zip(CPATH, CPATH[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0); u = u * u * (3 - 2 * u); return c0.lerp(c1, u)
    return CPATH[-1][1]
VIEW0 = 3.0                                         # 世界缩放 1 时的画面宽度（µm）
for f in range(1, NF + 1):
    t = (f - 1) / FPS; s = VIEW0 / (10 ** log_width(t)); c = center(t)
    WORLD.scale = (s, s, s); WORLD.location = -c * s
    WORLD.keyframe_insert('scale', frame=f); WORLD.keyframe_insert('location', frame=f)
set_interp(WORLD, 'LINEAR')
def t_at_width(w):
    """画面宽度第一次小于等于 w µm 的时刻（推进）"""
    for f in range(1, NF + 1):
        if 10 ** log_width((f - 1) / FPS) <= w: return (f - 1) / FPS
    return DUR

# ---------- 可见性：大物体在相机穿过前隐藏；小物体在大于约 1 像素后才出现 ----------
PX = 1080.0
def appear_when(objs, size):                        # 画面宽度 ≤ size × 像素数 时（≥ 1 像素）才渲染
    visible(objs, t_at_width(size * PX))
appear_when([wg_main, band, tail], WG_W); appear_when(other_wg, WG_W)
appear_when([rbc, rbc_mid], 7.5); appear_when([clad], 2.5)
appear_when(ssc_blocks, 8.0); appear_when(electrodes, 10.0); appear_when(cores, 8.2)
appear_when(fibers + [hair], 75.0); appear_when(layout, 3.0)
visible([phone, phone_scr, shelf], None, 4.9)                    # 托板和手机一起在 5 秒前退场
visible(sw + leds + others + rack, None, 4.4)                    # 相机越过面板前隐藏交换机
visible([shell, shell_front, tab], None, 5.2)                    # 模块外壳在镜头钻进去前隐藏
visible([dsp, driver, laser, mpo, pcb, ribbon], None, 9.5)
visible([rice], None, 8.0)
visible([vg, cover], None, 11.5)
visible([fibers[i] for i in range(8)] + cores + [hair], None, 11.5)
for o, t_on, t_off in VIS:
    o.hide_render = t_on is not None and t_on > 0; o.keyframe_insert('hide_render', frame=1)
    if t_on: o.hide_render = False; o.keyframe_insert('hide_render', frame=F(t_on))
    if t_off: o.hide_render = True; o.keyframe_insert('hide_render', frame=F(t_off))
    set_interp(o, 'CONSTANT')

# ---------- 相机（不动，绕焦点慢转）、灯（挂在相机组下，不随世界缩放） ----------
rig = bpy.data.objects.new('cam_rig', None); sc.collection.objects.link(rig)
bpy.ops.object.camera_add(); cam = bpy.context.object; cam.parent = rig; sc.camera = cam
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.lens = 35
hfov = 2 * math.atan((24 * W / H) / 2 / 35); DIST = (VIEW0 / 2) / math.tan(hfov / 2)
EL = math.radians(35)
cam.location = (0, -DIST * math.cos(EL), DIST * math.sin(EL)); cam.rotation_euler = (math.radians(90) - EL, 0, 0)
cam.data.clip_start = DIST * 0.05; cam.data.clip_end = DIST * 2000
cam.data.dof.use_dof = True; cam.data.dof.focus_distance = DIST
for t, fs in ((0.0, 8.0), (4.5, 5.6), (9.0, 2.8), (13.5, 1.6), (18.0, 1.4)):
    cam.data.dof.aperture_fstop = fs; cam.data.dof.keyframe_insert('aperture_fstop', frame=F(t))
rig.rotation_euler = (0, 0, math.radians(-12)); rig.keyframe_insert('rotation_euler', index=2, frame=1)
rig.rotation_euler = (0, 0, math.radians(16)); rig.keyframe_insert('rotation_euler', index=2, frame=NF)
for parts, _, _ in LB.values():
    tc = parts[0].constraints.new('TRACK_TO'); tc.target = cam; tc.track_axis = 'TRACK_Z'; tc.up_axis = 'UP_Y'
def area(name, loc, energy, size, col):
    L = bpy.data.lights.new(name, 'AREA'); L.energy = energy; L.size = size; L.color = col; o = bpy.data.objects.new(name, L); sc.collection.objects.link(o)
    o.parent = rig; o.location = loc; tc = o.constraints.new('TRACK_TO'); tc.target = rig; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'; return o
k2 = DIST ** 2
area('key', (-DIST * 1.2, -DIST * 0.9, DIST * 1.6), 160 * k2, DIST * 1.2, (1.0, 0.95, 0.88))
area('rim', (DIST * 1.4, DIST * 1.3, DIST * 0.7), 110 * k2, DIST * 1.0, (0.60, 0.72, 1.0))
area('fill', (0, -DIST * 1.6, DIST * 0.4), 35 * k2, DIST * 2.0, (0.75, 0.82, 1.0))
wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True
bg = wd.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.006, 0.020, 0.075, 1); bg.inputs['Strength'].default_value = 1.0

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
set_fmt('PNG')

# ---------- 每帧锚点（给 2D 合成） ----------
anchors = {}
for f in range(1, NF + 1):
    sc.frame_set(f); fr = {}
    for k, p in (('focus', FOCUS), ('module', Vector((0, MOD_FRONT + 20000, SHELL_Z))), ('chip', Vector((0, 0, 0)))):
        v = world_to_camera_view(sc, cam, WORLD.matrix_world @ p); fr[k] = [round(v.x * W, 1), round((1 - v.y) * H, 1)]
    fr['view_um'] = round(10 ** log_width((f - 1) / FPS), 3); anchors[f] = fr
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
