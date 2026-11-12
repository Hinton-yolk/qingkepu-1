#!/usr/bin/env bash
# 下载这一集用到的免费素材（Poly Haven，CC0：可商用、不用署名）。素材放在 assets_dl/，不进仓库。
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p assets_dl
get() { [ -s "assets_dl/$2" ] || curl -fsSL --retry 3 -o "assets_dl/$2" "$1"; echo "ok $2"; }
get https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/2k/studio_small_09_2k.hdr studio_small_09_2k.hdr
get https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/metal_plate/metal_plate_rough_2k.jpg metal_plate_rough_2k.jpg
