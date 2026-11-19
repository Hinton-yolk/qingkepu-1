# 美术规范样张（用户 2026-11-19）：桌面精密模型摄影。
# 材质：半透明玻璃、磨砂金属、细腻塑料、陶瓷；颜色：暖白、石墨灰、青绿、琥珀橙、金属银灰（颜色只用来引导注意）；
# 柔和三点布光、明确前后景、相机动得少；物体分解、展开、排列、组合来解释，不弹信息卡。
# 用法：blender -b -P desk.py -- --shot 1 --out a.png --scale 0.5 --samples 64 --font F.otf --ui ui.png
import os, math
here = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(here, 'scene.py'), encoding='utf-8').read()
exec(_src[:_src.index('ANCH = {}')])

# ---------------- 五个色系 ----------------
WARM = '#F2EDE4'      # 暖白
WARM2 = '#E6DED2'
GRAPH = '#3B3E44'     # 石墨灰
GRAPH2 = '#5A5E66'
TEAL = '#2C9A92'      # 青绿
AMBER = '#E8902C'     # 琥珀橙
SILVER = '#B9BDC3'    # 金属银灰

def ceramic(col, rough=0.42):
    m, p = bsdf_mat('ceramic', **{'Base Color': hexc(col), 'Roughness': rough, 'Coat Weight': 0.35, 'Coat Roughness': 0.12,
                                  'Subsurface Weight': 0.08, 'Subsurface Scale': 0.02})
    return m

def frosted_metal(col=SILVER, rough=0.38):
    m, p = bsdf_mat('fmetal', **{'Base Color': hexc(col), 'Metallic': 1.0, 'Roughness': rough, 'Anisotropic': 0.2})
    return m

def fine_plastic(col, rough=0.3):
    m, p = bsdf_mat('plastic', **{'Base Color': hexc(col), 'Roughness': rough, 'Coat Weight': 0.2, 'Coat Roughness': 0.2})
    return m

def frosted_glass(col='#F4F6F7', rough=0.32):
    return glass(col, rough=rough)

def glow(col, s=3.0):
    return emit(col, s)

# ---------------- 环境：一张暖白桌面 + 无缝背景，柔和三点布光 ----------------
def desk_set(desk_col='#E9E2D7', wall_top='#E3DCD1', wall_bot='#C9C0B3'):
    # 相机看到的远处：暖灰无缝背景（不换色、不跳纯黑）
    world(wall_top, wall_bot, light='#FFF8F0', light_strength=0.18)
    # 桌面：带一点点纹理的暖白哑光面，延伸出去
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 10, 0))
    d = bpy.context.active_object
    m = bpy.data.materials.new('desk'); m.use_nodes = True; nt = m.node_tree; p = nt.nodes['Principled BSDF']
    p.inputs['Roughness'].default_value = 0.7; p.inputs['Coat Weight'].default_value = 0.04
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 60; noise.inputs['Detail'].default_value = 4
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = hexc(desk_col); ramp.color_ramp.elements[1].color = hexc(WARM2)
    ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[1].position = 0.75
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    d.data.materials.append(m)
    return d

def three_point(target=(0, 0, 1), key=1100, fill=260, rim=900, scale=1.0):
    tx, ty, tz = target
    area((tx - 6 * scale, ty - 6 * scale, tz + 7 * scale), target, key, 6 * scale, '#FFF3E4')     # 主光：左前上方，暖，大而柔
    area((tx + 7 * scale, ty - 4 * scale, tz + 2 * scale), target, fill, 7 * scale, '#E8F0F4')     # 补光：右前，冷，弱
    area((tx + 2 * scale, ty + 7 * scale, tz + 5 * scale), target, rim, 4 * scale, '#FFFFFF')      # 轮廓光：后上方

