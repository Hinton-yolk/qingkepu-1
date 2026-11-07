# 光互连 04 · 小红书版 · 事实与来源

底稿事实（均衡、Retimer、Redriver、DSP、代价）以 `articles/ep04.md`（@Yihong）为准。下面只列这次新加的事实和类比。

| 口播 | 依据 | 结论 |
|---|---|---|
| 「一半的电，花在修信号上」「光模块里最费电的，往往是 DSP」 | 厂商资料常说 DSP 约占光模块功耗一半（FS：400G 模块 DSP 约 4 W，约占一半）。实测对比：800G 带 DSP 的模块约 16 W，去掉 DSP 的线性驱动（LPO）模块约 8 W（Axiom 实验室测试）。也有来源提醒：精确百分比要看具体型号的器件级拆分 | 「一半左右」成立（量级）；口播说「一半」「往往」，不报具体瓦数；画面耗电条只画「约一半」，标「示意」 |
| 「把 DSP 拿掉，让主芯片自己的 SerDes 来修，光模块的功耗能降到一半左右」 | LPO：光模块里不放 DSP，由交换机 / 主芯片的 SerDes 做均衡；800G LPO 约 8 W，DSP 版约 12–16 W。系统级省电更小（约 25%，Synopsys） | 成立；口播说的是「光模块的功耗」，不说整机 |
| 「修信号的活挪到了主芯片身上，对路况的要求也更高」 | LPO 模块内没有数字信号处理和补偿，依赖主机侧 SerDes；链路预算更紧 | 成立（原文「少放一颗 DSP，也可能只是把工作转给了主芯片」） |
| 「大多数光纤两头，都插着这样一个光模块」 | AI 集群里的光互连目前以可插拔光模块为主，一条链路两端各一个；CPO 等方案正在出现 | 成立；口播用「大多数」 |
| 「处理环节成千上万」 | 万卡级集群的光模块数量以万计（每颗 GPU 对应多个光模块） | 成立（量级） |
| 「音乐 App 的均衡器，和芯片里的均衡是同一个词、同一个道理」 | 两者都是按频率分别调增益：被吞得多的频段补得多（芯片里补的是被铜线削弱的高频成分） | 成立；口播说「同一个词」，画面不展开频率 |
| 「快递转运中心：拆开核对、重新打包再发」 | 类比 Retimer：认出数据、重新打节拍、重新发送 | 类比 |
| 「认糊掉的字条，结合前后文猜中间那个字」 | 类比 DSP 把前后很多个比特一起算（序列检测等） | 类比 |
| 「每秒上千亿个比特」 | 每条通道 112 / 224 Gb/s 级（见 02 FACTS） | 成立 |

来源：
- https://www.fs.com/blog/what-is-the-lpo-transceiver-8.html
- https://www.axiomupgrades.com/spotlight-detail/800G-LPO-vs-DSP-Power-Heat-and-Failure-Differences
- https://www.hengtongglobal.com/info/linear-pluggable-optics-power-savings-103606655.html
- https://origin-www.synopsys.com/articles/direct-drive-electro-optical.html
- https://www.fibermall.com/blog/?p=17327
