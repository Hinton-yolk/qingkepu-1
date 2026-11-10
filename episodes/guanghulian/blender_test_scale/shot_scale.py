# 一语道破 · Blender 测试镜头三：光在芯片里走的路有多细？（2026-11-10，真实感改造版，按 SHOTPLAN 第四版）
# 竖屏 18 秒，一个连续镜头对数匀速推进：交换机 → 光模块（手机）→ 硅光芯片（米粒）→ 芯片边缘的光纤阵列（头发）
#   → 离边缘约 150 µm 的波导（红细胞）→ 停在「不到 0.5 µm」的波导上。
# 做法：相机不动，整个世界围绕焦点逐帧缩放（单位 µm，网格按真实尺寸）。
# 真实感：Poly Haven HDRI 环境光（只用于打光和反射，相机看到的背景仍是深蓝）、倒角、程序生成的芯片版图贴图、
#         金属粗糙度贴图、浅景深、合成里只给光加辉光（AOV 遮罩）。
# 物体进出用淡入淡出（物体颜色的 alpha），淡完再关渲染；标签保持屏幕上的字号（反向缩放）。
# 默认 EEVEE。用法：
#   blender -b --python-exit-code 1 --python shot_scale.py -- <输出目录> <宽> <高> <采样> [--gpu] [--cycles] [--fps N] [--video] [帧号…]
#   --video：输出 PNG 序列（可续渲：已存在的帧跳过），云端再编码成视频。
import bpy, bmesh, math, sys, json, os, random, time
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

args = sys.argv[sys.argv.index('--') + 1:]; OUT, W, H, SAMP = args[0], int(args[1]), int(args[2]), int(args[3]); rest = args[4:]
GPU = '--gpu' in rest; CYCLES = '--cycles' in rest; VIDEO = '--video' in rest
FPS = int(rest[rest.index('--fps') + 1]) if '--fps' in rest else 30
LOOK = rest[rest.index('--look') + 1] if '--look' in rest else 'warm'      # 画面风格：warm（暖金逆光）/ cool（冷调机房）
FRAMES = [int(a) for i, a in enumerate(rest) if a.isdigit() and not (i > 0 and rest[i - 1] == '--fps')]
DUR = 18.0; NF = round(DUR * FPS); F = lambda sec: 1 + round(sec * FPS)
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, 'assets', 'label_font.otf'); LAYOUT = os.path.join(HERE, 'assets', 'chip_layout.png')
HDRI = os.path.join(HERE, 'assets_dl', 'studio_small_09_2k.hdr'); ROUGH = os.path.join(HERE, 'assets_dl', 'metal_plate_rough_2k.jpg')
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; os.makedirs(OUT, exist_ok=True)
print('BLENDER_VERSION', bpy.app.version_string)

# ---------- 版本兼容 ----------
def fcurves_of(idb):
    ad = idb.animation_data
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
def set_interp(idb, kind):
    for fc in fcurves_of(idb):
        for kp in fc.keyframe_points: kp.interpolation = kind
def set_fmt(fmt):
    ims = sc.render.image_settings
    if hasattr(ims, 'media_type'): ims.media_type = 'VIDEO' if fmt == 'FFMPEG' else 'IMAGE'
    ims.file_format = fmt

# ---------- 材质 ----------
# 所有材质的透明度都乘上「物体颜色的 alpha」（用来淡入淡出）；需要半透明的用 BLENDED，其余用 DITHERED。
def _fade_alpha(m, base, target_socket):
    N = m.node_tree.nodes; L = m.node_tree.links
    oi = N.new('ShaderNodeObjectInfo'); mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
    if isinstance(base, float): mul.inputs[1].default_value = base
    else: L.new(base, mul.inputs[1])
    L.new(oi.outputs['Alpha'], mul.inputs[0]); L.new(mul.outputs[0], target_socket)
def mat(name, col, metal=0.0, rough=0.5, alpha=1.0, coat=0.0, sss=0.0, rough_tex=None, rough_scale=1.0, bump=0.0, aniso=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal; b.inputs['Roughness'].default_value = rough
    b.inputs['Coat Weight'].default_value = coat
    if sss: b.inputs['Subsurface Weight'].default_value = sss
    if aniso and 'Anisotropic' in b.inputs: b.inputs['Anisotropic'].default_value = aniso
    if rough_tex or bump:                         # 粗糙度细节：贴图（金属划痕）或程序噪声
        tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (rough_scale, rough_scale * (8 if aniso else 1), rough_scale)
        L.new(tc.outputs['Object'], mp.inputs['Vector'])
        if rough_tex and os.path.exists(rough_tex):
            it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(rough_tex, check_existing=True); it.image.colorspace_settings.name = 'Non-Color'
            it.projection = 'BOX'; L.new(mp.outputs[0], it.inputs[0]); src = it.outputs['Color']
        else:
            nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0; nz.inputs['Detail'].default_value = 8.0; L.new(mp.outputs[0], nz.inputs['Vector']); src = nz.outputs['Fac']
        mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = max(0.02, rough - 0.12); mr.inputs['To Max'].default_value = min(1.0, rough + 0.15)
        L.new(src, mr.inputs['Value']); L.new(mr.outputs[0], b.inputs['Roughness'])
        if bump:
            bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump; L.new(src, bp.inputs['Height']); L.new(bp.outputs[0], b.inputs['Normal'])
    _fade_alpha(m, alpha, b.inputs['Alpha'])
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'BLENDED' if alpha < 1 else 'DITHERED'
    return m
def mat_emit(name, col, strength, alpha=1.0, aov=False):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    for n in list(N): N.remove(n)
    o = N.new('ShaderNodeOutputMaterial'); e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*col, 1); e.inputs['Strength'].default_value = strength
    tr = N.new('ShaderNodeBsdfTransparent'); mx = N.new('ShaderNodeMixShader')
    L.new(tr.outputs[0], mx.inputs[1]); L.new(e.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], o.inputs[0])
    _fade_alpha(m, alpha, mx.inputs['Fac'])
    if aov:
        ao = N.new('ShaderNodeOutputAOV'); ao.aov_name = 'lightmask'; ao.inputs['Value'].default_value = 1.0
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'BLENDED' if alpha < 1 else 'DITHERED'
    return m, e
CYAN = (0.20, 0.95, 0.85)
def mat_light_band():
    """光带：均匀青色；13 秒起叠加相位条纹（间距 0.5 µm，每秒走 1 µm，朝 −y：从调制器往芯片边缘、往光纤方向，发射端）"""
    m, e = mat_emit('light_band', CYAN, 1.6, aov=True); N = m.node_tree.nodes; L = m.node_tree.links
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])
    off = N.new('ShaderNodeValue'); off.name = 'phase_offset'
    add = N.new('ShaderNodeMath'); add.operation = 'ADD'; L.new(sep.outputs['Y'], add.inputs[0]); L.new(off.outputs[0], add.inputs[1])
    mul = N.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 2 * math.pi / 0.5; L.new(add.outputs[0], mul.inputs[0])
    sn = N.new('ShaderNodeMath'); sn.operation = 'SINE'; L.new(mul.outputs[0], sn.inputs[0])
    amp = N.new('ShaderNodeValue'); amp.name = 'stripe_amp'
    a1 = N.new('ShaderNodeMath'); a1.operation = 'MULTIPLY'; L.new(sn.outputs[0], a1.inputs[0]); L.new(amp.outputs[0], a1.inputs[1])
    a2 = N.new('ShaderNodeMath'); a2.operation = 'ADD'; a2.inputs[1].default_value = 1.0; L.new(a1.outputs[0], a2.inputs[0])
    st = N.new('ShaderNodeMath'); st.operation = 'MULTIPLY'; st.inputs[1].default_value = 1.6; L.new(a2.outputs[0], st.inputs[0]); L.new(st.outputs[0], e.inputs['Strength'])
    for fr, v in ((1, 0.0), (NF, (NF - 1) / FPS)): off.outputs[0].default_value = v; off.outputs[0].keyframe_insert('default_value', frame=fr)   # +v：条纹朝 −y 走
    for fr, v in ((1, 0.0), (F(12.6), 0.0), (F(13.4), 0.4), (NF, 0.4)): amp.outputs[0].default_value = v; amp.outputs[0].keyframe_insert('default_value', frame=fr)
    set_interp(m.node_tree, 'LINEAR'); return m
def mat_chip_surface():
    """芯片表面：深蓝氧化层底色；版图贴图 R = 硅器件（钢蓝），G = 金属（金），A = 亮着的光路（青，远景时看得见光走到哪）"""
    m = bpy.data.materials.new('chip_surface'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1 / 5000, 1 / 5000, 1); mp.inputs['Location'].default_value = (0.5, 0.5, 0)
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(LAYOUT, check_existing=True); it.image.colorspace_settings.name = 'Non-Color'; it.interpolation = 'Cubic'
    L.new(mp.outputs[0], it.inputs[0]); sp = N.new('ShaderNodeSeparateColor'); L.new(it.outputs['Color'], sp.inputs[0])
    def mix(fac, a, bcol):
        mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L.new(fac, mx.inputs['Factor'])
        if isinstance(a, tuple): mx.inputs['A'].default_value = (*a, 1)
        else: L.new(a, mx.inputs['A'])
        mx.inputs['B'].default_value = (*bcol, 1); return mx.outputs['Result']
    c1 = mix(sp.outputs['Red'], (0.015, 0.05, 0.20), (0.20, 0.27, 0.40)); c2 = mix(sp.outputs['Green'], c1, (0.95, 0.66, 0.24))
    L.new(c2, b.inputs['Base Color']); L.new(sp.outputs['Green'], b.inputs['Metallic'])
    rg = N.new('ShaderNodeMapRange'); rg.inputs['To Min'].default_value = 0.32; rg.inputs['To Max'].default_value = 0.2; L.new(sp.outputs['Green'], rg.inputs['Value']); L.new(rg.outputs[0], b.inputs['Roughness'])
    b.inputs['Coat Weight'].default_value = 0.5; b.inputs['Emission Color'].default_value = (*CYAN, 1)
    em = N.new('ShaderNodeMath'); em.operation = 'MULTIPLY'; em.inputs[1].default_value = 1.4; L.new(it.outputs['Alpha'], em.inputs[0]); L.new(em.outputs[0], b.inputs['Emission Strength'])
    _fade_alpha(m, 1.0, b.inputs['Alpha'])
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'DITHERED'
    return m
