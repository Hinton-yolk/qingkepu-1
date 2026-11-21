# 「一语道破」EP01 开场概念样片：冰箱里正在生成的世界（约 20 秒，9:16，30 fps）。
# 一间厨房、一台冰箱。冰箱里没有食物，门内是随 AI 写出的文字而成立的世界：
#   「……一片海洋」→ 门内升起海面、地平线、低太阳；回到同一个起点（演示回放）→ 海水退下、雾回来；
#   「……一片森林」→ 地面升起、树从门口一层层往远处长出来、光变成林间的暖绿。
# 门内世界是真的三维空间：冰箱背板和墙上开了洞，海和森林在墙后面延伸到远处；门框、内胆、门板正常遮挡；
# 门内的天光只从门洞照进厨房（Cycles 光门户）。
# pose(t) 是时间的纯函数；每一帧所有会动的东西都重新摆。
# 用法：blender -b -P fridge.py -- --outdir DIR [--res 540] [--samples 24] [--f0 0 --f1 -1 | --only 1.0,5.0]
import bpy, math, os, sys, json, random
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
import argparse
ap = argparse.ArgumentParser()
ap.add_argument('--outdir', default='/tmp/fridge'); ap.add_argument('--res', type=int, default=540); ap.add_argument('--samples', type=int, default=24)
ap.add_argument('--f0', type=int, default=0); ap.add_argument('--f1', type=int, default=-1); ap.add_argument('--only', default='')
A = ap.parse_args(argv)
FPS, DUR = 30, 20.0

# ---------------- 时间表（秒） ----------------
T_DOOR = (0.0, 1.5)          # 门从半开到全开（第一帧门已经开了一条缝，里面透出光）
T_SEA = 1.75                 # 「海洋」落定（2D 层同一时刻）
T_SEA_FORM = (1.95, 3.4)     # 雾从中间散开、海面升起、天和太阳出来
T_RW = (7.5, 8.9)            # 演示回放：海退下、雾回来
T_FOR = 9.7                  # 「森林」落定
T_FOR_FORM = (9.9, 12.0)     # 地面升起、树从门口往远处一层层长出来
VOID, SEA, FOREST = 0, 1, 2

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(u): u = clamp(u); return u * u * u * (u * (6 * u - 15) + 10)
def sstep(a, b, t): return ease((t - a) / (b - a)) if b > a else float(t >= b)
def lerp(a, b, u): return a + (b - a) * u
def mixc(c0, c1, u): return tuple(lerp(c0[i], c1[i], u) for i in range(len(c0)))
def hexc(h, a=1.0): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)
def lin(c): return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c[:3]) + (1.0,)
def H(h): return lin(hexc(h))

def states(t):
    """返回 (海的成立度, 森林的成立度)：0 = 雾（还没写定），1 = 成立"""
    sea = sstep(*T_SEA_FORM, t) * (1 - sstep(*T_RW, t))
    fo = sstep(*T_FOR_FORM, t)
    return sea, fo

# ---------------- 场景基础 ----------------
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
if os.environ.get('KEPU_GPU'):                 # RunPod：用 GPU（默认 CUDA；部分驱动上 OptiX 编译失败）
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for kind in ((os.environ.get('KEPU_GPU_KIND') or 'CUDA'), 'CUDA'):
        try:
            prefs.compute_device_type = kind; prefs.get_devices()
            if any(d.type == kind for d in prefs.devices): break
        except Exception: pass
    for d in prefs.devices: d.use = d.type != 'CPU'
    sc.cycles.device = 'GPU'
sc.cycles.samples = A.samples; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.03
sc.cycles.use_denoising = True
try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
except Exception: pass
sc.cycles.max_bounces = 5; sc.cycles.diffuse_bounces = 3; sc.cycles.glossy_bounces = 3; sc.cycles.transmission_bounces = 6; sc.cycles.transparent_max_bounces = 12
sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
sc.render.resolution_x = A.res; sc.render.resolution_y = int(A.res * 16 / 9); sc.render.resolution_percentage = 100
sc.render.use_persistent_data = True
sc.view_settings.view_transform = 'AgX'
try: sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
sc.render.film_transparent = False
COL = bpy.context.collection

def link(o): COL.objects.link(o); return o
def nodes_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); return m, nt, out

FOGS = []                                      # 门内世界的远景雾（按到相机的距离混进雾色），每帧改颜色和浓度
def fog_wrap(nt, sh, out):
    cam = nt.nodes.new('ShaderNodeCameraData'); mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = 8.0; mr.inputs['From Max'].default_value = 90.0
    mr.inputs['To Min'].default_value = 0.0; mr.inputs['To Max'].default_value = 0.6
    em = nt.nodes.new('ShaderNodeEmission'); mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(cam.outputs['View Distance'], mr.inputs['Value']); nt.links.new(mr.outputs[0], mx.inputs[0])
    nt.links.new(sh, mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs['Surface'])
    FOGS.append((mr, em))

def pbr(name, col, rough=0.5, metal=0.0, coat=0.0, fog=False, emit=None, trans=0.0, alpha=None):
    m, nt, out = nodes_mat(name); p = nt.nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Base Color'].default_value = H(col) if isinstance(col, str) else col
    p.inputs['Roughness'].default_value = rough; p.inputs['Metallic'].default_value = metal
    p.inputs['Coat Weight'].default_value = coat
    if trans: p.inputs['Transmission Weight'].default_value = trans
    if emit: p.inputs['Emission Color'].default_value = H(emit[0]); p.inputs['Emission Strength'].default_value = emit[1]
    if fog: fog_wrap(nt, p.outputs[0], out)
    else: nt.links.new(p.outputs[0], out.inputs['Surface'])
    m['p'] = p.name; return m