def tok(ch, loc, s=0.6, body=WARM, ink=GRAPH, rot=(0, 0, 0)):
    """字块：暖白陶瓷方块 + 石墨灰凸字"""
    ob = rbox((s, s * 0.62, s), loc, bevel=s * 0.14, mat=ceramic(body), rot=rot)
    t = text3d(ch, (0, 0, 0), s * 1.75, fine_plastic(ink, 0.35), extrude=0.012)
    M = Matrix.LocRotScale(Vector(loc), Euler(rot).to_quaternion(), None)
    t.matrix_world = M @ Matrix.Translation((0, -s * 0.31 - 0.004, -s * 0.03)) @ Euler((math.pi / 2, 0, 0)).to_matrix().to_4x4()
    return ob

def amber_q(loc, s=0.6, rot=(0, 0, 0)):
    """下一个要写的位置：琥珀色半透明玻璃块（注意力主色）"""
    ob = rbox((s, s * 0.62, s), loc, bevel=s * 0.15, mat=glass('#F2B866', 0.2), rot=rot)
    M = Matrix.LocRotScale(Vector(loc), Euler(rot).to_quaternion(), None)
    t = text3d('?', (0, 0, 0), s * 1.6, glow(AMBER, 3.0), extrude=0.04)
    t.matrix_world = M @ Matrix.Translation((0, -s * 0.33, -s * 0.03)) @ Euler((math.pi / 2, 0, 0)).to_matrix().to_4x4()
    return ob

# =====================================================================
if A.shot == 1:
    # 开头：桌上一台手机立在一个小金属支架上，AI 正在逐字回复；「去」从屏幕里浮出来，琥珀色「?」是下一个位置
    desk_set()
    three_point((0, 0, 2.2), key=1300, fill=300, rim=1100)
    ph = rbox((2.3, 0.34, 4.7), (0, 0, 2.6), bevel=0.4, seg=12, mat=frosted_metal('#C7CBD1', 0.3))
    bez = rbox((2.2, 0.02, 4.6), (0, -0.17, 0), bevel=0.32, seg=8, mat=fine_plastic('#17181B', 0.08)); bez.parent = ph
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.185, 0), rotation=(math.pi / 2, 0, 0))
    scr = bpy.context.active_object; scr.scale = (2.06, 4.46, 1)
    bpy.ops.object.transform_apply(scale=True)
    md = scr.modifiers.new('bev', 'BEVEL'); md.width = 0.28; md.segments = 8; md.affect = 'VERTICES'
    if A.ui: assign(scr, image_mat(A.ui, emit_strength=0.75))
    k1 = rbox((0.06, 0.14, 0.55), (1.16, 0, 1.0), bevel=0.025, mat=frosted_metal(SILVER))
    for o in (scr, k1): o.parent = ph
    ph.rotation_euler = (math.radians(-8), 0, math.radians(-22))
    # 支架：磨砂金属的小托
    rbox((1.6, 1.2, 0.12), (0.15, 0.5, 0.06), bevel=0.05, mat=frosted_metal('#AEB2B8', 0.42))
    rbox((1.4, 0.12, 0.6), (0.2, 0.95, 0.4), bevel=0.05, mat=frosted_metal('#AEB2B8', 0.42), rot=(math.radians(-12), 0, math.radians(-22)))
    tok('去', (1.55, -1.6, 3.0), s=0.92, rot=(0.12, 0.0, -0.3))
    amber_q((2.4, -1.15, 1.8), s=0.78, rot=(0.08, 0, -0.38))
    # 前景：一块虚掉的陶瓷字块和一支石墨色笔，给前后景
    tok('想', (-2.7, -4.6, 0.42), s=0.84, rot=(0, 0, 0.5))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=5.0, location=(2.4, -3.6, 0.12), rotation=(0, math.pi / 2, 0.5), vertices=6)
    o = bpy.context.active_object; assign(o, fine_plastic(GRAPH, 0.35))
    # 背景：远处一个银色金属块、一只陶瓷杯（虚）
    bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=1.9, location=(-3.6, 7.5, 0.95), vertices=64)
    o = bpy.context.active_object; smooth(o); assign(o, ceramic(WARM2, 0.35))
    rbox((2.2, 1.2, 0.8), (3.8, 9.0, 0.4), bevel=0.1, mat=frosted_metal(SILVER, 0.4))
    camera((0.9, -17.5, 3.9), (0.55, 0, 2.15), lens=44, focus=17.4, fstop=2.4)

