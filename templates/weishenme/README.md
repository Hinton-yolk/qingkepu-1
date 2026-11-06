# 「为什么」项目骨架（以 EP.02 微波炉为准）

系列规则在 `SERIES.md`（系列圣经），做新一集前先读。

## 开一集
1. 把本目录复制到 `episodes/weishenme/0N-短名/`（`covers/` 不用复制）。
2. `timeline.js`：唯一的时间表。`T` 里是每个画面事件的秒数（120 BPM，1 拍 = 0.5 秒，重要的点落在小节线上），`COPY` 里是全部字幕。
3. `index.html`：画面。`window.seek(t)` 是纯函数，只用带种子的随机数。
4. `music/score.mjs`：配乐和音效，读 `timeline.js` 里的 `HITS`。每集换调性、和声进行和旋律，不换曲风。

## 命令（在这一集的目录里跑）
- `node music/score.mjs`：生成 `music/score-C.wav`，再复制成 `music/score.wav`
- `sh tools/master.sh`：`music/score.wav` → `audio/mix.wav`（-14 LUFS）
- `python3 tools/fonts.py`：按片子里用到的字重新子集化字体（得意黑、Noto Sans SC，都是 OFL 授权）
- `node render.mjs --sheet`：每拍一帧接触表；`--stills=0,6.9`：单帧；`--strip=11.3,12.3`：剪辑点前后的连续帧
- `node render.mjs`：全片渲染并编码（H.264 yuv420p CRF 16，AAC 用 `-aac_coder fast`）；`--from=57.4` 只重渲某秒之后的帧
- `node tools/beatcheck.mjs`：检查 HITS 是否都在节拍网格上；`python3 tools/motion.py`：逐秒画面变化；`sh tools/verify.sh`：成片检查（`verify.sh` 里的文件名 `F=` 要改成这一集的）

## 封面（`covers/`）
- `shots.mjs` 从各集片子里截出干净画面放进 `covers/art/`，`make.mjs` 再排出抖音（1080×1920）和小红书（1080×1440）封面，`文案.md` 是三集的发布文案。
- `shots.mjs` 里的路径还是原来机器上的 `../ep01-gyroscope` 这种写法，用之前要改成 `../../../episodes/weishenme/0N-短名`。`art/*.png` 是截出来的中间文件，没放进仓库，跑一次 `shots.mjs` 就会重新生成。

成片、音频、帧和审片截图都不进仓库（见根目录 `.gitignore`）。
