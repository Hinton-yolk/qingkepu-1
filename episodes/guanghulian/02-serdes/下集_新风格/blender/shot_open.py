# 光互连 02 下集 · 新画面版 · 场景（草稿 v2，按审核 11-10 必改 12 条改）
# A 段（y1，约 2.4 秒）：桌上的手机，消息 1 秒内从「少了一位」那个字起整串变成乱码；一个金色信号从手机飞出去（往右上），镜头追着它甩上去。
# B 段（y2，约 4 秒）：信号从左下飞进画面（同一运动方向），落进 AI 服务器主板上的一对差分走线（盖在阻焊下，一直接到芯片封装底下），
#      镜头贴着板面滑过去，停在纸片立牌主持人（蹲着看）身边。
# view=…：B 场景的固定机位静帧，给中间讲解段（2.5D）当背景；同时导出走线在画面上的位置和每一位的边界（叠加层沿走线画刻度、鼓点）。
# 单位：毫米（scale_length = 0.001，景深按真实光圈算）。
# 用法：blender -b --python shot_open.py -- <A|B> <输出目录> <宽> <高> <采样> [cycles] [view=side|close|rx|wide] [pose=A|B] [bits=normal|long|blur] [off=位偏移] [xray=1] [帧号…]
#   云端草稿用 cycles（云端没有 EEVEE 要的 libEGL）；用户电脑上用 EEVEE。
import bpy, bmesh, math, os, sys, random, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

args = sys.argv[sys.argv.index('--') + 1:]
SHOT, OUT, W, H, SAMP = args[0], args[1], int(args[2]), int(args[3]), int(args[4]); rest = args[5:]
CYCLES = 'cycles' in rest; FRAMES = [int(a) for a in rest if a.isdigit()]
OPT = dict(a.split('=', 1) for a in rest if '=' in a)
FPS = 30; DUR = {'A': 2.4, 'B': 4.0}[SHOT]; NF = round(DUR * FPS); F = lambda s: 1 + round(s * FPS)
HERE = os.path.dirname(os.path.abspath(__file__)); AS = os.path.join(HERE, 'assets'); HDRI = os.path.join(HERE, 'assets_dl', 'studio_small_09_2k.hdr')
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; os.makedirs(OUT, exist_ok=True)
sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
random.seed(11)
GOLD = (1.0, 0.58, 0.12)
STAND_H = 2.2                                # 主持人站立身高（mm）；蹲姿按 0.62 倍（审核：前后大小要一致）
BIT = 0.7; NB = 120                          # 走线上每一位画多长（mm，示意）；比特贴图一圈 120 位
BITS = json.load(open(os.path.join(AS, 'bits.json')))
TR_Y0, TR_Y1 = -45.0, 66.0                   # 走线从画外来，一直钻到芯片封装底下（基板前沿 y = 62）

# ---------- 材质 ----------
def mat(name, col, metal=0.0, rough=0.5, coat=0.0, noise_bump=0.0, noise_scale=1.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat; b.inputs['Alpha'].default_value = alpha
    if alpha < 1 and hasattr(m, 'surface_render_method'): m.surface_render_method = 'BLENDED'
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
def lin(idb):
    ad = idb.animation_data
    if not ad or not ad.action: return
    act = ad.action; fcs = list(act.fcurves) if hasattr(act, 'fcurves') else [fc for ly in act.layers for st in ly.strips for cb in st.channelbags for fc in cb.fcurves]
    for fc in fcs:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
def mat_wood():
    m = mat('desk_wood', (0.3, 0.17, 0.08), 0.0, 0.42, coat=0.25); N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.02, 0.0025, 0.02); L.new(tc.outputs['Object'], mp.inputs[0])
    wv = N.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 1.6; wv.inputs['Distortion'].default_value = 11; wv.inputs['Detail'].default_value = 6; wv.inputs['Detail Scale'].default_value = 2.0; L.new(mp.outputs[0], wv.inputs[0])
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = (0.26, 0.14, 0.065, 1); cr.color_ramp.elements[1].color = (0.38, 0.22, 0.11, 1)
    L.new(wv.outputs['Fac'], cr.inputs[0]); L.new(cr.outputs[0], b.inputs['Base Color']); return m
