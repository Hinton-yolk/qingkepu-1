# EP.01「AI 为什么一个字一个字往外蹦？」新画风（风格化 2.5D 科学动画）3D 层。
# 每一拍是一个函数 beat(u)，u ∈ [0,1] 是这一拍里的进度；整片时间 t → (拍, u)。
# 草稿：每拍出一帧接触表；终版：逐帧渲（RunPod）。
# 用法：blender -b -P film3d.py -- --outdir DIR --scale 0.35 --samples 24 --font F.otf [--beats 1,2,3] [--u 0.6] [--times 1.0,9.5]
import sys, math, json, argparse, os
here = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(here, 'scene.py'), encoding='utf-8').read()
exec(_src[:_src.index('ANCH = {}')])          # 复用 scene.py 的材质、几何、灯光工具

fp = argparse.ArgumentParser()
fp.add_argument('--outdir', default='/tmp/film3d'); fp.add_argument('--beats', default='')
fp.add_argument('--u', type=float, default=0.6); fp.add_argument('--times', default='')
fp.add_argument('--ui_dir', default='')
F = fp.parse_known_args(argv)[0]
os.makedirs(F.outdir, exist_ok=True)
from bpy_extras.object_utils import world_to_camera_view

# ---------------- 节拍表（时间照用户确认的脚本 v2.1） ----------------
BEATS = [  # 【已作废，仅供对照】v2.1 的 25 拍时间表；实际顺序和时间见文末 V3 和 script.md「逐句字幕 v3」
    (1, 0.0, 2.2, 'blue'), (2, 2.2, 5.4, 'blue'), (3, 5.4, 8.2, 'blue'),
    (4, 8.2, 11.2, 'lilac'), (5, 11.2, 14.0, 'lilac'), (6, 14.0, 17.0, 'lilac'), (7, 17.0, 19.8, 'lilac'),
    (8, 19.8, 22.6, 'peach'), (9, 22.6, 25.4, 'peach'), (10, 25.4, 28.2, 'peach'), (11, 28.2, 31.4, 'peach'),
    (12, 31.4, 34.8, 'mint'),
    (13, 34.8, 38.2, 'butter'), (14, 38.2, 41.6, 'butter'),
    (15, 41.6, 44.4, 'rose'), (16, 44.4, 47.4, 'rose'), (17, 47.4, 50.6, 'rose'), (18, 50.6, 54.0, 'rose'),
    (19, 54.0, 57.6, 'mint'), (20, 57.6, 60.8, 'mint'),
    (21, 60.8, 64.4, 'rose'), (22, 64.4, 67.8, 'lilac'),
    (23, 67.8, 71.0, 'blue'), (24, 71.0, 75.0, 'blue'), (25, 75.0, 78.0, 'blue'),
]
# 底色：11-19 用户要求「色度做适当的提升」，比样张 v3 更饱和
BG = {'blue': ('#A3C6FA', '#78A8F4'), 'lilac': ('#CBB9F8', '#AA93F1'), 'peach': ('#FFC2A2', '#FF9F75'),
      'mint': ('#AEE9CB', '#7DD6A9'), 'butter': ('#FFE59A', '#FFCB5C'), 'rose': ('#F3B2DA', '#E688C4')}
GREEN, GRAY, DRAFT = '#2FCF7E', '#A9A5BC', '#E5DBFF'

# ---------------- 小工具 ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(u, a, b): return clamp((u - a) / (b - a))
def ease(u): return u * u * u * (u * (6 * u - 15) + 10)
def back_out(u, k=1.7):
    u = clamp(u); return 1 + (k + 1) * (u - 1) ** 3 + k * (u - 1) ** 2
def lerp(a, b, u): return a + (b - a) * u
ANCH = {}

