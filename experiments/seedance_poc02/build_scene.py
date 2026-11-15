"""Seedance PoC 02 — 动态摄影机 + 独立物体运动 Blockout（6 秒，180 帧，30 fps，竖屏 720×1280）。

摄影机绕固定的模块笼子做约 60° 的弧线运动（同时下降、靠近），光模块沿笼子轴线独立直线插入。
沿用 PoC 01 的代理几何体和 Workbench 灰盒风格。

和 PoC 01 的一处科学修正：笼子装在网卡板边，入口和金属挡板（PCIe bracket）平齐，
模块从挡板外侧插入，插好后光纤接口朝外。PCB 只在挡板里侧。

用法（在本目录运行）：
  blender -b --factory-startup --python-exit-code 1 --python build_scene.py -- check          # 只算投影，检查构图和视差，不渲染
  blender -b --factory-startup --python-exit-code 1 --python build_scene.py -- stills 1,46,91,136,180 [--half]
  blender -b --factory-startup --python-exit-code 1 --python build_scene.py -- anim [--half]

单位 1 BU ≈ 1 cm，只取大致比例。+Y 指向机箱外，模块沿 -Y 插入；+Z 向上；PCB 上表面 z = 0。
"""
import math
import os
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
F_START, F_END = 1, 180
RES_X, RES_Y = 720, 1280


def t_of(frame):
    return (frame - 1) / FPS


def lerp(a, b, k):
    return a + (b - a) * k


