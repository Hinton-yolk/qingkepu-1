# AI 系列新画风样张（2026-11-19）：风格化 2.5D 科学动画，主参考 Ordinary Folk《Equilibrium》。
# 用法：blender -b -P scene.py -- --shot 1 --out a.png --scale 0.5 --samples 64 --font NotoSansSC-Bold.otf
# 只出 3D 层；大字问题和字幕由 overlay.py 叠在 2D 层（字不进 3D，保证可读）。
import bpy, bmesh, math, sys, argparse
from mathutils import Vector, Euler, Matrix

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument('--shot', type=int, default=1)
ap.add_argument('--out', default='/tmp/shot.png')
ap.add_argument('--scale', type=float, default=0.5)
ap.add_argument('--samples', type=int, default=64)
ap.add_argument('--font', default='')
ap.add_argument('--ui', default='')          # 手机屏幕贴图（overlay.py 先生成）
A = ap.parse_args(argv)

def hexc(h, a=1.0):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    # sRGB → linear
    return tuple(((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c) + (a,)

# ---------------- 场景与渲染 ----------------
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = A.samples
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 10
sc.cycles.transmission_bounces = 10
sc.cycles.glossy_bounces = 6
sc.cycles.caustics_reflective = False
sc.cycles.caustics_refractive = False
sc.cycles.blur_glossy = 1.0
sc.render.resolution_x = 1080; sc.render.resolution_y = 1920
sc.render.resolution_percentage = int(A.scale * 100)
sc.render.image_settings.file_format = 'PNG'
sc.render.filepath = A.out
sc.view_settings.view_transform = 'Standard'   # 背景色要原样出来
sc.view_settings.look = 'None'
sc.render.film_transparent = False

# ---------------- 材质 ----------------
def bsdf_mat(name, **kw):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes['Principled BSDF']
    for k, v in kw.items():
        p.inputs[k].default_value = v
    return m, p

def candy(col, rough=0.22, coat=1.0, sss=0.0):
    m, p = bsdf_mat('candy', **{'Base Color': hexc(col), 'Roughness': rough,
                               'Coat Weight': coat, 'Coat Roughness': 0.04,
                               'Subsurface Weight': sss, 'Subsurface Scale': 0.05})
    return m

def glass(col, rough=0.08, ior=1.45, tint_density=1.0):
    m, p = bsdf_mat('glass', **{'Base Color': hexc(col), 'Roughness': rough,
                               'Transmission Weight': 1.0, 'IOR': ior,
                               'Coat Weight': 0.6, 'Coat Roughness': 0.03})
    return m

def satin_metal(col, rough=0.32):
    m, p = bsdf_mat('metal', **{'Base Color': hexc(col), 'Metallic': 1.0, 'Roughness': rough,
                               'Anisotropic': 0.3})
    return m

def emit(col, strength=4.0):
    m, p = bsdf_mat('emit', **{'Base Color': hexc(col), 'Emission Color': hexc(col),
                              'Emission Strength': strength, 'Roughness': 0.2})
    return m

def gradient_glass(c1, c2, axis='X', rough=0.12, lo=-1, hi=1):
    """同一个物体从一种颜色渐变到另一种（Equilibrium 的彩色玻璃）"""
    m = bpy.data.materials.new('gglass'); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes['Principled BSDF']
    p.inputs['Transmission Weight'].default_value = 1.0
    p.inputs['Roughness'].default_value = rough
    p.inputs['Coat Weight'].default_value = 0.6
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    mr = nt.nodes.new('ShaderNodeMapRange'); ramp = nt.nodes.new('ShaderNodeValToRGB')
    mr.inputs['From Min'].default_value = lo; mr.inputs['From Max'].default_value = hi
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    nt.links.new(sep.outputs[axis], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], ramp.inputs['Fac'])
    ramp.color_ramp.elements[0].color = hexc(c1); ramp.color_ramp.elements[1].color = hexc(c2)
    nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    return m

def image_mat(path, rough=0.05, emit_strength=1.0):
    """手机屏幕：贴图自发光 + 玻璃面高光"""
    m = bpy.data.materials.new('screen'); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = bpy.data.images.load(path)
    tex.extension = 'CLIP'
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nt.links.new(tc.outputs['UV'], tex.inputs['Vector'])
    nt.links.new(tex.outputs['Color'], p.inputs['Base Color'])
    nt.links.new(tex.outputs['Color'], p.inputs['Emission Color'])
    p.inputs['Emission Strength'].default_value = emit_strength
    p.inputs['Roughness'].default_value = rough
    p.inputs['Coat Weight'].default_value = 1.0
    p.inputs['Coat Roughness'].default_value = 0.02
    return m

# ---------------- 几何 ----------------
def assign(ob, m):
    ob.data.materials.clear(); ob.data.materials.append(m); return ob

def smooth(ob):
    for poly in ob.data.polygons: poly.use_smooth = True

def rbox(size, loc=(0, 0, 0), bevel=0.08, seg=6, mat=None, rot=(0, 0, 0)):
    """圆角方块：网格直接按尺寸建，不用 transform_apply（避免影响别的物体）"""
    me = bpy.data.meshes.new('box'); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('box', me); bpy.context.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler = rot
    md = ob.modifiers.new('bev', 'BEVEL'); md.width = min(bevel, min(size) * 0.49); md.segments = seg
    md.limit_method = 'NONE'
    smooth(ob)
    if mat: assign(ob, mat)
    return ob

def sphere(r, loc, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=64, ring_count=32)
    ob = bpy.context.active_object; smooth(ob); return assign(ob, mat)

def text3d(body, loc, size, mat, extrude=0.02, rot=(0, 0, 0)):
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = body
    if A.font: cu.font = bpy.data.fonts.load(A.font)
    cu.size = size; cu.extrude = extrude; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    cu.bevel_depth = extrude * 0.25; cu.bevel_resolution = 2
    ob = bpy.data.objects.new('t', cu); bpy.context.collection.objects.link(ob)
    ob.location = loc; ob.rotation_euler = rot
    cu.materials.append(mat); return ob

def token(ch, loc, s=0.62, body='#FBF8F2', ink='#1E2440', rot=(0, 0, 0), extra=None):
    """字块：糖果白方块 + 凸起的字（字块符号，沿用符号表）"""
    ob = rbox((s, s * 0.62, s), loc, bevel=s * 0.16, mat=candy(body, rough=0.3, sss=0.15), rot=rot)
    t = text3d(ch, (0, 0, 0), s * 1.75, candy(ink, rough=0.35), extrude=0.012)   # CJK 字体在 Blender 里实际字高约为 size 的 1/3
    M = Matrix.LocRotScale(Vector(loc), Euler(rot).to_quaternion(), None)
    t.matrix_world = M @ Matrix.Translation((0, -s * 0.31 - 0.004, -s * 0.03)) @ Euler((math.pi / 2, 0, 0)).to_matrix().to_4x4()
    return ob

def ribbon(points, width, mat, thick=0.03, twist=None):
    """一条有厚度的带子，沿给定路径（Equilibrium 的卷带）"""
    cu = bpy.data.curves.new('rib', 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(points) - 1)
    for i, p in enumerate(points):
        bp = sp.bezier_points[i]; bp.co = p
        bp.handle_left_type = bp.handle_right_type = 'AUTO'
        if twist: bp.tilt = twist[i]
    cu.extrude = width / 2; cu.bevel_depth = 0
    cu.resolution_u = 32; cu.twist_mode = 'MINIMUM'
    ob = bpy.data.objects.new('rib', cu); bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob; ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    ob = bpy.context.active_object
    md = ob.modifiers.new('sol', 'SOLIDIFY'); md.thickness = thick; md.offset = 0
    md2 = ob.modifiers.new('bev', 'BEVEL'); md2.width = thick * 0.45; md2.segments = 3
    smooth(ob); assign(ob, mat); return ob

# ---------------- 世界：相机看到纯粉彩底色（带一点竖向渐变），照明用柔和的白棚灯 ----------------
def world(top, bottom, light='#FFFFFF', light_strength=0.55):
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    lp = nt.nodes.new('ShaderNodeLightPath')
    mix = nt.nodes.new('ShaderNodeMixShader')
    bg_light = nt.nodes.new('ShaderNodeBackground'); bg_light.inputs['Color'].default_value = hexc(light)
    bg_light.inputs['Strength'].default_value = light_strength
    bg_cam = nt.nodes.new('ShaderNodeBackground'); bg_cam.inputs['Strength'].default_value = 1.0
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -0.35; mr.inputs['From Max'].default_value = 0.35
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = hexc(bottom); ramp.color_ramp.elements[1].color = hexc(top)
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])
    nt.links.new(sep.outputs['Z'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg_cam.inputs['Color'])
    # 透射 / 反射看到的也是底色（玻璃里透出底色），漫反射照明用白棚
    is_vis = nt.nodes.new('ShaderNodeMath'); is_vis.operation = 'MAXIMUM'
    nt.links.new(lp.outputs['Is Camera Ray'], is_vis.inputs[0])
    nt.links.new(lp.outputs['Is Transmission Ray'], is_vis.inputs[1])
    nt.links.new(is_vis.outputs[0], mix.inputs['Fac'])
    nt.links.new(bg_light.outputs[0], mix.inputs[1]); nt.links.new(bg_cam.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])

