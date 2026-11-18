# 一语道破 EP01「AI 又不打游戏，为什么还要用显卡？」—— 三个写实镜头的 Blender 场景（Cycles）。
# 自包含：不依赖贴图文件，全部程序生成；同一个脚本在本机（CPU、低清看构图）和 RunPod（GPU、成片分辨率）上跑。
#
#   DC     A 段：数据中心冷通道，相机沿通道缓慢推进（机柜、GPU 服务器前面板、顶部线槽、黄色光纤槽）
#   MACRO  A 段：AI 加速器模组微距，相机贴着电路板滑向封装，焦点落在大芯片边缘
#   CHIP   E 段：从正上方俯视大芯片开始（对齐 D 段的抽象运算阵列），慢慢拉远、倾斜，露出两侧 6 颗 HBM
#
# 结构是「示意的通用 AI 加速器」，不对应具体型号：中间一颗大 GPU 芯片 + 两侧各 3 颗 HBM 堆叠，
# 同在硅中介层上，下面是有机基板，再焊在模组电路板上（2.5D 封装，见 FACTS.md）。
#
# 用法（blender -b --python-exit-code 1 --python ep01_scenes.py -- 参数）：
#   still  <镜头> <秒> <输出.png> [宽x高] [采样]          看构图
#   anim   <镜头> <输出目录> <起始帧> <结束帧> [宽x高] [采样] [cpu|gpu]
#   anchors <镜头> <输出.json> [宽x高]                       逐帧投影：大芯片四角、6 颗 HBM 中心（给 Remotion 叠加层）
#   save   <镜头> <输出.blend>
import bpy, bmesh, math, random, sys, json, os
from mathutils import Vector, Matrix

FPS = 30
SHOTS = {'DC': 135, 'MACRO': 135, 'CHIP': 300, 'SERVER': 300, 'RACK': 300}     # 每个镜头的帧数（含前后余量）
rad = math.radians

# ------------------------------------------------------------------ 基础
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.render.fps = FPS
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.render.film_transparent = False
    return sc

def mat(name, base, metal=0.0, rough=0.5, emit=None, estr=0.0, coat=0.0, noise=0.0, nscale=20.0, spec=0.5, bump=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*base, 1)
    b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = estr
    if noise > 0 or bump > 0:
        tc = nt.nodes.new('ShaderNodeTexCoord'); n = nt.nodes.new('ShaderNodeTexNoise')
        n.inputs['Scale'].default_value = nscale; n.inputs['Detail'].default_value = 6
        nt.links.new(tc.outputs['Object'], n.inputs['Vector'])
        if noise > 0:
            mr = nt.nodes.new('ShaderNodeMapRange')
            mr.inputs['To Min'].default_value = max(0, rough - noise); mr.inputs['To Max'].default_value = min(1, rough + noise)
            nt.links.new(n.outputs['Fac'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], b.inputs['Roughness'])
        if bump > 0:
            bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump
            nt.links.new(n.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m

def box_mesh(name, sx, sy, sz, bevel=0.0):
    """以底面中心为原点的长方体网格（可共享给多个物体）"""
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, (v.co.z + 0.5) * sz))
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=2, affect='EDGES')
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = bevel > 0
    return me

def obj(name, me, loc=(0, 0, 0), m=None, rot=(0, 0, 0), parent=None, coll=None):
    o = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(o)
    o.location = loc; o.rotation_euler = rot
    if m is not None:
        if len(o.data.materials) == 0: o.data.materials.append(m)
        else: o.data.materials[0] = m
    if parent: o.parent = parent
    return o

def box(name, size, loc, m, bevel=0.0, rot=(0, 0, 0)):
    return obj(name, box_mesh(name, *size, bevel=bevel), loc, m, rot)

def world(color, strength):
    w = bpy.data.worlds.new('W'); bpy.context.scene.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (*color, 1); bg.inputs['Strength'].default_value = strength

def area_light(name, loc, rot, size, energy, color=(1, 1, 1), shape='RECTANGLE', size_y=None):
    L = bpy.data.lights.new(name, 'AREA'); L.energy = energy; L.color = color; L.shape = shape
    L.size = size
    if size_y is not None: L.size_y = size_y
    o = bpy.data.objects.new(name, L); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot
    return o

def camera(lens, sensor=36.0):
    c = bpy.data.cameras.new('Cam'); c.lens = lens; c.sensor_width = sensor; c.sensor_fit = 'HORIZONTAL'
    o = bpy.data.objects.new('Cam', c); bpy.context.scene.collection.objects.link(o)
    bpy.context.scene.camera = o
    return o

