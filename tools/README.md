# 工具

## motion_check.py：动效量化检查
交成片前必须跑一次（`CLAUDE.md`「交出成片前的自检循环」第 4 步）。

```bash
python3 tools/motion_check.py <film.mp4> <name> --end=<片尾卡开始的秒数>
```

- 通过标准（片尾卡之前的正片）：静止帧 < 15%，任意 5 秒窗口静止 < 30%，最长静止 ≤ 0.6 秒。FAIL 时「动效质量」最多 6 分。
- 原理：把视频转成 30 fps、135×240 的灰度图，逐帧求平均差，差值 < 0.15 算静止。60 fps 的片子也会先降到 30 fps，阈值不变。
- 依赖：`ffmpeg`、`numpy`。`librosa` 可选，只用来输出「音乐 BPM、画面变化卡在节拍上的比例」那一行；没装就显示 nan，不影响 PASS / FAIL。需要时 `pip install librosa`。

### 来历
原版由「如果」系列的会话在 2026-11-04 写成（`/home/user/studio-tools/motion_check.py`），从那次会话的记录里逐条还原。2026-11-06 存进仓库时做了三处修改：
1. 分析前先把视频统一转成 30 fps。原版把帧率写死成 30，60 fps 的片子（例如光互连）时间轴会算错。
2. librosa 改为可选依赖。
3. 完全静止、没有任何画面变化的片子不再崩溃，会正常给出 FAIL。

## gemini_watch.py：让 Gemini 看视频（流式）
看参考视频、竞品视频，或者让 Gemini 复查自己的成片时用。

```bash
python3 tools/gemini_watch.py "<YouTube 链接或本地视频文件>" -q "问题" [--start 6:20 --end 7:30] [--out 答案.md]
```

- **为什么要流式**：云端会话的网络代理在约 30 秒没有回应时会掐断请求。Gemini 看完整视频常常超过 30 秒，
  所以 watch skill 自带的 Gemini 模式会报 `HTTP 502: upstream request failed`。流式接口通常在 30 秒内就开始返回。
- **自动换模型**：某个模型拥堵（503）、太慢（30 秒 502）或这个 Key 用不了（404）时，按顺序换下一个。
  默认顺序 `gemini-3.5-flash, gemini-3.6-flash, gemini-3.7-flash, gemini-flash-latest`（2026-11-09 实测 3.5 最稳），
  可以用 `--models` 或环境变量 `WATCH_GEMINI_MODELS` 改。
- **视频去哪了**：YouTube 链接直接交给 Google，这里不下载；本地文件上传到 Gemini Files API，用完立刻删除
  （删不掉的 48 小时内自动过期）。不要用它处理不想离开本机的视频，那种情况用 watch skill 的本地模式。
- **Key**：读 `GEMINI_API_KEY` 环境变量，再读 `~/.config/watch/.env`。云端环境里真 Key 存在环境的 Network secrets 中，
  由代理注入 `x-goog-api-key` 请求头，本地只需要一个占位值。
- **只用标准库**，不用装依赖。
- Gemini 的回答是它对视频的描述，**不是核实过的事实**；要引用进脚本或 FACTS.md 的数字，先对照原视频。