def area(loc, target, energy, size, col='#FFFFFF'):
    ld = bpy.data.lights.new('a', 'AREA'); ld.energy = energy; ld.size = size; ld.color = hexc(col)[:3]
    ob = bpy.data.objects.new('a', ld); bpy.context.collection.objects.link(ob); ob.location = loc
    d = Vector(target) - Vector(loc); ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return ob

def studio(key=900, fill=300, rim=700):
    area((-4, -5, 6), (0, 0, 0), key, 6)          # 主光：左上前方的大柔光
    area((5, -3, 2), (0, 0, 0), fill, 6)           # 补光
    area((1, 6, 4), (0, 0, 0), rim, 4)             # 轮廓光：给糖果和玻璃边缘一圈亮边

def camera(loc, target, lens=85, focus=None, fstop=2.8):
    cd = bpy.data.cameras.new('cam'); cd.lens = lens
    cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 36
    ob = bpy.data.objects.new('cam', cd); bpy.context.collection.objects.link(ob)
    ob.location = loc; d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler(); sc.camera = ob
    cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
    cd.dof.focus_distance = focus if focus else d.length
    return ob

# 颜色（沿用符号表的分工：粉正蓝负 = 参数；黄 = 当前 / 答案；绿 = 算）
PINK, BLUE, YEL, GRN = '#FF6F96', '#4A8DFF', '#FFC93C', '#36D27E'

