# Animation Design Sprint 01 公用库（Blender）。
# 和运动草稿的根本区别：每段只搭一次场景，所有物体在整段里持续存在；每一帧只改它们的位置、朝向、材质状态。
# 材质、灯光、字块造型复用 style3d/film_desk.py（桌面精密模型摄影的美术规范），不另起画风。
#
# 每段样片写一个 shot_X.py：
#   build()      搭场景（只调用一次），返回要记录轨迹的物体 {名字: 物体}
#   pose(t)      把 t 秒时所有物体摆好（纯函数：同一个 t 永远摆出同一个画面）
#   DUR          时长（秒）
#   labels(t)    这一帧 2D 层要挂的提示 [(锚点名, 文字, 样式)]，锚点在 ANCH 里
# 渲染：blender -b -P shot_X.py -- --outdir DIR --scale 0.333 --samples 16 --font F.otf [--f0 0 --f1 -1]
import os, sys, math, json
_here = os.path.dirname(os.path.abspath(__file__))
_style = os.path.abspath(os.path.join(_here, '..', 'style3d'))
os.environ['FILM3D_LIB'] = '1'
_g = globals()
_src = open(os.path.join(_style, 'film_desk.py'), encoding='utf-8').read()
_src = _src[:_src.rindex('run_jobs(post=add_desk)')]          # 只要材质和工具，不跑运动草稿的逐拍渲染
_g['__file__'] = os.path.join(_style, 'film_desk.py')
exec(compile(_src, os.path.join(_style, 'film_desk.py'), 'exec'), _g)
_g['__file__'] = os.path.abspath(__file__)

import bpy
from mathutils import Vector, Euler, Matrix
from bpy_extras.object_utils import world_to_camera_view

def m_metal(col=SILVER, rough=0.36):
    # GPU 上带各向异性的金属在部分视角渲成全黑（整合片第 13、15、19、28 秒），这里关掉各向异性
    m, p = _bsdf('fmetal', **{'Base Color': hexc(col), 'Metallic': 1.0, 'Roughness': max(rough, 0.3)})
    return m

ap2 = __import__('argparse').ArgumentParser()
ap2.add_argument('--outdir', default='/tmp/anim'); ap2.add_argument('--f0', type=int, default=0); ap2.add_argument('--f1', type=int, default=-1)
ap2.add_argument('--fps', type=float, default=30); ap2.add_argument('--only', default='')   # --only 1.5,4.0：只渲这几个时刻（关键帧 / 调构图）
AA = ap2.parse_known_args(argv)[0]
FPS = AA.fps

# ---------------- 小工具 ----------------
def sstep(a, b, t):
    """t 在 [a,b] 里从 0 平滑到 1（ease in-out）"""
    return ease(clamp((t - a) / (b - a))) if b > a else float(t >= b)
def lin(a, b, t): return clamp((t - a) / (b - a)) if b > a else float(t >= b)
def mix3(p, q, u): return tuple(p[i] + (q[i] - p[i]) * u for i in range(3))
def back_out(u, k=1.4):
    """回弹：落位时略冲过头再回来"""
    u = clamp(u); u1 = u - 1; return 1 + (k + 1) * u1 ** 3 + k * u1 ** 2
def hex3(h): return hexc(h)[:3]