def box(size, loc, mat, bevel=0.0, name='box', rot=(0, 0, 0), seg=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.active_object; o.name = name
    o.scale = size; bpy.ops.object.transform_apply(scale=True)
    if bevel > 0:
        md = o.modifiers.new('bev', 'BEVEL'); md.width = bevel; md.segments = seg; md.limit_method = 'ANGLE'
    o.data.materials.append(mat)
    for poly in o.data.polygons: poly.use_smooth = bevel > 0
    return o

def cyl(r, d, loc, mat, verts=24, rot=(0, 0, 0), name='cyl'):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=verts, rotation=rot); o = bpy.context.active_object; o.name = name
    o.data.materials.append(mat)
    for poly in o.data.polygons: poly.use_smooth = True
    return o

def empty(name, loc=(0, 0, 0)):
    o = bpy.data.objects.new(name, None); link(o); o.location = loc; return o

# ---------------- 厨房 ----------------
FW, FD, FH = 0.80, 0.74, 1.86                 # 冰箱宽、深、高（背面贴墙 y=0，正面 y=-FD）
CX0, CX1, CZ0, CZ1 = -0.335, 0.335, 0.10, 1.25 # 冷藏室门洞（也是墙上的洞）
YF = -FD
wall_m = pbr('wall', '#E4DACD', 0.6)
tile_m, tnt, tout = nodes_mat('tile')
_p = tnt.nodes.new('ShaderNodeBsdfPrincipled'); _b = tnt.nodes.new('ShaderNodeTexBrick'); _tc = tnt.nodes.new('ShaderNodeTexCoord')
_b.inputs['Color1'].default_value = H('#F3EEE7'); _b.inputs['Color2'].default_value = H('#ECE5DC'); _b.inputs['Mortar'].default_value = H('#D9D0C4')
_b.inputs['Scale'].default_value = 1.0; _b.inputs['Mortar Size'].default_value = 0.006; _b.inputs['Brick Width'].default_value = 0.2; _b.inputs['Row Height'].default_value = 0.1
_mp = tnt.nodes.new('ShaderNodeMapping'); _mp.inputs['Rotation'].default_value = (math.pi / 2, 0, 0)
tnt.links.new(_tc.outputs['Object'], _mp.inputs['Vector']); tnt.links.new(_mp.outputs[0], _b.inputs['Vector'])
tnt.links.new(_b.outputs['Color'], _p.inputs['Base Color']); _p.inputs['Roughness'].default_value = 0.25; _p.inputs['Coat Weight'].default_value = 0.3
tnt.links.new(_p.outputs[0], tout.inputs['Surface'])
floor_m, fnt, fout = nodes_mat('floor')
_p = fnt.nodes.new('ShaderNodeBsdfPrincipled'); _w = fnt.nodes.new('ShaderNodeTexWave'); _r = fnt.nodes.new('ShaderNodeValToRGB')
_w.wave_type = 'BANDS'; _w.inputs['Scale'].default_value = 1.4; _w.inputs['Distortion'].default_value = 6.0; _w.inputs['Detail'].default_value = 3
_r.color_ramp.elements[0].color = H('#A9825E'); _r.color_ramp.elements[1].color = H('#8E6A4A')
fnt.links.new(_w.outputs['Fac'], _r.inputs['Fac']); fnt.links.new(_r.outputs['Color'], _p.inputs['Base Color']); _p.inputs['Roughness'].default_value = 0.35
fnt.links.new(_p.outputs[0], fout.inputs['Surface'])

# 房间是封闭的（相机在里面）：门内世界的天光只能从冰箱门洞照进来
box((8, 0.1, 4), (0, 3.05 - 3.0, 2), wall_m, name='wall_back_dummy').hide_render = True
def wall_with_hole():
    """后墙（y=0..0.1），冰箱门洞那一块挖空：墙后面就是门内世界"""
    T = 0.1; y = T / 2
    box((4.0, T, 3.2), (-2.0 + CX0, y, 1.6), tile_m, name='wL')
    box((4.0, T, 3.2), (2.0 + CX1, y, 1.6), tile_m, name='wR')
    box((CX1 - CX0, T, CZ0), (0, y, CZ0 / 2), tile_m, name='wB')
    box((CX1 - CX0, T, 3.2 - CZ1), (0, y, (3.2 + CZ1) / 2), tile_m, name='wT')
wall_with_hole()
box((8, 8, 0.1), (0, -3.5, -0.05), floor_m, name='floor')
box((0.1, 8, 3.2), (-2.2, -3.5, 1.6), wall_m, name='wallL'); box((0.1, 8, 3.2), (2.2, -3.5, 1.6), wall_m, name='wallR')
box((4.5, 0.1, 3.2), (0, -6.0, 1.6), wall_m, name='wallF'); box((4.5, 8, 0.1), (0, -3.5, 3.2), wall_m, name='ceil')
# 右边：橱柜 + 台面 + 水壶 + 一盆小绿植；左边：高柜
cab_m = pbr('cab', '#E6DED2', 0.45, coat=0.2); top_m = pbr('top', '#D8D2CA', 0.25, coat=0.4)
box((1.3, 0.62, 0.86), (FW / 2 + 0.03 + 0.65, -0.33, 0.43), cab_m, 0.01, 'cab')
box((1.34, 0.66, 0.04), (FW / 2 + 0.03 + 0.67, -0.34, 0.88), top_m, 0.006, 'ctop')
for k in range(2): box((0.62, 0.012, 0.78), (FW / 2 + 0.36 + 0.64 * k, -0.645, 0.43), cab_m, 0.006, 'cdoor')
km = pbr('kettle', '#C8CCD0', 0.18, metal=1.0)
cyl(0.09, 0.2, (0.82, -0.36, 1.0), km); bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, location=(0.82, -0.36, 1.1)); bpy.context.active_object.data.materials.append(km)
pot = pbr('pot', '#B9694A', 0.6); cyl(0.07, 0.12, (1.25, -0.3, 0.96), pot)
leaf_m = pbr('leaf', '#4E7D4A', 0.5)
for k in range(5):
    a = k * 1.26; bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(1.25 + 0.05 * math.cos(a), -0.3 + 0.05 * math.sin(a), 1.07 + 0.03 * (k % 2)))
    bpy.context.active_object.scale = (1, 0.6, 1.4); bpy.context.active_object.data.materials.append(leaf_m)