def reset(chapter, halo=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    global sc
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = A.samples
    sc.cycles.use_denoising = True; sc.cycles.max_bounces = 10; sc.cycles.transmission_bounces = 10
    sc.cycles.glossy_bounces = 6; sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 1.0
    sc.render.resolution_x = 1080; sc.render.resolution_y = 1920; sc.render.resolution_percentage = int(A.scale * 100)
    sc.render.image_settings.file_format = 'PNG'
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
    top, bot = BG[chapter]
    world(top, bot, light_strength=0.55, halo=('#D4E4FF', (-0.06, 1.0, -0.06), 0.30) if halo else None)   # 背光只给手机镜头（广角）
    ANCH.clear()

def lights(target=(0, 0, 0), key=900, fill=320, rim=900):
    area((-5, -8, 8), target, key, 7)
    area((7, -5, 2), target, fill, 6)
    area((1, 7, 5), target, rim, 5, '#FFF1DE')

def cam(loc, target, lens, fstop=4.0, focus=None):
    c = camera(loc, target, lens=lens, fstop=fstop, focus=focus); return c

def gray_q(loc, s=0.6, rot=(0, 0, 0)):
    """灰色「?」块：还没法写的位置"""
    ob = rbox((s, s * 0.62, s), loc, bevel=s * 0.16, mat=candy(GRAY, rough=0.45, sss=0.1), rot=rot)
    t = text3d('?', (0, 0, 0), s * 1.6, candy('#7D7990', 0.5), extrude=0.01)
    M = Matrix.LocRotScale(Vector(loc), Euler(rot).to_quaternion(), None)
    t.matrix_world = M @ Matrix.Translation((0, -s * 0.31 - 0.004, -s * 0.03)) @ Euler((math.pi / 2, 0, 0)).to_matrix().to_4x4()
    return ob

def yel_q(loc, s=0.6, rot=(0, 0, 0)):
    """黄色「?」玻璃块：下一个要写的位置"""
    ob = rbox((s, s * 0.62, s), loc, bevel=s * 0.17, mat=glass('#FFE07A', 0.15), rot=rot)
    M = Matrix.LocRotScale(Vector(loc), Euler(rot).to_quaternion(), None)
    t = text3d('?', (0, 0, 0), s * 1.6, emit(YEL, 4.0), extrude=0.04)
    t.matrix_world = M @ Matrix.Translation((0, -s * 0.33, -s * 0.03)) @ Euler((math.pi / 2, 0, 0)).to_matrix().to_4x4()
    return ob

def draft_tok(ch, loc, s=0.6, rot=(0, 0, 0), body=DRAFT):
    """小模型抢答的草稿字：淡紫，和正式的白字块区分开"""
    return token(ch, loc, s=s, body=body, rot=rot)

def bookmark(loc, s=0.6):
    """存档标记：字块右上角的一枚小书签（算过的结果存着，不重算）"""
    x, y, z = loc
    rbox((s * 0.16, 0.03, s * 0.34), (x + s * 0.3, y - s * 0.33, z + s * 0.36), bevel=0.02, mat=candy('#7F6BE0', 0.3))

def xmark(loc, size=1.0, rot_y=0.0, thick=0.12):
    """白色描边 ✕（错 / 作废）：两根交叉的白色圆角条"""
    for a in (math.pi / 4, -math.pi / 4):
        rbox((size, thick * 0.6, thick), loc, bevel=thick * 0.45, mat=candy('#FFFFFF', 0.25), rot=(0, a + rot_y, 0))

def check(loc, s=0.32):
    """绿勾：绿色圆片 + 白勾"""
    bpy.ops.mesh.primitive_cylinder_add(radius=s, depth=0.08, location=loc, rotation=(math.pi / 2, 0, 0), vertices=48)
    o = bpy.context.active_object; smooth(o); assign(o, candy(GREEN, 0.25))
    md = o.modifiers.new('b', 'BEVEL'); md.width = 0.03; md.segments = 3
    x, y, z = loc
    rbox((s * 0.22, 0.04, s * 0.6), (x - s * 0.2, y - 0.06, z - s * 0.08), bevel=0.02, mat=candy('#FFFFFF', 0.3), rot=(0, math.radians(-45), 0))
    rbox((s * 0.22, 0.04, s * 1.0), (x + s * 0.15, y - 0.06, z + s * 0.05), bevel=0.02, mat=candy('#FFFFFF', 0.3), rot=(0, math.radians(35), 0))

def curve_tube(pts, r, mat, poly=False):
    cu = bpy.data.curves.new('tube', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 4
    if poly:
        sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
        for i, p_ in enumerate(pts): sp.points[i].co = (*p_, 1)
    else:
        sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
        for i, p_ in enumerate(pts):
            bp = sp.bezier_points[i]; bp.co = p_; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new('tube', cu); bpy.context.collection.objects.link(o); cu.materials.append(mat); return o

def model_stack(x0=0.0, z0=0.45, n=5, gap=0.92, width=4.7, warm_upto=-1, seed=7, scale=1.0, hot=None):
    """模型：一摞奶白半透层板，上面是粉正蓝负的参数块；warm_upto = 已经走过的层（变暖黄）"""
    import random; rnd = random.Random(seed)
    zs = [z0 + k * gap * scale for k in range(n)]
    for k, z in enumerate(zs):
        rbox((width * scale, 0.34 * scale, 0.62 * scale), (x0, 0, z), bevel=0.14 * scale, seg=6,
             mat=candy('#FFEDB8' if k <= warm_upto else '#FAF8FF', rough=0.35, coat=0.6, sss=0.35))
        ncol = 10
        for r in range(2):
            for c in range(ncol):
                if c in (4, 5): continue
                v = rnd.uniform(-1, 1); col = PINK if v > 0 else BLUE
                x = x0 + (-2.05 + c * 0.455 + (0.08 if c > 5 else 0) - (0.08 if c < 4 else 0)) * scale * width / 4.7
                rbox((0.34 * scale, 0.1 * scale, 0.2 * scale), (x, -0.2 * scale, z + (0.13 - r * 0.26) * scale), bevel=0.05 * scale, seg=3,
                     mat=candy(col, rough=0.22 + 0.35 * (1 - abs(v)), sss=0.1))
        bpy.ops.mesh.primitive_torus_add(major_radius=0.2 * scale, minor_radius=0.03 * scale, location=(x0, -0.2 * scale, z), rotation=(math.pi / 2, 0, 0))
        t_ = bpy.context.active_object; smooth(t_); assign(t_, satin_metal('#BFB6E6', 0.3))
    if hot is not None:   # 发黄光的一段路：从最下面到 hot 高度
        bpy.ops.mesh.primitive_cylinder_add(radius=0.032 * scale, depth=hot - (zs[0] - 0.8 * scale), location=(x0, -0.2 * scale, (hot + zs[0] - 0.8 * scale) / 2), vertices=24)
        o = bpy.context.active_object; smooth(o); assign(o, emit(YEL, 2.2))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.026 * scale, depth=zs[-1] - zs[0] + 1.4 * scale, location=(x0, -0.2 * scale, (zs[-1] + zs[0]) / 2), vertices=24)
    o = bpy.context.active_object; smooth(o); assign(o, candy('#E9E5FA', 0.3))
    return zs

def ball(loc, r=0.15):
    sphere(r, loc, emit(YEL, 7.0)); sphere(r * 1.65, loc, glass('#FFE58A', 0.2))

def row(chars, x0, z, y=-0.6, s=0.6, step=0.72, rot=(0, 0, 0), marks=False):
    obs = []
    for k, ch in enumerate(chars):
        loc = (x0 + k * step, y, z); obs.append(token(ch, loc, s=s, rot=rot))
        if marks: bookmark(loc, s)
    return obs

def phone(ui_path, rot_z=-30, loc=(0, 0, 0), frame_box=False):
    ph = rbox((2.3, 0.34, 4.7), loc, bevel=0.4, seg=12, mat=satin_metal('#D6DAE4', 0.22))
    bez = rbox((2.2, 0.02, 4.6), (0, -0.17, 0), bevel=0.32, seg=8, mat=candy('#121318', 0.06)); bez.parent = ph
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.185, 0), rotation=(math.pi / 2, 0, 0))
    scr = bpy.context.active_object; scr.scale = (2.06, 4.46, 1)
    bpy.ops.object.transform_apply(scale=True)
    md = scr.modifiers.new('bev', 'BEVEL'); md.width = 0.28; md.segments = 8; md.affect = 'VERTICES'
    if ui_path and os.path.exists(ui_path): assign(scr, image_mat(ui_path, emit_strength=0.9))
    k1 = rbox((0.06, 0.14, 0.55), (1.16, 0, 1.0), bevel=0.025, mat=satin_metal('#C9CEDA'))
    cb = rbox((0.9, 0.08, 0.9), (0.5, 0.2, 1.6), bevel=0.2, mat=satin_metal('#C2C7D3', 0.3))
    for o in (scr, k1, cb): o.parent = ph
    ph.rotation_euler = (math.radians(6), 0, math.radians(rot_z))
    return ph

def ui(name): return os.path.join(F.ui_dir, name) if F.ui_dir else ''

# =====================================================================
# 每一拍
# =====================================================================
def o1(u):   # 手机里 AI 正在逐字回复，「去」从屏幕里浮出来
    reset('blue', halo=True)
    area((-4, -6, 6), (0, 0, 0), 800, 6); area((6, 4, 1.5), (0.5, 0, 0), 1400, 3, '#FFE2BF'); area((-6, 3, 3), (0, 0, 0), 700, 3, '#DCE8FF')
    phone(ui('ui_typing.png'))
    p = back_out(seg(u, 0.1, 0.6))
    token('去', (lerp(0.6, 1.5, p), lerp(-0.4, -1.7, p), lerp(0.45, 0.8, p)), s=0.95 * max(p, 0.05), rot=(0.12, 0, -0.3))
    yel_q((2.3, -1.25, -0.55), s=0.8, rot=(0.1, 0, -0.4))
    token('想', (-2.9, -5.2, -3.6), s=1.1, rot=(0.3, 0.2, 0.5))
    ANCH['qu'] = (1.5, -1.7, 1.4); ANCH['q'] = (2.3, -1.25, -1.1)
    cam((1.4, -15.0, 1.6), (0.5, 0, 0.45), 48, 2.0, 14.2)

