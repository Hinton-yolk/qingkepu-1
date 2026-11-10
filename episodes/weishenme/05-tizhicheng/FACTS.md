# FACTS · 体脂秤怎么知道你有多少脂肪？

| 说法（片中） | 依据 | 来源 |
|---|---|---|
| 脚下的金属片在给你通电，电很弱，感觉不到 | 生物电阻抗法（BIA）：家用秤一般用 50 kHz 的交流电，从一只脚的电极进、另一只脚出。电流大小因型号而异，Tanita 手册写 90 µA、100 µA、500 µA 等，都在 1 毫安以下。片中不写数字 | [Tanita SC-240 技术说明（50 kHz、90 µA）](https://www.manualslib.com/manual/798231/Tanita-Sc-240.html?page=26)；[Tanita BF-689（50 kHz、500 µA）](https://www.manualslib.com/manual/677058/Tanita-Bf-689.html?page=10)；[Live Science](https://www.livescience.com/health/how-do-smart-scales-measure-body-composition-and-how-accurate-are-they) |
| 肌肉里水多，电好走；脂肪里水少，电难走 | 组织的导电性取决于含水量；去脂组织的含水量相当稳定，约 73% | [Wang et al. 1999, AJCN 69(5):833–841](https://pubmed.ncbi.nlm.nih.gov/10232629)；[Kyle et al. 2004, Clin Nutr 23:1226–1243（ESPEN BIA 指南 I）](https://pubmed.ncbi.nlm.nih.gov/15380917) |
| 体脂秤其实是一台测电阻的表 | 测的是身体的阻抗（片中简化为「电阻」：50 kHz 下以电阻为主，另有一小部分容抗） | Kyle 2004 |
| 还要知道你的身高、年龄、性别 | 估算公式一般用「身高² ÷ 电阻」加上体重、年龄、性别，先算去脂体重，体脂 = 体重 − 去脂体重；公式按人群拟合，所以是估算 | [Kyle 2004](https://pubmed.ncbi.nlm.nih.gov/15380917)；[Frontiers in Nutrition 2022（含身高²/电阻、体重、性别、年龄的公式示例）](https://www.frontiersin.org/journals/nutrition/articles/10.3389/fnut.2022.820736/pdf) |
| 喝了水、出了汗，数字会变 | 读数受体内水分影响，脱水的影响最大；进食、运动的影响研究结论不一（2021 年一项研究发现影响很小）。片中只说「水变了，数就变」，不夸大 | [Kyle et al. 2004（ESPEN BIA 指南 I）](https://pubmed.ncbi.nlm.nih.gov/15380917)；[BMC Public Health 2021](https://doi.org/10.1186/s12889-021-10552-y)（反面证据：进食、运动影响很小）；[Live Science](https://www.livescience.com/health/how-do-smart-scales-measure-body-composition-and-how-accurate-are-they) |
| 装心脏起搏器的人别用体脂功能 | Tanita、Omron、Philips、Withings、iHealth 的说明书 / 支持页都写明：装起搏器或其他植入式电子设备的人不要使用（部分品牌可只用称重模式） | [Tanita BC-G01 手册](https://www.manualslib.com/manual/1146253/Tanita-Bc-G01.html?page=4)；[Omron HBF-516](https://www.manualslib.com/manual/951905/Omron-Hbf-516.html?page=4)；[Philips](https://www.usa.philips.com/c-e/heart-health/devices/philips-body-analysis-scale/getting-started/when-can-i-not-use-the-scale-are-there-contraindications.html)；[Withings](https://support.withings.com/hc/en-us/articles/218438708-Body-Frequently-asked-questions-about-safety) |
| （正文用，片中不讲）脚踩式秤的电主要在两条腿之间走（**仅单一来源**） | 脚对脚的电流只在两腿之间的回路里走，上半身的脂肪靠公式推 | [Acibadem: Smart scales and bioimpedance](https://acibademinternational.com/blog/smart-scales-and-bioimpedance-how-accurate-is-your-body-fat-reading/) |

| 它先按正常含水量来算；水一少，就会被算成脂肪多 | BIA 公式的前提是去脂组织含水约 73% 这一「常数」；含水异常（脱水、水肿）时结果不可靠。脱水时阻抗升高，体脂被高估（2021 年研究：脱水是误差最大的因素）。多频秤能单独估一部分水，但同样假设含水正常，所以片中不说「分不清」，只说「默认正常」 | [Wang et al. 1999, AJCN 69(5):833–841](https://pubmed.ncbi.nlm.nih.gov/10232629)；[Kyle et al. 2004, ESPEN BIA 指南 II, Clin Nutr 23:1430–1453](https://pubmed.ncbi.nlm.nih.gov/15556267)；[BMC Public Health 2021](https://doi.org/10.1186/s12889-021-10552-y) |
| 所以电越难走，脂肪一般就越多 | 「一般」：电阻还跟身高、腿长、腿粗有关，同样体型、含水正常时，电阻大才对应脂肪多；公式里用「身高² ÷ 电阻」正是为此 | [Kyle et al. 2004, ESPEN BIA 指南 I](https://pubmed.ncbi.nlm.nih.gov/15380917) |

| （评论回复）八电极把上半身也测进去，有研究里和 DEXA 稍微更一致 | Tanita 研究：八电极与 DEXA 相关 r = 0.87，四电极 r = 0.82；**仅一项研究、仅读到摘要、专业分析仪**，所以只说「稍微」 | [Pietrobelli et al., EJCN 2004](https://www.nature.com/articles/1601993.pdf) |
| （评论回复）两台秤的公式不一样，绝对值对不上；同一台看趋势 | 不同设备的公式不能互换，个体误差大；同一人的相对排序 / 变化较稳定 | [J Transl Med 2024](https://translational-medicine.biomedcentral.com/counter/pdf/10.1186/s12967-024-05272-x.pdf)；[J Electr Bioimpedance 2018](https://doaj.org/article/99e9cfd1dacc41d9ac891ea50f382c76)；[Measurement Toolkit](https://measurement-toolkit.org/anthropometry/objective-methods/bioelectric-impedence-analysis) |
| （评论回复）要光脚，穿袜子体脂测不准 | 说明书要求光脚站在电极上；有品牌说明书写明穿袜子 / 丝袜会产生测量误差 | [Tanita BC-418](https://www.notice-facile.com/en/manual/1271279/tanita+bc-418)；[Omron](https://omronhealthcare.com/scales)；[示例说明书](https://manualedistruzioni.it/aws/scale/msl-180/user-manual/2c75j) |

未核实、不使用：脚踩式秤「个人误差 4–8 个百分点」（只见于博客转述）。

## 画面上的简化（片中不写字，2026-11-09 制作时补）

| 画面 | 实际情况 |
|---|---|
| 电流从左脚前掌那块电极片进去，沿左腿上去、过腰、沿右腿下来，从右脚前掌那块出来 | 四片电极里一对通电流、另一对量电压（哪一对因型号而异，片中不讲）；电流在两条腿之间的回路里走（「电只走两条腿」按用户决定不进片子） |
| 「电越难走」画成往上走的电荷变少、变慢 | 示意。秤通的是一个恒定的、很小的交流电，电阻越大，量到的电压越高；片中只说「电好走 / 难走」 |
| 「脂肪越多」画成小腿切面上的脂肪层往里变厚、肌肉变小（小腿略变粗），旁边一块表的指针往上走 | 示意。电主要从含水多的去脂组织里走，同样一条腿，导电的部分越少，电阻越大；表盘上不标数字 |
| （v2）从切面里「拉出」一块肌肉、一块脂肪，两端各接同样的电极，各配一块表：肌肉里电荷连成一条线快速流过、表低；脂肪里电荷一颗颗挪、经常停住、表高 | 示意性的对比实验，不是真的取样；两块大小相同，所以比的是材料本身（导电好不好），表盘不标数字 |
| （v2）两条小腿并排、通同样的电：右边脂肪层厚，表盘读数更高 | 示意。同样的腿围，脂肪占比越高，导电的去脂组织越少，测到的电阻越大 |
| （v3）第二次钻进小腿：表盘上一条「正常含水」刻度；水滴变少时指针越过刻度往「难走」偏，读数里的体脂率变高，切面里多出一圈淡黄色带，内外两边墨色虚线（v3.1；秤「以为」的脂肪） | 示意。这圈带表示秤按「含水正常」的前提把多出来的电阻算成了脂肪，真实脂肪层没有变；读数 22.4 → 26.8 % 是示意数值 |
| （v3）卡片：体重标「秤称」，身高、年龄、性别标「你填」 | 体重由秤自己称出；身高、年龄、性别来自 App 里填的资料（公式里用到的变量见上表「还要知道你的身高、年龄、性别」） |
| 小腿横截面：外圈淡黄脂肪、里面红色肌肉（几条筋膜线）、浅灰的胫骨和腓骨 | 解剖简化：只画两根骨头和四五条肌间隔 / 筋膜线，比例按小腿中段大致画 |
| 水 = 几颗水滴；喝水后变多、出汗后变少 | 示意，不是含水量的比例 |
| 读数 58.6 kg、体脂率 22.4 %，以及跳动的 21.6 / 23.1 / 22.0 / 22.7 %、早晚的 22.4 / 20.9 %、水少时的 26.8 % | 示意数值，不对应任何真人或型号；幅度没有来源（26.8 的跳幅偏大，审核建议缩到 2–3 个百分点，待用户定） |
| 显示屏上的数字从镜头看是正的 | 真秤的显示屏朝向站在上面的人，从前方看本该是倒的；倒着的「22.4」看着像「h22」，所以画成正的（艺术处理，见 notes.md） |
