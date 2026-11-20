# RunPod 入口：blender -b -P run_shot.py -- --which a|b|c [其余参数照 shot_X.py]
import sys, os
argv_ = sys.argv[sys.argv.index('--') + 1:]
shot = argv_[argv_.index('--which') + 1]
here = os.path.dirname(os.path.abspath(__file__))
p = next(c for c in (os.path.join(here, f'shot_{shot}.py'), os.path.join(here, 'anim01', f'shot_{shot}.py')) if os.path.exists(c))
g = {'__file__': p, '__name__': '__main__'}
exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), g)
