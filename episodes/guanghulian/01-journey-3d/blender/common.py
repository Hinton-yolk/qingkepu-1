# 光互连 01（3D 版）· Blender 公共库。所有镜头脚本都从这里取：时间轴、命令行参数、材质、建模、相机、标注锚点、渲染。
# 约定：
#   · 时间一律用「全片时间（秒）」，帧号一律用全片帧号：帧 = round(秒 × fps) + 1。镜头起止只从 timeline/timeline.json 读。
#   · 每个镜头一个场景脚本（sNN_*.py），自带 build() 和相机动画，可单独运行：
#       blender -b --python-exit-code 1 --python s02_gpu_package.py -- <输出目录> [--res 270x480] [--samples 24]
#               [--times 13.5,16,19 | --frames 400,450 | --range 391 690 [--step 2]] [--gpu] [--anchors] [--save-blend]
#   · 颜色语义：金 = 电信号，青 = 光，珊瑚 = 出错 / 强调。硬件本体不用这三种颜色发光。
#   · 发光的信号材质都写 AOV「lightmask」，合成时辉光只加在遮罩内（光约束在芯区，不外溢）。
import bpy, bmesh, math, sys, json, os, time, argparse
from mathutils import Vector, Matrix, Euler
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TL = json.load(open(os.path.join(ROOT, 'timeline', 'timeline.json'), encoding='utf-8'))
FPS = TL['meta']['fps']
ASSETS_DL = os.path.join(HERE, 'assets_dl')           # 下载的 CC0 素材（不进仓库）
FONT = os.path.join(ROOT, '..', 'blender_test_scale', 'assets', 'label_font.otf')

GOLD = (1.00, 0.62, 0.14)      # 电
CYAN = (0.20, 0.95, 0.85)      # 光
CORAL = (1.00, 0.33, 0.26)     # 出错 / 强调

def F(t):
    """全片时间（秒）→ 全片帧号"""
    return round(t * FPS) + 1

class Shot:
    def __init__(self, sid):
        s = next(x for x in TL['shots'] if x['id'] == sid)
        self.id = sid; self.t0 = s['start']; self.t1 = s['end']; self.f0 = F(s['start']); self.f1 = round(s['end'] * FPS)
        self.data = s
    def u(self, t):
        """镜头内的归一化时间 0–1"""
        return (t - self.t0) / (self.t1 - self.t0)

def parse_args():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument('out'); p.add_argument('--res', default='270x480'); p.add_argument('--samples', type=int, default=24)
    p.add_argument('--times', default='', help='逗号分隔的全片时间（秒）'); p.add_argument('--frames', default='', help='逗号分隔的全片帧号')
    p.add_argument('--range', nargs=2, type=int); p.add_argument('--step', type=int, default=1)
    p.add_argument('--gpu', action='store_true'); p.add_argument('--anchors', action='store_true'); p.add_argument('--save-blend', action='store_true')
    p.add_argument('--no-render', action='store_true')
    return p.parse_args(argv)

# ---------- 场景 ----------
def reset(shot):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.frame_start = shot.f0; sc.frame_end = shot.f1; sc.render.fps = FPS
    print('BLENDER_VERSION', bpy.app.version_string, '| SHOT', shot.id, 'frames', shot.f0, shot.f1)
    return sc

def collection(name, parent=None):
    c = bpy.data.collections.new(name); (parent or bpy.context.scene.collection).children.link(c); return c

def link(obj, col=None):
    (col or bpy.context.scene.collection).objects.link(obj); return obj

def empty(name, loc=(0, 0, 0), col=None):
    e = bpy.data.objects.new(name, None); e.location = loc; e.empty_display_size = 0.01; return link(e, col)

def instance(src, name, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), col=None):
    """共享网格的实例（省内存）"""
    o = bpy.data.objects.new(name, src.data); o.location = loc; o.rotation_euler = rot; o.scale = scale; return link(o, col)

def instance_collection(src_col, name, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), col=None):
    o = bpy.data.objects.new(name, None); o.instance_type = 'COLLECTION'; o.instance_collection = src_col
    o.location = loc; o.rotation_euler = rot; o.scale = scale; return link(o, col)