box((0.7, 0.62, 2.2), (-FW / 2 - 0.03 - 0.35, -0.33, 1.1), cab_m, 0.01, 'tall')
box((0.012, 0.012, 0.5), (-FW / 2 - 0.12, -0.645, 1.0), km, 0.0, 'thandle')

# ---------------- 冰箱 ----------------
shell = pbr('shell', '#F4F1EC', 0.22, coat=0.6)
liner = pbr('liner', '#F7F7F5', 0.35)
gasket = pbr('gasket', '#9EA2A6', 0.6)
handle_m = pbr('handle', '#BFC3C7', 0.2, metal=1.0)
# 外壳：左右侧板、顶、底座、中梁（冷冻室和冷藏室之间）
box((0.04, FD, FH), (-FW / 2 + 0.02, YF / 2, FH / 2), shell, 0.012, 'sideL')
box((0.04, FD, FH), (FW / 2 - 0.02, YF / 2, FH / 2), shell, 0.012, 'sideR')
box((FW, FD, 0.04), (0, YF / 2, FH - 0.02), shell, 0.012, 'topP')
box((FW, FD, CZ0), (0, YF / 2, CZ0 / 2), shell, 0.012, 'base')
box((FW, FD, 0.08), (0, YF / 2, CZ1 + 0.04), shell, 0.012, 'mid')
# 冷藏室内胆（门洞到墙洞之间的一段白色内壁）：左右、上、下
box((0.035, FD - 0.02, CZ1 - CZ0), (CX0 - 0.0175, YF / 2, (CZ0 + CZ1) / 2), liner, 0.004, 'linL')
box((0.035, FD - 0.02, CZ1 - CZ0), (CX1 + 0.0175, YF / 2, (CZ0 + CZ1) / 2), liner, 0.004, 'linR')
box((CX1 - CX0, FD - 0.02, 0.02), (0, YF / 2, CZ1 - 0.01), liner, 0.004, 'linT')
box((CX1 - CX0, FD - 0.02, 0.02), (0, YF / 2, CZ0 + 0.01), liner, 0.004, 'linB')
# 门洞一圈密封条
for (sx, sz, lx, lz) in ((0.02, CZ1 - CZ0, CX0 - 0.01, (CZ0 + CZ1) / 2), (0.02, CZ1 - CZ0, CX1 + 0.01, (CZ0 + CZ1) / 2), (CX1 - CX0 + 0.04, 0.02, 0, CZ0 - 0.01), (CX1 - CX0 + 0.04, 0.02, 0, CZ1 + 0.01)):
    box((sx, 0.012, sz), (lx, YF - 0.004, lz), gasket, 0.004, 'gask')
# 冷冻室门（关着）
box((FW - 0.01, 0.06, FH - CZ1 - 0.1), (0, YF - 0.03, (FH + CZ1 + 0.08) / 2), shell, 0.015, 'fzdoor')
box((0.022, 0.03, 0.32), (FW / 2 - 0.08, YF - 0.08, CZ1 + 0.2), handle_m, 0.008, 'fzhandle')
# 冷藏室门：铰链在左边，往镜头左边打开；门内侧有两层门搁架，放着牛奶盒和两个瓶子（一看就是冰箱）
door = empty('door', (-FW / 2, YF, 0))
DH = CZ1 + 0.08 - 0.01
d = box((FW - 0.01, 0.06, DH - 0.01), (FW / 2, -0.03, (DH) / 2 + 0.005), shell, 0.015, 'dpanel'); d.parent = door
d = box((0.022, 0.03, 0.42), (FW - 0.08, -0.08, 0.95), handle_m, 0.008, 'dhandle'); d.parent = door
d = box((FW - 0.1, 0.03, DH - 0.12), (FW / 2, 0.012, DH / 2), liner, 0.01, 'dliner'); d.parent = door
shelf_m = pbr('shelf', '#E9F1F4', 0.1, trans=0.6)
milk = pbr('milk', '#FBFBF8', 0.5); cap = pbr('cap', '#3F7FB8', 0.4); bott = pbr('bott', '#7FA36A', 0.15, trans=0.5); juice = pbr('juice', '#E6A23C', 0.3)
for zz in (0.32, 0.78):
    d = box((FW - 0.14, 0.11, 0.012), (FW / 2, 0.08, zz), shelf_m, 0.003, 'dshelf'); d.parent = door
    d = box((FW - 0.14, 0.008, 0.07), (FW / 2, 0.135, zz + 0.04), shelf_m, 0.003, 'dlip'); d.parent = door
d = box((0.085, 0.085, 0.2), (0.22, 0.075, 0.44), milk, 0.006, 'milk'); d.parent = door
d = cyl(0.012, 0.02, (0.22, 0.075, 0.55), cap); d.parent = door
d = cyl(0.035, 0.24, (0.38, 0.075, 0.45), bott); d.parent = door
d = cyl(0.04, 0.17, (0.55, 0.075, 0.87), juice); d.parent = door
d = cyl(0.03, 0.2, (0.66, 0.075, 0.89), bott); d.parent = door

