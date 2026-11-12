# T5 第 1 拍 / 结尾「亮起」共用的机房场景。做法：读 blender/s01_datacenter.py 的源码，截到「路径线」之前执行（机柜、服务器、机房、线槽全复用，不改原文件），
# 再用文本补丁做 T5 需要的几处改动（只作用在内存里的源码）：
#   · 主机柜（A 排 i=4）：去掉顶板和后板，镜头才穿得出机箱、绕到机箱后面；
#   · 光口模块尾端加长到 40 mm（每台服务器都一样），GPU A 的第 1 个光口的尾端单独成一个物体，由本文件换成半透明光模块；
# 然后加：消息串的着色（全片统一画法）、沿路径的管（自带弧长 UV）、光模块、B 排的标记、远处渐隐、渲染设置。
import sys, os, math, time, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
BL = os.path.abspath(os.path.join(HERE, '..', '..', 'blender'))
sys.path.insert(0, BL)
import bpy, bmesh
from mathutils import Vector, Matrix
import common as C

V = Vector; PI = math.pi; rad = math.radians
FPS = C.FPS

# ---------- 命令行 ----------
def parse():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument('out'); p.add_argument('--res', default='270x480'); p.add_argument('--samples', type=int, default=24)
    p.add_argument('--times', default=''); p.add_argument('--frames', default='')
    p.add_argument('--range', nargs=2, type=int, default=None); p.add_argument('--step', type=int, default=1)
    p.add_argument('--gpu', action='store_true'); p.add_argument('--threads', type=int, default=2)
    p.add_argument('--save-blend', action='store_true'); p.add_argument('--no-render', action='store_true')
    a = p.parse_args(argv)
    if a.frames and '-' in a.frames and ',' not in a.frames:        # --frames a-b
        lo, hi = a.frames.split('-'); a.range = [int(lo), int(hi)]; a.frames = ''
    a.anchors = False
    return a

class T5Shot:
    """片内时间 0..dur，帧号 = round(t*fps)+1。"""
    def __init__(self, sid, dur):
        self.id = sid; self.t0 = 0.0; self.t1 = dur; self.f0 = 1; self.f1 = round(dur * FPS); self.data = {}
    def u(self, t): return (t - self.t0) / (self.t1 - self.t0)

def build_scene(sid, dur):
    """返回 dict：shot、args、ns（s01 截到路径线之前的全部变量）"""
    args = parse(); shot = T5Shot(sid, dur)
    C.parse_args = lambda: args; C.Shot = lambda _id: shot
    path = os.path.join(BL, 's01_datacenter.py'); src = open(path, encoding='utf-8').read()
    src = src[:src.index('# ---------- 路径线')]
    def patch(old, new):
        nonlocal src
        assert src.count(old) == 1, ('补丁没找到或次数不对', old, src.count(old)); src = src.replace(old, new)
    patch("g['rack'].box((RACK_W, 1.08, 0.02), (0, 0.54, RACK_H - 0.01));", "if not hero: g['rack'].box((RACK_W, 1.08, 0.02), (0, 0.54, RACK_H - 0.01));")
    patch("    g['rack'].box((RACK_W, 0.02, 0.04), (0, RACK_D - 0.01, RACK_H - 0.02))", "    if not hero: g['rack'].box((RACK_W, 0.02, 0.04), (0, RACK_D - 0.01, RACK_H - 0.02))")
    patch("    g['rack'].box((RACK_W - 0.01, 0.01, RACK_H - 0.1), (0, RACK_D - 0.005, RACK_H / 2 + 0.02))", "    if not hero: g['rack'].box((RACK_W - 0.01, 0.01, RACK_H - 0.1), (0, RACK_D - 0.005, RACK_H / 2 + 0.02))")
    patch("PORT_TIP = SD + 0.018", "PORT_TIP = SD + 0.042")
    patch("g['silver'].box((0.0183, 0.016, 0.0085), (px, SD + 0.009, PORT_Z))", "g['p0stub' if px == PORT_X[0] else 'silver'].box((0.0183, 0.040, 0.0085), (px, SD + 0.020, PORT_Z))")
    patch("'wire', 'silver', 'drive', 'label', 'led')}", "'wire', 'silver', 'p0stub', 'drive', 'label', 'led')}")
    patch("mk('wire',", "mk('p0stub', C.pbr, color=(0.70, 0.71, 0.73), metallic=1.0, rough=0.35)\nmk('wire',")
    ns = {'__file__': path, '__name__': 's01_t5'}
    t0 = time.time(); exec(compile(src, path, 'exec'), ns); print('S01_EXEC_SEC', round(time.time() - t0, 1), flush=True)
    return dict(shot=shot, args=args, ns=ns)

