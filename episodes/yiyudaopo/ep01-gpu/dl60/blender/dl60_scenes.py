# 一语道破 EP01 DIRECTOR-LOCKED 60s —— 开头（SHOT 01）和结尾（SHOT 06）两个写实镜头。
# 同一块加速器模组（复用 ../../blender/ep01_scenes.py 的 build_module：中间大芯片 + 两侧各 3 颗 HBM，
# 硅中介层 + 有机基板 + 模组板），同一支 50 mm 镜头，所以首尾是「同一个东西」。
#
#   OPEN   片子 0.0–5.5 秒（166 帧）：3/4 俯角慢推（芯片在屏幕上放大约 13%）→ 3.5 秒起稳住、开始抬向正面
#          → 4.3 秒起推向芯片方框，5.3 秒时芯片宽约 960 px、仰角约 74°（Remotion 在芯片方框里长出游戏视口）
#   CLOSE  片子 48.5–60.0 秒（345 帧）：正上方俯视、下降推进，接住 2D 的「芯片轮廓」（屏幕上芯片宽度 W(t)
#          与 Remotion 共用同一条曲线，见 die_width_px）→ 51–54 秒几乎不动（叠加层在上面算）
#          → 54–57 秒稍微拉远并倾斜 9° → 57–60 秒定在结尾构图
#
# 用法（blender -b --python-exit-code 1 --python dl60_scenes.py -- 参数）：
#   still   <镜头> <片子秒数> <输出.png> [宽x高] [采样]
#   anim    <镜头> <输出目录> [宽x高] [采样] [步长] [cpu|gpu|cuda] [起始帧] [结束帧]   逐帧 PNG，文件名用片子帧号
#   anchors <镜头> <输出.json>                              逐帧投影：芯片四角、6 颗 HBM 四角、基板四角（1080×1920 像素）
import bpy, math, os, sys, json, importlib.util
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
_src = os.path.join(HERE, 'ep01_scenes.py')            # RunPod 打包时把它复制到同目录
if not os.path.exists(_src): _src = os.path.join(HERE, '..', '..', 'blender', 'ep01_scenes.py')
spec = importlib.util.spec_from_file_location('ep01', _src)
E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)

FPS = 30
W_PX, H_PX = 1080, 1920
LENS = 50.0                       # 两个镜头同一支镜头
TAN = 18.0 / LENS                 # 36 mm 传感器宽 → tan(水平半视场)
SHOT = {'OPEN': (0, 165), 'CLOSE': (1455, 1799)}     # 片子帧号（含）
DIE_Y_PX = 1010                   # CLOSE：芯片中心在屏幕上的高度（上面留给结尾的字）

# ------------------------------------------------------------------ 工具
def pchip(xs, ys):
    """单调三次 Hermite 插值（不过冲），两端外推为常数。"""
    n = len(xs); h = [xs[i + 1] - xs[i] for i in range(n - 1)]; d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] <= 0: m[i] = 0.0
        else:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    def f(x):
        if x <= xs[0]: return ys[0]
        if x >= xs[-1]: return ys[-1]
        i = max(k for k in range(n - 1) if xs[k] <= x)
        t = (x - xs[i]) / h[i]; t2, t3 = t * t, t * t * t
        return ((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h[i] * m[i] + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h[i] * m[i + 1])
    return f

def place(cam, pos, tgt, up=(0, 1, 0)):
    """相机放在 pos 看向 tgt；屏幕「上」尽量对齐 up（俯视时也稳定）。"""
    fwd = (Vector(tgt) - Vector(pos)).normalized()
    right = fwd.cross(Vector(up)).normalized()
    upv = right.cross(fwd)
    M = Matrix((right, upv, -fwd)).transposed()
    cam.matrix_world = Matrix.Translation(Vector(pos)) @ M.to_4x4()

def orbit(tgt, d, el, az):
    el, az = math.radians(el), math.radians(az)
    return Vector(tgt) + d * Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))

