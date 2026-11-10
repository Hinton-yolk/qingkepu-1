# 光互连 02 下集 · 新画面版 · 开头镜头（草稿）
# A 段（y1，约 2.4 秒）：桌上的手机，消息 1 秒内变乱码；一个发光的信号从手机飞出去（往右上），镜头甩上去。
# B 段（y2，约 4 秒）：信号从左下飞进画面（同一运动方向），落进 AI 服务器电路板上的一对差分走线（盖在阻焊下），
#      镜头贴着板面滑过去，停在纸片立牌主持人（蹲着看）身边。
# 单位：毫米（scale_length = 0.001，景深按真实光圈算）。
# 用法：blender -b --python shot_open.py -- <A|B> <输出目录> <宽> <高> <采样> [cycles] [view=… pose=… bits=…] [帧号…]
#   view=…：B 场景的固定机位静帧，给中间讲解段（2.5D）当背景
#   云端草稿用 cycles（云端没有 EEVEE 要的 libEGL）；用户电脑上用 EEVEE。
import bpy, bmesh, math, os, sys, random
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
SHOT, OUT, W, H, SAMP = args[0], args[1], int(args[2]), int(args[3]), int(args[4]); rest = args[5:]
CYCLES = 'cycles' in rest; FRAMES = [int(a) for a in rest if a.isdigit()]
OPT = dict(a.split('=', 1) for a in rest if '=' in a)   # 2.5D 静帧：view=side|rx|wide|close  pose=A|B  bits=偏移
FPS = 30; DUR = {'A': 2.4, 'B': 4.0}[SHOT]; NF = round(DUR * FPS); F = lambda s: 1 + round(s * FPS)
HERE = os.path.dirname(os.path.abspath(__file__)); AS = os.path.join(HERE, 'assets'); HDRI = os.path.join(HERE, 'assets_dl', 'studio_small_09_2k.hdr')
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; os.makedirs(OUT, exist_ok=True)
sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
random.seed(11)

# ---------- 材质 ----------
def mat(name, col, metal=0.0, rough=0.5, coat=0.0, noise_bump=0.0, noise_scale=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat
    if noise_bump:
        nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = noise_scale; nz.inputs['Detail'].default_value = 6
        bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = noise_bump; L.new(nz.outputs['Fac'], bp.inputs['Height']); L.new(bp.outputs[0], b.inputs['Normal'])
    return m
def emit(name, col, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    for n in list(N): N.remove(n)
    o = N.new('ShaderNodeOutputMaterial'); e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*col, 1); e.inputs['Strength'].default_value = strength
    L.new(e.outputs[0], o.inputs[0]); return m, e
def img(N, path, cs='sRGB'):
    t = N.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path, check_existing=True); t.image.colorspace_settings.name = cs; return t
def mat_wood():
    m = mat('desk_wood', (0.3, 0.17, 0.08), 0.0, 0.42, coat=0.25); N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.02, 0.0025, 0.02); L.new(tc.outputs['Object'], mp.inputs[0])
    wv = N.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 1.6; wv.inputs['Distortion'].default_value = 11; wv.inputs['Detail'].default_value = 6; wv.inputs['Detail Scale'].default_value = 2.0; L.new(mp.outputs[0], wv.inputs[0])
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = (0.26, 0.14, 0.065, 1); cr.color_ramp.elements[1].color = (0.38, 0.22, 0.11, 1)
    L.new(wv.outputs['Fac'], cr.inputs[0]); L.new(cr.outputs[0], b.inputs['Base Color']); return m
