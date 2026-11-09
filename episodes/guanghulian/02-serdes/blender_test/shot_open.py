# 光互连 02 上集开头 · Blender 测试镜头（2026-11-09）
# 俯看一张木桌：左边一根老打印机的 25 针并口线（DB-25 插头朝镜头，能数针），右边一根 USB 2.0 线（A 型插头，舌片上 4 个金属触点 = 4 根线；不用 USB-C：C 型有 24 个触点、线里也不止 4 根）；两根线往画面上方延伸。
# 线上跑着发光的小环：并口线上稀、慢；USB 上密、快（运动模糊拖出光尾）。镜头 8.25 秒慢慢推近，浅景深。
# 用法：blender -b --python shot_open.py -- <输出目录> <宽> <高> <采样> [--gpu] [--fps N] [--video] [帧号…]
#   不给帧号就渲全部帧（8.25 秒）；--gpu 用显卡（OptiX，不行就 CUDA）；--video 直接出一个 MP4（opening.mp4），不出 PNG；--fps 默认 24
# 同时导出每帧几个锚点的屏幕坐标（anchors.json），给 2D 标签叠加用。
import bpy, bmesh, math, sys, json, os
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
args = sys.argv[sys.argv.index('--') + 1:]; OUT, W, H, SAMP = args[0], int(args[1]), int(args[2]), int(args[3]); rest = args[4:]
GPU = '--gpu' in rest; VIDEO = '--video' in rest; FPS = int(rest[rest.index('--fps') + 1]) if '--fps' in rest else 24
FRAMES = [int(a) for i, a in enumerate(rest) if a.isdigit() and not (i > 0 and rest[i - 1] == '--fps')]
NF = round(8.25 * FPS); SPD = 24 / FPS          # 光环速度按 24 fps 调的，换帧率时按比例换算
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; os.makedirs(OUT, exist_ok=True)
print('BLENDER_VERSION', bpy.app.version_string)
def fcurves_of(o):        # Blender 4.x：action.fcurves；Blender 5.x：分层动作，F 曲线在 channelbag 里
    ad = o.animation_data
    if not ad or not ad.action: return []
    act = ad.action
    if hasattr(act, 'fcurves'): return list(act.fcurves)
    try:
        from bpy_extras import anim_utils
        cb = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
        if cb: return list(cb.fcurves)
    except Exception: pass
    out = []
    for layer in act.layers:
        for strip in layer.strips:
            for cb in strip.channelbags: out += list(cb.fcurves)
    return out
def set_fmt(fmt):          # Blender 5.x 先要指定输出类型（图片 / 视频），再选格式
    ims = sc.render.image_settings
    if hasattr(ims, 'media_type'): ims.media_type = 'VIDEO' if fmt == 'FFMPEG' else 'IMAGE'
    ims.file_format = fmt

