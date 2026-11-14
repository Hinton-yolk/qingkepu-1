"""Blender PoC 03 — 用 Cycles 复刻 Seedance 2.5 那段的「看起来」（静帧）。

目标帧：refs/target_seedance25_f100.png（Seedance 2.5，4.17 s）。只复刻布光、景深、材质、色调和构图感觉；
几何按真实装配关系：网卡平放在深色反光台面上，笼子入口在板边，OSFP 模块从板外插入、已经到位，前端朝镜头。

单位：米（代码里用 MM 换算）。+Y 指向板外，模块沿 -Y 插入；+Z 向上；PCB 上表面 z = 0。
尺寸是真实器件的量级（见 FACTS.md，标了待核），不是精确图纸。

用法（本目录）：
  blender -b --factory-startup --python-exit-code 1 --python build_hero.py -- still [--res 540] [--spp 64] [--out out/hero.png]
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

for _t in (os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools'),                       # 云端打包后的目录
           os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'tools')):  # 仓库里
    if os.path.exists(os.path.join(_t, 'polyhaven_blender.py')):
        sys.path.insert(0, _t)
        break
import polyhaven_blender as ph  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
MM = 0.001
random.seed(3)

# ---------- 尺寸（mm） ----------
MOD_W, MOD_H, MOD_L = 22.58, 13.0, 107.8
CAGE_W, CAGE_H, CAGE_L, SHEET = 24.6, 15.0, 86.0, 0.3
MOD_Z0 = SHEET + 0.4                     # 模块底面高度（笼子底板 + 间隙）
MOD_FRONT_Y = -84.0 + MOD_L              # 模块后端在 y = -84（离笼子后壁 2 mm）→ 前端面 y ≈ 23.8
BOARD_EDGE_Y = -2.0                      # 板边比笼口靠里 2 mm（笼口略伸出板边）


# ---------- 材质 ----------
def principled(name, base, metallic=0.0, rough=0.5, aniso=0.0, coat=0.0, spec=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*base, 1)
    b.inputs['Metallic'].default_value = metallic
    b.inputs['Roughness'].default_value = rough
    b.inputs['Anisotropic'].default_value = aniso
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Specular IOR Level'].default_value = spec
    return m, b


def brushed(m, b, rough_lo, rough_hi, axis='Y', scale=900.0):
    """拉丝纹理：沿 axis 方向拉长的噪声控制粗糙度和凹凸，切线也沿 axis。"""
    nt = m.node_tree
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    sx, sy = (scale, scale * 0.012) if axis == 'Y' else (scale * 0.012, scale)
    mp.inputs['Scale'].default_value = (sx, sy, scale)
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 1.0
    nz.inputs['Detail'].default_value = 8.0
    ramp = nt.nodes.new('ShaderNodeMapRange')
    ramp.inputs['To Min'].default_value = rough_lo
    ramp.inputs['To Max'].default_value = rough_hi
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Value'])
    # 不完美：大块污渍（粗糙度斑驳）+ 稀疏细划痕（Voronoi 边线）
    sm = nt.nodes.new('ShaderNodeTexNoise')
    sm.inputs['Scale'].default_value = 70.0
    sm.inputs['Detail'].default_value = 3.0
    nt.links.new(tc.outputs['Object'], sm.inputs['Vector'])
    smr = nt.nodes.new('ShaderNodeMapRange')
    smr.inputs['From Min'].default_value = 0.52
    smr.inputs['From Max'].default_value = 0.72
    smr.inputs['To Min'].default_value = 0.0
    smr.inputs['To Max'].default_value = 0.14
    nt.links.new(sm.outputs['Fac'], smr.inputs['Value'])
    vo = nt.nodes.new('ShaderNodeTexVoronoi')
    vo.feature = 'DISTANCE_TO_EDGE'
    vo.inputs['Scale'].default_value = 260.0
    nt.links.new(tc.outputs['Object'], vo.inputs['Vector'])
    scr = nt.nodes.new('ShaderNodeMapRange')
    scr.inputs['From Min'].default_value = 0.0
    scr.inputs['From Max'].default_value = 0.012
    scr.inputs['To Min'].default_value = 1.0
    scr.inputs['To Max'].default_value = 0.0
    nt.links.new(vo.outputs['Distance'], scr.inputs['Value'])
    sparse = nt.nodes.new('ShaderNodeTexNoise')
    sparse.inputs['Scale'].default_value = 40.0
    nt.links.new(tc.outputs['Object'], sparse.inputs['Vector'])
    spr = nt.nodes.new('ShaderNodeMapRange')
    spr.inputs['From Min'].default_value = 0.55
    spr.inputs['From Max'].default_value = 0.65
    nt.links.new(sparse.outputs['Fac'], spr.inputs['Value'])
    scm = nt.nodes.new('ShaderNodeMath')
    scm.operation = 'MULTIPLY'
    nt.links.new(scr.outputs['Result'], scm.inputs[0])
    nt.links.new(spr.outputs['Result'], scm.inputs[1])
    scw = nt.nodes.new('ShaderNodeMath')
    scw.operation = 'MULTIPLY'
    scw.inputs[1].default_value = 0.16
    nt.links.new(scm.outputs['Value'], scw.inputs[0])
    add1 = nt.nodes.new('ShaderNodeMath')
    add1.operation = 'ADD'
    nt.links.new(ramp.outputs['Result'], add1.inputs[0])
    nt.links.new(smr.outputs['Result'], add1.inputs[1])
    add2 = nt.nodes.new('ShaderNodeMath')
    add2.operation = 'ADD'
    add2.use_clamp = True
    nt.links.new(add1.outputs['Value'], add2.inputs[0])
    nt.links.new(scw.outputs['Value'], add2.inputs[1])
    nt.links.new(add2.outputs['Value'], b.inputs['Roughness'])
    hgt = nt.nodes.new('ShaderNodeMath')
    hgt.operation = 'SUBTRACT'
    nt.links.new(nz.outputs['Fac'], hgt.inputs[0])
    nt.links.new(scm.outputs['Value'], hgt.inputs[1])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.06
    bump.inputs['Distance'].default_value = 0.00002
    nt.links.new(hgt.outputs['Value'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    tg = nt.nodes.new('ShaderNodeTangent')
    tg.direction_type = 'RADIAL'
    tg.axis = 'X' if axis == 'Y' else 'Y'
    nt.links.new(tg.outputs['Tangent'], b.inputs['Tangent'])


def make_materials():
    M = {}
    m, b = principled('Alu_brushed', (0.80, 0.80, 0.81), 1.0, 0.25, aniso=0.6)
    brushed(m, b, 0.18, 0.34)
    M['alu'] = m
    m, b = principled('Nickel_cage', (0.74, 0.73, 0.70), 1.0, 0.22, aniso=0.3)
    brushed(m, b, 0.16, 0.30, scale=1400.0)
    M['nickel'] = m
    m, b = principled('Pulltab_lime', (0.42, 0.72, 0.06), 0.0, 0.48, spec=0.4)
    b.inputs['Subsurface Weight'].default_value = 0.35
    b.inputs['Subsurface Scale'].default_value = 0.0015
    M['tab'] = m
    M['mpo'] = principled('MPO_darkplastic', (0.02, 0.021, 0.024), 0.0, 0.6, spec=0.3)[0]
    M['hole'] = principled('Hole_black', (0.004, 0.004, 0.005), 0.0, 0.8)[0]
    M['screw'] = principled('Screw_steel', (0.6, 0.6, 0.62), 1.0, 0.3)[0]
    M['gold'] = principled('ENIG_gold', (1.0, 0.76, 0.36), 1.0, 0.22)[0]
    M['heatsink'] = principled('Heatsink_black_anod', (0.025, 0.026, 0.03), 0.6, 0.38)[0]
    M['ic'] = principled('IC_black_epoxy', (0.02, 0.02, 0.022), 0.0, 0.55)[0]
    M['cap'] = principled('MLCC_tan', (0.42, 0.30, 0.18), 0.0, 0.5)[0]
    M['res'] = principled('Resistor_black', (0.015, 0.015, 0.017), 0.0, 0.35)[0]
    M['tin'] = principled('Tin_terminal', (0.75, 0.75, 0.76), 1.0, 0.3)[0]
    M['inductor'] = principled('Inductor_gray', (0.18, 0.18, 0.19), 0.3, 0.5)[0]
    M['desk'] = principled('Desk_dark', (0.004, 0.0045, 0.006), 0.0, 0.4, spec=0.3)[0]
    M['backdrop'] = principled('Backdrop', (0.01, 0.011, 0.014), 0.0, 0.7)[0]
    M['fr4'] = principled('FR4_edge', (0.55, 0.50, 0.25), 0.0, 0.6)[0]
    # PCB：阻焊层绿色 + 走线（略浅、微凸）+ 沉金焊盘
    m, b = principled('PCB_soldermask', (0.02, 0.12, 0.06), 0.0, 0.32, coat=0.6)
    nt = m.node_tree
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1 / 0.12, 1 / 0.12, 1)
    mp.inputs['Location'].default_value = (0.5, 0.5, 0)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    tr = nt.nodes.new('ShaderNodeTexImage')
    tr.image = bpy.data.images.load(os.path.join(HERE, 'assets_dl', 'pcb_trace_mask.png'))
    tr.image.colorspace_settings.name = 'Non-Color'
    tr.extension = 'REPEAT'
    pd = nt.nodes.new('ShaderNodeTexImage')
    pd.image = bpy.data.images.load(os.path.join(HERE, 'assets_dl', 'pcb_pad_mask.png'))
    pd.image.colorspace_settings.name = 'Non-Color'
    pd.extension = 'REPEAT'
    for t in (tr, pd):
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
    mixc = nt.nodes.new('ShaderNodeMix')
    mixc.data_type = 'RGBA'
    mixc.inputs['A'].default_value = (0.02, 0.12, 0.06, 1)
    mixc.inputs['B'].default_value = (0.08, 0.30, 0.12, 1)
    nt.links.new(tr.outputs['Color'], mixc.inputs['Factor'])
    gold_bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    gold_bsdf.inputs['Base Color'].default_value = (1.0, 0.76, 0.36, 1)
    gold_bsdf.inputs['Metallic'].default_value = 1.0
    gold_bsdf.inputs['Roughness'].default_value = 0.25
    sk = nt.nodes.new('ShaderNodeTexImage')
    sk.image = bpy.data.images.load(os.path.join(HERE, 'assets_dl', 'pcb_silk_mask.png'))
    sk.image.colorspace_settings.name = 'Non-Color'
    nt.links.new(mp.outputs['Vector'], sk.inputs['Vector'])
    mixk = nt.nodes.new('ShaderNodeMix')
    mixk.data_type = 'RGBA'
    mixk.inputs['B'].default_value = (0.85, 0.86, 0.82, 1)
    nt.links.new(mixc.outputs['Result'], mixk.inputs['A'])
    nt.links.new(sk.outputs['Color'], mixk.inputs['Factor'])
    nt.links.new(mixk.outputs['Result'], b.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.6
    bump.inputs['Distance'].default_value = 0.00003
    nt.links.new(tr.outputs['Color'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    mixs = nt.nodes.new('ShaderNodeMixShader')
    out = nt.nodes['Material Output']
    nt.links.new(pd.outputs['Color'], mixs.inputs['Fac'])
    nt.links.new(b.outputs['BSDF'], mixs.inputs[1])
    nt.links.new(gold_bsdf.outputs['BSDF'], mixs.inputs[2])
    nt.links.new(mixs.outputs['Shader'], out.inputs['Surface'])
    M['pcb'] = m
    return M


# ---------- 几何工具 ----------
def box(name, x0, x1, y0, y1, z0, z1, mat, bevel=0.0, parent=None):
    """按 mm 范围建方块，可选倒角（mm）。"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=((x0 + x1) / 2 * MM, (y0 + y1) / 2 * MM, (z0 + z1) / 2 * MM))
    o = bpy.context.active_object
    o.name = name
    o.scale = ((x1 - x0) * MM, (y1 - y0) * MM, (z1 - z0) * MM)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        o.data.materials.append(mat)
    if bevel > 0:
        bv = o.modifiers.new('bevel', 'BEVEL')
        bv.width = bevel * MM
        bv.segments = 3
        bv.limit_method = 'ANGLE'
        bv.harden_normals = False
    if parent:
        o.parent = parent
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def cutter_collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    c.hide_render = True
    return c