def o2(u):   # 你以为它早就写好了整段？一整段淡淡的字叠在上面；最后打 ✕
    reset('blue', halo=True)
    area((-4, -6, 6), (0, 0, 0), 800, 6); area((6, 4, 1.5), (0.5, 0, 0), 1400, 3, '#FFE2BF')
    phone(ui('ui_typing.png'))
    for k, ch in enumerate('周末我想去海边看日落'):   # 「早就写好的整段」：半透明的幽灵字块
        r, c = divmod(k, 5)
        ob = token(ch, (-1.75 + c * 0.86, -2.0, 1.2 - r * 0.95), s=0.72, body='#EEF3FF')
        ob.data.materials.clear(); ob.data.materials.append(glass('#F4F7FF', 0.35))   # 「早就写好的整段」：磨砂玻璃，像影子
    if u > 0.7:
        xmark((0.0, -2.6, 0.75), size=3.6 * back_out(seg(u, 0.7, 0.85)))
    cam((0.6, -15.0, 1.4), (0.0, 0, 0.6), 46, 2.4, 13.0)

def o3(u):   # ✕ 碎掉，只剩光标后面的空位：真的一个字一个字地写
    reset('blue', halo=True)
    area((-4, -6, 6), (0, 0, 0), 800, 6); area((6, 4, 1.5), (0.5, 0, 0), 1400, 3, '#FFE2BF')
    phone(ui('ui_typing.png'))
    import random; rnd = random.Random(3)
    for i in range(10):   # ✕ 的碎片往下落、变小
        f_ = 1 - seg(u, 0, 0.5)
        if f_ <= 0: break
        rbox((0.4 * f_, 0.1, 0.12), (rnd.uniform(-1.5, 1.5), -2.6, 0.7 - 2.5 * seg(u, 0, 0.5) + rnd.uniform(-0.8, 0.8)), bevel=0.04,
             mat=candy('#FFFFFF', 0.3), rot=(rnd.uniform(0, 3), rnd.uniform(0, 3), 0))
    row('周末我想去', -1.6, -1.55, y=-2.2, s=0.62, step=0.7)
    yel_q((1.9, -2.2, -1.55), s=0.62)
    ANCH['q'] = (1.9, -2.2, -1.0)
    cam((0.6, -15.0, 0.4), (0.1, 0, -0.8), 46, 2.4, 13.0)

def stack_scene(warm=-1, hot=None, extra=None):
    reset('lilac'); lights((0, 0, 1))
    zs = model_stack(warm_upto=warm, hot=hot)
    return zs

def o4(u):   # 第一轮：整句送进模型，一层层亮过去；之后只送新写的那个字（旧字有存档标记）
    zs = stack_scene(warm=int(4.99 * seg(u, 0.05, 0.7)) if u < 0.7 else 4, hot=zs_hot(u))
    first = u < 0.4
    row('周末我想去', -1.8, -0.55, marks=not first)
    yel_q((1.8, -0.6, -0.55))
    if first:   # 整句一起往上送：每个字块到第一层各一根黄线
        for k in range(5):
            x = -1.8 + k * 0.72
            curve_tube([(x, -0.6, -0.2), (x * 0.5, -0.4, 0.0), (0, -0.2, zs[0] - 0.35)], 0.03, emit(YEL, 2.0))
    else:       # 之后：只送新写的那一个字
        curve_tube([(1.8, -0.6, -0.2), (0.9, -0.4, 0.0), (0, -0.2, zs[0] - 0.35)], 0.035, emit(YEL, 2.4))
    bz = lerp(zs[0] - 0.4, zs[-1], seg(u, 0.05, 0.7)); ball((0, -0.2, bz))
    ANCH['model'] = (0, 0, zs[-1] + 1.3); ANCH['row'] = (-1.1, -0.6, 0.15)
    cam((1.6, -32, 7.6), (0, 0, 0.35), 100, 5.6, 32.6)

def zs_hot(u): return 0.45 - 0.8 + (0.45 + 4 * 0.92 + 0.6 - (0.45 - 0.8)) * seg(u, 0.05, 0.7)

def o5(u):   # 回头看：新位置伸出细线连回前面每一个字（句子越长线越多）
    zs = stack_scene(warm=4)
    row('周末我想去', -1.8, -0.55, marks=True)
    yel_q((1.8, -0.6, -0.55))
    n = int(round(5 * ease(seg(u, 0.05, 0.6))))
    for k in range(n):
        x = -1.8 + k * 0.72
        h = 0.55 + 0.18 * (5 - k)
        curve_tube([(1.8, -0.75, -0.2), ((1.8 + x) / 2, -0.85, -0.2 + h), (x, -0.75, -0.2)], 0.022, emit('#FFF3C4', 3.0))
    ANCH['q'] = (1.8, -0.6, -1.4)
    cam((1.2, -30, 3.0), (0, 0, 0.35), 90, 5.6, 30)

def o6(u, stack=True):   # 给每个可能的下一个字打分：模型出口冒出候选排行条
    reset('lilac'); lights((0, 0, 1))
    zs = model_stack(z0=-1.9, n=3, warm_upto=2, scale=0.55) if stack else None
    cands = [('海', 0.41), ('睡', 0.18), ('爬', 0.12), ('吃', 0.09)]
    for i, (ch, p) in enumerate(cands):
        z = 3.4 - i * 0.92; g = ease(seg(u, 0.05 + i * 0.08, 0.45 + i * 0.08))
        token(ch, (-1.9, -0.4, z), s=0.7, body='#FFD45A' if i == 0 else '#FBF8F2')
        L = 3.6 * p / 0.41 * max(g, 0.02)
        rbox((L, 0.3, 0.42), (-1.4 + L / 2, -0.3, z), bevel=0.14, mat=candy(YEL if i == 0 else '#F2EEFF', 0.25, sss=0.2))
        ANCH[f'p{i}'] = (-1.4 + L + 0.45, -0.3, z)
    rbox((0.5, 0.3, 0.12), (-1.9, -0.4, 3.4 - 4 * 0.92 + 0.2), bevel=0.05, mat=candy('#F2EEFF', 0.3))   # 「…」后面还有很多
    cam((1.0, -30, 2.4), (0, 0, -0.05), 85, 5.6, 30)

