# on a tools/runpod_exec.py pod: Blender 5.2.3 + the libraries it needs (headless Cycles on the GPU)
set -ex
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq >/dev/null
apt-get install -y -qq --no-install-recommends curl ca-certificates xz-utils libxrender1 libxxf86vm1 libxfixes3 libxi6 libxkbcommon0 \
  libxkbcommon-x11-0 libsm6 libice6 libx11-6 libxext6 libgl1 libegl1 libglib2.0-0 libtbb12 >/dev/null
cd /w && curl -sSL https://download.blender.org/release/Blender5.2/blender-5.2.3-linux-x64.tar.xz | tar -xJ && mv blender-*-linux-x64 bl
/w/bl/blender -b --version | head -2
nvidia-smi --query-gpu=name,memory.total --format=csv
