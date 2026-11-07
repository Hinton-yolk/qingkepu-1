# 光互连 03 · 抖音版（无旁白 · 科技感）

引擎沿用 02 抖音拆解版那套（`../../02-serdes/douyin-split/代码工程/`：engine.js、lib、split/core.js、split/tech.js）。运行前把这里的 `代码工程/` 拷进那份引擎目录。
- 分镜：`内容关卡_无旁白分镜.md`
- 时间表：`python3 tools/build_g.py` → `代码工程/split/g1.json`、`g2.json`（120 BPM 拍点）
- 画面：`代码工程/split/g1.js`（第 1 条）、`g2.js`（第 2 条，依赖 g1.js 的公用画法）
- 配乐 + 音效：`python3 tools/score_g.py g1|g2`（代码合成，小红书版音色）
- 草稿：`bash render_g.sh g1|g2`
- 早先做的纸桌 + 旁白版（`内容关卡_脚本.md`、`第1条_草稿接触表.jpg` 等）用户看后改成了无旁白科技感版，留作资料。