def mat_screen():
    """手机屏幕：聊天界面自发光；正常 → 乱码（Mix 系数做关键帧）"""
    m = mat('phone_screen', (0.0, 0.0, 0.0), 0.0, 0.04, coat=1.0); N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    a = img(N, os.path.join(AS, 'screen_ok.png')); c = img(N, os.path.join(AS, 'screen_bad.png'))
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.name = 'garble'; L.new(a.outputs['Color'], mx.inputs['A']); L.new(c.outputs['Color'], mx.inputs['B'])
    L.new(mx.outputs['Result'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 2.4
    fac = mx.inputs['Factor']
    for t, v in ((0.0, 0.0), (0.85, 0.0), (1.05, 1.0)): fac.default_value = v; fac.keyframe_insert('default_value', frame=F(t))
    return m
def mat_standee(k):
    m = bpy.data.materials.new('standee_' + k); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    t = img(N, os.path.join(AS, f'standee_{k}.png')); L.new(t.outputs['Color'], b.inputs['Base Color']); L.new(t.outputs['Alpha'], b.inputs['Alpha'])
    b.inputs['Roughness'].default_value = 0.8
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'DITHERED'
    return m, t.image.size[:]
def mat_signal():
    """走线上的信号：按电平画（高 = 亮、低 = 暗），相邻同电平连成一片；比特串贴图沿 y 往芯片方向走"""
    m, e = emit('signal_band', (1.0, 0.58, 0.12), 1.0); N = m.node_tree.nodes; L = m.node_tree.links
    tc = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sp.inputs[0])
    off = N.new('ShaderNodeValue'); off.name = 'offset'
    u = N.new('ShaderNodeMath'); u.operation = 'MULTIPLY_ADD'; u.inputs[1].default_value = 1 / 80.0; L.new(sp.outputs['Y'], u.inputs[0]); L.new(off.outputs[0], u.inputs[2])
    cm = N.new('ShaderNodeCombineXYZ'); L.new(u.outputs[0], cm.inputs['X']); cm.inputs['Y'].default_value = 0.5
    t = img(N, os.path.join(AS, 'bits.png'), 'Non-Color'); t.interpolation = 'Linear'; L.new(cm.outputs[0], t.inputs[0])
    st = N.new('ShaderNodeMath'); st.operation = 'MULTIPLY'; st.inputs[1].default_value = 2.4; L.new(t.outputs['Color'], st.inputs[0]); L.new(st.outputs[0], e.inputs['Strength'])
    for fr, v in ((1, 0.0), (NF, -DUR * 0.10)): off.outputs[0].default_value = v; off.outputs[0].keyframe_insert('default_value', frame=fr)
    for fc in (m.node_tree.animation_data.action.fcurves if hasattr(m.node_tree.animation_data.action, 'fcurves') else []):
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    return m

# ---------- 几何 ----------
def obj(name, me, m=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    o = bpy.data.objects.new(name, me); o.location = loc; o.rotation_euler = rot
    if m: o.data.materials.append(m)
    sc.collection.objects.link(o); return o
def box(name, sx, sy, sz, m, loc, rot=(0, 0, 0), bev=0.0, seg=3):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = obj(name, me, m, loc, rot)
    if bev:
        md = o.modifiers.new('bev', 'BEVEL'); md.width = bev; md.segments = seg
        for p in o.data.polygons: p.use_smooth = True
    return o
def boxes(name, specs, m):
    """很多小方块合成一个网格（省物体数）：specs = (cx, cy, cz, sx, sy, sz)"""
    bm = bmesh.new()
    for cx, cy, cz, sx, sy, sz in specs:
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r['verts']: v.co = Vector((cx + v.co.x * sx, cy + v.co.y * sy, cz + v.co.z * sz))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); return obj(name, me, m)
def sphere(name, r, m, loc):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=r); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return obj(name, me, m, loc)
def plane(name, sx, sy, m, loc, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, 0))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    me.uv_layers.new(name='UVMap')
    for lp in me.loops: v = me.vertices[lp.vertex_index].co; me.uv_layers[0].data[lp.index].uv = (v.x / sx + 0.5, v.y / sy + 0.5)
    return obj(name, me, m, loc, rot)
def standee(k, height, loc, yaw):
    """纸片立牌：竖着的一张纸（带白纸边），底下一小条折出来的纸脚"""
    m, (iw, ih) = mat_standee(k); w = height * iw / ih
    p = plane('standee_' + k, w, height, m, (loc[0], loc[1], loc[2] + height / 2), (math.radians(90), 0, yaw))
    box('standee_foot_' + k, w * 0.5, height * 0.12, height * 0.006, mat('paper', (0.92, 0.9, 0.85), 0, 0.8),
        (loc[0] - math.sin(yaw) * height * 0.04, loc[1] + math.cos(yaw) * height * 0.04, loc[2] + height * 0.003), (0, 0, yaw))
    return p
def bokeh_lights(n, center, spread, size, cols):
    for i in range(n):
        c = random.choice(cols); m, _ = emit(f'bk{i}', c, random.uniform(4, 12))
        sphere(f'bk{i}', size * random.uniform(0.6, 1.4), m, (center[0] + random.uniform(-spread[0], spread[0]), center[1] + random.uniform(-spread[1], spread[1]), center[2] + random.uniform(-spread[2], spread[2])))
def key(o, path, fr, val):
    setattr(o, path, val); o.keyframe_insert(path, frame=fr)

# ---------- 场景 ----------
cam_d = bpy.data.cameras.new('cam'); cam = obj('cam', cam_d); sc.camera = cam
cam_d.sensor_width = 36; cam_d.clip_start = 0.05; cam_d.clip_end = 20000; cam_d.dof.use_dof = True
tgt = bpy.data.objects.new('target', None); sc.collection.objects.link(tgt)
tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
cam_d.dof.focus_object = tgt

