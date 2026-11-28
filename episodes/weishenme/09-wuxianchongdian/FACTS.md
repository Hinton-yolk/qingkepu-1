# EP.09 无线充电 · FACTS

来源等级：〔规〕标准 / 规范原文或其官方摘要；〔厂〕厂商资料（立场可能有偏）；〔百〕百科 / 媒体；〔估〕自己的估算。
**所有条目在节点 ① 交最强模型做事实核查。**

| # | 事实（片中怎么说） | 片中用法 | 来源 |
|---|---|---|---|
| 1 | 手机无线充电主流是 Qi 标准（WPC 无线充电联盟），原理是**电磁感应**：充电板线圈通交流电产生交变磁场，手机里的线圈感应出交流电 | 第 4 段整体 | 〔百〕Wikipedia「Qi (standard)」；〔厂〕DigiKey「Inductive Versus Resonant Wireless Charging」 |
| 2 | Qi 基础 / 扩展功率档（BPP / EPP）工作频率约 110–205 kHz（资料下限有 87 / 100 / 105 / 110 kHz 几种写法）；Qi2 磁吸档（MPP）为 360 kHz → 片中说「每秒十几万到几十万次」（110–360 kHz = 每秒 11–36 万个周期） | 小字「每秒来回十几万到几十万次 · 慢放示意」 | 〔厂〕DigiKey 同上；〔百〕Wikipedia；MPP 360 kHz：〔测试实验室〕GRL「Qi2 wireless charging standards evolution」（BPP / EPP 87–205 kHz，MPP 360 kHz；Qi2 先以 BPP 128 kHz 握手再切到 360 kHz）；〔百〕Spilma「Qi, Qi2 wireless charging certification」、Tinkervault「Qi and Qi2 standards」（二手资料，WPC 规范原文未见）；〔估〕换算 |
| 3 | 手机压在充电板上，但两边电路之间隔着外壳，没有任何导电接触（电荷不穿过间隙，过去的是变化的磁场 / 能量） | 「没有一根线，连着它们」「电没走过去，过去的是磁」 | 由原理直接得出（感应耦合）〔百〕Wikipedia |
| 4 | 线圈要靠得近、对得正，耦合才好；Qi 设备通常要求发射、接收线圈对得比较准 | 「为什么要放正」段 | 〔百〕Wikipedia；〔厂〕DigiKey。**不放具体毫米数**（没找到可靠来源） |
| 5 | Qi2 的磁吸功率规范（MPP）基于苹果贡献的 MagSafe，用一圈磁铁让手机和充电器对正 | 「所以有的手机和充电器，各有一圈磁铁」，小字「Qi2 磁吸」（不少安卓机标 Qi2 Ready、本身没有磁铁，要靠磁吸壳） | 〔百〕Macworld / MacRumors 关于 Qi2 MPP 的报道（2023-01）；WPC 公告待补原文链接 |
| 6 | 手机和充电板**通过同一对线圈通信**：接收端改变自己的负载（负载调制 / ASK），发射端从线圈上的电压、电流包络读出数据包（控制误差包：「多一点 / 少一点」） | 「手机就用这圈线回话」「多一点、少一点」 | 〔规〕WPC Qi v1.3 Communications Physical Layer（PDF）；〔厂〕TI BQ51013C 数据手册「通信调制器」 |
| 7 | 充电板先发短促的「探测」（ping），收不到合规的回复就不开始送电 | 「板子会先问一声」「没有回话，就不送电」 | Qi 四个阶段：选择、探测（ping）、识别与配置、送电；数字 ping 收不到合规的信号强度包就不进入后续阶段、不送电。〔百〕All About Circuits「How Does the Qi Wireless Charging Standard Work」；〔专利〕US 9866073 等对 Qi 流程的描述。规范原文未见 |
| 8 | 金属异物（硬币、钥匙）在交变磁场里会因涡流发热；Qi 规定了异物检测（FOD）防止这种情况 | 钥匙那一拍；小提示「摘掉厚壳和金属指环」 | 〔规〕WPC Qi v1.3 FOD（PDF）；IEC 63563-7:2025（Qi 2.0 Part 7: FOD）；〔厂〕Avnet 文章 |
| 9 | 手机背面用玻璃而不是整块金属，一个原因是金属会产生涡流、消耗并发热；玻璃几乎不损耗磁场 | 可选小字（目前没进片） | 〔厂〕Corning「Glass is Better for Wireless Charging」（玻璃厂商，立场有偏） |
| 10 | 手机收到的是交流电，要经过整流变成直流，再由充电管理芯片充进电池 | 小字「交流 → 直流」 | 〔厂〕TI BQ51013C 数据手册（接收芯片集成同步整流器，输出直流给充电电路） |
| 11 | 苹果官方：iPhone 和充电器之间不要放东西；厚壳、金属壳会导致不充或变慢；金属物品会变热或干扰充电 | 小提示「充得慢、发烫？摘掉厚壳和金属指环，再放正一点」 | 〔厂〕Apple「How to wirelessly charge your iPhone」；Apple「Important safety information for iPhone」 |
| 12 | 线圈错位 → 穿过接收线圈的磁通变少、耦合系数下降；Qi 闭环功控会让发射端加大驱动补回功率，代价是效率下降、发热增加；补不回来或过热降功率时才变慢 / 停 | 「穿过手机这圈的磁就少了」「板子得更使劲，还容易发烫」 | 〔厂〕WECENT 台架数据（15 W 充电器错位 5 mm，效率约 81% → 63%，线圈约 35 °C → 50 °C 以上；**单一厂商，立场有偏，数字不上屏**）；功控机制见 #6。**待补：TI / Würth 应用笔记或论文** |
| 13 | 平面线圈的磁场集中在线圈正上方（轴线附近），在外缘掉头回绕；发射线圈下面、接收线圈上面各有一层铁氧体片，引导磁通并屏蔽 | 「磁都挤在线圈正上方」；画面铁氧体片 | 〔厂〕Würth Elektronik ANP014「Wireless Energy Transmission Coils as Key Components」 |

