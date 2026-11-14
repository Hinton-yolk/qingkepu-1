"""Seedance PoC 01 — 3D Blockout：光模块插入网卡模块笼子（6 秒，180 帧，30 fps，竖屏）。

只做灰盒预演：四组纯色几何体 + 一台连续运动的摄影机。不追求真实模型、材质和光影。

用法（在本目录运行）：
  blender -b --factory-startup --python-exit-code 1 --python build_scene.py -- save            # 只建场景，存 scene.blend
  blender -b --factory-startup --python-exit-code 1 --python build_scene.py -- stills 1,37,52,82,121,180
  blender -b --factory-startup --python-exit-code 1 --python build_scene.py -- anim             # 180 帧 PNG 到 out/frames/

单位：1 BU = 1 cm（尺寸只取大致比例，不是精确产品尺寸）。
坐标：+Y 指向笼子外（模块从 +Y 一侧插入，沿 -Y 运动），+Z 向上，PCB 上表面 z = 0。
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
F_START, F_END = 1, 180          # 第 1 帧 = 0.0 s，第 180 帧 = 5.967 s
RES_X, RES_Y = 720, 1280


def t_of(frame):
    return (frame - 1) / FPS


# ---------- 几何尺寸 ----------
# 笼子：外形 2.10 宽 × 1.10 高 × 6.00 长，壁厚 0.08；入口朝 +Y，在 y = 0；后端封闭在 y = -6。
CAGE_W, CAGE_H, CAGE_L, WALL = 2.10, 1.10, 6.00, 0.08
# 模块：1.85 宽 × 0.86 高 × 7.20 长，比笼子内腔（1.94 × 0.94）略小，沿笼子轴线运动。
MOD_W, MOD_H, MOD_L = 1.85, 0.86, 7.20
MOD_Z = WALL + 0.01 + MOD_H / 2            # 模块底面离笼子底板 0.01
# 模块后端面（朝笼子的一端）的 y：起点在入口外 1.0；终点 -5.80（离后壁内面 0.12），前端外露 1.40 供接光纤。
MOD_BACK_Y0, MOD_BACK_Y1 = 1.00, -5.80
F_INS0, F_INS1 = 37, 121                  # 1.2 s 开始插入，4.0 s 到位停止
LENS = 25.0

# ---------- 摄影机 ----------
# 相机 = 注视点 T + 距离 D × 方向(方位角 AZ, 仰角 EL)。AZ 从 +Y 轴向 +X 量（相机在模块右前方），EL 为俯视角。
# 四个阶段：
#   0.0–1.2 s  前推（D 17.6 → 14.7，到 1.2 s 速度降到接近 0）
#   1.2–1.7 s  相对稳定观察插入开始（D 只漂移 0.15，注视点不动）
#   1.7–4.0 s  注视点跟随模块外露段的中点，相机缓慢跟随、靠近，并向右侧平移产生视差
#   4.0–6.0 s  模块已静止，相机继续推向前端面，最后减速（不完全停死）
T_HOLD0, T_HOLD1, T_END = 1.2, 1.7, 5.967


def smootherstep(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * x * (x * (x * 6 - 15) + 10)


def smoothstep(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def lerp(a, b, k):
    return a + (b - a) * k


def insert_progress(frame):
    """模块插入进度 0→1。速度为梯形：约 0.3 s 余弦加速、匀速、最后约 0.9 s 余弦减速到 0（停稳）。
    这样相机稳定观察的 1.2–1.7 s 里，模块已经明显在往笼子里进。"""
    a, d = 0.3, 0.9
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
    total = integ(T)
    t = (frame - F_INS0) / FPS
    return min(max(integ(min(max(t, 0.0), T)) / total, 0.0), 1.0)


def module_back_y(frame):
    return lerp(MOD_BACK_Y0, MOD_BACK_Y1, insert_progress(frame))


def cam_at(frame):
    t = t_of(frame)
    front = module_back_y(frame) + MOD_L
    # 注视点 y：插入开始前固定在 4.4（同时框住笼子入口和整根模块）；1.7 s 起平滑过渡到「外露段中点 + 0.3」。
    track = 0.5 * front + 0.3
    w = smootherstep((t - T_HOLD1) / 0.6)
    ty = lerp(4.4, track, w)
    k_late = smoothstep((t - T_HOLD1) / (T_END - T_HOLD1))
    tx = lerp(0.6, 0.15, k_late)
    tz = lerp(0.35, 0.50, k_late)
    # 距离 D
    # 0–1.2 s 推进 2.9，到 1.2 s 速度降到起步时的约 30%；1.2–1.7 s 再线性减速到接近 0（推进 0.31），
    # 两段速度连续，相机在模块起步时「相对稳定」，但不会和模块起步前的空档叠成一段死静。
    if t < T_HOLD0:
        u = t / T_HOLD0
        d = 17.6 - 2.9 * (2 * u - 0.7 * u * u) / 1.3
    elif t < T_HOLD1:
        u = (t - T_HOLD0) / (T_HOLD1 - T_HOLD0)
        v0 = 2.9 * 0.6 / 1.3 / T_HOLD0 * (T_HOLD1 - T_HOLD0)   # 1.2 s 时的速度 × 0.5 s
        d = 14.7 - v0 * (u - 0.5 * 0.92 * u * u)
    else:
        u = (t - T_HOLD1) / (T_END - T_HOLD1)
        prog = 0.8 * smoothstep(u) + 0.2 * u         # 缓起；结尾减速但留约 20% 的余速
        d = lerp(14.7 - 2.9 * 0.6 / 1.3 / T_HOLD0 * (T_HOLD1 - T_HOLD0) * 0.54, 6.2, prog)
        # 0–1.2 s 斜向推进（方位角 11 → 13.3、俯角 27 → 24.7，减速到 1.2 s）；1.2–1.7 s 只再漂移 0.1°
    if t < T_HOLD0:
        u = t / T_HOLD0
        e = (2 * u - 0.7 * u * u) / 1.3
        az0, el0 = lerp(11.0, 13.3, e), lerp(27.0, 24.7, e)
    else:
        e = min((t - T_HOLD0) / (T_HOLD1 - T_HOLD0), 1.0)
        az0, el0 = lerp(13.3, 13.4, e), lerp(24.7, 24.6, e)
    az = math.radians(az0 + 8.0 * k_late)
    el = math.radians(el0 - 6.0 * k_late)
    T = Vector((tx, ty, tz))
    P = T + d * Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    return P, T


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


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = F_START, F_END
    sc.render.fps = FPS
    sc.render.resolution_x, sc.render.resolution_y = RES_X, RES_Y
    sc.render.resolution_percentage = 100

    m_pcb = mat('PCB_darkgreen', (0.035, 0.11, 0.06))
    m_cage = mat('Cage_midgray', (0.42, 0.42, 0.43))
    m_mod = mat('Module_blue', (0.08, 0.28, 0.85))
    m_bg = mat('Background_dark', (0.025, 0.026, 0.03))

    # A — PCB：固定，上表面 z = 0。比笼子大很多，向 +Y 延伸到相机下方，画面里看不到板边。
    box('A_PCB', (20.0, 40.0, 0.16), (0.0, 4.0, -0.08), m_pcb)

    # B — 笼子：中空长方体，五面（底、顶、左、右、后），入口 +Y 敞开。固定在 PCB 上。
    cage = bpy.data.objects.new('B_Cage', None)
    sc.collection.objects.link(cage)
    yc = -CAGE_L / 2
    box('B_Cage_floor', (CAGE_W, CAGE_L, WALL), (0, yc, WALL / 2), m_cage, cage)
    box('B_Cage_top', (CAGE_W, CAGE_L, WALL), (0, yc, CAGE_H - WALL / 2), m_cage, cage)
    box('B_Cage_left', (WALL, CAGE_L, CAGE_H), (-CAGE_W / 2 + WALL / 2, yc, CAGE_H / 2), m_cage, cage)
    box('B_Cage_right', (WALL, CAGE_L, CAGE_H), (CAGE_W / 2 - WALL / 2, yc, CAGE_H / 2), m_cage, cage)
    box('B_Cage_back', (CAGE_W, WALL, CAGE_H), (0, -CAGE_L + WALL / 2, CAGE_H / 2), m_cage, cage)

    # C — 光模块：唯一的运动主体。原点放在后端面中心，动画只改 location.y。
    bpy.ops.mesh.primitive_cube_add(size=1.0)
    mod = bpy.context.active_object
    mod.name = 'C_Module'
    mod.scale = (MOD_W, MOD_L, MOD_H)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for v in mod.data.vertices:          # 把原点移到后端面：网格整体向 +Y 平移半个长度
        v.co.y += MOD_L / 2
    mod.data.materials.append(m_mod)
    mod.color = m_mod.diffuse_color
    for f in range(F_START, F_END + 1):
        mod.location = (0.0, module_back_y(f), MOD_Z)
        mod.keyframe_insert('location', frame=f)

    # D — 背景：竖直深色平面，放在笼子后方；世界背景也设成近黑。
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(-6.0, -16.0, 8.0), rotation=(math.radians(90), 0, math.radians(-25)))
    bg = bpy.context.active_object
    bg.name = 'D_Background'
    bg.scale = (90, 50, 1)
    bg.data.materials.append(m_bg)
    bg.color = m_bg.diffuse_color
    world = bpy.data.worlds.new('World')
    world.color = (0.02, 0.021, 0.025)
    sc.world = world

    # 摄影机：注视空物体，位置和注视点逐帧烘焙（沿同一条连续曲线，单镜头无剪辑）。
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
    for o in (cam, target, mod):
        for fc in o.animation_data.action.fcurves if hasattr(o.animation_data.action, 'fcurves') else []:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'

    # 渲染：Workbench 灰盒风格——纯色、基础棚灯、物体轮廓线；无景深、无运动模糊。
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
    sc.display.render_aa = '8'
    sc.render.use_motion_blur = False
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.file_format = 'PNG'
    return sc


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['save']
    mode = argv[0]
    sc = build()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'scene.blend'), compress=True)
    if mode == 'stills':
        frames = [int(x) for x in argv[1].split(',')]
        os.makedirs(os.path.join(HERE, 'out', 'stills'), exist_ok=True)
        for f in frames:
            sc.frame_set(f)
            sc.render.filepath = os.path.join(HERE, 'out', 'stills', f'f{f:03d}.png')
            bpy.ops.render.render(write_still=True)
    elif mode == 'anim':
        os.makedirs(os.path.join(HERE, 'out', 'frames'), exist_ok=True)
        sc.render.filepath = os.path.join(HERE, 'out', 'frames', 'f')
        bpy.ops.render.render(animation=True)


main()