def o7(u):   # 按分数抽签：转盘停在「海」，「海」飞进空位
    reset('lilac'); lights((0, 0, 1))
    shares = [('海', 0.41, YEL), ('睡', 0.18, '#FFFFFF'), ('爬', 0.12, '#E8E2FF'), ('吃', 0.09, '#FFFFFF'), ('…', 0.20, '#D9D0FA')]
    spin = 2 * math.pi * (3 * (1 - (1 - seg(u, 0, 0.55)) ** 3))   # 转整 3 圈，停下时「海」正对指针
    a = math.pi / 2 - 0.41 * math.pi + spin   # 停下来时「海」那一格正对指针（上方）
    cx, cz, R = 0, 2.0, 1.9
    for ch, p, col in shares:
        bm = bmesh.new(); seg_n = max(4, int(64 * p)); verts = [bm.verts.new((0, 0, 0))]
        for i in range(seg_n + 1):
            th = a + 2 * math.pi * p * i / seg_n; verts.append(bm.verts.new((R * math.cos(th), 0, R * math.sin(th))))
        for i in range(1, len(verts) - 1): bm.faces.new((verts[0], verts[i], verts[i + 1]))
        ext = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])          # 往后挤出厚度（bmesh 的 solidify 在这里厚度为 0，会发黑）
        bmesh.ops.translate(bm, vec=(0, 0.22, 0), verts=[e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        me = bpy.data.meshes.new('w'); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new('w', me); bpy.context.collection.objects.link(o); o.location = (cx, 0, cz); assign(o, candy(col, 0.3, sss=0.0))   # 薄片不能开次表面，否则会发黑
        mid = a + math.pi * p
        if ch != '…':
            t = text3d(ch, (cx + 1.2 * math.cos(mid), -0.3, cz + 1.2 * math.sin(mid)), 1.1, candy('#1E2440', 0.4), extrude=0.02, rot=(math.pi / 2, 0, 0))
        a += 2 * math.pi * p
    bpy.ops.mesh.primitive_cone_add(radius1=0.22, depth=0.45, location=(cx, -0.25, cz + R + 0.25), rotation=(0, math.pi, 0), vertices=32)
    o = bpy.context.active_object; smooth(o); assign(o, emit(YEL, 2.5))
    row('周末我想去', -1.8, -0.75, step=0.72)
    fly = ease(seg(u, 0.6, 0.95))
    hai = (lerp(cx, 1.8, fly), lerp(-0.4, -0.6, fly), lerp(cz + 1.2, -0.75, fly))
    token('海', hai, s=0.6, body='#FFD45A')
    cam((1.0, -30, 4.2), (0, 0, 0.75), 100, 5.6, 30)

def branch_scene(up_n, dn_n, show_split=True, chosen=True):
    reset('peach'); lights((1, 0, 0), key=850, fill=300, rim=800)
    s = 0.56; step = 0.66; yaw = -0.35
    stem = [(-4.6, 0, 0), (-3.0, 0, 0), (-1.2, 0, 0), (0.0, 0, 0)]
    ribbon(stem, 0.9, gradient_glass('#FFF4EC', '#FFE6D6', 'X', 0.12, -4.6, 0), thick=0.06)
    for k, ch in enumerate('周末我想去'):
        token(ch, (-4.2 + k * step, -0.05, s / 2 + 0.05), s=s, rot=(0, 0, yaw))
    if show_split:
        up = [(0.0, 0, 0), (1.0, 0, 0.7), (2.0, 0, 2.5), (3.4, 0, 3.1), (5.9, 0, 3.15)]
        for sgn, chars, n in ((1, '海边看日落', up_n), (-1, '睡个懒觉', dn_n)):
            if n <= 0: continue
            ribbon([(p[0], p[1], p[2] * sgn) for p in up], 0.9, gradient_glass('#FFE6D6', '#FFF4EC', 'X', 0.12, 0, 5.6), thick=0.06)
            for k, ch in enumerate(chars[:n]):
                token(ch, (2.75 + k * step, -0.05, 3.13 * sgn + s / 2 + 0.08), s=s, body='#FFD45A' if k == 0 else '#FBF8F2', rot=(0, 0, yaw))
        sphere(0.2, (0.3, -0.05, 0.45), emit(YEL, 6)); sphere(0.34, (0.3, -0.05, 0.45), glass('#FFE58A', 0.2))
    cam((-9.85, -10.17, 1.4), (-0.05, 0.23, -0.35), 31.5, 2.8, 14.0)

def o8(u):   # 为什么不能几个字一起写？镜头退回「去」后面的空位，一分为二
    reset('peach'); lights((1, 0, 0), key=850, fill=300, rim=800)
    s = 0.56; step = 0.66; yaw = -0.35
    ribbon([(-4.6, 0, 0), (-3.0, 0, 0), (-1.2, 0, 0), (0.0, 0, 0)], 0.9, gradient_glass('#FFF4EC', '#FFE6D6', 'X', 0.12, -4.6, 0), thick=0.06)
    for k, ch in enumerate('周末我想去'):
        token(ch, (-4.2 + k * step, -0.05, s / 2 + 0.05), s=s, rot=(0, 0, yaw))
    g = ease(seg(u, 0.2, 0.9))
    up = [(0.0, 0, 0), (0.6 * g + 0.01, 0, 0.5 * g), (1.2 * g + 0.02, 0, 1.6 * g)]
    for sgn in (1, -1):
        ribbon([(p[0], p[1], p[2] * sgn) for p in up], 0.9, gradient_glass('#FFE6D6', '#FFF4EC', 'X', 0.12, 0, 2), thick=0.06)
    yel_q((0.7, -0.05, s / 2 + 0.05), s=s, rot=(0, 0, yaw))
    cam((-7.2, -9.0, 1.6), (-1.3, 0.2, 0.1), 38, 2.8, 10.8)

def o9(u): branch_scene(up_n=1 + int(4 * ease(seg(u, 0.1, 0.8))), dn_n=0)
def o10(u): branch_scene(up_n=5, dn_n=1 + int(3 * ease(seg(u, 0.1, 0.8))))

def o11(u):  # 回到一句：紧挨着的是黄色「?」，再往后一排灰色「?」
    reset('peach'); lights((1, 0, 0), key=850, fill=300, rim=800)
    s = 0.6; step = 0.72
    ribbon([(-4.0, 0, -0.5), (0, 0, -0.5), (5.0, 0, -0.5)], 0.95, gradient_glass('#FFF4EC', '#FFE6D6', 'X', 0.12, -4, 5), thick=0.06)
    row('周末我想去', -3.6, -0.5 + s / 2 + 0.05, y=-0.05, s=s, step=step)
    yel_q((-3.6 + 5 * step, -0.05, -0.5 + s / 2 + 0.05), s=s)
    for k in range(6, 10):
        gray_q((-3.6 + k * step, -0.05, -0.5 + s / 2 + 0.05), s=s)
    ANCH['q'] = (-3.6 + 5 * step, -0.05, 0.7); ANCH['gray'] = (-3.6 + 8 * step, -0.05, 0.7)
    cam((-2.9, -16, 2.6), (0.0, 0, -0.1), 38, 3.5, 16)

def o12(u):  # 显卡再多核，也只能一个字接一个字：显卡芯片里上万个绿色小核，沿着句子一格一格往前推
    reset('mint'); lights((0, 0, 0), key=900, fill=300, rim=1000)
    rbox((5.2, 0.5, 5.2), (0, 0.4, -0.2), bevel=0.25, mat=satin_metal('#5A6070', 0.35))     # 封装
    rbox((4.0, 0.2, 4.0), (0, 0.05, -0.2), bevel=0.08, mat=candy('#2B2F3D', 0.3))            # 芯片
    import random; rnd = random.Random(5)
    nx, nz = 16, 16; cw = 3.6 / nx
    front = int(5 * ease(seg(u, 0.1, 0.9)))   # 句子推进到第几个字
    for i in range(nx):
        for j in range(nz):
            lit = rnd.random() < 0.35
            col = GREEN if lit else '#1F5E44'
            o = rbox((cw * 0.72, 0.08, cw * 0.72), (-1.8 + cw * (i + 0.5), -0.1, -2.0 + cw * (j + 0.5)), bevel=0.02, seg=2,
                     mat=emit(col, 2.2) if lit else candy(col, 0.4))
    s = 0.6; step = 0.72
    X0 = -2.4
    for k, ch in enumerate('周末我想去'):
        token(ch, (X0 + k * step, -1.0, 2.7), s=s)
    xq = X0 + 5 * step
    yel_q((xq, -1.0, 2.7), s=s)
    gray_q((X0 + 6 * step, -1.0, 2.7), s=s)
    # 一道光沿着句子往前推：落在当前正在写的位置
    rbox((0.75, 0.05, 0.12), (xq, -1.05, 2.2), bevel=0.04, mat=emit(YEL, 3.0))
    ANCH['gpu'] = (0, -0.1, -2.6)
    cam((2.0, -24, 4.3), (0.0, 0, -1.4), 64, 4.0, 24)

def o13(u):  # 学说话的时候：一整段现成的文章摊开
    reset('butter'); lights((0, 0, 0))
    text = '周末我想去海边看日落'
    rbox((6.0, 0.2, 2.6), (0, 0.35, 0), bevel=0.15, mat=candy('#FFF8E6', 0.4, sss=0.3))   # 一张「纸」
    for k, ch in enumerate(text):
        r, c = divmod(k, 5); g = back_out(seg(u, 0.05 + 0.04 * k, 0.4 + 0.04 * k))
        token(ch, (-2.2 + c * 1.1, -0.1, 0.6 - r * 1.15), s=0.8 * max(g, 0.02))
    ANCH['page'] = (0, 0, 1.75)
    cam((1.0, -20, 4.5), (0, 0, -0.1), 58, 4.0, 20)

def o14(u):  # 整段每个位置同时猜下一个字、同时对答案：一排绿勾一起亮
    reset('butter'); lights((0, 0, 0))
    text = '周末我想去海边看日落'
    rbox((6.0, 0.2, 2.6), (0, 0.35, 0), bevel=0.15, mat=candy('#FFF8E6', 0.4, sss=0.3))
    on = u > 0.45
    for k, ch in enumerate(text):
        r, c = divmod(k, 5); loc = (-2.2 + c * 1.1, -0.1, 0.6 - r * 1.15)
        token(ch, loc, s=0.8)
        if on and k < len(text) - 1:
            check((loc[0] + 0.5, -0.65, loc[2] + 0.45), s=0.2 * back_out(seg(u, 0.45, 0.6)))
    cam((1.0, -20, 4.5), (0, 0, -0.1), 58, 4.0, 20)

def spec_row(drafts=0, sweep=None, verdict=False):
    s = 0.5; step = 0.58; X0 = -4.6 * step
    row('周末我想去', X0, -0.6, step=step, s=s)
    xs = [X0 + (5 + k) * step for k in range(4)]
    chars = '海边吃饭'
    for k, x in enumerate(xs):
        if k < drafts:
            if verdict and k >= 2:   # 「吃」对不上 → 作废；它后面的「饭」也一起作废：压暗、掉到下面、打 ✕
                draft_tok(chars[k], (x, -0.6, -1.4), s=s, body='#BDB6CF')
                xmark((x, -0.95, -1.4), size=0.62, thick=0.07)
            elif verdict:
                token(chars[k], (x, -0.6, -0.6), s=s)
                check((x, -0.95, -0.6 + 0.55), s=0.18)
            else:
                draft_tok(chars[k], (x, -0.6, -0.6), s=s)
        else:
            gray_q((x, -0.6, -0.6), s=s) if k > 0 else yel_q((x, -0.6, -0.6), s=s)
    if sweep is not None:
        rbox((0.1, 0.1, 1.15), (lerp(xs[0] - 0.4, xs[-1] + 0.4, sweep), -0.95, -0.6), bevel=0.04, mat=emit('#FFFFFF', 3.0))
        for x in xs:   # 4 个位置同时亮
            rbox((0.5, 0.05, 0.08), (x, -0.95, -0.98), bevel=0.03, mat=emit('#FFFFFF', 3.0))
    return xs

def o15(u):  # 那就先造一段「现成的」话：「海」退回去，空位回到「去」后面
    reset('rose'); lights((0, 0, 0))
    spec_row(drafts=0)
    ANCH['q'] = (0.4 * 0.58, -0.6, 0.05)
    cam((0.4, -18, 2.4), (0.0, 0, -0.1), 55, 3.5, 18)

def o16(u):  # 小模型先抢答几个字：一个小格子表飞快地连填 4 个字（草稿）
    reset('rose'); lights((0, 0, 0))
    model_stack(x0=1.6, z0=0.6, n=2, gap=0.92, scale=0.55, warm_upto=1, seed=3)
    xs = spec_row(drafts=int(4.99 * seg(u, 0.15, 0.8)))
    ANCH['small'] = (1.6, 0, 2.0)
    cam((0.4, -18, 2.4), (0.0, 0, 0.5), 55, 3.5, 18)

def o17(u):  # 大模型一次全部批改：一摞大格子表一次扫过 4 个字，4 个位置同时亮
    reset('rose'); lights((0, 0, 0))
    model_stack(x0=1.0, z0=0.8, n=4, gap=0.6, scale=0.6, warm_upto=3, seed=7)
    xs = spec_row(drafts=4, sweep=ease(seg(u, 0.2, 0.8)))
    ANCH['big'] = (1.0, 0, 3.3)
    cam((0.4, -20, 2.8), (0.0, 0, 0.7), 55, 3.5, 20)

def o18(u):  # 批改 4 个字和写 1 个字差不多快：两根计时条几乎一样长
    reset('rose'); lights((0, 0, 0))
    g = ease(seg(u, 0.1, 0.7))
    token('海', (-2.7, -0.4, 1.1), s=0.62)
    rbox((3.4 * g + 0.05, 0.3, 0.42), (-2.1 + (3.4 * g) / 2, -0.3, 1.1), bevel=0.14, mat=candy('#FFFFFF', 0.25))
    for k, ch in enumerate('海边吃饭'):
        draft_tok(ch, (-2.95 + (k % 2) * 0.55, -0.4, -0.55 + (0.28 if k < 2 else -0.28)), s=0.46)
    rbox((3.55 * g + 0.05, 0.3, 0.42), (-2.1 + (3.55 * g) / 2, -0.3, -0.55), bevel=0.14, mat=candy('#FFFFFF', 0.25))
    ANCH['w1'] = (-0.4, -0.3, 1.65); ANCH['w4'] = (-0.4, -0.3, 0.0)
    cam((-0.4, -18, 2.0), (-1.1, 0, 0.3), 58, 4.0, 18)

def mem_scene(u, fan=False):
    reset('mint'); lights((0, 0, 0), key=900, fill=300, rim=1000)
    for i in range(4):   # 显存：一摞蓝色薄片（记 = 蓝）
        rbox((1.6, 1.2, 0.22), (-2.6, 0.2, -1.6 + i * 0.3), bevel=0.06, mat=candy('#6F86C9', 0.3, sss=0.1))
    rbox((2.4, 0.4, 2.4), (2.4, 0.3, 1.4), bevel=0.12, mat=candy('#2B2F3D', 0.3))   # 计算核心
    import random; rnd = random.Random(9)
    lit_frac = 0.12 if not fan else 0.85
    for i in range(6):
        for j in range(6):
            lit = rnd.random() < lit_frac
            rbox((0.26, 0.08, 0.26), (2.4 - 1.0 + i * 0.4, 0.05, 1.4 - 1.0 + j * 0.4), bevel=0.02, seg=2,
                 mat=emit(GREEN, 2.2) if lit else candy('#1F5E44', 0.4))
    # 传送带：从显存到核心，粉蓝参数块排队搬过来
    curve_tube([(-1.8, -0.2, -1.1), (0, -0.4, -0.6), (1.2, -0.3, 0.6)], 0.16, candy('#F3F0FA', 0.4))
    for k in range(9):
        w = (k / 9 + 0.35 * u) % 1.0
        p0, p1, p2 = Vector((-1.8, -0.45, -0.95)), Vector((0, -0.65, -0.45)), Vector((1.2, -0.55, 0.75))
        pt = (1 - w) ** 2 * p0 + 2 * (1 - w) * w * p1 + w * w * p2
        rbox((0.22, 0.12, 0.16), tuple(pt), bevel=0.04, mat=candy(PINK if k % 2 else BLUE, 0.25))
    ANCH['mem'] = (-2.6, 0, -0.2); ANCH['core'] = (2.4, 0, 2.9)

def o19(u):
    mem_scene(u, fan=False)
    cam((-0.2, -22, 4.0), (-0.3, 0, 0.4), 46, 4.0, 22)

def o20(u):  # 搬一趟，就能顺便批好几个字：一批参数同时用到 4 个位置
    mem_scene(u, fan=True)
    xs = [-1.5 + k * 1.0 for k in range(4)]
    for k, ch in enumerate('海边吃饭'):
        draft_tok(ch, (xs[k], -0.8, -2.9), s=0.6)
        curve_tube([(2.4, -0.3, 0.2), ((2.4 + xs[k]) / 2, -0.6, -1.2), (xs[k], -0.8, -2.5)], 0.03, emit(YEL, 2.0))
    cam((-0.2, -24, 3.0), (-0.3, 0, -0.4), 46, 4.0, 24)

def o21(u):  # 对得上的全收下，从第一个对不上的接着来：「海 边」✓，「吃」✕ 换成「看」，「饭」一起作废
    reset('rose'); lights((0, 0, 0))
    xs = spec_row(drafts=4, verdict=u > 0.25)
    if u > 0.55:   # 大模型自己的「看」接上来
        token('看', (xs[2], -0.6, lerp(0.6, -0.6, back_out(seg(u, 0.55, 0.8)))), s=0.5, body='#FFD45A')
        ANCH['own'] = (xs[2], -0.6, 0.15)
    cam((0.4, -18, 2.0), (0.0, 0, -0.9), 55, 3.5, 18)

def o22(u):  # 一步就出好几个字，快 2–3 倍：3D 大字
    reset('lilac'); lights((0, 0, 0))
    g = back_out(seg(u, 0.15, 0.5))
    smiley = '/usr/share/fonts/truetype/smiley-sans/SmileySans-Oblique.ttf'
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = '2–3倍'; cu.font = bpy.data.fonts.load(smiley)
    cu.size = 2.6 * max(g, 0.02); cu.extrude = 0.18; cu.bevel_depth = 0.05; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    ob = bpy.data.objects.new('t', cu); bpy.context.collection.objects.link(ob); ob.location = (0, 0, 1.5); ob.rotation_euler = (math.pi / 2, 0, 0)
    cu.materials.append(candy(YEL, 0.2, sss=0.2))
    row('海边', -0.72, -0.5, step=0.72); token('看', (0.72, -0.6, -0.5), s=0.6, body='#FFD45A')
    cam((0.8, -18, 2.4), (0, 0, 0.0), 60, 4.0, 18)

def o23(u):  # 回到聊天气泡（放在示意框里）：这次一小段一小段地蹦
    reset('blue', halo=True)
    area((-4, -6, 6), (0, 0, 0), 800, 6); area((6, 4, 1.5), (0.5, 0, 0), 1400, 3, '#FFE2BF')
    phone(ui('ui_chunks.png'), rot_z=-18)
    s = 0.62
    for k, ch in enumerate('海边看'):
        p = back_out(seg(u, 0.2 + 0.05 * k, 0.6 + 0.05 * k))
        token(ch, (0.55 + k * 0.62, -1.8, 0.95), s=0.56 * max(p, 0.02), rot=(0.1, 0, -0.2))
    cam((1.0, -15.0, 1.4), (0.4, 0, 0.3), 48, 2.2, 14.0)

def o24(u):  # 片尾大字（2D 层）：背景是虚掉的手机
    reset('blue', halo=True)
    area((-4, -6, 6), (0, 0, 0), 800, 6)
    phone(ui('ui_chunks.png'), rot_z=-18)
    cam((1.0, -15.0, 1.4), (0.4, 0, 0.3), 48, 1.2, 9.0)

def o25(u):  # 片尾卡（2D 层）
    reset('blue', halo=True)
    cam((0, -10, 0), (0, 0, 0), 50, 4.0, 10)

# ---------------- v3 补的拍（11-19，补 1–6） ----------------
NUMCOL = '#8FE3FF'
def num_strip(x0, z, n=12, y=-0.6, cw=0.34, seed=1, glow=False):
    """数字条：一串数（深蓝底小块 + 青色数字），符号表里的「数字条」"""
    import random; rnd = random.Random(seed)
    for i in range(n):
        x = x0 + i * (cw + 0.04)
        rbox((cw, 0.16, cw * 1.25), (x, y, z), bevel=0.05, seg=3, mat=candy('#1D2350', 0.3))
        d = str(rnd.randint(0, 9))
        t = text3d(d, (x, y - 0.09, z - 0.02), cw * 1.9, emit(NUMCOL, 2.5 if glow else 1.6), extrude=0.008, rot=(math.pi / 2, 0, 0))

def n_strip(u):   # 补 1：一个字进模型，先变成一串数
    reset('lilac'); lights((0, 0, 0))
    model_stack(z0=1.6, n=3, gap=0.92, scale=0.8, seed=7)
    g = ease(seg(u, 0.1, 0.6))
    token('去', (lerp(-1.2, -2.4, g), -0.6, -0.9), s=0.9)
    n = max(1, int(round(12 * g)))
    num_strip(-1.75, -0.9 + 1.1 * g * 0, n=n, y=-0.6) if g > 0.05 else None
    curve_tube([(0.4, -0.5, -0.4), (0.4, -0.4, 0.4), (0.0, -0.3, 1.0)], 0.03, emit(YEL, 2.0))
    ANCH['strip'] = (0.3, -0.6, -0.25)
    cam((0.6, -24, 3.0), (0, 0, 0.6), 70, 4.0, 24)

def n_mult(u):    # 补 1：每一层拿这串数和参数表乘一下、加起来，交给下一层
    reset('lilac'); lights((0, 0, 0))
    import random; rnd = random.Random(11)
    # 一块层板，上面一格格参数
    rbox((5.0, 0.4, 1.6), (0, 0.1, 0.6), bevel=0.18, mat=candy('#FAF8FF', 0.35, coat=0.6, sss=0.35))
    for r in range(3):
        for c in range(10):
            v = rnd.uniform(-1, 1)
            rbox((0.36, 0.1, 0.3), (-2.07 + c * 0.46, -0.15, 1.05 - r * 0.42), bevel=0.05, seg=3,
                 mat=candy(PINK if v > 0 else BLUE, 0.22 + 0.35 * (1 - abs(v)), sss=0.1))
    num_strip(-2.1, -0.95, n=12, y=-0.6, seed=2)                                   # 进来的一串数
    k = int(10 * seg(u, 0.1, 0.8))
    for c in range(min(k, 10)):   # 乘加：黄色小方块一闪，从下往上
        rbox((0.16, 0.16, 0.16), (-2.07 + c * 0.46, -0.45, 0.6 + 0.25 * math.sin(c)), bevel=0.04, mat=emit(YEL, 3.5))
    if u > 0.6: num_strip(-2.1, 2.05, n=12, y=-0.6, seed=5, glow=True)             # 出来一串新的数
    ANCH['layer'] = (2.2, -0.2, 1.55); ANCH['in'] = (-2.4, -0.6, -1.5)
    cam((0.6, -24, 2.4), (0, 0, 0.55), 66, 4.0, 24)

def n_attnlong(u):  # 补 3：聊得越长，每个字要回头看的越多
    reset('lilac'); lights((0, 0, 0))
    text = '周末我想去海边看日落然后'
    n = 5 + int(round(6 * ease(seg(u, 0.05, 0.75))))
    s_ = 0.5; step = 0.58; x0 = -3.2
    for k in range(n):
        x = x0 + k * step; token(text[k], (x, -0.6, -0.8), s=s_); bookmark((x, -0.6, -0.8), s_)
    xq = x0 + n * step; yel_q((xq, -0.6, -0.8), s=s_)
    for k in range(n):
        x = x0 + k * step; h = 0.4 + 0.14 * (n - k)
        curve_tube([(xq, -0.75, -0.5), ((xq + x) / 2, -0.85, -0.5 + h), (x, -0.75, -0.5)], 0.018, emit('#FFF3C4', 3.0))
    cam((0.2, -22, 2.4), (0.0, 0, 0.2), 58, 4.0, 22)

def n_tail(u):      # 补 2：其实它认识的十几万个字，每个都打了分
    o6(1.0, stack=False)
    # 排行条后面一条很长、很淡的尾巴：越来越短、越来越淡，望不到头
    g = ease(seg(u, 0.1, 0.8))
    for i in range(int(26 * g)):
        z = 3.4 - 4 * 0.92 - 0.25 - i * 0.12
        L = max(0.05, 0.7 * math.exp(-i / 9))
        rbox((L, 0.12, 0.07), (-1.4 + L / 2, -0.3, z), bevel=0.03, seg=2, mat=candy('#EDE7FF', 0.4))
    ANCH['tail'] = (0.6, -0.3, -2.4)

def n_mem16(u):     # 补 4：写一个字要搬 16 GB
    mem_scene(u, fan=False)
    smiley = '/usr/share/fonts/truetype/smiley-sans/SmileySans-Oblique.ttf'
    g = back_out(seg(u, 0.1, 0.45))
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = '16 GB'; cu.font = bpy.data.fonts.load(smiley)
    cu.size = 1.7 * max(g, 0.02); cu.extrude = 0.12; cu.bevel_depth = 0.035; cu.align_x = 'CENTER'
    ob = bpy.data.objects.new('t', cu); bpy.context.collection.objects.link(ob); ob.location = (-2.2, -0.6, 0.15); ob.rotation_euler = (math.pi / 2, 0, 0)
    cu.materials.append(candy('#FFFFFF', 0.2))
    cam((-0.2, -22, 4.0), (-0.3, 0, 0.4), 46, 4.0, 22)

def n_timing(u):    # 补 4：光搬就要约 16 毫秒，真正的乘加只要 0.1 毫秒
    reset('mint'); lights((0, 0, 0), key=900, fill=300, rim=1000)
    g = ease(seg(u, 0.1, 0.8))
    for i in range(3): rbox((0.9, 0.7, 0.14), (-2.6, 0.1, 1.0 + i * 0.18), bevel=0.04, mat=candy('#6F86C9', 0.3))   # 搬（显存，蓝）
    rbox((4.4 * g + 0.05, 0.3, 0.42), (-1.9 + (4.4 * g) / 2, -0.3, 1.2), bevel=0.14, mat=candy('#6F86C9', 0.25))
    rbox((0.8, 0.3, 0.8), (-2.6, 0.2, -0.6), bevel=0.08, mat=candy('#2B2F3D', 0.3))                       # 算（核心，绿）
    for i in range(3):
        for j in range(3):
            rbox((0.16, 0.06, 0.16), (-2.85 + i * 0.25, 0.0, -0.85 + j * 0.25), bevel=0.02, seg=2, mat=emit(GREEN, 2.0) if (i + j) % 4 == 0 else candy('#1F5E44', 0.4))
    Lc = max(0.028, 4.4 * g / 160)   # 按比例：算 ≈ 搬的 1/160
    rbox((Lc, 0.3, 0.42), (-1.9 + Lc / 2, -0.3, -0.6), bevel=0.01, mat=candy(GREEN, 0.25))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.42, minor_radius=0.04, location=(-1.9, -0.45, -0.6), rotation=(math.pi / 2, 0, 0))
    o = bpy.context.active_object; smooth(o); assign(o, candy('#FFFFFF', 0.25))   # 放大框：圈住那一小截
    ANCH['move'] = (-1.9 + 4.4 * g + 0.6, -0.3, 1.2); ANCH['calc'] = (-1.2, -0.3, -0.6)
    cam((0.0, -18, 2.0), (-0.3, 0, 0.3), 58, 4.0, 18)

def n_accept(u):    # 补 6：所以写出来的话，和大模型自己写的一样（上下两句并排，一模一样，同时亮绿勾）
    reset('rose'); lights((0, 0, 0))
    s_ = 0.48; step = 0.55; X0 = -4.0 * step
    for zr, body in ((0.5, '#FBF8F2'), (-0.9, '#FBF8F2')):
        row('周末我想去海边看', X0, zr, step=step, s=s_)
    if u > 0.35:
        for zr in (0.5, -0.9):
            check((X0 + 7 * step + 0.55, -0.7, zr), s=0.18 * back_out(seg(u, 0.35, 0.55)))
    ANCH['top'] = (X0 + 3.5 * step, -0.6, 1.25); ANCH['bot'] = (X0 + 3.5 * step, -0.6, -1.65)
    cam((0.4, -18, 2.0), (0.0, 0, -0.15), 55, 3.5, 18)

def n_easy(u):      # 补 5：小模型猜得准的，多半是好猜的字（睡个懒 → 觉）
    reset('rose'); lights((0, 0, 0))
    s_ = 0.6; step = 0.7; X0 = -2.1
    row('睡个懒', X0 + step, -0.6, step=step, s=s_)
    x = X0 + 4 * step
    draft_tok('觉', (x, -0.6, -0.6), s=s_)
    if u > 0.4: check((x, -0.95, -0.6 + 0.6), s=0.22 * back_out(seg(u, 0.4, 0.6)))
    model_stack(x0=1.4, z0=1.2, n=2, gap=0.92, scale=0.5, warm_upto=1, seed=3)
    ANCH['small'] = (1.4, 0, 2.4); ANCH['easy'] = (x, -0.6, -1.4)
    cam((0.4, -18, 2.4), (0.0, 0, 0.3), 58, 3.5, 18)

def n_hard(u):      # 补 5：难猜的常对不上，对不上就从那儿接着来（回到「海边吃饭」那句：海边后面做什么，难猜）
    reset('rose'); lights((0, 0, 0))
    xs = spec_row(drafts=4, verdict=u > 0.3)
    if u > 0.5: token('看', (xs[2], -0.6, lerp(0.6, -0.6, back_out(seg(u, 0.5, 0.75)))), s=0.5, body='#FFD45A')
    ANCH['hard'] = (xs[2] - 0.3, -0.6, 0.3); ANCH['count'] = (xs[0] - 0.5, -0.6, 1.05)
    cam((0.4, -18, 2.0), (0.0, 0, -0.9), 55, 3.5, 18)


# ---------------- 自动取景：把所有物体和标签锚点收进安全框（审核节点 ②：右边缘 ≤ x940，不压小字和字幕） ----------------
def screen_box(extra_pts=()):
    from bpy_extras.object_utils import world_to_camera_view as w2c
    bpy.context.view_layer.update()
    xs, ys = [], []
    dg = bpy.context.evaluated_depsgraph_get()
    for o in bpy.data.objects:
        if o.type not in ('MESH', 'CURVE', 'FONT') or o.get('deco'): continue
        oe = o.evaluated_get(dg)
        for c in oe.bound_box:
            v = w2c(sc, sc.camera, oe.matrix_world @ Vector(c))
            if v.z <= 0: continue
            xs.append(v.x); ys.append(1 - v.y)
    for pt in extra_pts:
        v = w2c(sc, sc.camera, Vector(pt))
        if v.z > 0: xs += [v.x - 0.11, v.x + 0.11]; ys += [1 - v.y - 0.02, 1 - v.y + 0.02]   # 标签条大约这么宽
    return min(xs), max(xs), min(ys), max(ys)

def autofit(bottom=0.64, top=0.12, left=0.07, right=0.86, fill=0.94, iters=7):
    cam_o = sc.camera; cd_ = cam_o.data
    for _ in range(iters):
        x0, x1, y0, y1 = screen_box(ANCH.values())
        k = max((x1 - x0) / ((right - left) * fill), (y1 - y0) / ((bottom - top) * fill))
        fwd = cam_o.matrix_world.to_quaternion() @ Vector((0, 0, -1))
        rgt = cam_o.matrix_world.to_quaternion() @ Vector((1, 0, 0))
        up = cam_o.matrix_world.to_quaternion() @ Vector((0, 1, 0))
        d = cd_.dof.focus_distance
        # 拉远 / 推近：画面里的大小大约和距离成反比
        nd = d * k
        cam_o.location = cam_o.location - fwd * (nd - d); cd_.dof.focus_distance = nd
        # 平移：把内容中心移到安全框中心
        Hw = cd_.sensor_height / cd_.lens * nd; Ww = Hw * 1080 / 1920
        dx = ((x0 + x1) / 2 - (left + right) / 2) / k
        dy = ((y0 + y1) / 2 - (top + bottom) / 2) / k
        cam_o.location = cam_o.location + rgt * dx * Ww - up * dy * Hw
        bpy.context.view_layer.update()
        if abs(k - 1) < 0.02 and abs(dx) < 0.005 and abs(dy) < 0.005: break

# ---------------- v3 的顺序（34 拍），时间从 script.md 的逐句字幕 v3 表读，保证和字幕同步 ----------------
V3 = ['o1', 'o2', 'o3', 'o4', 'n_strip', 'n_mult', 'o5', 'n_attnlong', 'o6', 'n_tail', 'o7',
      'o8', 'o9', 'o10', 'o11', 'o12', 'o13', 'o14', 'o15', 'o16', 'o17', 'o18', 'o19', 'n_mem16', 'n_timing',
      'o20', 'o21', 'n_easy', 'n_hard', 'n_accept', 'o22', 'o23', 'o24', 'o25']
def read_times():
    md = open(os.path.join(here, '..', '..', 'script.md'), encoding='utf-8').read()
    sec = md[md.index('## 逐句字幕 v3'):]
    rows = [l for l in sec.split('\n') if re.match(r'^\| \d+ \|', l)]
    out = []
    for l in rows:
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        t0, t1 = c[1].split('–'); out.append((int(c[0]), float(t0), float(t1), bool(c[4].strip())))
    return out
import re
TIMES = read_times()
assert len(TIMES) == len(V3), (len(TIMES), len(V3))

def beat_at(t):
    for (b, t0, t1, _n) in TIMES:
        if t < t1 or b == len(TIMES): return b, clamp((t - t0) / (t1 - t0))

CU = {'o2': 0.85, 'o4': 0.3, 'o5': 0.7, 'o6': 0.8, 'o7': 0.8, 'o8': 0.8, 'o9': 0.9, 'o10': 0.9, 'o14': 0.8, 'o16': 0.85, 'o17': 0.55,
      'o18': 0.9, 'o20': 0.7, 'o21': 0.9, 'o22': 0.8, 'o23': 0.9, 'n_strip': 0.8, 'n_mult': 0.85, 'n_attnlong': 0.9, 'n_tail': 0.9,
      'n_mem16': 0.7, 'n_timing': 0.9, 'n_accept': 0.6, 'n_easy': 0.8, 'n_hard': 0.8}
jobs = []
if F.times:
    for x in F.times.split(','):
        b, u = beat_at(float(x)); jobs.append((f't{float(x):06.2f}', b, u))
else:
    bs = [int(x) for x in F.beats.split(',')] if F.beats else list(range(1, len(V3) + 1))
    jobs = [(f'b{b:02d}', b, CU.get(V3[b - 1], F.u)) for b in bs]
for name, b, u in jobs:
    fn = V3[b - 1]
    globals()[fn](u)
    if fn not in ('o1', 'o2', 'o3', 'o23', 'o24', 'o25'):
        autofit(bottom=0.63 if TIMES[b - 1][3] else 0.69)
    bpy.context.view_layer.update()
    sc.render.filepath = os.path.join(F.outdir, name + '.png')
    bpy.ops.render.render(write_still=True)
    meta = {'beat': b, 'fn': fn, 'u': u, 'anch': {k: [round(c, 4) for c in world_to_camera_view(sc, sc.camera, Vector(v))[:2]] for k, v in ANCH.items()}}
    json.dump(meta, open(os.path.join(F.outdir, name + '.json'), 'w'))