elif A.shot == 2:
    # 第 6 拍：每一层都拿这串数和参数表乘一下、加起来，交给下一层。
    # 「模型」是一台桌上的精密仪器：磨砂金属框架里插着五块磨砂玻璃层板；一串数（陶瓷小块）正从下往上穿过第三层，
    # 穿过的地方，层板上的参数块（陶瓷，深浅 = 大小）被琥珀色点亮——一道道乘加；走过的层留下淡淡的琥珀色。
    desk_set()
    three_point((0, 0, 2.4), key=1200, fill=280, rim=1000)
    import random; rnd = random.Random(7)
    # 框架：两根立柱 + 底座
    rbox((5.6, 1.6, 0.25), (0, 0, 0.125), bevel=0.08, mat=frosted_metal('#A9AEB5', 0.42))
    for x in (-2.75, 2.75):
        rbox((0.16, 0.16, 5.2), (x, 0.55, 2.7), bevel=0.05, mat=frosted_metal(SILVER, 0.32))
    zs = [0.9 + k * 0.95 for k in range(5)]; cur = 2
    for k, z in enumerate(zs):
        passed = k < cur
        rbox((5.4, 1.6, 0.1), (0, 0.15, z), bevel=0.04, mat=frosted_glass('#F6E7D2' if passed else '#F1F3F4', 0.3))
        rbox((5.4, 0.06, 0.12), (0, -0.66, z), bevel=0.02, mat=frosted_metal(SILVER, 0.3))   # 层板前沿一道银边
        for r in range(3):
            for c in range(11):
                v = rnd.random()
                col = '#' + ''.join(f'{int(a + (b - a) * v):02x}' for a, b in zip((0xF2, 0xED, 0xE4), (0x3B, 0x3E, 0x44)))   # 暖白 → 石墨，深浅 = 大小
                lit = (k == cur and c == int(10 * 0.62) and True)
                rbox((0.36, 0.3, 0.07 + 0.08 * v), (-2.3 + c * 0.46, -0.15 + r * 0.38, z + 0.09 + 0.04 * v), bevel=0.03, seg=3,
                     mat=glow(AMBER, 2.5) if (k == cur and c in (5, 6) and r == 1) else ceramic(col, 0.4))
    # 一串数：一排陶瓷小块（石墨底、暖白数字），正竖着往上穿过第 3 层；穿过的位置琥珀色亮
    for i, dgt in enumerate('5280731946'):
        x = -2.1 + i * 0.46
        z = zs[cur] - 0.32
        rbox((0.32, 0.22, 0.34), (x, -0.75, z), bevel=0.05, mat=ceramic(GRAPH, 0.35))
        text3d(dgt, (x, -0.87, z - 0.02), 0.62, ceramic(WARM, 0.4), extrude=0.008, rot=(math.pi / 2, 0, 0))
    for i in range(10):   # 上一层出来的新的一串数（还在形成）：琥珀色细光点
        x = -2.1 + i * 0.46
        if i < 6: sphere(0.05, (x, -0.75, zs[cur] + 0.35), glow(AMBER, 4.0))
    # 前景：虚掉的一块参数陶瓷片；背景：远处桌上的金属块
    rbox((1.2, 0.5, 0.18), (-2.6, -4.2, 0.09), bevel=0.06, mat=ceramic('#9A9690', 0.4), rot=(0, 0, 0.4))
    rbox((2.4, 1.4, 1.0), (4.2, 9, 0.5), bevel=0.1, mat=frosted_metal(SILVER, 0.4))
    camera((2.8, -15.0, 9.5), (0.0, 0, 2.2), lens=46, focus=16.6, fstop=3.5)