def add_cutter(coll, x0, x1, y0, y1, z0, z1, parent=None):
    o = box('cut', x0, x1, y0, y1, z0, z1, None, 0, parent)
    for c in o.users_collection:
        c.objects.unlink(o)
    coll.objects.link(o)
    o.display_type = 'WIRE'
    o.hide_render = True
    return o


def boolean(obj, coll, bevel=0.0):
    md = obj.modifiers.new('cut', 'BOOLEAN')
    md.operation = 'DIFFERENCE'
    md.operand_type = 'COLLECTION'
    md.collection = coll
    md.solver = 'EXACT'
    # 倒角放在布尔之后
    for m in list(obj.modifiers):
        if m.type == 'BEVEL':
            obj.modifiers.remove(m)
    if bevel > 0:
        bv = obj.modifiers.new('bevel', 'BEVEL')
        bv.width = bevel * MM
        bv.segments = 2
        bv.limit_method = 'ANGLE'
        bv.angle_limit = math.radians(40)


# ---------- 光模块（局部坐标：前端面在 y = 0，向 -Y 延伸） ----------
def build_module(M):
    root = bpy.data.objects.new('OSFP_module', None)
    bpy.context.scene.collection.objects.link(root)
    hw = MOD_W / 2
    # 下半主体
    box('mod_body', -hw, hw, -MOD_L, -2.0, 0.0, 9.0, M['alu'], 0.45, root)
    # 鳍片底板 + 纵向鳍片（散热器集成在模块上）
    box('mod_finbase', -hw, hw, -100.0, -24.5, 9.0, 10.0, M['alu'], 0.3, root)
    nfin, t = 11, 0.75
    pitch = (MOD_W - 2.4 - t) / (nfin - 1)
    for i in range(nfin):
        x = -hw + 1.2 + i * pitch
        box(f'mod_fin{i}', x, x + t, -99.0, -26.0, 10.0, MOD_H, M['alu'], 0.2, root)
    # 前段实心盖（两颗螺丝），和鳍片段之间留一条分缝
    box('mod_nose_top', -hw, hw, -24.0, -2.0, 9.0, MOD_H, M['alu'], 0.45, root)
    for sx in (-7.0, 7.0):
        bpy.ops.mesh.primitive_cylinder_add(radius=1.25 * MM, depth=0.5 * MM, location=(sx * MM, -7.0 * MM, (MOD_H + 0.15) * MM))
        s = bpy.context.active_object
        s.name = 'mod_screw'
        s.data.materials.append(M['screw'])
        s.parent = root
        for a in (0, 90):
            c = box('mod_screw_slot', sx - 0.8, sx + 0.8, -7.18, -6.82, MOD_H + 0.25, MOD_H + 0.45, M['hole'], 0, root)
            c.rotation_euler = (0, 0, math.radians(a))
            c.location = (sx * MM, -7.0 * MM, (MOD_H + 0.35) * MM)
    # 侧面的锁扣窗口（浅槽）
    for sx in (-1, 1):
        x = sx * (hw + 0.01)
        box('mod_latch', min(x, x + sx * 0.12), max(x, x + sx * 0.12), -46.0, -34.0, 2.5, 5.0, M['hole'], 0, root)
    # 前框 + 凹进去的接口区
    bez = box('mod_bezel', -hw, hw, -2.0, 0.0, 0.0, MOD_H, M['alu'], 0, root)
    cc = cutter_collection('cut_bezel')
    add_cutter(cc, -9.6, 9.6, -3.0, 0.5, 1.4, 11.6, root)
    boolean(bez, cc, bevel=0.3)
    # 双 MPO 插座：深色塑料外壳 + 内腔
    for cx in (-4.75, 4.75):
        sh = box('mpo_shroud', cx - 4.3, cx + 4.3, -6.0, -0.9, 1.6, 11.4, M['mpo'], 0, root)
        cc = cutter_collection('cut_mpo')
        add_cutter(cc, cx - 3.3, cx + 3.3, -1.9, 0.0, 3.6, 9.4, root)
        boolean(sh, cc, bevel=0.25)
        box('mpo_cavity', cx - 3.3, cx + 3.3, -1.98, -1.85, 3.6, 9.4, M['hole'], 0, root)      # 内腔底，挡在主体前表面前面
        box('mpo_ferrule', cx - 2.6, cx + 2.6, -1.85, -1.25, 5.6, 7.4, M['mpo'], 0.12, root)  # 插芯
    # 拉环：一个水平的环（外圈 - 内圈），整体向下倾 8°
    tab = build_pulltab(M)
    tab.parent = root
    root.location = (0, MOD_FRONT_Y * MM, MOD_Z0 * MM)
    return root


