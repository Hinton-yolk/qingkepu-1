# FACTS — 屏上每一句科学陈述的出处

| 屏上说法 | 依据 | 来源 |
|---|---|---|
| 手机里的陀螺仪和加速度计在一颗芯片里（6 轴 IMU） | ST LSM6DSO：3 轴加速度计 + 3 轴陀螺仪的 iNEMO 惯性测量单元 | [ST LSM6DSO 产品页](https://www.st.com/en/mems-and-sensors/lsm6dso.html)、[数据手册](https://xdevs.com/doc/STM/lsm6dso.pdf) |
| 芯片约 3 × 2.5 mm，"比一粒米还小" | LSM6DSO 封装 LGA-14L 2.5 × 3.0 × 0.83 mm；一粒米约 6–7 × 2.5–3 mm（常识量级，画面中按 6.5 × 2.6 mm 绘制） | 同上 |
| 陀螺仪不旋转，是一块被驱动振动的硅质量块；转动时科里奥利力把它推向垂直方向，梳齿电容变化被读出 | MEMS 振动陀螺仪的标准原理：梳齿静电驱动质量块沿一轴振动；转动时科里奥利力在检测轴上产生位移，由交叉梳齿电容读出 | [Berkeley EE245 作业（驱动/检测模态示例）](https://inst.eecs.berkeley.edu/~ee245/fa11/homework/hw7.ee245-f11.v5.pdf)、[US7827864 专利](https://patents.google.com/patent/US7827864)、[COMSOL MEMS 陀螺仪模型](https://doc.comsol.com/6.4/doc/com.comsol.help.models.mems.gyroscope_mixed_formulation/models.mems.gyroscope_mixed_formulation.pdf) |
| "每秒来回振动上万次" | 驱动模态典型 5–25 kHz，常见约 10–20 kHz（即每秒 1–2 万次以上） | 同上专利与课程材料；具体型号未公开驱动频率，故只说"上万次" |
| "推得越狠，说明转得越快" | 科里奥利力 F = 2m v × Ω，与角速度成正比 | 物理定义 |
| 加速度计"只认哪边是下"、屏幕旋转依赖它 | Android 系统设置 `ACCELEROMETER_ROTATION`："Control whether the accelerometer will be used to change screen orientation" | [Android Settings.System.ACCELEROMETER_ROTATION](https://learn.microsoft.com/zh-tw/dotnet/api/android.provider.settings.system.accelerometerrotation?view=net-android-37.0) |

画面中的示意（标注"慢放演示"）：振动频率放慢到 2 Hz、位移放大到可见，均为示意，不是实际尺度。
芯片内部的结构布局为通用示意，不对应任何具体品牌型号。