def mat_screen():
    """手机屏幕：聊天界面自发光；0.85–1.05 秒从正常变成乱码（Mix 系数做关键帧）"""
    m = mat('phone_screen', (0.0, 0.0, 0.0), 0.0, 0.04, coat=1.0); N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    a = img(N, os.path.join(AS, 'screen_ok.png')); c = img(N, os.path.join(AS, 'screen_bad.png'))
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L.new(a.outputs['Color'], mx.inputs['A']); L.new(c.outputs['Color'], mx.inputs['B'])
    L.new(mx.outputs['Result'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 2.2
    fac = mx.inputs['Factor']; g = float(OPT.get('garble', -1))
    if g >= 0: fac.default_value = g
    else:
        for t, v in ((0.0, 0.0), (0.85, 0.0), (1.05, 1.0)): fac.default_value = v; fac.keyframe_insert('default_value', frame=F(t))
    return m
def mat_standee(k):
    m = bpy.data.materials.new('standee_' + k); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    t = img(N, os.path.join(AS, f'standee_{k}.png')); L.new(t.outputs['Color'], b.inputs['Base Color']); L.new(t.outputs['Alpha'], b.inputs['Alpha'])
    b.inputs['Roughness'].default_value = 0.8
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'DITHERED'
    return m, t.image.size[:]
def mat_signal(tex):
    """走线上的信号（示意：两根线之间的电压差）：半透明金色光带，按电平画（高 = 亮、低 = 暗，相邻同电平连成一片），
       透过它看得见下面那一对线和中间的缝；比特贴图沿 y 往芯片方向走"""
    m = bpy.data.materials.new('signal_band'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    for n in list(N): N.remove(n)
    o = N.new('ShaderNodeOutputMaterial'); e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*GOLD, 1)
    tr = N.new('ShaderNodeBsdfTransparent'); mx = N.new('ShaderNodeMixShader')
    geo = N.new('ShaderNodeNewGeometry'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sp.inputs[0])   # 世界坐标（审核：和导出的位边界对齐）
    off = N.new('ShaderNodeValue'); off.name = 'offset'
    u = N.new('ShaderNodeMath'); u.operation = 'MULTIPLY_ADD'; u.inputs[1].default_value = 1 / (NB * BIT); L.new(sp.outputs['Y'], u.inputs[0]); L.new(off.outputs[0], u.inputs[2])
    cm = N.new('ShaderNodeCombineXYZ'); L.new(u.outputs[0], cm.inputs['X']); cm.inputs['Y'].default_value = 0.5
    t = img(N, os.path.join(AS, tex), 'Non-Color'); t.interpolation = 'Closest' if 'blur' not in tex else 'Linear'; L.new(cm.outputs[0], t.inputs[0])
    st = N.new('ShaderNodeMath'); st.operation = 'MULTIPLY_ADD'; st.inputs[1].default_value = 2.0; st.inputs[2].default_value = 0.25; L.new(t.outputs['Color'], st.inputs[0]); L.new(st.outputs[0], e.inputs['Strength'])
    fa = N.new('ShaderNodeMath'); fa.operation = 'MULTIPLY_ADD'; fa.inputs[1].default_value = 0.45; fa.inputs[2].default_value = 0.35; L.new(t.outputs['Color'], fa.inputs[0])
    L.new(fa.outputs[0], mx.inputs['Fac']); L.new(tr.outputs[0], mx.inputs[1]); L.new(e.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], o.inputs[0])
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'BLENDED'
    for fr, v in ((1, 0.0), (NF, -DUR * 0.12)): off.outputs[0].default_value = v; off.outputs[0].keyframe_insert('default_value', frame=fr)
    lin(m.node_tree); return m

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
    """很多小方块合成一个网格：specs = (cx, cy, cz, sx, sy, sz[, 绕 z 转角])"""
    bm = bmesh.new()
    for sp_ in specs:
        cx, cy, cz, sx, sy, sz = sp_[:6]; a = sp_[6] if len(sp_) > 6 else 0.0; ca, sa = math.cos(a), math.sin(a)
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r['verts']:
            x, y = v.co.x * sx, v.co.y * sy; v.co = Vector((cx + x * ca - y * sa, cy + x * sa + y * ca, cz + v.co.z * sz))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); return obj(name, me, m)
