# 一语道破 · Blender 测试镜头二：硅光波导是怎么刻出来的（2026-11-09，Branch Education 式层块工艺）
# 竖屏 14 秒。SOI 层块（硅衬底 / 埋氧层 / 顶层硅）→ 旋涂光刻胶 → 掩模滑入、紫外光照射（镜头跟着光往下推）→ 显影
# → 等离子刻蚀，停在埋氧层 → 去胶 → 镜头绕到正面，光从刻好的硅波导端面射出来。
# 全部程序化建模；兼容 Blender 4.5 与 5.x。层厚按对数压缩（片中角注「厚度示意」）。
# 用法：blender -b --python-exit-code 1 --python shot_waveguide.py -- <输出目录> <宽> <高> <采样> [--gpu] [--eevee] [--fps N] [--video] [帧号…]
#       --eevee：用实时引擎 EEVEE 渲（快很多，画面略简化）；采样数即 EEVEE 的抗锯齿采样
import bpy, bmesh, math, sys, json, os
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

args = sys.argv[sys.argv.index('--') + 1:]; OUT, W, H, SAMP = args[0], int(args[1]), int(args[2]), int(args[3]); rest = args[4:]
GPU = '--gpu' in rest; EEVEE = '--eevee' in rest; VIDEO = '--video' in rest; FPS = int(rest[rest.index('--fps') + 1]) if '--fps' in rest else 30
FRAMES = [int(a) for i, a in enumerate(rest) if a.isdigit() and not (i > 0 and rest[i - 1] == '--fps')]
DUR = 14.0; NF = round(DUR * FPS)
F = lambda sec: 1 + round(sec * FPS)                       # 秒 → 帧
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; os.makedirs(OUT, exist_ok=True)
print('BLENDER_VERSION', bpy.app.version_string)

# ---------- 版本兼容 ----------
def fcurves_of(o):
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
def set_fmt(fmt):
    ims = sc.render.image_settings
    if hasattr(ims, 'media_type'): ims.media_type = 'VIDEO' if fmt == 'FFMPEG' else 'IMAGE'
    ims.file_format = fmt
def ease_all(o, kind='BEZIER'):
    for fc in fcurves_of(o):
        for kp in fc.keyframe_points: kp.interpolation = kind; kp.easing = 'EASE_IN_OUT'