def rounded_rect(cu, x0, x1, y0, y1, r):
    sp = cu.splines.new('POLY')
    pts = []
    for (cx, cy, a0) in ((x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270)):
        for k in range(9):
            a = math.radians(a0 + k * 90 / 8)
            pts.append(((cx + r * math.cos(a)) * MM, (cy + r * math.sin(a)) * MM, 0))
    sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts):
        p.co = (*c, 1)
    sp.use_cyclic_u = True


def u_outline(cu, ox=13.4, ix=9.8, y0=-6.0, oy=31.0, iy=23.5, ro=7.0, ri=4.5, n=10):
    """U 形拉环的外轮廓（一条闭合线，后端开口）：两臂从模块两侧伸出，在前面绕成握把。"""
    pts = [(-ox, y0)]
    for k in range(n + 1):                                  # 外圈：左上角 → 右上角
        a = math.radians(180 - 90 * k / n)
        pts.append((-ox + ro + ro * math.cos(a), oy - ro + ro * math.sin(a)))
    for k in range(n + 1):
        a = math.radians(90 - 90 * k / n)
        pts.append((ox - ro + ro * math.cos(a), oy - ro + ro * math.sin(a)))
    pts += [(ox, y0), (ix, y0)]
    for k in range(n + 1):                                  # 内圈：右上角 → 左上角
        a = math.radians(0 + 90 * k / n)
        pts.append((ix - ri + ri * math.cos(a), iy - ri + ri * math.sin(a)))
    for k in range(n + 1):
        a = math.radians(90 + 90 * k / n)
        pts.append((-ix + ri + ri * math.cos(a), iy - ri + ri * math.sin(a)))
    pts.append((-ix, y0))
    sp = cu.splines.new('POLY')
    sp.points.add(len(pts) - 1)
    for p, (x, y) in zip(sp.points, pts):
        p.co = (x * MM, y * MM, 0, 1)
    sp.use_cyclic_u = True


