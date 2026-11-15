#!/usr/bin/env python3
"""把这一集的 Blender 场景整理成云端渲染要的目录和任务表（配合 tools/runpod_render.py 用）。
用法：python3 blender/cloud_stage.py <工作目录> <镜头号[,镜头号…]> [--res 540x960] [--samples 24] [--step 1] [--chunk 130]
  例：python3 blender/cloud_stage.py /tmp/x S01 --chunk 195
做的事：
  · 在 <工作目录>/stage/ 下按原来的相对位置放好：01-journey-3d/blender（场景脚本、下载的素材）、
    01-journey-3d/timeline、blender_test_scale/assets（标签字体）。common.py 靠这些相对位置找文件。
  · 写 <工作目录>/jobs_<镜头>.json：每个镜头按 --chunk 帧一段切成几个任务（每段各建一次场景）。
  · 输出目录是 <工作目录>/out_cloud/。
不上传、不花钱；真正租机器的是 runpod_render.py 的 run … --yes。
runpod_render.py 目前在 PR #1 的分支里（tools/），合并前先把它拷到 <工作目录>/tools/ 下再运行。"""
import argparse, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__)); EP = os.path.dirname(HERE); SERIES = os.path.dirname(EP)
SCRIPTS = {'S01': 's01_datacenter.py', 'S02': 's02_gpu_package.py', 'S03': 's03_serdes.py'}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('work'); ap.add_argument('shots')
    ap.add_argument('--res', default='540x960'); ap.add_argument('--samples', type=int, default=24)
    ap.add_argument('--step', type=int, default=1); ap.add_argument('--chunk', type=int, default=130)
    ap.add_argument('--sec-per-frame', type=float, default=4.0)
    a = ap.parse_args()
    tl = json.load(open(os.path.join(EP, 'timeline', 'timeline.json'), encoding='utf-8')); fps = tl['meta']['fps']
    stage = os.path.join(a.work, 'stage'); shutil.rmtree(stage, ignore_errors=True)
    dst_bl = os.path.join(stage, '01-journey-3d', 'blender'); os.makedirs(dst_bl)
    for name in os.listdir(HERE):
        src = os.path.join(HERE, name)
        if name == '__pycache__': continue
        (shutil.copytree if os.path.isdir(src) else shutil.copy2)(src, os.path.join(dst_bl, name))
    shutil.copytree(os.path.join(EP, 'timeline'), os.path.join(stage, '01-journey-3d', 'timeline'))
    font_dir = os.path.join(SERIES, 'blender_test_scale', 'assets')
    os.makedirs(os.path.join(stage, 'blender_test_scale', 'assets'))
    for name in os.listdir(font_dir):
        if name.endswith(('.otf', '.ttf')): shutil.copy2(os.path.join(font_dir, name), os.path.join(stage, 'blender_test_scale', 'assets', name))
    for sid in a.shots.split(','):
        s = next(x for x in tl['shots'] if x['id'] == sid); f0 = round(s['start'] * fps) + 1; f1 = round(s['end'] * fps); tasks = []
        f = f0
        while f <= f1:
            g = min(f + a.chunk * a.step - 1, f1); n = len(range(f, g + 1, a.step))
            tasks.append({'args': [SCRIPTS[sid], '{out}', '--range', str(f), str(g), '--step', str(a.step), '--res', a.res,
                                   '--samples', str(a.samples), '--gpu', '--anchors'], 'units': n})
            f = g + 1
        jobs = {'scene_dir': 'stage', 'script': '01-journey-3d/blender/cloud_entry.py', 'out_dir': 'out_cloud',
                'sec_per_unit': a.sec_per_frame, 'tasks': tasks}
        p = os.path.join(a.work, f'jobs_{sid}.json'); json.dump(jobs, open(p, 'w'), ensure_ascii=False, indent=1)
        print(p, '：', len(tasks), '个任务，', sum(t['units'] for t in tasks), '帧')

if __name__ == '__main__':
    main()