# =====================================================================
if A.shot == 1:
    # 开头：手机里 AI 正在逐字回复，「去」字块从屏幕里浮出来，下一个位置是黄色「?」
    world('#BFD8F6', '#A9C8F0')
    studio()
    ph = rbox((2.3, 0.3, 4.7), (0, 0, 0), bevel=0.36, seg=10, mat=satin_metal('#DCE0EA', 0.25))
    bez = rbox((2.2, 0.02, 4.6), (0, -0.15, 0), bevel=0.3, seg=8, mat=candy('#15171F', 0.08)); bez.parent = ph
    # 屏幕：略小一圈、贴在正面
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.165, 0), rotation=(math.pi / 2, 0, 0))
    scr = bpy.context.active_object; scr.scale = (2.04, 4.44, 1)
    bpy.ops.object.transform_apply(scale=True)
    md = scr.modifiers.new('bev', 'BEVEL'); md.width = 0.28; md.segments = 8; md.affect = 'VERTICES'
    if A.ui: assign(scr, image_mat(A.ui, emit_strength=0.85))
    # 侧键（产品细节）
    k1 = rbox((0.05, 0.12, 0.5), (1.16, 0, 0.9), bevel=0.02, mat=satin_metal('#D9DCE6'))
    k2 = rbox((0.05, 0.12, 0.8), (-1.16, 0, 1.0), bevel=0.02, mat=satin_metal('#D9DCE6'))
    for o in (scr, k1, k2): o.parent = ph
    ph.rotation_euler = (math.radians(4), 0, math.radians(-24))
    # 浮出屏幕的字块「去」，和后面的黄色「?」玻璃块
    token('去', (1.45, -1.6, 0.75), s=0.95, rot=(0.12, 0.0, -0.28))
    q = rbox((0.8, 0.5, 0.8), (2.35, -1.2, -0.45), bevel=0.13, mat=glass('#FFE07A', rough=0.18), rot=(0.1, 0, -0.4))
    text3d('?', (2.35, -1.2, -0.47), 1.3, emit(YEL, 4.0), extrude=0.06, rot=(math.pi / 2 + 0.1, 0, -0.4))
    # 前景虚化的字块（景深层次）
    token('想', (-2.6, -5.0, -3.4), s=1.1, rot=(0.3, 0.2, 0.5))
    token('周', (3.3, -2.5, -2.9), s=0.7, rot=(-0.3, 0.3, -0.6))
    sphere(0.2, (-1.7, -0.8, 2.3), candy(YEL, 0.2))
    sphere(0.12, (2.6, -0.6, 1.2), glass('#FFFFFF', 0.05))
    for (x, y, z, r, c) in [(-3.6, 6, 2.6, 2.0, '#E4EEFC'), (4.2, 7, -2.4, 2.6, '#EAF2FD')]:
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=0.25, location=(x, y, z), rotation=(math.pi / 2, 0, 0), vertices=96)
        o = bpy.context.active_object; smooth(o); assign(o, candy(c, 0.5, coat=0.5, sss=0.3))
    camera((1.4, -15.0, 1.6), (0.5, 0, 0.45), lens=48, focus=14.2, fstop=2.0)