def look_at(o, target):
    d = Vector(target) - o.location
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

def smooth(t):   # 0..1 → 0..1，两头缓
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)

def key_cam(cam, frames, pos_fn, tgt_fn, focus_fn=None, lens_fn=None):
    """逐帧打关键帧（相机路径用函数写，方便和 anchors 共用）"""
    for f in range(frames):
        t = f / (frames - 1)
        cam.location = pos_fn(t); look_at(cam, tgt_fn(t))
        cam.keyframe_insert('location', frame=f + 1); cam.keyframe_insert('rotation_euler', frame=f + 1)
        if focus_fn:
            cam.data.dof.focus_distance = focus_fn(t); cam.data.dof.keyframe_insert('focus_distance', frame=f + 1)
        if lens_fn:
            cam.data.lens = lens_fn(t); cam.data.keyframe_insert('lens', frame=f + 1)
    for fc in (cam.animation_data.action.fcurves if hasattr(cam.animation_data.action, 'fcurves') else []):
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'

# ------------------------------------------------------------------ DC：数据中心冷通道（单位 m）
def build_dc():
    sc = reset(); random.seed(7)
    world((0.010, 0.012, 0.016), 1.0)
    M = dict(
        floor=mat('架空地板', (0.20, 0.205, 0.21), rough=0.42, noise=0.08, nscale=3),
        seam=mat('地板缝', (0.05, 0.05, 0.055), rough=0.7),
        perf=mat('通风地板', (0.14, 0.145, 0.15), metal=0.6, rough=0.4),
        rack=mat('机柜钢', (0.018, 0.019, 0.021), metal=0.7, rough=0.42, noise=0.06, nscale=8),
        bezel=mat('服务器面板', (0.045, 0.047, 0.052), metal=0.8, rough=0.36, noise=0.05, nscale=30),
        mesh=mat('进风网孔', (0.006, 0.006, 0.007), metal=0.5, rough=0.6),
        handle=mat('拉手', (0.55, 0.56, 0.58), metal=1.0, rough=0.28),
        drive=mat('硬盘托架', (0.11, 0.115, 0.12), metal=0.6, rough=0.4),
        blank=mat('盲板', (0.012, 0.012, 0.014), rough=0.6),
        led_g=mat('绿灯', (0, 0, 0), emit=(0.25, 1.0, 0.45), estr=18),
        led_b=mat('蓝灯', (0, 0, 0), emit=(0.25, 0.55, 1.0), estr=18),
        led_a=mat('琥珀灯', (0, 0, 0), emit=(1.0, 0.55, 0.12), estr=14),
        ceil=mat('顶棚', (0.03, 0.03, 0.033), rough=0.8),
        tray=mat('线槽', (0.45, 0.46, 0.47), metal=1.0, rough=0.35),
        fiber=mat('黄色光纤槽', (0.85, 0.62, 0.05), rough=0.45, coat=0.3),
        cable=mat('网线束', (0.08, 0.18, 0.40), rough=0.55),
        lamp=mat('灯带', (1, 1, 1), emit=(0.92, 0.95, 1.0), estr=6),
        glass=mat('通道门玻璃', (0.6, 0.65, 0.7), metal=0.0, rough=0.05),
        door=mat('门框', (0.02, 0.02, 0.022), metal=0.8, rough=0.4),
    )
    g = M['glass'].node_tree.nodes['Principled BSDF']; g.inputs['Transmission Weight'].default_value = 0.85; g.inputs['IOR'].default_value = 1.5
    AISLE = 1.8            # 冷通道宽（两排机柜前门之间）
    W, D, H = 0.6, 1.2, 2.2
    N = 14                 # 每排机柜数
    # 地板：0.6 m 方砖，冷通道里是通风砖
    box('地面', (12, 30, 0.02), (0, 6, -0.02), M['seam'])
    tile = box_mesh('砖', 0.592, 0.592, 0.02, bevel=0.002)
    for ix in range(-6, 7):
        for iy in range(-4, 26):
            x, y = ix * 0.6, iy * 0.6
            perf = abs(x) < AISLE / 2 - 0.1 and iy % 2 == 0
            obj('砖', tile, (x, y, 0), M['perf'] if perf else M['floor'])
    # 服务器前面板（8U GPU 服务器，示意）：深色面板 + 大面积进风网孔 + 两侧拉手 + 一排硬盘托架 + 状态灯
    U = 0.04445
    def server(parent_loc, z, face):          # face = +1 朝 +x（左排），-1 朝 -x（右排）
        x0, y0 = parent_loc
        fx = x0 + face * (D / 2 + 0.01)
        h = 8 * U - 0.004
        rot = (0, 0, 0)
        box('面板', (0.02, W - 0.05, h), (fx, y0, z), M['bezel'], bevel=0.002)
        # 进风网孔（三块）
        for k, (yy, ww) in enumerate(((-0.17, 0.16), (0.0, 0.16), (0.17, 0.16))):
            box('网孔', (0.004, ww, h * 0.55), (fx + face * 0.011, y0 + yy, z + h * 0.38), M['mesh'])
        # 硬盘托架一排
        for k in range(8):
            box('托架', (0.006, 0.058, 0.07), (fx + face * 0.012, y0 - 0.21 + k * 0.06, z + h * 0.08), M['drive'], bevel=0.001)
        # 拉手
        for s in (-1, 1):
            box('拉手', (0.03, 0.012, h * 0.7), (fx + face * 0.02, y0 + s * (W / 2 - 0.045), z + h * 0.15), M['handle'], bevel=0.003)
        # 状态灯
        r = random.random()
        led = M['led_b'] if r < 0.5 else M['led_g']
        box('灯', (0.004, 0.006, 0.006), (fx + face * 0.013, y0 + 0.24, z + h * 0.92), led)
        if random.random() < 0.08:
            box('灯', (0.004, 0.006, 0.006), (fx + face * 0.013, y0 + 0.225, z + h * 0.92), M['led_a'])
    def switch(x0, y0, z, face):
        fx = x0 + face * (D / 2 + 0.01)
        box('交换机', (0.02, W - 0.05, U - 0.003), (fx, y0, z), M['bezel'])
        for k in range(16):
            box('口', (0.004, 0.022, 0.016), (fx + face * 0.011, y0 - 0.23 + k * 0.03, z + 0.012), M['mesh'])
            if random.random() < 0.7:
                box('口灯', (0.003, 0.004, 0.003), (fx + face * 0.013, y0 - 0.23 + k * 0.03, z + 0.034), M['led_g'])
    for side in (-1, 1):                   # -1 左排（x<0，前门朝 +x），+1 右排
        xc = side * (AISLE / 2 + D / 2)
        face = -side
        for i in range(N):
            yc = i * (W + 0.002) + W / 2
            # 机柜框
            box('机柜', (D, W, H), (xc, yc, 0), M['rack'], bevel=0.004)
            # 柜内设备：顶部交换机 + 4 台 8U 服务器 + 盲板
            z = 0.12
            for k in range(4):
                server((xc, yc), z, face); z += 8 * U
            for k in range(3):
                box('盲板', (0.01, W - 0.05, U - 0.002), (xc + face * (D / 2 + 0.008), yc, z), M['blank']); z += U
            switch(xc, yc, z, face); z += U
            switch(xc, yc, z, face)
            # 机柜立柱（前门两侧）
            for s in (-1, 1):
                box('立柱', (0.03, 0.025, H), (xc + face * (D / 2 + 0.018), yc + s * (W / 2 - 0.012), 0), M['rack'])
    # 顶部：线槽（网格桥架）沿通道两侧，黄色光纤槽居中，横向灯带
    for side in (-1, 1):
        x = side * (AISLE / 2 + D / 2)
        box('桥架', (0.4, 30, 0.08), (x, 6, H + 0.35), M['tray'])
        for k in range(60):
            box('线', (0.3, 0.6, 0.05), (x, k * 0.5 - 8, H + 0.43), M['cable'] if k % 3 else M['fiber'])
    for side in (-1, 1):
        box('光纤槽', (0.16, 30, 0.10), (side * (AISLE / 2 + 0.25), 6, H + 0.62), M['fiber'], bevel=0.01)
    for k in range(-4, 26, 2):
        box('灯带', (2.6, 0.08, 0.03), (0, k * 0.9, 3.15), M['lamp'])
    box('顶棚', (12, 30, 0.05), (0, 6, 3.2), M['ceil'])
    # 通道尽头：封闭通道门（玻璃）
    yend = N * (W + 0.002) + 0.05
    box('门框', (AISLE + 0.1, 0.06, H + 0.1), (0, yend, 0), M['door'])
    box('门玻璃', (AISLE - 0.1, 0.02, H - 0.1), (0, yend, 0.05), M['glass'])
    area_light('门外', (0, yend + 2.0, 1.5), (rad(-90), 0, 0), 2.0, 300, (0.75, 0.85, 1.0))
    # 灯：顶部灯带本身发光 + 几盏面光补亮机柜前面
    for k in range(0, N, 3):
        y = k * (W + 0.002) + 0.3
        area_light(f'顶光{k}', (0, y, 3.0), (0, 0, 0), 1.4, 70, (0.92, 0.95, 1.0), 'RECTANGLE', 0.6)
    cam = camera(28)
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.8
    # 相机：站在通道口，眼高 1.45 m，沿通道慢慢推进约 2.4 m，稍微往右偏看机柜面板
    def pos(t): s = smooth(t) * 0.75 + t * 0.25; return Vector((-0.18 + 0.05 * s, -1.6 + 2.4 * s, 1.45 - 0.08 * s))
    def tgt(t): s = smooth(t); return Vector((0.35 + 0.25 * s, 6.5 + 1.0 * s, 1.05))
    key_cam(cam, SHOTS['DC'], pos, tgt, focus_fn=lambda t: 3.2 + 0.4 * t)
    sc.cycles.max_bounces = 6
    return sc, {}