# ---------------- 门内：「还没写定」的雾 ----------------
# 门洞后半段的一张发光雾幕：中间先散开（门内世界成立），回放时再合上
mist_m, mnt, mout = nodes_mat('mist')
_tc = mnt.nodes.new('ShaderNodeTexCoord'); _sep = mnt.nodes.new('ShaderNodeSeparateXYZ')
_noise = mnt.nodes.new('ShaderNodeTexNoise'); _noise.inputs['Scale'].default_value = 3.0; _noise.inputs['Detail'].default_value = 4; _noise.noise_dimensions = '4D'
_add = mnt.nodes.new('ShaderNodeMath'); _add.operation = 'MULTIPLY_ADD'; _add.inputs[1].default_value = 0.18
MIST_R = mnt.nodes.new('ShaderNodeMapRange')            # 距中心 < 半径 → 透明（散开）
MIST_R.inputs['From Min'].default_value = 0.0; MIST_R.inputs['From Max'].default_value = 0.12; MIST_R.inputs['To Min'].default_value = 1.0; MIST_R.inputs['To Max'].default_value = 0.0
_sub = mnt.nodes.new('ShaderNodeMath'); _sub.operation = 'SUBTRACT'
_tr = mnt.nodes.new('ShaderNodeBsdfTransparent'); MIST_E = mnt.nodes.new('ShaderNodeEmission'); MIST_E.inputs['Color'].default_value = H('#FFF8EC')
_mx = mnt.nodes.new('ShaderNodeMixShader'); _inv = mnt.nodes.new('ShaderNodeMath'); _inv.operation = 'SUBTRACT'; _inv.inputs[0].default_value = 1.0
mnt.links.new(_tc.outputs['UV'], _sep.inputs[0]); mnt.links.new(_tc.outputs['UV'], _noise.inputs['Vector'])
mnt.links.new(_noise.outputs['Fac'], _add.inputs[0]); mnt.links.new(_sep.outputs['Y'], _add.inputs[2])   # 从下往上散：高度 + 噪声   # 距离 + 0.18×噪声：边缘是不规则的雾
MIST_RAD = mnt.nodes.new('ShaderNodeValue')
mnt.links.new(_add.outputs[0], _sub.inputs[0]); mnt.links.new(MIST_RAD.outputs[0], _sub.inputs[1]); mnt.links.new(_sub.outputs[0], MIST_R.inputs['Value'])
mnt.links.new(MIST_R.outputs[0], _inv.inputs[1])
mnt.links.new(_inv.outputs[0], _mx.inputs[0]); mnt.links.new(MIST_E.outputs[0], _mx.inputs[1]); mnt.links.new(_tr.outputs[0], _mx.inputs[2])
mnt.links.new(_mx.outputs[0], mout.inputs['Surface'])
MIST_NOISE = _noise
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.08, (CZ0 + CZ1) / 2), rotation=(math.pi / 2, 0, 0))
mist = bpy.context.active_object; mist.name = 'mist'; mist.scale = (CX1 - CX0 + 0.02, CZ1 - CZ0 + 0.02, 1); mist.data.materials.append(mist_m)
mist.visible_shadow = False
# 雾幕前面第二层（更淡），雾有厚度
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.42, (CZ0 + CZ1) / 2), rotation=(math.pi / 2, 0, 0))
mist2 = bpy.context.active_object; mist2.name = 'mist2'; mist2.scale = mist.scale; mist2.data.materials.append(mist_m); mist2.visible_shadow = False

# 门洞里的补光（颜色跟着门内世界变）：门开时把门内的光打到厨房地上
bpy.ops.object.light_add(type='AREA', location=(0, -0.2, (CZ0 + CZ1) / 2), rotation=(-math.pi / 2, 0, 0))
spill = bpy.context.active_object; spill.data.shape = 'RECTANGLE'; spill.data.size = CX1 - CX0; spill.data.size_y = CZ1 - CZ0
spill.data.energy = 60; spill.rotation_euler = (math.pi / 2, 0, 0)     # 朝 -y（朝厨房）
# 门户：帮 Cycles 从门洞采样墙后的天光
bpy.ops.object.light_add(type='AREA', location=(0, 0.12, (CZ0 + CZ1) / 2)); portal = bpy.context.active_object
portal.data.shape = 'RECTANGLE'; portal.data.size = CX1 - CX0; portal.data.size_y = CZ1 - CZ0; portal.rotation_euler = (math.pi / 2, 0, 0)
try: portal.data.cycles.is_portal = True
except Exception: pass
# 厨房灯：顶上一盏暖光大面光 + 相机这边一盏柔和补光
bpy.ops.object.light_add(type='AREA', location=(0.6, -1.9, 3.1)); kl = bpy.context.active_object; kl.data.size = 2.2; kl.data.energy = 110; kl.data.color = (1.0, 0.9, 0.78)
bpy.ops.object.light_add(type='AREA', location=(-0.6, -4.5, 1.8), rotation=(math.radians(80), 0, math.radians(-10))); fl = bpy.context.active_object; fl.data.size = 2.5; fl.data.energy = 45; fl.data.color = (1.0, 0.95, 0.9)

# ---------------- 世界：天空（随门内世界变） ----------------
W = bpy.data.worlds.new('w'); sc.world = W; W.use_nodes = True; wn = W.node_tree; wn.nodes.clear()
wo = wn.nodes.new('ShaderNodeOutputWorld'); bg = wn.nodes.new('ShaderNodeBackground'); tc = wn.nodes.new('ShaderNodeTexCoord')
sep = wn.nodes.new('ShaderNodeSeparateXYZ'); SKY = wn.nodes.new('ShaderNodeValToRGB')
wn.links.new(tc.outputs['Generated'], sep.inputs[0]); wn.links.new(sep.outputs['Z'], SKY.inputs['Fac'])
SKY.color_ramp.elements[0].position = 0.0; SKY.color_ramp.elements[1].position = 0.35
SKY.color_ramp.elements.new(0.08)
wn.links.new(SKY.outputs['Color'], bg.inputs['Color']); wn.links.new(bg.outputs[0], wo.inputs['Surface'])
SKYC = {VOID: ('#FBF7F0', '#FBF7F0', '#F6F1EA', 1.4), SEA: ('#FFC890', '#F2B98E', '#3F86CC', 1.45), FOREST: ('#E9E3A8', '#D6E3A4', '#8FC0C8', 1.2)}
FOGC = {VOID: '#FBF7F0', SEA: '#EAD3BD', FOREST: '#B9CC98'}