def smoothstep(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ---------- 几何（和 PoC 01 相同的笼子和模块） ----------
CAGE_W, CAGE_H, CAGE_L, WALL = 2.10, 1.10, 6.00, 0.08
MOD_W, MOD_H, MOD_L = 1.85, 0.86, 7.20
MOD_Z = WALL + 0.01 + MOD_H / 2
CAGE_B_X = -2.90                          # 相邻的第二个空笼子（双口网卡），只作参照
PLATE_Y0, PLATE_Y1 = -0.10, 0.0           # 挡板厚 0.1，外表面在 y = 0，和笼子入口平齐
PLATE_X0, PLATE_X1, PLATE_Z0, PLATE_Z1 = -6.5, 4.5, -4.5, 1.55   # 向下延伸当机箱后壁；向上做低（示意），好越过它看到笼子和 PCB
MOD_BACK_Y0, MOD_BACK_Y1 = 1.30, -5.80    # 起点：后端面在挡板外 1.3；终点：前端面外露 1.4
F_INS0, F_INS1 = 46, 136                  # 1.5 s 开始插入，4.5 s 到位停止

# ---------- 摄影机 ----------
LENS = 26.0
# 相机 = 注视点 T + 距离 D × 方向(方位角 AZ, 仰角 EL)。AZ 从 +Y（机箱外正前方）向 +X 量：
# +X 一侧在「站在机箱外面对挡板」时的左手边。
AZ0, AZ1 = 54.0, -18.0                    # 相对注视点 72°；相对固定的笼子入口约 60°（见 camera_motion.md）
EL0, EL1 = 31.0, 16.0                     # 高机位 → 低机位
D0, D1 = 19.0, 8.6
T0 = Vector((0.0, 4.3, 0.45))             # 起点注视点（y 实际由模块前端位置决定）
T1 = Vector((0.0, 0.75, 0.55))            # 终点注视点：模块外露段中点，同时带到挡板和笼子入口


def cam_progress():
    """镜头进度 0→1。速度：起步就有约 45% 的速度，0.9 s 内升到满速，4.5 s 后余弦减速到约 15%。"""
    n = F_END - F_START + 1
    v = []
    for i in range(n):
        t = i / FPS
        if t < 0.9:
            vel = 0.45 + 0.55 * smoothstep(t / 0.9)
        elif t < 4.5:
            vel = 1.0
        else:
            u = (t - 4.5) / (5.967 - 4.5)
            vel = 0.15 + 0.85 * (0.5 + 0.5 * math.cos(math.pi * min(u, 1.0)))
        v.append(vel)
    s = [0.0]
    for i in range(1, n):
        s.append(s[-1] + 0.5 * (v[i - 1] + v[i]))
    return [x / s[-1] for x in s]


PROG = cam_progress()


def cam_at(frame):
    p = PROG[frame - F_START]
    az = math.radians(lerp(AZ0, AZ1, p))
    el = math.radians(lerp(EL0, EL1, p))
    d = lerp(D0, D1, p)
    # 注视点 y 跟随「笼子入口（y = 0）和模块前端」的中点，x、z 随镜头进度过渡。
    front = module_back_y(frame) + MOD_L
    T = Vector((lerp(T0.x, T1.x, p), 0.5 * front + 0.05, lerp(T0.z, T1.z, p)))
    P = T + d * Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    return P, T


def insert_progress(frame):
    """模块插入进度 0→1。梯形速度：约 0.35 s 加速、匀速、最后约 0.9 s 减速到 0（停稳不反弹）。"""
    a, d = 0.35, 0.9
    T = (F_INS1 - F_INS0) / FPS

    def vel(t):
        if t <= 0 or t >= T:
            return 0.0
        if t < a:
            return 0.5 - 0.5 * math.cos(math.pi * t / a)
        if t > T - d:
            return 0.5 + 0.5 * math.cos(math.pi * (t - (T - d)) / d)
        return 1.0

    def integ(t, n=400):
        if t <= 0:
            return 0.0
        h = t / n
        return sum(vel((i + 0.5) * h) for i in range(n)) * h

    t = min(max((frame - F_INS0) / FPS, 0.0), T)
    return integ(t) / integ(T)


def module_back_y(frame):
    return lerp(MOD_BACK_Y0, MOD_BACK_Y1, insert_progress(frame))


# ---------- 场景 ----------
def mat(name, rgb):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*rgb, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.9
    return m


def box(name, size, loc, material, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    o.color = material.diffuse_color
    if parent:
        o.parent = parent
    return o


def box_span(name, x0, x1, y0, y1, z0, z1, material, parent=None):
    return box(name, (x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), material, parent)


def cage(name, x, material):
    root = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(root)
    yc = -CAGE_L / 2
    box(f'{name}_floor', (CAGE_W, CAGE_L, WALL), (x, yc, WALL / 2), material, root)
    box(f'{name}_top', (CAGE_W, CAGE_L, WALL), (x, yc, CAGE_H - WALL / 2), material, root)
    box(f'{name}_left', (WALL, CAGE_L, CAGE_H), (x - CAGE_W / 2 + WALL / 2, yc, CAGE_H / 2), material, root)
    box(f'{name}_right', (WALL, CAGE_L, CAGE_H), (x + CAGE_W / 2 - WALL / 2, yc, CAGE_H / 2), material, root)
    box(f'{name}_back', (CAGE_W, WALL, CAGE_H), (x, -CAGE_L + WALL / 2, CAGE_H / 2), material, root)
    return root


def build(half=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = F_START, F_END
    sc.render.fps = FPS
    sc.render.resolution_x, sc.render.resolution_y = RES_X, RES_Y
    sc.render.resolution_percentage = 50 if half else 100

    m_pcb = mat('PCB_darkgreen', (0.035, 0.11, 0.06))
    m_cage = mat('Cage_midgray', (0.42, 0.42, 0.43))
    m_mod = mat('Module_blue', (0.08, 0.28, 0.85))
    m_plate = mat('Bracket_darksteel', (0.24, 0.26, 0.30))
    m_heat = mat('Heatsink_charcoal', (0.15, 0.15, 0.17))
    m_chip = mat('Chip_black', (0.06, 0.06, 0.07))
    m_cap = mat('Part_ochre', (0.42, 0.30, 0.12))

    # A — PCB：只在挡板里侧（y ≤ 0），板边和挡板贴齐。
    box_span('A_PCB', -7.0, 7.0, -20.0, 0.0, -0.16, 0.0, m_pcb)

    # B — 两个笼子：A 口（目标）在 x = 0，B 口（相邻、空）在 x = -2.9。入口在 y = 0。
    cage('B_Cage_target', 0.0, m_cage)
    cage('B_Cage_neighbor', CAGE_B_X, m_cage)

    # E — 环境体块：金属挡板（开两个口让笼子入口露出来）、芯片散热器、两颗芯片、一排元件。
    plate = bpy.data.objects.new('E_Bracket', None)
    sc.collection.objects.link(plate)
    gap = 0.02
    xa0, xa1 = -CAGE_W / 2 - gap, CAGE_W / 2 + gap
    xb0, xb1 = CAGE_B_X - CAGE_W / 2 - gap, CAGE_B_X + CAGE_W / 2 + gap
    zt = CAGE_H + gap
    box_span('E_Bracket_bottom', PLATE_X0, PLATE_X1, PLATE_Y0, PLATE_Y1, PLATE_Z0, 0.0, m_plate, plate)
    box_span('E_Bracket_top', PLATE_X0, PLATE_X1, PLATE_Y0, PLATE_Y1, zt, PLATE_Z1, m_plate, plate)
    box_span('E_Bracket_left', PLATE_X0, xb0, PLATE_Y0, PLATE_Y1, 0.0, zt, m_plate, plate)
    box_span('E_Bracket_mid', xb1, xa0, PLATE_Y0, PLATE_Y1, 0.0, zt, m_plate, plate)
    box_span('E_Bracket_right', xa1, PLATE_X1, PLATE_Y0, PLATE_Y1, 0.0, zt, m_plate, plate)
    box_span('E_Heatsink', -2.2, 2.6, -14.0, -9.4, 0.0, 2.4, m_heat)
    box_span('E_Chip_1', 3.0, 4.6, -6.0, -4.6, 0.0, 0.35, m_chip)
    box_span('E_Chip_2', -5.6, -3.9, -8.4, -6.9, 0.0, 0.30, m_chip)
    for i in range(4):
        box_span(f'E_Part_{i}', 2.2 + i * 0.75, 2.7 + i * 0.75, -8.6, -8.0, 0.0, 0.7, m_cap)

    # C — 光模块：原点在后端面中心，动画只改 location.y。
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    mod = bpy.context.active_object
    mod.name = 'C_Module'
    mod.scale = (MOD_W, MOD_L, MOD_H)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for v in mod.data.vertices:
        v.co.y += MOD_L / 2
    mod.data.materials.append(m_mod)
    mod.color = m_mod.diffuse_color
    for f in range(F_START, F_END + 1):
        mod.location = (0.0, module_back_y(f), MOD_Z)
        mod.keyframe_insert('location', frame=f)

    # D — 背景：只用近黑的世界背景（竖直背景板被侧光照亮时会像一根柱子，去掉）。
    world = bpy.data.worlds.new('World')
    world.color = (0.02, 0.021, 0.025)
    sc.world = world

    # 摄影机：注视空物体，位置和注视点逐帧烘焙。
    target = bpy.data.objects.new('CAM_Target', None)
    sc.collection.objects.link(target)
    cam_data = bpy.data.cameras.new('CAM')
    cam_data.lens = LENS
    cam_data.sensor_fit = 'VERTICAL'
    cam_data.clip_start, cam_data.clip_end = 0.1, 500
    cam_data.dof.use_dof = False
    cam = bpy.data.objects.new('CAM', cam_data)
    sc.collection.objects.link(cam)
    sc.camera = cam
    trk = cam.constraints.new('TRACK_TO')
    trk.target = target
    trk.track_axis, trk.up_axis = 'TRACK_NEGATIVE_Z', 'UP_Y'
    for f in range(F_START, F_END + 1):
        P, T = cam_at(f)
        cam.location = P
        target.location = T
        cam.keyframe_insert('location', frame=f)
        target.keyframe_insert('location', frame=f)

    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading
    sh.light = 'STUDIO'
    sh.color_type = 'OBJECT'
    sh.show_object_outline = True
    sh.object_outline_color = (0.0, 0.0, 0.0)
    sh.show_cavity = True
    sh.cavity_type = 'WORLD'
    sh.show_shadows = True
    sh.shadow_intensity = 0.35
    sh.background_type = 'WORLD'
    sc.display.render_aa = '5' if half else '8'
    sc.render.use_motion_blur = False
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.file_format = 'PNG'
    return sc


# ---------- 不渲染的构图检查 ----------
def check(sc):
    cam = sc.camera
    mod = sc.objects['C_Module']

    def ndc(p):
        v = world_to_camera_view(sc, cam, Vector(p))
        return v.x, v.y, v.z

    def margin(points):
        m = 1.0
        for p in points:
            x, y, z = ndc(p)
            m = min(m, x, 1 - x, y, 1 - y)
        return m

    cage_mouth = [(sx * CAGE_W / 2, 0.0, z) for sx in (-1, 1) for z in (0.0, CAGE_H)]
    plate_pt = (PLATE_X1, 0.0, PLATE_Z1)          # 挡板右上角
    heat_pt = (0.2, -9.4, 2.4)                    # 散热器前上沿
    print('frame  t     az    el    D    | 模块框边距 | 笼口框边距 | 模块前端屏幕位置 | 挡板角 vs 散热器（视差）')
    rows = []
    for f in (1, 16, 31, 46, 61, 76, 91, 106, 121, 136, 151, 166, 180):
        sc.frame_set(f)
        p = PROG[f - 1]
        yb = mod.location.y
        corners = [(sx * MOD_W / 2, yb + dy, MOD_Z + sz * MOD_H / 2) for sx in (-1, 1) for dy in (0, MOD_L) for sz in (-1, 1)]
        front = ndc((0, yb + MOD_L, MOD_Z))
        a, b = ndc(plate_pt), ndc(heat_pt)
        rows.append((f, front, a, b))
        print(f'{f:4d}  {t_of(f):4.2f}  {lerp(AZ0, AZ1, p):5.1f} {lerp(EL0, EL1, p):5.1f} {lerp(D0, D1, p):5.1f} |'
              f'   {margin(corners):+.3f}   |   {margin(cage_mouth):+.3f}   |  ({front[0]:.2f}, {front[1]:.2f})  |'
              f' dx={a[0] - b[0]:+.3f} dy={a[1] - b[1]:+.3f}')
    (f0, _, a0, b0), (f1, _, a1, b1) = rows[0], rows[-1]
    print('视差：挡板角和散热器在画面上的相对位置，从头到尾变化 dx %.3f、dy %.3f（画面宽 / 高 = 1）'
          % ((a1[0] - b1[0]) - (a0[0] - b0[0]), (a1[1] - b1[1]) - (a0[1] - b0[1])))


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['save']
    half = '--half' in argv
    argv = [a for a in argv if a != '--half']
    mode = argv[0]
    sc = build(half)
    if mode == 'check':
        check(sc)
        return
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'scene.blend'), compress=True)
    if mode == 'stills':
        os.makedirs(os.path.join(HERE, 'out', 'stills'), exist_ok=True)
        for f in [int(x) for x in argv[1].split(',')]:
            sc.frame_set(f)
            sc.render.filepath = os.path.join(HERE, 'out', 'stills', f'f{f:03d}.png')
            bpy.ops.render.render(write_still=True)
    elif mode == 'anim':
        os.makedirs(os.path.join(HERE, 'out', 'frames'), exist_ok=True)
        sc.render.filepath = os.path.join(HERE, 'out', 'frames', 'f')
        bpy.ops.render.render(animation=True)


main()