# ------------------------------------------------------------------ 加速器模组（单位 mm，场景里 1 = 1 mm）
DIE = (26.0, 31.0)          # 大芯片约 800 mm²（示意，FACTS）
HBM = (11.0, 10.0)          # HBM 堆叠（示意）
INTP = (50.0, 36.0)         # 硅中介层（示意，包住芯片和 6 颗 HBM）
SUBS = (62.0, 54.0)         # 有机基板
Z_SUB, Z_INTP = 1.6, 0.6    # 基板厚、中介层（含凸点）厚
PCB_T = 1.8

def hbm_centers():
    xs = (-(DIE[0] / 2 + 0.8 + HBM[0] / 2), DIE[0] / 2 + 0.8 + HBM[0] / 2)
    ys = (-HBM[1] - 0.6, 0.0, HBM[1] + 0.6)
    return [(x, y) for x in xs for y in ys]

def build_module(sc, detail=True, env=True):
    random.seed(3)
    M = dict(
        pcb=mat('模组电路板阻焊', (0.010, 0.035, 0.026), rough=0.35, coat=0.6, noise=0.05, nscale=0.8),
        gold=mat('镀金焊盘', (0.95, 0.70, 0.32), metal=1.0, rough=0.25),
        subs=mat('有机基板', (0.035, 0.045, 0.030), rough=0.45, coat=0.4, noise=0.06, nscale=1.0),
        intp=mat('硅中介层', (0.30, 0.31, 0.34), metal=0.9, rough=0.2),
        die=mat('芯片硅背面', (0.40, 0.41, 0.45), metal=0.75, rough=0.30, noise=0.05, nscale=0.6),
        hbm=mat('HBM 顶面', (0.30, 0.31, 0.34), metal=0.7, rough=0.34, noise=0.05, nscale=0.9),
        mold=mat('填充胶', (0.015, 0.015, 0.017), rough=0.55),
        mlcc=mat('电容', (0.52, 0.40, 0.27), rough=0.5),
        term=mat('焊端', (0.82, 0.82, 0.80), metal=1.0, rough=0.35),
        ind=mat('电感', (0.035, 0.035, 0.038), rough=0.55, bump=0.1, nscale=2),
        vrm=mat('功率级', (0.03, 0.03, 0.033), rough=0.4),
        steel=mat('加强框', (0.62, 0.63, 0.65), metal=1.0, rough=0.32, noise=0.08, nscale=0.3),
        silk=mat('丝印', (0.85, 0.86, 0.84), rough=0.6),
        hole=mat('螺孔', (0.75, 0.62, 0.30), metal=1.0, rough=0.3),
    )
    # 模组电路板（示意尺寸）
    box('模组板', (150, 92, PCB_T), (0, 0, -PCB_T), M['pcb'], bevel=0.4)
    # 基板 + 中介层 + 芯片 + HBM
    box('基板', (SUBS[0], SUBS[1], Z_SUB), (0, 0, 0), M['subs'], bevel=0.15)
    z1 = Z_SUB
    box('中介层', (INTP[0], INTP[1], Z_INTP), (0, 0, z1), M['intp'], bevel=0.05)
    z2 = z1 + Z_INTP
    box('填充', (INTP[0] - 0.3, INTP[1] - 0.3, 0.70), (0, 0, z2), M['mold'], bevel=0.05)
    die = box('大芯片', (DIE[0], DIE[1], 0.78), (0, 0, z2), M['die'], bevel=0.04)
    for i, (x, y) in enumerate(hbm_centers()):
        box(f'HBM{i}', (HBM[0], HBM[1], 0.74), (x, y, z2), M['hbm'], bevel=0.04)
    # 基板四周：去耦电容（成排的小电容）
    cap = box_mesh('电容体', 1.0, 0.5, 0.5, bevel=0.04); term = box_mesh('焊端', 0.22, 0.52, 0.52, bevel=0.03)
    def capacitor(x, y, z, rot):
        o = obj('C', cap, (x, y, z), M['mlcc'], (0, 0, rot))
        for s in (-1, 1):
            t = obj('T', term, (s * 0.45, 0, -0.01), M['term']); t.parent = o
    for k in range(40):
        for edge in range(4):
            if edge < 2:
                x = -SUBS[0] / 2 + 3 + k * (SUBS[0] - 6) / 39; y = (1 if edge else -1) * (INTP[1] / 2 + 3.5)
                if k % 5 != 4: capacitor(x, y, Z_SUB, rad(90))
            else:
                y = -SUBS[1] / 2 + 3 + k * (SUBS[1] - 6) / 39; x = (1 if edge == 3 else -1) * (INTP[0] / 2 + 3.5)
                if k % 5 != 4 and abs(y) < SUBS[1] / 2 - 2: capacitor(x, y, Z_SUB, 0)
    # 加强框（基板上的金属框，示意）
    for s in (-1, 1):
        box('框', (SUBS[0] - 2, 2.2, 1.2), (0, s * (SUBS[1] / 2 - 1.6), Z_SUB), M['steel'], bevel=0.15)
        box('框', (2.2, SUBS[1] - 6, 1.2), (s * (SUBS[0] / 2 - 1.6), 0, Z_SUB), M['steel'], bevel=0.15)
    # 环境：机箱底板（拉丝铝）、旁边一块模组的散热鳍片（虚在背景里），不让模组孤零零悬在黑色里
    if env:
        chassis = mat('机箱底板', (0.10, 0.105, 0.11), metal=1.0, rough=0.45, noise=0.1, nscale=0.05)
        box('机箱底', (900, 900, 1), (0, 0, -PCB_T - 9), chassis)
        fin = mat('邻近散热鳍片', (0.45, 0.46, 0.48), metal=1.0, rough=0.35)
        finm = box_mesh('鳍片', 120, 0.35, 30)
        for k in range(70):
            obj('鳍', finm, (0, 120 + k * 3.0, -PCB_T - 8), fin)
        for k in range(70):
            obj('鳍', finm, (175, -40 + k * 2.2, -PCB_T - 8), fin)
    if detail:
        # 模组板上：供电（电感 + 功率级）排成两排、螺孔、金色焊盘
        indm = box_mesh('电感', 6.5, 6.5, 4.5, bevel=0.15); vrm = box_mesh('功率级', 5, 4, 1.0, bevel=0.15)
        for row in (-1, 1):
            for k in range(11):
                x = -60 + k * 10.0
                if abs(x) < SUBS[0] / 2 + 6 and row == 0: continue
                obj('L', indm, (x, row * 40.5, 0), M['ind'])
                obj('Q', vrm, (x, row * 33.0, 0), M['vrm'])
        for s in (-1, 1):
            for k in range(14):
                obj('L', indm, (s * 66, -36 + k * 5.6 if False else -32 + k * 4.9, 0), M['ind']) if k % 2 == 0 else None
        hole = box_mesh('孔', 5.5, 5.5, 0.08, bevel=1.2)
        for x in (-70, 70):
            for y in (-41, 41):
                obj('孔', hole, (x, y, 0), M['hole'])
        for k in range(30):
            box('焊盘', (1.2, 0.6, 0.03), (-72 + k * 0.0 + 0, -20 + k * 1.4, 0), M['gold'])
        # 小电容散在板上
        for k in range(160):
            x = random.uniform(-72, 72); y = random.uniform(-44, 44)
            if abs(x) < SUBS[0] / 2 + 2 and abs(y) < SUBS[1] / 2 + 2: continue
            capacitor(x, y, 0, random.choice((0, rad(90))))
    return die, z2 + 0.78