M = dict(
    chip=mat_chip_surface(),
    clad=mat('upper_cladding_glass', (0.6, 0.7, 0.9), 0.0, 0.12, alpha=0.05),
    si_wg=mat('si_waveguide_clear', (0.35, 0.45, 0.62), 0.0, 0.12, alpha=0.30),     # 硅在 1310 nm 透明：画成半透明，看得见芯区里的光
    si_side=mat('si_die_side', (0.10, 0.11, 0.14), 0.7, 0.35, bump=0.2),
    gold=mat('gold_electrode', (0.95, 0.66, 0.24), 1.0, 0.22, rough_tex=ROUGH, rough_scale=0.02),
    light=mat_light_band(),
    tail=mat_emit('evanescent_tail', CYAN, 0.7, alpha=0.10, aov=True)[0],
    glass=mat('fiber_glass', (0.70, 0.78, 0.88), 0.0, 0.05, alpha=0.18, coat=0.6),
    vgroove=mat('v_groove_block', (0.16, 0.17, 0.20), 0.5, 0.3, bump=0.05),         # 硅 V 形槽块：深灰金属光泽
    ssc=mat('ssc_block', (0.45, 0.55, 0.75), 0.0, 0.2, alpha=0.35),
    rbc=mat('red_blood_cell', (0.26, 0.05, 0.06), 0.0, 0.5, sss=0.1),
    hair=mat('hair', (0.08, 0.055, 0.045), 0.0, 0.35, coat=0.6, bump=0.3),
    rice=mat('rice', (0.92, 0.90, 0.84), 0.0, 0.35, sss=0.6, bump=0.15),
    pcb=mat('pcb_solder_mask', (0.03, 0.14, 0.05), 0.0, 0.35, coat=0.5, bump=0.1),   # 绿色阻焊（不用青蓝）
    copper=mat('pcb_gold_pad', (0.95, 0.66, 0.24), 1.0, 0.25),
    ic=mat('ic_package', (0.05, 0.05, 0.055), 0.2, 0.45, bump=0.05),
    laser=mat('laser_chip', (0.32, 0.33, 0.36), 0.7, 0.3),
    ribbon=mat('fiber_ribbon', (0.55, 0.56, 0.58), 0.0, 0.5),
    mpo=mat('mpo', (0.25, 0.26, 0.28), 0.0, 0.45),
    shell=mat('module_shell', (0.72, 0.74, 0.78), 1.0, 0.3, alpha=0.25, rough_tex=ROUGH, rough_scale=0.0003, aniso=0.6),
    shell_end=mat('module_front', (0.66, 0.68, 0.72), 1.0, 0.3, rough_tex=ROUGH, rough_scale=0.0003, aniso=0.6),
    tab=mat('pull_tab', (0.10, 0.10, 0.11), 0.0, 0.55),
    sw=mat('switch_metal', (0.06, 0.065, 0.075), 0.7, 0.45, rough_tex=ROUGH, rough_scale=0.00005),
    sw_top=mat('switch_cover', (0.10, 0.11, 0.13), 0.0, 0.55, alpha=0.04),
    asic=mat('switch_asic_dim', (0.04, 0.04, 0.045), 0.2, 0.5),
    cage=mat('port_cage', (0.58, 0.60, 0.63), 1.0, 0.3, rough_tex=ROUGH, rough_scale=0.0002),
    led=mat_emit('led_green', (0.2, 1.0, 0.25), 5.0)[0],
    rack=mat('rack_rail', (0.10, 0.11, 0.12), 0.8, 0.4, rough_tex=ROUGH, rough_scale=0.00005),
    other=mat('other_device', (0.045, 0.05, 0.06), 0.6, 0.45),
    patch=mat('patch_cord_os2_yellow', (0.78, 0.52, 0.03), 0.0, 0.45, coat=0.3),   # 单模跳线常用黄色护套
    phone=mat('phone_body', (0.16, 0.16, 0.18), 0.9, 0.25),
    phone_screen=mat('phone_screen_off', (0.008, 0.008, 0.01), 0.0, 0.06, coat=1.0),
    shelf=mat('shelf', (0.12, 0.13, 0.15), 0.7, 0.45),
    label=mat_emit('label_white', (1.0, 1.0, 1.0), 3.0)[0],
)

# ---------- 硬件段的贴图材质（贴图由 make_hw_textures.py 生成） ----------
PCB_TEX = os.path.join(HERE, 'assets', 'pcb_module.png'); PERF_TEX = os.path.join(HERE, 'assets', 'perf_hex.png'); RACK_TEX = os.path.join(HERE, 'assets', 'rack_holes.png')
def _obj_uv(N, L, ax_u, ax_v, su, sv, ou=0.0, ov=0.0):
    """物体坐标的两个轴 → 贴图 UV：u = 轴_u·su + ou，v = 轴_v·sv + ov"""
    tc = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sp.inputs[0]); cm = N.new('ShaderNodeCombineXYZ')
    for ax, s, o, sock in ((ax_u, su, ou, 'X'), (ax_v, sv, ov, 'Y')):
        m1 = N.new('ShaderNodeMath'); m1.operation = 'MULTIPLY_ADD'; L.new(sp.outputs[ax], m1.inputs[0]); m1.inputs[1].default_value = s; m1.inputs[2].default_value = o
        L.new(m1.outputs[0], cm.inputs[sock])
    return cm.outputs[0]
def _img(N, L, path, vec, ext='REPEAT'):
    it = N.new('ShaderNodeTexImage'); it.image = bpy.data.images.load(path, check_existing=True); it.image.colorspace_settings.name = 'Non-Color'
    it.extension = ext; L.new(vec, it.inputs[0]); return it
def _mix(N, L, fac, a, bcol):
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L.new(fac, mx.inputs['Factor'])
    if isinstance(a, tuple): mx.inputs['A'].default_value = (*a, 1)
    else: L.new(a, mx.inputs['A'])
    mx.inputs['B'].default_value = (*bcol, 1); return mx.outputs['Result']
def _range(N, L, src, lo, hi, dst):
    mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = lo; mr.inputs['To Max'].default_value = hi; L.new(src, mr.inputs['Value']); L.new(mr.outputs[0], dst)
def mat_holes(name, col, metal, rough, tex, ax_u, ax_v, per_u, per_v, ou=0.0, ov=0.0, hole=(0.004, 0.004, 0.005), bump=0.5):
    """冲孔板 / 立柱方孔：贴图白 = 孔（孔里暗、不反光，孔边有凹陷）"""
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    it = _img(N, L, tex, _obj_uv(N, L, ax_u, ax_v, 1 / per_u, 1 / per_v, ou, ov)); k = it.outputs['Color']
    L.new(_mix(N, L, k, col, hole), b.inputs['Base Color']); _range(N, L, k, metal, 0.0, b.inputs['Metallic']); _range(N, L, k, rough, 0.95, b.inputs['Roughness'])
    bp = N.new('ShaderNodeBump'); bp.invert = True; bp.inputs['Strength'].default_value = bump; L.new(k, bp.inputs['Height']); L.new(bp.outputs[0], b.inputs['Normal'])
    _fade_alpha(m, 1.0, b.inputs['Alpha'])
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'DITHERED'
    return m
def mat_pcb(name, tile_u=17150.0, tile_v=76000.0, dim=1.0):
    """电路板顶面：绿色阻焊；阻焊下的铜（走线、铺铜）稍亮；金焊盘；白色丝印；过孔微凸"""
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    it = _img(N, L, PCB_TEX, _obj_uv(N, L, 'X', 'Y', 1 / tile_u, 1 / tile_v, 0.5, 0.5)); sp = N.new('ShaderNodeSeparateColor'); L.new(it.outputs['Color'], sp.inputs[0])
    d = lambda c: tuple(v * dim for v in c)
    c = _mix(N, L, sp.outputs['Red'], d((0.018, 0.085, 0.03)), d((0.05, 0.20, 0.07)))
    c = _mix(N, L, sp.outputs['Green'], c, (0.95, 0.66, 0.24)); c = _mix(N, L, sp.outputs['Blue'], c, d((0.78, 0.80, 0.76)))
    L.new(c, b.inputs['Base Color']); L.new(sp.outputs['Green'], b.inputs['Metallic']); _range(N, L, sp.outputs['Green'], 0.32, 0.22, b.inputs['Roughness'])
    h = N.new('ShaderNodeMath'); h.operation = 'MULTIPLY_ADD'; L.new(sp.outputs['Red'], h.inputs[0]); h.inputs[1].default_value = 0.35; L.new(it.outputs['Alpha'], h.inputs[2])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.25; L.new(h.outputs[0], bp.inputs['Height']); L.new(bp.outputs[0], b.inputs['Normal'])
    b.inputs['Coat Weight'].default_value = 0.45; _fade_alpha(m, 1.0, b.inputs['Alpha'])
    if hasattr(m, 'surface_render_method'): m.surface_render_method = 'DITHERED'
    return m
