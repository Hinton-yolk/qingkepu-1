# runs ON the pod: uv run python /w/in/gen.py  — reads /w/in/jobs.json, writes /w/out/music/*.wav
# job: {name, caption, key, bpm, duration, seeds, model, stages:[{start, end, caption}]}  (stages = repaint passes, in order)
import json, os, shutil, sys, time, traceback, gc
sys.path.insert(0, '/w/acestep'); os.chdir('/w/acestep')
import torch
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music
J = json.load(open('/w/in/jobs.json')); OUT = '/w/out/music'; os.makedirs(OUT, exist_ok=True); CK = '/w/acestep/checkpoints'
llm = LLMHandler()
for be in (J.get('lm_backend', 'vllm'), 'pt'):
    try: llm.initialize(checkpoint_dir=CK, lm_model_path='acestep-5Hz-lm-1.7B', backend=be, device='cuda'); print('LM backend', be, flush=True); break
    except Exception: traceback.print_exc(); llm = LLMHandler()
cur, dit = None, None
def gen(params, seeds, tag):
    cfg = GenerationConfig(batch_size=len(seeds), use_random_seed=False, seeds=seeds, audio_format='wav')
    tmp = f'{OUT}/tmp_{tag}'; t0 = time.time(); r = generate_music(dit, llm, params, cfg, save_dir=tmp)
    if not r.success: raise RuntimeError(r.error)
    paths = [a['path'] for a in r.audios]; print(tag, f'{time.time() - t0:.1f}s', [(a.get('key'), a['params'].get('bpm'), a['params'].get('keyscale')) for a in r.audios], flush=True)
    return paths
for j in J['jobs']:
    try:
        if j['model'] != cur:
            dit = None; gc.collect(); torch.cuda.empty_cache()
            dit = AceStepHandler(); dit.initialize_service(project_root='/w/acestep', config_path=j['model'], device='cuda'); cur = j['model']
        base = dict(lyrics='[Instrumental]', instrumental=True, bpm=j['bpm'], keyscale=j['key'], timesignature='4', inference_steps=8, shift=3.0)
        p = GenerationParams(task_type='text2music', caption=j['caption'], duration=j['duration'], thinking=True, use_cot_caption=False, **base)
        for k, src in enumerate(gen(p, j['seeds'], j['name'])):
            s = j['seeds'][k]; cur_path = f"{OUT}/{j['name']}_s{s}_raw.wav"; shutil.copy(src, cur_path)
            for n, st in enumerate(j.get('stages', [])):
                q = GenerationParams(task_type='repaint', src_audio=cur_path, repainting_start=st['start'], repainting_end=st['end'],
                                     chunk_mask_mode='explicit', caption=st['caption'], **base)
                nxt = f"{OUT}/{j['name']}_s{s}_st{n + 1}.wav"; shutil.copy(gen(q, [s + 100 * (n + 1)], f"{j['name']}_s{s}_st{n + 1}")[0], nxt); cur_path = nxt
            shutil.copy(cur_path, f"{OUT}/{j['name']}_s{s}_final.wav")
    except Exception:
        traceback.print_exc(); print('JOB FAILED', j['name'], flush=True)
for d in os.listdir(OUT):
    if d.startswith('tmp_'): shutil.rmtree(f'{OUT}/{d}', ignore_errors=True)
print('ALL DONE', flush=True)