def build_macro():
    sc = reset()
    world((0.020, 0.023, 0.028), 1.0)
    die, ztop = build_module(sc)
    # 布光：左上方大柔光（主光）、右后方窄条（勾边）、正面很弱的补光
    area_light('主光', (-120, -60, 160), (rad(35), rad(-30), 0), 120, 6.0e5, (1.0, 0.96, 0.9))
    area_light('勾边', (110, 120, 60), (rad(-60), rad(40), 0), 160, 3.0e5, (0.75, 0.85, 1.0), 'RECTANGLE', 20)
    area_light('补光', (0, -200, 40), (rad(80), 0, 0), 200, 4.0e4, (0.9, 0.92, 1.0))
    cam = camera(50)
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 4.0
    cam.data.clip_start = 1.0; cam.data.clip_end = 2000
    # 相机：低角度从板子前缘滑向封装，最后停在大芯片边缘
    def pos(t): s = smooth(t) * 0.8 + t * 0.2; return Vector((-30 + 14 * s, -128 + 58 * s, 78 - 30 * s))
    def tgt(t): s = smooth(t); return Vector((-4 + 2 * s, -10 + 6 * s, 2.0))
    def foc(t): return (pos(t) - Vector((-DIE[0] / 4, -DIE[1] / 2, ztop))).length
    key_cam(cam, SHOTS['MACRO'], pos, tgt, focus_fn=foc)
    return sc, {}