def mat_ribbon():
    """光纤带：8 根 250 µm 涂覆光纤并排（中性浅灰，起伏按光纤位置）"""
    m = mat('fiber_ribbon', (0.62, 0.63, 0.65), 0.0, 0.45); N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sp.inputs[0])
    mu = N.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = 2 * math.pi / 250.0; L.new(sp.outputs['X'], mu.inputs[0])
    cs = N.new('ShaderNodeMath'); cs.operation = 'COSINE'; L.new(mu.outputs[0], cs.inputs[0])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.6; L.new(cs.outputs[0], bp.inputs['Height']); L.new(bp.outputs[0], b.inputs['Normal'])
    return m
M.update(
    pcb=mat_pcb('module_pcb'), host_pcb=mat_pcb('host_pcb', 34300.0, 152000.0, dim=0.55),
    ribbon=mat_ribbon(),
    face=mat_holes('switch_faceplate', (0.075, 0.08, 0.09), 0.85, 0.42, PERF_TEX, 'X', 'Z', 40000.0, 41560.0, bump=0.6),
    cage_body=mat_holes('cage_body', (0.34, 0.35, 0.37), 1.0, 0.42, PERF_TEX, 'X', 'Y', 16000.0, 16620.0, bump=0.3),
    rack=mat_holes('rack_rail', (0.10, 0.11, 0.12), 0.8, 0.4, RACK_TEX, 'X', 'Z', 25000.0, 44450.0, ou=0.5, ov=-0.5),
    other=mat_holes('other_device', (0.05, 0.055, 0.065), 0.6, 0.45, PERF_TEX, 'X', 'Z', 40000.0, 41560.0),
    mouth=mat('cage_mouth_dark', (0.035, 0.036, 0.04), 0.3, 0.55),
    mpo_apc=mat('mpo_apc_green', (0.04, 0.30, 0.10), 0.0, 0.4),      # APC 端面的 MPO 外壳常用绿色
    plastic=mat('black_plastic', (0.025, 0.025, 0.028), 0.0, 0.5, bump=0.05),
    heatsink=mat('heatsink_dim', (0.28, 0.29, 0.31), 1.0, 0.35),
    substrate=mat('bga_substrate', (0.10, 0.085, 0.055), 0.0, 0.4, coat=0.3),
    mlcc=mat('mlcc_body', (0.42, 0.34, 0.24), 0.0, 0.55), tin=mat('mlcc_terminal', (0.78, 0.78, 0.80), 1.0, 0.3),
    phone_frame=mat('phone_frame', (0.55, 0.56, 0.60), 1.0, 0.22, aniso=0.4),
    rj45=mat('rj45_dark', (0.02, 0.02, 0.022), 0.2, 0.6),
)

# ---------- 几何工具（单位 µm，网格按真实尺寸） ----------
WORLD = bpy.data.objects.new('WORLD', None); sc.collection.objects.link(WORLD)
def link(o, parent=WORLD): sc.collection.objects.link(o); o.parent = parent; return o
def bevel(o, w, seg=3):
    md = o.modifiers.new('bev', 'BEVEL'); md.width = w; md.segments = seg; md.limit_method = 'ANGLE'
    for p in o.data.polygons: p.use_smooth = True
    o.modifiers.new('wn', 'WEIGHTED_NORMAL')
def box(name, cx, cy, cz, sx, sy, sz, m, bev=0.06):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = (cx, cy, cz); o.data.materials.append(m); link(o)
    if bev: bevel(o, bev * min(sx, sy, sz))
    return o
def cyl(name, r, depth, m, loc, rot=(0, 0, 0), verts=40):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r, depth=depth); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; o.rotation_euler = rot; o.data.materials.append(m); return link(o)
def tube(name, pts, r, m):
    """沿控制点生成圆管（跳线用）"""
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 3
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts): bp.co = p; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(name, cu); o.data.materials.append(m); return link(o)
def ellipsoid(name, rx, ry, rz, m, loc, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=20, radius=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * rx, v.co.y * ry, v.co.z * rz))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; o.rotation_euler = rot; o.data.materials.append(m); return link(o)
def rbc_mesh(name, D, m, loc):
    """红细胞：双凹圆盘（Evans–Fung 截面形状），直径 D"""
    R = D / 2; prof = []
    for j in range(25):
        rr = R * j / 24; x = rr / R
        h = 0.5 * R * math.sqrt(max(0.0, 1 - x * x)) * (0.207 + 2.003 * x * x - 1.123 * x ** 4)
        prof.append((rr, max(h, 0.0)))
    bm = bmesh.new(); seg = 48
    top = [[bm.verts.new((rr * math.cos(2 * math.pi * i / seg), rr * math.sin(2 * math.pi * i / seg), h)) for i in range(seg)] for rr, h in prof[:-1]]
    bot = [[bm.verts.new((rr * math.cos(2 * math.pi * i / seg), rr * math.sin(2 * math.pi * i / seg), -h)) for i in range(seg)] for rr, h in prof[:-1]]
    rim = [bm.verts.new((R * math.cos(2 * math.pi * i / seg), R * math.sin(2 * math.pi * i / seg), 0)) for i in range(seg)]
    for layer, flip in ((top, False), (bot, True)):
        rows = layer + [rim]
        for j in range(1, len(rows) - 1):
            for i in range(seg):
                q = [rows[j][i], rows[j][(i + 1) % seg], rows[j + 1][(i + 1) % seg], rows[j + 1][i]]
                bm.faces.new(q[::-1] if flip else q)
        cen = rows[0]
        for i in range(seg):
            t = [cen[i], cen[(i + 1) % seg], rows[1][(i + 1) % seg], rows[1][i]]
            try: bm.faces.new(t[::-1] if flip else t)
            except ValueError: pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.location = loc; o.data.materials.append(m); return link(o)

# ---------- 尺度时间线（先定义：可见性、标签都要用） ----------
KEYS = [(0.0, 600000.0), (2.0, 400000.0), (4.5, 120000.0), (7.0, 12000.0), (9.0, 1000.0), (11.5, 100.0), (13.5, 25.0), (16.0, 4.0), (18.0, 3.0)]
def log_width(t):
    for (t0, w0), (t1, w1) in zip(KEYS, KEYS[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0)
            if t1 == KEYS[-1][0]: u = 1 - (1 - u) ** 2
            return math.log10(w0) + u * (math.log10(w1) - math.log10(w0))
    return math.log10(KEYS[-1][1])
view_w = lambda t: 10 ** log_width(t)
def t_at_width(w):
    for f in range(1, NF + 1):
        if view_w((f - 1) / FPS) <= w: return (f - 1) / FPS
    return DUR

# ---------- 芯片（5 mm 示例），表面 z = 0，前边缘 y = −2500 ----------
DIE = 5000.0; EDGE = -DIE / 2
WG_W, WG_H = 0.40, 0.22
SSC_L = 100.0                                       # 模斑转换器（示意）长 100 µm；焦点在它后面 50 µm
FOCUS = Vector((0.0, EDGE + 150.0, WG_H / 2))
die_top = box('die_surface', 0, 0, -0.01, DIE, DIE, 0.02, M['chip'], bev=0)
die_body = box('die_body', 0, 0, -375.5, DIE, DIE, 749.0, M['si_side'], bev=0.01)
clad = box('upper_cladding', 0, 0, 1.25, DIE - 2, DIE - 2, 2.5, M['clad'], bev=0)     # 整片上包层：很淡的玻璃面
FX = [250.0 * (i - 3) for i in range(8)]
WG_Y0, WG_Y1 = EDGE + SSC_L, EDGE + 1600
wgs, bands, tails, sscs, ssc_bands, electrodes = [], [], [], [], [], []
for i, x in enumerate(FX):
    cy, ly = (WG_Y0 + WG_Y1) / 2, WG_Y1 - WG_Y0
    wgs.append(box(f'wg_{i}', x, cy, WG_H / 2, WG_W, ly, WG_H, M['si_wg'], bev=0.08))
    bands.append(box(f'band_{i}', x, cy, WG_H / 2, WG_W * 0.62, ly, WG_H * 0.58, M['light'], bev=0))
    tails.append(box(f'tail_{i}', x, cy, WG_H / 2 + 0.001, WG_W * 2.0, ly, WG_H * 1.7, M['tail'], bev=0))
    sscs.append(box(f'ssc_{i}', x, EDGE + SSC_L / 2, 1.5, 8.0, SSC_L, 3.0, M['ssc'], bev=0.1))
    ssc_bands.append(box(f'ssc_band_{i}', x, EDGE + SSC_L / 2, 1.5, 3.0, SSC_L, 1.2, M['light'], bev=0))   # 模斑转换器里也有光（示意）
    for sgn in (-1, 1): electrodes.append(box(f'mzm_{i}_{sgn}', x + sgn * 9.0, EDGE + 665, 1.0, 10.0, 1000, 2.0, M['gold'], bev=0.15))
# 光纤阵列（端面耦合）：V 形槽块抵着芯片边缘，光纤躺在槽里，纤芯和波导同高；盖板省略
# 块底面落在模块电路板上（芯片也是直接贴在板上：芯片底面 z = −750 = 板顶面）
VG_L = 4000.0
vg = box('v_groove_block', 375.0, EDGE - VG_L / 2 - 5, -375.0, 2600, VG_L, 750, M['vgroove'], bev=0.02)
fibers, cores = [], []
for i, x in enumerate(FX):
    fibers.append(cyl(f'fiber_{i}', 62.5, VG_L, M['glass'], (x, EDGE - VG_L / 2 - 5, 0.0), (math.radians(90), 0, 0)))
    cores.append(cyl(f'fiber_core_{i}', 4.1, VG_L, M['light'], (x, EDGE - VG_L / 2 - 5, 0.0), (math.radians(90), 0, 0), verts=16))
hair = cyl('human_hair', 37.5, 3000.0, M['hair'], (300.0, EDGE - 450, 62.5 + 37.5), (0, math.radians(90), math.radians(8)), verts=24)
rbc = rbc_mesh('red_blood_cell', 7.5, M['rbc'], (6.0, FOCUS.y + 4.0, 2.5 + 1.1))

# ---------- 合并网格工具（很多小方块合成一个物体：省物体数，渲染快） ----------
def boxes(name, specs, mats, bev=0.0):
    """specs：(cx, cy, cz, sx, sy, sz, 材质序号[, 前脸材质序号])；前脸 = 朝 −y 的面"""
    bm = bmesh.new()
    for sp in specs:
        cx, cy, cz, sx, sy, sz, mi = sp[:7]; fi = sp[7] if len(sp) > 7 else mi
        r = bmesh.ops.create_cube(bm, size=1.0); vs = r['verts']
        for v in vs: v.co = Vector((cx + v.co.x * sx, cy + v.co.y * sy, cz + v.co.z * sz))
        for f in {f for v in vs for f in v.link_faces}:
            f.normal_update(); f.material_index = fi if f.normal.y < -0.9 else mi
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    o = bpy.data.objects.new(name, me); link(o)
    if bev: bevel(o, bev, seg=2)
    return o
def rounded_slab(name, cx, cy, cz, sx, sy, sz, r, m, edge_bev=0.0, seg=10):
    """圆角矩形板（手机）：四条竖边倒成半径 r 的圆角，上下棱再倒一点"""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
    ve = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) > 1e-6]
    bmesh.ops.bevel(bm, geom=ve, offset=r, segments=seg, profile=0.5, affect='EDGES')
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = (cx, cy, cz); o.data.materials.append(m); link(o)
    if edge_bev: bevel(o, edge_bev, seg=3)
    else:
        for p in o.data.polygons: p.use_smooth = True
    return o