def build_pulltab(M):
    cu = bpy.data.curves.new('pulltab', 'CURVE')
    cu.dimensions = '2D'
    cu.fill_mode = 'BOTH'
    cu.extrude = 1.1 * MM
    cu.bevel_depth = 0.35 * MM
    cu.bevel_resolution = 3
    u_outline(cu)
    o = bpy.data.objects.new('mod_pulltab', cu)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(M['tab'])
    o.location = (0, 0, 5.2 * MM)
    o.rotation_euler = (math.radians(-12), 0, 0)   # 近水平、略下倾，末端贴近台面（形态待核，见 FACTS）
    # 握把上的防滑横纹
    for i in range(5):
        y = 25.0 + i * 1.1
        r = box('tab_rib', -8.5, 8.5, y, y + 0.45, 1.1, 1.55, M['tab'], 0.15)
        r.parent = o
    return o


# ---------- 笼子（入口在 y = 0） ----------
def build_cage(M):
    hw = CAGE_W / 2
    shell = box('cage_shell', -hw, hw, -CAGE_L, 0.0, 0.0, CAGE_H, M['nickel'], 0)
    cc = cutter_collection('cut_cage')
    s = SHEET
    add_cutter(cc, -hw + s, hw - s, -CAGE_L + s, 1.0, s, CAGE_H - s)          # 掏空，入口敞开
    for row, x in ((0, -5.0), (1, 5.0)):                                       # 顶面两排通风长孔
        for k in range(6):
            y = -12.0 - k * 11.0
            add_cutter(cc, x - 3.0, x + 3.0, y - 1.6, y, CAGE_H - 1, CAGE_H + 1)
    for sx in (-1, 1):                                                         # 侧面两排小孔
        for row, z in ((0, 4.0), (1, 9.0)):
            for k in range(7):
                y = -16.0 - k * 9.0
                add_cutter(cc, sx * hw - 1, sx * hw + 1, y - 4.5, y, z, z + 1.5)
    boolean(shell, cc, bevel=0.12)
    # 入口外翻的边框
    fr = box('cage_flange', -hw - 0.6, hw + 0.6, -1.0, 0.0, -0.0, CAGE_H + 0.6, M['nickel'], 0)
    cc2 = cutter_collection('cut_flange')
    add_cutter(cc2, -hw + s, hw - s, -2, 1, s, CAGE_H - s)
    boolean(fr, cc2, bevel=0.2)
    # 入口内侧的接地簧片（EMI 指）
    for i in range(9):
        x = -hw + 1.6 + i * 2.6
        f = box('cage_emi', x, x + 1.8, -5.0, -0.6, CAGE_H - s - 0.25, CAGE_H - s, M['nickel'], 0.08)
        f.rotation_euler = (math.radians(-10), 0, 0)
    # 两侧焊脚
    for sx in (-1, 1):
        for k in range(4):
            y = -10.0 - k * 22.0
            box('cage_foot', sx * hw - (0.25 if sx > 0 else -0.25) - 0.4, sx * hw - (0.25 if sx > 0 else -0.25) + 0.4,
                y - 2.0, y, -0.05, 1.2, M['nickel'], 0.08)