# ---------- 消息串：沿路径流动的亮暗段（全片统一画法） ----------
PATTERN = [1, 1, 0, 1, 0, 0, 1, 0]
GOLD_MSG = (0.949, 0.714, 0.251)        # #F2B640 电
CYAN_MSG = (0.247, 0.902, 0.941)        # #3FE6F0 光
DARK_LEVEL = 0.20                        # 暗位 = 亮位的 20%
GAP_LEVEL = 0.05                         # 段与段之间的短暗隙

def message_material(name, color, strength=4.0, cell=0.05, flip=False, head=False):
    """沿「弧长 UV」（米）流动的八位图样：亮位 1、暗位 0.2、段间隙 0.05。
    节点 'msg_offset'（Value，单位 = 位）：打关键帧，图样沿弧长增大的方向流动；'msg_strength'（Value）：整体强度。
    flip=True：图样沿弧长减小的方向流动。"""
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    for n in list(N): N.remove(n)
    def math_(op, a, b=None, c=None):
        n = N.new('ShaderNodeMath'); n.operation = op
        for i, v in enumerate((a, b, c)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: L.new(v, n.inputs[i])
        return n.outputs[0]
    uv = N.new('ShaderNodeUVMap'); uv.uv_map = 'UV'; sep = N.new('ShaderNodeSeparateXYZ'); L.new(uv.outputs['UV'], sep.inputs[0])
    off = N.new('ShaderNodeValue'); off.name = 'msg_offset'; off.outputs[0].default_value = 0.0
    stv = N.new('ShaderNodeValue'); stv.name = 'msg_strength'; stv.outputs[0].default_value = strength
    i_ = math_('SUBTRACT', math_('ADD', math_('DIVIDE', sep.outputs['X'], cell), 8000.0), off.outputs[0])
    cellid = math_('FLOOR', i_); frac = math_('SUBTRACT', i_, cellid); b = math_('MODULO', cellid, 8.0)
    lit = None
    for k, v in enumerate(PATTERN):
        if v:
            c = math_('COMPARE', b, float(k), 0.25); lit = c if lit is None else math_('ADD', lit, c)
    level = math_('ADD', DARK_LEVEL, math_('MULTIPLY', lit, 1.0 - DARK_LEVEL))
    edge = math_('MINIMUM', frac, math_('SUBTRACT', 1.0, frac))
    mr = N.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'; mr.inputs['From Min'].default_value = 0.04; mr.inputs['From Max'].default_value = 0.09
    L.new(edge, mr.inputs['Value'])
    val = math_('ADD', GAP_LEVEL, math_('MULTIPLY', math_('SUBTRACT', level, GAP_LEVEL), mr.outputs['Result']))
    if head:                                      # 'msg_head'（Value，米）：消息的前端走到哪；前端之后的路段不亮（到达动画用）
        hd = N.new('ShaderNodeValue'); hd.name = 'msg_head'; hd.outputs[0].default_value = 1e6
        hm = N.new('ShaderNodeMapRange'); hm.interpolation_type = 'SMOOTHSTEP'
        L.new(math_('SUBTRACT', hd.outputs[0], sep.outputs['X']), hm.inputs['Value']); hm.inputs['From Min'].default_value = 0.0; hm.inputs['From Max'].default_value = 0.06
        val = math_('MULTIPLY', val, hm.outputs['Result'])
    e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*color, 1)
    L.new(math_('MULTIPLY', val, stv.outputs[0]), e.inputs['Strength'])
    out = N.new('ShaderNodeOutputMaterial'); L.new(e.outputs[0], out.inputs[0])
    a = N.new('ShaderNodeOutputAOV'); a.aov_name = 'lightmask'; L.new(val, a.inputs['Value'])
    return m