def hide_collection(col):
    """把只当实例源用的集合从视图层里排除（实例仍然渲染）"""
    def walk(lc):
        if lc.collection == col: lc.exclude = True; return True
        return any(walk(ch) for ch in lc.children)
    walk(bpy.context.view_layer.layer_collection)

# ---------- 建模：把很多小零件攒进一个网格 ----------
class Mesh:
    """用法：m = Mesh(); m.box(...); m.cyl(...); obj = m.obj('名字', 材质, col)"""
    def __init__(self): self.bm = bmesh.new()
    def box(self, size, loc=(0, 0, 0), rot=None):
        r = bmesh.ops.create_cube(self.bm, size=1.0); vs = r['verts']
        mat = Matrix.LocRotScale(Vector(loc), Euler(rot) if rot else None, Vector(size))
        bmesh.ops.transform(self.bm, matrix=mat, verts=vs); return vs
    def cyl(self, r, h, loc=(0, 0, 0), rot=None, seg=24, r2=None):
        res = bmesh.ops.create_cone(self.bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h); vs = res['verts']
        mat = Matrix.LocRotScale(Vector(loc), Euler(rot) if rot else None, None)
        bmesh.ops.transform(self.bm, matrix=mat, verts=vs); return vs
    def sphere(self, r, loc=(0, 0, 0), scale=(1, 1, 1), seg=24):
        res = bmesh.ops.create_uvsphere(self.bm, u_segments=seg, v_segments=seg // 2, radius=r); vs = res['verts']
        bmesh.ops.transform(self.bm, matrix=Matrix.LocRotScale(Vector(loc), None, Vector(scale)), verts=vs); return vs
    def path(self, pts, w, h):
        """沿折线（各段平行于坐标轴）铺矩形截面的线：走线、导线用"""
        for a, b in zip(pts, pts[1:]):
            a = Vector(a); b = Vector(b); d = b - a; c = (a + b) / 2
            sx = abs(d.x) + w if abs(d.x) > 1e-9 else w; sy = abs(d.y) + w if abs(d.y) > 1e-9 else w
            sz = abs(d.z) + h if abs(d.z) > 1e-9 else h
            self.box((sx, sy, sz), c)
    def obj(self, name, material=None, col=None, bevel=0.0, smooth=False, loc=(0, 0, 0)):
        me = bpy.data.meshes.new(name); self.bm.to_mesh(me); self.bm.free(); o = bpy.data.objects.new(name, me); o.location = loc
        if material: me.materials.append(material)
        if smooth:
            for p in me.polygons: p.use_smooth = True
        if bevel > 0:
            b = o.modifiers.new('bevel', 'BEVEL'); b.width = bevel; b.segments = 2; b.limit_method = 'ANGLE'; b.angle_limit = math.radians(40)
            b.harden_normals = True
        return link(o, col)

def box(name, size, loc=(0, 0, 0), material=None, col=None, bevel=0.0, rot=None):
    m = Mesh(); m.box(size, (0, 0, 0)); o = m.obj(name, material, col, bevel); o.location = loc
    if rot: o.rotation_euler = rot
    return o

def cyl(name, r, h, loc=(0, 0, 0), material=None, col=None, rot=None, seg=32, bevel=0.0):
    m = Mesh(); m.cyl(r, h, seg=seg); o = m.obj(name, material, col, bevel, smooth=True); o.location = loc
    if rot: o.rotation_euler = rot
    return o

def curve_tube(name, pts, radius, material=None, col=None, res=8, cyclic=False):
    """沿若干点的平滑曲线管：跳线、光纤、头发用"""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = radius; cu.bevel_resolution = 3; cu.resolution_u = res
    sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    sp.use_endpoint_u = True; sp.order_u = min(4, len(pts)); sp.use_cyclic_u = cyclic
    o = bpy.data.objects.new(name, cu)
    if material: cu.materials.append(material)
    return link(o, col)

def text3d(name, body, size, loc, material, rot=(math.radians(90), 0, 0), extrude=0.04, col=None, align='CENTER'):
    """场景里的立体字（尺度数字用）。extrude 是相对字号的厚度"""
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.size = size; cu.extrude = size * extrude; cu.align_x = align; cu.align_y = 'CENTER'
    if os.path.exists(FONT): cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    o = bpy.data.objects.new(name, cu); o.location = loc; o.rotation_euler = rot
    if material: cu.materials.append(material)
    return link(o, col)

# ---------- 材质 ----------
def _nodes(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; return m, m.node_tree.nodes, m.node_tree.links

def _fade(m, N, L, base_alpha, socket):
    """透明度 × 物体颜色的 alpha：给 obj.color[3] 打关键帧就能淡入淡出"""
    oi = N.new('ShaderNodeObjectInfo'); mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = base_alpha
    L.new(oi.outputs['Alpha'], mul.inputs[0]); L.new(mul.outputs[0], socket)
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'BLENDED' if base_alpha < 1 else 'DITHERED'

def pbr(name, color, metallic=0.0, rough=0.5, alpha=1.0, coat=0.0, transmission=0.0, ior=1.45, emission=None, emission_strength=0.0,
        noise_scale=0.0, noise_rough=0.12, bump=0.0, stretch=(1, 1, 1), fade=False):
    """通用写实材质。noise_scale > 0 时用程序噪声扰动粗糙度（和凹凸），避免「塑料玩具」的均匀高光；stretch 把噪声拉成拉丝纹。"""
    m, N, L = _nodes(name); b = N['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Metallic'].default_value = metallic; b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat; b.inputs['IOR'].default_value = ior
    if transmission: b.inputs['Transmission Weight'].default_value = transmission
    if emission: b.inputs['Emission Color'].default_value = (*emission, 1); b.inputs['Emission Strength'].default_value = emission_strength
    if noise_scale > 0:
        tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = tuple(noise_scale * s for s in stretch)
        nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.0; nz.inputs['Detail'].default_value = 6.0
        L.new(tc.outputs['Object'], mp.inputs['Vector']); L.new(mp.outputs[0], nz.inputs['Vector'])
        mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = max(0.02, rough - noise_rough); mr.inputs['To Max'].default_value = min(1.0, rough + noise_rough)
        L.new(nz.outputs['Fac'], mr.inputs['Value']); L.new(mr.outputs[0], b.inputs['Roughness'])
        if bump:
            bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; L.new(nz.outputs['Fac'], bp.inputs['Height']); L.new(bp.outputs[0], b.inputs['Normal'])
    if fade or alpha < 1: _fade(m, N, L, alpha, b.inputs['Alpha'])
    return m

def emit(name, color, strength=2.0, aov=True, fade=False):
    """发光的信号材质（金 = 电，青 = 光）。强度可打关键帧：material.node_tree.nodes['Emission'].inputs['Strength']"""
    m, N, L = _nodes(name)
    for n in list(N): N.remove(n)
    o = N.new('ShaderNodeOutputMaterial'); e = N.new('ShaderNodeEmission'); e.name = 'Emission'
    e.inputs['Color'].default_value = (*color, 1); e.inputs['Strength'].default_value = strength
    if fade:
        tr = N.new('ShaderNodeBsdfTransparent'); mx = N.new('ShaderNodeMixShader'); L.new(tr.outputs[0], mx.inputs[1]); L.new(e.outputs[0], mx.inputs[2])
        L.new(mx.outputs[0], o.inputs[0]); _fade(m, N, L, 1.0, mx.inputs['Fac'])
    else: L.new(e.outputs[0], o.inputs[0])
    if aov:
        a = N.new('ShaderNodeOutputAOV'); a.aov_name = 'lightmask'; a.inputs['Value'].default_value = 1.0
    return m

def emit_pattern(name, color, axis='X', strength=3.0, base=0.06, speed_node=True):
    """沿线分布的亮暗图样（电压 / 光强的空间分布示意）：沿物体坐标 axis 方向，用一张 1×N 的位图决定哪一段亮。
    返回 (材质, 位图图像, 偏移值节点)。位图像素 = 一个符号；偏移值打关键帧让图样沿线前进。
    节点名：'pattern_scale'（Value：每个物体单位里有几个符号）、'pattern_offset'（Value：平移，单位是符号数）、'blur'（Value：0–1，沿线越糊）。"""
    m, N, L = _nodes(name)
    for n in list(N): N.remove(n)
    out = N.new('ShaderNodeOutputMaterial'); e = N.new('ShaderNodeEmission'); e.name = 'Emission'; e.inputs['Color'].default_value = (*color, 1)
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])
    sc = N.new('ShaderNodeValue'); sc.name = 'pattern_scale'; sc.outputs[0].default_value = 1.0
    off = N.new('ShaderNodeValue'); off.name = 'pattern_offset'
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; L.new(sep.outputs[axis], mul.inputs[0]); L.new(sc.outputs[0], mul.inputs[1])
    sub = N.new('ShaderNodeMath'); sub.operation = 'SUBTRACT'; L.new(mul.outputs[0], sub.inputs[0]); L.new(off.outputs[0], sub.inputs[1])
    img = bpy.data.images.new(name + '_bits', 64, 1); img.colorspace_settings.name = 'Non-Color'
    dv = N.new('ShaderNodeMath'); dv.operation = 'DIVIDE'; dv.inputs[1].default_value = 64.0; L.new(sub.outputs[0], dv.inputs[0])
    cmb = N.new('ShaderNodeCombineXYZ'); L.new(dv.outputs[0], cmb.inputs['X']); cmb.inputs['Y'].default_value = 0.5
    it = N.new('ShaderNodeTexImage'); it.image = img; it.interpolation = 'Closest'; it.extension = 'REPEAT'; it.name = 'bits'; L.new(cmb.outputs[0], it.inputs[0])
    it2 = N.new('ShaderNodeTexImage'); it2.image = img; it2.interpolation = 'Cubic'; it2.extension = 'REPEAT'; it2.name = 'bits_soft'; L.new(cmb.outputs[0], it2.inputs[0])
    bl = N.new('ShaderNodeValue'); bl.name = 'blur'
    mx = N.new('ShaderNodeMix'); mx.data_type = 'FLOAT'; L.new(bl.outputs[0], mx.inputs['Factor']); L.new(it.outputs['Color'], mx.inputs['A']); L.new(it2.outputs['Color'], mx.inputs['B'])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = base * strength; mr.inputs['To Max'].default_value = strength
    L.new(mx.outputs['Result'], mr.inputs['Value']); L.new(mr.outputs[0], e.inputs['Strength']); L.new(e.outputs[0], out.inputs[0])
    a = N.new('ShaderNodeOutputAOV'); a.aov_name = 'lightmask'; L.new(mx.outputs['Result'], a.inputs['Value'])
    return m, img, off