# ---------- 材质 ----------
def mat_pbr(name, col, metal=0.0, rough=0.5, transm=0.0, ior=1.45, alpha=1.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    b.inputs['Transmission Weight'].default_value = transm; b.inputs['IOR'].default_value = ior; b.inputs['Alpha'].default_value = alpha; b.inputs['Coat Weight'].default_value = coat
    return m
def mat_glow(name, col, strength, transparent=0.0):
    """发光材质；transparent > 0 时和透明混合（光柱用）。返回材质和强度插口（可做关键帧）"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    for n in list(N): N.remove(n)
    out = N.new('ShaderNodeOutputMaterial'); em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*col, 1); em.inputs['Strength'].default_value = strength
    if transparent > 0:
        tr = N.new('ShaderNodeBsdfTransparent'); mix = N.new('ShaderNodeMixShader'); mix.inputs['Fac'].default_value = 1 - transparent
        L.new(tr.outputs['BSDF'], mix.inputs[1]); L.new(em.outputs['Emission'], mix.inputs[2]); L.new(mix.outputs['Shader'], out.inputs['Surface'])
    else: L.new(em.outputs['Emission'], out.inputs['Surface'])
    return m, em.inputs['Strength']
M = dict(
    sub=mat_pbr('si_substrate', (0.13, 0.15, 0.2), 0.3, 0.45),
    box=mat_pbr('buried_oxide', (0.55, 0.68, 0.84), 0.0, 0.35, coat=0.4),
    si=mat_pbr('si_top', (0.3, 0.34, 0.46), 0.55, 0.28),
    resist=mat_pbr('resist', (0.42, 0.16, 0.72), 0.0, 0.22, coat=0.7),
    glass=mat_pbr('mask_glass', (0.85, 0.92, 1.0), 0.0, 0.05, alpha=0.22, coat=1.0),
    chrome=mat_pbr('mask_chrome', (0.78, 0.8, 0.84), 1.0, 0.18),
    floor=mat_pbr('floor', (0.07, 0.075, 0.09), 0.0, 0.85))
M['resist_exp'] = mat_pbr('resist_exposed', (0.42, 0.16, 0.72), 0.0, 0.22, coat=0.7)          # 被照到的胶：照射时发紫光
_b = M['resist_exp'].node_tree.nodes['Principled BSDF']; _b.inputs['Emission Color'].default_value = (0.65, 0.45, 1.0, 1); EXP_GLOW = _b.inputs['Emission Strength']
M['uv'], UV_STR = mat_glow('uv_light', (0.62, 0.45, 1.0), 0.0, transparent=0.95)
M['ray'], RAY_STR = mat_glow('uv_ray', (0.7, 0.55, 1.0), 0.0)
M['ion'], _ = mat_glow('plasma_ion', (1.0, 0.45, 0.3), 12.0)
M['core'], CORE_STR = mat_glow('waveguide_light', (0.25, 0.85, 0.78), 0.0)
def mat_beam(name, col):
    """出光锥：边缘和远端渐隐的发光（正对相机处最亮，掠射边缘透明；沿光路由亮到暗）"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    for n in list(N): N.remove(n)
    out = N.new('ShaderNodeOutputMaterial'); em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*col, 1)
    tr = N.new('ShaderNodeBsdfTransparent'); mix = N.new('ShaderNodeMixShader')
    lw = N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5
    inv = N.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.use_clamp = True; inv.inputs[0].default_value = 1.0; L.new(lw.outputs['Facing'], inv.inputs[1])
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Generated'], sep.inputs[0])
    along = N.new('ShaderNodeMath'); along.operation = 'SUBTRACT'; along.inputs[0].default_value = 1.0; L.new(sep.outputs['Z'], along.inputs[1])
    pw = N.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 1.6; L.new(along.outputs[0], pw.inputs[0])
    fac = N.new('ShaderNodeMath'); fac.operation = 'MULTIPLY'; fac.use_clamp = True;   # 必须夹到 0–1：背面朝向值越界会让透明权重变负，出现黑影
    L.new(inv.outputs[0], fac.inputs[0]); L.new(pw.outputs[0], fac.inputs[1])
    L.new(fac.outputs[0], mix.inputs['Fac']); L.new(tr.outputs['BSDF'], mix.inputs[1]); L.new(em.outputs['Emission'], mix.inputs[2]); L.new(mix.outputs['Shader'], out.inputs['Surface'])
    return m, em.inputs['Strength']
M['exit'], EXIT_STR = mat_beam('exit_beam', (0.45, 1.0, 0.92))
M['ridge'] = mat_pbr('si_ridge', (0.3, 0.34, 0.46), 0.55, 0.28)                                   # 波导条单独一份：导光时自己发青光
_b = M['ridge'].node_tree.nodes['Principled BSDF']; _b.inputs['Emission Color'].default_value = (0.25, 0.85, 0.78, 1); RIDGE_GLOW = _b.inputs['Emission Strength']

# ---------- 几何 ----------
def box(name, x0, x1, y0, y1, z0, z1, mat, origin=None, bevel=0.015):
    """轴对齐方块；origin 是物体原点（缩放围绕它），默认在底面中心"""
    ox, oy, oz = origin if origin else ((x0 + x1) / 2, (y0 + y1) / 2, z0)
    bm = bmesh.new(); v = [bm.verts.new((x - ox, y - oy, z - oz)) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)): bm.faces.new([v[i] for i in f])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); o.location = (ox, oy, oz)
    o.data.materials.append(mat)
    if bevel: md = o.modifiers.new('bev', 'BEVEL'); md.width = bevel; md.segments = 2
    return o