def build_chip():
    sc = reset()
    world((0.020, 0.023, 0.028), 1.0)
    die, ztop = build_module(sc)
    area_light('主光', (-90, -70, 220), (rad(20), rad(-22), 0), 160, 7.0e5, (1.0, 0.96, 0.9))
    area_light('勾边', (120, 110, 70), (rad(-60), rad(40), 0), 160, 3.0e5, (0.75, 0.85, 1.0), 'RECTANGLE', 20)
    area_light('顶补', (0, 0, 260), (0, 0, 0), 120, 1.2e5, (0.95, 0.97, 1.0))
    cam = camera(85)
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 5.6
    cam.data.clip_start = 1.0; cam.data.clip_end = 3000
    # 起点：正上方俯视，芯片长边竖着（31 mm 方向对屏幕竖向），芯片宽度约占画面 72%
    # 9:16 画面、85 mm 镜头、36 mm 传感器宽：水平视场 = 2·atan(18/85)；距离 d 使 26 mm / (2 d tan) = 0.72
    hfov = 2 * math.atan(18 / 85); d0 = DIE[0] / (0.72 * 2 * math.tan(hfov / 2))
    def pos(t):
        s = smooth(min(1, max(0, (t - 0.12) / 0.88)))       # 前 12% 静止俯视（叠加层对齐）
        el = rad(90 - 50 * s); dist = d0 * (1 + 1.55 * s); az = rad(-90 + 25 * s)
        return Vector((dist * math.cos(el) * math.cos(az), dist * math.cos(el) * math.sin(az), ztop + dist * math.sin(el)))
    def tgt(t):
        s = smooth(min(1, max(0, (t - 0.12) / 0.88))); return Vector((0, 0, ztop - 0.6 * s))
    key_cam(cam, SHOTS['CHIP'], pos, tgt, focus_fn=lambda t: (pos(t) - tgt(t)).length)
    # 俯视时 look_at 的「上」方向不稳定：起点固定成芯片长边竖直（屏幕上方 = +y）
    return sc, dict(ztop=ztop)


