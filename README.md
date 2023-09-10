# 轮式格斗车主控程序

------
<!-- TOC -->

* [轮式格斗车主控程序](#轮式格斗车主控程序)
    * [简述](#简述)
    * [2023国赛实际配置](#2023国赛实际配置)
    * [基础运作逻辑](#基础运作逻辑)
    * [传感器默认配置](#传感器默认配置)

<!-- TOC -->
------

## 简述

本主控程序是在博创的标准人工智能控制器上开发的，这个控制器的官方资料可以在仓库[Reference-Material](https://github.com/Kazu-Kusa/Reference-Material/tree/main/TOTURIAL)
查看，同时程序设计的对应模型版本为[BattleBot_Kazu_Models_v0.8.7.8](https://github.com/Kazu-Kusa/BattleBot_Kazu_Models/releases/tag/v0.8.7.8)

注：由于硬件原因和开发周期的原因，理想的计划的传感器数量（18）并没有被实现

------

## 2023国赛实际配置

- **主控**

*

*

人工智能控制器（实质上是一块带扩展板的树莓派），详细说明见[人工智能版控制器硬件说明.pdf](https://github.com/Kazu-Kusa/Reference-Material/blob/main/TOTURIAL/创意之星人工智能版控制器硬件说明.pdf)
**

    - 树莓派系统内核版本 `v6.21`
    - 树莓派超频设置将`1500MHz`（默认）超频到`2000Mhz`
    - python解释器版本 `3.11.0`

- **架构**

    *
  *4路[BDMC2083](https://github.com/Kazu-Kusa/Reference-Material/tree/main/TOTURIAL/%E9%A9%B1%E5%8A%A8%E5%99%A8%E8%B0%83%E8%AF%95)
  闭环驱动**

*

*4路[Faulhaber2342L012CR](https://item.taobao.com/item.htm?spm=a1z09.2.0.0.271e2e8dwBT4HS&id=20965620027&_u=a3un1ne9d249)
直流有刷减速编码电机**

**14路传感器**

    - **9路模拟量传感器**
        - 4路用于边缘检测
        - 2路分别用于左右侧检测
        - 2路分别用于前后侧检测
        - 1路用于车体在台上/台下的判定检测

    - **5路逻辑量传感器**
        - 2路用于边缘检测
        - 2路用于前侧物体检测
        - 1路用于后侧物体检测

​

*

*

1路[720P 30FPS的摄像头](https://detail.tmall.com/item.htm?abbucket=15&id=655422944269&ns=1&spm=a21n57.1.0.0.4402523ctOgRLp)
**

​
实际使用过程中会使用最低分辨率用作识别以保证处理速度（实际可以更加的低），参考[不同分辨率下Apriltag识别精度测试_apriltag 评测比较](https://blog.csdn.net/zhuoqingjoking97298/article/details/122316966)

​    **单块6串联18650电池供电，标称电压24V**

​
树莓派供电适配器[LM2596S](https://detail.tmall.com/item.htm?_u=a3un1ne9688d&id=672825188272&spm=a1z09.2.0.0.3dee2e8dzyr0Xh)
，树莓派的正常供电说明可以在[人工智能版控制器硬件说明.pdf](https://github.com/Kazu-Kusa/Reference-Material/blob/main/TOTURIAL/创意之星人工智能版控制器硬件说明.pdf)

*

*

重要注意：从扩展板为树莓派供电时，供电电压必须随着树莓派负载增加而略有提高，但是一般不要超过16V，核心供电不足会有严重的降频，这是由于扩展板的降压原理，原理详情见扩展板板载稳压芯片[SY8286ARAC手册](https://item.szlcsc.com/189643.html)
**

​ 电机驱动供电适配器，无，直接链接

- **战斗逻辑**

  台上任务优先级队列

    1. 边缘响应
    2. 周围物体响应
    3. 寻物响应

  台下任务优先级队列

    1. 围栏方向响应

- **调参**

  使用参数配置文件统一管理

## 基础运作逻辑

响应器

![响应器 drawio](https://github.com/Kazu-Kusa/BattleBot_Kazu_Control/assets/88489697/b4650c6a-c337-4bb1-9b27-29d3846bb7c6)

通过多个响应器的串联可以实现优先级任务队列

![串联响应器 drawio](https://github.com/Kazu-Kusa/BattleBot_Kazu_Control/assets/88489697/dff0d956-4e9c-419e-b623-d188d537a17c)

## 传感器默认配置

注意：设备命名规则见[设备命名方式.pdf](https://github.com/Kazu-Kusa/Reference-Material/blob/main/技术参考/设备命名方式.pdf)
，其中由于后期加入了额外的传感器，这些传感器是命名规则中不存在的，所以各个地方的命名还未统一，额外添加的使用`extra-added`标注了

```python
"""
fl ad6
rl ad7
fr ad2
rr ad1

l1 ad8
r1 ad0
fb ad3
rb ad5

gray scaler  ad4  extra-added

gray l io3
gray r io2

ftl io7 	extra-added
ftr io6		extra-added
rtr io5		extra-added
"""
```
