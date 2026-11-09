# 光互连 02 上集开头 · Blender 测试镜头（2026-11-09）
# 俯看一张木桌：左边一根老打印机的 25 针并口线（DB-25 插头朝镜头，能数针），右边一根 USB-C 线；两根线往画面上方延伸。
# 线上跑着发光的小环：并口线上稀、慢；USB 上密、快（运动模糊拖出光尾）。镜头 8.25 秒慢慢推近，浅景深。
# 用法：blender -b --python shot_open.py -- <输出目录> <宽> <高> <采样> [帧号…]（不给帧号就渲全部 1–198 帧，24 fps）
# 同时导出每帧几个锚点的屏幕坐标（anchors.json），给 2D 标签叠加用。
import bpy, bmesh, math, sys, json, os
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
args = sys.argv[sys.argv.index('--') + 1:]; OUT, W, H, SAMP = args[0], int(args[1]), int(args[2]), int(args[3]); FRAMES = [int(a) for a in args[4:]]
FPS, NF = 24, 198
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; os.makedirs(OUT, exist_ok=True)

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

# ---------- USB-C 插头 ----------
UX = 1.9; UZ = 0.31
rbox('overmold', (UX, 1.0, UZ), (1.2, 2.0, 0.62), M['black'], 0.22)
rbox('cshell', (UX, -0.32, UZ), (0.84, 0.65, 0.26), M['nickel'], 0.12)
rbox('ctongue', (UX, -0.62, UZ), (0.62, 0.06, 0.1), M['insert'], 0.04)

# ---------- 线（贝塞尔曲线 + 圆截面） ----------
def cable(name, pts, r, mat):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 6; cu.resolution_u = 24
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts): bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); sc.collection.objects.link(o); o.data.materials.append(mat); return o
cA = cable('cableA', [(DX, 3.3, ZC), (DX - 0.2, 6.0, 0.42), (DX + 0.9, 12, 0.38), (DX - 0.6, 19, 0.38), (DX + 0.4, 28, 0.38), (DX - 0.3, 40, 0.38)], 0.38, M['grey'])
cB = cable('cableB', [(UX, 2.0, UZ), (UX + 0.15, 4.5, 0.17), (UX - 0.6, 11, 0.16), (UX + 0.5, 18, 0.16), (UX - 0.3, 28, 0.16), (UX + 0.2, 40, 0.16)], 0.16, M['black'])

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
            for fc in o.animation_data.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
                # 折回处（1 → 0）用常数插值，避免倒着扫过整根线
                kps = fc.keyframe_points
                for i in range(len(kps) - 1):
                    if kps[i + 1].co[1] < kps[i].co[1]: kps[i].interpolation = 'CONSTANT'
pulses(cA, 4, 0.40, 0.035, M['glowS'], 0.0018)          # 并口线：稀、慢
pulses(cB, 22, 0.175, 0.03, M['glowY'], 0.0085)         # USB：密、快

# ---------- 灯光、世界 ----------
def area(loc, rot, energy, size, col):
    bpy.ops.object.light_add(type='AREA', location=loc); L = bpy.context.object; L.data.energy = energy; L.data.size = size; L.data.color = col; L.rotation_euler = [math.radians(a) for a in rot]; return L
area((-14, -6, 18), (35, 0, -55), 9000, 14, (1.0, 0.93, 0.85))      # 主光：左上、暖、大而软
area((12, 26, 9), (65, 0, 150), 2500, 8, (0.65, 0.8, 1.0))           # 轮廓光：右后、冷
area((0, -20, 4), (85, 0, 0), 600, 10, (1.0, 0.95, 0.9))             # 补光：正面低
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.045, 0.04, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.6

# ---------- 相机：俯看、慢慢推近、浅景深 ----------
bpy.ops.object.empty_add(location=(-1.3, 3.0, 0.4)); tgt = bpy.context.object; tgt.name = 'target'
bpy.ops.object.camera_add(location=(-1.3, -10.5, 11.0)); cam = bpy.context.object; sc.camera = cam; cam.data.lens = 24; cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24
tc_ = cam.constraints.new('TRACK_TO'); tc_.target = tgt; tc_.track_axis = 'TRACK_NEGATIVE_Z'; tc_.up_axis = 'UP_Y'
cam.data.dof.use_dof = True; bpy.ops.object.empty_add(location=(-1.0, 0.0, 0.6)); foc = bpy.context.object; foc.name = 'focus'; cam.data.dof.focus_object = foc; cam.data.dof.aperture_fstop = 0.55
cam.keyframe_insert('location', frame=1); cam.location = (-1.3, -9.4, 9.7); cam.keyframe_insert('location', frame=NF)
tgt.keyframe_insert('location', frame=1); tgt.location = (-1.3, 2.2, 0.4); tgt.keyframe_insert('location', frame=NF)
for o in (cam, tgt):
    for fc in o.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'EASE_IN_OUT'

# ---------- 渲染设置 ----------
sc.unit_settings.scale_length = 0.01
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMP; sc.cycles.use_denoising = True; sc.cycles.use_adaptive_sampling = True
sc.cycles.max_bounces = 6; sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5; sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, NF
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'; sc.render.image_settings.file_format = 'PNG'

# ---------- 每帧锚点（给 2D 标签） ----------
ANCH = {'db25': Vector((DX, -0.6, ZC + 0.9)), 'usb': Vector((UX, -0.65, UZ + 0.35)), 'cableA': Vector((DX + 0.9, 12, 0.8)), 'cableB': Vector((UX - 0.6, 11, 0.4))}
anchors = {}
for f in range(1, NF + 1):
    sc.frame_set(f); anchors[f] = {k: [round(v.x * W, 1), round((1 - v.y) * H, 1)] for k, p in ANCH.items() for v in [world_to_camera_view(sc, cam, p)]}
json.dump(anchors, open(os.path.join(OUT, 'anchors.json'), 'w'))
for f in (FRAMES or range(1, NF + 1)):
    sc.frame_set(f); sc.render.filepath = os.path.join(OUT, f'f{f:04d}.png'); bpy.ops.render.render(write_still=True)
print('DONE', OUT)
