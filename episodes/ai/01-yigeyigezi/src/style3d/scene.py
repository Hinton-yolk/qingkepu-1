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
A = ap.parse_known_args(argv)[0]

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
def world(top, bottom, light='#FFFFFF', light_strength=0.55, halo=None):
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
    if halo:   # halo = (颜色, 方向, 半径)：相机方向上一团很软的亮光（Illumina 产品镜头的背光）
        hc, hd, hr = halo
        dp = nt.nodes.new('ShaderNodeVectorMath'); dp.operation = 'DOT_PRODUCT'
        nt.links.new(tc.outputs['Generated'], dp.inputs[0]); dp.inputs[1].default_value = Vector(hd).normalized()
        mh = nt.nodes.new('ShaderNodeMapRange'); mh.inputs['From Min'].default_value = math.cos(hr); mh.inputs['From Max'].default_value = 1.0
        mh.interpolation_type = 'SMOOTHSTEP'
        nt.links.new(dp.outputs['Value'], mh.inputs['Value'])
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
        nt.links.new(mh.outputs['Result'], mx.inputs['Factor'])
        nt.links.new(ramp.outputs['Color'], mx.inputs['A']); mx.inputs['B'].default_value = hexc(hc)
        nt.links.new(mx.outputs['Result'], bg_cam.inputs['Color'])
    else:
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
ANCH = {}   # 要在 2D 层挂标签的点：名字 → 世界坐标；渲染时投影到屏幕，存成 json

if A.shot == 1:
    # 开头（3D 主视觉，产品镜头）：手机里 AI 正在逐字回复，「去」字块从屏幕里浮出来，下一个位置是黄色「?」
    # v2：按画风草案，产品照 Illumina 的做法（渐变无缝底、轮廓光、缎面金属），去掉杂物，一帧只留底色 + 白 + 一个黄
    world('#B9D4F8', '#8FB6F0', light_strength=0.5, halo=('#EEF5FF', (-0.06, 1.0, -0.06), 0.42))
    area((-4, -6, 6), (0, 0, 0), 800, 6)                       # 主光
    area((6, 4, 1.5), (0.5, 0, 0), 1400, 3, '#FFE2BF')          # 右后方暖色轮廓光：勾出机身侧面
    area((-6, 3, 3), (0, 0, 0), 700, 3, '#DCE8FF')              # 左后方冷色轮廓光
    ph = rbox((2.3, 0.34, 4.7), (0, 0, 0), bevel=0.4, seg=12, mat=satin_metal('#D6DAE4', 0.22))
    bez = rbox((2.2, 0.02, 4.6), (0, -0.17, 0), bevel=0.32, seg=8, mat=candy('#121318', 0.06)); bez.parent = ph
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.185, 0), rotation=(math.pi / 2, 0, 0))
    scr = bpy.context.active_object; scr.scale = (2.06, 4.46, 1)
    bpy.ops.object.transform_apply(scale=True)
    md = scr.modifiers.new('bev', 'BEVEL'); md.width = 0.28; md.segments = 8; md.affect = 'VERTICES'
    if A.ui: assign(scr, image_mat(A.ui, emit_strength=0.9))
    k1 = rbox((0.06, 0.14, 0.55), (1.16, 0, 1.0), bevel=0.025, mat=satin_metal('#C9CEDA'))
    k2 = rbox((0.06, 0.14, 0.35), (1.16, 0, 0.3), bevel=0.025, mat=satin_metal('#C9CEDA'))
    cam_bump = rbox((0.9, 0.08, 0.9), (0.5, 0.2, 1.6), bevel=0.2, mat=satin_metal('#C2C7D3', 0.3))
    for o in (bez, scr, k1, k2, cam_bump): o.parent = ph
    ph.rotation_euler = (math.radians(6), 0, math.radians(-30))
    # 背后一大团很虚的亮光（Illumina 产品镜头的背光）
    token('去', (1.5, -1.7, 0.8), s=0.95, rot=(0.12, 0.0, -0.3))
    rbox((0.8, 0.5, 0.8), (2.3, -1.25, -0.55), bevel=0.13, mat=glass('#FFE07A', rough=0.15), rot=(0.1, 0, -0.4))
    text3d('?', (2.3, -1.25, -0.57), 1.3, emit(YEL, 4.0), extrude=0.06, rot=(math.pi / 2 + 0.1, 0, -0.4))
    token('想', (-2.9, -5.2, -3.6), s=1.1, rot=(0.3, 0.2, 0.5))          # 前景虚化，做景深层次
    ANCH['qu'] = (1.5, -1.7, 0.8 + 0.6); ANCH['q'] = (2.3, -1.25, -0.55 - 0.55)
    camera((1.4, -15.0, 1.6), (0.5, 0, 0.45), lens=48, focus=14.2, fstop=2.0)