def key(o, path, frame, value, idx=None):
    if idx is None: setattr(o, path, value); o.keyframe_insert(path, frame=frame)
    else: getattr(o, path)[idx] = value; o.keyframe_insert(path, index=idx, frame=frame)

# 尺寸（场景单位；层厚按对数压缩）：块 5.2 × 7.2，硅衬底 1.6，埋氧层 0.9，顶层硅 0.35，胶 0.22，波导宽 1.0
X0, X1, Y0, Y1 = -2.6, 2.6, -3.6, 3.6
Z_SUB, Z_BOX, Z_SI, Z_RES = 1.6, 0.9, 0.35, 0.22
zb = Z_SUB; zs = zb + Z_BOX; zt = zs + Z_SI; zr = zt + Z_RES          # 各层顶面高度
WG = 0.5                                                              # 波导半宽
box('substrate', X0, X1, Y0, Y1, 0, zb, M['sub'])
box('box_oxide', X0, X1, Y0, Y1, zb, zs, M['box'])
ridge = box('si_ridge', -WG, WG, Y0, Y1, zs, zt, M['ridge'], bevel=0.0)   # 三块拼接处不倒角：刻之前看不出缝
siL = box('si_left', X0, -WG, Y0, Y1, zs, zt, M['si'], bevel=0.0)
siR = box('si_right', WG, X1, Y0, Y1, zs, zt, M['si'], bevel=0.0)
# 地面（暗，衬托）
bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, -0.01)); fl = bpy.context.object; fl.data.materials.append(M['floor'])

# ---------- 时间轴（秒） ----------
T = dict(coat0=1.0, coat1=2.6, mask0=2.8, mask1=3.4, uv0=3.5, uv1=4.9, dev0=5.3, dev1=6.4, etch0=6.6, etch1=8.6, strip0=9.0, strip1=9.8,
         cam_front0=10.0, cam_front1=11.4, light0=11.4, light1=12.6, exit0=12.4)

# 1) 旋涂：一滴胶落到中心，然后从中心向两边铺开（三块：中间 + 左右）
drop_m = M['resist']; bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(0, 0, zt + 3.0), segments=24, ring_count=12); drop = bpy.context.object; drop.data.materials.append(drop_m)
bpy.ops.object.shade_smooth()
key(drop, 'location', F(T['coat0']), (0, 0, zt + 3.0)); key(drop, 'location', F(T['coat0'] + 0.4), (0, 0, zt + 0.15)); ease_all(drop)
key(drop, 'scale', F(T['coat0'] + 0.35), (1, 1, 1)); key(drop, 'scale', F(T['coat0'] + 0.55), (1.6, 1.6, 0.05))
key(drop, 'hide_render', 1, True); key(drop, 'hide_render', F(T['coat0']), False); key(drop, 'hide_render', F(T['coat0'] + 0.6), True)
resC = box('resist_mid', -WG, WG, Y0, Y1, zt, zr, M['resist'], origin=(0, 0, zt), bevel=0.0)
resL = box('resist_left', X0, -WG, Y0, Y1, zt, zr, M['resist_exp'], origin=(-WG, 0, zt), bevel=0.0)       # 原点在内侧边：向外铺开
resR = box('resist_right', WG, X1, Y0, Y1, zt, zr, M['resist_exp'], origin=(WG, 0, zt), bevel=0.0)
c0, c1 = F(T['coat0'] + 0.45), F(T['coat1'])
for o in (resC, resL, resR): key(o, 'scale', 1, (0.001, 0.02, 1)); key(o, 'scale', c0, (0.001, 0.02, 1)); key(o, 'hide_render', 1, True); key(o, 'hide_render', c0, False)
key(resC, 'scale', c0 + 3, (1, 0.25, 1)); key(resC, 'scale', c1, (1, 1, 1))
for o in (resL, resR): key(o, 'scale', c0 + 3, (0.05, 0.25, 1)); key(o, 'scale', c1, (1, 1, 1))
for o in (resC, resL, resR): ease_all(o)