# ---------- 网卡板和元件 ----------
def build_board(M):
    box('pcb', -55.0, 75.0, -170.0, BOARD_EDGE_Y, -1.6, 0.0, M['pcb'], 0.15)
    box('pcb_edge', -55.0, 75.0, BOARD_EDGE_Y - 0.02, BOARD_EDGE_Y + 0.01, -1.6, 0.0, M['fr4'], 0)
    # 安装孔（沉金环）
    for (x, y) in ((-46.0, -12.0), (66.0, -14.0), (-46.0, -150.0)):
        bpy.ops.mesh.primitive_torus_add(major_radius=2.6 * MM, minor_radius=0.9 * MM, location=(x * MM, y * MM, 0.0))
        t = bpy.context.active_object
        t.scale = (1, 1, 0.08)
        t.data.materials.append(M['gold'])
        bpy.ops.mesh.primitive_cylinder_add(radius=1.7 * MM, depth=3.4 * MM, location=(x * MM, y * MM, -0.8 * MM))
        h = bpy.context.active_object
        h.data.materials.append(M['hole'])
    # 主芯片散热器（黑色阳极氧化，纵向鳍片）
    box('hs_base', -22.0, 30.0, -150.0, -100.0, 0.0, 3.0, M['heatsink'], 0.4)
    for i in range(16):
        x = -21.0 + i * 3.2
        box('hs_fin', x, x + 1.1, -149.0, -101.0, 3.0, 20.0, M['heatsink'], 0.25)
    # 元件：避开笼子和散热器
    def free(x, y, w, d):
        if -14.5 < x < 14.5 and y > -90:
            return False
        if -24 < x < 32 and -152 < y < -98:
            return False
        return -52 < x < 72 and -165 < y < BOARD_EDGE_Y - 3
    placed = 0
    while placed < 650:
        kind = random.random()
        x, y = random.uniform(-52, 72), random.uniform(-165, -5)
        rot = random.choice([0, 90])
        if kind < 0.45:                       # 0603 / 0402 电容
            w, d, h = random.choice([(1.6, 0.8, 0.8), (1.0, 0.5, 0.5)])
            if rot:
                w, d = d, w
            if not free(x, y, w, d):
                continue
            box('cap', x, x + w, y, y + d, 0, h, M['cap'], 0.06)
            if w > d:
                box('cap_t', x - 0.02, x + 0.25, y - 0.02, y + d + 0.02, 0, h + 0.02, M['tin'], 0.05)
                box('cap_t', x + w - 0.25, x + w + 0.02, y - 0.02, y + d + 0.02, 0, h + 0.02, M['tin'], 0.05)
            else:
                box('cap_t', x - 0.02, x + w + 0.02, y - 0.02, y + 0.25, 0, h + 0.02, M['tin'], 0.05)
                box('cap_t', x - 0.02, x + w + 0.02, y + d - 0.25, y + d + 0.02, 0, h + 0.02, M['tin'], 0.05)
        elif kind < 0.75:                     # 电阻
            w, d, h = (1.6, 0.8, 0.45) if not rot else (0.8, 1.6, 0.45)
            if not free(x, y, w, d):
                continue
            box('res', x, x + w, y, y + d, 0, h, M['res'], 0.05)
        elif kind < 0.92:                     # 小 IC + 引脚
            s = random.choice([3.0, 4.0, 5.0])
            if not free(x, y, s, s):
                continue
            box('ic', x, x + s, y, y + s, 0, 0.9, M['ic'], 0.12)
            n = int(s / 0.65)
            for k in range(n):
                xx = x + 0.3 + k * 0.65
                box('lead', xx, xx + 0.25, y - 0.45, y, 0, 0.18, M['tin'], 0)
                box('lead', xx, xx + 0.25, y + s, y + s + 0.45, 0, 0.18, M['tin'], 0)
        else:                                 # 功率电感
            s = random.choice([4.0, 5.0])
            if not free(x, y, s, s):
                continue
            box('ind', x, x + s, y, y + s, 0, 3.0, M['inductor'], 0.3)
        placed += 1