if SHOT == 'A':
    plane('desk', 1600, 1600, mat_wood(), (0, 0, 0))
    ph_rot = math.radians(-18)
    body = box('phone_body', 71.5, 150, 7.8, mat('phone_frame', (0.62, 0.63, 0.66), 1.0, 0.25), (0, 0, 3.9), (0, 0, ph_rot), bev=3.2, seg=6)
    glass = box('phone_glass', 70.8, 149.3, 0.4, mat('glass_black', (0.005, 0.005, 0.006), 0.0, 0.05, coat=1.0), (0, 0, 7.75), (0, 0, ph_rot), bev=2.8, seg=6)
    plane('screen', 66.5, 144, mat_screen(), (0, 0, 7.97), (0, 0, ph_rot))
    # 桌上的环境：杯子、笔记本、远处的灯（只当虚化背景）
    cup = bpy.data.meshes.new('cup'); bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=40, radius2=44, depth=95); bm.to_mesh(cup); bm.free()
    obj('cup', cup, mat('cup', (0.85, 0.83, 0.78), 0, 0.3, coat=0.6), (-170, 260, 47.5))
    box('notebook', 150, 210, 12, mat('notebook', (0.12, 0.2, 0.32), 0, 0.6), (190, 230, 6), (0, 0, math.radians(12)), bev=1.5)
    wall = plane('wall', 4000, 2000, mat('wall', (0.30, 0.24, 0.19), 0, 0.85, noise_bump=0.03, noise_scale=0.01), (0, 1100, 1000), (math.radians(90), 0, 0))
    glow_m, _ = emit('lamp_glow', (1.0, 0.72, 0.42), 3.0); sphere('lamp', 60, glow_m, (650, 1000, 420)); sphere('lamp2', 45, glow_m, (-900, 1050, 600))
    shelf = box('shelf', 900, 250, 25, mat('shelf', (0.18, 0.11, 0.06), 0, 0.5), (-300, 1000, 380))
    for i in range(9): box(f'book{i}', 28 + random.uniform(0, 20), 180, random.uniform(150, 230), mat(f'book{i}', random.choice([(0.35, 0.12, 0.08), (0.1, 0.2, 0.3), (0.5, 0.45, 0.35), (0.15, 0.25, 0.15)]), 0, 0.6), (-650 + i * 75, 1000, 480))
    bokeh_lights(18, (0, 1060, 820), (1500, 20, 120), 10, [(1.0, 0.78, 0.5), (1.0, 0.88, 0.65)])
    # 信号：1.6 秒从手机顶端飞出，往右上；2.1 秒起镜头往上甩
    sig_m, _ = emit('signal_A', (1.0, 0.66, 0.2), 160.0); sig = sphere('signal', 5.0, sig_m, (0, 0, 0))
    halo_m, _ = emit('signal_halo', (1.0, 0.6, 0.15), 6.0); halo = sphere('signal_halo', 14.0, halo_m, (0, 0, 0)); halo.parent = sig
    top = Vector((math.sin(-ph_rot) * 70, math.cos(-ph_rot) * 70, 9))
    for t, p in ((0.0, top), (1.55, top), (2.0, top + Vector((60, 120, 140))), (2.4, top + Vector((220, 420, 520)))): key(sig, 'location', F(t), p)
    for t, s in ((0.0, 0.0), (1.5, 0.0), (1.6, 1.0)): key(sig, 'scale', F(t), (s, s, s))
    for t, p, g in ((0.0, (-10, -205, 120), (-6, 4, 6)), (1.6, (-8, -175, 105), (-4, 10, 6)), (2.0, (0, -165, 110), top + Vector((60, 120, 140))), (2.4, (30, -140, 160), top + Vector((220, 420, 520)))):
        key(cam, 'location', F(t), p); key(tgt, 'location', F(t), g)
    cam_d.lens = 35; cam_d.dof.aperture_fstop = 2.0; sc.render.motion_blur_shutter = 1.0
    sun = bpy.data.lights.new('key', 'AREA'); sun.energy = 2.5e6; sun.size = 600; sun.color = (1.0, 0.82, 0.62)
    obj('key', sun, None, (-500, -200, 700), (math.radians(40), math.radians(-35), 0))