# 2) 掩模从右侧滑入：玻璃板 + 中间一条铬（挡住波导那一条），紫外光从上方照下来
MZ = zr + 2.0
mglass = box('mask_glass', X0 - 0.3, X1 + 0.3, Y0 - 0.3, Y1 + 0.3, MZ, MZ + 0.12, M['glass'], bevel=0.03)
mchrome = box('mask_chrome', -WG, WG, Y0 - 0.3, Y1 + 0.3, MZ - 0.02, MZ, M['chrome'], bevel=0.0)
for o in (mglass, mchrome):
    base = Vector(o.location); off = base + Vector((14, 0, 0))          # 先记下原位：key() 会改 location
    key(o, 'location', 1, off); key(o, 'location', F(T['mask0']), off); key(o, 'location', F(T['mask1']), base)
    key(o, 'location', F(T['dev0'] - 0.3), base); key(o, 'location', F(T['dev0'] + 0.3), base + Vector((0, 0, 9))); ease_all(o)
uvL = box('uv_left', X0, -WG, Y0, Y1, zr, MZ - 0.02, M['uv'], bevel=0.0)
uvR = box('uv_right', WG, X1, Y0, Y1, zr, MZ - 0.02, M['uv'], bevel=0.0)
for o in (uvL, uvR): key(o, 'hide_render', 1, True); key(o, 'hide_render', F(T['uv0']), False); key(o, 'hide_render', F(T['uv1'] + 0.1), True)
def key_socket(sock, frame, val):
    sock.default_value = val; sock.keyframe_insert('default_value', frame=frame)
key_socket(UV_STR, F(T['uv0']), 0.0); key_socket(UV_STR, F(T['uv0'] + 0.3), 0.6); key_socket(UV_STR, F(T['uv1'] - 0.3), 0.6); key_socket(UV_STR, F(T['uv1']), 0.0)
# 紫外光线：两侧一排排细光线从掩模射到胶面（中间铬条下面没有）
for side in (-1, 1):
    for i in range(4):
        for j in range(6):
            x = side * (WG + 0.35 + i * (X1 - WG - 0.6) / 3); y = Y0 + 0.5 + j * (Y1 - Y0 - 1.0) / 5
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.018, depth=MZ - zr, location=(x, y, (MZ + zr) / 2)); r = bpy.context.object; r.data.materials.append(M['ray'])
            r.scale = (1, 1, 0.001); r.location.z = MZ
            key(r, 'hide_render', 1, True); key(r, 'hide_render', F(T['uv0']), False); key(r, 'hide_render', F(T['uv1'] + 0.1), True)
            d = 0.04 * (i + j)                                       # 依次射下
            key(r, 'scale', F(T['uv0'] + d), (1, 1, 0.001)); key(r, 'location', F(T['uv0'] + d), (x, y, MZ))
            key(r, 'scale', F(T['uv0'] + d + 0.35), (1, 1, 1)); key(r, 'location', F(T['uv0'] + d + 0.35), (x, y, (MZ + zr) / 2))
key_socket(RAY_STR, F(T['uv0']), 4.0); key_socket(RAY_STR, F(T['uv1'] - 0.3), 4.0); key_socket(RAY_STR, F(T['uv1']), 0.0)
key_socket(EXP_GLOW, 1, 0.0); key_socket(EXP_GLOW, F(T['uv0'] + 0.2), 0.0); key_socket(EXP_GLOW, F(T['uv0'] + 0.9), 1.6); key_socket(EXP_GLOW, F(T['dev1']), 1.6)

