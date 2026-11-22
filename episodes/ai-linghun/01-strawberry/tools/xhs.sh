#!/bin/sh
# 小红书全屏版 1080×2340。本系列字幕在下方（约 y 1300–1400），所以补高分在上下两边：顶部 24 行模糊拉伸成 210 px 补在上方、
# 底部 24 行模糊拉伸成 210 px 补在下方，字幕落在全屏的约 65–69% 处，避开小红书底部的标题 / 文案浮层（只补顶部 420 px 会落到约 73–78%）。
# 「为什么」系列字幕在顶部，仍用只补顶部的做法（见该系列 skill）。音频原样拷贝。
#   sh tools/xhs.sh <成片 1080×1920.mp4> <输出 1080×2340.mp4>
set -e
ffmpeg -v error -y -i "$1" -filter_complex "[0:v]split=3[a][b][c];[a]crop=1080:24:0:0,scale=1080:210,boxblur=20:2[top];[c]crop=1080:24:0:1896,scale=1080:210,boxblur=20:2[bot];[top][b][bot]vstack=inputs=3,format=yuv420p[v]" \
  -map "[v]" -map 0:a? -c:v libx264 -preset slow -crf 16 -profile:v high -movflags +faststart -c:a copy "$2"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height -show_entries format=duration -of csv=p=0 "$2"