else:
    plane('board', 400, 400, mat('solder_mask', (0.025, 0.14, 0.06), 0.0, 0.32, coat=0.5, noise_bump=0.05, noise_scale=8), (0, 60, 0))
    mask_cu = mat('mask_over_copper', (0.07, 0.27, 0.11), 0.15, 0.28, coat=0.5)
    pairs = []
    for px in [0.0] + [s * d for d in (1.3, 2.6, 3.9, 5.2, 7.5, 9.8) for s in (-1, 1)]:
        for dx in (-0.105, 0.105): pairs.append((px + dx, 20, 0.0175, 0.09, 80, 0.035))
    boxes('traces', pairs, mask_cu)
    vias = [(x, y, 0.01, 0.35, 0.35, 0.02) for x in (-6.5, -4.5, 4.5, 6.5) for y in range(-15, 55, 7)]
    boxes('vias', vias, mat('via_gold', (0.9, 0.65, 0.25), 1.0, 0.25))
    caps = []
    for i in range(70):
        x = random.choice([-1, 1]) * random.uniform(0.9, 22); y = random.uniform(-25, 55); along = random.random() < 0.5
        caps.append((x, y, 0.25, 1.0 if along else 0.5, 0.5 if along else 1.0, 0.5))
    boxes('caps_body', [(x, y, z, sx * 0.7 if sx > sy else sx, sy * 0.7 if sy > sx else sy, sz) for x, y, z, sx, sy, sz in caps], mat('mlcc', (0.20, 0.15, 0.10), 0, 0.35, coat=0.3))
    ends = []
    for x, y, z, sx, sy, sz in caps:
        for sg in (-1, 1): ends.append((x + sg * sx * 0.42, y, z, sx * 0.16, sy, sz * 1.02) if sx > sy else (x, y + sg * sy * 0.42, z, sx, sy * 0.16, sz * 1.02))
    boxes('caps_ends', ends, mat('tin', (0.8, 0.8, 0.82), 1.0, 0.3))
    # 远处的 AI 芯片封装：基板 + 金属顶盖 + 散热器（主持人眼里是一堵墙）
    box('substrate', 60, 60, 1.6, mat('substrate', (0.09, 0.08, 0.05), 0, 0.4, coat=0.3), (0, 92, 0.8), bev=0.3)
    box('lid', 46, 46, 2.6, mat('lid', (0.72, 0.72, 0.74), 1.0, 0.3, noise_bump=0.02, noise_scale=30), (0, 92, 2.9), bev=0.6)
    boxes('fins', [(-21 + k * 1.6, 92, 4.2 + 22, 0.5, 46, 44) for k in range(27)], mat('fin', (0.8, 0.8, 0.82), 1.0, 0.28))
    box('inductor_L', 10, 10, 5, mat('inductor', (0.06, 0.06, 0.065), 0.2, 0.5), (-18, 40, 2.5), bev=0.5)
    box('inductor_R', 10, 10, 5, mat('inductor', (0.06, 0.06, 0.065), 0.2, 0.5), (19, 30, 2.5), bev=0.5)
    chassis = mat('chassis', (0.16, 0.17, 0.19), 0.8, 0.45, noise_bump=0.02, noise_scale=0.05)
    box('fan_wall', 400, 6, 60, chassis, (0, 190, 30))
    for k in range(6):
        cyl_me = bpy.data.meshes.new(f'fan{k}'); bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=26, radius2=26, depth=4); bm.to_mesh(cyl_me); bm.free()
        obj(f'fan{k}', cyl_me, mat(f'fan{k}', (0.03, 0.03, 0.035), 0.1, 0.5), (-150 + k * 60, 186, 30), (math.radians(90), 0, 0))
    box('wall_L', 6, 400, 60, chassis, (-110, 60, 30)); box('wall_R', 6, 400, 60, chassis, (110, 60, 30))
    for k in range(5): box(f'dimm{k}', 1.3, 130, 32, mat(f'dimm{k}', (0.05, 0.22, 0.10), 0, 0.4), (60 + k * 8, 90, 16))
    led = []
    for i in range(30):
        c = random.choice([(0.3, 1.0, 0.45), (0.45, 0.7, 1.0)]); m_, _ = emit(f'led{i}', c, 25); sphere(f'led{i}', 0.6, m_, (random.uniform(-160, 160), 183, random.uniform(5, 55)))
    plane('signal_band', 0.30, 80, mat_signal(), (0, 20, 0.045))
    POSE = OPT.get('pose', 'B'); standee(POSE, 2.2 if POSE == 'A' else 1.8, (-0.75, 5.5, 0.0), math.radians(-25))
    # 信号从左下飞进画面（和 A 段同一运动方向），落进走线
    sig_m, _ = emit('signal_B', (1.0, 0.72, 0.28), 60.0); sig = sphere('signal', 0.25, sig_m, (0, 0, 0))
    for t, p in ((0.0, (-14, -26, 14)), (0.5, (-5, -16, 5)), (0.9, (0, -8, 0.06)), (1.6, (0, 30, 0.06))): key(sig, 'location', F(t), p)
    for t, s in ((0.0, 1.0), (0.9, 1.0), (1.1, 0.25), (1.6, 0.0)): key(sig, 'scale', F(t), (s, s, s))
    for t, p, g in ((0.0, (-4.0, -24, 7.0), (0, -6, 0)), (1.0, (-2.6, -10, 3.0), (0, 2, 0.3)), (2.8, (-2.4, 0.4, 1.2), (-0.4, 6.0, 0.7)), (4.0, (-2.3, 0.9, 1.15), (-0.45, 6.0, 0.7))):
        key(cam, 'location', F(t), p); key(tgt, 'location', F(t), g)
    cam_d.lens = 28; cam_d.dof.aperture_fstop = 4.0
    sun = bpy.data.lights.new('key', 'AREA'); sun.energy = 9e4; sun.size = 120; sun.color = (1.0, 0.9, 0.8)
    obj('key', sun, None, (-80, -40, 120), (math.radians(35), math.radians(-30), 0))
    rim = bpy.data.lights.new('rim', 'AREA'); rim.energy = 6e4; rim.size = 150; rim.color = (0.6, 0.75, 1.0)
    obj('rim', rim, None, (40, 220, 60), (math.radians(-70), 0, math.radians(170)))