# 3) 显影：被照过的胶（左右两块）溶掉（厚度 → 0）
for o in (resL, resR): key(o, 'scale', F(T['dev0']), (1, 1, 1)); key(o, 'scale', F(T['dev1']), (1, 1, 0.001)); ease_all(o)

# 4) 刻蚀：等离子离子从上方落下；没有胶保护的顶层硅被一层层削掉，停在埋氧层
import random
rnd = random.Random(7); ions = []
for k in range(36):
    side = -1 if k % 2 else 1; x = side * rnd.uniform(WG + 0.25, X1 - 0.25); y = rnd.uniform(Y0 + 0.3, Y1 - 0.3)
    t0 = T['etch0'] + (T['etch1'] - T['etch0'] - 0.4) * k / 36
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(x, y, zt + 5), segments=12, ring_count=6); o = bpy.context.object; o.scale = (1, 1, 3.5); o.data.materials.append(M['ion'])
    key(o, 'location', F(t0), (x, y, zt + 5)); key(o, 'location', F(t0 + 0.35), (x, y, zt + 0.05))
    for fc in fcurves_of(o):
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    key(o, 'hide_render', 1, True); key(o, 'hide_render', F(t0), False); key(o, 'hide_render', F(t0 + 0.4), True)
    ions.append(o)
for o in (siL, siR): key(o, 'scale', F(T['etch0'] + 0.2), (1, 1, 1)); key(o, 'scale', F(T['etch1']), (1, 1, 0.001)); ease_all(o)
for o in (siL, siR): key(o, 'hide_render', F(T['etch1']), False); key(o, 'hide_render', F(T['etch1']) + 1, True)
for o in (resL, resR): key(o, 'hide_render', F(T['dev1']), False); key(o, 'hide_render', F(T['dev1']) + 1, True)

# 5) 去胶：中间那条胶去掉，露出硅波导
key(resC, 'scale', F(T['strip0']), (1, 1, 1)); key(resC, 'scale', F(T['strip1']), (1, 1, 0.001)); ease_all(resC)
key(resC, 'hide_render', F(T['strip1']), False); key(resC, 'hide_render', F(T['strip1']) + 1, True)   # 压扁后会和硅顶面重叠闪烁，直接隐藏

# 6) 导光：光从波导里由远到近传过来，从正面端面射出
core = box('wg_core', -WG * 0.45, WG * 0.45, Y0, Y1, zt - 0.02, zt + 0.006, M['core'], origin=(0, Y1, zt - 0.02), bevel=0.0)
key(core, 'hide_render', 1, True); key(core, 'hide_render', F(T['light0']), False)
key(core, 'scale', 1, (1, 0.001, 1)); key(core, 'scale', F(T['light0']), (1, 0.001, 1)); key(core, 'scale', F(T['light1']), (1, 1, 1))
for fc in fcurves_of(core):
    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
key_socket(CORE_STR, F(T['light0']), 0.0); key_socket(CORE_STR, F(T['light0'] + 0.2), 5.0)
key_socket(RIDGE_GLOW, 1, 0.0); key_socket(RIDGE_GLOW, F(T['light1'] - 0.2), 0.0); key_socket(RIDGE_GLOW, F(T['light1'] + 0.5), 1.8)
BEAM = 1.4                                                                            # 出光锥：端面射出、略发散
bpy.ops.mesh.primitive_cone_add(vertices=48, end_fill_type='NOTHING', radius1=WG * 0.75, radius2=0.55, depth=BEAM, location=(0, Y0 - 0.015 - BEAM / 2, (zs + zt) / 2), rotation=(math.radians(90), 0, 0))
ex = bpy.context.object; ex.data.materials.append(M['exit']); bpy.ops.object.shade_smooth()
ex.scale = (1, 0.45, 1)   # 竖向压扁：贴着端面那一圈不能低于埋氧层顶面，否则在正面投出一道黑弧
key(ex, 'hide_render', 1, True); key(ex, 'hide_render', F(T['exit0']), False)
key_socket(EXIT_STR, 1, 0.0); key_socket(EXIT_STR, F(T['exit0']), 0.0); key_socket(EXIT_STR, F(T['exit0'] + 0.5), 2.5)
facet = box('facet_glow', -WG + 0.02, WG - 0.02, Y0 - 0.012, Y0 - 0.004, zs + 0.02, zt - 0.02, M['core'], bevel=0.0)   # 端面本身亮起来
key(facet, 'hide_render', 1, True); key(facet, 'hide_render', F(T['exit0']), False)

