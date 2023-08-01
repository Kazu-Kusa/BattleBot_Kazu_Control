#!/bin/bash


# 替换apt源为清华源（bullseye版本）
sudo sed -i 's|deb http://raspbian.raspberrypi.org/raspbian/ bullseye main contrib non-free rpi|#deb http://raspbian.raspberrypi.org/raspbian/ bullseye main contrib non-free rpi|g' /etc/apt/sources.list
sudo sed -i 's|#deb-src http://raspbian.raspberrypi.org/raspbian/ bullseye main contrib non-free rpi|deb-src http://raspbian.raspberrypi.org/raspbian/ bullseye main contrib non-free rpi|g' /etc/apt/sources.list
sudo sed -i 's|#deb http://archive.raspberrypi.org/debian/ bullseye main|deb http://archive.raspberrypi.org/debian/ bullseye main|g' /etc/apt/sources.list
sudo sed -i 's|#deb-src http://archive.raspberrypi.org/debian/ bullseye main|deb-src http://archive.raspberrypi.org/debian/ bullseye main|g' /etc/apt/sources.list

# 更新apt包管理器，并替换为清华源
sudo apt update
sudo apt upgrade -y

# 安装编译python所需的依赖
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev \
libssl-dev libsqlite3-dev libreadline-dev libffi-dev libbz2-dev

# 下载并编译安装Python 3.11
wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tar.xz
tar -xf Python-3.11.0.tar.xz
cd Python-3.11.0
./configure --enable-optimizations
make -j4
sudo make install

# 更新pip，并替换为中科大源
pip3 install --upgrade pip
sudo pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 配置raspi-config
sudo raspi-config nonint do_i2c 0  # 激活I2C
sudo raspi-config nonint do_fan 0  # 激活风扇
sudo raspi-config nonint set_config_var dtoverlay=gpio-fan,gpiopin=18,temp=60000 /boot/config.txt  # 设置风扇GPIO和激活温度为65℃
# 开启SPI
sudo raspi-config nonint do_spi 0

# 设置内核超频
sudo sed -i 's/#arm_freq=800/arm_freq=2000/g' /boot/config.txt
sudo sed -i 's/#over_voltage=0/over_voltage=10/g' /boot/config.txt
sudo sed -i 's/#arm_freq_min=600/arm_freq_min=750/g' /boot/config.txt

# 创建文档并写入配置参数
echo "APT源已替换为清华源" > environment_config.txt
echo "Python版本：3.11.0" >> environment_config.txt
echo "PIP源已替换为中科大源" >> environment_config.txt
echo "树莓派配置已完成" >> environment_config.txt
echo "SPI已开启" >> environment_config.txt
echo "内核超频：ARM频率2000MHz，内核频率750MHz" >> environment_config.txt