# ---------- 材质 ----------
def principled(name, col, metal=0.0, rough=0.5, emit=None, es=0.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = es
    return m
def wood():
    m = bpy.data.materials.new('wood'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; Lk = nt.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.55, 0.045, 0.55)
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0; nz.inputs['Detail'].default_value = 8
    wv = N.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 3.0; wv.inputs['Distortion'].default_value = 2.5; wv.inputs['Detail'].default_value = 6
    ramp = N.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (0.36, 0.21, 0.11, 1); ramp.color_ramp.elements[1].color = (0.55, 0.35, 0.19, 1)
    Lk.new(tc.outputs['Object'], mp.inputs['Vector']); Lk.new(mp.outputs['Vector'], nz.inputs['Vector']); Lk.new(nz.outputs['Color'], wv.inputs['Vector'])
    Lk.new(wv.outputs['Fac'], ramp.inputs['Fac']); Lk.new(ramp.outputs['Color'], b.inputs['Base Color'])
    bump = N.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.08; Lk.new(wv.outputs['Fac'], bump.inputs['Height']); Lk.new(bump.outputs['Normal'], b.inputs['Normal'])
    b.inputs['Roughness'].default_value = 0.42; b.inputs['Coat Weight'].default_value = 0.25; b.inputs['Coat Roughness'].default_value = 0.2
    return m
M = dict(wood=wood(), beige=principled('beige', (0.72, 0.68, 0.58), 0, 0.55), nickel=principled('nickel', (0.85, 0.85, 0.83), 1.0, 0.22),
         insert=principled('insert', (0.03, 0.035, 0.05), 0, 0.5), gold=principled('gold', (1.0, 0.76, 0.35), 1.0, 0.25),
         grey=principled('greycable', (0.62, 0.6, 0.55), 0, 0.6), black=principled('black', (0.02, 0.02, 0.022), 0, 0.42),
         glowY=principled('glowY', (1, 0.8, 0.3), 0, 0.5, (1.0, 0.72, 0.22), 40.0), glowS=principled('glowS', (1, 0.8, 0.3), 0, 0.5, (1.0, 0.65, 0.2), 18.0))

def mesh_obj(name, bm, mat, bevel=0.0, seg=3):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.data.materials.append(mat)
    if bevel: md = o.modifiers.new('bev', 'BEVEL'); md.width = bevel; md.segments = seg; md.limit_method = 'ANGLE'
    for p in o.data.polygons: p.use_smooth = True
    return o
def prism(name, pts, y0, y1, mat, bevel=0.0, seg=3):      # pts：x-z 平面上的多边形，沿 y 从 y0 拉到 y1
    bm = bmesh.new(); a = [bm.verts.new((x, y0, z)) for x, z in pts]; b = [bm.verts.new((x, y1, z)) for x, z in pts]
    bm.faces.new(a[::-1]); bm.faces.new(b)
    for i in range(len(pts)): j = (i + 1) % len(pts); bm.faces.new((a[i], a[j], b[j], b[i]))
    return mesh_obj(name, bm, mat, bevel, seg)
def rbox(name, c, s, mat, bevel):
    bpy.ops.mesh.primitive_cube_add(location=c); o = bpy.context.object; o.name = name; o.scale = (s[0] / 2, s[1] / 2, s[2] / 2); bpy.ops.object.transform_apply(scale=True)
    md = o.modifiers.new('bev', 'BEVEL'); md.width = bevel; md.segments = 6; o.data.materials.append(mat); bpy.ops.object.shade_smooth(); return o
def cyl(name, c, r, d, mat, axis='Y'):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=c, vertices=24); o = bpy.context.object; o.name = name
    if axis == 'Y': o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(mat); bpy.ops.object.shade_smooth(); return o

# ---------- 桌面 ----------
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 20, 0)); desk = bpy.context.object; desk.data.materials.append(M['wood'])

# ---------- DB-25 插头（单位：厘米） ----------
DX = -1.9; ZC = 0.8
def trap(tw, bw, h, r=0.0): return [(DX - tw / 2, ZC + h / 2), (DX + tw / 2, ZC + h / 2), (DX + bw / 2, ZC - h / 2), (DX - bw / 2, ZC - h / 2)]
rbox('hood', (DX, 1.7, ZC), (5.5, 3.2, 1.6), M['beige'], 0.18)
rbox('flange', (DX, 0.04, ZC), (5.3, 0.08, 1.25), M['nickel'], 0.03)
shell = prism('shell', trap(3.9, 3.3, 0.95), -0.6, 0.0, M['nickel'], 0.02)
cut = prism('cut', trap(3.7, 3.1, 0.8), -0.8, -0.1, M['nickel'])
bo = shell.modifiers.new('hole', 'BOOLEAN'); bo.object = cut; bo.operation = 'DIFFERENCE'; cut.hide_render = True; cut.hide_viewport = True
prism('insert', trap(3.7, 3.1, 0.8), -0.36, 0.0, M['insert'])
for k in range(13): cyl(f'pinA{k}', (DX - 1.662 + k * 0.277, -0.44, ZC + 0.14), 0.05, 0.18, M['gold'])
for k in range(12): cyl(f'pinB{k}', (DX - 1.524 + k * 0.277, -0.44, ZC - 0.14), 0.05, 0.18, M['gold'])
for s in (-1, 1): cyl(f'screw{s}', (DX + s * 2.35, -0.25, ZC), 0.17, 0.6, M['nickel'])