# ---------- 灯光、世界 ----------
def area(loc, rot, energy, size, col):
    bpy.ops.object.light_add(type='AREA', location=loc); L = bpy.context.object; L.data.energy = energy; L.data.size = size; L.data.color = col; L.rotation_euler = [math.radians(a) for a in rot]; return L
area((-8, -6, 12), (35, 0, -50), 2600, 8, (1.0, 0.94, 0.86))
area((9, 8, 6), (65, 0, 135), 900, 6, (0.6, 0.78, 1.0))
area((0, -14, 2), (88, 0, 0), 250, 8, (1.0, 0.96, 0.92))
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.03, 0.032, 0.04, 1); w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.5

# ---------- 相机：俯视层块 → 跟着光往下推 → 拉开看刻蚀 → 绕到正面低角度看端面出光 ----------
bpy.ops.object.empty_add(location=(0, 0, zs)); tgt = bpy.context.object; tgt.name = 'target'
bpy.ops.object.camera_add(location=(10.5, -13.0, 12.0)); cam = bpy.context.object; sc.camera = cam
cam.data.lens = 30; cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24
tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
cam.data.dof.use_dof = True; cam.data.dof.focus_object = tgt; cam.data.dof.aperture_fstop = 4.0
CAMK = [  # (秒, 相机位置, 目标位置)
    (0.0, (9.0, -13.5, 10.0), (0.3, 0, 1.2)),               # 3/4 俯视，整个层块
    (2.6, (8.0, -12.0, 9.0), (0.3, 0, 1.4)),                # 慢推
    (3.4, (9.0, -13.0, 5.8), (0, 0, zr + 0.9)),           # 放低：看到掩模悬在胶上方
    (4.8, (6.8, -10.0, 4.6), (0, 0, zr + 0.6)),           # 跟着光往下推
    (6.6, (8.0, -11.5, 7.6), (0, 0, zs)),                 # 升高看显影、刻蚀
    (9.8, (6.8, -10.5, 6.4), (0, 0, zs)),
    (11.4, (1.3, -10.5, 5.4), (0, -0.6, zs)),            # 绕到正前方偏上：波导条顺着竖屏往远处延伸
    (14.0, (0.9, -9.0, 4.3), (0, -2.2, zs))]
for s, cl, tl in CAMK:
    cam.location = cl; cam.keyframe_insert('location', frame=F(s)); tgt.location = tl; tgt.keyframe_insert('location', frame=F(s))
ease_all(cam); ease_all(tgt)

# ---------- 渲染设置 ----------
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
if GPU:
    prefs = bpy.context.preferences.addons['cycles'].preferences; ok = None
    for dt in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = dt; (prefs.refresh_devices() if hasattr(prefs, 'refresh_devices') else prefs.get_devices())
            devs = [d for d in prefs.devices if d.type == dt]
            if devs:
                for d in prefs.devices: d.use = d.type == dt
                ok = dt; break
        except Exception: pass
    if ok: sc.cycles.device = 'GPU'; print('GPU_DEVICE', ok, [d.name for d in prefs.devices if d.use])
    else: print('GPU_DEVICE none —— 没找到 NVIDIA 显卡，改用 CPU（会很慢）')