def strip(name, pts, width, thick, m):
    """扁平带：沿 (x, y, z) 点列，x 方向宽 width、厚 thick（光纤带）"""
    bm = bmesh.new(); prev = None
    for (x, y, z) in pts:
        a = bm.verts.new((x - width / 2, y, z)); b = bm.verts.new((x + width / 2, y, z))
        if prev: bm.faces.new((prev[0], prev[1], b, a))
        prev = (a, b)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); o.data.materials.append(m); link(o)
    sol = o.modifiers.new('sol', 'SOLIDIFY'); sol.thickness = thick; sol.offset = 0.0
    return o
def smooth_path(way, n=60):
    """经过各控制点的平滑路径（段内余弦插值，各段相接处切线水平）"""
    out = []
    for (p0, p1) in zip(way, way[1:]):
        for k in range(n):
            u = k / n; s = 0.5 - 0.5 * math.cos(math.pi * u); out.append(tuple(a + (b - a) * (u if i == 1 else s) for i, (a, b) in enumerate(zip(p0, p1))))
    out.append(way[-1]); return out

# ---------- 光模块（QSFP-DD）----------
MOD_W, MOD_H = 18350.0, 8500.0
MOD_FRONT, MOD_BACK = -40000.0, 38000.0
PCB_Z = -750.0 - 500.0; PCB_TOP = PCB_Z + 500
pcb = box('module_pcb', 0, (MOD_FRONT + MOD_BACK) / 2, PCB_Z, MOD_W - 1200, MOD_BACK - MOD_FRONT - 2000, 1000, M['pcb'], bev=0.05)
# 金手指：QSFP-DD 每面两排（双密度），每排 19 个；靠板边一排短、往里一排长（示意）
fingers = [boxes('gold_fingers', [(-7000 + k * 760 + 250, 36000 - 650, PCB_TOP + 15, 500, 1300, 30, 0) for k in range(19)] +
                 [(-7000 + k * 760 + 250, 33250, PCB_TOP + 15, 500, 2300, 30, 0) for k in range(19)], [M['copper']])]
# DSP：BGA 焊球层（暗）+ 有机基板 + 金属盖
dsp = boxes('dsp', [(0, 18000, PCB_TOP + 175, 11600, 11600, 350, 0), (0, 18000, PCB_TOP + 350 + 450, 12000, 12000, 900, 1)], [M['plastic'], M['substrate']], bev=60)
dsp_lid = box('dsp_lid', 0, 18000, PCB_TOP + 1250 + 600, 9600, 9600, 1200, M['shell_end'], bev=0.12)
driver = box('driver_tia', -5200, 2000, PCB_TOP + 400, 3000, 3000, 800, M['ic'], bev=0.05)
laser = box('laser', 4200, 1200, PCB_TOP + 300, 1000, 2000, 600, M['laser'], bev=0.05)
# 0402 贴片电容（1.0 × 0.5 × 0.5 mm）：陶瓷本体 + 两端镀锡
def mlcc(x, y, along_x=True):
    L0, Wd, H = 1000.0, 500.0, 500.0; z = PCB_TOP + H / 2; out = []
    for off, ln, mi in ((-400, 200, 1), (0, 600, 0), (400, 200, 1)):
        out.append((x + off, y, z, ln, Wd, H, mi) if along_x else (x, y + off, z, Wd, ln, H, mi))
    return out
CAP_XY = [(-7000 + k * 1150, 25200, True) for k in range(12)] + [(-7000, 12500 + k * 1200, False) for k in range(9)] + \
         [(7000, 12500 + k * 1200, False) for k in range(9)] + [(-6300 + k * 1300, 10800, True) for k in range(4)] + \
         [(-6250, -8650, True), (-6250, -15650, True), (6250, -10650, True), (6250, -20650, True), (-6200, 4600, True), (-4200, 4600, True)]
caps = boxes('mlcc_caps', [b for (x, y, ax) in CAP_XY for b in mlcc(x, y, ax)], [M['mlcc'], M['tin']])
# 光纤带：从 V 形槽块后端出来，弯下去贴着电路板走，再抬起来进 MPO 插座（不悬空）
MPO_Y, MPO_Z = MOD_FRONT + 3500, PCB_TOP + 2300
rib_way = [(125.0, EDGE - VG_L - 5, 0.0), (125.0, EDGE - VG_L - 4500, PCB_TOP + 130), (125.0, MPO_Y + 6500, PCB_TOP + 130), (125.0, MPO_Y + 2500, MPO_Z)]
ribbon = strip('fiber_ribbon', smooth_path(rib_way, 40), 2100.0, 250.0, M['ribbon'])
mpo = box('mpo', 0, MPO_Y, MPO_Z, 9000, 5000, 4000, M['mpo'], bev=0.05)
rice = ellipsoid('rice_grain', 1300, 3200, 950, M['rice'], (6000, -6000, PCB_TOP + 950), (0, 0, math.radians(15)))
SHELL_Z = PCB_Z - 1500 + MOD_H / 2
shell = box('module_shell', 0, (MOD_FRONT + MOD_BACK) / 2, SHELL_Z, MOD_W, MOD_BACK - MOD_FRONT, MOD_H, M['shell'], bev=0.04)
shell_front = box('module_front', 0, MOD_FRONT + 1000, SHELL_Z, MOD_W, 2000, MOD_H, M['shell_end'], bev=0.04)
TAB_DZ = -3900.0                                                                 # 拉环贴着模块底面往前伸
tab = box('pull_tab', 0, MOD_FRONT - 7500, SHELL_Z + TAB_DZ, 9000, 15000, 1200, M['tab'], bev=0.2)

# ---------- 交换机（1U，2 排 × 16 个 QSFP-DD，上下对齐的 2×1 叠层笼子）+ 机柜 + 托板 + 手机 ----------
U = 44450.0
FACE_Y = MOD_FRONT + 6000                                                        # 面板前表面附近；模块前端伸出面板约 5 mm
SW_ZC = SHELL_Z - 9000
SW_W, SW_D = 440000.0, 420000.0
PITCH = 23000.0
OUR_COL = 7                                                                      # 我们的模块在上排第 7 列，画面居中
port_x = lambda col, row=0: (col - OUR_COL) * PITCH
sw_xc = port_x(7.5)                                                              # 机箱中心
ROW_Z = (SW_ZC + 9000, SW_ZC - 9000)
BOARD_TOP = SW_ZC - U / 2 + 4200                                                 # 主板顶面
sw = [box('sw_face', sw_xc, FACE_Y, SW_ZC, SW_W, 2500, U, M['face'], bev=0.03),
      box('sw_bottom', sw_xc, FACE_Y + SW_D / 2, SW_ZC - U / 2 + 1000, SW_W, SW_D, 2000, M['sw'], bev=0.1),
      box('sw_cover', sw_xc, FACE_Y + SW_D / 2, SW_ZC + U / 2 - 600, SW_W, SW_D, 1200, M['sw_top'], bev=0),
      boxes('sw_walls', [(sw_xc - SW_W / 2 + 750, FACE_Y + SW_D / 2, SW_ZC, 1500, SW_D, U - 1200, 0), (sw_xc + SW_W / 2 - 750, FACE_Y + SW_D / 2, SW_ZC, 1500, SW_D, U - 1200, 0),
                         (sw_xc, FACE_Y + SW_D - 750, SW_ZC, SW_W, 1500, U - 1200, 0)], [M['sw']])]