# ---------- 环境、光、相机 ----------
def build_env(M, hdri_strength=0.07):
    sc = bpy.context.scene
    box('desk', -600.0, 600.0, -900.0, 600.0, -3.0, -1.6, M['desk'], 0)
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0, -0.9, 0.3), rotation=(math.radians(90), 0, 0))
    bd = bpy.context.active_object
    bd.scale = (3, 1.2, 1)
    bd.data.materials.append(M['backdrop'])
    # 背景散景：远处的小发光点（机房指示灯 / 走廊灯的感觉），靠景深虚化
    for i in range(70):
        x, y, z = random.uniform(-0.22, 0.22), random.uniform(-0.80, -0.30), random.uniform(0.012, 0.09)   # 放在镜头上沿能看到的高度
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(1.5, 4.0) * MM, location=(x, y, z))
        b = bpy.context.active_object
        warm = random.random() < 0.18
        col = (1.0, 0.62, 0.3) if warm else (0.45, 0.7, 1.0)
        em = bpy.data.materials.new('bokeh')
        em.use_nodes = True
        nt = em.node_tree
        nt.nodes.remove(nt.nodes['Principled BSDF'])
        e = nt.nodes.new('ShaderNodeEmission')
        e.inputs['Color'].default_value = (*col, 1)
        e.inputs['Strength'].default_value = random.uniform(1.5, 6.0)
        nt.links.new(e.outputs['Emission'], nt.nodes['Material Output'].inputs['Surface'])
        b.data.materials.append(em)
        b.visible_shadow = False
    # 世界：HDRI 只给反射，镜头直接看到的是近黑（Poly Haven，CC0，经 tools/polyhaven.py 下载）
    ph.set_world_hdri('studio_small_09', res='2k', strength=hdri_strength, rotation_deg=140,
                      camera_sees=(0.004, 0.005, 0.007))
    # 体积雾：只放在光束经过的区域，做出斜射的光柱
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.42, 0.10))   # 雾只放在主体后面
    v = bpy.context.active_object
    v.name = 'haze'
    v.scale = (0.8, 0.56, 0.2)
    vm = bpy.data.materials.new('haze')
    vm.use_nodes = True
    nt = vm.node_tree
    nt.nodes.remove(nt.nodes['Principled BSDF'])
    pv = nt.nodes.new('ShaderNodeVolumePrincipled')
    pv.inputs['Density'].default_value = 0.22
    pv.inputs['Anisotropy'].default_value = 0.55
    nt.links.new(pv.outputs['Volume'], nt.nodes['Material Output'].inputs['Volume'])
    v.data.materials.append(vm)