sc.cycles.samples = SAMP; sc.cycles.use_denoising = True; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.03
# 反弹次数够用即可（场景是简单方块 + 发光体）：比 8 次反弹快约一倍，画面看不出差别（2026-11-09 实测）
sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2; sc.cycles.transparent_max_bounces = 8
if GPU and hasattr(sc.cycles, 'denoising_use_gpu'): sc.cycles.denoising_use_gpu = True
sc.cycles.transmission_bounces = 6; sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.4; sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, NF
sc.view_settings.view_transform = 'AgX'
for lk in ('AgX - Medium High Contrast', 'Medium High Contrast'):
    try: sc.view_settings.look = lk; break
    except Exception: pass
# 发光体、光柱、玻璃不投影（否则出光锥在端面下投出一块黑影）；掩模上的铬条照常投影 —— 那正是「挡光」
LIGHTY = {M[k].name for k in ('uv', 'ray', 'ion', 'core', 'exit', 'glass')}
for o in sc.objects:
    if o.type == 'MESH' and o.data.materials and o.data.materials[0] and o.data.materials[0].name in LIGHTY:
        if hasattr(o, 'visible_shadow'): o.visible_shadow = False
# 半透明材质在 EEVEE 里用混合模式（默认的抖动模式在 64 采样下有颗粒）
for k in ('uv', 'exit', 'glass'):
    if hasattr(M[k], 'surface_render_method'): M[k].surface_render_method = 'BLENDED'
set_fmt('PNG')
if EEVEE:
    ENG = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    sc.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in ENG else 'BLENDER_EEVEE_NEXT'; ee = sc.eevee
    for k, v in (('taa_render_samples', SAMP), ('use_raytracing', True), ('use_shadows', True), ('use_fast_gi', True)):
        try: setattr(ee, k, v)
        except Exception as e: print('EEVEE 设置跳过', k, e)

# ---------- 每帧锚点（给 2D 标签、工序条） ----------
ANCH = {'top_si': Vector((X1 - 0.6, Y0, (zs + zt) / 2)), 'box': Vector((X1 - 0.6, Y0, (zb + zs) / 2)), 'sub': Vector((X1 - 0.6, Y0, zb / 2)),
        'resist': Vector((X1 - 1.5, Y0, (zt + zr) / 2)), 'ridge_front': Vector((0, Y0, (zs + zt) / 2)), 'mask': Vector((0, 0, MZ + 0.1))}
anchors = {}
for f in range(1, NF + 1):
    sc.frame_set(f); anchors[f] = {k: [round(v.x * W, 1), round((1 - v.y) * H, 1)] for k, p in ANCH.items() for v in [world_to_camera_view(sc, cam, p)]}
json.dump({'fps': FPS, 'nf': NF, 'w': W, 'times': T, 'frames': anchors}, open(os.path.join(OUT, 'anchors.json'), 'w'))
if VIDEO and not FRAMES:
    set_fmt('FFMPEG'); sc.render.ffmpeg.format = 'MPEG4'; sc.render.ffmpeg.codec = 'H264'
    for k, v in (('constant_rate_factor', 'PERC_LOSSLESS'), ('ffmpeg_preset', 'GOOD')):
        try: setattr(sc.render.ffmpeg, k, v)
        except Exception as e: print('ffmpeg 设置跳过', k, e)
    sc.render.filepath = os.path.join(OUT, 'waveguide.mp4'); bpy.ops.render.render(animation=True)
else:
    import time
    for f in (FRAMES or range(1, NF + 1)):
        sc.frame_set(f); sc.render.filepath = os.path.join(OUT, f'f{f:04d}.png'); t0 = time.time(); bpy.ops.render.render(write_still=True)
        print(f'FRAME_TIME 第 {f} 帧：{time.time() - t0:.1f} 秒')
        if EEVEE and f == (FRAMES or [1])[0]:
            try: import gpu; print('EEVEE_GPU', gpu.platform.vendor_get(), '|', gpu.platform.renderer_get())
            except Exception as e: print('EEVEE_GPU 未知', e)
print('DONE', OUT)
