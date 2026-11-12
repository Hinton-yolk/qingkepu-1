# S03 SerDes：并排 → 一列（23–39 秒）· 第一站 出发。单位：1 = 1 µm。
# 状态：v1 粗模（预演用）。连线层数、线宽、串化电路结构都是简化示意，不能当最终科学结构交付。
# 朝向（倒装芯片，接 S02）：相机从硅背面一侧往下看。+Z 朝硅背面（朝相机），−Z 朝凸点和封装基板。
#   所以离相机最近的是细的下层连线，往下是粗的上层金属，再往下是凸点。输出信号离开芯片 = 往 −Z 走，和相机推进同向。
# 几何、材质、灯光、相机路线都在 beol_assets.py（和 S02 尾段共用，23.0 秒两边是同一套东西，不切）。画法见那个文件开头，要点：
#   · 32 条并排的数据线（「一大排」，示意画 32 条），每条线整体亮（1）或暗（0），一拍（6.4 秒）同时换一排。
#   · 串化电路画成五级二选一树：32 → 16 → 8 → 4 → 2 → 1，每过一级节拍快一倍；最后一条线的节拍是并行线的 32 倍（0.2 秒一拍）。
#   · 输出驱动把这一路信号变成一对互补的线（差分 P / N，一根亮时另一根暗）：两根并行的粗线 → 两串通孔 → 两个相邻的微凸点
#     （直径约 25 µm、间距画 45 µm；真实是 40 µm 上下一档，FACTS V12）→ 硅中介层表面的一对走线。树里和并行线仍是单根（片内逻辑信号，示意）。
#     真实叠层：芯片 → 微凸点 → 硅中介层 → C4 凸点 → 有机基板 → 焊球 → 电路板（FACTS V12）。
#   · 不画沿线移动的小球：片内导线只有几十微米，一个符号对应毫米级长度，同一时刻整条线几乎等电位（FACTS V9）。
# 示意、要在屏幕上加注的：凸点周围 ±36 µm 的连线清掉了（真实芯片这里同样布满连线）；P / N 两根线没有配平长度；
#   微凸点画成球（真实多是铜柱 + 焊帽）；中介层表面的走线和焊盘只是示意；节拍慢放约两百亿倍（按 0.2 秒一拍重算，FACTS V8）。
# 运行：blender -b --python-exit-code 1 --python s03_serdes.py -- <输出目录> [--times 23.2,26,30,34,37,38.8] [--res 270x480] [--samples 24]
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import common as C
import beol_assets as B

shot = C.Shot('S03'); args = C.parse_args(); sc = C.reset(shot); rad = math.radians

# ---------- 连线层：信号线（五级树 + 差分输出）和周围的连线，全部来自共享模块 ----------
beol = B.build(shot.t0, shot.t1)

# ---------- 相机（路线在 beol_assets.micro_cam） ----------
# 23.0 s 接 S02 的尾帧：几乎正俯视，数据线在画面里竖着（相机在 −X 一侧朝 +X 看），还带着 S02 末尾的推进和前进速度。
# 23–27.4：沿数据线推到串化电路上方；27.4–35.5：基本停住（只留很慢的漂移；讲工序时相机不动）；
# 35.5–39：贴着差分对的一侧一直往下（−Z），从 P 凸点旁边落到芯片下面，方位只变几度；39.0 秒仍在往下，S04 接着落到电路板。
cam, tgt = C.add_camera('cam_S03', lens=50, fstop=1.0, clip=(0.05, 5000))
C.animate_camera(cam, tgt, B.micro_cam, shot)
for tt in (shot.t0, shot.t0 + 1 / C.FPS, 35.5, 38.9, shot.t1 - 1 / C.FPS):     # 接缝核对用：23.0 秒对 S02 的尾帧；39 秒看是不是还在往下
    d = B.micro_cam(tt); print('CAMCHK S03 t=%.4f 局部µm loc=(%.3f, %.3f, %.3f) tgt=(%.3f, %.3f, %.3f) fstop=%.5f lens=%.1f' % (tt, *d['loc'], *d['tgt'], d['fstop'], d['lens']))

# ---------- 灯光：两盏平行光（冷主光 + 暖逆光）+ 环境光，和 S02 尾段同一套；底色深蓝黑，金色只留给信号 ----------
B.world(local=True)
B.lights(beol['root'])

dev = C.setup_render(args, exposure=0.0)
if args.anchors:
    pair = C.empty('锚点_差分输出')
    for f in range(shot.f0, shot.f1 + 1): pair.location = B.anchor_pair((f - 1) / C.FPS); pair.keyframe_insert('location', frame=f)
    C.export_anchors(os.path.join(args.out, f'anchors_{shot.id}.json'), shot, cam,
                     {'并行总线': beol['pts']['并行总线'], '串化电路旁': beol['pts']['串化电路旁'], '差分输出': pair,
                      'bump_p': beol['pts']['bump_p'], 'bump_n': beol['pts']['bump_n']})
C.render(args, shot, dev)
