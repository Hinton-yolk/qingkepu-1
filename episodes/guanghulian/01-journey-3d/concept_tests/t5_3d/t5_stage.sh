#!/usr/bin/env bash
# 把 T5 场景按仓库里的相对位置放进 <工作目录>/stage（给 runpod_render.py 打包上传）
set -euo pipefail
EP=/home/user/kepu-studio/episodes/guanghulian; W="$1"; S="$W/stage"
rm -rf "$S"; mkdir -p "$S/01-journey-3d/concept_tests" "$S/blender_test_scale"
cp -r "$EP/01-journey-3d/blender" "$S/01-journey-3d/blender"
cp -r "$EP/01-journey-3d/timeline" "$S/01-journey-3d/timeline"
cp -r "$EP/01-journey-3d/concept_tests/t5_3d" "$S/01-journey-3d/concept_tests/t5_3d"
cp -r "$EP/blender_test_scale/assets" "$S/blender_test_scale/assets"
find "$S" -name __pycache__ -prune -exec rm -rf {} +
du -sh "$S"