# ------------------------------------------------------------------ G 段：一块 GPU → 模组 → 服务器里的 8 块（单位 mm）
# 第 0 块模组在原点，相机起点和 CHIP 镜头的终点一样（接得上）；拿掉了散热器（示意，画面上注明）
MOD_PITCH = (160.0, 102.0)
def module_offsets():
    return [(c * MOD_PITCH[0], r * MOD_PITCH[1]) for r in range(4) for c in range(2)]

def build_server():
    sc = reset()
    world((0.020, 0.023, 0.028), 1.0)
    die, ztop = None, None
    for i, (ox, oy) in enumerate(module_offsets()):
        before = set(bpy.data.objects)
        d, zt = build_module(sc, detail=(i < 2), env=False)
        if i == 0: die, ztop = d, zt
        for o in set(bpy.data.objects) - before:
            if o.parent is None: o.location.x += ox; o.location.y += oy
    steel = mat('机箱钢板', (0.30, 0.31, 0.33), metal=1.0, rough=0.42, noise=0.08, nscale=0.02)
    pcb = mat('底板阻焊', (0.012, 0.04, 0.03), rough=0.38, coat=0.5)
    fanm = mat('风扇', (0.03, 0.03, 0.035), rough=0.5)
    psu = mat('电源', (0.12, 0.125, 0.13), metal=0.8, rough=0.4)
    cx, cy = MOD_PITCH[0] / 2, MOD_PITCH[1] * 1.5
    W, Dp, H = 440, 760, 340                      # 8U 机箱内腔（示意）
    box('底板', (380, 460, 1.6), (cx, cy, -PCB_T - 6), pcb)
    box('机箱底', (W, Dp, 2), (cx, cy + 120, -PCB_T - 12), steel)
    for s_ in (-1, 1):
        box('侧板', (2, Dp, H), (cx + s_ * W / 2, cy + 120, -PCB_T - 12), steel)
    box('前风扇墙', (W, 8, H * 0.8), (cx, cy - 290, -PCB_T - 12), steel)
    for k in range(5):
        for j in range(2):
            f_ = bpy.data.meshes.new('fan'); bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=36, radius2=36, depth=10); bm.to_mesh(f_); bm.free()
            o = obj('风扇', f_, (cx - 170 + k * 85, cy - 296, -PCB_T + 50 + j * 120), fanm, (rad(90), 0, 0))
    for k in range(4):
        box('电源', (95, 200, 80), (cx - 150 + k * 100, cy + 420, -PCB_T - 10), psu, bevel=2)
    area_light('主光', (-300, -500, 900), (rad(35), rad(-18), 0), 900, 3.0e7, (1.0, 0.96, 0.9))
    area_light('勾边', (600, 900, 400), (rad(-60), rad(40), 0), 700, 1.2e7, (0.75, 0.85, 1.0))
    area_light('近主光', (-90, -70, 220), (rad(20), rad(-22), 0), 160, 7.0e5, (1.0, 0.96, 0.9))
    cam = camera(85)
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 8.0
    cam.data.clip_start = 1.0; cam.data.clip_end = 6000
    hfov = 2 * math.atan(18 / 85); d0 = DIE[0] / (0.72 * 2 * math.tan(hfov / 2))
    def pose(t):
        s = smooth(t)
        dist = d0 * 2.55 * math.exp(math.log(1500 / (d0 * 2.55)) * s)     # 对数匀速拉远
        el = rad(40 + 18 * s); az = rad(115 - 15 * s)        # 从机箱后侧看过去，前面的风扇墙在背景里
        tg = Vector((lerp_(0, cx, s), lerp_(0, cy + 60, s), lerp_(ztop - 0.6, 0, s)))
        return tg + Vector((dist * math.cos(el) * math.cos(az), dist * math.cos(el) * math.sin(az), dist * math.sin(el))), tg
    key_cam(cam, SHOTS['SERVER'], lambda t: pose(t)[0], lambda t: pose(t)[1], focus_fn=lambda t: (pose(t)[0] - pose(t)[1]).length)
    return sc, dict(ztop=ztop)

