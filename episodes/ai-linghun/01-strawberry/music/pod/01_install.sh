# install ACE-Step 1.5 with uv and download the main model (turbo DiT + 1.7B LM) and the XL turbo DiT
set -ex
cd /w/acestep
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH=$HOME/.local/bin:$PATH
uv sync 2>&1 | tail -25
uv run acestep-download 2>&1 | tail -15
uv run acestep-download --model acestep-v15-xl-turbo 2>&1 | tail -8
du -sh checkpoints/* 2>/dev/null
uv run python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