# 机箱里面（透过透明上盖看得到，压暗）：交换芯片 + 散热片（鳍片顺着前后风道）、后部风扇和两个电源
ASIC_Y = FACE_Y + 200000
inside = [box('sw_asic', sw_xc, ASIC_Y, BOARD_TOP + 2000, 75000, 75000, 4000, M['asic'], bev=0.05),
          boxes('asic_heatsink', [(sw_xc, ASIC_Y, BOARD_TOP + 4000 + 2000, 100000, 100000, 4000, 0)] +
                [(sw_xc - 48750 + k * 2500, ASIC_Y, BOARD_TOP + 8000 + 14000, 800, 100000, 28000, 0) for k in range(40)], [M['heatsink']]),
          boxes('fans', [(sw_xc + (k - 2.5) * 44000, FACE_Y + SW_D - 30000, BOARD_TOP + 19000, 40000, 52000, 38000, 0) for k in range(6)] +
                [(sw_xc + (k - 2.5) * 44000, FACE_Y + SW_D - 4000, BOARD_TOP + 19000, 20000, 3000, 6000, 0) for k in range(6)], [M['plastic']], bev=400),
          boxes('psus', [(sw_xc + sgn * (SW_W / 2 - 32000), FACE_Y + SW_D - 95000, BOARD_TOP + 19000, 54000, 180000, 38000, 0) for sgn in (-1, 1)], [M['sw']], bev=400)]
host_board = box('host_board', sw_xc, FACE_Y + SW_D / 2, BOARD_TOP - 800, SW_W - 4000, SW_D - 4000, 1600, M['host_pcb'], bev=0)
# 端口笼子：面板前面一圈笼口（4 条边），面板后面是笼子主体（顶上有冲孔）；笼口里面是暗的
CAGE_W, CAGE_D = 21000.0, 70000.0
CAGE_Y = FACE_Y + 1250 + CAGE_D / 2
rings = []
for col in range(16):
    for z in ROW_Z:
        x = port_x(col); y = FACE_Y - 1250 - 450
        rings += [(x, y, z + 5000, CAGE_W, 900, 1000, 0), (x, y, z - 5000, CAGE_W, 900, 1000, 0),
                  (x - 10000, y, z, 1000, 900, 9000, 0), (x + 10000, y, z, 1000, 900, 9000, 0)]
rings = boxes('cage_rings', rings, [M['cage']], bev=150)
cage_specs = []
for col in range(16):
    x = port_x(col)
    if col == OUR_COL:                                                           # 我们这一列：下面的笼子单独一块，上面那格（我们的）另做
        cage_specs.append((x, CAGE_Y, (BOARD_TOP + ROW_Z[0] - 5500) / 2, CAGE_W, CAGE_D, ROW_Z[0] - 5500 - BOARD_TOP, 0, 1))
    else:
        cage_specs.append((x, CAGE_Y, (BOARD_TOP + ROW_Z[0] + 5500) / 2, CAGE_W, CAGE_D, ROW_Z[0] + 5500 - BOARD_TOP, 0, 1))
cages = boxes('cages', cage_specs, [M['cage_body'], M['mouth']], bev=120)
our_cage = boxes('our_cage', [(port_x(OUR_COL), CAGE_Y, ROW_Z[0], CAGE_W, CAGE_D, 11000, 0, 1)], [M['cage_body'], M['mouth']], bev=120)
host_conn = box('host_connector', 0, MOD_BACK + 3000, (BOARD_TOP + ROW_Z[0] + 5000) / 2, 20000, 10000, ROW_Z[0] + 5000 - BOARD_TOP, M['plastic'], bev=0.03)
# 面板上的东西：端口指示灯（导光柱）、左侧系统指示灯、右侧两个管理口（RJ45）
leds = [boxes('port_leds', [(port_x(c) + 8000, FACE_Y - 1700, z + (6300 if z > SW_ZC else -6300), 1500, 400, 900, 0) for c in range(16) for z in ROW_Z], [M['led']])]
leds.append(boxes('sys_leds', [(sw_xc - SW_W / 2 + 14000 + k * 4500, FACE_Y - 1500, SW_ZC + 12000, 1600, 400, 1000, 0) for k in range(3)], [M['led']]))
mgmt = boxes('mgmt_ports', [(sw_xc + SW_W / 2 - 19000, FACE_Y - 1300, SW_ZC + sgn * 9000, 16000, 600, 13500, 0) for sgn in (-1, 1)], [M['rj45']], bev=200)
# 其它端口上的模块（只露出面板外的一段）+ 拉环；所有模块（包括我们的）都插着 MPO 跳线
others, plug_specs, our_plug_specs = [], [], []
for col in range(16):
    for z in ROW_Z:
        x = port_x(col); ours = (col == OUR_COL and z == ROW_Z[0])
        dst = our_plug_specs if ours else plug_specs
        dst += [(x, FACE_Y - 6000 - 5500, z + 300, 12400, 11000, 6400, 0), (x, FACE_Y - 17000 - 12500, z + 300, 6500, 25000, 4800, 1)]   # MPO 插头外壳 + 尾套
        if ours: continue
        others += [(x, FACE_Y - 3000, z, MOD_W, 6000, MOD_H, 0), (x, FACE_Y - 6000 - 7500, z + TAB_DZ, 9000, 15000, 1200, 1)]
others = [boxes('other_modules', others, [M['shell_end'], M['tab']], bev=150)]
plugs = boxes('mpo_plugs', plug_specs, [M['mpo_apc'], M['patch']], bev=250)
our_plug = boxes('our_mpo_plug', our_plug_specs, [M['mpo_apc'], M['patch']], bev=250)
# 跳线：从尾套出来先往前，再垂下去分到两侧理线（每根略有不同）
rng = random.Random(7); cords = []
for col in range(16):
    for z in ROW_Z:
        x = port_x(col); side = -1 if col < 8 else 1; j = rng.uniform(-1, 1)
        p0 = Vector((x, FACE_Y - 42000, z + 300))
        pts = [p0, p0 + Vector((0, -14000, -2500 + 1500 * j)), Vector((x + side * 6000, FACE_Y - 66000 - 5000 * j, z - 45000)),
               Vector((x * 0.75 + side * 60000, FACE_Y - 72000 - 6000 * j, z - 150000))]
        c = tube(f'cord_{col}_{"t" if z > SW_ZC else "b"}', pts, 1500, M['patch'])
        if col == OUR_COL and z == ROW_Z[0]: our_cord = c
        else: cords.append(c)
# 机柜：两根立柱（EIA-310 方孔）、交换机挂耳和螺丝、下面两台设备（前面板冲孔 + 指示灯）
RAIL_Y = FACE_Y + 12500
rack = [box('device_below', sw_xc, FACE_Y + SW_D / 2, SW_ZC - U, SW_W, SW_D, U - 800, M['other'], bev=0.02),
        box('device_below2', sw_xc, FACE_Y + SW_D / 2, SW_ZC - 2 * U, SW_W, SW_D, U - 800, M['other'], bev=0.02),
        boxes('ears', [(sw_xc + sgn * (SW_W / 2 + 12000), FACE_Y - 2750 - 750, SW_ZC, 26000, 1500, U - 1000, 0) for sgn in (-1, 1)], [M['sw']], bev=300),
        boxes('below_leds', [(sw_xc - SW_W / 2 + 14000 + k * 4500, FACE_Y - 400, SW_ZC - U * (1 + d) + 12000, 1600, 400, 1000, 0) for k in range(3) for d in range(2)], [M['led']])]
for sgn in (-1, 1):
    for zc in (6350.0, 38100.0):                                                 # 挂耳螺丝：在这一 U 的第 1、3 个孔
        rack.append(cyl(f'screw_{sgn}_{int(zc)}', 5500, 2000, M['cage'], (sw_xc + sgn * (SW_W / 2 + 15000), FACE_Y - 4500 - 1000, SW_ZC - U / 2 + zc), (math.radians(90), 0, 0), verts=24))
# 上方空 U 位：一条浅托板，从左边伸到我们的模块左侧为止；手机横放（长边沿 x），完全在托板上
SHELF_X0, SHELF_X1 = -200000.0, -14000.0
shelf = box('shelf_empty_u', (SHELF_X0 + SHELF_X1) / 2, FACE_Y + 40000, SW_ZC + U / 2 + 1500, SHELF_X1 - SHELF_X0, 80000, 2000, M['shelf'], bev=0.05)
PHONE = Vector((SHELF_X1 - 4000 - 75000, FACE_Y + 40000, SW_ZC + U / 2 + 2500 + 4000))
phone = rounded_slab('phone', PHONE.x, PHONE.y, PHONE.z, 150000, 71000, 7600, 9500, M['phone_frame'], edge_bev=1200)
phone_scr = rounded_slab('phone_screen', PHONE.x, PHONE.y, PHONE.z + 3600, 149000, 70000, 600, 9000, M['phone_screen'])
phone_cam = cyl('phone_front_camera', 1600, 200, M['rj45'], (PHONE.x + 75000 - 9000, PHONE.y, PHONE.z + 3950), verts=24)
phone_btn = boxes('phone_buttons', [(PHONE.x + 30000 + k * 16000, PHONE.y + 35500 + 500, PHONE.z, 12000 if k else 7000, 1000, 2600, 0) for k in range(2)], [M['phone_frame']], bev=300)