def cyl(name, r, depth, m, loc, rot=(0, 0, 0), seg=40):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=depth); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return obj(name, me, m, loc, rot)
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
    """纸片立牌：竖着的一张纸（带白纸边），底下一条折出来的纸脚"""
    m, (iw, ih) = mat_standee(k); w = height * iw / ih
    p = plane('standee_' + k, w, height, m, (loc[0], loc[1], loc[2] + height / 2), (math.radians(90), 0, yaw))
    box('standee_foot_' + k, w * 0.5, height * 0.12, height * 0.006, mat('paper', (0.92, 0.9, 0.85), 0, 0.8),
        (loc[0] - math.sin(yaw) * height * 0.04, loc[1] + math.cos(yaw) * height * 0.04, loc[2] + height * 0.003), (0, 0, yaw))
    return p
def bokeh_lights(n, center, spread, size, cols, strength=(4, 12)):
    for i in range(n):
        c = random.choice(cols); m, _ = emit(f'bk{i}', c, random.uniform(*strength))
        o_ = sphere(f'bk{i}', size * random.uniform(0.6, 1.4), m, (center[0] + random.uniform(-spread[0], spread[0]), center[1] + random.uniform(-spread[1], spread[1]), center[2] + random.uniform(-spread[2], spread[2])))
        o_.visible_glossy = False          # 背景灯只当虚化背景，不在手机玻璃上反光（审核：白点压字）
def key(o, path, fr, val):
    setattr(o, path, val); o.keyframe_insert(path, frame=fr)
def dust_near_camera(n, dmin, dmax, size):
    """前景灰尘：离镜头很近、虚成光斑，慢慢漂（审核：前景灰尘是必要的；数量少、很虚）"""
    dm, _ = emit('dust', (1.0, 0.9, 0.75), 0.12)  # 灰尘不进反射
    _dust_objs = []
    cam_mat = cam.matrix_world.copy()
    for i in range(n):
        d = random.uniform(dmin, dmax); x = random.choice([-1, 1]) * random.uniform(0.30, 0.5) * d; y = random.uniform(-0.85, 0.85) * d
        p = cam_mat @ Vector((x, y, -d)); s = sphere(f'dust{i}', size * random.uniform(0.5, 1.3), dm, p); s.visible_glossy = False
        drift = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-0.5, 1))) * d * 0.04
        key(s, 'location', 1, p); key(s, 'location', NF, p + drift); lin(s)

# ---------- 相机 ----------
cam_d = bpy.data.cameras.new('cam'); cam = obj('cam', cam_d); sc.camera = cam
cam_d.sensor_width = 36; cam_d.clip_start = 0.05; cam_d.clip_end = 20000; cam_d.dof.use_dof = True
tgt = bpy.data.objects.new('target', None); sc.collection.objects.link(tgt)
tc_ = cam.constraints.new('TRACK_TO'); tc_.target = tgt; tc_.track_axis = 'TRACK_NEGATIVE_Z'; tc_.up_axis = 'UP_Y'
cam_d.dof.focus_object = tgt

