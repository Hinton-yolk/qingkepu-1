# EP.01 34 拍 · 按用户 2026-11-19 的美术规范重做（桌面精密模型摄影）。
# 复用 film3d.py 的节拍结构、时间表、自动取景和锚点；这里把材质、颜色、环境、灯光换成美术规范，
# 并把像信息卡的拍（排行条）改成实物（陶瓷字块立在高低不同的柱子上）。
# 用法：blender -b -P film_desk.py -- --outdir DIR --scale 0.4 --samples 24 --font F.otf --ui_dir DIR [--beats ...] [--times ...]
import os, math
os.environ['FILM3D_LIB'] = '1'
_me = os.path.abspath(__file__); _here = os.path.dirname(_me)
_g = globals(); _g['__file__'] = os.path.join(_here, 'film3d.py')
exec(open(os.path.join(_here, 'film3d.py'), encoding='utf-8').read(), _g)
_g['__file__'] = _me

# ---------------- 五个色系（11-19「色度略提一点」：比样张 v1 略饱和） ----------------
WARM, WARM2 = '#EFE5D5', '#E0D3BF'
GRAPH, GRAPH2 = '#393C42', '#5B5F67'
TEAL = '#1F9A8E'
AMBER = '#DC8A3A'
AMBER_L = '#EBA45A'
SILVER = '#B6BBC2'

_bsdf = bsdf_mat
_glass0 = glass
_emit0 = emit
_world0 = world

def m_ceramic(col, rough=0.42):
    m, p = _bsdf('ceramic', **{'Base Color': hexc(col), 'Roughness': max(0.3, rough), 'Coat Weight': 0.35, 'Coat Roughness': 0.12,
                               'Subsurface Weight': 0.06, 'Subsurface Scale': 0.02})
    return m
def m_metal(col=SILVER, rough=0.36):
    m, p = _bsdf('fmetal', **{'Base Color': hexc(col), 'Metallic': 1.0, 'Roughness': rough, 'Anisotropic': 0.2})
    return m
def m_plastic(col, rough=0.32):
    m, p = _bsdf('plastic', **{'Base Color': hexc(col), 'Roughness': rough, 'Coat Weight': 0.2, 'Coat Roughness': 0.2})
    return m
def m_glass(col='#EEF0F1', rough=0.3):
    return _glass0(col, rough=rough)

# 旧颜色 → (材质, 新颜色)。颜色只用来引导注意：琥珀 = 注意力主色，青绿 = 次要强调
CMAP = {
    'FF6F96': ('ceramic', '#D9C7AE'), '4A8DFF': ('ceramic', '#575B62'),          # 参数：浅陶瓷 / 深陶瓷（深浅 = 大小，不分正负颜色）
    'FFC93C': ('ceramic', AMBER), 'FFD84A': ('ceramic', AMBER), '2FCF7E': ('ceramic', TEAL),
    'FBF8F2': ('ceramic', WARM), 'FDFBF6': ('ceramic', WARM), '1E2440': ('plastic', GRAPH),
    'FFD45A': ('ceramic', AMBER_L), 'E5DBFF': ('glass', '#EAE6DF'), 'BDB6CF': ('ceramic', '#CAC3B9'),
    'A9A5BC': ('ceramic', '#7C7872'), '7D7990': ('plastic', '#57534D'), '7F6BE0': ('metal', '#9FA5AD'),
    'FFFFFF': ('metal', SILVER), 'FAF8FF': ('glass', '#F0F1F1'), 'FFEDB8': ('glass', '#F1D2A8'),
    'E9E5FA': ('metal', SILVER), 'F2EEFF': ('ceramic', WARM2), 'EDE7FF': ('ceramic', WARM2), 'E8E2FF': ('ceramic', '#D8CBB8'),
    'D9D0FA': ('ceramic', '#CDBFAA'), '6F86C9': ('metal', '#C2C6CC'), '2B2F3D': ('plastic', GRAPH), '1F5E44': ('ceramic', '#464A50'),
    '1D2350': ('ceramic', GRAPH), 'F3F0FA': ('metal', '#A9AEB5'), 'FFF8E6': ('ceramic', '#F2EADC'), 'EEF3FF': ('glass', '#EEF0F1'),
    '121318': ('plastic', '#141518'), 'F4F2FB': ('glass', '#F0F1F1'), 'FFE7A6': ('glass', '#F1D2A8'),
}
MAKE = {'ceramic': m_ceramic, 'metal': m_metal, 'plastic': m_plastic, 'glass': m_glass}
def _map(col):
    return CMAP.get(col.lstrip('#').upper(), ('ceramic', col))

