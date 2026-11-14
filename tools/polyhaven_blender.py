"""在 Blender 脚本里使用 tools/polyhaven.py 下载的素材。

用法（在 Blender 的 Python 脚本里）：
    import sys; sys.path.insert(0, '<仓库>/tools')
    import polyhaven_blender as ph
    mat = ph.pbr_material('metal_plate', res='2k')              # 按真实尺寸铺贴图（用物体坐标，单位米）
    ph.set_world_hdri('studio_small_09', res='2k', strength=0.3, rotation_deg=140, camera_sees=(0.004, 0.005, 0.007))
    objs = ph.import_model('<模型id>', res='1k')

素材必须先用 tools/polyhaven.py get 下载好；这里不联网。
"""
import json
import math
import os

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'assets', 'polyhaven')


def _dir(kind, aid, res):
    d = os.path.join(CACHE, kind, aid, res)
    if not os.path.exists(os.path.join(d, 'manifest.json')):
        raise FileNotFoundError(f'没有下载：python3 tools/polyhaven.py get {aid} --res {res}')
    return d, json.load(open(os.path.join(d, 'manifest.json')))


def pbr_material(aid, res='2k', name=None, real_size_m=None, disp_strength=0.0):
    """建 Principled BSDF 材质。贴图按物体坐标平铺：real_size_m 默认取素材标注的真实尺寸。"""
    d, man = _dir('textures', aid, res)
    f = man['files']
    m = bpy.data.materials.new(name or f'PH_{aid}')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    if real_size_m is None:
        dims = man.get('dimensions_mm') or [1000, 1000]
        real_size_m = dims[0] / 1000.0
    mp.inputs['Scale'].default_value = (1 / real_size_m, 1 / real_size_m, 1 / real_size_m)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])

    def img(key, colorspace):
        if key not in f:
            return None
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(os.path.join(d, f[key]), check_existing=True)
        t.image.colorspace_settings.name = colorspace
        t.projection = 'BOX'
        t.projection_blend = 0.2
        nt.links.new(mp.outputs['Vector'], t.inputs['Vector'])
        return t

    if (t := img('Diffuse', 'sRGB')):
        nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    if (t := img('Rough', 'Non-Color')):
        nt.links.new(t.outputs['Color'], b.inputs['Roughness'])
    if (t := img('Metal', 'Non-Color')):
        nt.links.new(t.outputs['Color'], b.inputs['Metallic'])
    if (t := img('nor_gl', 'Non-Color')):
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nt.links.new(t.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    if disp_strength and (t := img('Displacement', 'Non-Color')):
        dn = nt.nodes.new('ShaderNodeDisplacement')
        dn.inputs['Scale'].default_value = disp_strength
        nt.links.new(t.outputs['Color'], dn.inputs['Height'])
        nt.links.new(dn.outputs['Displacement'], nt.nodes['Material Output'].inputs['Displacement'])
    return m


def set_world_hdri(aid, res='2k', strength=1.0, rotation_deg=0.0, camera_sees=None):
    """HDRI 做环境光和反射。camera_sees=(r,g,b) 时，镜头直接看到的背景换成这个颜色（只要反射，不要背景）。"""
    d, man = _dir('hdris', aid, res)
    sc = bpy.context.scene
    w = sc.world or bpy.data.worlds.new('World')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_WORLD':
            nt.nodes.remove(n)
    out = nt.nodes['World Output']
    env = nt.nodes.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(os.path.join(d, man['files']['hdri']), check_existing=True)
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0, 0, math.radians(rotation_deg))
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Strength'].default_value = strength
    nt.links.new(env.outputs['Color'], bg.inputs['Color'])
    if camera_sees is None:
        nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
        return w
    dark = nt.nodes.new('ShaderNodeBackground')
    dark.inputs['Color'].default_value = (*camera_sees, 1)
    lp = nt.nodes.new('ShaderNodeLightPath')
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs['Fac'])
    nt.links.new(bg.outputs['Background'], mix.inputs[1])
    nt.links.new(dark.outputs['Background'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    return w


def import_model(aid, res='1k'):
    """导入 gltf / blend 模型，返回新增的物体列表。"""
    d, man = _dir('models', aid, res)
    path = os.path.join(d, man['files']['model'])
    before = set(bpy.data.objects)
    if path.endswith(('.gltf', '.glb')):
        bpy.ops.import_scene.gltf(filepath=path)
    elif path.endswith('.blend'):
        with bpy.data.libraries.load(path, link=False) as (src, dst):
            dst.objects = src.objects
        for o in dst.objects:
            if o is not None:
                bpy.context.scene.collection.objects.link(o)
    elif path.endswith('.fbx'):
        bpy.ops.import_scene.fbx(filepath=path)
    return [o for o in bpy.data.objects if o not in before]