def lerp_(a, b, t): return a + (b - a) * t

# ------------------------------------------------------------------ H 段：一台服务器 → 机柜 → 一排排机柜（单位 m，复用 DC 场景）
RACK_W, RACK_D, AISLE = 0.6, 1.2, 1.8
def build_rack():
    sc, _ = build_dc()
    cam = sc.camera
    cam.animation_data_clear(); cam.data.animation_data_clear()
    cam.data.lens = 24
    s_y = 6 * (RACK_W + 0.002) + RACK_W / 2
    face_x = -(AISLE / 2) - 0.01
    srv_z = 0.12 + 1.5 * 8 * 0.04445
    def pose(t):
        s = smooth(t)
        p0 = Vector((face_x + 0.62, s_y - 0.25, srv_z + 0.05)); t0 = Vector((face_x, s_y, srv_z))
        p1 = Vector((0.55, -2.4, 2.55)); t1 = Vector((-0.1, 6.0, 1.05))
        k = 1 - (1 - s) ** 2.2
        return p0.lerp(p1, k), t0.lerp(t1, s)
    key_cam(cam, SHOTS['RACK'], lambda t: pose(t)[0], lambda t: pose(t)[1], focus_fn=lambda t: 0.6 + 4.0 * smooth(t))
    return sc, dict(rack_top=[((-1 if side < 0 else 1) * (AISLE / 2 + RACK_D / 2) + (1 if side < 0 else -1) * (RACK_D / 2 + 0.02),
                               i * (RACK_W + 0.002) + RACK_W / 2, 1.68) for side in (-1, 1) for i in range(14)],
                    servers=[((-(AISLE / 2) - 0.02), i * (RACK_W + 0.002) + RACK_W / 2, 0.12 + (k + 0.5) * 8 * 0.04445) for i in range(14) for k in range(4)])

