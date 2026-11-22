# one-shot setup on a fresh tools/runpod_exec.py pod: system packages, ACE-Step 1.5 code, uv env, main model + XL turbo DiT
set -ex
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq >/dev/null && apt-get install -y -qq git ffmpeg curl >/dev/null
cd /w && rm -rf acestep && git clone --depth 1 https://github.com/ACE-Step/ACE-Step-1.5 acestep
cd /w/acestep && git log -1 --format='%H %cd'
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH=$HOME/.local/bin:$PATH
uv sync 2>&1 | tail -5
uv run acestep-download 2>&1 | tail -3
uv run acestep-download --model acestep-v15-xl-turbo 2>&1 | tail -3
uv run python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
