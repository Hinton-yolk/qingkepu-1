# T5 第 1 拍「空间与悬念」6.5 秒（195 帧，30 fps）。镜头节奏表：t5_3d/镜头节奏表_T5.md。
# 运行：blender -b --python-exit-code 1 --python t5_shot1.py -- <输出目录> --res 540x960 --samples N [--gpu] [--threads 2] [--times 0.0,1.5] [--frames a-b] [--save-blend]
# 镜头：
#   0–3 s   从 GPU A 的 +Y 边出发，贴着散热片和电路板，跟着金色消息往机箱后部走，同时往上抬、穿出机箱（上盖、柜门和上面的设备都已透明化）；
#   3–5 s   升到通道上方、转向：对面 B 排一台服务器（GPU B）的标记柔和地亮起，中间是线槽和十几米纵深；
#   5–6.5 s 俯冲回 GPU A 机箱后部：金色消息流进后面板上插着的半透明光模块，最后停在模块上。
# 消息：全片统一画法（t5_s1_scene.message_material），金色 = 电。
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import t5_s1_scene as S
import bpy
from mathutils import Vector
import common as C
V = Vector; PI = math.pi

DUR = 6.5
env = S.build_scene('T5S1', DUR); shot = env['shot']; args = env['args']; ns = env['ns']; sc = bpy.context.scene
G_A = ns['G_A']; G_B = ns['G_B']; M = ns['M']; to_world = ns['to_world']; srv_to_rack = ns['srv_to_rack']; I_A = ns['I_A']

# ---------- 把 S01 里和主机柜有关的淡出物件永久隐藏（相当于 S01 的 8.5 s 之后） ----------
FD = ns['FD']
for o in FD['door'] + FD['upper'] + FD['lid']: o.hide_render = True; o.hide_viewport = True
FD['light'].energy = 0.0
for o in bpy.data.objects:
    if o.name == 'A_服务器_p0stub_1': o.hide_render = True; o.hide_viewport = True

# ---------- 消息串的路径：GPU A +Y 边 → 模组小板 → 底板 → 网卡 → 铜缆 → 后面板光口 → 光模块里 ----------
SD = ns['SD']; ZM = ns['ZM']; ZB = ns['ZB']; ZC = ns['ZC']; COLS = ns['COLS']; ROW_Y = ns['ROW_Y']; LANE_X = ns['LANE_X']; GAP_Y = ns['GAP_Y']
NIC_Y = ns['NIC_Y']; CHIP_Y = ns['CHIP_Y']; CHIP = ns['CHIP']; CHIP_H = ns['CHIP_H']; R_CABLE = ns['R_CABLE']; CAGE_Y0 = ns['CAGE_Y0']; PORT_Z = ns['PORT_Z']
cable_route = ns['cable_route']; fillet = ns['fillet']
def stream_route():
    gx, gy = COLS[1], ROW_Y[0]; zt = ZM + 0.00053; zb = ZB + 0.0015; zc = ZC + 0.0016; zh = ZC + CHIP_H + 0.0016; zg = PORT_Z + 0.00625 + 0.0016
    y0 = NIC_Y[0] - 0.003; c0 = CHIP_Y - CHIP / 2 - 0.002; c1 = CHIP_Y + CHIP / 2 + 0.002; k0 = NIC_Y[1] - 0.014; dz = R_CABLE + 0.0012
    cab = [(p[0], p[1], p[2] + dz) for p in cable_route()[1:5]]
    pts = fillet([(gx, gy + 0.036, zt), (gx, gy + 0.100, zt), (gx, gy + 0.10125, zt), (gx, gy + 0.10125, zb), (gx, GAP_Y, zb), (LANE_X, GAP_Y, zb), (LANE_X, y0, zb), (LANE_X, y0, zc),
                  (LANE_X, c0, zc), (LANE_X, c0, zh), (LANE_X, c1, zh), (LANE_X, c1, zc), (LANE_X, k0, zc), (LANE_X, k0, ZC + 0.003 + dz)] + cab +
                 [(LANE_X, CAGE_Y0 - 0.002, zg), (LANE_X, SD - 0.014, zg), (LANE_X, SD - 0.006, PORT_Z + 0.0004)], 0.003, n=3)
    pts += [V((LANE_X, SD + 0.0005, PORT_Z + 0.0004)), V((LANE_X, SD + 0.0275, PORT_Z + 0.0004))]
    return pts
route = stream_route(); world = [to_world('A', I_A, srv_to_rack(p)) for p in route]
def radii(pts, r0, r_in):
    out = []
    for p in pts:
        y = p[1]; k = C.smooth(C.seg(y, SD - 0.014, SD - 0.006)); out.append(C.lerp(r0, r_in, k))
    return out
rl = radii(route, 0.0042, 0.0008)
FAR_K = 4.5                                                             # 拉远时管的粗细倍数（形态键 far）
msg_mat = S.message_material('msg_gold', (1.0, 0.50, 0.02), strength=9.0, cell=0.04)
tube = S.sweep_tube('消息串_金', world, rl, msg_mat, sides=8, radius_far=[r * (FAR_K if r > 0.0008 else 2.0) for r in rl])
print('STREAM 长度', round(tube['arc_len'], 3), 'm | 起点', tuple(round(v, 3) for v in world[0]), '| 终点', tuple(round(v, 3) for v in world[-1]))
# 流速：每秒几位（物理量，随镜头尺度调：贴近时 4 位/秒，拉远后加快，让屏幕上看起来约每秒 3–4 位）
RATE = [(0.0, 4.0), (2.0, 4.5), (3.5, 9.0), (5.0, 9.0), (6.5, 6.0)]
off_keys = []; acc = 0.0; tt = 0.0
while tt <= DUR + 1e-6:
    off_keys.append((tt, acc)); dt = 0.25; r = S.hermite_s(RATE, tt + dt / 2); acc += r * dt; tt += dt