# ---------- USB 2.0 A 型插头（外壳 12 × 4.5 mm，舌片上 4 个触点） ----------
UX = 1.75; UZ = 0.42
M['white'] = principled('white', (0.92, 0.91, 0.88), 0, 0.45)
rbox('overmold', (UX, 1.25, UZ), (1.6, 2.5, 0.84), M['black'], 0.2)
ash = prism('ashell', [(UX - 0.6, UZ + 0.225), (UX + 0.6, UZ + 0.225), (UX + 0.6, UZ - 0.225), (UX - 0.6, UZ - 0.225)], -1.2, 0.0, M['nickel'], 0.015)
acut = prism('acut', [(UX - 0.56, UZ + 0.19), (UX + 0.56, UZ + 0.19), (UX + 0.56, UZ - 0.19), (UX - 0.56, UZ - 0.19)], -1.4, -0.05, M['nickel'])
bo2 = ash.modifiers.new('hole', 'BOOLEAN'); bo2.object = acut; bo2.operation = 'DIFFERENCE'; acut.hide_render = True; acut.hide_viewport = True
rbox('atongue', (UX, -0.6, UZ - 0.09), (1.1, 1.15, 0.18), M['white'], 0.02)
for k, dx in enumerate((-0.375, -0.125, 0.125, 0.375)): rbox(f'acontact{k}', (UX + dx, -0.66, UZ + 0.005), (0.11, 0.85, 0.012), M['gold'], 0.004)
for dx in (-0.3, 0.3): rbox(f'awin{dx}', (UX + dx, -0.75, UZ + 0.226), (0.22, 0.22, 0.006), M['insert'], 0.01)
# 插头前端往上翘 25°（像搭在线上），让镜头看得见舌片上的 4 个触点
bpy.ops.object.empty_add(location=(UX, -1.2, UZ + 0.1)); uanc = bpy.context.object; uanc.name = 'usb_anchor'
bpy.ops.object.empty_add(location=(UX, 2.5, UZ)); piv = bpy.context.object; piv.name = 'usb_pivot'
for o in [x for x in sc.objects if x.name.startswith(('overmold', 'ashell', 'acut', 'atongue', 'acontact', 'awin', 'usb_anchor'))]:
    o.parent = piv; o.matrix_parent_inverse = piv.matrix_world.inverted()
piv.rotation_euler.x = math.radians(-25); bpy.context.view_layer.update()

# ---------- 线（贝塞尔曲线 + 圆截面） ----------
def cable(name, pts, r, mat):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 6; cu.resolution_u = 24
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts): bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o); o.data.materials.append(mat); return o
cA = cable('cableA', [(DX, 3.3, ZC), (DX - 0.2, 6.0, 0.42), (DX + 0.9, 12, 0.38), (DX - 0.6, 19, 0.38), (DX + 0.4, 28, 0.38), (DX - 0.3, 40, 0.38)], 0.38, M['grey'])
cB = cable('cableB', [(UX, 2.5, UZ), (UX + 0.15, 5.0, 0.21), (UX - 0.6, 11, 0.2), (UX + 0.5, 18, 0.2), (UX - 0.3, 28, 0.2), (UX + 0.2, 40, 0.2)], 0.2, M['black'])

# ---------- 沿线跑的光环（Follow Path，线性匀速，首尾循环） ----------
def pulses(path, n, r, minor, mat, speed_frac, phase0=0.0):
    path.data.use_path = True; path.data.path_duration = NF
    for k in range(n):
        bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=minor, major_segments=32, minor_segments=8); o = bpy.context.object; o.data.materials.append(mat)
        c = o.constraints.new('FOLLOW_PATH'); c.target = path; c.use_fixed_location = True; c.use_curve_follow = True; c.forward_axis = 'FORWARD_Z'; c.up_axis = 'UP_Y'
        # offset 从 a 线性走到 a + speed*NF；超过 1 的部分用多个关键帧折回（保证 1–198 帧连续）
        a = (phase0 + k / n) % 1.0
        for f in range(1, NF + 1, 2):
            c.offset_factor = min(0.999, (a + speed_frac * (f - 1)) % 1.0); c.keyframe_insert('offset_factor', frame=f)
        if o.animation_data and o.animation_data.action:
            for fc in fcurves_of(o):
                for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
                # 折回处（1 → 0）用常数插值，避免倒着扫过整根线
                kps = fc.keyframe_points
                for i in range(len(kps) - 1):
                    if kps[i + 1].co[1] < kps[i].co[1]: kps[i].interpolation = 'CONSTANT'
pulses(cA, 4, 0.40, 0.035, M['glowS'], 0.0018 * SPD)          # 并口线：稀、慢
pulses(cB, 22, 0.215, 0.03, M['glowY'], 0.0085 * SPD)         # USB：密、快

# ---------- 灯光、世界 ----------
def area(loc, rot, energy, size, col):
    bpy.ops.object.light_add(type='AREA', location=loc); L = bpy.context.object; L.data.energy = energy; L.data.size = size; L.data.color = col; L.rotation_euler = [math.radians(a) for a in rot]; return L
