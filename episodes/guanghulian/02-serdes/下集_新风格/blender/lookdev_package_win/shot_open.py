# 光互连 02 下集 · 新画面版 · 场景（正式版渲染包，按渲染包审核 11-10 必改 8 条改；用户 11-10 定：去掉主持人）
# A 段（y1，约 2.4 秒）：桌上的手机，消息 1 秒内从「少了一位」那个字起整串变成乱码；一个金色信号从手机飞出去，镜头追着它往远处飞。
# B 段（y2，约 4 秒）：第 1 帧信号就在画面中间、小而远（接住 A 段结尾），镜头在后面追着它，它落进 AI 服务器主板上的一对差分走线
#      （盖在阻焊下，一直接到芯片封装底下），光带从落点往前铺开；镜头降到板面，最后一帧和 side 背景是同一个机位（y3 接上不跳）。
# view=…：B 场景的固定机位静帧，给中间讲解段（2.5D）当背景；同时导出走线在画面上的位置和每一位的边界（叠加层沿走线画刻度、鼓点）。
# 单位：毫米（scale_length = 0.001，景深按真实光圈算）。
# 用法：blender -b --python shot_open.py -- <A|B> <输出目录> <宽> <高> <采样> [cycles] [seq] [view=side|close|count|rx|wide] [bits=normal|long|blur] [off=位偏移] [xray=1] [noband=1] [帧号…]
#   seq：渲整段 PNG 序列（已渲的帧跳过，可续渲）；noband=1：静帧不渲光带（正式版光带在云端画成动画）
#   云端草稿用 cycles（云端没有 EEVEE 要的 libEGL）；用户电脑上用 EEVEE。
import bpy, bmesh, math, os, sys, random, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

args = sys.argv[sys.argv.index('--') + 1:]
SHOT, OUT, W, H, SAMP = args[0], args[1], int(args[2]), int(args[3]), int(args[4]); rest = args[5:]
CYCLES = 'cycles' in rest; CLOUD = 'cloud' in rest; GPU = 'gpu' in rest; SEQ = 'seq' in rest; FRAMES = [int(a) for a in rest if a.isdigit()]
OPT = dict(a.split('=', 1) for a in rest if '=' in a)
FPS = 30; DUR = {'A': 2.4, 'B': 4.0}[SHOT]; NF = round(DUR * FPS); F = lambda s: 1 + round(s * FPS)
HERE = os.path.dirname(os.path.abspath(__file__)); AS = os.path.join(HERE, 'assets'); HDRI = os.path.join(HERE, 'assets_dl', 'studio_small_09_2k.hdr')
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; os.makedirs(OUT, exist_ok=True)
sc.unit_settings.scale_length = 0.001; sc.unit_settings.length_unit = 'MILLIMETERS'
random.seed(11)
GOLD = (1.0, 0.52, 0.08)
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
    st = N.new('ShaderNodeMath'); st.operation = 'MULTIPLY_ADD'; st.inputs[1].default_value = 1.1; st.inputs[2].default_value = 0.2; L.new(t.outputs['Color'], st.inputs[0]); L.new(st.outputs[0], e.inputs['Strength'])
    fa = N.new('ShaderNodeMath'); fa.operation = 'MULTIPLY_ADD'; fa.inputs[1].default_value = 0.45; fa.inputs[2].default_value = 0.35; L.new(t.outputs['Color'], fa.inputs[0])
    rv = N.new('ShaderNodeValue'); rv.name = 'reveal'; lt = N.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; L.new(sp.outputs['Y'], lt.inputs[0]); L.new(rv.outputs[0], lt.inputs[1])
    lo = N.new('ShaderNodeValue'); lo.name = 'reveal_lo'; gt = N.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; L.new(sp.outputs['Y'], gt.inputs[0]); L.new(lo.outputs[0], gt.inputs[1])
    mk = N.new('ShaderNodeMath'); mk.operation = 'MULTIPLY'; L.new(lt.outputs[0], mk.inputs[0]); L.new(gt.outputs[0], mk.inputs[1])
    fm = N.new('ShaderNodeMath'); fm.operation = 'MULTIPLY'; L.new(fa.outputs[0], fm.inputs[0]); L.new(mk.outputs[0], fm.inputs[1])
    L.new(fm.outputs[0], mx.inputs['Fac']); L.new(tr.outputs[0], mx.inputs[1]); L.new(e.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], o.inputs[0])
    if SHOT == 'B' and 'view' not in OPT:      # B 段：光带从信号落点（y = 0，0.9 秒）往芯片方向铺开（审核建议：跟着一个东西走）
        for t, v in ((0.0, -0.01), (0.9, 0.0), (1.5, 14.0), (2.6, 70.0)): rv.outputs[0].default_value = v; rv.outputs[0].keyframe_insert('default_value', frame=F(t))
        for t, v in ((0.0, 0.0), (1.8, 0.0), (2.8, -60.0)): lo.outputs[0].default_value = v; lo.outputs[0].keyframe_insert('default_value', frame=F(t))   # 落点后面那段晚一点再亮（信号是从那边来的）
    else: rv.outputs[0].default_value = 999.0; lo.outputs[0].default_value = -999.0
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'BLENDED'
    for fr, v in ((1, 0.0), (NF, -DUR * 0.12)): off.outputs[0].default_value = v; off.outputs[0].keyframe_insert('default_value', frame=fr)
    lin(m.node_tree); return m