# ---------------- 海 ----------------
WL = 0.46                                       # 海面高度（在冷藏室里，大约到第一层搁板）
sea = empty('sea')
wat_m, wnt, wout = nodes_mat('water')
_p = wnt.nodes.new('ShaderNodeBsdfPrincipled'); _p.inputs['Base Color'].default_value = H('#145B80'); _p.inputs['Roughness'].default_value = 0.06
_p.inputs['Coat Weight'].default_value = 0.0; _p.inputs['IOR'].default_value = 1.33
_tc = wnt.nodes.new('ShaderNodeTexCoord'); _n1 = wnt.nodes.new('ShaderNodeTexNoise'); _n1.noise_dimensions = '4D'; _n1.inputs['Scale'].default_value = 1.6; _n1.inputs['Detail'].default_value = 6; _n1.inputs['Roughness'].default_value = 0.55
_mpw = wnt.nodes.new('ShaderNodeMapping'); _mpw.inputs['Scale'].default_value = (1.0, 2.6, 1.0)        # 拉长成横向的浪
_bump = wnt.nodes.new('ShaderNodeBump'); _bump.inputs['Strength'].default_value = 0.35; _bump.inputs['Distance'].default_value = 0.08
wnt.links.new(_tc.outputs['Object'], _mpw.inputs['Vector']); wnt.links.new(_mpw.outputs[0], _n1.inputs['Vector']); wnt.links.new(_n1.outputs['Fac'], _bump.inputs['Height'])
wnt.links.new(_bump.outputs[0], _p.inputs['Normal'])
fog_wrap(wnt, _p.outputs[0], wout); WAVE = _n1
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 300, 0)); w1 = bpy.context.active_object; w1.name = 'seaFar'; w1.scale = (900, 600, 1); w1.data.materials.append(wat_m); w1.parent = sea
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, YF / 2 + 0.05, 0)); w2 = bpy.context.active_object; w2.name = 'seaIn'; w2.scale = (CX1 - CX0, -YF + 0.1, 1); w2.data.materials.append(wat_m); w2.parent = sea
# 冷藏室里那一截海水的正面切面（像鱼缸）：看得出水有深度
body_m, _bnt, _bout = nodes_mat('waterbody')            # 冷藏室里那一块海水：透明的水 + 体积吸收（越深越蓝，看得进去）
_bp = _bnt.nodes.new('ShaderNodeBsdfPrincipled'); _bp.inputs['Base Color'].default_value = (1, 1, 1, 1); _bp.inputs['Roughness'].default_value = 0.04
_bp.inputs['Transmission Weight'].default_value = 1.0; _bp.inputs['IOR'].default_value = 1.03
_bv = _bnt.nodes.new('ShaderNodeVolumeAbsorption'); _bv.inputs['Color'].default_value = H('#2E9CC0'); _bv.inputs['Density'].default_value = 2.2
_bs = _bnt.nodes.new('ShaderNodeVolumeScatter'); _bs.inputs['Color'].default_value = H('#8FE0EA'); _bs.inputs['Density'].default_value = 2.6
_bad = _bnt.nodes.new('ShaderNodeAddShader'); _bnt.links.new(_bv.outputs[0], _bad.inputs[0]); _bnt.links.new(_bs.outputs[0], _bad.inputs[1])
_bnt.links.new(_bp.outputs[0], _bout.inputs['Surface']); _bnt.links.new(_bad.outputs[0], _bout.inputs['Volume'])
seabody = box((CX1 - CX0 - 0.004, -YF - 0.03, 1.0), (0, YF / 2, 0), body_m, 0.0, 'seabody')
SB_C = [sum(v[i] for v in seabody.bound_box) / 8 for i in range(3)]          # 网格自身中心的偏移（每帧移动时要扣掉）   # 冷藏室里的一整块海水（看得到正面的水深）
# 低太阳（看得见的日轮，海面上有一条反光的路）+ 太阳光
sun_m = pbr('sunm', '#FFE9C2', 1.0, emit=('#FFE0B0', 30.0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=9.0, location=(-12, 420, 22)); sund = bpy.context.active_object; sund.data.materials.append(sun_m); sund.parent = sea; sund.visible_shadow = False
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10)); sunl = bpy.context.active_object; sunl.data.angle = math.radians(1.5)
sunl.rotation_euler = (Vector((12, -420, -22)).to_track_quat('-Z', 'Y').to_euler())
# 远处：两座小岛 + 一只帆船（给尺度和视差）
isl = pbr('isl', '#6E7C86', 0.8, fog=True)
for (x, y, r, h) in ((-70, 300, 26, 7), (95, 380, 40, 9), (40, 520, 30, 5)):
    bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=r * 0.25, depth=h * 2, location=(x, y, 0), vertices=10); o = bpy.context.active_object; o.data.materials.append(isl); o.parent = sea
boat = empty('boat'); boat.parent = sea
hull = pbr('hull', '#5B4A3E', 0.5, fog=True); sail = pbr('sail', '#FFF9F0', 0.6, fog=True)
o = box((2.4, 0.7, 0.4), (0, 0, 0.15), hull, 0.1, 'hull'); o.parent = boat
bpy.ops.mesh.primitive_cone_add(radius1=1.1, radius2=0.0, depth=3.4, vertices=3, location=(0.1, 0, 2.0)); o = bpy.context.active_object; o.scale = (1, 0.06, 1); o.data.materials.append(sail); o.parent = boat