def candy(col, rough=0.22, coat=1.0, sss=0.0):
    kind, c = _map(col); return MAKE[kind](c, rough if kind != 'glass' else 0.3)
EMAP = {'FFC93C': AMBER, 'FFD84A': AMBER, '2FCF7E': TEAL, 'FFF3C4': '#F0BE80', '8FE3FF': '#F3EBDD', 'FFFFFF': '#F7EFE2', 'F7EFE2': '#F7EFE2'}
def emit(col, strength=4.0):
    return _emit0(EMAP.get(col.lstrip('#').upper(), col), strength * 0.85)
GMAP = {'FFE07A': '#F0B565', 'FFE58A': '#F0B565', 'F4F7FF': '#EEF0F1', 'D9D2FF': '#E7E9EA', 'FFFFFF': '#F2F2F0'}
def glass(col, rough=0.08, ior=1.45, tint_density=1.0):
    return _glass0(GMAP.get(col.lstrip('#').upper(), col), rough=max(rough, 0.18))
def gradient_glass(c1, c2, axis='X', rough=0.12, lo=-1, hi=1):
    return _glass0('#EDEBE6', rough=0.25)                                          # 玻璃带：中性磨砂玻璃
def satin_metal(col, rough=0.32):
    return m_metal('#B4B8BE' if col.upper() in ('#BFB6E6',) else col, rough)
PINK, BLUE, YEL, GREEN = '#FF6F96', '#4A8DFF', '#FFC93C', '#2FCF7E'                # 旧名字保留，经 CMAP 映射

def world(top, bottom, light='#FFFFFF', light_strength=0.55, halo=None):
    _world0('#E8DCCA', '#CDBFAB', light='#FFF5EA', light_strength=0.45)            # 全片一个环境：暖灰无缝背景；环境光够，远处桌面不发黑

def lights(target=(0, 0, 0), key=900, fill=320, rim=900):
    tx, ty, tz = target
    area((tx - 7, ty - 7, tz + 6), target, 750, 10, '#FFF1E0')    # 主光：左前，暖，大而柔（11-19：别太亮）
    area((tx + 8, ty - 5, tz + 2), target, 260, 8, '#E6EEF2')     # 补光：右前，冷，弱
    area((tx + 2, ty + 8, tz + 5), target, 800, 5, '#FFFFFF')     # 轮廓光：后上方

def check(loc, s=0.32):
    bpy.ops.mesh.primitive_cylinder_add(radius=s, depth=0.08, location=loc, rotation=(math.pi / 2, 0, 0), vertices=48)
    o = bpy.context.active_object; smooth(o); assign(o, m_ceramic(TEAL, 0.3))
    md = o.modifiers.new('b', 'BEVEL'); md.width = 0.03; md.segments = 3
    x, y, z = loc
    rbox((s * 0.22, 0.04, s * 0.6), (x - s * 0.2, y - 0.06, z - s * 0.08), bevel=0.02, mat=m_ceramic(WARM, 0.3), rot=(0, math.radians(-45), 0))
    rbox((s * 0.22, 0.04, s * 1.0), (x + s * 0.15, y - 0.06, z + s * 0.05), bevel=0.02, mat=m_ceramic(WARM, 0.3), rot=(0, math.radians(35), 0))

def xmark(loc, size=1.0, rot_y=0.0, thick=0.12):
    """作废：石墨灰 ✕，盖在压亮的浅灰字块上（审核：✕ 要和字块分得开）"""
    thick = max(thick, 0.1); size *= 1.1
    for a in (math.pi / 4, -math.pi / 4):
        rbox((size, thick * 0.6, thick), loc, bevel=thick * 0.45, mat=m_plastic(GRAPH, 0.3), rot=(0, a + rot_y, 0))

# ---------------- 像信息卡的拍改成实物 ----------------
def score_columns(cands, x0=-2.2, step=1.05, base=0.0, H=3.0, s=0.62, tail=0):
    """打分：每个候选字立在一根陶瓷柱上，柱高 = 分数；第一名琥珀色。tail = 后面再排多少根越来越矮的柱（词表长尾）"""
    top = cands[0][1]
    for i, (ch, p) in enumerate(cands):
        h = max(0.08, H * p / top); x = x0 + i * step
        rbox((0.5, 0.5, h), (x, 0, base + h / 2), bevel=0.06, mat=m_ceramic(AMBER if i == 0 else '#D6CBB9', 0.35))
        token(ch, (x, -0.05, base + h + s / 2 + 0.02), s=s, body='#FFD45A' if i == 0 else '#FBF8F2')
        ANCH[f'p{i}'] = (x + 0.35, -0.3, base + h + s + 0.25)
    for j in range(tail):   # 长尾：往后、往右排下去，越来越矮、越来越淡，望不到头
        k = len(cands) + j; x = x0 + k * step * (1 - 0.012 * j); y = 0.55 * j
        h = max(0.05, H * 0.09 * math.exp(-j / 14)); col = '#CDBFAA' if j < 12 else '#D9CDBA'
        rbox((0.42, 0.42, h), (x, y, base + h / 2), bevel=0.04, mat=m_ceramic(col, 0.4))