def area(name, loc, target, size, power, color):
    d = bpy.data.lights.new(name, 'AREA')
    d.size = size
    d.energy = power
    d.color = color
    o = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o


def lights():
    tgt = (0, MOD_FRONT_Y * MM * 0.3, 0.008)
    area('key_cool', (-0.12, -0.16, 0.16), tgt, 0.10, 3.0, (0.86, 0.93, 1.0))
    top = area('top_soft', (0.02, -0.03, 0.22), (0, -0.03, 0), 0.22, 2.2, (0.9, 0.95, 1.0))   # 大面积顶光：只给金属高光
    top.visible_diffuse = False      # 不照亮台面、电路板这类漫反射面，只在金属上留下光泽
    area('fill_warm', (0.14, 0.26, 0.05), (0, MOD_FRONT_Y * MM, 0.007), 0.12, 0.25, (1.0, 0.78, 0.55))
    area('rim_cool', (0.16, -0.20, 0.07), tgt, 0.06, 0.8, (0.6, 0.8, 1.0))
    sp = bpy.data.lights.new('beam', 'SPOT')
    sp.energy = 55.0
    sp.spot_size = math.radians(16)
    sp.spot_blend = 0.7
    sp.shadow_soft_size = 0.004
    sp.color = (0.82, 0.9, 1.0)
    o = bpy.data.objects.new('beam', sp)
    bpy.context.scene.collection.objects.link(o)
    o.location = (-0.16, -0.70, 0.24)   # 从后方斜着逆光，穿过散热器那一带的雾
    o.rotation_euler = (Vector((0.02, -0.10, 0.0)) - Vector(o.location)).to_track_quat('-Z', 'Y').to_euler()