if SHOT == 'A':
    plane('desk', 1600, 1600, mat_wood(), (0, 0, 0))
    ph_rot = math.radians(-12)
    box('phone_body', 71.5, 150, 7.8, mat('phone_frame', (0.62, 0.63, 0.66), 1.0, 0.25), (0, 0, 3.9), (0, 0, ph_rot), bev=3.2, seg=6)
    box('phone_glass', 70.8, 149.3, 0.4, mat('glass_black', (0.005, 0.005, 0.006), 0.0, 0.05, coat=1.0), (0, 0, 7.75), (0, 0, ph_rot), bev=2.8, seg=6)
    plane('screen', 66.5, 144, mat_screen(), (0, 0, 7.97), (0, 0, ph_rot))
    cup = bpy.data.meshes.new('cup'); bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=48, radius1=40, radius2=44, depth=95); bm.to_mesh(cup); bm.free()
    obj('cup', cup, mat('cup', (0.85, 0.83, 0.78), 0, 0.3, coat=0.6), (-170, 260, 47.5))
    box('notebook', 150, 210, 12, mat('notebook', (0.12, 0.2, 0.32), 0, 0.6), (190, 230, 6), (0, 0, math.radians(12)), bev=1.5)
    plane('wall', 4000, 2000, mat('wall', (0.30, 0.24, 0.19), 0, 0.85, noise_bump=0.03, noise_scale=0.01), (0, 1100, 1000), (math.radians(90), 0, 0))
    glow_m, _ = emit('lamp_glow', (1.0, 0.72, 0.42), 3.0); sphere('lamp', 60, glow_m, (650, 1000, 420)); sphere('lamp2', 45, glow_m, (-900, 1050, 600))
    box('shelf', 900, 250, 25, mat('shelf', (0.18, 0.11, 0.06), 0, 0.5), (-300, 1000, 380))
    for i in range(9): box(f'book{i}', 28 + random.uniform(0, 20), 180, random.uniform(150, 230), mat(f'book{i}', random.choice([(0.35, 0.12, 0.08), (0.1, 0.2, 0.3), (0.5, 0.45, 0.35), (0.15, 0.25, 0.15)]), 0, 0.6), (-650 + i * 75, 1000, 480))
    bokeh_lights(18, (0, 1060, 820), (1500, 20, 120), 10, [(1.0, 0.78, 0.5), (1.0, 0.88, 0.65)], strength=(2, 5))
    sig_m, _ = emit('signal_A', GOLD, 160.0); sig = sphere('signal', 5.0, sig_m, (0, 0, 0))
    halo_m, _ = emit('signal_halo', GOLD, 6.0); halo = sphere('signal_halo', 14.0, halo_m, (0, 0, 0)); halo.parent = sig
    top = Vector((math.sin(-ph_rot) * 70, math.cos(-ph_rot) * 70, 9))
    for t, p in ((0.0, top), (1.55, top), (2.0, top + Vector((60, 120, 140))), (2.4, top + Vector((220, 420, 520)))): key(sig, 'location', F(t), p)
    for t, s in ((0.0, 0.0), (1.5, 0.0), (1.6, 1.0)): key(sig, 'scale', F(t), (s, s, s))
    # 镜头推近到消息能读出来；1.6 秒起追着信号往右上甩
    for t, p, g in ((0.0, (-4, -150, 118), (0, 14, 6)), (1.6, (-3, -132, 104), (0, 18, 6)), (2.0, (4, -125, 110), top + Vector((60, 120, 140))), (2.4, (30, -110, 160), top + Vector((220, 420, 520)))):
        key(cam, 'location', F(t), p); key(tgt, 'location', F(t), g)
    cam_d.lens = 35; cam_d.dof.aperture_fstop = 2.0
    sun = bpy.data.lights.new('key', 'AREA'); sun.energy = 2.5e6; sun.size = 600; sun.color = (1.0, 0.82, 0.62)
    obj('key', sun, None, (-500, -200, 700), (math.radians(40), math.radians(-35), 0))
    MIST = (250, 1400, (0.32, 0.24, 0.17))
