# 轮式格斗车主控程序

- 主控

  树莓派

  stm32

- 架构

  四驱电机

  18路传感器+一路摄像头

- 战法

  对箱子，对敌

- 调参
  热调试
  冷调试

# MPU6500功能简介

MPU-6500是一款六轴运动处理传感器，在大小为3.0×3.0×0.9mm的芯片上，通过QFN 封装（无引线方形封装），集成了 3 轴 MEMS 陀螺仪，3 轴
MEMS加速度计，以及一个数字运动处理器 DMP（ Digital Motion Processor）。还可以通过辅助I2C端口与多个非惯性数字传感器（例如压力传感器、磁力计）进行连接。
![image](https://user-images.githubusercontent.com/88489697/213609141-13c99d10-06c6-4a6a-a45a-e8c5e3e89ee5.png)

<details>
<summary>展开细节</summary>
<pre><code>

## 1.陀螺仪功能

MPU-6500中的三轴MEMS陀螺仪具有广泛的特性：
<details>
<summary>功能详情</summary>
<pre><code>
- 数字输出X、Y和Z轴角速度传感器(陀螺仪)，其用户可编程全量程为±250，±500，±1000和±2000°/秒，使用16位ADC采集数据。
- 数字可编程低通滤波器
- 陀螺仪工作电流：3.2mA
- 工厂校准灵敏度标度因子
- 自测试
</code></pre>
</details>

## 2.加速度计功能

MPU-6500中的三轴MEMS加速度计具有广泛的功能：
<details>
<summary>功能详情</summary>
<pre><code>
- 数字输出X-，Y-，Z轴加速度计，可编程全量程为±2g，±4g，+8g和±16g，使用16位ADC采集数据。
- 加速度计正常工作电流：450 uA
- 低功率加速度计模式电流：0.98Hz为6.37uA，31.25Hz为17.75uA
- 用户可编程中断
- 用于应用程序处理器低功耗操作的唤醒运动中断
- 自测
</code></pre>
</details>

## 3.附加功能

MPU-6500包括下列附加功能：
<details>
<summary>功能详情</summary>
<pre><code>
- 从外部传感器(例如磁强计)读取数据的辅助IIC总线
- 3.4mA工作电流当所有6轴都都工作时
- VDD电源电压范围为1.8~3.3V±5%
- VDDIO基准电压1.8~3.3V±5%提供至辅助IIC设备
- 芯片大小：3x3x0.9mm
- 加速度计和陀螺仪之间的最小交叉轴灵敏度
- 512字节FIFO缓冲器，使应用程序处理器能够读取突发数据。
- 数字输出温度传感器
- 陀螺仪、加速度计和温度传感器可编程数字滤波器
- 400 KHzIIC用于与所有寄存器通信
- 1 MHz SPI串行接口用于与所有寄存器通信
- 20 MHz SPL串行接口用于读取传感器和中断寄存器（提高读取速度）。
- MEMS结构在硅片级密封和键合
- 符合RoHS和绿色标准
</code></pre>
</details>

## 4.运动处理

<details>
<summary>功能详情</summary>
<pre><code>
- 内部数字运动处理(DMP)引擎支持高级运动处理和低功耗功能，例如使用可编程中断的姿态识别。
- 除角速度外，该设备还可以选择输出角度。
- 低功率计步器功能允许主机处理器在DMP保持步数计数的同时进入睡眠状态。
</code></pre>
</details>
</code></pre>
</details>

### MPU6500默认配置

- 角速度量程±2000°/s
- 加速度量程±8G
- 采样率1kHz

### 传感器配置

```python
"""
edge_rr 0
edge_fr 1
edge_fl 2
edge_rl 3
l2 8
r2 7
ftr 6
fb 4
rb 5
[edge_rr, edge_fr, edge_fl, edge_rl, fb,rb,fr,r2,l2]
{0:edge_rr,1:edge_fr,2:edge_fl, 3:edge_rl, 4:fb,5:rb,6:fr,7:r2,8:l2}

{0:r_gray,1:l_gray}
l_gray io 1
r_gray io 0
"""
```

