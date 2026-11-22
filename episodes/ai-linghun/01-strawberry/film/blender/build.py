# build.py — EP.01 film in Blender: import the three.js scene (scene.glb), swap in real materials and lights, key every frame
# from anim.json (exported by ../render.mjs --export), render with Cycles.
#
#   blender -b --python build.py -- <out_dir> <frame_start> <frame_end> <samples> <cycles|eevee> <gpu|cpu> [res_scale]
#
# Frame numbers are the film's global frame numbers (t * 30). Output: <out_dir>/<frame:05d>.png
# Coordinates: three.js is Y-up, Blender Z-up. The glTF importer converts geometry and node frames by C (x, y, z) -> (x, -z, y),
# so a three.js world matrix Mt becomes C @ Mt @ C^-1 for imported objects, and C @ Mt for the camera (same local convention).
import bpy, json, math, os, sys
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = argv[0] if len(argv) > 0 else os.path.join(HERE, "out", "test")
FS = int(argv[1]) if len(argv) > 1 else 640
FE = int(argv[2]) if len(argv) > 2 else FS
SAMPLES = int(argv[3]) if len(argv) > 3 else 64
ENGINE = argv[4] if len(argv) > 4 else "cycles"
DEVICE = argv[5] if len(argv) > 5 else "gpu"
SCALE = float(argv[6]) if len(argv) > 6 else 1.0

DATA = argv[7] if len(argv) > 7 else HERE           # a still's folder (render.mjs --export-stills) or the whole-film export next to this script
A = json.load(open(os.path.join(DATA, "anim.json")))
FR = {A["f0"] + i: fr for i, fr in enumerate(A["frames"])}
C = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
CI = C.inverted()
def m4(e):  # three.js column-major elements -> mathutils Matrix
    return Matrix(((e[0], e[4], e[8], e[12]), (e[1], e[5], e[9], e[13]), (e[2], e[6], e[10], e[14]), (e[3], e[7], e[11], e[15])))
def lin(h):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in c) + (1.0,)
def v3(x, y, z): return Vector((x, -z, y))           # a three.js point in Blender coordinates

# ---------- scene ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=os.path.join(DATA, "scene.glb"))
scn = bpy.context.scene
for o in list(bpy.data.objects):
    if o.type in ("LIGHT", "CAMERA"): bpy.data.objects.remove(o, do_unlink=True)

# ---------- materials (by the names set in index.html) ----------
def base(name): return name.split(".")[0]
def fresh(mat):
    mat.use_nodes = True; nt = mat.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); return nt, out
def imported_color(mat):
    """the colour three.js had on this material at export time (glTF base colour factor), or None"""
    if not (mat.use_nodes and mat.node_tree): return None
    for nd in mat.node_tree.nodes:
        if nd.type == "BSDF_PRINCIPLED" and not nd.inputs["Base Color"].is_linked: return tuple(nd.inputs["Base Color"].default_value)
    return None
KEEP_COLOR = os.environ.get("KEPU_KEEP_COLOR", "1") == "1"
def principled(mat, col, rough, **kw):
    ic = imported_color(mat) if KEEP_COLOR else None
    nt, out = fresh(mat); b = nt.nodes.new("ShaderNodeBsdfPrincipled"); nt.links.new(b.outputs[0], out.inputs[0])
    b.inputs["Base Color"].default_value = ic if ic and mat.get("keep_color", True) else lin(col); b.inputs["Roughness"].default_value = rough
    for k, v in kw.items():
        if k in b.inputs: b.inputs[k].default_value = v
    return b