def set_bits(img, bits):
    """把 0/1 序列写进位图（长度不足 64 时循环）"""
    px = []
    for i in range(img.size[0]):
        v = float(bits[i % len(bits)]); px += [v, v, v, 1.0]
    img.pixels[:] = px; img.pack()

def key_value(node_or_socket, keys, interp='LINEAR'):
    """给 Value 节点或输入插口打关键帧：keys = [(全片秒, 值), …]"""
    sock = node_or_socket.outputs[0] if hasattr(node_or_socket, 'outputs') and not hasattr(node_or_socket, 'default_value') else node_or_socket
    for t, v in keys: sock.default_value = v; sock.keyframe_insert('default_value', frame=F(t))
    set_interp(sock.id_data, interp)

def key_fade(obj, keys):
    """物体淡入淡出：keys = [(全片秒, alpha), …]。注意：alpha 到 0 以后物体仍参与渲染（只是全透明），
    层数多时要调高 cycles.transparent_max_bounces，或像 s01 的 fade_out() 那样另打 hide_render 关键帧。"""
    for t, a in keys:
        obj.color = (1, 1, 1, a); obj.keyframe_insert('color', frame=F(t))
    set_interp(obj, 'LINEAR')

def fcurves_of(idb):
    ad = idb.animation_data
    if not ad or not ad.action: return []
    act = ad.action
    if hasattr(act, 'fcurves'): return list(act.fcurves)
    out = []
    for layer in act.layers:
        for strip in layer.strips:
            for cb in strip.channelbags: out += list(cb.fcurves)
    return out