else:
    plane('board', 400, 400, mat('solder_mask', (0.02, 0.24, 0.07), 0.0, 0.34, coat=0.5, noise_bump=0.05, noise_scale=8), (0, 60, 0))
    mask_cu = mat('mask_over_copper', (0.10, 0.42, 0.13), 0.15, 0.28, coat=0.5)
    PAIR_X = [0.0] + [s * d for d in (1.3, 2.6, 3.9, 5.2, 7.5, 9.8) for s in (-1, 1)]
    boxes('traces', [(px + dx, (TR_Y0 + TR_Y1) / 2, 0.0175, 0.09, TR_Y1 - TR_Y0, 0.035) for px in PAIR_X for dx in (-0.105, 0.105)], mask_cu)
    # 去耦电容：成排排在芯片封装周围，带焊盘，避开走线通道（审核：不能随机撒、不能压在走线上）
    caps, ends, pads = [], [], []
    for side in (-1, 1):
        for row in range(3):
            for k in range(8):
                x = side * (13.0 + k * 1.9); y = 53.5 + row * 2.4; caps.append((x, y, 0.27, 0.7, 0.5, 0.5))
                for sg in (-1, 1): ends.append((x + sg * 0.42, y, 0.27, 0.16, 0.5, 0.51)); pads.append((x + sg * 0.42, y, 0.015, 0.34, 0.6, 0.03))
        for k in range(14):
            x = side * 33.5; y = 64 + k * 3.8; caps.append((x, y, 0.27, 0.5, 0.7, 0.5))
            for sg in (-1, 1): ends.append((x, y + sg * 0.42, 0.27, 0.5, 0.16, 0.51)); pads.append((x, y + sg * 0.42, 0.015, 0.6, 0.34, 0.03))
    boxes('caps_body', caps, mat('mlcc', (0.20, 0.15, 0.10), 0, 0.35, coat=0.3)); boxes('caps_ends', ends, mat('tin', (0.8, 0.8, 0.82), 1.0, 0.3))
    boxes('cap_pads', pads, mat('pad', (0.75, 0.75, 0.72), 1.0, 0.35))
    # 过孔：圆的，被阻焊盖住（只是微微鼓起、颜色深一点）
    tent = mat('tented_via', (0.03, 0.18, 0.06), 0.0, 0.3, coat=0.5)
    for i, (x, y) in enumerate([(x, y) for x in (-11.5, 11.5) for y in range(-30, 58, 4)]): cyl(f'via{i}', 0.18, 0.02, tent, (x, y, 0.01), seg=16)
    # AI 芯片封装：基板 + 顶盖 + 散热器（底座 + 鳍片）；主持人眼里是一堵墙
    box('substrate', 60, 60, 1.6, mat('substrate', (0.09, 0.08, 0.05), 0, 0.4, coat=0.3), (0, 92, 0.8), bev=0.3)
    XR = OPT.get('xray') == '1'
    lid_m = mat('lid', (0.72, 0.72, 0.74), 1.0, 0.3, noise_bump=0.02, noise_scale=30, alpha=0.18 if XR else 1.0)
    box('lid', 46, 46, 2.6, lid_m, (0, 92, 2.9), bev=0.6)
    if XR:      # y10：顶盖半透明，露出裸片和靠走线那一边的收发电路（示意）
        box('die', 26, 26, 0.8, mat('die', (0.12, 0.13, 0.16), 0.3, 0.3), (0, 92, 2.0))
        sd_m, _ = emit('serdes_blocks', (0.55, 0.85, 1.0), 4.0)
        boxes('serdes', [(-10.5 + k * 3.0, 80.2, 2.45, 2.4, 1.6, 0.06) for k in range(8)], sd_m)
    else:
        box('hs_base', 46, 46, 3.0, mat('fin', (0.8, 0.8, 0.82), 1.0, 0.28), (0, 92, 5.7))
        boxes('fins', [(-21 + k * 1.6, 92, 7.2 + 20, 0.5, 46, 40) for k in range(27)], mat('fin2', (0.8, 0.8, 0.82), 1.0, 0.28))
    ind = mat('inductor', (0.06, 0.06, 0.065), 0.2, 0.5)
    boxes('inductors', [(sx * (45 + k * 11), 70 + r * 13, 2.5, 9, 9, 5) for sx in (-1, 1) for k in range(3) for r in range(3)], ind)
    # 机箱：两侧壁、后面一排风扇（轮毂 + 扇叶）、天花板上数据中心的灯带；再远处是雾（合成里的空气透视）
    chassis = mat('chassis', (0.16, 0.17, 0.19), 0.8, 0.45, noise_bump=0.02, noise_scale=0.05)
    box('fan_wall', 400, 6, 60, chassis, (0, 196, 30)); box('wall_L', 6, 400, 60, chassis, (-110, 60, 30)); box('wall_R', 6, 400, 60, chassis, (110, 60, 30))
    blade = mat('fan_blade', (0.04, 0.04, 0.045), 0.1, 0.45)
    for k in range(6):
        cx = -150 + k * 60
        cyl(f'fan_ring{k}', 27, 3, mat(f'fan_ring{k}', (0.02, 0.02, 0.022), 0.1, 0.5), (cx, 190, 30), (math.radians(90), 0, 0))
        cyl(f'fan_hub{k}', 9, 6, blade, (cx, 187, 30), (math.radians(90), 0, 0))
        boxes(f'fan_blades{k}', [(cx + math.cos(a) * 15, 186.5, 30 + math.sin(a) * 15, 13, 1.0, 7, a) for a in [i * 2 * math.pi / 7 for i in range(7)]], blade)
        bpy.data.objects[f'fan_blades{k}'].rotation_euler = (math.radians(90), 0, 0); bpy.data.objects[f'fan_blades{k}'].location = (0, 0, 0)
    ceil_m, _ = emit('ceiling_light', (0.85, 0.95, 1.0), 6.0)
    for r in range(6): box(f'ceil{r}', 900, 30, 4, ceil_m, (0, 150 + r * 260, 900))
    for i in range(30):
        c = random.choice([(0.3, 1.0, 0.45), (0.45, 0.7, 1.0)]); m_, _ = emit(f'led{i}', c, 25); sphere(f'led{i}', 0.6, m_, (random.uniform(-160, 160), 192, random.uniform(5, 55)))
    BTEX = {'normal': 'bits.png', 'long': 'bits_long.png', 'blur': 'bits_blur.png'}[OPT.get('bits', 'normal')]
    plane('signal_band', 0.32, TR_Y1 - 2 - TR_Y0, mat_signal(BTEX), (0, (TR_Y0 + TR_Y1 - 2) / 2, 0.045))
    POSE = OPT.get('pose', 'B'); standee(POSE, STAND_H if POSE == 'A' else STAND_H * 0.62, (-0.75, 5.5, 0.0), math.radians(-25))
    sig_m, _ = emit('signal_B', GOLD, 60.0); sig = sphere('signal', 0.25, sig_m, (0, 0, 0))
    for t, p in ((0.0, (-14, -26, 14)), (0.5, (-5, -16, 5)), (0.9, (0, -8, 0.06)), (1.6, (0, 30, 0.06))): key(sig, 'location', F(t), p)
    for t, s in ((0.0, 1.0), (0.9, 1.0), (1.1, 0.25), (1.6, 0.0)): key(sig, 'scale', F(t), (s, s, s))
    for t, p, g in ((0.0, (-4.0, -24, 7.0), (0, -6, 0)), (1.0, (-2.6, -10, 3.0), (0, 2, 0.3)), (2.8, (-2.4, 0.4, 1.2), (-0.4, 6.0, 0.7)), (4.0, (-2.3, 0.9, 1.15), (-0.45, 6.0, 0.7))):
        key(cam, 'location', F(t), p); key(tgt, 'location', F(t), g)
    cam_d.lens = 28; cam_d.dof.aperture_fstop = 2.8
    sun = bpy.data.lights.new('key', 'AREA'); sun.energy = 9e4; sun.size = 120; sun.color = (1.0, 0.9, 0.8)
    obj('key', sun, None, (-80, -40, 120), (math.radians(35), math.radians(-30), 0))
    rim = bpy.data.lights.new('rim', 'AREA'); rim.energy = 6e4; rim.size = 150; rim.color = (0.6, 0.75, 1.0)
    obj('rim', rim, None, (40, 220, 60), (math.radians(-70), 0, math.radians(170)))
    MIST = (18, 260, (0.16, 0.30, 0.30))

