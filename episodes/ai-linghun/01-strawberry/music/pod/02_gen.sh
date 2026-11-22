set -x
export PATH=$HOME/.local/bin:$PATH
cd /w/acestep && uv run python /w/in/gen.py
ls -la /w/out/music
