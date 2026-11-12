# T5 结尾「对面服务器亮起」2.5 秒（75 帧，30 fps）。同一个机房：一条青色的消息沿跳线 / 线槽从过桥走到 B 排，B 排 GPU B 那台服务器的标记亮起。
# 画面：通道里的中景，上半是过桥和 B 排线槽（消息走过），下半是 B 排机柜上的标记。中间偏上留空给合成的八格和 ✓。
# 运行：blender -b --python-exit-code 1 --python t5_arrive.py -- <输出目录> --res 540x960 --samples N [--gpu] [--threads 2] [--times 0.5,2.0] [--frames a-b]
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t5_s1_scene as S
import bpy
from mathutils import Vector
import common as C
V = Vector; PI = math.pi; rad = math.radians

DUR = 2.5
env = S.build_scene('T5ARR', DUR, hero_b=True); shot = env['shot']; args = env['args']; ns = env['ns']
G_A = ns['G_A']; G_B = ns['G_B']; to_world = ns['to_world']; I_A = ns['I_A']; I_B = ns['I_B']
fillet = ns['fillet']; hero_route = ns['hero_route']; X_CROSS = ns['X_CROSS']

# ---------- B 主机柜：像 shot1 里的 A 一样，门、上方设备、上盖永久隐藏，去掉后板（补丁在 t5_s1_scene.build_scene） ----------
FDB = ns['FDB']; heroB = bpy.data.objects['机柜B']
for o in FDB['door'] + FDB['upper'] + FDB['lid']: o.hide_render = True; o.hide_viewport = True
FDB['light'].energy = 0.0
for o in bpy.data.objects:
    if o.parent == heroB and 'p0stub' in o.name: o.hide_render = True; o.hide_viewport = True
mod = S.optical_module(ns, 'B', idx=I_B)
SD = ns['SD']; PORT_Z = ns['PORT_Z']; LANE_X = ns['LANE_X']; srv_to_rack = ns['srv_to_rack']

# ---------- 青色消息的路径：A 线槽 → 过桥 → B 线槽 → B 机柜背面下去 → 进光模块 ----------
ra = [to_world('A', I_A, p) for p in hero_route()]; rb = [to_world('B', I_B, p) for p in reversed(hero_route())]
zt = ra[-1].z; ya = ra[-1].y; yb = rb[0].y; xk = X_CROSS - 0.10
tray_run = fillet([ra[-1], (xk, ya, zt), (xk, yb, zt), rb[0]], 0.06, n=6)
route = [V(p) for p in tray_run + rb[1:]] + [mod['W']((LANE_X, SD + 0.0275, PORT_Z + 0.0004))]
cell = 0.12
msg = S.message_material('msg_cyan', (0.02, 0.85, 1.0), strength=9.0, cell=cell, head=True)
dd = [0.0]
for a_, b_ in zip(route, route[1:]): dd.append(dd[-1] + (b_ - a_).length)
rad_ = [C.lerp(0.0016, 0.0125, C.smooth(C.seg(dd[-1] - d, 0.01, 0.16))) for d in dd]
tube = S.sweep_tube('消息串_青', route, rad_, msg, sides=10)
L_TOT = tube['arc_len']
print('STREAM 长度', round(L_TOT, 2), 'm | 起点', tuple(round(v, 2) for v in route[0]), '| 终点', tuple(round(v, 2) for v in route[-1]))
SPEED = 8.0 * cell
S.key_sock(msg.node_tree.nodes['msg_offset'].outputs[0], [(0.0, 0.0), (DUR, SPEED / cell * DUR)])
HEAD_T = 1.35
S.key_sock(msg.node_tree.nodes['msg_head'].outputs[0], [(0.0, 4.6), (HEAD_T, L_TOT + 0.1), (DUR, L_TOT + 0.1)])

# ---------- B 服务器里亮起（青色柔光从机箱里透出来）；B 标记（前面板的亮带）也同步亮起 ----------
T_ARR = HEAD_T + 0.05
mk = S.b_marker(ns, strength=6.0)
S.key_sock(mk['e1'].inputs['Strength'], [(0.0, 1.0), (T_ARR, 1.0), (T_ARR + 0.2, 40.0), (T_ARR + 0.8, 22.0), (DUR, 22.0)])
S.key_energy(mk['light'], [(0.0, 60.0), (T_ARR, 60.0), (T_ARR + 0.2, 1200.0), (T_ARR + 0.8, 900.0), (DUR, 900.0)])
GB = G_B
gl = C.area_light('B服务器亮起', GB + V((0.0, 0.0, 0.30)), GB, 0.45, 0.0, (0.20, 0.90, 1.0), size_y=0.45, col=C.collection('B亮起'))
gl.visible_camera = False
S.key_energy(gl.data, [(0.0, 0.0), (T_ARR, 0.0), (T_ARR + 0.25, 20.0), (T_ARR + 0.8, 11.0), (DUR, 11.0)])

# ---------- 灯光 ----------
C.world(ns['FOG'], 1.0, hdri='studio_small_09_2k.hdr', hdri_strength=0.14, hdri_rot=rad(90))
lights = C.collection('灯光')
def no_cam(o): o.visible_camera = False; return o
for x in ns['LIGHT_X'][::2]:
    no_cam(C.area_light(f'顶灯{x:.1f}', (x, 0, 2.74), (x, 0, 0), 0.9, 42.0, (0.30, 0.55, 1.0), size_y=0.25, col=lights))
no_cam(C.area_light('逆光', (ns['X1'] - 0.4, 0, 2.55), (ns['X1'] - 4.5, 0, 0.6), 1.4, 120, (0.30, 0.55, 1.0), size_y=0.6, col=lights))
no_cam(C.area_light('后走道补光', (5.0, -3.6, 2.7), (5.2, -1.6, 1.0), 2.2, 260, (0.55, 0.75, 1.0), col=lights))
no_cam(C.area_light('后走道侧补光', (7.2, -2.6, 2.2), (5.2, -1.6, 1.0), 1.2, 90, (1.0, 0.85, 0.7), col=lights))
S.add_fog_all(ns)

# ---------- 相机 ----------
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 't5_arrive_cam.py'), encoding='utf-8').read())
cam, tgt = C.add_camera('cam_T5ARR', lens=30, fstop=2.0, clip=(0.01, 200))
C.animate_camera(cam, tgt, cam_fn, shot)

if args.anchors:
    S.write_anchors(shot, cam, {'gpu_b': G_B, 'module_b': mod['W']((LANE_X, SD + 0.02, PORT_Z))}, args.out)
    sys.exit(0)

dev = S.setup_render(args, exposure=0.0)
S.setup_glare(size=7, strength=3.0)
print('G_B', tuple(round(v, 3) for v in G_B))
C.render(args, shot, dev)