def set_interp(idb, kind):
    for fc in fcurves_of(idb):
        for kp in fc.keyframe_points: kp.interpolation = kind

# ---------- 缓动 ----------
def clamp01(x): return max(0.0, min(1.0, x))
def smooth(x): x = clamp01(x); return x * x * (3 - 2 * x)
def smoother(x): x = clamp01(x); return x * x * x * (x * (6 * x - 15) + 10)
def lerp(a, b, u): return a + (b - a) * u
def loglerp(a, b, u): return math.exp(lerp(math.log(a), math.log(b), u))
def vlerp(a, b, u): return Vector(a).lerp(Vector(b), u)
def seg(t, t0, t1): return clamp01((t - t0) / (t1 - t0))

# ---------- 相机 ----------
def add_camera(name='cam', lens=35.0, fstop=None, clip=(0.01, 1000.0)):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36.0; cd.clip_start, cd.clip_end = clip
    cam = link(bpy.data.objects.new(name, cd)); tgt = empty(name + '_target')
    c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    if fstop: cd.dof.use_dof = True; cd.dof.focus_object = tgt; cd.dof.aperture_fstop = fstop
    bpy.context.scene.camera = cam; return cam, tgt

def animate_camera(cam, tgt, fn, shot, step=1):
    """fn(全片秒) → dict(loc=, tgt=, lens=可选, fstop=可选)。每 step 帧采样一次、线性插值，路径完全由 fn 决定（对数推进也准）。"""
    f = shot.f0
    frames = list(range(shot.f0, shot.f1 + 1, step))
    if frames[-1] != shot.f1: frames.append(shot.f1)
    for f in frames:
        d = fn((f - 1) / FPS)
        cam.location = d['loc']; cam.keyframe_insert('location', frame=f); tgt.location = d['tgt']; tgt.keyframe_insert('location', frame=f)
        if 'lens' in d: cam.data.lens = d['lens']; cam.data.keyframe_insert('lens', frame=f)
        if 'fstop' in d: cam.data.dof.aperture_fstop = d['fstop']; cam.data.dof.keyframe_insert('aperture_fstop', frame=f)
        if 'clip' in d:
            cam.data.clip_start, cam.data.clip_end = d['clip']; cam.data.keyframe_insert('clip_start', frame=f); cam.data.keyframe_insert('clip_end', frame=f)
    for idb in (cam, tgt, cam.data): set_interp(idb, 'LINEAR')

