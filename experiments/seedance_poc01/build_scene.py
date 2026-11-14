"""Seedance PoC 01 — 3D Blockout：光模块插入网卡模块笼子（6 秒，180 帧，30 fps，竖屏）。

只做灰盒预演：四组纯色几何体 + 一台连续运动的摄影机。不追求真实模型、材质和光影。

用法（在本目录运行）：
  blender -b --factory-startup --python-exit-code 1 --python build_scene.py -- save            # 只建场景，存 scene.blend
  blender -b --factory-startup --python-exit-code 1 --python build_scene.py -- stills 1,37,82,127,180
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
# 笼子：外形 2.10 宽 × 1.10 高 × 5.00 长，壁厚 0.08；入口朝 +Y，在 y = 0；后端封闭在 y = -5。
CAGE_W, CAGE_H, CAGE_L, WALL = 2.10, 1.10, 5.00, 0.08
# 模块：1.85 宽 × 0.86 高 × 7.20 长，比笼子内腔（1.94 × 0.94）略小，沿笼子轴线运动。
MOD_W, MOD_H, MOD_L = 1.85, 0.86, 7.20
MOD_Z = WALL + 0.01 + MOD_H / 2            # 模块底面离笼子底板 0.01
# 模块后端面（朝笼子的一端）的 y：起点在入口外 1.0，终点插进 4.6（前端外露 2.6）。
MOD_BACK_Y0, MOD_BACK_Y1 = 1.00, -4.60
F_INS0, F_INS1 = 37, 127                  # 1.2 s 开始插入，4.2 s 停止

# ---------- 摄影机路径（相机位置 P，注视点 L），三段二次 Bezier 拼成一条连续曲线 ----------
CAM_P = [Vector((4.8, 18.2, 8.7)),        # 0.0 s 斜前右上方，中近景：插入方向在竖屏里大致上下走向
         Vector((3.9, 13.6, 6.5)),        # 1.2 s 只轻微前移
         Vector((2.6, 9.8, 4.3)),         # 4.2 s 向左（朝插入轴线）侧移 + 靠近，产生视差
         Vector((2.0, 7.0, 2.7))]         # 6.0 s 落在模块前端面斜前方，笼子入口仍在画面里
CAM_L = [Vector((0.8, 2.4, 0.30)),
         Vector((0.6, 2.8, 0.30)),
         Vector((0.2, 1.5, 0.45)),
         Vector((0.1, 1.8, 0.50))]        # 模块前端面中心最终在 y = 2.6
LENS = 25.0


def smootherstep(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * x * (x * (x * 6 - 15) + 10)


def cam_progress():
    """相机沿路径的进度 s(t) ∈ [0, 1]。速度：开头以约 85% 起步，中段匀速，4.2 s 后余弦减速到约 30%（不完全停死）。"""
    n = F_END - F_START + 1
    v = []
    for i in range(n):
        t = i / FPS
        if t < 1.2:
            vel = 0.85 + 0.15 * (0.5 - 0.5 * math.cos(math.pi * t / 1.2))
        elif t < 4.2:
            vel = 1.0
        else:
            u = (t - 4.2) / (5.967 - 4.2)
            vel = 0.30 + 0.70 * (0.5 + 0.5 * math.cos(math.pi * min(u, 1.0)))
        v.append(vel)
    s = [0.0]
    for i in range(1, n):
        s.append(s[-1] + 0.5 * (v[i - 1] + v[i]))
    return [x / s[-1] for x in s]


def path_point(pts, s):
    """经过四个控制点的分段 Catmull-Rom（均匀参数），保证在关键点处切线连续，不会在 1.2 s / 4.2 s 停顿。"""
    seg = min(int(s * 3), 2)
    u = s * 3 - seg
    p0 = pts[max(seg - 1, 0)]
    p1, p2 = pts[seg], pts[seg + 1]
    p3 = pts[min(seg + 2, 3)]
    u2, u3 = u * u, u * u * u
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u2 + (-p0 + 3 * p1 - 3 * p2 + p3) * u3)


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

    # A — PCB：固定，上表面 z = 0。比笼子大很多，向 +Y 延伸到模块起点之外，给出地面。
    box('A_PCB', (16.0, 26.0, 0.16), (0.0, 1.0, -0.08), m_pcb)

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
        k = smootherstep((f - F_INS0) / (F_INS1 - F_INS0))
        mod.location = (0.0, MOD_BACK_Y0 + (MOD_BACK_Y1 - MOD_BACK_Y0) * k, MOD_Z)
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
    prog = cam_progress()
    for i, f in enumerate(range(F_START, F_END + 1)):
        cam.location = path_point(CAM_P, prog[i])
        target.location = path_point(CAM_L, prog[i])
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