# ---------------- 路径（字块沿着走的轨道） ----------------
class Path:
    """过控制点的平滑曲线（Catmull-Rom），按弧长取点：at(s) / tan(s)，s ∈ [0, L]"""
    def __init__(self, pts, n=400):
        P = [Vector(p) for p in pts]
        P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
        out = []
        for i in range(1, len(P) - 2):
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            m = max(2, n // (len(P) - 3))
            for k in range(m):
                u = k / m
                out.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
        out.append(P[-2])
        self.pts = out; self.cum = [0.0]
        for a, b in zip(out, out[1:]): self.cum.append(self.cum[-1] + (b - a).length)
        self.L = self.cum[-1]
    def _i(self, s):
        s = max(0.0, min(self.L, s)); lo, hi = 0, len(self.cum) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.cum[mid] <= s: lo = mid
            else: hi = mid
        seg_ = self.cum[hi] - self.cum[lo]; u = (s - self.cum[lo]) / seg_ if seg_ > 0 else 0
        return lo, hi, u
    def at(self, s):
        lo, hi, u = self._i(s); return tuple(self.pts[lo].lerp(self.pts[hi], u))
    def tan(self, s):
        lo, hi, u = self._i(s); d = self.pts[hi] - self.pts[lo]
        return tuple(d.normalized()) if d.length > 1e-9 else (1, 0, 0)
    def upto(self, s):
        """从起点到 s 的点（画正在长出来的轨道用）"""
        lo, hi, u = self._i(s); return [tuple(p) for p in self.pts[:lo + 1]] + [tuple(self.pts[lo].lerp(self.pts[hi], u))]

def yaw_of(tan): return math.atan2(tan[1], tan[0])

# ---------------- 材质：一个字块一份，状态可逐帧改 ----------------
def state_mat(name, col='#EFE5D5', glass_col='#ECEAE4'):
    """陶瓷（正式）↔ 磨砂玻璃（草稿 / 假设）可以连续过渡；外加自发光（强调）和透明度（退场）"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    cer = nt.nodes.new('ShaderNodeBsdfPrincipled')
    cer.inputs['Base Color'].default_value = hexc(col); cer.inputs['Roughness'].default_value = 0.42
    cer.inputs['Coat Weight'].default_value = 0.35; cer.inputs['Coat Roughness'].default_value = 0.12
    cer.inputs['Subsurface Weight'].default_value = 0.06; cer.inputs['Subsurface Scale'].default_value = 0.02
    gl = nt.nodes.new('ShaderNodeBsdfPrincipled')
    gl.inputs['Base Color'].default_value = hexc(glass_col); gl.inputs['Roughness'].default_value = 0.28
    gl.inputs['Transmission Weight'].default_value = 1.0; gl.inputs['IOR'].default_value = 1.45
    gl.inputs['Coat Weight'].default_value = 0.4; gl.inputs['Coat Roughness'].default_value = 0.05
    mx = nt.nodes.new('ShaderNodeMixShader'); mx.inputs['Fac'].default_value = 0.0
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 0.0; em.inputs['Color'].default_value = hexc(AMBER)
    add = nt.nodes.new('ShaderNodeAddShader')
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mx2 = nt.nodes.new('ShaderNodeMixShader'); mx2.inputs['Fac'].default_value = 1.0
    L = nt.links.new
    L(cer.outputs[0], mx.inputs[1]); L(gl.outputs[0], mx.inputs[2])
    L(mx.outputs[0], add.inputs[0]); L(em.outputs[0], add.inputs[1])
    L(tr.outputs[0], mx2.inputs[1]); L(add.outputs[0], mx2.inputs[2]); L(mx2.outputs[0], out.inputs['Surface'])
    m['_n'] = 1
    m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
    return m

def set_state(m, draft=None, col=None, glow=None, glow_col=None, alpha=None):
    nt = m.node_tree.nodes
    mx = [n for n in nt if n.bl_idname == 'ShaderNodeMixShader']
    cer = [n for n in nt if n.bl_idname == 'ShaderNodeBsdfPrincipled'][0]
    em = [n for n in nt if n.bl_idname == 'ShaderNodeEmission'][0]
    if draft is not None: mx[0].inputs['Fac'].default_value = clamp(draft)
    if col is not None: cer.inputs['Base Color'].default_value = hexc(col) if isinstance(col, str) else (*col, 1)
    if glow is not None: em.inputs['Strength'].default_value = max(0.0, glow)
    if glow_col is not None: em.inputs['Color'].default_value = hexc(glow_col)
    if alpha is not None: mx[1].inputs['Fac'].default_value = clamp(alpha)

def ink_mat(name, col=GRAPH):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); p = nt.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value = hexc(col); p.inputs['Roughness'].default_value = 0.32
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader'); mx.inputs['Fac'].default_value = 1.0
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(p.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs['Surface'])
    return m
DRAFT_COL = '#DCE2E6'
def set_ink(m, col=None, alpha=None):
    nt = m.node_tree.nodes
    if col is not None: [n for n in nt if n.bl_idname == 'ShaderNodeBsdfPrincipled'][0].inputs['Base Color'].default_value = hexc(col) if isinstance(col, str) else (*col, 1)
    if alpha is not None: [n for n in nt if n.bl_idname == 'ShaderNodeMixShader'][0].inputs['Fac'].default_value = clamp(alpha)

# ---------------- 字块：一个根节点 + 方块 + 凸字，整体移动 ----------------
class Tok:
    def __init__(self, ch, s=0.6, name=None, col=WARM):
        self.ch, self.s = ch, s
        self.root = bpy.data.objects.new(name or f'tok_{ch}', None); bpy.context.collection.objects.link(self.root)
        self.mat = state_mat(f'm_{ch}', col)
        self.box = rbox((s, s * 0.62, s), (0, 0, 0), bevel=s * 0.16, mat=self.mat); self.box.parent = self.root
        self.ink = ink_mat(f'ink_{ch}')
        self.txt = text3d(ch, (0, 0, 0), s * 1.75, self.ink, extrude=0.012)
        self.txt.parent = self.root; self.txt.location = (0, -s * 0.31 - 0.004, -s * 0.03); self.txt.rotation_euler = (math.pi / 2, 0, 0)
        self.col = col
    def put(self, loc, yaw=0.0, pitch=0.0, roll=0.0, scale=1.0):
        self.root.location = loc; self.root.rotation_euler = (pitch, roll, yaw); self.root.scale = (scale, scale, scale)
    def look(self, draft=0.0, glow=0.0, glow_col=AMBER, alpha=1.0, col=None, ink=None):
        """draft：0 = 正式（陶瓷），1 = 草稿 / 假设（冷白磨砂、半透，字仍然读得清）"""
        c0 = hex3(col or self.col); c1 = hex3(DRAFT_COL)
        c = tuple(c0[i] + (c1[i] - c0[i]) * draft for i in range(3))
        set_state(self.mat, draft=0.42 * draft, glow=glow, glow_col=glow_col, alpha=alpha, col=c)
        i0, i1 = hex3(GRAPH), hex3('#6F757C'); ic = tuple(i0[i] + (i1[i] - i0[i]) * draft for i in range(3))
        set_ink(self.ink, alpha=alpha, col=ink if ink else ic)
        hide = alpha < 0.02 or self.root.scale[0] < 0.02
        self.box.hide_render = hide; self.txt.hide_render = hide

# ---------------- 场景 ----------------
def new_scene():
    reset('peach')                          # film_desk 把 world 换成暖灰无缝背景
    sc_ = bpy.context.scene
    sc_.render.use_persistent_data = True
    sc_.cycles.use_denoising = True
    try: sc_.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    sc_.cycles.max_bounces = 12; sc_.cycles.transmission_bounces = 12; sc_.cycles.glossy_bounces = 4; sc_.cycles.transparent_max_bounces = 16
    return sc_

def desk(z=0.0, size=200):
    """暖白桌面（带很细的纹理），和运动草稿同一张桌子；不带运动草稿的自动推镜"""
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 30, z))
    d = bpy.context.active_object
    m = bpy.data.materials.new('desk'); m.use_nodes = True; nt = m.node_tree; p = nt.nodes['Principled BSDF']
    p.inputs['Roughness'].default_value = 0.95; p.inputs['Coat Weight'].default_value = 0.0; p.inputs['Specular IOR Level'].default_value = 0.04
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 40; noise.inputs['Detail'].default_value = 4
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = hexc('#E9DDCB'); ramp.color_ramp.elements[1].color = hexc('#DCCCB5')
    ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[1].position = 0.75
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    d.data.materials.append(m); return d

def studio_lights(target=(0, 0, 0), key=700, fill=260, rim=320):
    """同一套三点布光，轮廓光压低（不把远处桌面打成一片白）"""
    tx, ty, tz = target
    area((tx - 7, ty - 7, tz + 7), target, key, 10, '#FFF1E0')
    area((tx + 8, ty - 5, tz + 3), target, fill, 8, '#E6EEF2')
    area((tx + 1, ty + 5, tz + 6), target, rim, 4, '#FFFFFF')

class Rig:
    """相机：每帧给位置、注视点、焦距；对焦在注视点上（浅景深，前后虚）"""
    def __init__(self, fstop=4.0):
        self.cam = camera((0, -10, 3), (0, 0, 0), lens=50, fstop=fstop)
    def set(self, loc, target, lens=50, focus=None):
        c = self.cam; c.location = loc
        d = Vector(target) - Vector(loc); c.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        c.data.lens = lens; c.data.dof.focus_distance = focus if focus else d.length

class Grow:
    """会长出来的玻璃轨道：每帧按长度重建（同一条轨道，只是长度在变）"""
    def __init__(self, path, width, mat, thick=0.05, name='rib', z=None, s0=0.0):
        self.path, self.width, self.mat, self.thick, self.name, self.z, self.s0 = path, width, mat, thick, name, z, s0; self.ob = None; self._s = None
    def show(self, s):
        s = round(max(0.0, min(self.path.L, s)), 3)
        if s == self._s: return
        if self.ob is not None:
            me = self.ob.data; bpy.data.objects.remove(self.ob, do_unlink=True); bpy.data.meshes.remove(me); self.ob = None
        self._s = s
        if s < 0.05: return
        pts = [tuple(p) for p, c in zip(self.path.pts, self.path.cum) if self.s0 <= c < s] + [self.path.at(s)]
        if s - self.s0 < 0.05: return
        step = max(1, len(pts) // 60); pts = pts[::step] + ([pts[-1]] if (len(pts) - 1) % step else [])
        if len(pts) < 2: return
        if self.z is not None: pts = [(p[0], p[1], self.z) for p in pts]
        self.ob = flat_strip(pts, self.width, self.mat, thick=self.thick); self.ob.name = self.name

def flat_strip(pts, width, mat, thick=0.05):
    """平铺在桌面上的玻璃轨道：沿路径，宽度方向水平"""
    import bmesh
    me = bpy.data.meshes.new('strip'); bm = bmesh.new(); V = [Vector(p) for p in pts]; rows = []
    for i, p in enumerate(V):
        a = V[max(0, i - 1)]; b = V[min(len(V) - 1, i + 1)]; d = (b - a); d.z = 0
        d = d.normalized() if d.length > 1e-9 else Vector((1, 0, 0)); n = Vector((-d.y, d.x, 0)) * (width / 2)
        rows.append((bm.verts.new(p + n), bm.verts.new(p - n)))
    for (a1, b1), (a2, b2) in zip(rows, rows[1:]): bm.faces.new((a1, b1, b2, a2))
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('strip', me); bpy.context.collection.objects.link(ob)
    md = ob.modifiers.new('sol', 'SOLIDIFY'); md.thickness = thick; md.offset = -1
    md2 = ob.modifiers.new('bev', 'BEVEL'); md2.width = thick * 0.4; md2.segments = 2
    smooth(ob); assign(ob, mat); return ob

# ---------------- 渲染循环 + 轨迹记录 ----------------
def run(shot):
    sc_ = bpy.context.scene
    tracked = shot['tracked']()            # {名字: 物体}：要记录轨迹的主角
    nf = int(round(shot.get('FILM_DUR', shot['DUR']) * FPS))
    tmap = shot.get('tmap')                # 成片时间 → 场景时间（V03 起）；没有就是同一个时间
    if AA.only:                            # --only 写场景时间
        frames = [('s', float(x)) for x in AA.only.split(',')] if tmap else [int(round(float(x) * FPS)) for x in AA.only.split(',')]
    else:
        frames = list(range(AA.f0, nf if AA.f1 < 0 else min(AA.f1, nf)))
    os.makedirs(AA.outdir, exist_ok=True)
    for fi in frames:
        if isinstance(fi, tuple): t = fi[1]; fi = int(round(t * 100))
        else: t = tmap(fi / FPS) if tmap else fi / FPS
        if os.environ.get('KEPU_SKIP_DONE') and os.path.exists(os.path.join(AA.outdir, f'f{fi:05d}.json')): continue   # 断点续渲
        ANCH.clear(); shot['pose'](t)
        bpy.context.view_layer.update()
        sc_.render.filepath = os.path.join(AA.outdir, f'f{fi:05d}.png')
        bpy.ops.render.render(write_still=True)
        def scr(v):
            p = world_to_camera_view(sc_, sc_.camera, Vector(v)); return [round(p.x, 4), round(1 - p.y, 4), round(p.z, 3)]
        meta = {'t': round(t, 4), 'f': fi, 'ft': round(fi / FPS, 4),
                'objs': {k: {'world': [round(c, 4) for c in o.matrix_world.translation], 'screen': scr(o.matrix_world.translation),
                             'visible': not getattr(o, '_hidden', False)} for k, o in tracked.items()},
                'anch': {k: scr(v) for k, v in ANCH.items()},
                'cam': {'loc': [round(c, 3) for c in sc_.camera.location], 'lens': sc_.camera.data.lens}}
        json.dump(meta, open(os.path.join(AA.outdir, f'f{fi:05d}.json'), 'w'), ensure_ascii=False)