area((-14, -6, 18), (35, 0, -55), 9000, 14, (1.0, 0.93, 0.85))      # 主光：左上、暖、大而软
area((12, 26, 9), (65, 0, 150), 2500, 8, (0.65, 0.8, 1.0))           # 轮廓光：右后、冷
area((0, -20, 4), (85, 0, 0), 600, 10, (1.0, 0.95, 0.9))             # 补光：正面低
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.045, 0.04, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6

# ---------- 相机：俯看、慢慢推近、浅景深 ----------
bpy.ops.object.empty_add(location=(-1.15, 3.0, 0.4)); tgt = bpy.context.object; tgt.name = 'target'
bpy.ops.object.camera_add(location=(-1.15, -11.2, 11.7)); cam = bpy.context.object; sc.camera = cam; cam.data.lens = 24; cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24
tc_ = cam.constraints.new('TRACK_TO'); tc_.target = tgt; tc_.track_axis = 'TRACK_NEGATIVE_Z'; tc_.up_axis = 'UP_Y'
cam.data.dof.use_dof = True; bpy.ops.object.empty_add(location=(-1.0, 0.0, 0.6)); foc = bpy.context.object; foc.name = 'focus'; cam.data.dof.focus_object = foc; cam.data.dof.aperture_fstop = 0.55
cam.keyframe_insert('location', frame=1); cam.location = (-1.15, -10.0, 10.4); cam.keyframe_insert('location', frame=NF)
tgt.keyframe_insert('location', frame=1); tgt.location = (-1.15, 2.2, 0.4); tgt.keyframe_insert('location', frame=NF)
for o in (cam, tgt):
    for fc in fcurves_of(o):
        for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'EASE_IN_OUT'

# ---------- 渲染设置 ----------
sc.unit_settings.scale_length = 0.01
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
if GPU:
    prefs = bpy.context.preferences.addons['cycles'].preferences; ok = None
    for dt in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = dt; (prefs.refresh_devices() if hasattr(prefs, 'refresh_devices') else prefs.get_devices()); devs = [d for d in prefs.devices if d.type == dt]
            if devs:
                for d in prefs.devices: d.use = d.type == dt
                ok = dt; break
        except Exception: pass
    if ok: sc.cycles.device = 'GPU'; print('GPU_DEVICE', ok, [d.name for d in prefs.devices if d.use])
    else: print('GPU_DEVICE none —— 没找到 NVIDIA 显卡，改用 CPU（会很慢）')
sc.cycles.samples = SAMP; sc.cycles.use_denoising = True; sc.cycles.use_adaptive_sampling = True
sc.cycles.max_bounces = 6; sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5; sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, NF
sc.view_settings.view_transform = 'AgX'
for lk in ('AgX - Medium High Contrast', 'Medium High Contrast'):
    try: sc.view_settings.look = lk; break
    except Exception: pass
set_fmt('PNG')

# ---------- 每帧锚点（给 2D 标签） ----------
ANCH = {'db25': Vector((DX, -0.6, ZC + 0.9)), 'usb': None, 'cableA': Vector((DX + 0.9, 12, 0.8)), 'cableB': Vector((UX - 0.6, 11, 0.4))}
anchors = {}
for f in range(1, NF + 1):
    sc.frame_set(f); ANCH['usb'] = uanc.matrix_world.translation.copy(); anchors[f] = {k: [round(v.x * W, 1), round((1 - v.y) * H, 1)] for k, p in ANCH.items() for v in [world_to_camera_view(sc, cam, p)]}
json.dump({'fps': FPS, 'nf': NF, 'w': W, 'frames': anchors}, open(os.path.join(OUT, 'anchors.json'), 'w'))
if VIDEO and not FRAMES:      # 直接出一个 MP4（几乎无损），省得传一堆 PNG
    set_fmt('FFMPEG'); sc.render.ffmpeg.format = 'MPEG4'; sc.render.ffmpeg.codec = 'H264'
    for k, v in (('constant_rate_factor', 'PERC_LOSSLESS'), ('ffmpeg_preset', 'GOOD')):
        try: setattr(sc.render.ffmpeg, k, v)
        except Exception as e: print('ffmpeg 设置跳过', k, e)
    sc.render.filepath = os.path.join(OUT, 'opening.mp4')
    bpy.ops.render.render(animation=True)
else:
    for f in (FRAMES or range(1, NF + 1)):
        sc.frame_set(f); sc.render.filepath = os.path.join(OUT, f'f{f:04d}.png'); bpy.ops.render.render(write_still=True)
print('DONE', OUT)