# ------------------------------------------------------------------ 场景：同一块模组，调过材质和光（表面不出白斑）
def build_common():
    sc = E.reset()
    E.world((0.016, 0.018, 0.022), 1.0)
    die, ztop = E.build_module(sc, detail=True, env=True)
    # 去掉旁边那块散热鳍片（低清下像一块灰盒子，抢画面）
    for o in list(bpy.data.objects):
        if o.name.startswith('鳍'): bpy.data.objects.remove(o, do_unlink=True)
    # 材质：芯片背面粗一点（不出镜面白斑）、HBM 略暗，和芯片分得开
    def setp(mname, **kw):
        b = bpy.data.materials[mname].node_tree.nodes['Principled BSDF']
        for k, v in kw.items(): b.inputs[k].default_value = v
        if 'Roughness' in kw:      # mat() 里有噪声时，粗糙度由 MapRange 节点给（rough ± noise），一起改
            for n in bpy.data.materials[mname].node_tree.nodes:
                if n.type == 'MAP_RANGE':
                    r = kw['Roughness']; n.inputs['To Min'].default_value = r - 0.05; n.inputs['To Max'].default_value = r + 0.05
    setp('芯片硅背面', **{'Base Color': (0.34, 0.35, 0.38, 1), 'Metallic': 0.5, 'Roughness': 0.52})
    setp('HBM 顶面', **{'Base Color': (0.20, 0.205, 0.22, 1), 'Metallic': 0.4, 'Roughness': 0.55})
    setp('硅中介层', **{'Roughness': 0.36})
    setp('机箱底板', **{'Base Color': (0.035, 0.037, 0.04, 1), 'Roughness': 0.62})
    return sc, ztop

def lights_open():
    E.area_light('主光', (-140, -40, 190), (math.radians(30), math.radians(-34), 0), 420, 5.5e5, (1.0, 0.97, 0.93))
    E.area_light('勾边', (120, 150, 70), (math.radians(-62), math.radians(38), 0), 180, 2.6e5, (0.78, 0.86, 1.0), 'RECTANGLE', 24)
    E.area_light('补光', (0, -230, 60), (math.radians(78), 0, 0), 240, 3.0e4, (0.9, 0.93, 1.0))

def lights_close():
    # 俯视时相机看到的是芯片表面反射的「正上方」：放一块大而柔的顶光，偏一点，反射成平缓的渐变
    E.area_light('顶柔光', (-60, 70, 260), (math.radians(-14), math.radians(-12), 0), 520, 7.0e5, (1.0, 0.97, 0.93))
    E.area_light('勾边', (120, 150, 70), (math.radians(-62), math.radians(38), 0), 180, 2.2e5, (0.78, 0.86, 1.0), 'RECTANGLE', 24)
    E.area_light('补光', (-260, -160, 40), (math.radians(80), 0, math.radians(-60)), 300, 2.0e4, (0.9, 0.93, 1.0))

# ------------------------------------------------------------------ 镜头路径（输入：片子秒数）
def open_path(ztop):
    K = [0.0, 3.5, 4.25, 5.3, 5.5]
    logd = pchip(K, [math.log(150), math.log(133), math.log(127), math.log(42.5), math.log(41.5)])
    el = pchip(K, [37, 39, 46, 74, 75])
    az = pchip(K, [-104, -101, -97, -90.5, -90])
    ty = pchip(K, [7.0, 6.0, 3.5, 0.0, 0.0])
    def f(t):
        tgt = (0.0, ty(t), ztop)
        return orbit(tgt, math.exp(logd(t)), el(t), az(t)), tgt, (0, 0, 1)
    return f

# CLOSE：屏幕上芯片宽度（像素）随片子秒数变化。Remotion 的 2D 段在 45–48.5 秒用同一条曲线接进来（见 src60/lib/world.ts）
DIEW_K = [45.0, 48.5, 51.0, 52.2, 54.0, 57.0, 60.0]
DIEW_V = [250.0, 430.0, 610.0, 628.0, 640.0, 440.0, 425.0]
die_width_px = pchip(DIEW_K, [math.log(v) for v in DIEW_V])