elif A.shot == 2:
    # 模型一层层（讲解镜头）。v3：用户 11-19「这三者不是要拼成三种风格」→ 不做扁平图，用同一套材质（Ordinary Folk 质感），
    # 清晰靠 Kurzgesagt 的方法：正面构图、长焦压平、少而大的物体、一物一义、标签。
    world('#DCD5F8', '#C2B7F0', light_strength=0.55, halo=('#F1EDFF', (0.0, 1.0, 0.05), 0.5))
    area((-5, -8, 9), (0, 0, 1), 900, 7)
    area((6, -6, 2), (0, 0, 1), 350, 6)
    area((0, 6, 6), (0, 0, 1), 900, 5, '#FFF1DE')            # 背后轮廓光：给磨砂层板边缘一圈亮边
    import random; random.seed(7)
    nL = 5; zs = [0.45 + k * 0.92 for k in range(nL)]; zball = (zs[2] + zs[3]) / 2
    for k, z in enumerate(zs):
        passed = z < zball
        rbox((4.7, 0.34, 0.62), (0, 0, z), bevel=0.14, seg=6,
             mat=candy('#FFEDB8' if passed else '#FAF8FF', rough=0.35, coat=0.6, sss=0.35))   # 半透的奶白层板（走过的层变暖黄）
        for r in range(2):
            for c in range(10):
                if c in (4, 5): continue                                            # 中间留给「新字」走的路
                v = random.uniform(-1, 1)
                col = PINK if v > 0 else BLUE
                x = -2.05 + c * 0.455 + (0.08 if c > 5 else 0) - (0.08 if c < 4 else 0)
                rbox((0.34, 0.1, 0.2), (x, -0.2, z + 0.13 - r * 0.26), bevel=0.05, seg=3,
                     mat=candy(col, rough=0.22 + 0.35 * (1 - abs(v)), sss=0.1))        # 参数：粉正蓝负的糖果小方块
        bpy.ops.mesh.primitive_torus_add(major_radius=0.2, minor_radius=0.03, location=(0, -0.2, z), rotation=(math.pi / 2, 0, 0))
        t = bpy.context.active_object; smooth(t); assign(t, satin_metal('#BFB6E6', 0.3))
    # 竖向的路：一根细玻璃管穿过各层；走过的一段发黄光
    def rod(z0, z1, r, mat):
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=z1 - z0, location=(0, -0.2, (z0 + z1) / 2), vertices=32)
        o = bpy.context.active_object; smooth(o); assign(o, mat)
    rod(zs[0] - 0.8, zs[-1] + 0.6, 0.028, candy('#E9E5FA', 0.3))
    rod(zs[0] - 0.8, zball, 0.032, emit(YEL, 2.2))
    sphere(0.15, (0, -0.2, zball), emit(YEL, 7.0))
    sphere(0.25, (0, -0.2, zball), glass('#FFE58A', 0.2))
    # 一排字块 + 黄色「?」玻璃块
    ry = -0.55; step = 0.72
    xs0 = -2.5 * step
    for k, ch in enumerate('周末我想去'):
        token(ch, (xs0 + k * step - 0.36 + 0.36, -0.6, ry), s=0.6)
    qx = xs0 + 5 * step
    rbox((0.6, 0.37, 0.6), (qx, -0.6, ry), bevel=0.1, mat=glass('#FFE07A', 0.15))
    text3d('?', (qx, -0.8, ry), 0.95, emit(YEL, 4.0), extrude=0.04, rot=(math.pi / 2, 0, 0))
    # 出口：从最上面一层绕到「?」（一根细磨砂管）
    pts = [(0, -0.2, zs[-1] + 0.6), (0, -0.2, zs[-1] + 0.85), (2.7, -0.2, zs[-1] + 0.85), (2.7, -0.2, ry + 0.7), (qx, -0.6, ry + 0.7), (qx, -0.6, ry + 0.33)]
    cu = bpy.data.curves.new('pipe', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.03; cu.bevel_resolution = 3
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, p_ in enumerate(pts): sp.points[i].co = (*p_, 1)
    po = bpy.data.objects.new('pipe', cu); bpy.context.collection.objects.link(po); cu.materials.append(glass('#D9D2FF', 0.25))
    ANCH['model'] = (0, 0, zs[-1] + 1.3); ANCH['q'] = (qx - 0.75, -0.6, ry + 0.7)
    camera((1.6, -32, 8.2), (0, 0, 0.9), lens=100, focus=32.6, fstop=5.6)

elif A.shot == 3:
    # 分叉：句子是一条玻璃带，在「去」后面一分为二，上面一条接「海边看日落」，下面一条接「睡个懒觉」
    world('#FFCFB8', '#FFB394')
    studio(key=850, fill=280, rim=750)
    s = 0.56; step = 0.66; yaw = -0.35
    stem = [(-4.6, 0, 0), (-3.0, 0, 0), (-1.2, 0, 0), (0.0, 0, 0)]
    up = [(0.0, 0, 0), (1.0, 0, 0.7), (2.0, 0, 2.5), (3.4, 0, 3.1), (5.4, 0, 3.15)]
    dn = [(0.0, 0, 0), (1.0, 0, -0.7), (2.0, 0, -2.5), (3.4, 0, -3.1), (5.4, 0, -3.15)]
    ribbon(stem, 0.9, gradient_glass('#FFF4EC', '#FFE6D6', 'X', 0.12, -4.6, 0), thick=0.06)
    ribbon(up, 0.9, gradient_glass('#FFE6D6', '#FFF4EC', 'X', 0.12, 0, 5.6), thick=0.06)
    ribbon(dn, 0.9, gradient_glass('#FFE6D6', '#FFF4EC', 'X', 0.12, 0, 5.6), thick=0.06)
    for k, ch in enumerate('周末我想去'):
        token(ch, (-4.2 + k * step, -0.05, s / 2 + 0.05), s=s, rot=(0, 0, yaw))
    def zpath(x, z1):
        u = max(0.0, min(1.0, (x - 0.4) / 2.4)); u = u * u * (3 - 2 * u); return z1 * u
    def branch(chars, z1):
        for k, ch in enumerate(chars):
            x = 2.3 + k * step
            body = '#FFD45A' if k == 0 else '#FBF8F2'
            token(ch, (x, -0.05, zpath(x, z1) + s / 2 + 0.05), s=s, body=body, rot=(0, 0, yaw))
    branch('海边看日落', 3.12)
    branch('睡个懒觉', -3.12)
    ANCH['zhou'] = (-4.2 - s / 2, -0.05, s / 2); ANCH['luo'] = (2.3 + 4 * step + s / 2, -0.05, 3.12 + s); ANCH['jue'] = (2.3 + 3 * step + s / 2, -0.05, -3.12 + s)
    # 分叉点：一颗黄球
    sphere(0.2, (0.3, -0.05, 0.45), emit(YEL, 6))
    sphere(0.34, (0.3, -0.05, 0.45), glass('#FFE58A', 0.2))
    camera((-9.85, -10.17, 1.4), (-0.05, 0.23, -0.35), lens=31.5, focus=14.0, fstop=2.8)

bpy.ops.render.render(write_still=True)
if ANCH:
    import json
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    out = {k: [round(c, 4) for c in world_to_camera_view(sc, sc.camera, Vector(v))[:2]] for k, v in ANCH.items()}
    json.dump(out, open(A.out.rsplit('.', 1)[0] + '_anchors.json', 'w'))