elif A.shot == 2:
    # 模型一层层：一摞玻璃层板，每层顶面铺粉 / 蓝参数方块；新字（黄色发光球）正往上穿过各层
    world('#D6CEF6', '#C3B8F0')
    studio(key=800, fill=260, rim=800)
    layers = 5; gap = 0.8; n = 7; cell = 0.32
    import random; random.seed(7)
    for L in range(layers):
        z = -1.2 + L * gap
        passed = L <= 2
        rbox((n * cell + 0.3, n * cell + 0.3, 0.1), (0, 0, z), bevel=0.05,
             mat=candy('#F4F2FB' if not passed else '#FFE7A6', rough=0.4, sss=0.3))
        for i in range(n):
            for j in range(n):
                v = random.uniform(-1, 1)
                if i == (n - 1) // 2 and j == (n - 1) // 2: continue   # 中间留一个洞：新字从这里穿上去
                col = PINK if v > 0 else BLUE
                h = 0.04 + abs(v) * 0.16
                c = rbox((cell * 0.8, cell * 0.8, h), ((i - (n - 1) / 2) * cell, (j - (n - 1) / 2) * cell, z + 0.05 + h / 2),
                         bevel=0.03, seg=3, mat=candy(col, rough=0.25 + 0.3 * (1 - abs(v))))
    # 黄色发光球：新字正在穿过第 3 层
    sphere(0.22, (0.0, 0.0, -1.2 + 2.55 * gap), emit(YEL, 8.0))
    sphere(0.36, (0.0, 0.0, -1.2 + 2.55 * gap), glass('#FFE58A', 0.2))
    # 穿过的路径：一串淡黄的玻璃圆环（Equilibrium 的「球穿过环」）
    for L in range(3):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.42, minor_radius=0.035, location=(0, 0, -1.2 + L * gap + 0.3))
        t = bpy.context.active_object; smooth(t); assign(t, glass('#FFE58A', 0.1))
    # 下方一排字块，从底层送进模型
    for k, ch in enumerate('周末我想去'):
        token(ch, (-1.75 + k * 0.6, -1.2, -2.3), s=0.5, rot=(0, 0, 0.55))
    rbox((0.5, 0.31, 0.5), (-1.75 + 5 * 0.6, -1.2, -2.3), bevel=0.09, mat=glass('#FFE07A', 0.15), rot=(0, 0, 0.55))
    text3d('?', (-1.75 + 5 * 0.6 + 0.12, -1.38, -2.3), 0.8, emit(YEL, 4.0), extrude=0.04, rot=(math.pi / 2, 0, 0.55))
    camera((7.2, -11.0, 1.8), (0.0, -0.3, -0.85), lens=50, focus=13.1, fstop=3.5)

elif A.shot == 3:
    # 分叉：句子是一条玻璃带，在「去」后面一分为二，上面一条接「海边看日落」，下面一条接「睡个懒觉」
    world('#FFE2D2', '#FFD0BE')
    studio(key=850, fill=280, rim=750)
    s = 0.56; step = 0.66; yaw = -0.35
    stem = [(-4.6, 0, 0), (-3.0, 0, 0), (-1.2, 0, 0), (0.0, 0, 0)]
    up = [(0.0, 0, 0), (1.0, 0, 0.3), (2.0, 0, 1.1), (3.4, 0, 1.4), (5.6, 0, 1.45)]
    dn = [(0.0, 0, 0), (1.0, 0, -0.3), (2.0, 0, -1.1), (3.4, 0, -1.4), (5.6, 0, -1.45)]
    ribbon(stem, 0.9, gradient_glass('#9CC6FF', '#C9B8FF', 'X', 0.1, -4.6, 0), thick=0.05)
    ribbon(up, 0.9, gradient_glass('#C9B8FF', '#7FD8FF', 'X', 0.1, 0, 5.6), thick=0.05)
    ribbon(dn, 0.9, gradient_glass('#C9B8FF', '#FFB0C8', 'X', 0.1, 0, 5.6), thick=0.05)
    for k, ch in enumerate('周末我想去'):
        token(ch, (-4.2 + k * step, -0.05, s / 2 + 0.05), s=s, rot=(0, 0, yaw))
    def zpath(x, z1):
        u = max(0.0, min(1.0, (x - 0.3) / 2.2)); u = u * u * (3 - 2 * u); return z1 * u
    def branch(chars, z1):
        for k, ch in enumerate(chars):
            x = 2.3 + k * step
            body = '#FFD45A' if k == 0 else '#FBF8F2'
            token(ch, (x, -0.05, zpath(x, z1) + s / 2 + 0.05), s=s, body=body, rot=(0, 0, yaw))
    branch('海边看日落', 1.42)
    branch('睡个懒觉', -1.42)
    # 分叉点：一颗黄球
    sphere(0.2, (0.3, -0.05, 0.45), emit(YEL, 6))
    sphere(0.34, (0.3, -0.05, 0.45), glass('#FFE58A', 0.2))
    camera((-8.6, -10.6, 3.0), (0.0, 0, -0.35), lens=33, focus=13.9, fstop=2.8)

bpy.ops.render.render(write_still=True)
