# EP.08 充电寿命 · FACTS（白话版 v1，2026-11-16）

来源等级：〔官〕厂商官方文档；〔综〕综述 / 论文；〔科〕独立科普站；〔待〕还没找到可靠来源，进脚本前要补。
本会话里 apple.com / support.apple.com 不在网络白名单，Apple 条目是从搜索摘要读到的原文片段；节点 ① 事实核查时要对照原页面（或请用户放行这两个域名）。
脚本定稿时由审核用最强模型做事实核查。

| # | 片中说法 | 事实 | 来源 |
|---|---|---|---|
| 1 | 它不数你插了几次；搬满一整趟才算一次 | Apple：一次充电循环 = 累计用掉相当于 100% 电量，不必一次用完；例：今天用 75% 充满、明天再用 25%，合起来算一次 | 〔官〕Apple「Why Lithium-ion」https://www.apple.com/batteries/why-lithium-ion/ ；〔官〕iPhone 15 电池循环说明（转引 MacRumors 2024-02-20 https://www.macrumors.com/2024/02/20/apple-raises-iphone-15-advertised-battery-lifespan/ ） |
| 2 | 「充两次半格，加起来还是一次」 | 由 #1 推出；是「累计量」的简化示例。严格说循环老化还和放电深度、倍率、温度有关：浅充浅放比深充深放更温和 | 〔官〕同 1；〔科〕Battery University BU-808（放电深度越浅，循环寿命越长；锂离子没有记忆效应，不需要定期放空）https://batteryuniversity.com/article/bu-808-how-to-prolong-lithium-based-batteries |
| 3 | 电池确实有寿命（不进字幕的背景） | iPhone 15 系列：理想条件下 1000 次完整循环后保留约 80% 原始容量；iPhone 14 及更早为 500 次 | 〔官〕Apple「iPhone 电池与性能」（转引 MacRumors，同 1）。**片中不放这个数**（画面数字上限 3 个） |
| 4 | 充电 = 锂离子从正极搬到负极（石墨）；用电再搬回去 | 锂离子电池「摇椅」原理：充电时 Li⁺ 从正极脱出，经电解液嵌入石墨负极；放电反之。电子走外电路 | 〔综〕教科书常识；可引 Goodenough & Park, JACS 2013, 135, 1167 |
| 5 | （v3）锂挤在这一边时，总有一些被「粘」住（表面那层膜慢慢变厚）；被粘住的锂搬不回去 | 石墨负极表面的 SEI 膜由电解液还原生成，持续生长会消耗可循环锂（loss of lithium inventory），这是日常存放老化里容量下降的主因。高 SoC 时石墨嵌锂多、负极电位低，电解液还原加快 | 〔综〕Keil et al., J. Electrochem. Soc. 163 (2016) A1872，「Calendar Aging of Lithium-Ion Batteries I」：容量衰减主要来自可循环锂损失，高 SoC（石墨嵌锂 > 50%）下低负极电位加速锂损失，建议避免高 SoC 存放。**「粘」「膜」是类比 / 简化，画面加注「示意」**；片中不画析锂（那是低温 / 快充的另一机制，留给「天冷掉电」） |
| 6 | 又满又热的时候粘得最快 | 存放老化随温度升高显著加快；100% SoC 存放的影响远大于 80% 以下 | 〔综〕Keil 2016（同 5）；Werner et al., Batteries 7 (2021) 28（100% SoC 存放影响大，80% 以下影响小）https://www.mdpi.com/2313-0105/7/2/28 ；〔官〕Apple：环境温度高于 35 °C 可能永久损害电池容量 https://www.apple.com/batteries/maximizing-performance/ |
| 7 | 能搬的锂少了，电池就不耐用了 | 可循环锂减少 → 可用容量下降（满电也装得少） | 〔综〕同 5 |
| 8 | 夜里插着充一整晚，不少手机会先停在 80%，等你快起床再充满 | iPhone「优化电池充电」：学习充电习惯，预计会长时间连着充电器时，把超过 80% 的那段推迟，在你拔下前充满；目的是减少满电的时间、减少电池损耗。Pixel「自适应充电」、三星「自适应保护电池」做法类似 | 〔官〕Apple https://support.apple.com/en-us/108055 、https://support.apple.com/HT210512 ；〔官〕Google https://support.google.com/pixelphone/answer/6090612 ；三星：〔官〕Samsung「Galaxy Battery protection feature in One UI 6.1」https://www.samsung.com/sg/support/mobile-devices/galaxy-battery-protection-feature-in-one-ui-6-1/ （「自适应」：睡眠时停在约 80%，起床前充满，约需 2 周学习作息）；Apple 另见 https://support.apple.com/en-euro/122502 （优化充电不生效的情况）。字幕说「不少手机」，不点名 |
| 9 | 小提示：边充边打游戏、闷着充，最容易发烫（v2：不说被子） | 充电本身发热；高负载使用再叠加发热；Apple：某些保护壳里充电会产生过多热量，充电时发烫先取下保护壳 | 〔官〕Apple maximizing-performance（同 6）。「闷着充」依据：Apple「充电时发烫，先取下保护壳」（v2 起不说被子） |
| 10 | （不进片，备查）用光了再充更好？ | 不对：锂离子没有记忆效应；深度放电反而让循环寿命变短。「用光再充」来自镍镉电池 | 〔科〕Battery University BU-808、BU-415 https://batteryuniversity.com/article/bu-415-how-to-charge-and-when-to-charge |
| 11 | （v3）另一边锂少了，结构也会塌一点 | 充满时正极脱锂最多、电位最高；高电压 / 高脱锂态下层状氧化物正极（手机常用钴酸锂等）会发生相变、表面重构、过渡金属溶出，损失活性材料；同时正极侧电解液氧化。Keil 2016 认为存放老化里这部分比负极 SEI 次要 | 〔综〕Keil 2016（同 5）；〔综〕Konar, Maiti, Shpigel, Aurbach, Energy Storage Materials 2023，高电压 LiCoO₂ 失效机理综述（O3→H1-3 相变、c 轴收缩、钴溶出、CEI 退化）https://cris.iucc.ac.il/en/publications/reviewing-failure-mechanisms-and-modification-strategies-in-stabi/ 。**钴酸锂充满（约 4.45 V）只脱出约六到七成锂（〔待〕在 Konar 原文里标出页码 / 原句，链接也要核对），不是「掏空」**（审核 11-16）；画面里充满时正极留约三分之一的小球。「塌」是简化，画面加注「示意」 |
| 12 | （v2）SEI「本来就有一层，慢慢变厚」 | SEI 主要在首次充电（化成）时形成，之后随时间和循环缓慢增厚 | 〔综〕同 5；用户 11-16 定画法 |
| 13 | （v3）锂挤在这一边时，总有一些被粘住；再搬一趟，回去的少了 | SEI 在任何电量下都在缓慢增厚，高 SoC 时更快；也随循环增厚（石墨嵌锂膨胀，膜开裂后再长） | 〔综〕Keil 2016（同 5）；审核 11-16 核查 |
| 14 | （v4）充满就不再往里充了，只是一直满着 | 锂离子充电是恒流—恒压，电流降到很小时终止，不做持续涓流 / 浮充（锂离子不能承受过充）；之后电量掉下一点时再补充。所以整晚插着的问题不是「一直往里灌」，而是「一直待在满电」——即 #6 的高 SoC 存放老化 | 〔科〕Battery University BU-409 https://batteryuniversity.com/article/bu-409-charging-lithium-ion （〔待〕对照原文终止电流 / 不浮充的原句）；〔官〕Apple 80% 上限：充到约 80% 停，掉到 75% 再充（同 #8 HT210512，搜索摘要） |
| 15 | （v4）也可以在设置里，限到 80% | iPhone 15 及以后：设置 › 电池 › 电池健康与充电 › 充电优化，可选「80% 上限」（另可在 80–100% 间按 5% 设上限）；Pixel 有 80% 充电上限；三星「最大」保护模式上限 80% | 〔官〕Apple HT210512（搜索摘要）；Google https://support.google.com/pixelphone/answer/6090612 ；三星同 #8。字幕不点名品牌；**老款 iPhone（14 及以前）没有手动上限，只有优化充电**，字幕用「也可以」不说「都可以」 |