# ---------- 机房环境：交换机在一台开放式机架的顶部，左右是闭合机柜，身后一排排机柜伸向远处 ----------
# 「环境最重要」（用户 2026-11-10）：不再是深蓝虚空。单位 µm；机柜 600 mm 宽、2 m 高，排距 2.4 m
FLOOR_TEX = os.path.join(HERE, 'assets', 'floor_tile.png'); LEDS_TEX = os.path.join(HERE, 'assets', 'rack_leds.png')
def mat_rack_front(name):
    """机柜前门：冲孔深灰 + 零散指示灯（自发光，进环境辉光遮罩）"""
    m = mat_holes(name, (0.05, 0.055, 0.06), 0.6, 0.45, PERF_TEX, 'X', 'Z', 30000.0, 31170.0); N = m.node_tree.nodes; L = m.node_tree.links; b = N['Principled BSDF']
    it = _img(N, L, LEDS_TEX, _obj_uv(N, L, 'X', 'Z', 1 / 600000.0, 1 / 2000000.0, 0.5, 0.5)); sp = N.new('ShaderNodeSeparateColor'); L.new(it.outputs['Color'], sp.inputs[0])
    c = _mix(N, L, sp.outputs['Red'], (0, 0, 0), (0.15, 1.0, 0.3)); c = _mix(N, L, sp.outputs['Green'], c, (0.2, 0.5, 1.0)); c = _mix(N, L, sp.outputs['Blue'], c, (1.0, 0.55, 0.1)); c = _mix(N, L, it.outputs['Alpha'], c, (1.0, 1.0, 1.0))
    L.new(c, b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 6.0
    ao = N.new('ShaderNodeOutputAOV'); ao.aov_name = 'envglow'; mx = N.new('ShaderNodeMath'); mx.operation = 'MAXIMUM'
    m2 = N.new('ShaderNodeMath'); m2.operation = 'MAXIMUM'; L.new(sp.outputs['Red'], mx.inputs[0]); L.new(sp.outputs['Green'], mx.inputs[1]); L.new(mx.outputs[0], m2.inputs[0]); L.new(sp.outputs['Blue'], m2.inputs[1])
    m3 = N.new('ShaderNodeMath'); m3.operation = 'MAXIMUM'; L.new(m2.outputs[0], m3.inputs[0]); L.new(it.outputs['Alpha'], m3.inputs[1]); L.new(m3.outputs[0], ao.inputs['Value'])
    return m
def mat_floor():
    m = mat_holes('raised_floor', (0.30, 0.31, 0.32), 0.2, 0.35, FLOOR_TEX, 'X', 'Y', 1200000.0, 600000.0, hole=(0.03, 0.03, 0.035), bump=0.2)
    m.node_tree.nodes['Principled BSDF'].inputs['Coat Weight'].default_value = 0.4; return m
M.update(rack_front=mat_rack_front('rack_front_door'), floor=mat_floor(),
         tray=mat('fiber_tray_yellow', (0.80, 0.55, 0.04), 0.0, 0.45),
         ceil_light=mat_emit('ceiling_light', (1.0, 0.92, 0.80) if LOOK == 'warm' else (0.85, 0.93, 1.0), 12.0)[0])
for k in ('ceil_light', 'led'):                       # 环境里的灯也进「环境辉光」遮罩（和光带的辉光分开）
    nt = M[k].node_tree; ao = nt.nodes.new('ShaderNodeOutputAOV'); ao.aov_name = 'envglow'; ao.inputs['Value'].default_value = 1.0
MM = 1000.0
RACK_TOP = SW_ZC + U / 2 + 1.5 * U                    # 交换机上面只有放手机的那一格，再往上是机架顶
FLOOR = RACK_TOP - 42 * U                             # 42U 机架，约 1.87 m
RW_, RD_, RH_ = 600 * MM, 1070 * MM, 42 * U + 60 * MM
RACK_Y0 = FACE_Y - 30 * MM                            # 机柜前门所在的平面（比设备面板靠前一点）
hall = []
# 我们这台开放式机架：4 根立柱，从地板到顶；交换机下面塞满设备（1U / 2U，前面板冲孔 + 指示灯）
for sx in (-1, 1):
    for dy in (0.0, 900 * MM):
        hall.append(box(f'post_{sx}_{int(dy)}', sw_xc + sx * (SW_W / 2 + 15000), RAIL_Y + dy, (FLOOR + RACK_TOP) / 2, 25000, 30000, RACK_TOP - FLOOR, M['rack'], bev=0.02))
rng_h = random.Random(11); specs, led_specs = [], []; zt = SW_ZC - U / 2 - 2 * U
while zt - U > FLOOR + 4 * U:
    h = U * rng_h.choice((1, 1, 2, 2, 4)); zc = zt - h / 2
    specs.append((sw_xc, FACE_Y + SW_D / 2, zc, SW_W, SW_D, h - 800, 0))
    for k in range(rng_h.randint(2, 6)): led_specs.append((sw_xc - SW_W / 2 + 12000 + k * 4000, FACE_Y - 400, zc + h / 2 - 9000, 1500, 400, 900, 0))
    zt -= h
hall += [boxes('rack_gear', specs, [M['other']], bev=300), boxes('rack_gear_leds', led_specs, [M['led']])]
# 左右两台闭合机柜、身后 7 排机柜（正面朝相机），每排 24 台
rack_specs = [(sw_xc + sx * RW_, RACK_Y0 + RD_ / 2, FLOOR + RH_ / 2, RW_ - 4 * MM, RD_, RH_, 0) for sx in (-1, 1, -2, 2, -3, 3)]
for r in range(1, 8):
    y0 = RACK_Y0 + 2400 * MM * r
    for c in range(-12, 12): rack_specs.append((sw_xc + (c + 0.5) * RW_, y0 + RD_ / 2, FLOOR + RH_ / 2, RW_ - 4 * MM, RD_, RH_, 0))
hall.append(boxes('hall_racks', rack_specs, [M['rack_front']], bev=0))
# 地板、天花板灯带（每条通道上方一条）、黄色光纤走线槽
hall.append(box('floor', sw_xc, RACK_Y0 + 9000 * MM, FLOOR - 25 * MM, 30000 * MM, 30000 * MM, 50 * MM, M['floor'], bev=0))
hall.append(boxes('ceiling_lights', [(sw_xc, RACK_Y0 + 2400 * MM * r - 600 * MM, FLOOR + 3200 * MM, 14000 * MM, 120 * MM, 40 * MM, 0) for r in range(-1, 8)], [M['ceil_light']]))
hall.append(boxes('fiber_trays', [(sw_xc, RACK_Y0 + 2400 * MM * r + 500 * MM, FLOOR + RH_ + 450 * MM, 14000 * MM, 300 * MM, 100 * MM, 0) for r in range(0, 8)], [M['tray']]))

# ---------- 可见性：每个物体只登记一个区间；淡入淡出用物体颜色 alpha，淡完关渲染 ----------
VIS = {}
def vis(objs, t_in=None, t_out=None, fade=0.4):
    for o in objs if isinstance(objs, (list, tuple)) else [objs]:
        VIS[o.name] = (o, t_in, t_out, fade)
def appear(objs, size, px=1.0, fade=0.5):           # 物体约 px 像素大时开始淡入
    t = t_at_width(size * W / px); vis(objs, t if t > 0.01 else None, None, fade)
appear(wgs + bands + tails, WG_W * 3, 1.0)           # 单根波导太细时，由芯片贴图里的光路代替
appear(sscs + ssc_bands, 8.0, 1.5); appear(electrodes, 10.0, 1.5)
vis(fibers + cores, None, 11.0, 0.5); vis([hair], 7.0, 9.8, 0.4); vis([vg], None, 10.6, 0.5)
vis([clad], 8.0, None, 1.0); vis([rbc], 11.2, 14.8, 0.4)
vis([phone, phone_scr, phone_cam, phone_btn, shelf], None, 4.6, 0.4)
# 面板、上盖、跳线、机柜、机箱里远处的东西：相机穿过面板前淡出
vis(sw + inside + leds + [mgmt, rings, plugs] + others + cords, None, 4.3, 0.6)
vis([our_cage], None, 3.9, 0.6)                      # 我们这一格的笼子先透明化，露出模块
vis([cages, host_conn, host_board], None, 6.6, 0.6)
vis(hall + rack, None, 6.6, 0.8)                      # 机房环境、机架：一直留到推进模块里面  # 穿过面板以后，旁边的笼子、主板、后面的连接器还在（不在虚空里）
vis([shell, shell_front, tab, our_plug, our_cord], None, 5.4, 0.6)
vis([dsp, dsp_lid, driver, laser, mpo, pcb, ribbon, caps] + fingers, None, 9.4, 0.6)
vis([rice], 4.4, 8.0, 0.4)

# ---------- 3D 标签：字保持屏幕大小（反向缩放），尺寸箭头跟着物体真实大小 ----------
FNT = bpy.data.fonts.load(FONT)
LABEL_FRAC = 0.05                                    # 字高约占画面宽的比例（默认 5%，短标签可以更大）
labels = {}
CRUMB = 2.5                                          # 旧标签留在原地缩小的时长（参考片 A：旧标签不消失，跟着场景缩小）
def label(key, text, loc, t_in, t_out, arrow=None, arrow_z=None, frac=LABEL_FRAC, crumb=True):
    t_mid = t_in + 0.3; h0 = frac * view_w(t_mid); t_hold = t_out
    if t_out and crumb: t_out = min(DUR, t_out + CRUMB)
    cu = bpy.data.curves.new('lbl_' + key, 'FONT'); cu.body = text; cu.font = FNT; cu.size = 1.0; cu.align_x = 'CENTER'; cu.extrude = 0.04   # 字号放在物体缩放里（Blender 文字字号上限 10000）
    o = bpy.data.objects.new('lbl_' + key, cu); o.data.materials.append(M['label']); link(o); o.location = loc
    for f in range(max(1, F(t_in) - 1), min(NF, F(t_out if t_out else DUR) + 1) + 1):
        tt = (f - 1) / FPS if not t_hold else min((f - 1) / FPS, t_hold)   # 过了 t_hold 不再反向缩放：字跟着世界一起变小
        k = h0 * view_w(tt) / view_w(t_mid); o.scale = (k, k, k); o.keyframe_insert('scale', frame=f)
    vis([o], t_in if t_in > 0 else None, t_out, 0.6 if crumb else 0.25); parts = [o]
    if arrow:                                        # 双箭头横跨被量的东西（真实尺寸）
        az = arrow_z if arrow_z is not None else loc[2] - h0 * 0.6; th = arrow * 0.02
        parts.append(box('lbl_' + key + '_shaft', loc[0], loc[1], az, arrow * 0.84, th, th, M['label'], bev=0))
        for sgn in (-1, 1):
            bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=arrow * 0.05, radius2=0, depth=arrow * 0.08); me = bpy.data.meshes.new('tip'); bm.to_mesh(me); bm.free()
            tip = bpy.data.objects.new('lbl_' + key + f'_tip{sgn}', me); tip.data.materials.append(M['label']); link(tip)
            tip.location = (loc[0] + sgn * arrow * 0.46, loc[1], az); tip.rotation_euler = (0, sgn * math.radians(90), 0); parts.append(tip)
        vis(parts[1:], t_in if t_in > 0 else None, t_out, 0.6)
    labels[key] = o; return parts
