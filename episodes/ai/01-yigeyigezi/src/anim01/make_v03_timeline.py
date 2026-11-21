# 把 post.py 里 v03 的屏幕文字换算成成片时间，写成字幕时间表（给观众 Codex 和交付文档用）
import sys, os
sys.argv = ['x']; __file__ = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0] or '.')), 'post.py')
H = os.path.dirname(os.path.abspath(__file__)) if os.path.exists(__file__) else os.getcwd()
exec(open(os.path.join(H, 'post.py'), encoding='utf-8').read().split("if __name__")[0])
f = v03_time.scene_to_film
rows = [(max(0, f(a)), f(min(b, 79.0)), '大字' if y < 1400 else '底部小字', t) for (t, a, b, y, sz) in TITLES['v03']]
rows += [(max(0, f(a)), f(b), '标签', t) for (k, t, st, a, b, dy) in LABELS['v03']]
rows.sort()
out = '\n'.join(f'{a:5.1f}–{b:5.1f} 秒  [{kind}] {t}' for a, b, kind, t in rows)
print(out)