def sweep_tube(name, pts, radius, mat, sides=8, col=None, radius_far=None):
    """沿折线的圆管（自己做的网格，UV 的 U = 沿线弧长（米），V = 绕一圈）。
    radius_far：再做一份更粗的形态存成形态键 'far'（形态键值 0→1 打关键帧：镜头拉远时管变粗）。radius 可以是数或逐点的列表。"""
    q = [V(pts[0])]
    for p in pts[1:]:
        if (V(p) - q[-1]).length > 1e-6: q.append(V(p))
    pts = q; n = len(pts)
    tang = [(pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized() for i in range(n)]
    up0 = V((0, 0, 1)) if abs(tang[0].z) < 0.9 else V((1, 0, 0)); nrm = tang[0].cross(up0).normalized(); frames = []
    for i in range(n):
        if i:
            axis = tang[i - 1].cross(tang[i])
            if axis.length > 1e-8: nrm = Matrix.Rotation(math.asin(min(1.0, axis.length)), 3, axis.normalized()) @ nrm
            nrm = (nrm - tang[i] * nrm.dot(tang[i])).normalized()
        frames.append((nrm, tang[i].cross(nrm).normalized()))
    arc = [0.0]
    for a, b in zip(pts, pts[1:]): arc.append(arc[-1] + (b - a).length)
    def build(r):
        rr = r if isinstance(r, list) else [r] * n
        return [[pts[i] + (frames[i][0] * math.cos(2 * PI * k / sides) + frames[i][1] * math.sin(2 * PI * k / sides)) * rr[i] for k in range(sides)] for i in range(n)]
    rings = build(radius); bm = bmesh.new(); uvl = bm.loops.layers.uv.new('UV'); vs = [[bm.verts.new(p) for p in rg] for rg in rings]
    for i in range(n - 1):
        for k in range(sides):
            k2 = (k + 1) % sides; f = bm.faces.new((vs[i][k], vs[i][k2], vs[i + 1][k2], vs[i + 1][k]))
            for lp, (u, v) in zip(f.loops, ((arc[i], k / sides), (arc[i], (k + 1) / sides), (arc[i + 1], (k + 1) / sides), (arc[i + 1], k / sides))): lp[uvl].uv = (u, v)
            f.smooth = True
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if mat: me.materials.append(mat)
    o = bpy.data.objects.new(name, me); C.link(o, col)
    if radius_far is not None:
        o.shape_key_add(name='basis'); sk = o.shape_key_add(name='far'); rf = build(radius_far)
        for i in range(n):
            for k in range(sides): sk.data[i * sides + k].co = rf[i][k]
    o['arc_len'] = arc[-1]
    return o

# ---------- 半透明光模块（装在服务器的第 1 个光口，尾端伸出后面板 40 mm） ----------
def optical_module(ns, row='A', idx=None):
    """露出部分半透明，看得到里面的小电路板、驱动芯片、激光器和透镜。返回 dict(objs, W, chip_local)。W：服务器坐标 → 世界。"""
    SD = ns['SD']; PORT_Z = ns['PORT_Z']; LANE_X = ns['LANE_X']; to_world = ns['to_world']; srv_to_rack = ns['srv_to_rack']
    idx = ns['I_A'] if idx is None else idx
    col = C.collection('光模块_' + row)
    def W(p): return to_world(row, idx, srv_to_rack(p))
    x, z = LANE_X, PORT_Z
    y0, y1 = SD + 0.0010, SD + 0.0400
    w, h = 0.0183, 0.0085
    mats = dict(
        shell=C.pbr('module_shell', (0.62, 0.78, 0.95), metallic=0.0, rough=0.08, alpha=0.16, coat=0.8),
        frame=C.pbr('module_frame', (0.55, 0.57, 0.60), metallic=1.0, rough=0.28),
        pcb=C.pbr('module_pcb', (0.010, 0.060, 0.045), rough=0.35, coat=0.5),
        chip=C.pbr('module_chip', (0.02, 0.02, 0.024), rough=0.35),
        si=C.pbr('module_si', (0.30, 0.32, 0.37), metallic=0.9, rough=0.15),
        gold=C.pbr('module_gold', (0.80, 0.62, 0.22), metallic=1.0, rough=0.3),
        lens=C.pbr('module_lens', (0.02, 0.02, 0.03), rough=0.05, coat=1.0))
    g = {k: C.Mesh() for k in mats}
    g['shell'].box((w, y1 - y0, h), (0, (y0 + y1) / 2, 0))
    t = 0.0007                                                   # 边框：四条长棱 + 前后两圈
    for sx in (-1, 1):
        for sz in (-1, 1): g['frame'].box((t, y1 - y0, t), (sx * (w / 2 - t / 2), (y0 + y1) / 2, sz * (h / 2 - t / 2)))
    for yy in (y0, y1 - 0.0015):
        for sz in (-1, 1): g['frame'].box((w, 0.0015, t), (0, yy + 0.00075, sz * (h / 2 - t / 2)))
        for sx in (-1, 1): g['frame'].box((t, 0.0015, h), (sx * (w / 2 - t / 2), yy + 0.00075, 0))
    g['pcb'].box((w - 0.0030, 0.030, 0.0007), (0, y0 + 0.0165, -0.0012))
    for k in range(5): g['gold'].box((0.0010, 0.0026, 0.0002), (-0.0050 + k * 0.0025, y0 + 0.0020, -0.00085))
    g['chip'].box((0.0065, 0.0065, 0.0016), (0, y0 + 0.0125, -0.0003)); g['chip'].box((0.0035, 0.0035, 0.0012), (0.0045, y0 + 0.0210, -0.0004))
    g['si'].box((0.0035, 0.0045, 0.0012), (-0.0030, y0 + 0.0290, -0.0004)); g['si'].box((0.0030, 0.0030, 0.0009), (0.0032, y0 + 0.0290, -0.0005))
    g['lens'].cyl(0.0014, 0.0030, (0, y0 + 0.0345, -0.0003), rot=(PI / 2, 0, 0), seg=16)
    objs = []
    for nm, m_ in g.items():
        o = m_.obj('模块_' + nm, mats[nm], col, bevel=0.0003 if nm in ('shell', 'chip') else 0.0); o.location = W((x, 0, z)); objs.append(o)
    return dict(objs=objs, W=W, chip_local=(x, y0 + 0.0290, z + 0.0004), y0=y0, y1=y1, x=x, z=z)

# ---------- B 排的标记 ----------
def b_marker(ns, strength=3.0):
    """B 排 GPU B 那台服务器的柔和标记：门前一圈青白色的细框 + 很淡的底光 + 一盏柔光。"""
    to_world = ns['to_world']; srv_to_rack = ns['srv_to_rack']; SH = ns['SH']; SW = ns['SW']; I_B = ns['I_B']
    c = to_world('B', I_B, srv_to_rack((0, 0, SH / 2)))
    y = -0.600 + 0.012
    w, h = SW + 0.040, SH + 0.040; t = 0.010
    col = C.collection('B标记')
    m = bpy.data.materials.new('b_marker'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    for n in list(N): N.remove(n)
    e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (0.72, 1.0, 1.0, 1); e.inputs['Strength'].default_value = strength
    out = N.new('ShaderNodeOutputMaterial'); L.new(e.outputs[0], out.inputs[0])
    fm = C.Mesh()
    for sx in (-1, 1): fm.box((t, 0.006, h), (sx * (w / 2 - t / 2), 0, 0))
    for sz in (-1, 1): fm.box((w, 0.006, t), (0, 0, sz * (h / 2 - t / 2)))
    o = fm.obj('B标记框', m, col); o.location = (c.x, y, c.z)
    m2 = bpy.data.materials.new('b_marker_fill'); m2.use_nodes = True; N2 = m2.node_tree.nodes; L2 = m2.node_tree.links
    for n in list(N2): N2.remove(n)
    e2 = N2.new('ShaderNodeEmission'); e2.inputs['Color'].default_value = (0.62, 0.95, 1.0, 1); e2.inputs['Strength'].default_value = strength * 0.18
    tr = N2.new('ShaderNodeBsdfTransparent'); mx = N2.new('ShaderNodeMixShader'); mx.inputs['Fac'].default_value = 0.35
    o2 = N2.new('ShaderNodeOutputMaterial'); L2.new(tr.outputs[0], mx.inputs[1]); L2.new(e2.outputs[0], mx.inputs[2]); L2.new(mx.outputs[0], o2.inputs[0])
    fl = C.Mesh(); fl.box((w - 0.02, 0.003, h - 0.02), (0, 0, 0)); of = fl.obj('B标记底光', m2, col); of.location = (c.x, y + 0.002, c.z)
    ld = bpy.data.lights.new('B标记柔光', 'AREA'); ld.energy = 0.0; ld.color = (0.60, 0.95, 1.0); ld.shape = 'RECTANGLE'; ld.size = w * 1.6; ld.size_y = h * 1.6
    lo = C.link(bpy.data.objects.new('B标记柔光', ld), col); lo.location = (c.x, y + 0.15, c.z)
    lo.rotation_euler = V((0, -1, 0)).to_track_quat('-Z', 'Y').to_euler(); lo.visible_camera = False
    return dict(light=ld, center=c, e1=e, e2=e2, mix=mx, frame_obj=o, fill_obj=of)

def key_sock(sock, keys):
    """keys = [(片内秒, 值)]，线性。sock 是节点输入 / 输出插口"""
    for t, v in keys: sock.default_value = v; sock.keyframe_insert('default_value', frame=C.F(t))
    C.set_interp(sock.id_data, 'LINEAR')

def key_energy(ld, keys):
    for t, e in keys: ld.energy = e; ld.keyframe_insert('energy', frame=C.F(t))
    C.set_interp(ld, 'LINEAR')

# ---------- 远处渐隐 ----------
def add_fog_all(ns, d0=3.5, scale=8.0):
    FOG = ns['FOG']; NT = ns['NT']; M = ns['M']
    def add_fog(m):
        nt = m.node_tree; N = nt.nodes; L = nt.links; out = next((n for n in N if n.type == 'OUTPUT_MATERIAL'), None)
        if not out or not out.inputs['Surface'].is_linked: return
        src = out.inputs['Surface'].links[0].from_socket; t = NT(m); cd = N.new('ShaderNodeCameraData')
        x = t.m('MAXIMUM', t.m('DIVIDE', t.m('SUBTRACT', cd.outputs['View Distance'], d0), scale), 0.0)
        fac = t.m('SUBTRACT', 1.0, t.m('POWER', 2.718281828, t.m('MULTIPLY', x, -1.0)))
        em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*FOG, 1); mx = N.new('ShaderNodeMixShader')
        L.new(fac, mx.inputs[0]); L.new(src, mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs['Surface'])
    for key, m in M.items():
        if not key.endswith('_fade') and not key.startswith('path_'): add_fog(m)

# ---------- 相机样条（速度连续） ----------
def hermite(keys, t):
    """keys = [(t, Vector)]；切线取相邻差分；端点用单边差分"""
    n = len(keys); t = max(keys[0][0], min(keys[-1][0], t))
    def tan(i):
        if i == 0: return (keys[1][1] - keys[0][1]) / (keys[1][0] - keys[0][0])
        if i == n - 1: return (keys[-1][1] - keys[-2][1]) / (keys[-1][0] - keys[-2][0])
        return (keys[i + 1][1] - keys[i - 1][1]) / (keys[i + 1][0] - keys[i - 1][0])
    i = max(k for k in range(n - 1) if keys[k][0] <= t); (t0, p0), (t1, p1) = keys[i], keys[i + 1]; h = t1 - t0; s = (t - t0) / h
    return (2 * s ** 3 - 3 * s ** 2 + 1) * p0 + (s ** 3 - 2 * s ** 2 + s) * h * tan(i) + (-2 * s ** 3 + 3 * s ** 2) * p1 + (s ** 3 - s ** 2) * h * tan(i + 1)

def hermite_s(keys, t):
    return hermite([(a, V((b, 0, 0))) for a, b in keys], t).x

def setup_render(args, exposure=0.0):
    dev = C.setup_render(args, exposure=exposure)
    sc = bpy.context.scene; sc.cycles.transparent_max_bounces = 48
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.4
    if args.threads and not args.gpu:
        sc.render.threads_mode = 'FIXED'; sc.render.threads = args.threads
    return dev