## 类比 / 示意（片中要标注）
- 磁场的颜色、磁力线的样子：**示意**，磁场看不见，画面加注「颜色为示意」。
- 电流「来回换方向」用慢放演示：加注「慢放示意」。
- 「说话」是比喻：实际是手机改变自己的负载（ASK 负载调制），板子从自己线圈的电流 / 电压幅度变化里读出。小字「负载调制 · 示意」。
- 收发两边电流的相位不画死（两侧有谐振电容，并非正好反相）。
- 「问一声」不画外扩波纹：100–360 kHz 是近场耦合，不是辐射。
- 外壳画成玻璃质感是画风，片中字幕说「外壳」。

## 链接
- https://en.wikipedia.org/wiki/Qi_(standard)
- https://www.digikey.com/es/articles/inductive-versus-resonant-wireless-charging
- https://www.wirelesspowerconsortium.com/media/mxdjdezs/qi-v13-comms-physical.pdf
- https://www.wirelesspowerconsortium.com/media/klfjiwfh/qi-v13-fod.pdf
- https://standards.iteh.ai/catalog/standards/iec/2aebf0ed-d5ee-4986-93cb-af6beec820d2/iec-63563-7-2025
- https://www.ti.com/document-viewer/BQ51003/datasheet/communication-modulator-lit69829021
- https://www.macrumors.com/2023/01/03/qi2-wireless-charging-standard-gains-magsafe/
- https://www.macworld.com/article/1445626/magsafe-iphone-qi2-wireless-charging-standard-magnetic-power-profile.html
- https://www.corning.com/gorillaglass/worldwide/en/glass-is-better-for-wireless-charging.html
- https://www.spilma.com/en/guides/qi-wireless-power-consortium
- https://www.tinkervault.com/wireless-charging-protocols/qi-wireless-charging
- https://www.allaboutcircuits.com/news/how-does-qi-wireless-charging-standard-work/
- https://www.graniteriverlabs.com/en-us/technical-blog/qi2-wireless-charging-standards-evolution
- https://support.apple.com/en-us/ht208078
- https://support.apple.com/en-kz/guide/iphone/iph301fc905/18/ios
- https://www.we-online.com/components/media/o109042v410%20ANP014_Wireless%20Energy%20Transmission%20Coils%20as%20Key%20Components.pdf
- https://www.gdwecent.com/?p=21693
- https://www.avnet.com/americas/resources/article/watch-for-these-2-problems-in-your-qi-wireless-charging-project/