def camera(az=16.0, el=17.0, dist=0.155, lens=60.0, fstop=8.0, dof=True):
    sc = bpy.context.scene
    focus = Vector((0, (MOD_FRONT_Y - 4.0) * MM, (MOD_Z0 + 9.0) * MM))   # 对焦在前端面稍后（前段顶盖），笼子入口也比较清楚
    aim = Vector((1.5 * MM, (MOD_FRONT_Y - 30.0) * MM, (MOD_Z0 + 2.0) * MM))   # 视线往后，模块前端在下三分之一，上方留给笼子和散热器
    a, e = math.radians(az), math.radians(el)
    pos = focus + dist * Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e)))
    cd = bpy.data.cameras.new('CAM')
    cd.lens = lens
    cd.sensor_fit = 'VERTICAL'
    cd.sensor_height = 36.0
    cd.clip_start = 0.005
    cd.dof.use_dof = dof
    cd.dof.focus_distance = (pos - focus).length
    cd.dof.aperture_fstop = fstop
    cd.dof.aperture_blades = 7
    c = bpy.data.objects.new('CAM', cd)
    sc.collection.objects.link(c)
    c.location = pos
    c.rotation_euler = (aim - pos).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = c
    return c


def build(res=540, spp=64):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.length_unit = 'MILLIMETERS'
    M = make_materials()
    build_board(M)
    build_cage(M)
    build_module(M)
    build_env(M)
    lights()
    camera(dof='--nodof' not in sys.argv)
    r = sc.render
    r.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    if '--gpu' in sys.argv:            # 云端：用 OPTIX；找不到显卡直接报错，不悄悄退回 CPU
        pr = bpy.context.preferences.addons['cycles'].preferences
        pr.compute_device_type = 'OPTIX'
        pr.get_devices()
        gpus = [d for d in pr.devices if d.type == 'OPTIX']
        if not gpus:
            raise SystemExit('要求用 GPU，但没找到 OPTIX 设备')
        for d in pr.devices:
            d.use = d.type == 'OPTIX'
        sc.cycles.device = 'GPU'
        print('GPU:', [d.name for d in gpus])
    sc.cycles.samples = spp
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.volume_step_rate = 4.0
    sc.cycles.volume_max_steps = 256
    r.resolution_x, r.resolution_y = res, int(res * 16 / 9)
    r.resolution_percentage = 100
    r.film_transparent = False
    sc.view_settings.view_transform = 'AgX'
    try:
        sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    sc.view_settings.exposure = 0.0
    r.image_settings.file_format = 'PNG'
    return sc


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['still']
    def opt(k, d):
        return type(d)(argv[argv.index(k) + 1]) if k in argv else d
    res, spp = opt('--res', 540), opt('--spp', 64)
    out = opt('--out', os.path.join('out', 'hero.png'))
    sc = build(res, spp)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'scene_hero.blend'), compress=True)
    if argv[0] == 'still':
        os.makedirs(os.path.dirname(os.path.join(HERE, out)), exist_ok=True)
        sc.render.filepath = os.path.join(HERE, out)
        bpy.ops.render.render(write_still=True)


main()