# ---------- 灯光和环境 ----------
def world(color=(0.02, 0.025, 0.035), strength=1.0, hdri=None, hdri_strength=1.0, hdri_rot=0.0, bg_visible_hdri=False):
    """背景色给相机看；HDRI（如果文件在）只用来打光和反射，除非 bg_visible_hdri。"""
    w = bpy.data.worlds.new('world'); w.use_nodes = True; bpy.context.scene.world = w; N = w.node_tree.nodes; L = w.node_tree.links
    for n in list(N): N.remove(n)
    out = N.new('ShaderNodeOutputWorld'); bg = N.new('ShaderNodeBackground'); bg.inputs['Color'].default_value = (*color, 1); bg.inputs['Strength'].default_value = strength
    path = os.path.join(ASSETS_DL, hdri) if hdri else None
    if path and os.path.exists(path):
        tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (0, 0, hdri_rot)
        env = N.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(path, check_existing=True)
        L.new(tc.outputs['Generated'], mp.inputs['Vector']); L.new(mp.outputs[0], env.inputs['Vector'])
        bg2 = N.new('ShaderNodeBackground'); bg2.inputs['Strength'].default_value = hdri_strength; L.new(env.outputs[0], bg2.inputs['Color'])
        if bg_visible_hdri: L.new(bg2.outputs[0], out.inputs[0])
        else:
            lp = N.new('ShaderNodeLightPath'); mx = N.new('ShaderNodeMixShader'); L.new(lp.outputs['Is Camera Ray'], mx.inputs['Fac'])
            L.new(bg2.outputs[0], mx.inputs[1]); L.new(bg.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs[0])
    else:
        if hdri: print('提示：没找到 HDRI', path, '，用纯色环境。跑 blender/fetch_assets.sh 下载。')
        L.new(bg.outputs[0], out.inputs[0])
    return w

def area_light(name, loc, target, size, power, color=(1, 1, 1), size_y=None, col=None):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = power; ld.color = color; ld.size = size
    if size_y: ld.shape = 'RECTANGLE'; ld.size_y = size_y
    o = link(bpy.data.objects.new(name, ld), col); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); return o