## v4 新增
| # | 事实 | 片中用法 | 来源 |
|---|---|---|---|
| 14 | 法拉第电磁感应：磁铁插入 / 拔出线圈时，线圈里感应出电流，方向相反；磁铁不动就没有电流。多匝线圈 + 强磁铁可以点亮 LED（中学常见演示）。片中用两颗反向并联的 LED，插入亮一颗、拔出亮另一颗，以显示方向 | 「磁铁插进线圈，灯就亮一下」「磁一变，线圈里就有电」 | 法拉第定律（任一大学物理教材）；〔百〕Wikipedia「Faraday's law of induction」 |
| 15 | 电池充电需要直流；接收端的整流电路（二极管 / 同步整流）把线圈里的交流变成单向的电，再经稳压、充电管理送进电池 | 「电池只收单向的，芯片把它理顺」，小字「整流 · 示意」 | 〔厂〕TI BQ51013C 数据手册（同步整流器）；见 #10 |
| 16 | 金属在交变磁场里会感应出闭合的涡流，涡流在金属电阻上发热 | 「金属里也会感应出电，在里面打转」「这些电，全变成了热」，小字「涡流」 | 〔规〕WPC Qi v1.3 FOD（金属异物发热）；〔厂〕Corning（涡流发热）；见 #8、#9 |
| 17 | 功率损耗型异物检测：接收端定期报告收到的功率（Received Power Packet），发射端用自己送出的功率减去它，估算「不明损耗」；超过阈值就判定有金属异物，降功率或停止送电 | 「板子一算：送出的比收到的多，就降速、甚至停充」，小字「异物检测」 | 〔规〕WPC Qi v1.3 Foreign Object Detection（PDF，见链接）；IEC 63563-7:2025。**待核：引规范原文段落** |
| 18 | 热成像配色（蓝 → 黄 → 红）只是示意温度高低，不对应具体温度 | 「热成像 · 示意」 | 示意，无数字 |

## v5 新增 / 修正（2026-11-28）
| # | 事实 | 片中用法 | 来源 |
|---|---|---|---|
| 19 | 线圈错位 → 两圈耦合变差，大部分磁通不穿过接收线圈（漏磁变多）→ 接收功率和效率下降、充得慢；Qi2 用磁铁对正以减少错位损失 | 「磁从旁边漏走了，手机接到的就少」，小字「漏磁」 | 〔百〕Android Authority「wireless charging battery health」（Qi2 磁铁减少错位损失；错位时效率可低至约 50%）；〔厂〕WECENT 台架数据（见 #12，数字不上屏） |
| 20 | 无线充电效率低于有线（专家估计：有线约 95%，无线约 70–80%；对不准时更低）；没传过去的能量变成热 | 「隔空传过去，总会损失一些」「损失的变成了热」，小字「线圈电阻 · 漏磁」 | 〔百〕TechRadar「Does wireless charging kill your phone's battery?」；Android Authority 同上；iFixit「Wireless charging: trading efficiency for convenience」；Engadget。数字不上屏 |
| 21 | 手机的接收线圈贴在机身背面、电池背后（线圈 + 铁氧体片叠在电池和后盖之间） | 「就贴在电池背后」 | 〔拆解〕iFixit iPhone 8 拆解（https://www.ifixit.com/Guide/iPhone+8+Teardown/97481）：打开玻璃后盖后第一眼看到的就是充电线圈，X 光图里线圈盖住了下面的电池和主板；iPhone 8 Plus 拆解（https://www.ifixit.com/Guide/iPhone+8+Plus+Teardown/97482）：电池胶条改为四条，以免拆电池时伤到线圈。即叠放顺序为后盖 → 线圈 → 电池 |
| 22 | 金属在交变磁场里感应出涡流，涡流产生的磁场与原磁场方向相反，抵消、挡住一部分磁通 → 接收端拿到的变少；被挡下的能量在金属里变成热 | 「金属里感应出电，反过来把磁挡住」「挡下来的，在金属里变成热」 | 楞次定律（大学物理）；〔专利〕US10181757B2（金属结构中的涡流产生反向磁场，使发射线圈失谐、效率下降） |
（#15「交流 → 直流」一段已删，事实保留备查。）