S.key_sock(msg_mat.node_tree.nodes['msg_offset'].outputs[0], off_keys)
FAR = [(0.0, 0.0), (1.5, 0.0), (3.5, 1.0), (5.0, 1.0), (6.0, 0.0)]       # 形态键 far（粗 / 细）
sk = tube.data.shape_keys.key_blocks['far']
for t, v in FAR: sk.value = v; sk.keyframe_insert('value', frame=C.F(t))
C.set_interp(tube.data.shape_keys, 'LINEAR')

# ---------- 光模块（半透明） ----------
mod = S.optical_module(ns, 'A')

# ---------- B 排标记：服务器里透出的青色柔光；2.6–3.6 s 亮起 ----------
mk = S.b_marker(ns, strength=6.0)
S.key_sock(mk['e1'].inputs['Strength'], [(0.0, 0.0), (2.6, 0.0), (3.6, 40.0)])
S.key_energy(mk['light'], [(0.0, 0.0), (2.6, 0.0), (3.6, 900.0)])
# ---------- 很淡的青色虚线：沿线槽从 A 一侧指向 B ----------
fillet = ns['fillet']; hero_route = ns['hero_route']; X_CROSS = ns['X_CROSS']; I_B = ns['I_B']
ra = [to_world('A', I_A, p) for p in hero_route()]; rb = [to_world('B', I_B, p) for p in reversed(hero_route())]
zt = ra[-1].z; ya = ra[-1].y; yb = rb[0].y; xk = X_CROSS - 0.10
dpts = [V(p) + V((0, 0, 0.035)) for p in fillet([ra[-1], (xk, ya, zt), (xk, yb, zt), rb[0]], 0.06, n=6)]
dmat = S.dash_material('dash_cyan', (0.15, 0.85, 1.0), strength=1.2, period=0.22)
dash = S.sweep_tube('虚线_青', dpts, 0.012, dmat, sides=6)
S.key_sock(dmat.node_tree.nodes['dash_strength'].outputs[0], [(0.0, 0.0), (2.8, 0.0), (3.8, 1.2)])
S.key_sock(dmat.node_tree.nodes['dash_offset'].outputs[0], [(0.0, 0.0), (DUR, 2.2 * DUR)])

# ---------- 灯光 ----------
ns_ = ns; rad = math.radians
C.world(ns['FOG'], 1.0, hdri='studio_small_09_2k.hdr', hdri_strength=0.14, hdri_rot=rad(90))
lights = C.collection('灯光')
def no_cam(o): o.visible_camera = False; return o
for x in ns['LIGHT_X'][::2]:
    no_cam(C.area_light(f'顶灯{x:.1f}', (x, 0, 2.74), (x, 0, 0), 0.9, 42.0, (0.30, 0.55, 1.0), size_y=0.25, col=lights))
no_cam(C.area_light('逆光', (ns['X1'] - 0.4, 0, 2.55), (ns['X1'] - 4.5, 0, 0.6), 1.4, 120, (0.30, 0.55, 1.0), size_y=0.6, col=lights))
O_MOD = G_A - V((0, 0, 0.00253))
BOX = (('箱内暖逆光', (-0.180, 0.260, 0.240), 0.26, (1.0, 0.82, 0.62), 3.6), ('箱内冷补光', (0.240, -0.200, 0.160), 0.30, (0.62, 0.78, 1.0), 1.2),
       ('箱内顶光', (0.0, -0.020, 0.320), 0.20, (1.0, 1.0, 1.0), 0.7), ('箱内环境替身', (0.0, -0.05, 0.50), 0.80, (0.85, 0.90, 1.0), 0.5))
for name, off, size, color, e in BOX:
    o = no_cam(C.area_light(name, O_MOD + V(off), O_MOD, size, e, color, col=lights))
# 机箱后部：给光模块一盏柔光
PORT_W = to_world('A', I_A, srv_to_rack((LANE_X, SD + 0.10, PORT_Z + 0.18)))
no_cam(C.area_light('后部补光', PORT_W, to_world('A', I_A, srv_to_rack((LANE_X, SD + 0.01, PORT_Z))), 0.25, 1.2, (0.9, 0.95, 1.0), col=lights))
S.add_fog_all(ns)

# ---------- 相机 ----------
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 't5_shot1_cam.py'), encoding='utf-8').read())
cam, tgt = C.add_camera('cam_T5S1', lens=35, fstop=2.8, clip=(0.005, 200))
C.animate_camera(cam, tgt, cam_fn, shot)

# ---------- --anchors：只出屏幕坐标，不渲染（合成用） ----------
if args.anchors:
    S.write_anchors(shot, cam, {'gpu_a': G_A, 'gpu_b': G_B, 'module_a': mod['W']((LANE_X, SD + 0.02, PORT_Z))}, args.out)
    sys.exit(0)

# ---------- 渲染 ----------
dev = S.setup_render(args, exposure=0.0)
S.setup_glare(size=7, strength=3.0)
print('G_A', tuple(round(v, 4) for v in G_A), '| G_B', tuple(round(v, 4) for v in G_B), '| 光模块', tuple(round(v, 4) for v in mod['W']((LANE_X, SD + 0.02, PORT_Z))))
C.render(args, shot, dev)
