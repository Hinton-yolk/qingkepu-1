# T5 云端渲染入口（拷自 blender/cloud_entry.py）：一个任务表跑 t5_3d 里不同的镜头脚本。
# 用法（在 blender `--` 之后）：<镜头脚本名> <输出目录> [镜头脚本自己的参数…]
#   blender -b --python cloud_entry.py -- t5_shot1.py /w/out/shot1 --frames 1-195 --res 540x960 --samples 32 --gpu
# 做的事：把第一个参数当成同目录下的脚本名，去掉它之后原样执行那个脚本。
import os, runpy, sys

here = os.path.dirname(os.path.abspath(__file__))
i = sys.argv.index('--')
script = sys.argv[i + 1]
if os.path.basename(script) != script or not script.endswith('.py'):
    raise SystemExit('第一个参数必须是同目录下的脚本名：' + script)
sys.argv = sys.argv[:i + 1] + sys.argv[i + 2:]
sys.path.insert(0, here)
runpy.run_path(os.path.join(here, script), run_name='__main__')
