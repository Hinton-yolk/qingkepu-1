# 生成 RunPod 渲染包和 jobs.json（tools/runpod_render_gql.py 用）。
# 用法（仓库根目录）：python3 episodes/ai/01-yigeyigezi/src/anim01/runpod_pack.py <包目录> <输出目录> --scale 0.5 --samples 24 --chunks 4 [--shots a,b,c]
import os, sys, json, shutil, argparse
here = os.path.dirname(os.path.abspath(__file__)); repo = os.path.abspath(os.path.join(here, '..', '..', '..', '..', '..'))
ap = argparse.ArgumentParser(); ap.add_argument('pack'); ap.add_argument('out')
ap.add_argument('--scale', type=float, default=0.5); ap.add_argument('--samples', type=int, default=24); ap.add_argument('--chunks', type=int, default=4)
ap.add_argument('--shots', default='a,b,c'); ap.add_argument('--ranges', default='');   # 例：0-260,1182-2160（只渲这些帧）
ap.add_argument('--font', default=os.path.join(here, '..', 'style3d', 'out', 'motion_v2', 'NotoSansSC-Bold.otf'))
a = ap.parse_args()
pk = os.path.join(repo, a.pack); shutil.rmtree(pk, ignore_errors=True); os.makedirs(os.path.join(pk, 'anim01')); os.makedirs(os.path.join(pk, 'style3d'))
for f in ('lib.py', 'shot_a.py', 'shot_b.py', 'shot_c.py', 'shot_int.py', 'shot_int2.py', 'shot_full.py', 'shot_v02.py', 'ui_phone.png', 'ui_phone_v2.png'): shutil.copy(os.path.join(here, f), os.path.join(pk, 'anim01', f))
shutil.copy(os.path.join(here, 'run_shot.py'), os.path.join(pk, 'run_shot.py'))
for f in ('film_desk.py', 'film3d.py', 'scene.py'): shutil.copy(os.path.join(here, '..', 'style3d', f), os.path.join(pk, 'style3d', f))
shutil.copy(os.path.join(here, '..', '..', 'script.md'), os.path.join(pk, 'style3d', 'script.md'))
shutil.copy(a.font, os.path.join(pk, 'NotoSansSC-Bold.otf'))
DUR = {'a': 14.0, 'b': 10.5, 'c': 17.0, 'int': 34.0, 'int2': 32.0, 'full': 64.5, 'v02': 72.0}
tasks = []
for s in a.shots.split(','):
    nf = int(round(DUR[s] * 30))
    rg = [tuple(map(int, r.split('-'))) for r in a.ranges.split(',')] if a.ranges else [(0, nf)]
    tot = sum(b - a_ for a_, b in rg); step = -(-tot // a.chunks)
    for r0, r1 in rg:
        for f0 in range(r0, r1, step):
            f1 = min(r1, f0 + step)
            tasks.append({'args': ['--which', s, '--outdir', '{out}/' + s, '--f0', str(f0), '--f1', str(f1), '--scale', str(a.scale),
                                   '--samples', str(a.samples), '--font', '/w/scene/NotoSansSC-Bold.otf'], 'units': f1 - f0})
J = {'scene_dir': a.pack, 'script': 'run_shot.py', 'out_dir': a.out, 'sec_per_unit': 1.5, 'env': {'KEPU_GPU': '1'}, 'tasks': tasks}
json.dump(J, open(os.path.join(pk, 'jobs.json'), 'w'), ensure_ascii=False, indent=1)
print('ok', pk, sum(t['units'] for t in tasks), 'frames,', len(tasks), 'tasks')
