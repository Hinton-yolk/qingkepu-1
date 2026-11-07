# 三条抖音拆解版口播（第四稿：≤ 55 秒，每条一个知识点）：python3 make_script.py → script_s1.json / s2 / s3
# 每句：id、text（口播）、sub（关键点字幕）、big（开头两句的同步大字）、seg（open / explain / reveal / end）、reuse（一字不差的旧录音）、say（TTS 用的读法，缺省同 text）
import json
S1 = [
 ('w01', 'AI 芯片之间，', None, 'AI 芯片之间，', 'open', None),
 ('w02', '最快的路，只修几条。', None, '最快的路，只修几条。', 'open', None),
 ('w03', '就像 4 根线的 USB，跑赢了 25 针的老打印机线。', '4 根线，跑赢 25 针', None, 'open', None),
 ('w04', '路少了，凭什么更快？', None, None, 'open', None),
 ('w05', '几十条路一起送，有个前提：每一批都得一起到，对面才拼得出数据。', '每一批都得一起到', None, 'explain', None),
 ('w06', '慢的时候不难。可一快，一批紧挨一批，留给「一起到」的时间越来越短。', '越快，留给「一起到」的时间越短', None, 'explain', None),
 ('w07', '这时哪条路长了一点点，那一位就晚到一步，混进下一批：整批全错。', None, None, 'reveal', None),
 ('w08', '路越多，越难条条一样长。', None, None, 'reveal', None),
 ('w09', '所以干脆只修几条路，排成一列跑：不用等谁，一路提速。', '排成一列，一路提速', None, 'reveal', None),
 ('w10', '一句话带走：', None, None, 'end', 'a19'),
 ('w11', '速度一高，「一起到」比「路多」更难。', None, None, 'end', None),
 ('w12', '下一条：连续五个 1，芯片怎么数清？', None, None, 'end', None),
]
S2 = [
 ('v01', '你刷的每条视频，', None, '你刷的每条视频，', 'open', 'b01'),
 ('v02', '都是一串 0 和 1。', None, '都是一串 0 和 1。', 'open', 'b02'),
 ('v03', '可在线上，连续五个 1 就是一条直线：四个，还是五个？', '连续五个 1 = 一条直线', None, 'open', None),
 ('v04', '数错一个，数据就错了。而 AI 芯片每秒要这样数上千亿个，没人给它打拍子。', '每秒上千亿个，没人打拍子', None, 'open', None),
 ('v05', '数清的关键，是知道每一位有多长：这就是节拍。', None, None, 'explain', None),
 ('v06', '它靠的是跳变：每次 0 变 1、1 变 0，就对一次表。', '每次跳变，对一次表', None, 'explain', None),
 ('v07', '早了往后拨，晚了往前拨，几下就锁住了。', None, None, 'reveal', None),
 ('v08', '然后在每一位正中间看一眼：五个，不是四个。', None, None, 'reveal', None),
 ('v09', '可一长串全是 1，没有跳变，节拍就会跑偏。', '没有跳变，节拍跑偏', None, 'reveal', None),
 ('v10', '所以发出前先把数据打乱，收到再还原。', '先打乱，再还原', None, 'reveal', None),
 ('v11', '一句话带走：', None, None, 'end', 'a19'),
 ('v12', '芯片不是在看 0 和 1，是在听节拍。', None, None, 'end', None),
 ('v13', '下一条：芯片说速度翻倍，该问哪三句？', None, None, 'end', None),
]
S3 = [
 ('u01', 'AI 芯片的新闻，', None, 'AI 芯片的新闻，', 'open', 'c01'),
 ('u02', '天天在说速度翻倍。', None, '天天在说速度翻倍。', 'open', 'c02'),
 ('u03', '可这就像汽车说最高时速 300，没说是在什么路上跑的。', '最高时速 300，在什么路上？', None, 'open', 'c03'),
 ('u04', '看懂这类新闻，先问三个问题。', None, None, 'open', 'z04'),
 ('u05', '第一问：在什么路上跑出来的？', None, None, 'explain', 'z05'),
 ('u06', '同样写着 224G，一个能推过一米长的铜缆，一个只跑几厘米。', '同样 224G：一米，还是几厘米', None, 'explain', 'c03b'),
 ('u07', '第二问：每传一个比特，花多少电？', None, None, 'explain', 'z08'),
 ('u08', '每个比特的电降不下来，速度翻倍，电费也跟着翻倍；几万颗芯片一起跑，这就是真金白银。', '速度翻倍，电费也翻倍', None, 'explain', None),
 ('u09', '第三问：是 PPT 上的速度，还是真芯片测出来的？', None, None, 'reveal', None),
 ('u10', '做出来、测出来，才算数。', None, None, 'reveal', None),
 ('u11', '一句话带走：', None, None, 'end', 'a19'),
 ('u12', '下次看到速度翻倍，先问：什么路？多少电？测过没有？', None, None, 'end', None),
 ('u13', '下一条：信号上路以后，为什么会越跑越模糊？', None, None, 'end', 'z14'),
]
SAY = {'w03': '就像四根线的 USB，跑赢了二十五针的老打印机线。', 'w06': '慢的时候不难。可一快，一批紧挨一批，留给一起到的时间越来越短。', 'w11': '速度一高，一起到，比路多更难。'}
if __name__ == '__main__':
    import re
    for n, S in (('s1', S1), ('s2', S2), ('s3', S3)):
        json.dump([dict(id=i, text=t, sub=u, big=b, seg=g, reuse=r, say=SAY.get(i, t)) for i, t, u, b, g, r in S], open(f'script_{n}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(n, len(S), 'lines; new TTS bytes', sum(len(SAY.get(i, t).encode()) for i, t, u, b, g, r in S if not r))
