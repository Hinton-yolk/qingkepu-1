#!/usr/bin/env python3
"""Blender 混合段：为 blender/seg/<f0>_<f1>/（render.mjs --export-seg 导出）各做一个 RunPod 任务目录和 jobs.json。
每段一个目录 blender/hyb/<段>/（build.py + 段数据），每 30 帧一个任务；之后在仓库根目录对每段跑：
  python3 tools/runpod_render_gql.py run episodes/ai-linghun/01-strawberry/film/blender/hyb/<段>/jobs.json --pods N --yes
渲好的帧拉回 film/blender/out/hyb/<帧号>.png（index.html ?bg=hyb 用它合成调色和字幕）。
  python3 hyb_jobs.py [--samples 128] [--chunk 30] [--only <段>,<段>]
"""
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
a = sys.argv[1:]; opt = lambda k, d: a[a.index(k) + 1] if k in a else d
SAMPLES, CHUNK = opt("--samples", "128"), int(opt("--chunk", 30))
ONLY = opt("--only", "")   # --only 00000_00240,02391_02469 : just these segments (the others keep their job dirs and rendered frames)
for seg in sorted(os.listdir(os.path.join(HERE, "seg"))):
    if ONLY and seg not in ONLY.split(","): continue
    src = os.path.join(HERE, "seg", seg); A = json.load(open(os.path.join(src, "anim.json")))
    job = os.path.join(HERE, "hyb", seg); shutil.rmtree(job, ignore_errors=True); os.makedirs(job)
    shutil.copy(os.path.join(HERE, "build.py"), job); shutil.copytree(src, os.path.join(job, "data"))
    tasks = [dict(args=["{out}", str(f), str(min(f + CHUNK - 1, A["f1"])), SAMPLES, "cycles", "gpu", "1.0", "/w/scene/data"], units=min(CHUNK, A["f1"] - f + 1))
             for f in range(A["f0"], A["f1"] + 1, CHUNK)]
    J = dict(scene_dir=os.path.relpath(job, REPO), script="build.py", out_dir=os.path.relpath(os.path.join(HERE, "out", "hyb"), REPO),
             sec_per_unit=9, env=dict(KEPU_GPU="OPTIX"), tasks=tasks)
    json.dump(J, open(os.path.join(job, "jobs.json"), "w"), ensure_ascii=False, indent=1)
    print(seg, len(tasks), "tasks,", A["f1"] - A["f0"] + 1, "frames ->", os.path.relpath(os.path.join(job, "jobs.json"), REPO))
