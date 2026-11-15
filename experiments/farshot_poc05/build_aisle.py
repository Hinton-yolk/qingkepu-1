"""远景氛围镜头（PoC 05）：数据中心冷通道，相机匀速推进，最后落在右侧一台交换机的 OSFP 口上。

用来比较 Cycles 和 LTX-2.5 Layout-To-Render 在「远景、氛围」这类镜头上的差别（DECISIONS 11-14：「我们再测试一个远景的」）。
24 fps、145 帧（6.04 s）、1088×1920，灰模和 Cycles 关键帧同尺寸、同视场。单位：米。

用法（本目录）：
  python3 make_panel_textures.py                                     # 先生成面板贴图
  blender -b --factory-startup --python-exit-code 1 --python build_aisle.py -- frames 1,73,145 --res 544 --spp 32 --out out/prev
  blender -b ... -- clay --out out/clay/f                             # 灰模（Workbench），145 帧
  blender -b ... -- anim --spp 128 [--gpu] [--fs 1 --fe 72] --out out/frames/f
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, F_LAST = 24, 145
random.seed(5)

U = 0.04445
RACK_W, RACK_D, RACK_H = 0.60, 1.07, 2.0     # 42U 机柜（含框架）
AISLE = 1.2                                  # 冷通道宽（两排机柜前门之间）
N_RACKS = 9
TARGET_RACK, TARGET_U = 4, 27                # 右排第 5 台机柜，第 27U 放那台交换机（离地约 1.3 m）

_MESH = {}


# ---------- 材质 ----------
def mat_basic(name, col, metal=0.0, rough=0.5, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = strength
    return m


def mat_panel(name):
    """面板：颜色图 + 指示灯发光遮罩（UV 铺满面板正面）。"""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    col = nt.nodes.new('ShaderNodeTexImage')
    col.image = bpy.data.images.load(os.path.join(HERE, 'assets_dl', f'{name}_col.png'), check_existing=True)
    led = nt.nodes.new('ShaderNodeTexImage')
    led.image = bpy.data.images.load(os.path.join(HERE, 'assets_dl', f'{name}_led.png'), check_existing=True)
    nt.links.new(col.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(led.outputs['Color'], b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value = 10.0
    b.inputs['Metallic'].default_value = 0.3
    b.inputs['Roughness'].default_value = 0.42
    return m


def mat_tile(name, real=0.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1 / real, 1 / real, 1)
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = bpy.data.images.load(os.path.join(HERE, 'assets_dl', f'{name}_col.png'), check_existing=True)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
    nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.35
    return m


# ---------- 几何 ----------
def box(name, x0, x1, y0, y1, z0, z1, mat):
    key = (round(x1 - x0, 4), round(y1 - y0, 4), round(z1 - z0, 4), mat.name)
    me = _MESH.get(key)
    if me is None:
        import bmesh
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(x1 - x0, y1 - y0, z1 - z0), verts=bm.verts)
        me = bpy.data.meshes.new('box')
        bm.to_mesh(me)
        bm.free()
        me.materials.append(mat)
        _MESH[key] = me
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    return o


def panel(name, mat, w, h, loc, facing):
    """面板平面（UV 0–1 铺满），facing = +1 朝 +X，-1 朝 -X。"""
    key = ('panel', round(w, 4), round(h, 4), mat.name, facing)
    me = _MESH.get(key)
    if me is None:
        me = bpy.data.meshes.new('panel')
        hw, hh = w / 2, h / 2
        if facing > 0:
            verts = [(0, hw, -hh), (0, -hw, -hh), (0, -hw, hh), (0, hw, hh)]
        else:
            verts = [(0, -hw, -hh), (0, hw, -hh), (0, hw, hh), (0, -hw, hh)]
        me.from_pydata(verts, [], [(0, 1, 2, 3)])
        uv = me.uv_layers.new()
        for li, (u, v) in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
            uv.data[li].uv = (u, v)
        me.materials.append(mat)
        _MESH[key] = me
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    return o


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    M = dict(
        frame=mat_basic('rack_frame', (0.012, 0.012, 0.014), 0.3, 0.45),
        side=mat_basic('rack_side', (0.02, 0.02, 0.024), 0.2, 0.55),
        tray_yellow=mat_basic('fiber_tray', (0.85, 0.62, 0.02), 0.0, 0.45),
        tray_black=mat_basic('ladder_tray', (0.03, 0.03, 0.035), 0.4, 0.5),
        light=mat_basic('ceiling_light', (1, 1, 1), 0, 0.5, (0.85, 0.92, 1.0), 9.0),
        ceiling=mat_basic('ceiling', (0.05, 0.05, 0.055), 0.0, 0.8),
        wall=mat_basic('end_wall', (0.03, 0.035, 0.04), 0.0, 0.8),
    )
    P = {n: mat_panel(n) for n in ('srv1u_0', 'srv1u_1', 'srv1u_2', 'srv2u_0', 'srv2u_1', 'srv2u_2', 'sw1u_osfp', 'blank1u')}
    T = {n: mat_tile(n) for n in ('tile', 'tile_perf')}

    # 活动地板：通道里是开孔的通风地板（冷通道送风），机柜下是普通地板
    for i in range(-2, 2 * N_RACKS + 4):
        y0 = -1.8 + i * 0.6
        for j, x0 in enumerate((-1.8, -1.2, -0.6, 0.0, 0.6, 1.2)):
            perf = -AISLE / 2 <= x0 + 0.3 <= AISLE / 2
            box('tile', x0 + 0.002, x0 + 0.598, y0 + 0.002, y0 + 0.598, -0.03, 0.0, T['tile_perf' if perf else 'tile'])
    box('floor_under', -6, 6, -6, 16, -0.2, -0.031, M['frame'])
    box('ceiling', -6, 6, -6, 16, 3.2, 3.3, M['ceiling'])
    box('end_wall', -6, 6, 1.0 + N_RACKS * RACK_W + 1.5, 1.0 + N_RACKS * RACK_W + 1.6, 0, 3.3, M['wall'])

    # 两排机柜，前门开着（看得到设备面板），面朝通道
    for side in (-1, 1):
        xf = side * AISLE / 2                    # 机柜前沿
        xb = side * (AISLE / 2 + RACK_D)
        for r in range(N_RACKS):
            y0 = r * RACK_W
            x0, x1 = min(xf, xb), max(xf, xb)
            box('rack_top', x0, x1, y0, y0 + RACK_W, RACK_H - 0.04, RACK_H, M['frame'])
            box('rack_post', x0, x1, y0, y0 + 0.02, 0, RACK_H, M['side'])
            box('rack_post', x0, x1, y0 + RACK_W - 0.02, y0 + RACK_W, 0, RACK_H, M['side'])
            box('rack_plinth', x0, x1, y0, y0 + RACK_W, 0, 0.1, M['frame'])
            # 设备：从 2U 处往上填，随机 1U / 2U / 挡板 / 交换机
            u = 2
            while u < 42:
                if side > 0 and r == TARGET_RACK and u == TARGET_U:
                    kind, n = 'sw1u_osfp', 1
                else:
                    roll = random.random()
                    if roll < 0.12:
                        kind, n = 'blank1u', 1
                    elif roll < 0.55:
                        kind, n = random.choice(['srv1u_0', 'srv1u_1', 'srv1u_2']), 1
                    elif roll < 0.92:
                        kind, n = random.choice(['srv2u_0', 'srv2u_1', 'srv2u_2']), 2
                    else:
                        kind, n = 'sw1u_osfp', 1
                if u + n > 42:
                    kind, n = 'blank1u', 1
                zc = 0.1 + (u + n / 2) * U
                inset = 0.03
                panel(f'{kind}', P[kind], 0.4826, n * U - 0.001, (xf + side * inset, y0 + RACK_W / 2, zc), -side)   # 面板比机柜前沿往里缩 3 cm
                # 设备本体（深色方块，往机柜里面延伸，挡住后面）
                box('chassis', min(xf + side * (inset + 0.002), xf + side * 0.75), max(xf + side * (inset + 0.002), xf + side * 0.75),
                    y0 + 0.06, y0 + RACK_W - 0.06, zc - n * U / 2, zc + n * U / 2 - 0.001, M['frame'])
                u += n
        # 机柜上方：黄色光纤槽 + 黑色梯架
        box('fiber_tray', min(xf, xf + side * 0.35), max(xf, xf + side * 0.35), -0.5, N_RACKS * RACK_W + 0.5, 2.35, 2.45, M['tray_yellow'])
        box('ladder_tray', min(xb, xb - side * 0.5), max(xb, xb - side * 0.5), -0.5, N_RACKS * RACK_W + 0.5, 2.6, 2.65, M['tray_black'])
    # 通道正上方的条形灯
    for k in range(6):
        y = -0.3 + k * 1.0
        box('light', -0.08, 0.08, y, y + 0.7, 3.05, 3.08, M['light'])
        if '--clay' not in sys.argv:                 # 每盏灯下面放一个真正照明的面光源（发光网格只负责「看得见灯」）
            ld = bpy.data.lights.new('fixture', 'AREA')
            ld.shape = 'RECTANGLE'
            ld.size, ld.size_y = 0.16, 0.7
            ld.energy = 42.0
            ld.color = (0.86, 0.92, 1.0)
            lo = bpy.data.objects.new('fixture', ld)
            sc.collection.objects.link(lo)
            lo.location = (0, y + 0.35, 3.04)
    # 远处补一点冷色环境光，让机柜轮廓从暗部里出来
    if '--clay' not in sys.argv:
        ld = bpy.data.lights.new('fill', 'AREA')
        ld.size = 1.2
        ld.energy = 18.0
        ld.color = (0.6, 0.75, 1.0)
        lo = bpy.data.objects.new('fill', ld)
        sc.collection.objects.link(lo)
        lo.location = (0, 6.5, 1.6)
        lo.rotation_euler = (math.radians(90), 0, 0)
    return sc, M


# ---------- 相机 ----------
def cam_state(f):
    """相机：从通道口（y≈-1.6）匀速推进到 y≈1.7，高度 1.55 → 1.42，镜头逐渐转向右侧那台交换机。"""
    t = (f - 1) / (F_LAST - 1)
    e = 0.5 - 0.5 * math.cos(math.pi * t)                # 缓起缓停
    e = 0.15 * t + 0.85 * e
    target_sw = Vector((AISLE / 2 - 0.03, TARGET_RACK * RACK_W + RACK_W / 2, 0.1 + (TARGET_U + 0.5) * U))
    pos = Vector((0.05 - 0.22 * e, -1.6 + 3.3 * e, 1.55 - 0.13 * e))
    far = Vector((0.0, pos.y + 6.0, 1.35))               # 开头：看向通道深处
    w = 0.5 - 0.5 * math.cos(math.pi * min(max((t - 0.2) / 0.8, 0), 1))
    aim = far.lerp(target_sw, w)
    return pos, aim


def camera(sc, lens=24.0):
    cd = bpy.data.cameras.new('CAM')
    cd.lens = lens
    cd.sensor_fit = 'VERTICAL'
    cd.sensor_height = 36.0
    cd.clip_start = 0.02
    c = bpy.data.objects.new('CAM', cd)
    sc.collection.objects.link(c)
    sc.camera = c
    prev = None
    for f in range(1, F_LAST + 1):
        pos, aim = cam_state(f)
        c.location = pos
        q = (aim - pos).to_track_quat('-Z', 'Y')
        c.rotation_euler = q.to_euler('XYZ', prev) if prev else q.to_euler()
        prev = c.rotation_euler.copy()
        c.keyframe_insert('location', frame=f)
        c.keyframe_insert('rotation_euler', frame=f)
        cd.dof.focus_distance = (aim - pos).length
        cd.dof.keyframe_insert('focus_distance', frame=f)
    cd.dof.aperture_fstop = 2.8
    return c


def look_cycles(sc, spp, gpu):
    # 薄雾：整条通道
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 3.0, 1.6))
    v = bpy.context.active_object
    v.name = 'haze'
    v.scale = (4.0, 14.0, 3.2)
    vm = bpy.data.materials.new('haze')
    vm.use_nodes = True
    nt = vm.node_tree
    nt.nodes.remove(nt.nodes['Principled BSDF'])
    pv = nt.nodes.new('ShaderNodeVolumePrincipled')
    pv.inputs['Density'].default_value = 0.014
    pv.inputs['Color'].default_value = (0.75, 0.85, 1.0, 1)
    nt.links.new(pv.outputs['Volume'], nt.nodes['Material Output'].inputs['Volume'])
    v.data.materials.append(vm)
    w = bpy.data.worlds.new('W')
    w.color = (0.002, 0.003, 0.004)
    sc.world = w
    sc.camera.data.dof.use_dof = True
    r = sc.render
    r.engine = 'CYCLES'
    sc.cycles.samples = spp
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.cycles.volume_step_rate = 4.0
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.4
    sc.view_settings.view_transform = 'AgX'
    try:
        sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    sc.cycles.device = 'CPU'
    if gpu:
        pr = bpy.context.preferences.addons['cycles'].preferences
        pr.compute_device_type = 'OPTIX'
        pr.get_devices()
        gpus = [d for d in pr.devices if d.type == 'OPTIX']
        if not gpus:
            raise SystemExit('要求用 GPU，但没找到 OPTIX 设备')
        for d in pr.devices:
            d.use = d.type == 'OPTIX'
        sc.cycles.device = 'GPU'
        print('GPU:', [d.name for d in gpus], flush=True)


def look_clay(sc):
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading
    sh.light = 'STUDIO'
    sh.color_type = 'SINGLE'
    sh.single_color = (0.62, 0.62, 0.62)
    sh.show_cavity = True
    sh.cavity_type = 'WORLD'
    sh.show_shadows = True
    sh.shadow_intensity = 0.4
    sh.background_type = 'WORLD'
    w = bpy.data.worlds.new('W')
    w.color = (0.05, 0.05, 0.055)
    sc.world = w
    sc.display.render_aa = '8'
    sc.render.use_motion_blur = False
    sc.camera.data.dof.use_dof = False
    sc.view_settings.view_transform = 'Standard'


def main():
    import time
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['frames', '1']
    opt = lambda k, d: type(d)(argv[argv.index(k) + 1]) if k in argv else d
    t0 = time.time()
    sc, M = build()
    camera(sc)
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, F_LAST
    sc.render.resolution_x = opt('--w', 1088)
    sc.render.resolution_y = opt('--h', 1920)
    res = opt('--res', 0)
    sc.render.resolution_percentage = int(100 * res / sc.render.resolution_x) if res else 100
    out = os.path.join(HERE, opt('--out', 'out/prev'))
    sc.render.image_settings.file_format = 'PNG'
    if argv[0] == 'clay':
        look_clay(sc)
    else:
        look_cycles(sc, opt('--spp', 64), '--gpu' in argv)
    print(f'[timing] 搭场景 {time.time() - t0:.1f} 秒，物体 {len(bpy.data.objects)}', flush=True)
    t1 = time.time()
    if argv[0] == 'frames':
        os.makedirs(out, exist_ok=True)
        for f in [int(x) for x in argv[1].split(',')]:
            sc.frame_set(f)
            sc.render.filepath = os.path.join(out, f'f{f:04d}.png')
            bpy.ops.render.render(write_still=True)
    else:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        sc.frame_start, sc.frame_end = opt('--fs', 1), opt('--fe', F_LAST)
        sc.render.filepath = out
        bpy.ops.render.render(animation=True)
    print(f'[timing] 渲染 {time.time() - t1:.1f} 秒', flush=True)
    if '--save' in argv:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'scene_aisle.blend'), compress=True)


main()