label('switch', '交换机', (0, FACE_Y - 30000, SW_ZC + 60000), 0.0, 2.2, frac=0.09)
label('module', '光模块 约 9 cm（含拉环）', (0, MOD_FRONT - 4000, SHELL_Z + 16000), 2.4, 4.8, frac=0.055)
label('chip', '硅光芯片 约 5 mm（示例）', (0, -400, 900), 5.0, 7.6, arrow=DIE, arrow_z=300, frac=0.06)
label('fiber', '光纤 125 µm', (-250, EDGE - 250, 200), 7.4, 8.6, arrow=125, arrow_z=75, frac=0.05, crumb=False)   # 和头发标签同一位置附近，不留
label('hair', '头发 约 0.07–0.08 mm', (150, EDGE - 520, 230), 8.6, 9.6, frac=0.045, crumb=False)   # 和光纤标签错开时间，不叠在一起
label('rbc', '红细胞 约 7.5 µm', (6.0, FOCUS.y + 5.0, 9.0), 11.8, 14.0, arrow=7.5, arrow_z=5.6, frac=0.055)
label('wg', '不到 0.5 µm', (0.0, FOCUS.y, 0.55), 16.0, None, arrow=WG_W, arrow_z=WG_H + 0.05, frac=0.07)   # 放在焦平面上，不被景深虚掉
for name, (o, t_in, t_out, fade) in VIS.items():
    def key(t, a, hide):
        fr = max(1, F(t)); o.color[3] = a; o.keyframe_insert('color', index=3, frame=fr); o.hide_render = hide; o.keyframe_insert('hide_render', frame=fr)
    if t_in: key(0.0, 0.0, True); key(t_in, 0.0, False); key(t_in + fade, 1.0, False)
    else: key(0.0, 1.0, False)
    if t_out: key(t_out - fade, 1.0, False); key(t_out, 0.0, False); key(t_out + 1 / FPS, 0.0, True)
    for fc in fcurves_of(o):
        if fc.data_path in ('hide_render', 'color'):
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT' if fc.data_path == 'hide_render' else 'LINEAR'

# ---------- 世界缩放（逐帧关键帧）；焦点路径 ----------
CPATH = [(0.0, Vector((sw_xc * 0.35, FACE_Y + 30000, SW_ZC))), (2.0, Vector((-20000, FACE_Y + 15000, SW_ZC + 6000))),
         (4.5, Vector((0, MOD_FRONT + 25000, SHELL_Z))), (7.0, Vector((0, EDGE - 800, 0))), (9.0, Vector((0, EDGE + 100, 0))),
         (11.5, Vector((2.0, FOCUS.y, 1.0))), (18.0, FOCUS)]
def center(t):
    for (t0, c0), (t1, c1) in zip(CPATH, CPATH[1:]):
        if t0 <= t <= t1:
            u = (t - t0) / (t1 - t0); u = u * u * (3 - 2 * u); return c0.lerp(c1, u)
    return CPATH[-1][1]
VIEW0 = 3.0
for f in range(1, NF + 1):
    t = (f - 1) / FPS; s = VIEW0 / view_w(t); c = center(t)
    WORLD.scale = (s, s, s); WORLD.location = -c * s
    WORLD.keyframe_insert('scale', frame=f); WORLD.keyframe_insert('location', frame=f)
set_interp(WORLD, 'LINEAR')

# ---------- 相机、灯光、环境 ----------
rig = bpy.data.objects.new('cam_rig', None); sc.collection.objects.link(rig)
bpy.ops.object.camera_add(); cam = bpy.context.object; cam.parent = rig; sc.camera = cam
cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.lens = 35
hfov = 2 * math.atan((24 * W / H) / 2 / 35); DIST = (VIEW0 / 2) / math.tan(hfov / 2)
EL = math.radians(26)                                # 俯角放低：看得到远处
cam.location = (0, -DIST * math.cos(EL), DIST * math.sin(EL)); cam.rotation_euler = (math.radians(90) - EL, 0, 0)
cam.data.clip_start = DIST * 0.05; cam.data.clip_end = DIST * 3000
cam.data.dof.use_dof = True; cam.data.dof.focus_distance = DIST
# 场景 1 单位 = 1 µm，但 Blender 按 1 单位 = 1 m 算景深，所以光圈值要很小才有浅景深
# 第二版：硬件段也开大光圈，像微距不像产品图（参考片两部全程浅景深）
for t, fs in ((0.0, 0.35), (4.5, 0.25), (9.0, 0.14), (13.5, 0.07), (18.0, 0.06)):
    cam.data.dof.aperture_fstop = fs; cam.data.dof.keyframe_insert('aperture_fstop', frame=F(t))
rig.rotation_euler = (0, 0, math.radians(-12)); rig.keyframe_insert('rotation_euler', index=2, frame=1)
rig.rotation_euler = (0, 0, math.radians(14)); rig.keyframe_insert('rotation_euler', index=2, frame=NF)
# 相机绕视线慢慢滚转（参考片 A：每秒 1–2°）：先绕自身视轴滚，再俯仰 → 欧拉顺序 ZXY
cam.rotation_mode = 'ZXY'
for fr, r in ((1, -9.0), (NF, 15.0)): cam.rotation_euler = (math.radians(90) - EL, 0, math.radians(r)); cam.keyframe_insert('rotation_euler', index=2, frame=fr)
set_interp(cam, 'LINEAR')
for o in labels.values():
    tc = o.constraints.new('TRACK_TO'); tc.target = cam; tc.track_axis = 'TRACK_Z'; tc.up_axis = 'UP_Y'
def area(name, loc, energy, size, col):
    L = bpy.data.lights.new(name, 'AREA'); L.energy = energy; L.size = size; L.color = col; o = bpy.data.objects.new(name, L); sc.collection.objects.link(o)
    o.parent = rig; o.location = loc; tc = o.constraints.new('TRACK_TO'); tc.target = rig; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'; return o
k2 = DIST ** 2
# 灯光（第二版）：低角度逆光勾边 + 弱的正面补光 + 顶上柔光。两种风格：warm = 暖金逆光，cool = 冷调机房（暖白勾边）
LOOKS = dict(
    warm=dict(back=(1.0, 0.62, 0.30), fill=(0.55, 0.66, 0.90), top=(1.0, 0.85, 0.65), haze=(0.36, 0.19, 0.07), dust=(1.0, 0.82, 0.55)),
    cool=dict(back=(0.75, 0.88, 1.0), fill=(0.40, 0.65, 1.00), top=(0.80, 0.90, 1.00), haze=(0.03, 0.12, 0.20), dust=(0.80, 0.92, 1.0)))