def o6(u, stack=True):   # 给每个可能的下一个字打分：候选字立在高低不同的柱子上（柱高 = 分数），从模型出口那一侧排出来
    reset('lilac'); lights((0, 0, 1))
    g = ease(seg(u, 0.05, 0.6))
    cands = [('海', 0.41 * g + 0.001), ('睡', 0.18 * g + 0.001), ('爬', 0.12 * g + 0.001), ('吃', 0.09 * g + 0.001)]
    # 模型在上一拍已经交代过，这一拍只留候选字，柱子能放大
    score_columns(cands, x0=-1.6, step=1.05, base=0.0)
    cam((2.0, -16, 4.0), (0.0, 0, 1.4), 55, 4.0, 16)

def n_tail(u):      # 补 2：其实它认识的十几万个字，每个都打了分：柱子一路排到远处，望不到头
    reset('lilac'); lights((0, 0, 1))
    g = ease(seg(u, 0.1, 0.8))
    cands = [('海', 0.41), ('睡', 0.18), ('爬', 0.12), ('吃', 0.09)]
    score_columns(cands, x0=-1.6, step=1.05, base=0.0, tail=int(60 * g))
    cam((-3.2, -11, 3.6), (2.2, 6, 0.9), 44, 4.0, 12)

def n_mem16(u):     # 补 4：写一个字要搬 16 GB——「16 GB」刻在显存那摞上（观众：别让人以为这个字有 16 GB）
    mem_scene(u, fan=False)
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = '16 GB'
    cu.font = bpy.data.fonts.load(SMILEY_TTF)
    cu.size = 0.62; cu.extrude = 0.015; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    ob = bpy.data.objects.new('t', cu); bpy.context.collection.objects.link(ob); ob.location = (-2.6, -0.42, -1.15); ob.rotation_euler = (math.pi / 2, 0, 0)
    cu.materials.append(m_plastic(GRAPH, 0.3))
    ANCH['mem'] = (-2.6, 0, -0.2)
    cam((-0.2, -22, 4.0), (-0.3, 0, 0.4), 46, 4.0, 22)

FN_NOAUTO = {'o1', 'o2', 'o3', 'o23', 'o24', 'o25', 'n_tail'}   # 长尾要伸出画面，不自动取景

def add_desk(fn, u=0.5):
    """在所有物体的最低点放一张暖白桌面（带细纹理），像拍桌上的精密模型"""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get(); zmin = 1e9
    for o in bpy.data.objects:
        if o.type not in ('MESH', 'CURVE', 'FONT'): continue
        oe = o.evaluated_get(dg)
        for c in oe.bound_box: zmin = min(zmin, (oe.matrix_world @ Vector(c)).z)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 40, zmin - 0.005))
    d = bpy.context.active_object
    m = bpy.data.materials.new('desk'); m.use_nodes = True; nt = m.node_tree; p = nt.nodes['Principled BSDF']
    p.inputs['Roughness'].default_value = 0.88; p.inputs['Coat Weight'].default_value = 0.0; p.inputs['Specular IOR Level'].default_value = 0.15   # 桌面不反出灯板的「窗影」
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 40; noise.inputs['Detail'].default_value = 4
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = hexc('#E9DDCB'); ramp.color_ramp.elements[1].color = hexc('#DCCCB5')
    ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[1].position = 0.75
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    d.data.materials.append(m)
    # 每拍里相机都在慢慢动（推近约 4%、横移约 2%），画面不完全静止；转场在 2D 合成里做
    cam_o = sc.camera
    if cam_o:
        q = cam_o.matrix_world.to_quaternion(); fwd = q @ Vector((0, 0, -1)); rgt = q @ Vector((1, 0, 0))
        dd = cam_o.data.dof.focus_distance
        cam_o.location = cam_o.location + fwd * (0.04 * dd * ease(u)) + rgt * (0.02 * dd * (u - 0.5))
        cam_o.data.dof.focus_distance = dd * (1 - 0.04 * ease(u))

# 草稿接触表的代表时刻：沿用 film3d 的 CU
run_jobs(post=add_desk)
