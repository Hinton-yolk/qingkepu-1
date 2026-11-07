# 光互连 03 · 小红书改版 · 事实与来源

底稿事实（变弱、拖尾、码间干扰、越快越远越糟、三种办法、损耗 / dB 的写法）以 `articles/ep03.md`（@Yihong）为准，旧版说明 `../output/旁白版说明.md`。下面只列这次新加的事实和类比。

| 口播 | 依据 | 结论 |
|---|---|---|
| 「同样的雷电线，0.8 米跑 40G，2 米只剩 20G」 | Thunderbolt 3 无源线：0.8 m 款标 40 Gbps（StarTech TBLT34MM80CM；NI 787580-0R8「Passive 40 Gbps, 0.8m」）；2 m 无源款标 20 Gbps（NI 785608-02「Passive 20 Gbps, 2m」）。2 m 的 40 Gbps 线是有源线 | 成立。口播说的是**无源**雷电线；画面标签写「无源」以免和有源 2 m 线混淆 |
| 「想又长又快，就得换带芯片的线，或者光纤线」 | 有源 USB4 / 雷电线在线缆里加芯片（retimer / redriver），全速可到 2 m 左右，个别 4 m；更长用光纤线（如 OWC、Corning 的光纤雷电线） | 成立 |
| 「带芯片的线，就是把检修站做进了线里」 | 有源雷电 / USB4 线的芯片是 retimer（重新认出并整理信号再发出）或 redriver（只放大和均衡）。「检修站」在本系列指 retimer / DSP | 成立；口播是类比的说法，不展开 retimer 和 redriver 的区别 |
| HDMI（备用，未进口播） | HDMI 2.1 48 Gbps：认证的无源铜线可靠全速约 3 m，个别到 5 m；更长用有源铜线（约 7.5 m）或光纤 HDMI 线（10–50 m） | 备用例子 |
| 「一条通道已经冲到 200G 这一级」 | OIF CEI-224G 定义每通道 224 Gb/s；IEEE P802.3dj 定义每通道 200 Gb/s 的以太网电接口（见 `../../02-serdes/douyin-split/FACTS.md`） | 成立 |
| 「一些最新的 AI 整机柜，柜里的芯片靠几千根铜缆连在一起」 | 某 72 颗 GPU 整机柜的柜内互连用约 5,000 根直连铜缆，总长约 2 英里；厂商称比用光模块每柜省约 20 kW（SemiAnalysis；ServeTheHome 转述厂商发布会）。不同来源的根数口径不一 | 成立；口播只说「几千根」，不点名 |
| 「在楼道里喊人，离得越远声音越小」 | 类比：变弱（损耗） | 类比，口播用「就像」 |
| 「空车库里说话，回音把字糊成一片」 | 类比：拖尾 / 码间干扰（文章原用「长走廊喊话、余音没散」） | 类比 |
| 「语速翻倍，一个回音盖住两个字」 | 类比：比特时间减半、脉冲拖尾长度不变 → 影响的比特数翻倍（文章原文） | 类比 |
| 「认错一个，就是照片花了一块，消息里冒出一个乱码」 | 示意：实际链路有纠错（FEC）和重传，单个比特错不一定直接变成乱码；这里是说明「认错会让内容出错」 | 示意，画面不写成实测 |
| 「一辆车说能跑 200 公里每小时：在高速上，还是山路上？」 | 类比：速度指标要带测试条件（损耗、频率）才能比较 | 类比 |

来源：
- https://etesters.com/product/8607AC40-2D7F-44AD-9C59-4AC35EC8CCD9/thunderbolt-3-type-c-cable-passive-40-gbps-5a-0-8m
- https://etesters.com/product/32265730-2042-4E67-8F92-C50A24A3DCB1/thunderbolt-3-type-c-cable-passive-20-gbps-5a-2m
- https://www.lambda-tek.com/StarTech-com-TBLT34MM80CM-sh/B43520931
- https://plugable.com/en-ca/blogs/news/what-s-the-difference-between-active-and-passive-thunderbolt-cables
- https://www.techadvisor.com/test-centre/accessories/best-thunderbolt-4-usb4-cables-3802567/
- https://www.newnex.com/firenex-ulink-40g.php
- https://www.cablematters.com/Blog/HDMI/how-do-active-hdmi-cables-work
- https://bzbgear.com/blog/hdmi-cables-explained-copper-vs-fiber/
- https://newsletter.semianalysis.com/p/nvidias-optical-boogeyman-nvl72-infiniband
- https://www.servethehome.com/this-is-the-nvidia-dgx-gb200-nvl72/