def emission(mat, col, strength, with_alpha=False):
    nt, out = fresh(mat); e = nt.nodes.new("ShaderNodeEmission"); e.inputs["Color"].default_value = lin(col); e.inputs["Strength"].default_value = strength
    if not with_alpha: nt.links.new(e.outputs[0], out.inputs[0]); return e, None
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(e.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0]); return e, mx
MAT = {}
for mat in bpy.data.materials:
    n = base(mat.name)
    if n == "table":
        b = principled(mat, "#DCCDB4", 0.82)
        nt = mat.node_tree; nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 60.0; bm = nt.nodes.new("ShaderNodeBump"); bm.inputs["Strength"].default_value = 0.04
        nt.links.new(nz.outputs["Fac"], bm.inputs["Height"]); nt.links.new(bm.outputs["Normal"], b.inputs["Normal"])
    elif n in ("cream", "cream2") or n.startswith("cream_"):
        b = principled(mat, "#E2D8C6" if n == "cream2" else "#EEE6D8", 0.5, **{"Subsurface Weight": 0.06, "Coat Weight": 0.15, "Coat Roughness": 0.35})
        b.inputs["Emission Color"].default_value = lin("#FFE2BE"); b.inputs["Emission Strength"].default_value = 0.0; MAT[n] = b
    elif n == "coal": principled(mat, "#2B2726", 0.45, **{"Coat Weight": 0.25, "Coat Roughness": 0.3})
    elif n == "alu": principled(mat, "#C9CBCE", 0.3, Metallic=1.0, Anisotropic=0.7)
    elif n == "coral": principled(mat, "#EE6A47", 0.42, **{"Coat Weight": 0.15})
    elif n == "glass": principled(mat, "#F4F1EA", 0.3, **{"Transmission Weight": 1.0, "IOR": 1.5})
    elif n == "pipeglass": principled(mat, "#F6E1BC", 0.12, **{"Transmission Weight": 0.8, "IOR": 1.45}); mat["keep_color"] = False   # stills v2: warm, like three.js (was clear -> read white)
    elif n == "rubber": principled(mat, "#1C1A19", 0.42)
    elif n == "screw": principled(mat, "#8E9196", 0.35, Metallic=1.0)
    elif n == "pipecore": MAT[n] = emission(mat, "#FFB45A", 3.0)[0]
    elif n.startswith("pulse_"): MAT[n] = emission(mat, "#FFE2B8", 25.0)[0]
    elif n.startswith("blade_"): MAT[n] = emission(mat, "#FFE6C4", 30.0, with_alpha=True)
    elif n in ("scan", "scanH"): MAT[n] = emission(mat, "#FFE3BC", 10.0, with_alpha=True)
    elif n == "screen":     # the phone screen is unlit in three.js (MeshBasic): show its texture as emission, not as a lit grey surface
        tex = next((nd for nd in mat.node_tree.nodes if nd.type == "TEX_IMAGE"), None) if mat.use_nodes else None
        if tex and tex.image:
            img = tex.image; nt, out = fresh(mat); ti = nt.nodes.new("ShaderNodeTexImage"); ti.image = img; e = nt.nodes.new("ShaderNodeEmission")
            e.inputs["Strength"].default_value = 1.0; nt.links.new(ti.outputs["Color"], e.inputs["Color"]); nt.links.new(e.outputs[0], out.inputs[0])
    # decal_*, disp_*: keep the imported (textured) setups

# ---------- lights / world ----------
def add_light(name, kind, energy, col, loc, **kw):
    d = bpy.data.lights.new(name, kind); d.energy = energy; d.color = lin(col)[:3]
    for k, v in kw.items(): setattr(d, k, v)
    o = bpy.data.objects.new(name, d); scn.collection.objects.link(o); o.location = loc; return o
sun = add_light("sun", "SUN", 4.2, "#FFD3A0", v3(-13, 6.2, -9), angle=math.radians(4.0))
sun.rotation_euler = (-sun.location).to_track_quat("-Z", "Y").to_euler()
box = add_light("softbox", "AREA", 260.0, "#FFF4E8", v3(1.0, 13.0, 3.0), size=9.0)
box.rotation_euler = (v3(0, 0, -1) - box.location).to_track_quat("-Z", "Y").to_euler()
cutL = add_light("cutL", "POINT", 0.0, "#FFC890", v3(-0.6, 0.49 + 0.28 + 0.4, -3.1 + 0.6), shadow_soft_size=0.15)
w = bpy.data.worlds.new("world"); scn.world = w; w.use_nodes = True; nt = w.node_tree; nt.nodes.clear()
wo = nt.nodes.new("ShaderNodeOutputWorld"); lp = nt.nodes.new("ShaderNodeLightPath"); bgc = nt.nodes.new("ShaderNodeBackground"); bga = nt.nodes.new("ShaderNodeBackground"); mx = nt.nodes.new("ShaderNodeMixShader")
bgc.inputs["Color"].default_value = lin("#5E4F3E"); bga.inputs["Color"].default_value = lin("#F2E6D2"); bga.inputs["Strength"].default_value = 1.0   # stills v2: brighter room for reflections (alu read near-black at 0.35)
nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0]); nt.links.new(bga.outputs[0], mx.inputs[1]); nt.links.new(bgc.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], wo.inputs[0])

# ---------- camera ----------
cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); scn.collection.objects.link(cam); scn.camera = cam
f0 = A["frames"][0]
cd.sensor_fit = "VERTICAL"; cd.angle_y = math.radians(f0["fov"]); cd.clip_start = 0.1; cd.clip_end = 300
cd.shift_y = -f0["offy"] / A["H"]                     # three.js setViewOffset(0, OFFY): the picture moves up by OFFY px
cd.dof.use_dof = True; cd.dof.aperture_fstop = 2.2

# ---------- keys ----------
objs = {n: bpy.data.objects.get(n) for n in f0["nodes"]}
missing = [n for n, o in objs.items() if o is None]
if missing: print("missing objects:", missing)
def tree(o): return [o] + list(o.children_recursive)
def key_mat(node, path_owner, path, value, frame):
    setattr(path_owner, path, value) if not hasattr(path_owner, "default_value") else None
