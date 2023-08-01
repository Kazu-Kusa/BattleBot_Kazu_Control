#!/bin/bash
# apt source
APT_FILE_PATH=/etc/apt/sources.list
sudo sh -c "echo 'deb https://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ bullseye main non-free contrib rpi' > $APT_FILE_PATH"
sudo sh -c "echo 'deb-src https://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ bullseye main non-free contrib rpi' >> $APT_FILE_PATH"

# apt update
sudo apt update
sudo apt upgrade -y

python_version="3.11"  # 要判断的Python版本

function installPython(){
# install python3.11 compile dep
    sudo apt install -y build-essential libffi-dev libssl-dev openssl
    # install python3.11
    wget https://mirrors.huaweicloud.com/python/3.11.0/Python-3.11.0.tar.xz
    tar -xf Python-3.11.0.tar.xz
    cd Python-3.11.0
    ./configure --enable-optimizations
    make -j4
    sudo make install
    # update pip
    pip3 install --upgrade pip
    sudo pip3 config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple

}


function check_python_modules() {
    if python3 --version 2>&1 | grep -qF "$python_version"; then
        echo "Python $python_version 已安装."

        # 检查ssl模块是否存在
        ssl_module=$(python3 -c "import ssl" 2>&1)
        if [[ $? -eq 0 ]]; then
            echo "ssl模块已安装"
        else
            echo "ssl模块未安装"
            installPython
        fi

        # 检查ctypes模块是否存在
        ctypes_module=$(python3 -c "import ctypes" 2>&1)
        if [[ $? -eq 0 ]]; then
            echo "ctypes模块已安装"
        else
            echo "ctypes模块未安装"
            installPython
        fi
    else
        echo "Python $python_version 未安装."
        installPython
    fi
}

# 调用函数
check_python_modules

wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb

# raspi-config
sudo raspi-config nonint do_i2c 0  # 激活I2C
sudo raspi-config nonint do_fan 0  # 激活风扇
sudo sed -i 's/gpiopin=14/gpiopin=18/' /boot/config.txt
sudo sed -i 's/temp=80000/temp=60000/' /boot/config.txt  # 设置风扇GPIO和激活温度为60℃
# open SPI
sudo raspi-config nonint do_spi 0

function check_and_append_string() {
    file_path="$1"
    string_to_append="$2"

    if grep -q "$string_to_append" "$file_path"; then
        echo "String already exists in the file."
    else
        echo "$string_to_append" >> "$file_path"
        echo "String appended to the file."
    fi
}

# over clock
config_file="/boot/config.txt"
arm_freq="arm_freq=2000"
over_voltage="over_voltage=9"
core_freq="core_freq=750"

check_and_append_string "$config_file" "$arm_freq"
check_and_append_string "$config_file" "$over_voltage"
check_and_append_string "$config_file" "$core_freq"
sudo reboot