VIEWS = {   # 中间讲解段的固定机位（2.5D 背景）：相机位置、看向哪里、焦距、光圈
    'side': ((-3.6, 2.6, 0.95), (0.3, 8.0, 0.35), 28, 2.8),     # 主持人在左，走线和信号斜着伸向远处的芯片
    'close': ((-0.55, 10.0, 0.55), (0.05, 16.0, 0.03), 35, 2.8), # 主持人前方，贴着信号看：跳变、鼓点、打乱
    'rx': ((-5.0, 47.0, 2.6), (0.0, 61.5, 0.8), 28, 2.8),       # 收货端：走线钻进芯片封装底下
    'wide': ((-22.0, -28.0, 22.0), (0.0, 40.0, 2.0), 30, 4.0),  # 拉开：芯片、散热器、很多对走线
    'rxx': ((-9.0, 50.0, 14.0), (0.0, 78.0, 2.0), 28, 4.0),     # y10：从斜上方看半透明顶盖下的裸片和收发电路
    'count': ((-4.2, 13.6, 1.5), (0.0, 14.2, 0.05), 18, 2.8),   # y6–y8：从侧面横着看走线，一位一位从左排到右（数五拍、看跑偏）
}
if SHOT == 'B' and 'view' in OPT:
    for o in (cam, tgt): o.animation_data_clear()
    cp, tp, lens, fs = VIEWS['rxx' if OPT['view'] == 'rx' and OPT.get('xray') == '1' else OPT['view']]; cam.location = cp; tgt.location = tp; cam_d.lens = lens; cam_d.dof.aperture_fstop = fs
    sig.hide_render = True
    nt = bpy.data.materials['signal_band'].node_tree; nt.animation_data_clear(); nt.nodes['offset'].outputs[0].default_value = float(OPT.get('off', 0)) / NB
    FRAMES = FRAMES or [60]
