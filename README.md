# kepu-studio

「芯片与光」科普短视频工作室：剑桥材料学博士讲芯片与光，发在抖音和小红书。视频由 Claude Code 写代码生成。

## 怎么用
1. 在 Claude Code 里新开会话时，**选上这个仓库**。`CLAUDE.md` 和 `.claude/skills/` 里的系列 skill 会自动加载。
2. 告诉 Claude 要做哪个系列的哪一集，它会按 `CLAUDE.md` 的流程走：拆题 → 脚本 → 你确认 → 草稿 → 你确认 → 终版。
3. 每周把抖音、小红书的数据导出或截图发给 Claude，说「写周报」。

## 目录
| 路径 | 内容 |
|---|---|
| `DECISIONS.md` | 所有决定和理由 |
| `CLAUDE.md` | 每次做片都要遵守的通用规则 |
| `.claude/skills/series-guanghulian/` | 「白话光互连」系列 |
| `.claude/skills/series-weishenme/` | 「为什么」系列 |
| `.claude/skills/weekly-report/` | 数据周报 |
| `episodes/` | 每集的脚本、FACTS.md、封面文案 |
| `assets/` | 「芯片与光」素材库 |
| `tools/` | 检查脚本（动效检测 motion_check.py） |
| `templates/` | 各系列的项目模板（渲染脚本、时间轴、配乐、封面脚本），从原会话迁入后放这里 |
| `config/` | 配音等配置 |
| `data/` | 每周数据快照和周报 |
| `archive/` | 暂停系列（「如果」）的资料 |

工具类 skill（agent-browser、find-skills、grill-me、grilling、anysearch）由云端环境的启动脚本安装，不在本仓库里。