BOARD_TEX = os.path.join(AS, 'board_rgba.png')
def mat_board():
    """主板（去塑料感，11-10 用户「很塑料，没有质感」）：暗墨绿哑光阻焊 + 一层清漆；阻焊下的铜略亮、偏橄榄色；
       裸露的金焊盘（ENIG）、白色丝印、过孔微凸；表面细微起伏和粗糙度变化。贴图由 make_board_texture.py 生成"""
    m = bpy.data.materials.new('board'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    geo = N.new('ShaderNodeNewGeometry'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(geo.outputs['Position'], sp.inputs[0])
    u = N.new('ShaderNodeMath'); u.operation = 'MULTIPLY_ADD'; u.inputs[1].default_value = 1 / 120.0; u.inputs[2].default_value = 0.5; L.new(sp.outputs['X'], u.inputs[0])
    v = N.new('ShaderNodeMath'); v.operation = 'MULTIPLY_ADD'; v.inputs[1].default_value = 1 / 120.0; v.inputs[2].default_value = 50 / 120.0; L.new(sp.outputs['Y'], v.inputs[0])
    cm = N.new('ShaderNodeCombineXYZ'); L.new(u.outputs[0], cm.inputs['X']); L.new(v.outputs[0], cm.inputs['Y'])
    t = img(N, BOARD_TEX, 'Non-Color'); t.extension = 'EXTEND'; L.new(cm.outputs[0], t.inputs[0])
    sc_ = N.new('ShaderNodeSeparateColor'); L.new(t.outputs['Color'], sc_.inputs[0])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.5; nz.inputs['Detail'].default_value = 10; L.new(geo.outputs['Position'], nz.inputs['Vector'])
    def mix(fac, a, bcol):
        mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L.new(fac, mx.inputs['Factor'])
        if isinstance(a, tuple): mx.inputs['A'].default_value = (*a, 1)
        else: L.new(a, mx.inputs['A'])
        mx.inputs['B'].default_value = (*bcol, 1); return mx.outputs['Result']
    c = mix(nz.outputs['Fac'], (0.018, 0.105, 0.040), (0.026, 0.135, 0.050))          # 阻焊本身有一点不均匀
    c = mix(sc_.outputs['Red'], c, (0.07, 0.22, 0.075))                               # 阻焊下的铜：略亮、偏橄榄
    c = mix(sc_.outputs['Green'], c, (0.95, 0.68, 0.32))                               # 金焊盘
    c = mix(sc_.outputs['Blue'], c, (0.82, 0.83, 0.80))                                # 丝印
    L.new(c, b.inputs['Base Color']); L.new(sc_.outputs['Green'], b.inputs['Metallic'])
    rr = N.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = 0.30; rr.inputs['To Max'].default_value = 0.46; L.new(nz.outputs['Fac'], rr.inputs['Value'])
    rm = N.new('ShaderNodeMix'); rm.data_type = 'FLOAT'; L.new(sc_.outputs['Green'], rm.inputs['Factor']); L.new(rr.outputs[0], rm.inputs['A']); rm.inputs['B'].default_value = 0.22
    rs = N.new('ShaderNodeMix'); rs.data_type = 'FLOAT'; L.new(sc_.outputs['Blue'], rs.inputs['Factor']); L.new(rm.outputs['Result'], rs.inputs['A']); rs.inputs['B'].default_value = 0.75
    L.new(rs.outputs['Result'], b.inputs['Roughness'])
    cw = N.new('ShaderNodeMath'); cw.operation = 'MULTIPLY'; cw.inputs[1].default_value = 0.55; L.new(sc_.outputs['Red'], cw.inputs[0])   # 清漆：铜上更亮一点
    ca = N.new('ShaderNodeMath'); ca.operation = 'ADD'; ca.inputs[1].default_value = 0.35; L.new(cw.outputs[0], ca.inputs[0]); L.new(ca.outputs[0], b.inputs['Coat Weight'])
    b.inputs['Coat Roughness'].default_value = 0.12
    h = N.new('ShaderNodeMath'); h.operation = 'MULTIPLY_ADD'; h.inputs[1].default_value = 0.6; L.new(sc_.outputs['Red'], h.inputs[0])
    h2 = N.new('ShaderNodeMath'); h2.operation = 'MULTIPLY_ADD'; h2.inputs[1].default_value = 0.08; L.new(nz.outputs['Fac'], h2.inputs[0]); L.new(h.outputs[0], h2.inputs[2])
    L.new(t.outputs['Alpha'], h.inputs[2])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.35; bp.inputs['Distance'].default_value = 0.02; L.new(h2.outputs[0], bp.inputs['Height']); L.new(bp.outputs[0], b.inputs['Normal'])
    return m
def mat_brushed(name, col=(0.72, 0.73, 0.75)):
    """拉丝铝（散热片）：沿鳍片长度方向的细拉丝纹，粗糙度有变化，各向异性高光"""
    m = mat(name, col, 1.0, 0.3); N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (40.0, 0.4, 40.0); L.new(tc.outputs['Object'], mp.inputs[0])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 6.0; nz.inputs['Detail'].default_value = 12; L.new(mp.outputs[0], nz.inputs['Vector'])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 0.22; mr.inputs['To Max'].default_value = 0.42; L.new(nz.outputs['Fac'], mr.inputs['Value']); L.new(mr.outputs[0], b.inputs['Roughness'])
    if 'Anisotropic' in b.inputs: b.inputs['Anisotropic'].default_value = 0.7
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.15; bp.inputs['Distance'].default_value = 0.01; L.new(nz.outputs['Fac'], bp.inputs['Height']); L.new(bp.outputs[0], b.inputs['Normal'])
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
_BK = {}
def bokeh_lights(n, center, spread, size, cols, strength=(4, 12)):
    for i in range(n):
        c = random.choice(cols)
        if c not in _BK: _BK[c] = emit(f'bk{len(_BK)}', c, sum(strength) / 2)[0]
        m = _BK[c]
        o_ = sphere(f'bk{i}', size * random.uniform(0.6, 1.4), m, (center[0] + random.uniform(-spread[0], spread[0]), center[1] + random.uniform(-spread[1], spread[1]), center[2] + random.uniform(-spread[2], spread[2])))
        o_.visible_glossy = False          # 背景灯只当虚化背景，不在手机玻璃上反光（审核：白点压字）
def key(o, path, fr, val):
    setattr(o, path, val); o.keyframe_insert(path, frame=fr)
def dust_near_camera(n, dmin, dmax, size):
    """前景灰尘：挂在相机上（相机本地坐标），离镜头很近、虚成光斑，慢慢漂；画面左右两侧，不压画面中间的关键内容
       （渲染包审核：原来按片尾机位摆，前 1.8 秒全在画外；横向偏移超出视野）"""
    dm = bpy.data.materials.new('dust'); dm.use_nodes = True; Nd = dm.node_tree.nodes; Ld = dm.node_tree.links
    for x_ in list(Nd): Nd.remove(x_)
    od = Nd.new('ShaderNodeOutputMaterial'); ed = Nd.new('ShaderNodeEmission'); ed.inputs['Color'].default_value = (1.0, 0.86, 0.66, 1); ed.inputs['Strength'].default_value = 1.2
    td = Nd.new('ShaderNodeBsdfTransparent'); md = Nd.new('ShaderNodeMixShader'); md.inputs['Fac'].default_value = 0.18     # 半透明的暖色小光斑（复核：像水渍）
    Ld.new(td.outputs[0], md.inputs[1]); Ld.new(ed.outputs[0], md.inputs[2]); Ld.new(md.outputs[0], od.inputs[0])
    if hasattr(dm, 'surface_render_method'): dm.surface_render_method = 'BLENDED'
    for i in range(n):
        d = random.uniform(dmin, dmax); x = (-1 if i % 2 else 1) * random.uniform(0.12, 0.22) * d; y = random.uniform(-0.6, 0.6) * d
        s = sphere(f'dust{i}', size * random.uniform(0.6, 1.3), dm, (x, y, -d)); s.parent = cam; s.visible_glossy = False
        drift = Vector((random.uniform(-1, 1), random.uniform(-1, 1), 0)) * d * 0.05
        key(s, 'location', 1, Vector((x, y, -d))); key(s, 'location', NF, Vector((x, y, -d)) + drift); lin(s)

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
    BOOK = [mat(f'book{k}', c, 0, 0.6) for k, c in enumerate([(0.35, 0.12, 0.08), (0.1, 0.2, 0.3), (0.5, 0.45, 0.35), (0.15, 0.25, 0.15)])]
    for i in range(9): box(f'book{i}', 28 + random.uniform(0, 20), 180, random.uniform(150, 230), random.choice(BOOK), (-650 + i * 75, 1000, 480))
    bokeh_lights(18, (0, 1060, 820), (1500, 20, 120), 10, [(1.0, 0.78, 0.5), (1.0, 0.88, 0.65)], strength=(2, 5))
    sig_m, _ = emit('signal_A', GOLD, 160.0); sig = sphere('signal', 5.0, sig_m, (0, 0, 0))
    halo_m, _ = emit('signal_halo', GOLD, 6.0); halo = sphere('signal_halo', 14.0, halo_m, (0, 0, 0)); halo.parent = sig
    sl = bpy.data.lights.new('signal_light', 'POINT'); sl.color = GOLD; sl.shadow_soft_size = 5; obj('signal_light', sl).parent = sig
    for t, v in ((0.0, 0.0), (1.5, 0.0), (1.6, 3e4)): sl.energy = v; sl.keyframe_insert('energy', frame=F(t))   # 信号出现之前不亮（复核：手机顶上提前多一个亮点）
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
    BOARD_M = mat_board()
    plane('board', 400, 400, BOARD_M, (0, 60, 0))
    mask_cu = mat('mask_over_copper', (0.10, 0.42, 0.13), 0.15, 0.28, coat=0.5)
    PAIR_X = [0.0] + [s * d for d in (1.3, 2.6, 3.9, 5.2, 7.5, 9.8) for s in (-1, 1)]
    # 走线、焊盘、过孔、丝印都在主板贴图里（阻焊下几乎是平的，只有很浅的起伏；原来凸起的方块像塑料条）
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
    boxes('caps_body', caps, mat('mlcc', (0.30, 0.22, 0.14), 0, 0.45, coat=0.15, noise_bump=0.1, noise_scale=8)); boxes('caps_ends', ends, mat('tin', (0.8, 0.8, 0.82), 1.0, 0.3))
    # 电容焊盘在主板贴图里
    # 过孔：圆的，被阻焊盖住（只是微微鼓起、颜色深一点）
    tent = mat('tented_via', (0.03, 0.18, 0.06), 0.0, 0.3, coat=0.5)
    # 过孔在主板贴图里
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
        box('hs_base', 46, 46, 3.0, mat_brushed('fin'), (0, 92, 5.7), bev=0.3)
        FIN = mat_brushed('fin2', (0.76, 0.77, 0.79))
        for k in range(27): box(f'fin{k}', 0.5, 46, 40 * (1 - 0.02 * (k % 3)), FIN, (-21 + k * 1.6, 92, 7.2 + 20), bev=0.12)
    ind = mat('inductor', (0.06, 0.06, 0.065), 0.2, 0.5)
    boxes('inductors', [(sx * (45 + k * 11), 70 + r * 13, 2.5, 9, 9, 5) for sx in (-1, 1) for k in range(3) for r in range(3)], ind)
    # 机箱：两侧壁、后面一排风扇（轮毂 + 扇叶）、天花板上数据中心的灯带；再远处是雾（合成里的空气透视）
    chassis = mat('chassis', (0.16, 0.17, 0.19), 0.8, 0.45, noise_bump=0.02, noise_scale=0.05)
    box('fan_wall', 400, 6, 60, chassis, (0, 196, 30)); box('wall_L', 6, 400, 60, chassis, (-110, 60, 30)); box('wall_R', 6, 400, 60, chassis, (110, 60, 30))
    blade = mat('fan_blade', (0.04, 0.04, 0.045), 0.1, 0.45); FAN_RING = mat('fan_ring', (0.02, 0.02, 0.022), 0.1, 0.5)
    for k in range(6):
        cx = -150 + k * 60
        cyl(f'fan_ring{k}', 27, 3, FAN_RING, (cx, 190, 30), (math.radians(90), 0, 0))
        cyl(f'fan_hub{k}', 9, 6, blade, (cx, 187, 30), (math.radians(90), 0, 0))
        for i in range(7):
            a = i * 2 * math.pi / 7; box(f'fan_blade{k}_{i}', 13, 1.0, 7, blade, (cx + math.cos(a) * 15, 186.5, 30 + math.sin(a) * 15), (0, -a, 0))
    ceil_m, _ = emit('ceiling_light', (0.85, 0.95, 1.0), 2.5)
    for r in range(6): box(f'ceil{r}', 900, 30, 4, ceil_m, (0, 150 + r * 260, 900))
    LED = [emit('led_g', (0.3, 1.0, 0.45), 80)[0], emit('led_b', (0.45, 0.7, 1.0), 80)[0]]
    for i in range(30):
        sphere(f'led{i}', 1.6, LED[i % 2], (random.uniform(-160, 160), 192, random.uniform(5, 55)))
    BTEX = {'normal': 'bits.png', 'long': 'bits_long.png', 'blur': 'bits_blur.png'}[OPT.get('bits', 'normal')]
    plane('signal_band', 0.32, TR_Y1 - 2 - TR_Y0, mat_signal(BTEX), (0, (TR_Y0 + TR_Y1 - 2) / 2, 0.045))
    POSE = OPT.get('pose', 'B')
    if OPT.get('host') == '1': standee(POSE, STAND_H if POSE == 'A' else STAND_H * 0.62, (-0.75, 5.5, 0.0), math.radians(-25))   # 用户 11-10：去掉人物（不协调、显得假）
    sig_m, _ = emit('signal_B', GOLD, 60.0); sig = sphere('signal', 0.25, sig_m, (0, 0, 0))
    SIG_PATH = ((0.0, (0, -14, 9.0)), (0.45, (0, -6, 4.0)), (0.9, (0, 0.0, 0.06)), (1.5, (0, 14, 0.06)))
    for t, p in SIG_PATH: key(sig, 'location', F(t), p)
    for t, s in ((0.0, 1.0), (0.9, 1.0), (1.2, 0.35), (1.5, 0.0)): key(sig, 'scale', F(t), (s, s, s))
    SIDE_CAM, SIDE_TGT = (-3.6, 2.6, 0.95), (0.3, 8.0, 0.35)
    # 0–1.0 秒：镜头在信号后上方追着它，信号一直在画面中间；1.0–4.0 秒：降到板面，落到 side 机位（和 y3 的背景是同一个机位）
    for t, p, g in ((0.0, (0, -26, 15.0), (0, -14, 9.0)), (0.45, (-0.3, -18, 8.5), (0, -6, 4.0)), (1.0, (-1.2, -11, 4.0), (0, 1.5, 0.1)),
                    (2.4, (-3.0, -2.5, 1.6), (0.2, 6.0, 0.25)), (4.0, SIDE_CAM, SIDE_TGT)):
        key(cam, 'location', F(t), p); key(tgt, 'location', F(t), g)
    cam_d.lens = 28; cam_d.dof.aperture_fstop = 2.8
    sun = bpy.data.lights.new('key', 'AREA'); sun.energy = 1.4e5; sun.size = 120; sun.color = (1.0, 0.88, 0.75)
    obj('key', sun, None, (-80, -40, 120), (math.radians(35), math.radians(-30), 0))
    rim = bpy.data.lights.new('rim', 'AREA'); rim.energy = 1.6e5; rim.size = 90; rim.color = (0.65, 0.8, 1.0)
    obj('rim', rim, None, (40, 220, 60), (math.radians(-70), 0, math.radians(170)))
    MIST = (18, 260, (0.08, 0.26, 0.28))

VIEWS = {   # 中间讲解段的固定机位（2.5D 背景）：相机位置、看向哪里、焦距、光圈
    'side': ((-3.6, 2.6, 0.95), (0.3, 8.0, 0.35), 28, 2.8),     # 走线和信号斜着伸向远处的芯片（= B 段最后一帧的机位）
    'close': ((-0.55, 10.0, 0.55), (0.05, 16.0, 0.03), 35, 2.8), # 贴着信号往前看：越快越糊（y10 第一段、y14）
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
    if OPT.get('noband') == '1': bpy.data.objects['signal_band'].hide_render = True
    FRAMES = FRAMES or [60]
# 前景灰尘不在 Blender 里放：EEVEE 试渲里半透明灰尘没被景深虚掉，成了清晰的圆片（用户 11-10 试渲）；整片统一由云端加会漂的 2D 虚化光斑

# ---------- 世界、渲染、合成（空气透视 + 光的辉光） ----------
wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True; N = wd.node_tree.nodes; L = wd.node_tree.links
bg = N['Background']; bg.inputs['Strength'].default_value = 0.35 if SHOT == 'A' else 0.15
if os.path.exists(HDRI):
    env = N.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(HDRI); L.new(env.outputs['Color'], bg.inputs['Color'])
lp = N.new('ShaderNodeLightPath'); mx = N.new('ShaderNodeMixShader'); dark = N.new('ShaderNodeBackground'); dark.inputs['Color'].default_value = (*MIST[2], 1)
out = N['World Output']; L.new(lp.outputs['Is Camera Ray'], mx.inputs['Fac']); L.new(bg.outputs[0], mx.inputs[1]); L.new(dark.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs[0])
if CYCLES:
    sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMP; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 6; sc.cycles.device = 'CPU'
    if GPU:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for dt in ('OPTIX', 'CUDA'):
            try:
                prefs.compute_device_type = dt; prefs.refresh_devices()
                if [d for d in prefs.devices if d.type == dt]:
                    for d in prefs.devices: d.use = d.type == dt
                    sc.cycles.device = 'GPU'; print('CYCLES_DEVICE', dt); break
            except Exception as e: print('显卡设置跳过', dt, e)
else:
    ENG = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    sc.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in ENG else 'BLENDER_EEVEE_NEXT'; sc.eevee.taa_render_samples = SAMP
    DOF_K = 0.025   # EEVEE 试渲：远处散热片都是清楚的，光圈没按毫米单位换算；按审核建议缩小到约 1/40
    cam_d.dof.aperture_fstop *= DOF_K; print('EEVEE 景深光圈', round(cam_d.dof.aperture_fstop, 4))
    for k, v in (('use_raytracing', SHOT == 'B'), ('use_shadows', True), ('use_fast_gi', SHOT == 'B'), ('bokeh_max_size', 300.0), ('motion_blur_max', 120)):
        try: setattr(sc.eevee, k, v)
        except Exception as e: print('EEVEE 设置跳过', k, e)
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, NF
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 1.0 if SHOT == 'A' else 0.5
sc.view_settings.view_transform = 'AgX'; sc.view_settings.exposure = 0.9 if SHOT == 'B' else 0.2
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
if CLOUD:   # 云端草稿：没有 libEGL，合成节点会让 Blender 直接退出；改用很淡的体积雾做空气透视
    vm = bpy.data.materials.new('haze'); vm.use_nodes = True; Nn = vm.node_tree.nodes; Ln = vm.node_tree.links
    for n in list(Nn): Nn.remove(n)
    vo = Nn.new('ShaderNodeOutputMaterial'); vs = Nn.new('ShaderNodeVolumeScatter'); vs.inputs['Density'].default_value = 0.6 / MIST[1]
    vs.inputs['Color'].default_value = (*MIST[2], 1); Ln.new(vs.outputs[0], vo.inputs['Volume'])
    hb = box('haze_box', 1, 1, 1, vm, (0, 0, 0)); c0 = cam.location
    hb.scale = (MIST[1] * 6, MIST[1] * 6, MIST[1] * 6); hb.location = (c0.x, c0.y + MIST[1] * 2.5, c0.z)
    if SHOT == 'B' and 'view' not in OPT: hb.location = (0, 60, 0)
else:
  try:
    if bpy.app.version < (5, 0, 0): raise SystemExit('需要 Blender 5.0 或更新版本（现在是 ' + bpy.app.version_string + '）')
    vl = sc.view_layers[0]; vl.use_pass_mist = True; vl.use_pass_emit = True
    wd.mist_settings.start = MIST[0]; wd.mist_settings.depth = MIST[1]; wd.mist_settings.falloff = 'QUADRATIC'
    ng = bpy.data.node_groups.new('comp', 'CompositorNodeTree'); sc.compositing_node_group = ng
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new('CompositorNodeRLayers'); rl.scene = sc
    gl = ng.nodes.new('CompositorNodeGlare'); ng.links.new(rl.outputs.get('Emit') or rl.outputs.get('Emission'), gl.inputs['Image'])
    for k, v in (('Type', 'Bloom'), ('Threshold', 0.2 if SHOT == 'B' else 1.5), ('Strength', 0.8), ('Size', 0.6), ('Quality', 'High')):   # A 段阈值高：手机屏幕也是自发光，别把字糊掉
        try: gl.inputs[k].default_value = v
        except Exception as e: print('辉光参数跳过', k, e)
    add = ng.nodes.new('ShaderNodeMix'); add.data_type = 'RGBA'; add.blend_type = 'ADD'; add.inputs['Factor'].default_value = 1.0
    ng.links.new(rl.outputs['Image'], add.inputs['A']); ng.links.new(gl.outputs['Glare'], add.inputs['B'])
    hz = ng.nodes.new('ShaderNodeMath'); hz.operation = 'MULTIPLY'; hz.inputs[1].default_value = 0.35 if SHOT == 'B' else 0.6; ng.links.new(rl.outputs['Mist'], hz.inputs[0])   # EEVEE 试渲：背景被雾糊成一片平灰，减半
    fog = ng.nodes.new('ShaderNodeMix'); fog.data_type = 'RGBA'; fog.blend_type = 'MIX'; ng.links.new(hz.outputs[0], fog.inputs['Factor'])
    ng.links.new(add.outputs['Result'], fog.inputs['A']); fog.inputs['B'].default_value = (*MIST[2], 1)
    go = ng.nodes.new('NodeGroupOutput'); ng.links.new(fog.outputs['Result'], go.inputs[0]); print('COMPOSITOR 辉光 + 空气透视已接上')
  except Exception as e: print('[!] 合成节点出错（雾和辉光接不上），先停下：', e); raise SystemExit(1)
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
    json.dump(dict(W=W, H=H, bit_mm=BIT, pts=pts), open(path, 'w'))
if OPT.get('check') == '1':     # 自查：逐帧列出信号、灰尘在画面上的位置（不渲染）；EEVEE 分支下也打印合成节点的连线
    if sc.compositing_node_group:
        for lk in sc.compositing_node_group.links: print('LINK', lk.from_node.bl_idname, lk.from_socket.name, '→', lk.to_node.bl_idname, lk.to_socket.name)
    dl = [o for o in bpy.data.objects if o.name.startswith('dust')]; sg = bpy.data.objects.get('signal')
    for f in range(1, NF + 1):
        sc.frame_set(f); c = world_to_camera_view(sc, cam, sg.matrix_world.translation) if sg else None
        n_in = sum(1 for o in dl if (lambda v: v.z > 0 and 0 <= v.x <= 1 and 0 <= v.y <= 1)(world_to_camera_view(sc, cam, o.matrix_world.translation)))
        print(f'CHECK {SHOT} f{f:03d} signal=({c.x * W:.0f},{(1 - c.y) * H:.0f},z{c.z:.1f}) scale={sg.scale.x:.2f} dust_in={n_in}/{len(dl)}' if c else f'CHECK f{f}')
    raise SystemExit(0)
import time
def _gpu_name():
    try:
        import gpu; return gpu.platform.renderer_get()
    except Exception as e: return f'（查不到：{e}）'
if SEQ:      # 整段序列：已渲的帧跳过，每帧打印耗时
    d_ = os.path.join(OUT, SHOT); os.makedirs(d_, exist_ok=True); t0 = [time.time()]
    def _pre(scene, *a): t0[0] = time.time()
    def _post(scene, *a): print(f'FRAME_TIME 第 {scene.frame_current} 帧：{time.time() - t0[0]:.1f} 秒', flush=True)
    bpy.app.handlers.render_pre.append(_pre); bpy.app.handlers.render_post.append(_post)
    for fn in os.listdir(d_):
        fp = os.path.join(d_, fn)
        if fn.lower().endswith('.png') and os.path.getsize(fp) < 10000: os.remove(fp); print('删掉不完整的帧', fn)
    sc.render.filepath = os.path.join(d_, '####'); sc.render.use_overwrite = False; sc.render.use_placeholder = False
    bpy.ops.render.render(animation=True); print('GPU', _gpu_name()); print('SEQ_DONE', SHOT, NF)
else:
  for f in FRAMES or [1]:
    t_ = time.time(); sc.frame_set(f)
    name = (f"{SHOT}_{OPT['view']}_{OPT.get('bits', 'normal')}" + ('_xray' if OPT.get('xray') == '1' else '') + ('_noband' if OPT.get('noband') == '1' else '')) if 'view' in OPT else f'{SHOT}_f{f:04d}'
    if 'garble' in OPT: name += f"_g{OPT['garble']}"
    fp_ = os.path.join(OUT, name + '.png')
    if 'view' in OPT and os.path.exists(fp_) and os.path.getsize(fp_) > 10000 and os.path.exists(os.path.join(OUT, name + '.json')): print('已渲过，跳过', name); continue
    sc.render.filepath = fp_; bpy.ops.render.render(write_still=True); print('RENDERED', sc.render.filepath)
    print(f'FRAME_TIME {name}：{time.time() - t_:.1f} 秒', flush=True); print('GPU', _gpu_name())
    if 'view' in OPT: export_band(os.path.join(OUT, name + '.json'))