bpy.context.view_layer.update()
if SHOT == 'B': dust_near_camera(3, 0.3, 0.9, 0.02) if 'view' in OPT else None
else: dust_near_camera(3, 12, 30, 0.9)

# ---------- 世界、渲染、合成（空气透视 + 光的辉光） ----------
wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True; N = wd.node_tree.nodes; L = wd.node_tree.links
bg = N['Background']; bg.inputs['Strength'].default_value = 0.35
if os.path.exists(HDRI):
    env = N.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(HDRI); L.new(env.outputs['Color'], bg.inputs['Color'])
lp = N.new('ShaderNodeLightPath'); mx = N.new('ShaderNodeMixShader'); dark = N.new('ShaderNodeBackground'); dark.inputs['Color'].default_value = (*MIST[2], 1)
out = N['World Output']; L.new(lp.outputs['Is Camera Ray'], mx.inputs['Fac']); L.new(bg.outputs[0], mx.inputs[1]); L.new(dark.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs[0])
if CYCLES:
    sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMP; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 4; sc.cycles.device = 'CPU'
else:
    ENG = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    sc.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in ENG else 'BLENDER_EEVEE_NEXT'; sc.eevee.taa_render_samples = SAMP
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, NF
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 1.0 if SHOT == 'A' else 0.5
sc.view_settings.view_transform = 'AgX'; sc.view_settings.exposure = 0.9 if SHOT == 'B' else 0.2
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
if CYCLES:   # 云端草稿：没有 libEGL，合成节点会让 Blender 直接退出；改用很淡的体积雾做空气透视
    vm = bpy.data.materials.new('haze'); vm.use_nodes = True; Nn = vm.node_tree.nodes; Ln = vm.node_tree.links
    for n in list(Nn): Nn.remove(n)
    vo = Nn.new('ShaderNodeOutputMaterial'); vs = Nn.new('ShaderNodeVolumeScatter'); vs.inputs['Density'].default_value = 0.6 / MIST[1]
    vs.inputs['Color'].default_value = (*MIST[2], 1); Ln.new(vs.outputs[0], vo.inputs['Volume'])
    hb = box('haze_box', 1, 1, 1, vm, (0, 0, 0)); c0 = cam.location
    hb.scale = (MIST[1] * 6, MIST[1] * 6, MIST[1] * 6); hb.location = (c0.x, c0.y + MIST[1] * 2.5, c0.z)
    if SHOT == 'B' and 'view' not in OPT: hb.location = (0, 60, 0)