# ---------------- 森林 ----------------
forest = empty('forest')
gnd_m, gnt, gout = nodes_mat('ground')
_p = gnt.nodes.new('ShaderNodeBsdfPrincipled'); _n = gnt.nodes.new('ShaderNodeTexNoise'); _n.inputs['Scale'].default_value = 0.9; _n.inputs['Detail'].default_value = 8
_r = gnt.nodes.new('ShaderNodeValToRGB'); _r.color_ramp.elements[0].color = H('#4C6A33'); _r.color_ramp.elements[1].color = H('#8A8A45')
_tc = gnt.nodes.new('ShaderNodeTexCoord'); gnt.links.new(_tc.outputs['Object'], _n.inputs['Vector'])
gnt.links.new(_n.outputs['Fac'], _r.inputs['Fac']); gnt.links.new(_r.outputs['Color'], _p.inputs['Base Color']); _p.inputs['Roughness'].default_value = 0.9
fog_wrap(gnt, _p.outputs[0], gout)
VZ = -3.2                                       # 墙后面地势往下落：从冰箱里看出去是一片林谷，树冠一层层往远处排
def zg(y): return 0.0 if y <= 0.05 else VZ * ease(min(1.0, (y - 0.05) / 9.0))
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 300, VZ)); g1 = bpy.context.active_object; g1.scale = (900, 600, 1); g1.data.materials.append(gnd_m); g1.parent = forest
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, YF / 2 + 0.05, 0)); g2 = bpy.context.active_object; g2.scale = (CX1 - CX0, -YF + 0.1, 1); g2.data.materials.append(gnd_m); g2.parent = forest
path_m = pbr('path', '#B9A27A', 0.95, fog=True)     # 一条往林子深处去的小路（看得出纵深）
_sl = bpy.data.meshes.new('slope'); _V = []; _F = []
for i in range(21):
    y = 0.05 + 9.2 * i / 20; _V += [(-60, y, zg(y)), (60, y, zg(y))]
    if i: _F.append((2 * i - 2, 2 * i - 1, 2 * i + 1, 2 * i))
_sl.from_pydata(_V, [], _F); slope = bpy.data.objects.new('slope', _sl); link(slope); slope.data.materials.append(gnd_m); slope.parent = forest
bpy.ops.mesh.primitive_plane_add(size=1, location=(0.0, 40, VZ + 0.004)); pth = bpy.context.active_object; pth.scale = (1.4, 62, 1); pth.data.materials.append(path_m); pth.parent = forest
trunk_m = pbr('trunk', '#5A4130', 0.85, fog=True)
needle = [pbr(f'needle{k}', c, 0.75, fog=True) for k, c in enumerate(('#2F5E3A', '#3D6E3F', '#4B7A3B'))]
crown = [pbr(f'crown{k}', c, 0.7, fog=True) for k, c in enumerate(('#6E9A45', '#86A84B', '#5C8A3E'))]
TREES = []                                      # (根, 生长开始时刻, 摇摆相位, 高度)
rnd = random.Random(7)
def make_tree(x, y, h, kind, mi):
    root = empty('tree', (x, y, zg(y))); root.parent = forest
    o = cyl(0.04 * h, h * 0.45, (0, 0, h * 0.22), trunk_m, verts=8); o.parent = root; o.location = (0, 0, h * 0.22)
    if kind == 0:
        for k, (r, z) in enumerate(((0.32, 0.38), (0.25, 0.6), (0.16, 0.8))):
            bpy.ops.mesh.primitive_cone_add(radius1=r * h, radius2=0, depth=0.42 * h, vertices=9, location=(0, 0, z * h)); c = bpy.context.active_object
            c.data.materials.append(needle[mi]); c.parent = root; c.location = (0, 0, z * h)
    else:
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.3 * h, subdivisions=2, location=(0, 0, 0.62 * h)); c = bpy.context.active_object
        c.scale = (1, 1, 1.15); c.data.materials.append(crown[mi]); c.parent = root; c.location = (0, 0, 0.62 * h)
        for poly in c.data.polygons: poly.use_smooth = False
    return root
# 树：沿小路两边一层层往远处排，越远越多；门口第一排就在冷藏室里（树长在冰箱里）
spots = []
for k in range(230):
    y = 9.5 + (k / 230) ** 1.3 * 125
    side = -1 if k % 2 else 1
    x = side * (0.9 + 0.045 * y * rnd.uniform(0.0, 2.2) + rnd.uniform(0, 1.2))
    spots.append((x, y, rnd.uniform(2.6, 4.4) * (1 + 0.006 * y), rnd.random() < 0.6))
for k in range(14):                                  # 小路尽头：远处正中也有一排树，挡住地平线，林子有尽头的层次
    y = rnd.uniform(40, 110); spots.append((rnd.uniform(-4, 4), y, rnd.uniform(4.0, 6.0), rnd.random() < 0.6))
for (x, y, h, kind) in spots:
    r = make_tree(x, y, h, 0 if kind else 1, rnd.randrange(3))
    TREES.append((r, T_FOR_FORM[0] + 0.15 + 1.3 * clamp((y - 9.0) / 80) ** 0.7 + rnd.uniform(0, 0.12), rnd.uniform(0, 6.28), h, y))
# 门口的几丛蕨（在冷藏室里，最近处）
fern_m = pbr('fern', '#5E8E43', 0.7)
FERNS = []
for (x, y) in ((-0.22, -0.62), (0.2, -0.58), (-0.05, -0.2), (0.27, -0.12)):
    root = empty('fern', (x, y, 0)); root.parent = forest
    for k in range(6):
        a = k * 1.05; bpy.ops.mesh.primitive_cone_add(radius1=0.018, radius2=0.0, depth=0.2, vertices=4, location=(0, 0, 0.09))
        c = bpy.context.active_object; c.rotation_euler = (0.7 * math.cos(a), 0.7 * math.sin(a), 0); c.scale = (1, 3, 1); c.data.materials.append(fern_m); c.parent = root
    FERNS.append(root)