VIEWS = {   # 中间讲解段的固定机位（2.5D 背景）：相机位置、看向哪里、焦距、光圈
    'side': ((-3.6, 2.6, 0.95), (0.3, 8.0, 0.35), 28, 4.0),     # 主持人在左，走线和信号斜着伸向远处的芯片
    'close': ((-0.55, 10.0, 0.55), (0.05, 16.0, 0.03), 35, 5.6),  # 主持人前方，贴着信号看：跳变、鼓点、打乱
    'rx': ((-5.0, 47.0, 2.6), (0.0, 61.5, 0.8), 28, 4.0),       # 收货端：走线钻进芯片封装
    'wide': ((-22.0, -28.0, 22.0), (0.0, 40.0, 2.0), 30, 8.0),  # 拉开：芯片、散热器、很多对走线（讲速度和耗电）
}
if SHOT == 'B' and 'view' in OPT:
    for o in (cam, tgt): o.animation_data_clear()
    cp, tp, lens, fs = VIEWS[OPT['view']]; cam.location = cp; tgt.location = tp; cam_d.lens = lens; cam_d.dof.aperture_fstop = fs
    sig.hide_render = True
    if 'bits' in OPT:
        n_ = bpy.data.materials['signal_band'].node_tree.nodes['offset']; n_.outputs[0].animation_data_clear() if hasattr(n_.outputs[0], 'animation_data_clear') else None
        bpy.data.materials['signal_band'].node_tree.animation_data_clear(); n_.outputs[0].default_value = float(OPT['bits'])
    FRAMES = FRAMES or [60]

# ---------- 世界、渲染 ----------
wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True; N = wd.node_tree.nodes; L = wd.node_tree.links
bg = N['Background']; bg.inputs['Strength'].default_value = 0.35
if os.path.exists(HDRI):
    env = N.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(HDRI); L.new(env.outputs['Color'], bg.inputs['Color'])
lp = N.new('ShaderNodeLightPath'); mx = N.new('ShaderNodeMixShader'); dark = N.new('ShaderNodeBackground'); dark.inputs['Color'].default_value = (0.02, 0.025, 0.035, 1) if SHOT == 'B' else (0.05, 0.04, 0.035, 1)
out = N['World Output']; L.new(lp.outputs['Is Camera Ray'], mx.inputs['Fac']); L.new(bg.outputs[0], mx.inputs[1]); L.new(dark.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs[0])
if CYCLES:
    sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMP; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 4; sc.cycles.device = 'CPU'
else:
    ENG = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    sc.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in ENG else 'BLENDER_EEVEE_NEXT'; sc.eevee.taa_render_samples = SAMP
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, NF
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5
sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
sc.render.image_settings.file_format = 'PNG'
for f in FRAMES or [1]:
    sc.frame_set(f); sc.render.filepath = os.path.join(OUT, (f"{SHOT}_{OPT['view']}_{OPT.get('pose', 'B')}.png" if 'view' in OPT else f'{SHOT}_f{f:04d}.png')); bpy.ops.render.render(write_still=True); print('RENDERED', sc.render.filepath)