else:
  try:
    vl = sc.view_layers[0]; vl.use_pass_mist = True
    wd.mist_settings.start = MIST[0]; wd.mist_settings.depth = MIST[1]; wd.mist_settings.falloff = 'QUADRATIC'
    ng = bpy.data.node_groups.new('comp', 'CompositorNodeTree'); sc.compositing_node_group = ng
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new('CompositorNodeRLayers'); rl.scene = sc
    gl = ng.nodes.new('CompositorNodeGlare'); ng.links.new(rl.outputs['Image'], gl.inputs['Image'])
    for k, v in (('Type', 'Bloom'), ('Threshold', 1.0), ('Strength', 0.6), ('Size', 0.6), ('Quality', 'High')):
        try: gl.inputs[k].default_value = v
        except Exception as e: print('辉光参数跳过', k, e)
    add = ng.nodes.new('ShaderNodeMix'); add.data_type = 'RGBA'; add.blend_type = 'ADD'; add.inputs['Factor'].default_value = 1.0
    ng.links.new(rl.outputs['Image'], add.inputs['A']); ng.links.new(gl.outputs['Glare'], add.inputs['B'])
    hz = ng.nodes.new('ShaderNodeMath'); hz.operation = 'MULTIPLY'; hz.inputs[1].default_value = 0.75; ng.links.new(rl.outputs['Mist'], hz.inputs[0])
    fog = ng.nodes.new('ShaderNodeMix'); fog.data_type = 'RGBA'; fog.blend_type = 'MIX'; ng.links.new(hz.outputs[0], fog.inputs['Factor'])
    ng.links.new(add.outputs['Result'], fog.inputs['A']); fog.inputs['B'].default_value = (*MIST[2], 1)
    go = ng.nodes.new('NodeGroupOutput'); ng.links.new(fog.outputs['Result'], go.inputs[0]); print('COMPOSITOR 辉光 + 空气透视已接上')
  except Exception as e: print('COMPOSITOR 跳过：', e)
sc.render.image_settings.file_format = 'PNG'

def export_band(path):
    """导出走线在画面上的位置和每一位的边界：叠加层沿走线画节拍刻度、在跳变处画鼓点"""
    bits = BITS[OPT.get('bits', 'normal')]; off = float(OPT.get('off', 0)); pts = []
    for j in range(int(TR_Y0 / BIT) - 2, int((TR_Y1 - 2) / BIT) + 2):
        y = (j - off) * BIT
        if not (TR_Y0 <= y <= TR_Y1 - 2): continue
        c = world_to_camera_view(sc, cam, Vector((0, y, 0.05))); l = world_to_camera_view(sc, cam, Vector((-0.4, y, 0.05)))
        if c.z <= 0 or not (-0.2 <= c.x <= 1.2 and -0.2 <= c.y <= 1.2): continue
        pts.append(dict(j=j, y=round(y, 3), bit=bits[j % NB], x=round(c.x * W, 1), yy=round((1 - c.y) * H, 1), lx=round(l.x * W, 1), ly=round((1 - l.y) * H, 1)))
    hp = world_to_camera_view(sc, cam, Vector((-0.75, 5.5, STAND_H * 1.05)))
    json.dump(dict(W=W, H=H, bit_mm=BIT, pts=pts, host_head=(round(hp.x * W, 1), round((1 - hp.y) * H, 1))), open(path, 'w'))
for f in FRAMES or [1]:
    sc.frame_set(f)
    name = (f"{SHOT}_{OPT['view']}_{OPT.get('pose', 'B')}_{OPT.get('bits', 'normal')}" + ('_xray' if OPT.get('xray') == '1' else '')) if 'view' in OPT else f'{SHOT}_f{f:04d}'
    if 'garble' in OPT: name += f"_g{OPT['garble']}"
    sc.render.filepath = os.path.join(OUT, name + '.png'); bpy.ops.render.render(write_still=True); print('RENDERED', sc.render.filepath)
    if 'view' in OPT: export_band(os.path.join(OUT, name + '.json'))
