# 打 RunPod 渲染包：python3 episodes/ai/01-yigeyigezi/src/fridge01/pack.py [--res 540] [--samples 32] [--chunks 8] [--ranges 0-600]
import os, json, shutil, argparse
here = os.path.dirname(os.path.abspath(__file__)); repo = os.path.abspath(os.path.join(here, '..', '..', '..', '..', '..'))
ap = argparse.ArgumentParser(); ap.add_argument('--res', type=int, default=540); ap.add_argument('--samples', type=int, default=32)
ap.add_argument('--chunks', type=int, default=8); ap.add_argument('--ranges', default='0-600'); ap.add_argument('--tag', default='v1')
a = ap.parse_args()
rel = os.path.relpath(here, repo); pk = os.path.join(here, 'out', 'pack_' + a.tag); shutil.rmtree(pk, ignore_errors=True); os.makedirs(pk)
shutil.copy(os.path.join(here, 'fridge.py'), pk)
tasks = []
rg = [tuple(map(int, r.split('-'))) for r in a.ranges.split(',')]; tot = sum(b - a_ for a_, b in rg); step = -(-tot // a.chunks)
for r0, r1 in rg:
    for f0 in range(r0, r1, step):
        f1 = min(r1, f0 + step)
        tasks.append({'args': ['--outdir', '{out}/frames', '--f0', str(f0), '--f1', str(f1), '--res', str(a.res), '--samples', str(a.samples)], 'units': f1 - f0})
J = {'scene_dir': os.path.join(rel, 'out', 'pack_' + a.tag), 'script': 'fridge.py', 'out_dir': os.path.join(rel, 'out', 'render_' + a.tag),
     'sec_per_unit': 2.0, 'env': {'KEPU_GPU': '1'}, 'tasks': tasks}
json.dump(J, open(os.path.join(pk, 'jobs.json'), 'w'), ensure_ascii=False, indent=1)
print('ok', pk, tot, 'frames', len(tasks), 'tasks')