# ---------- 标注锚点 ----------
def export_anchors(path, shot, cam, anchors, step=1, res=(1080, 1920)):
    """anchors：{名字: 物体 或 Vector}。逐帧把它们投影到屏幕（1080×1920，左上角为原点），给 Remotion 贴标签用。
    名字直接用 timeline.json 里那条标注的 anchor 字符串（例如「大芯片」「串化电路旁」），Remotion 按它匹配。"""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    sc = bpy.context.scene; out = {'shot': shot.id, 'fps': FPS, 'width': res[0], 'height': res[1], 'step': step, 'frames': {}}
    for f in range(shot.f0, shot.f1 + 1, step):
        sc.frame_set(f); row = {}
        for k, a in anchors.items():
            p = a.matrix_world.translation if hasattr(a, 'matrix_world') else Vector(a)
            v = world_to_camera_view(sc, cam, p)
            row[k] = [round(v.x * res[0], 1), round((1 - v.y) * res[1], 1), round(v.z, 4), int(v.z > 0 and 0 <= v.x <= 1 and 0 <= v.y <= 1)]
        out['frames'][str(f)] = row
    json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':')); print('ANCHORS', path)

# ---------- 渲染 ----------
def setup_render(args, exposure=0.0, look=None, film_transparent=False, volume=False):
    sc = bpy.context.scene; w, h = (int(x) for x in args.res.lower().split('x'))
    sc.render.engine = 'CYCLES'; sc.render.resolution_x = w; sc.render.resolution_y = h; sc.render.resolution_percentage = 100
    cy = sc.cycles; cy.samples = args.samples; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.02
    cy.use_denoising = True; cy.max_bounces = 6; cy.transparent_max_bounces = 16; cy.glossy_bounces = 4; cy.diffuse_bounces = 3
    cy.sample_clamp_indirect = 8.0; cy.caustics_reflective = False; cy.caustics_refractive = False
    if not volume: cy.volume_bounces = 0
    dev = 'CPU'
    if args.gpu:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for kind in ('OPTIX', 'CUDA'):
            try:
                prefs.compute_device_type = kind; prefs.get_devices()
                got = [d for d in prefs.devices if d.type == kind]
                if got:
                    for d in prefs.devices: d.use = d.type == kind
                    cy.device = 'GPU'; dev = kind + ':' + ','.join(d.name for d in got); break
            except Exception as e: print('GPU', kind, '不可用：', e)
    sc.render.film_transparent = film_transparent
    sc.view_settings.view_transform = 'AgX'; sc.view_settings.exposure = exposure
    if look:
        try: sc.view_settings.look = look
        except Exception: print('提示：没有这个 look：', look)
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'; sc.render.image_settings.compression = 30
    try: bpy.context.view_layer.aovs.add().name = 'lightmask'
    except Exception: pass
    print('RENDER_DEVICE', dev, '| RES', w, h, '| SAMPLES', args.samples); return dev

def frames_from_args(args, shot):
    if args.times: return [F(float(t)) for t in args.times.split(',')]
    if args.frames: return [int(f) for f in args.frames.split(',')]
    if args.range: return list(range(args.range[0], args.range[1] + 1, args.step))
    return [F(lerp(shot.t0, shot.t1, u)) for u in (0.02, 0.35, 0.65, 0.98)]

def render(args, shot, dev='CPU'):
    """渲染指定帧到 <out>/<镜头号>_<全片帧号>.png；已存在的帧跳过（可续渲）；写渲染日志。"""
    sc = bpy.context.scene; os.makedirs(args.out, exist_ok=True); log = []
    if args.save_blend: bpy.ops.wm.save_as_mainfile(filepath=os.path.join(args.out, shot.id + '.blend'))
    if args.no_render: return
    for f in frames_from_args(args, shot):
        path = os.path.join(args.out, f'{shot.id}_{f:06d}.png')
        if os.path.exists(path): print('SKIP', path); continue
        sc.frame_set(f); sc.render.filepath = path; t = time.time(); bpy.ops.render.render(write_still=True)
        dt = round(time.time() - t, 2); log.append({'frame': f, 'sec': dt}); print('RENDERED', path, dt, 's', flush=True)
    meta = {'shot': shot.id, 'blender': bpy.app.version_string, 'device': dev, 'res': args.res, 'samples': args.samples, 'frames': log,
            'timeline_version': TL['meta']['version']}
    lp = os.path.join(args.out, f'render_log_{shot.id}.json'); old = json.load(open(lp)) if os.path.exists(lp) else []
    json.dump(old + [meta], open(lp, 'w'), ensure_ascii=False, indent=1)
