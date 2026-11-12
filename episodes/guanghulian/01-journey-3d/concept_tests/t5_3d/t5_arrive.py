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
env = S.build_scene('T5ARR', DUR); shot = env['shot']; args = env['args']; ns = env['ns']
G_A = ns['G_A']; G_B = ns['G_B']; to_world = ns['to_world']; I_A = ns['I_A']; I_B = ns['I_B']
fillet = ns['fillet']; hero_route = ns['hero_route']; X_CROSS = ns['X_CROSS']

# 主机柜 A 的淡出物件：这一镜看不到 A 机柜，保持原样（不隐藏也无妨）
# ---------- 青色消息的路径：A 线槽 → 过桥 → B 线槽 → B 机柜背面下去（照 S01 的路径线） ----------
ra = [to_world('A', I_A, p) for p in hero_route()]; rb = [to_world('B', I_B, p) for p in reversed(hero_route())]
zt = ra[-1].z; ya = ra[-1].y; yb = rb[0].y; xk = X_CROSS - 0.10
tray_run = fillet([ra[-1], (xk, ya, zt), (xk, yb, zt), rb[0]], 0.06, n=6)
route = tray_run + rb[1:]
cell = 0.12
msg = S.message_material('msg_cyan', S.CYAN_MSG, strength=7.0, cell=cell, head=True)
tube = S.sweep_tube('消息串_青', route, 0.020, msg, sides=10)
L_TOT = tube['arc_len']
# 过桥的位置（沿路径的弧长）：到 B 线槽的入口
arc = 0.0; arcs = [0.0]
for a, b in zip(route, route[1:]): arc += (V(b) - V(a)).length; arcs.append(arc)
print('STREAM 长度', round(L_TOT, 2), 'm | 起点', tuple(round(v, 2) for v in route[0]), '| 终点', tuple(round(v, 2) for v in route[-1]))
# 流速 = 每秒 8 位（0.96 m/s）；前端（head）匀速前进，1.5 s 走到终点附近
SPEED = 8.0 * cell
S.key_sock(msg.node_tree.nodes['msg_offset'].outputs[0], [(0.0, 0.0), (DUR, SPEED / cell * DUR)])
HEAD_T = 1.55
S.key_sock(msg.node_tree.nodes['msg_head'].outputs[0], [(0.0, 0.2), (HEAD_T, L_TOT + 0.1), (DUR, L_TOT + 0.1)])

# ---------- B 标记：先暗，消息到了以后亮起（先冲高一点再回到 shot1 里的柔和亮度） ----------
mk = S.b_marker(ns, strength=3.0)
T_ARR = HEAD_T + 0.05
S.key_sock(mk['e1'].inputs['Strength'], [(0.0, 0.5), (T_ARR, 0.5), (T_ARR + 0.18, 6.0), (T_ARR + 0.7, 3.0), (DUR, 3.0)])
S.key_sock(mk['e2'].inputs['Strength'], [(0.0, 0.08), (T_ARR, 0.08), (T_ARR + 0.18, 1.2), (T_ARR + 0.7, 0.55), (DUR, 0.55)])
S.key_energy(mk['light'], [(0.0, 8.0), (T_ARR, 8.0), (T_ARR + 0.18, 70.0), (T_ARR + 0.7, 30.0), (DUR, 30.0)])

# ---------- 灯光 ----------
C.world(ns['FOG'], 1.0, hdri='studio_small_09_2k.hdr', hdri_strength=0.14, hdri_rot=rad(90))
lights = C.collection('灯光')
def no_cam(o): o.visible_camera = False; return o
for x in ns['LIGHT_X'][::2]:
    no_cam(C.area_light(f'顶灯{x:.1f}', (x, 0, 2.74), (x, 0, 0), 0.9, 42.0, (0.30, 0.55, 1.0), size_y=0.25, col=lights))
no_cam(C.area_light('逆光', (ns['X1'] - 0.4, 0, 2.55), (ns['X1'] - 4.5, 0, 0.6), 1.4, 120, (0.30, 0.55, 1.0), size_y=0.6, col=lights))
S.add_fog_all(ns)

# ---------- 相机 ----------
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 't5_arrive_cam.py'), encoding='utf-8').read())
cam, tgt = C.add_camera('cam_T5ARR', lens=30, fstop=2.0, clip=(0.01, 200))
C.animate_camera(cam, tgt, cam_fn, shot)

dev = S.setup_render(args, exposure=0.0)
print('G_B', tuple(round(v, 3) for v in G_B), '| 标记中心', tuple(round(v, 3) for v in mk['center']))
C.render(args, shot, dev)