LK = LOOKS[LOOK]
area('back', (DIST * 0.25, DIST * 1.9, DIST * 1.1), 120 * k2, DIST * 1.2, LK['back'])
area('fill', (-DIST * 1.1, -DIST * 1.0, DIST * 0.5), 22 * k2, DIST * 1.6, LK['fill'])
area('top', (-DIST * 0.3, DIST * 0.2, DIST * 2.2), 18 * k2, DIST * 2.0, LK['top'])
# 前景灰尘（用户 2026-11-10：「这种前景灰尘是很有必要的」）：挂在相机上，离镜头很近、虚成光斑，慢慢漂；
# 在相机空间里，所以每个尺度看起来都一样。数量少，不做粒子特效
vfov = 2 * math.atan(12 / 35); rd = random.Random(5); dust_m = mat_emit('dust', LK['dust'], 0.5, alpha=0.18)[0]; dust = []
for k in range(28):
    d = DIST * rd.uniform(0.18, 0.7); x = rd.uniform(-1, 1) * d * math.tan(hfov / 2) * 1.1; y = rd.uniform(-1, 1) * d * math.tan(vfov / 2) * 1.1
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=DIST * rd.uniform(0.0006, 0.0022)); me = bpy.data.meshes.new('dust'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(f'dust_{k}', me); o.data.materials.append(dust_m); sc.collection.objects.link(o); o.parent = cam
    v = Vector((rd.uniform(-1, 1), rd.uniform(-0.6, 0.3), rd.uniform(-0.3, 0.3))) * DIST * 0.012
    for fr, tt in ((1, 0.0), (NF, DUR)): o.location = Vector((x, y, -d)) + v * tt; o.keyframe_insert('location', frame=fr)
    set_interp(o, 'LINEAR'); dust.append(o)
# 环境：HDRI 只用来打光和出反射（调暗，不要平光）；相机直接看到的远处是雾的颜色（和合成里的空气透视同色）
wd = bpy.data.worlds.new('w'); sc.world = wd; wd.use_nodes = True; N = wd.node_tree.nodes; L = wd.node_tree.links
for n in list(N): N.remove(n)
out = N.new('ShaderNodeOutputWorld'); bg_hdr = N.new('ShaderNodeBackground'); bg_col = N.new('ShaderNodeBackground'); mx = N.new('ShaderNodeMixShader'); lp = N.new('ShaderNodeLightPath')
bg_col.inputs['Color'].default_value = (*LK['haze'], 1); bg_hdr.inputs['Strength'].default_value = 0.35
if os.path.exists(HDRI):
    env = N.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(HDRI, check_existing=True); L.new(env.outputs['Color'], bg_hdr.inputs['Color'])
else:
    print('没找到 HDRI：', HDRI, '—— 用纯色环境代替'); bg_hdr.inputs['Color'].default_value = (0.5, 0.55, 0.65, 1)
L.new(bg_hdr.outputs[0], mx.inputs[1]); L.new(bg_col.outputs[0], mx.inputs[2]); L.new(lp.outputs['Is Camera Ray'], mx.inputs['Fac']); L.new(mx.outputs[0], out.inputs[0])

# ---------- 渲染设置 ----------
if CYCLES:
    sc.render.engine = 'CYCLES'; sc.cycles.samples = SAMP; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 4
    if GPU:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for dt in ('OPTIX', 'CUDA'):
            try:
                prefs.compute_device_type = dt; prefs.refresh_devices()
                if [d for d in prefs.devices if d.type == dt]:
                    for d in prefs.devices: d.use = d.type == dt
                    sc.cycles.device = 'GPU'; print('GPU_DEVICE', dt); break
            except Exception: pass
else:
    ENG = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    sc.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in ENG else 'BLENDER_EEVEE_NEXT'
    for k, v in (('taa_render_samples', SAMP), ('use_raytracing', True), ('use_shadows', True), ('use_fast_gi', True)):
        try: setattr(sc.eevee, k, v)
        except Exception as e: print('EEVEE 设置跳过', k, e)
sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, NF
sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.3
sc.view_settings.view_transform = 'AgX'
for lk in ('AgX - Medium High Contrast', 'Medium High Contrast'):
    try: sc.view_settings.look = lk; break
    except Exception: pass
# 合成：只给「光」加辉光（AOV 遮罩 × 自发光层 → 辉光 → 叠加回去）
try:
    vl = sc.view_layers[0]; vl.use_pass_emit = True; vl.use_pass_mist = True
    for an in ('lightmask', 'envglow'): aov = vl.aovs.add(); aov.name = an; aov.type = 'VALUE'
    wd.mist_settings.start = DIST * 1.05; wd.mist_settings.depth = DIST * 5.0; wd.mist_settings.falloff = 'QUADRATIC'
    ng = bpy.data.node_groups.new('comp', 'CompositorNodeTree'); sc.compositing_node_group = ng
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new('CompositorNodeRLayers'); rl.scene = sc
    emit = rl.outputs.get('Emit') or rl.outputs.get('Emission'); mask = rl.outputs.get('lightmask')
    print('RLAYER_OUTPUTS', [o.name for o in rl.outputs])
    mul = ng.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1.0
    ng.links.new(emit, mul.inputs['A']); ng.links.new(mask, mul.inputs['B'])
    gl = ng.nodes.new('CompositorNodeGlare'); ng.links.new(mul.outputs['Result'], gl.inputs['Image'])
    for k, v in (('Type', 'Fog Glow'), ('Threshold', 0.0), ('Strength', 0.9), ('Quality', 'High')):
        try: gl.inputs[k].default_value = v
        except Exception as e: print('辉光参数跳过', k, e)
    add = ng.nodes.new('ShaderNodeMix'); add.data_type = 'RGBA'; add.blend_type = 'ADD'; add.inputs['Factor'].default_value = 1.0
    ng.links.new(rl.outputs['Image'], add.inputs['A']); ng.links.new(gl.outputs['Glare'], add.inputs['B'])
    # 环境里的灯（指示灯、天花板灯带）单独一层辉光，和光带分开
    mul2 = ng.nodes.new('ShaderNodeMix'); mul2.data_type = 'RGBA'; mul2.blend_type = 'MULTIPLY'; mul2.inputs['Factor'].default_value = 1.0
    ng.links.new(emit, mul2.inputs['A']); ng.links.new(rl.outputs.get('envglow'), mul2.inputs['B'])
    gl2 = ng.nodes.new('CompositorNodeGlare'); ng.links.new(mul2.outputs['Result'], gl2.inputs['Image'])
    for k, v in (('Type', 'Bloom'), ('Threshold', 0.3), ('Strength', 1.2), ('Size', 0.8), ('Quality', 'High')):
        try: gl2.inputs[k].default_value = v
        except Exception as e: print('环境辉光参数跳过', k, e)
    add2 = ng.nodes.new('ShaderNodeMix'); add2.data_type = 'RGBA'; add2.blend_type = 'ADD'; add2.inputs['Factor'].default_value = 1.0
    ng.links.new(add.outputs['Result'], add2.inputs['A']); ng.links.new(gl2.outputs['Glare'], add2.inputs['B'])
    # 空气透视：按雾层把远处混成雾的颜色（每个尺度都一样，参考片 A 越远越亮越淡）
    hz = ng.nodes.new('ShaderNodeMath'); hz.operation = 'MULTIPLY'; hz.inputs[1].default_value = 0.88; ng.links.new(rl.outputs['Mist'], hz.inputs[0])
    fog = ng.nodes.new('ShaderNodeMix'); fog.data_type = 'RGBA'; fog.blend_type = 'MIX'; ng.links.new(hz.outputs[0], fog.inputs['Factor'])
    ng.links.new(add2.outputs['Result'], fog.inputs['A']); fog.inputs['B'].default_value = (*LK['haze'], 1)
    go = ng.nodes.new('NodeGroupOutput'); ng.links.new(fog.outputs['Result'], go.inputs[0])
    print('COMPOSITOR 辉光 + 空气透视已接上')
except Exception as e: print('COMPOSITOR 跳过：', e)
set_fmt('PNG'); sc.render.use_overwrite = False; sc.render.use_placeholder = True

# ---------- 每帧锚点（给 2D 合成） ----------
anchors = {}
for f in range(1, NF + 1):
    sc.frame_set(f); fr = {}
    for k, p in (('focus', FOCUS), ('module', Vector((0, MOD_FRONT + 20000, SHELL_Z))), ('chip', Vector((0, 0, 0)))):
        v = world_to_camera_view(sc, cam, WORLD.matrix_world @ p); fr[k] = [round(v.x * W, 1), round((1 - v.y) * H, 1)]
    fr['view_um'] = round(view_w((f - 1) / FPS), 3); anchors[f] = fr
json.dump({'fps': FPS, 'nf': NF, 'w': W, 'frames': anchors}, open(os.path.join(OUT, 'anchors.json'), 'w'))
if VIDEO and not FRAMES:                              # PNG 序列：中途停了可以续渲
    sc.render.filepath = os.path.join(OUT, 'frames', 'f'); bpy.ops.render.render(animation=True)
else:
    sc.render.use_overwrite = True
    for i, f in enumerate(FRAMES or range(1, NF + 1)):
        sc.frame_set(f); sc.render.filepath = os.path.join(OUT, f'f{f:04d}.png'); t0 = time.time(); bpy.ops.render.render(write_still=True)
        print(f'FRAME_TIME 第 {f} 帧：{time.time() - t0:.1f} 秒')
        if i == 0:
            try: import gpu; print('EEVEE_GPU', gpu.platform.vendor_get(), '|', gpu.platform.renderer_get())
            except Exception as e: print('EEVEE_GPU 未知', e)
print('DONE', OUT)
