# 3 秒运动测试：镜头 ②（模型一层层）→ 镜头 ③（分叉），一个连续镜头。
# 用法：blender -b -P motion.py -- --outdir DIR --scale 0.5 --samples 32 --font F.otf [--frames 0,45,89]
# 每帧按时间 t 直接摆好所有物体（时间的纯函数），渲一张 png，并把标签锚点投影存成 json。
import sys, math, json, argparse, os
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'scene.py'), encoding='utf-8').read()
exec(src[:src.index('ANCH = {}')])          # 复用 scene.py 的材质、几何、灯光工具（不执行镜头段）

mp = argparse.ArgumentParser()
mp.add_argument('--outdir', default='/tmp/motion'); mp.add_argument('--frames', default='')
mp.add_argument('--fps', type=int, default=30); mp.add_argument('--dur', type=float, default=3.0)
M = mp.parse_known_args(argv)[0]
os.makedirs(M.outdir, exist_ok=True)
from bpy_extras.object_utils import world_to_camera_view

# ---------------- 时间工具 ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, t0, t1): return clamp((t - t0) / (t1 - t0))
def ease(u): return u * u * u * (u * (6 * u - 15) + 10)            # smootherstep：缓入缓出
def ease_out(u): return 1 - (1 - u) ** 3
def back_out(u, k=1.7):                                              # 落位轻微回弹
    u = clamp(u); return 1 + (k + 1) * (u - 1) ** 3 + k * (u - 1) ** 2
def lerp(a, b, u): return a + (b - a) * u
def lerpv(a, b, u): return Vector(a).lerp(Vector(b), u)
def mixc(h1, h2, u):
    c1, c2 = hexc(h1), hexc(h2); return tuple(lerp(c1[i], c2[i], u) for i in range(4))

# ---------------- 世界：两套底色之间渐变（章节 = 底色） ----------------
LIL_T, LIL_B, PEA_T, PEA_B = '#DCD5F8', '#C2B7F0', '#FFCFB8', '#FFB394'
world(LIL_T, LIL_B, light_strength=0.55)
wnt = sc.world.node_tree
RAMP = [n for n in wnt.nodes if n.type == 'VALTORGB'][0]
area((-5, -8, 9), (0, 0, 1), 900, 7)
area((6, -6, 2), (0, 0, 1), 350, 6)
area((0, 6, 6), (0, 0, 1), 900, 5, '#FFF1DE')
area((-8, -6, 3), (2, 0, -1), 500, 6)                               # 补到镜头 ③ 的方向

# ---------------- 镜头 ② 的模型（之后整体升走） ----------------
import random; random.seed(7)
STACK = []                                                          # (物体, 初始位置)
LAYER_MATS = []
zs = [0.45 + k * 0.92 for k in range(5)]
zball0 = (zs[2] + zs[3]) / 2
def keep(o): STACK.append((o, Vector(o.location))); return o
for k, z in enumerate(zs):
    m = candy('#FAF8FF', rough=0.35, coat=0.6, sss=0.35); LAYER_MATS.append((m, z))
    keep(rbox((4.7, 0.34, 0.62), (0, 0, z), bevel=0.14, seg=6, mat=m))
    for r in range(2):
        for c in range(10):
            if c in (4, 5): continue
            v = random.uniform(-1, 1); col = PINK if v > 0 else BLUE
            x = -2.05 + c * 0.455 + (0.08 if c > 5 else 0) - (0.08 if c < 4 else 0)
            keep(rbox((0.34, 0.1, 0.2), (x, -0.2, z + 0.13 - r * 0.26), bevel=0.05, seg=3,
                      mat=candy(col, rough=0.22 + 0.35 * (1 - abs(v)), sss=0.1)))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.2, minor_radius=0.03, location=(0, -0.2, z), rotation=(math.pi / 2, 0, 0))
    t_ = bpy.context.active_object; smooth(t_); assign(t_, satin_metal('#BFB6E6', 0.3)); keep(t_)