# 林间光柱（斜着从树冠照下来的淡光）+ 飘落的叶子
shaft_m, snt, sout = nodes_mat('shaft')
_e = snt.nodes.new('ShaderNodeEmission'); _e.inputs['Color'].default_value = H('#FFF1C6'); _t = snt.nodes.new('ShaderNodeBsdfTransparent'); SHAFT_MIX = snt.nodes.new('ShaderNodeMixShader')
snt.links.new(_t.outputs[0], SHAFT_MIX.inputs[1]); snt.links.new(_e.outputs[0], SHAFT_MIX.inputs[2]); snt.links.new(SHAFT_MIX.outputs[0], sout.inputs['Surface']); SHAFT_E = _e
SHAFTS = []
for (x, y, w) in ((-1.4, 7, 0.9), (1.2, 12, 1.2), (-0.3, 20, 1.6), (2.4, 28, 2.2)):
    o = box((w, 0.05, 14), (x, y, 5.5), shaft_m, 0.0, 'shaft', rot=(math.radians(-28), math.radians(14), 0)); o.parent = forest; o.visible_shadow = False; SHAFTS.append(o)
lf_m = [pbr('lf0', '#C9A23E', 0.6), pbr('lf1', '#9DB34A', 0.6)]
LEAVES = []
for k in range(14):
    bpy.ops.mesh.primitive_plane_add(size=0.05, location=(0, 0, 0)); o = bpy.context.active_object; o.scale = (1, 0.6, 1); o.data.materials.append(lf_m[k % 2]); o.parent = forest
    LEAVES.append((o, rnd.uniform(-0.3, 0.3) + rnd.uniform(-1.5, 1.5) * (k % 3 == 0), rnd.uniform(0.2, 4.0), rnd.uniform(0, 10), rnd.uniform(0.6, 1.0)))

# ---------------- 相机 ----------------
cam_d = bpy.data.cameras.new('cam'); camo = bpy.data.objects.new('cam', cam_d); link(camo); sc.camera = camo
cam_d.sensor_fit = 'VERTICAL'; cam_d.sensor_height = 24.0
sc.view_settings.exposure = -0.35
cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 5.6
CAM = [  # (秒, 位置, 注视点, 焦距)
    (0.0,  (0.95, -3.55, 1.2), (-0.12, -0.6, 0.88), 25),   # 从右前方看：门往左打开，看得到门板和门上的牛奶、瓶子
    (1.6,  (0.88, -3.4, 1.18), (-0.1, -0.6, 0.86), 25),
    (3.5,  (0.85, -3.35, 1.17), (-0.08, -0.6, 0.86), 25),  # 「海洋」落定、海成立：镜头基本稳住
    (7.2,  (0.05, -2.75, 1.05), (0.02, -0.3, 0.86), 25),   # 横移 + 推近：门框和门内远景之间有视差
    (8.9,  (0.88, -3.4, 1.18), (-0.1, -0.6, 0.86), 25),    # 回放：镜头也回到起点的位置
    (11.9, (0.85, -3.35, 1.17), (-0.08, -0.6, 0.86), 25),  # 「森林」落定、森林成立：稳住
    (16.6, (0.3, -2.45, 1.12), (0.0, 0.0, 0.92), 25),      # 推进门口：林子的层次
    (20.0, (0.27, -2.33, 1.12), (0.0, 0.1, 0.93), 25),
]
def cam_at(t):
    ts = [c[0] for c in CAM]; i = max(k for k in range(len(CAM)) if ts[k] <= t) if t >= 0 else 0; i = min(i, len(CAM) - 2)
    u = ease((t - ts[i]) / (ts[i + 1] - ts[i]))
    return (Vector(CAM[i][1]).lerp(Vector(CAM[i + 1][1]), u), Vector(CAM[i][2]).lerp(Vector(CAM[i + 1][2]), u), lerp(CAM[i][3], CAM[i + 1][3], u))

