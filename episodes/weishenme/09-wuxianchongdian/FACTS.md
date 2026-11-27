# EP.09 无线充电 · FACTS

来源等级：〔规〕标准 / 规范原文或其官方摘要；〔厂〕厂商资料（立场可能有偏）；〔百〕百科 / 媒体；〔估〕自己的估算。
**所有条目在节点 ① 交最强模型做事实核查。**

| # | 事实（片中怎么说） | 片中用法 | 来源 |
|---|---|---|---|
| 1 | 手机无线充电主流是 Qi 标准（WPC 无线充电联盟），原理是**电磁感应**：充电板线圈通交流电产生交变磁场，手机里的线圈感应出交流电 | 第 4 段整体 | 〔百〕Wikipedia「Qi (standard)」；〔厂〕DigiKey「Inductive Versus Resonant Wireless Charging」 |
| 2 | Qi 基础 / 扩展功率档（BPP / EPP）工作频率约 110–205 kHz（资料下限有 87 / 100 / 105 / 110 kHz 几种写法）；Qi2 磁吸档（MPP）为 360 kHz → 片中说「每秒十几万到几十万次」（110–360 kHz = 每秒 11–36 万个周期） | 小字「每秒十几万到几十万次 · 慢放示意」 | 〔厂〕DigiKey 同上；〔百〕Wikipedia；MPP 360 kHz：〔百〕Spilma「Qi, Qi2 wireless charging certification」、Tinkervault「Qi and Qi2 standards」（二手资料，WPC 规范原文未见）；〔估〕换算 |
| 3 | 两个线圈之间隔着外壳，没有任何导电接触 | 「板子和手机，其实没碰到」 | 由原理直接得出（感应耦合）〔百〕Wikipedia |
| 4 | 线圈要靠得近、对得正，耦合才好；Qi 设备通常要求发射、接收线圈对得比较准 | 「为什么要放正」段 | 〔百〕Wikipedia；〔厂〕DigiKey。**不放具体毫米数**（没找到可靠来源） |
| 5 | Qi2 的磁吸功率规范（MPP）基于苹果贡献的 MagSafe，用一圈磁铁让手机和充电器对正 | 「背后有一圈磁铁，一贴就正」，小字「Qi2 磁吸」 | 〔百〕Macworld / MacRumors 关于 Qi2 MPP 的报道（2023-01）；WPC 公告待补原文链接 |
| 6 | 手机和充电板**通过同一对线圈通信**：接收端改变自己的负载（负载调制 / ASK），发射端从线圈上的电压、电流包络读出数据包（控制误差包：「多一点 / 少一点」） | 「手机就用这圈线回话」「多一点、少一点」 | 〔规〕WPC Qi v1.3 Communications Physical Layer（PDF）；〔厂〕TI BQ51013C 数据手册「通信调制器」 |
| 7 | 充电板先发短促的「探测」（ping），收不到合规的回复就不开始送电 | 「板子会先问一声」「没有回话，就不送电」 | Qi 四个阶段：选择、探测（ping）、识别与配置、送电；数字 ping 收不到合规的信号强度包就不进入后续阶段、不送电。〔百〕All About Circuits「How Does the Qi Wireless Charging Standard Work」；〔专利〕US 9866073 等对 Qi 流程的描述。规范原文未见 |
| 8 | 金属异物（硬币、钥匙）在交变磁场里会因涡流发热；Qi 规定了异物检测（FOD）防止这种情况 | 钥匙那一拍；小提示「摘掉金属指环扣」 | 〔规〕WPC Qi v1.3 FOD（PDF）；IEC 63563-7:2025（Qi 2.0 Part 7: FOD）；〔厂〕Avnet 文章 |
| 9 | 手机背面用玻璃而不是整块金属，一个原因是金属会产生涡流、消耗并发热；玻璃几乎不损耗磁场 | 可选小字（目前没进片） | 〔厂〕Corning「Glass is Better for Wireless Charging」（玻璃厂商，立场有偏） |
| 10 | 手机收到的是交流电，要经过整流变成直流，再由充电管理芯片充进电池 | 小字「交流 → 直流」 | 〔厂〕TI BQ51013C 数据手册（接收芯片集成同步整流器，输出直流给充电电路） |

## 类比 / 示意（片中要标注）
- 磁场的颜色、磁力线的样子：**示意**，磁场看不见，画面加注「颜色为示意」。
- 电流「来回换方向」用慢放演示：加注「慢放示意」。
- 「说话」是比喻：实际是改变负载被对方读出。小字说明。

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
- https://www.avnet.com/americas/resources/article/watch-for-these-2-problems-in-your-qi-wireless-charging-project/
