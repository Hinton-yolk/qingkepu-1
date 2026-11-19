# 生成 RunPod 渲染用的场景包目录和 jobs.json（tools/runpod_render.py 用）。
# 用法：python3 runpod_bundle.py <包目录（相对仓库根）> <输出目录（相对仓库根）> --fps 12 --scale 0.25 --samples 8 --chunks 8
import os, sys, json, shutil, argparse
here = os.path.dirname(os.path.abspath(__file__)); repo = os.path.abspath(os.path.join(here, '..', '..', '..', '..', '..'))
ap = argparse.ArgumentParser(); ap.add_argument('pack'); ap.add_argument('out')
ap.add_argument('--fps', type=float, default=12); ap.add_argument('--scale', type=float, default=0.25); ap.add_argument('--samples', type=int, default=8)
ap.add_argument('--chunks', type=int, default=8); ap.add_argument('--start', type=int, default=0); ap.add_argument('--dur', type=float, default=109.6); ap.add_argument('--font', required=True); ap.add_argument('--ui_dir', required=True)
a = ap.parse_args()
pk = os.path.join(repo, a.pack); os.makedirs(pk, exist_ok=True)
for f in ('scene.py', 'film3d.py', 'film_desk.py'): shutil.copy(os.path.join(here, f), pk)
shutil.copy(os.path.join(here, '..', '..', 'script.md'), os.path.join(pk, 'script.md'))
shutil.copy(a.font, os.path.join(pk, 'NotoSansSC-Bold.otf'))
for f in ('ui_typing.png', 'ui_chunks.png'): shutil.copy(os.path.join(a.ui_dir, f), pk)
smiley = '/usr/share/fonts/truetype/smiley-sans/SmileySans-Oblique.ttf'
nf = int(round(a.dur * a.fps)); step = -(-(nf - a.start) // a.chunks)
tasks = [{'args': ['--outdir', '{out}', '--fps', str(a.fps), '--f0', str(i), '--f1', str(min(nf, i + step)), '--scale', str(a.scale), '--samples', str(a.samples),
                   '--font', '/w/scene/NotoSansSC-Bold.otf', '--ui_dir', '/w/scene'], 'units': min(nf, i + step) - i} for i in range(a.start, nf, step)]
J = {'scene_dir': a.pack, 'script': 'film_desk.py', 'out_dir': a.out, 'sec_per_unit': 1.2, 'env': {'KEPU_GPU': '1'}, 'tasks': tasks}
shutil.copy(smiley, os.path.join(pk, 'SmileySans-Oblique.ttf'))
json.dump(J, open(os.path.join(pk, 'jobs.json'), 'w'), ensure_ascii=False, indent=1)
print('ok', pk, nf, 'frames,', len(tasks), 'tasks')