for fnum in range(FS, FE + 1):
    fr = FR.get(fnum)
    if fr is None: continue
    for n, o in objs.items():
        if o is None: continue
        v, e = fr["nodes"][n][0], fr["nodes"][n][1:]
        o.rotation_mode = "QUATERNION"; o.matrix_world = C @ m4(e) @ CI
        for p in ("location", "rotation_quaternion", "scale"): o.keyframe_insert(p, frame=fnum)
        for q in tree(o): q.hide_render = not v; q.keyframe_insert("hide_render", frame=fnum)
    cam.rotation_mode = "QUATERNION"; cam.matrix_world = C @ m4(fr["cam"])
    for p in ("location", "rotation_quaternion"): cam.keyframe_insert(p, frame=fnum)
    cd.dof.focus_distance = fr["focus"]; cd.dof.keyframe_insert("focus_distance", frame=fnum)
    for j, op in enumerate(fr["blades"]):
        e_mx = MAT.get(f"blade_{j}")
        if e_mx: e_mx[1].inputs[0].default_value = op; e_mx[1].inputs[0].keyframe_insert("default_value", frame=fnum)
    if "pipecore" in MAT: MAT["pipecore"].inputs["Strength"].default_value = 6.0 * fr["pipe"]; MAT["pipecore"].inputs["Strength"].keyframe_insert("default_value", frame=fnum)
    for g, fl in enumerate(fr["flash"]):
        b = MAT.get("cream_merged" if g == 3 else f"cream_block_{g}")
        if b: b.inputs["Emission Strength"].default_value = 2.5 * fl; b.inputs["Emission Strength"].keyframe_insert("default_value", frame=fnum)
    for nm in ("scan", "scanH"):
        e_mx = MAT.get(nm)
        if e_mx: e_mx[1].inputs[0].default_value = float(fr["nodes"][nm][0]) * (0.95 if nm == "scan" else 0.5); e_mx[1].inputs[0].keyframe_insert("default_value", frame=fnum)
    cutL.data.energy = 40.0 * fr["cutL"]; cutL.data.keyframe_insert("energy", frame=fnum)
# linear between per-frame keys (no overshoot for motion blur); visibility steps
for ad in [o.animation_data for o in bpy.data.objects if o.animation_data] + [m.node_tree.animation_data for m in bpy.data.materials if m.node_tree and m.node_tree.animation_data] + [cd.animation_data, cutL.data.animation_data]:
    if not ad or not ad.action: continue
    fcs = ad.action.fcurves if hasattr(ad.action, "fcurves") else [fc for layer in ad.action.layers for strip in layer.strips for cb in strip.channelbags for fc in cb.fcurves]
    for fc in fcs:
        for kp in fc.keyframe_points: kp.interpolation = "CONSTANT" if fc.data_path.endswith("hide_render") else "LINEAR"

# ---------- render settings ----------
r = scn.render; r.resolution_x = int(A["W"] * SCALE); r.resolution_y = int(A["H"] * SCALE); r.resolution_percentage = 100; r.fps = A["fps"]
r.image_settings.file_format = "PNG"; r.image_settings.color_mode = "RGB"; r.film_transparent = False
scn.view_settings.view_transform = "AgX"; scn.view_settings.look = "AgX - Base Contrast" if "AgX - Base Contrast" in [i.identifier for i in scn.view_settings.bl_rna.properties["look"].enum_items] else "None"
scn.view_settings.exposure = 0.0
if ENGINE == "cycles":
    r.engine = "CYCLES"; cy = scn.cycles; cy.samples = SAMPLES; cy.use_adaptive_sampling = True; cy.use_denoising = True
    try: cy.denoiser = "OPENIMAGEDENOISE"
    except Exception: pass
    cy.max_bounces = 8; cy.transmission_bounces = 8; cy.glossy_bounces = 4; cy.caustics_reflective = False; cy.caustics_refractive = False; cy.blur_glossy = 1.0
    r.use_motion_blur = True; r.motion_blur_shutter = 0.4
    if DEVICE == "gpu":
        pr = bpy.context.preferences.addons["cycles"].preferences
        for dt in ("OPTIX", "CUDA") if os.environ.get("KEPU_GPU") == "OPTIX" else ("CUDA",):
            try: pr.compute_device_type = dt; pr.get_devices(); break
            except Exception: continue
        for d in pr.devices: d.use = d.type != "CPU"
        cy.device = "GPU"
    else: cy.device = "CPU"
else:
    r.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in r.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    ee = scn.eevee; ee.taa_render_samples = SAMPLES
    for k, v in (("use_raytracing", True), ("use_shadows", True)):
        if hasattr(ee, k): setattr(ee, k, v)
os.makedirs(OUT, exist_ok=True)
for fnum in range(FS, FE + 1):
    scn.frame_set(fnum); r.filepath = os.path.join(OUT, f"{fnum:05d}.png"); bpy.ops.render.render(write_still=True)
    print("rendered", fnum, flush=True)