BUILD = dict(DC=build_dc, MACRO=build_macro, CHIP=build_chip, SERVER=build_server, RACK=build_rack)

def setup_render(sc, w, h, samples, device):
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'
    if device in ('gpu', 'cuda'):        # cuda：有的 RunPod 机器 OptiX 内核编译失败（OPTIX_ERROR_INTERNAL_COMPILER_ERROR），改走 CUDA
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for dev_type in (('CUDA',) if device == 'cuda' else ('OPTIX', 'CUDA')):
            try:
                prefs.compute_device_type = dev_type; prefs.get_devices()
                if any(d.type == dev_type for d in prefs.devices): break
            except Exception: pass
        for d in prefs.devices: d.use = d.type != 'CPU'
        if not any(d.use for d in prefs.devices): raise SystemExit('要求 GPU 但没找到显卡')
        sc.cycles.device = 'GPU'
        print('GPU:', [d.name for d in prefs.devices if d.use])

def project(sc, cam, p):
    from bpy_extras.object_utils import world_to_camera_view
    v = world_to_camera_view(sc, cam, Vector(p)); return [round(v.x, 5), round(1 - v.y, 5), round(v.z, 4)]

def main():
    a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    mode, shot = a[0], a[1]
    sc, info = BUILD[shot]()
    sc.frame_start, sc.frame_end = 1, SHOTS[shot]
    if mode == 'still':
        t, out = float(a[2]), a[3]
        w, h = map(int, (a[4] if len(a) > 4 else '270x480').split('x')); smp = int(a[5]) if len(a) > 5 else 16
        setup_render(sc, w, h, smp, 'cpu'); sc.frame_set(1 + round(t * FPS))
        sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    elif mode == 'anim':
        out, f0, f1 = a[2], int(a[3]), int(a[4])
        w, h = map(int, (a[5] if len(a) > 5 else '1080x1920').split('x')); smp = int(a[6]) if len(a) > 6 else 64
        setup_render(sc, w, h, smp, a[7] if len(a) > 7 else 'gpu')
        os.makedirs(out, exist_ok=True)
        step = int(os.environ.get('STEP', '1'))          # 隔帧渲（本机 CPU），之后用插帧补到 30 fps
        for f in range(f0, f1 + 1, step):
            p = os.path.join(out, f'{shot}_{f:04d}.png')
            if os.path.exists(p): continue
            sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True)
    elif mode == 'anchors':
        out = a[2]; w, h = map(int, (a[3] if len(a) > 3 else '1080x1920').split('x'))
        sc.render.resolution_x, sc.render.resolution_y = w, h
        cam = sc.camera; frames = []
        zt = info.get('ztop', 3.0)
        corners = [(-DIE[0] / 2, DIE[1] / 2, zt), (DIE[0] / 2, DIE[1] / 2, zt), (DIE[0] / 2, -DIE[1] / 2, zt), (-DIE[0] / 2, -DIE[1] / 2, zt)]
        if shot in ('SERVER', 'RACK'):
            for f in range(1, SHOTS[shot] + 1):
                sc.frame_set(f)
                if shot == 'SERVER':
                    frames.append(dict(die=[project(sc, cam, c) for c in corners],
                                       mods=[project(sc, cam, (ox, oy, zt)) for ox, oy in module_offsets()]))
                else:
                    frames.append(dict(tops=[project(sc, cam, p) for p in info['rack_top']], servers=[project(sc, cam, p) for p in info['servers']]))
            json.dump(dict(shot=shot, fps=FPS, w=w, h=h, frames=frames), open(out, 'w')); return
        for f in range(1, SHOTS[shot] + 1):
            sc.frame_set(f)
            frames.append(dict(die=[project(sc, cam, c) for c in corners],
                               hbm=[project(sc, cam, (x, y, zt - 0.04)) for x, y in hbm_centers()],
                               hbmq=[[project(sc, cam, (x + sx * HBM[0] / 2, y + sy * HBM[1] / 2, zt - 0.04)) for sx, sy in ((-1, 1), (1, 1), (1, -1), (-1, -1))]
                                     for x, y in hbm_centers()]))
        json.dump(dict(shot=shot, fps=FPS, w=w, h=h, frames=frames), open(out, 'w'))
    elif mode == 'save':
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a[2]))

main()