def rod(z0, z1, r, mat):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=1.0, location=(0, -0.2, 0), vertices=32)
    o = bpy.context.active_object; smooth(o); assign(o, mat)
    for v in o.data.vertices: v.co.z += 0.5                         # 原点放到底部，方便按高度缩放
    o.location.z = z0; o.scale.z = z1 - z0; return o
ZTOP = zs[-1] + 0.85
keep(rod(zs[0] - 0.8, zs[-1] + 0.6, 0.028, candy('#E9E5FA', 0.3)))
HOT = rod(zs[0] - 0.8, zball0, 0.032, emit(YEL, 2.2)); keep(HOT)
# 出口细管
ry = -0.55; step = 0.72; xs0 = -2.5 * step; qx = xs0 + 5 * step; TY = -0.6
PIPE = [(0, -0.2, zs[-1] + 0.6), (0, -0.2, ZTOP), (2.7, -0.2, ZTOP), (2.7, -0.2, ry + 0.7), (qx, TY, ry + 0.7), (qx, TY, ry)]
cu = bpy.data.curves.new('pipe', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.03; cu.bevel_resolution = 3
sp = cu.splines.new('POLY'); sp.points.add(len(PIPE[:-1]) - 1)
for i, p_ in enumerate(PIPE[:-1]): sp.points[i].co = (*p_, 1)
po = bpy.data.objects.new('pipe', cu); bpy.context.collection.objects.link(po); cu.materials.append(glass('#D9D2FF', 0.25)); keep(po)

# ---------------- 一排字块（贯穿两个镜头的那个东西）+「?」 ----------------
S_TOK = 0.6; YAW3 = -0.35
TOK = []
for k, ch in enumerate('周末我想去'):
    TOK.append(token(ch, (xs0 + k * step, TY, ry), s=S_TOK))
# token() 把字放成独立物体：把字挂到方块上，旋转时一起转
for ob in TOK:
    pass
QBOX = rbox((0.6, 0.37, 0.6), (qx, TY, ry), bevel=0.1, mat=glass('#FFE07A', 0.15))
QTXT = text3d('?', (qx, TY - 0.2, ry), 0.95, emit(YEL, 4.0), extrude=0.04, rot=(math.pi / 2, 0, 0))

# 黄球：新写出来的字
BALL = sphere(0.15, (0, -0.2, zball0), emit(YEL, 7.0))
SHELL = sphere(0.25, (0, -0.2, zball0), glass('#FFE58A', 0.2))

# ---------------- 镜头 ③ 的玻璃带（用曲线的 bevel_factor_end 让它「长出来」） ----------------
P = Vector((qx, TY + 0.05, ry - S_TOK / 2 - 0.08))                  # 分叉点：就在「?」的位置下面
def ribbon_curve(points, width, mat, thick=0.06):
    c = bpy.data.curves.new('rib', 'CURVE'); c.dimensions = '3D'
    s_ = c.splines.new('BEZIER'); s_.bezier_points.add(len(points) - 1)
    for i, p_ in enumerate(points):
        bp = s_.bezier_points[i]; bp.co = p_; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    c.extrude = width / 2; c.bevel_depth = thick / 2; c.bevel_resolution = 3
    c.resolution_u = 32; c.twist_mode = 'MINIMUM'; c.use_fill_caps = True
    c.bevel_factor_mapping_end = 'SPLINE'
    o = bpy.data.objects.new('rib', c); bpy.context.collection.objects.link(o); c.materials.append(mat)
    return o
RIBMAT = gradient_glass('#FFF4EC', '#FFE6D6', 'X', 0.12, -3, 7)
stem_pts = [P + Vector((-4.8, 0, 0)), P + Vector((-3.0, 0, 0)), P + Vector((-1.2, 0, 0)), P]
up_off = [(0, 0, 0), (0.9, 0, 0.7), (1.8, 0, 2.6), (3.0, 0, 3.12), (5.9, 0, 3.15)]
STEM = ribbon_curve(stem_pts, 0.9, RIBMAT)
UP = ribbon_curve([P + Vector(o) for o in up_off], 0.9, RIBMAT)
DN = ribbon_curve([P + Vector((o[0], o[1], -o[2])) for o in up_off], 0.9, RIBMAT)
def zpath(dx, z1):
    u = clamp((dx - 0.4) / 2.4); u = u * u * (3 - 2 * u); return z1 * u
BR = []                                                             # (方块, 出现时间, 目标位置)
for sgn, chars in ((1, '海边看日落'), (-1, '睡个懒觉')):
    for k, ch in enumerate(chars):
        dx = 2.75 + k * 0.66                                         # 放在分叉后的平直段上
        pos = P + Vector((dx, -0.05, 3.13 * sgn + S_TOK / 2 + 0.08))
        ob = token(ch, tuple(pos), s=S_TOK, body='#FFD45A' if k == 0 else '#FBF8F2', rot=(0, 0, YAW3))
        BR.append((ob, 2.05 + k * 0.09, pos))

# 字块上的字是独立物体（token() 用 matrix_world 摆好）：找出每个方块对应的字，之后跟着方块一起动
bpy.context.view_layer.update()
TXT_OF = {}
fonts = [o for o in bpy.data.objects if o.type == 'FONT' and o.data.body not in ('?',)]
cubes = TOK + [b[0] for b in BR]
for ob in cubes:
    best = min(fonts, key=lambda f: (f.matrix_world.translation - ob.location).length)
    TXT_OF[ob] = (best, ob.matrix_world.inverted() @ best.matrix_world)

# ---------------- 相机 ----------------
cd = bpy.data.cameras.new('cam'); cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36
CAM = bpy.data.objects.new('cam', cd); bpy.context.collection.objects.link(CAM); sc.camera = CAM
cd.dof.use_dof = True
C2 = (Vector((1.6, -32, 8.2)), Vector((0, 0, 0.9)), 100.0, 5.6)    # 镜头 ② 的机位
C3 = (Vector((-7.5, -10.9, 0.47)), Vector((2.3, -0.5, -1.28)), 28.0, 2.8)   # 镜头 ③ 的机位（整体平移到新坐标）

def place(ob, loc, rot=None, scale=None):
    ob.location = loc
    if rot is not None: ob.rotation_euler = rot
    if scale is not None: ob.scale = (scale, scale, scale)
    if ob in TXT_OF:
        bpy.context.view_layer.update()
        f, rel = TXT_OF[ob]; f.matrix_world = ob.matrix_world @ rel

def pipe_point(u):
    """沿出口细管走，u ∈ [0,1]"""
    L = [(Vector(PIPE[i + 1]) - Vector(PIPE[i])).length for i in range(len(PIPE) - 1)]
    d = u * sum(L)
    for i, l in enumerate(L):
        if d <= l or i == len(L) - 1:
            return Vector(PIPE[i]).lerp(Vector(PIPE[i + 1]), clamp(d / l))
        d -= l

def frame(t):
    # 1) 黄球：0–0.6 秒继续往上穿；0.6–1.4 秒沿细管跑到「?」
    if t < 0.6:
        bp = Vector((0, -0.2, lerp(zball0, ZTOP, ease(seg(t, 0, 0.6)))))
        if bp.z > zs[-1] + 0.6: bp = pipe_point(0)
    else:
        u = ease(seg(t, 0.6, 1.4)); bp = pipe_point(u)
    lift = Vector((0, 0, 12.0 * ease(seg(t, 1.35, 2.25))))            # 模型整体升走
    # 管子跟着模型升走，球在离开管子后就不跟了
    for o, p0 in STACK: o.location = p0 + lift
    if t < 1.4: bp = bp + (lift if t < 1.35 else Vector())
    # 落进「?」之后，球往下落到玻璃带的分叉点上，成为分叉的结
    SPLIT = P + Vector((0.3, -0.1, 0.45))
    if t >= 1.4: bp = Vector((qx, TY, ry)).lerp(SPLIT, ease(seg(t, 1.55, 1.95)))
    pop = back_out(seg(t, 1.38, 1.62))                                # 落进「?」时轻轻一弹
    sc_ball = 1 + 0.35 * math.sin(math.pi * seg(t, 1.38, 1.62))
    place(BALL, bp, scale=sc_ball); place(SHELL, bp, scale=sc_ball)
    # 2) 走过的层变暖、发光的管跟着球长
    for m, z in LAYER_MATS:
        w = clamp((min(bp.z, ZTOP) - z) / 0.3) if t < 0.6 else 1.0
        m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = mixc('#FAF8FF', '#FFEDB8', w)
    hz = min(bp.z, zs[-1] + 0.6) if t < 0.6 else zs[-1] + 0.6
    HOT.scale.z = max(0.01, hz - (zs[0] - 0.8))
    # 3)「?」被球顶替：缩没
    qs = 1 - ease(seg(t, 1.32, 1.5))
    place(QBOX, Vector((qx, TY, ry)), scale=max(qs, 0.001))
    QTXT.scale = (max(qs, 0.001),) * 3
    # 4) 字块慢慢转到镜头 ③ 的朝向
    yaw = YAW3 * ease(seg(t, 1.4, 2.4))
    for k, ob in enumerate(TOK): place(ob, Vector((xs0 + k * step, TY, ry)), rot=(0, 0, yaw))
    # 5) 玻璃带：主干从左往右长到分叉点，两条分叉再长出去；分叉上的字块跟着生长的前沿弹出来
    STEM.data.bevel_factor_end = ease(seg(t, 1.45, 1.95))
    g = ease_out(seg(t, 1.85, 2.65))
    UP.data.bevel_factor_end = g; DN.data.bevel_factor_end = g
    for ob, t0, pos in BR:
        s_ = back_out(seg(t, t0, t0 + 0.3))
        place(ob, pos, scale=max(s_, 0.001))
    # 6) 底色：淡紫 → 桃色（换章节）
    u = ease(seg(t, 1.4, 2.3))
    RAMP.color_ramp.elements[0].color = mixc(LIL_B, PEA_B, u)
    RAMP.color_ramp.elements[1].color = mixc(LIL_T, PEA_T, u)
    # 7) 相机：从正面长焦摆到左前方广角；焦点一直跟着黄球。结尾继续极慢地漂（不完全静止）
    u = ease(seg(t, 1.25, 2.55))
    pos = C2[0].lerp(C3[0], u); tgt = C2[1].lerp(C3[1], u)
    pos.z += 1.2 * math.sin(math.pi * u)                              # 摆的路线略微抬高，弧线更顺
    drift = 0.25 * seg(t, 2.55, 3.0); pos += Vector((drift, -drift * 0.6, 0.05 * drift))
    lens = math.exp(lerp(math.log(C2[2]), math.log(C3[2]), u))
    if t < 1.25: pos += Vector((0, 0, 0.4 * ease(seg(t, 0, 1.25))))  # 前段跟着球轻轻上摇
    CAM.location = pos
    CAM.rotation_euler = (tgt - pos).to_track_quat('-Z', 'Y').to_euler()
    cd.lens = lens
    cd.dof.focus_distance = (bp - pos).length
    cd.dof.aperture_fstop = lerp(C2[3], C3[3], u)
    return bp

nf = int(round(M.dur * M.fps))
frames = [int(x) for x in M.frames.split(',')] if M.frames else list(range(nf))
for fi in frames:
    t = fi / M.fps
    bp = frame(t)
    bpy.context.view_layer.update()
    sc.render.filepath = os.path.join(M.outdir, f'f{fi:04d}.png')
    bpy.ops.render.render(write_still=True)
    anch = {'ball': bp, 'model': Vector((0, 0, zs[-1] + 1.3)) + Vector((0, 0, 12.0 * ease(seg(t, 1.35, 2.25)))),
            'q': Vector((qx - 0.75, TY, ry + 0.7)), 'hai': BR[0][2] + Vector((0, 0, S_TOK * 0.9)),
            'zhou': Vector((xs0 - S_TOK / 2, TY, ry)), 'luo': BR[4][2] + Vector((S_TOK / 2, 0, S_TOK / 2)), 'jue': BR[8][2] + Vector((S_TOK / 2, 0, 0))}
    json.dump({k: [round(c, 4) for c in world_to_camera_view(sc, CAM, v)[:2]] for k, v in anch.items()},
              open(os.path.join(M.outdir, f'f{fi:04d}.json'), 'w'))