elif A.shot == 3:
    # 第 24–25 拍：桌上一块显卡板。显存颗粒（磨砂金属封装）围着计算芯片；一列参数陶瓷片沿着板上的通道从显存搬向芯片；
    # 芯片里的小核大多是暗的石墨色，参数到了的那几格才亮青绿；旁边两根桌面量杆：「搬」很长（银灰），「算」只有一小截（琥珀）。
    desk_set()
    three_point((0, 0, 0.5), key=1200, fill=260, rim=1000)
    rbox((6.4, 3.8, 0.12), (0, 0.6, 0.06), bevel=0.03, mat=fine_plastic('#2F3236', 0.45))           # 板（石墨）
    rbox((2.0, 2.0, 0.18), (0.9, 0.7, 0.21), bevel=0.05, mat=frosted_metal('#8E939A', 0.35))        # 芯片封装
    import random; rnd = random.Random(5)
    for i in range(10):
        for j in range(10):
            lit = (i in (6, 7)) and rnd.random() < 0.6
            rbox((0.12, 0.12, 0.03), (0.9 - 0.72 + i * 0.16, 0.7 - 0.72 + j * 0.16, 0.315), bevel=0.01, seg=2,
                 mat=glow(TEAL, 2.4) if lit else ceramic('#45494F', 0.45))
    mem = [(-2.2, 1.9), (-2.2, 0.7), (-2.2, -0.5), (3.0, 1.9), (3.0, 0.7), (3.0, -0.5)]
    for (x, y) in mem:
        rbox((0.9, 0.7, 0.14), (x, y, 0.19), bevel=0.04, mat=frosted_metal('#C3C7CD', 0.4))
    # 通道 + 一列参数陶瓷片（暖白→石墨的深浅），正从左边显存往芯片搬
    rbox((2.0, 0.24, 0.02), (-0.9, 0.7, 0.13), bevel=0.01, mat=frosted_metal('#9EA3AA', 0.3))
    for k in range(7):
        v = (k * 0.37) % 1
        col = '#' + ''.join(f'{int(a + (b - a) * v):02x}' for a, b in zip((0xF2, 0xED, 0xE4), (0x3B, 0x3E, 0x44)))
        rbox((0.2, 0.18, 0.08), (-1.75 + k * 0.26, 0.7, 0.2), bevel=0.03, mat=ceramic(col, 0.4))
    # 「16 GB」：刻在显存颗粒上（不弹卡片）
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = '16 GB'
    cu.font = bpy.data.fonts.load('/usr/share/fonts/truetype/smiley-sans/SmileySans-Oblique.ttf')
    cu.size = 0.55; cu.extrude = 0.02; cu.align_x = 'CENTER'
    ob = bpy.data.objects.new('t', cu); bpy.context.collection.objects.link(ob); ob.location = (-2.2, -1.35, 0.14)
    cu.materials.append(fine_plastic(GRAPH, 0.3))
    # 两根桌面量杆：搬（长，银灰） vs 算（按比例只有一小截，琥珀），放在板前面的桌上
    rbox((5.6, 0.22, 0.22), (0.0, -2.2, 0.11), bevel=0.08, mat=frosted_metal(SILVER, 0.3))
    rbox((0.05, 0.22, 0.22), (-2.775, -2.8, 0.11), bevel=0.01, mat=ceramic(AMBER, 0.3))
    bpy.ops.mesh.primitive_torus_add(major_radius=0.28, minor_radius=0.025, location=(-2.775, -2.8, 0.14), rotation=(0, 0, 0))
    o = bpy.context.active_object; smooth(o); assign(o, frosted_metal(SILVER, 0.25))
    # 前景虚化：桌边一颗陶瓷字块
    tok('海', (3.6, -4.2, 0.36), s=0.72, rot=(0, 0, -0.4))
    camera((0.5, -13.0, 12.5), (0.2, -0.6, 0.0), lens=40, focus=18.0, fstop=4.0)

bpy.ops.render.render(write_still=True)
