"""生成 tools/runpod_render.py 的任务表：每个镜头一个任务。
用法：python3 gen_jobs.py <场景包目录（相对仓库根）> <输出目录（相对仓库根）> <缩放%> <亮场采样> <暗场采样> <每帧预计秒> [隔几帧渲一帧] > jobs.json"""
import sys, json
scene, out, scale, spp, spp_dark, spu = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], float(sys.argv[6])
step = int(sys.argv[7]) if len(sys.argv) > 7 else 1
SEGS = [("y1", 0, 59), ("y2", 0, 101), ("y3d", 0, 35), ("s34a", 0, 89), ("s34b", 90, 186), ("y4d", 0, 40), ("s34c", 228, 257), ("y5", 0, 119),
        ("y6g", 0, 95), ("y6c", 96, 269), ("y7", 0, 113), ("y8d", 0, 70), ("y8c", 0, 84), ("y9e", 0, 93), ("s9a", 0, 61), ("s9b", 62, 373),
        ("y12c", 0, 30), ("y12g", 0, 54), ("y12a", 0, 75), ("y13", 0, 119), ("y14", 0, 95)]
tasks = []
for shot, fs, fe in SEGS:
    dark = shot in ("y6g", "y12g")
    tasks.append({"args": ["/w/scene/tex", "/w/scene/dl", "{out}/" + shot, scale, spp_dark if dark else spp, "gpu=1", "thr=0.02" if int(scale) >= 100 else "thr=0.05",
                           f"shot={shot}", f"fs={fs}", f"fe={fe}"] + ([f"step={step}"] if step > 1 else []),
                  "units": int((fe - fs + 1) / step * (1.9 if dark else 1.0)) + 8})
print(json.dumps({"scene_dir": scene, "script": "film.py", "out_dir": out, "sec_per_unit": spu, "tasks": tasks}, ensure_ascii=False, indent=1))