# ---------------- 每帧 ----------------
def pose(t):
    sea_s, for_s = states(t)
    # 门：第一帧已经开了一条缝（里面透出光）→ 全开
    a = -lerp(math.radians(16), math.radians(118), sstep(*T_DOOR, t))       # 往镜头这边打开
    door.rotation_euler = (0, 0, a)
    # 雾：海或森林成立时从中间散开；回放时合上
    open_ = max(sea_s, for_s)
    MIST_RAD.outputs[0].default_value = lerp(1.3, -0.35, open_)          # 高度 > 阈值的地方透明：阈值往下走，雾从上往下散开
    MIST_NOISE.inputs['W'].default_value = t * 0.25
    MIST_E.inputs['Strength'].default_value = lerp(5.0, 3.0, open_)
    mist.hide_render = mist2.hide_render = open_ > 0.995
    # 海：从冰箱底下升起来；回放时退下去
    rise = sea_s
    sea.location = (0, 0, lerp(-1.2, WL, ease(rise)))
    sea.hide_render = rise < 0.002
    for o in sea.children_recursive: o.hide_render = rise < 0.002
    z = sea.location.z; hb = max(0.001, z - CZ0 - 0.006)
    seabody.location = (0, YF / 2 + 0.01 - SB_C[1], CZ0 + hb / 2 - 0.004 - SB_C[2] * hb); seabody.scale = (1, 1, hb); seabody.hide_render = z <= CZ0 + 0.005
    sund.location = (-12, 420, lerp(-12, 22, ease(rise)))      # 太阳从海平线下升起
    WAVE.inputs['W'].default_value = t * 0.22
    boat.location = (5.0 - 0.18 * t, 70, 0.05 * math.sin(t * 1.6)); boat.rotation_euler = (0.04 * math.sin(t * 1.3), 0, 0.3)
    sunl.data.energy = 3.2 * sea_s + 4.0 * for_s
    if for_s > sea_s:
        sunl.rotation_euler = (Vector((-30, -60, -70)).to_track_quat('-Z', 'Y').to_euler()); sunl.data.color = (1.0, 0.92, 0.75)
    else:
        sunl.rotation_euler = (Vector((12, -420, -22)).to_track_quat('-Z', 'Y').to_euler()); sunl.data.color = (1.0, 0.8, 0.6)
    # 森林：地面升起，树从门口一层层往远处长出来，轻轻摇
    fz = lerp(-1.5, 0.0, ease(sstep(T_FOR_FORM[0], T_FOR_FORM[0] + 0.5, t)))
    forest.location = (0, 0, fz); fvis = for_s > 0.001 or t > T_FOR_FORM[0]
    forest.hide_render = not fvis
    for o in forest.children_recursive: o.hide_render = not fvis
    for (r, t0, ph, h, y) in TREES:
        g = clamp((t - t0) / 0.7); s_ = 0.0 if g <= 0 else 1 + 1.25 * (g - 1) ** 3 + 0.25 * (g - 1) ** 2   # 长出来时略冲过头再回来
        r.scale = (max(0.001, s_),) * 3; r.hide_render = (g <= 0) or not fvis
        for c in r.children: c.hide_render = r.hide_render
        r.rotation_euler = (0.012 * math.sin(t * 0.9 + ph), 0.015 * math.sin(t * 0.7 + ph * 1.3), 0)
    for i, f in enumerate(FERNS):
        g = clamp((t - T_FOR_FORM[0] - 0.05 - 0.08 * i) / 0.5); s_ = 0.0 if g <= 0 else 1 + 1.4 * (g - 1) ** 3 + 0.4 * (g - 1) ** 2
        f.scale = (max(0.001, s_),) * 3; f.rotation_euler = (0, 0, 0.08 * math.sin(t * 1.1 + i))
        for c in f.children: c.hide_render = g <= 0 or not fvis
    sh = for_s * (0.55 + 0.1 * math.sin(t * 0.8))
    SHAFT_MIX.inputs[0].default_value = 0.025 * sh; SHAFT_E.inputs['Strength'].default_value = 2.0
    for o in SHAFTS: o.hide_render = True
    for (o, x0, y0, ph, sp) in LEAVES:
        tt = t - T_FOR_FORM[1] + ph
        if t < T_FOR_FORM[1] - 0.5: o.hide_render = True; continue
        zz = 2.4 - (tt * 0.28 * sp) % 2.4
        o.location = (x0 + 0.15 * math.sin(tt * 1.3 + ph), y0 - 0.05 * tt, zz)
        o.rotation_euler = (tt * 2.1, tt * 1.4 + ph, tt * 0.9); o.hide_render = False
    # 天、雾、门洞补光：雾 → 海 / 森林
    def blend3(d):
        c = d[VOID]
        if isinstance(c, str): c0 = H(c); cs = H(d[SEA]); cf = H(d[FOREST]); return mixc(mixc(c0, cs, sea_s), cf, for_s)
        out = []
        for k in range(len(c)):
            a0, a1, a2 = d[VOID][k], d[SEA][k], d[FOREST][k]
            if isinstance(a0, str): out.append(mixc(mixc(H(a0), H(a1), sea_s), H(a2), for_s))
            else: out.append(lerp(lerp(a0, a1, sea_s), a2, for_s))
        return out
    hz, low, top, stren = blend3(SKYC)
    SKY.color_ramp.elements[0].color = low; SKY.color_ramp.elements[1].color = hz; SKY.color_ramp.elements[2].color = top
    sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value = stren
    fc = blend3(FOGC)
    for mr, em in FOGS:
        em.inputs['Color'].default_value = fc; em.inputs['Strength'].default_value = 1.0
        mr.inputs['From Min'].default_value = lerp(40.0, 8.0, for_s); mr.inputs['From Max'].default_value = lerp(520.0, 170.0, for_s)
        mr.inputs['To Max'].default_value = lerp(0.32, 0.55, for_s)
    spill.data.color = tuple(blend3({VOID: '#FFF6E8', SEA: '#BFD8F0', FOREST: '#DDEBB8'})[:3])
    spill.data.energy = lerp(45, 18, open_) * (0.6 + 0.4 * sstep(0.0, 0.8, t))
    loc, tgt, lens = cam_at(t)
    camo.location = loc; camo.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler(); cam_d.lens = lens
    cam_d.dof.focus_distance = (Vector((0, YF, 0.8)) - loc).length + 0.3

def scr(v):
    from bpy_extras.object_utils import world_to_camera_view
    p = world_to_camera_view(sc, camo, Vector(v)); return [round(p.x, 4), round(1 - p.y, 4), round(p.z, 3)]

os.makedirs(A.outdir, exist_ok=True)
nf = int(DUR * FPS)
frames = [int(round(float(x) * FPS)) for x in A.only.split(',')] if A.only else list(range(A.f0, nf if A.f1 < 0 else min(A.f1, nf)))
for fi in frames:
    t = fi / FPS
    if os.environ.get('SKIP_DONE') and os.path.exists(os.path.join(A.outdir, f'f{fi:05d}.json')): continue
    pose(t); bpy.context.view_layer.update()
    sc.render.filepath = os.path.join(A.outdir, f'f{fi:05d}.png'); bpy.ops.render.render(write_still=True)
    meta = {'t': t, 'f': fi, 'anch': {'door': scr((0, YF, (CZ0 + CZ1) / 2)), 'doortop': scr((0, YF, CZ1)), 'doorbot': scr((0, YF, CZ0))}}
    json.dump(meta, open(os.path.join(A.outdir, f'f{fi:05d}.json'), 'w'))