def close_path(ztop):
    K = [48.5, 54.0, 57.0, 60.0]
    el = pchip(K, [90.0, 90.0, 81.0, 80.6])
    az = pchip(K, [-90.0, -90.0, -96.0, -96.5])
    def f(t):
        W = math.exp(die_width_px(t))
        d = W_PX * E.DIE[0] / (2 * TAN * W)                    # 距离 → 屏幕上芯片宽 W 像素
        # 芯片中心落在屏幕 y = DIE_Y_PX：俯视时把看点往 +y（屏幕上方）挪
        off = (DIE_Y_PX - H_PX / 2) / W_PX * (2 * TAN * d)
        tgt = (0.0, off, ztop)
        e = el(t)
        if e >= 89.999:
            pos = (0.0, off, ztop + d)
        else:
            pos = orbit(tgt, d, e, az(t))
        return Vector(pos), tgt, (0, 1, 0)
    return f

def build(shot):
    sc, ztop = build_common()
    (lights_open if shot == 'OPEN' else lights_close)()
    cam = E.camera(LENS)
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 4.0 if shot == 'OPEN' else 5.6
    cam.data.clip_start = 1.0; cam.data.clip_end = 3000
    path = (open_path if shot == 'OPEN' else close_path)(ztop)
    return sc, cam, path, ztop

def pose(cam, path, t, ztop):
    pos, tgt, up = path(t)
    place(cam, pos, tgt, up)
    cam.data.dof.focus_distance = (Vector(pos) - Vector((0, 0, ztop))).length

def setup(sc, w, h, smp):
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.cycles.samples = smp; sc.cycles.use_adaptive_sampling = True
    sc.cycles.max_bounces = 6
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'

def proj(sc, cam, p):
    from bpy_extras.object_utils import world_to_camera_view
    v = world_to_camera_view(sc, cam, Vector(p)); return [round(v.x * W_PX, 2), round((1 - v.y) * H_PX, 2)]

def quad(cx, cy, sx, sy, z):    # 左上、右上、右下、左下（屏幕方向：+y 在上）
    return [(cx - sx / 2, cy + sy / 2, z), (cx + sx / 2, cy + sy / 2, z), (cx + sx / 2, cy - sy / 2, z), (cx - sx / 2, cy - sy / 2, z)]

def main():
    a = sys.argv[sys.argv.index('--') + 1:]
    mode, shot = a[0], a[1]
    sc, cam, path, ztop = build(shot)
    f0, f1 = SHOT[shot]
    if mode == 'still':
        t, out = float(a[2]), a[3]
        w, h = map(int, (a[4] if len(a) > 4 else '270x480').split('x')); smp = int(a[5]) if len(a) > 5 else 16
        setup(sc, w, h, smp); pose(cam, path, t, ztop)
        sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    elif mode == 'anim':
        out = a[2]; w, h = map(int, (a[3] if len(a) > 3 else '540x960').split('x'))
        smp = int(a[4]) if len(a) > 4 else 16; step = int(a[5]) if len(a) > 5 else 1
        dev = a[6] if len(a) > 6 else 'cpu'
        if len(a) > 8: f0, f1 = int(a[7]), int(a[8])
        setup(sc, w, h, smp); os.makedirs(out, exist_ok=True)
        if dev != 'cpu': E.setup_render(sc, w, h, smp, dev); sc.cycles.use_adaptive_sampling = True; sc.cycles.max_bounces = 6
        frames = list(range(f0, f1 + 1, step))
        if frames[-1] != f1: frames.append(f1)
        for f in frames:
            p = os.path.join(out, f'{shot}_{f:04d}.png')
            if os.path.exists(p): continue
            pose(cam, path, f / FPS, ztop); sc.render.filepath = p; bpy.ops.render.render(write_still=True)
    elif mode == 'anchors':
        out = a[2]; sc.render.resolution_x, sc.render.resolution_y = W_PX, H_PX
        fr = []
        for f in range(f0, f1 + 1):
            pose(cam, path, f / FPS, ztop); bpy.context.view_layer.update()
            fr.append(dict(f=f,
                           die=[proj(sc, cam, p) for p in quad(0, 0, E.DIE[0], E.DIE[1], ztop)],
                           hbm=[[proj(sc, cam, p) for p in quad(x, y, E.HBM[0], E.HBM[1], ztop - 0.04)] for x, y in E.hbm_centers()],
                           subs=[proj(sc, cam, p) for p in quad(0, 0, E.SUBS[0], E.SUBS[1], E.Z_SUB)]))
        json.dump(dict(shot=shot, fps=FPS, w=W_PX, h=H_PX, f0=f0, f1=f1, frames=fr), open(out, 'w'))

main()
