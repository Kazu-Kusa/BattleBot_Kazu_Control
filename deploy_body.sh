#!/bin/bash
# apt source
APT_FILE_PATH=/etc/apt/sources.list
sudo sh -c "echo 'deb https://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ bullseye main non-free contrib rpi' > $APT_FILE_PATH"
sudo sh -c "echo 'deb-src https://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ bullseye main non-free contrib rpi' >> $APT_FILE_PATH"
sudo sh -c "echo 'deb http://mirrors.ustc.edu.cn/raspbian/raspbian/ bullseye main contrib non-free rpi' >> $APT_FILE_PATH"
sudo sh -c "echo 'deb http://raspbian.raspberrypi.org/raspbian/ bullseye main contrib non-free rpi' >> $APT_FILE_PATH"



# apt update
sudo apt update
sudo apt upgrade -y


sudo apt install -y git gcc cmake

python_version="3.11"  # 要判断的Python版本

function installPython() {
    # install python3.11 compile dep
    sudo apt install -y build-essential libffi-dev libssl-dev openssl
    # install python3.11
    TEMP_DIR="~/temp"
    mkdir '$TEMP_DIR'
    cd '$TEMP_DIR'
    wget https://mirrors.huaweicloud.com/python/3.11.0/Python-3.11.0.tar.xz
    tar -xf Python-3.11.0.tar.xz
    cd Python-3.11.0
    ./configure --enable-optimizations
    make -j4
    sudo make install
    # update pip
    pip3 install --upgrade pip


}
pip3 install --upgrade pip setuptools wheel

pip3 config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple
pip3 config list

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



if command -v gpio; then
    echo "wiringpi 已经安装"
else
    echo "下载并安装wiringpi中"
    TEMP_DIR="~/temp"
    mkdir '$TEMP_DIR'
    cd '$TEMP_DIR'
    rm wiringpi-latest.deb
    wget https://project-downloads.drogon.net/wiringpi-latest.deb
    sudo dpkg -i wiringpi-latest.deb
fi



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
        echo "String '$2' already exists in the file '$1',do nothing."
    else
        echo "$string_to_append" >> "$file_path"
        echo "String '$2' appended to the file '$1'."
    fi
}

# over clock
config_file="/boot/config.txt"
arm_freq="arm_freq=2000"
over_voltage="over_voltage=7"
core_freq="core_freq=750"
echo "-超频配置参数-"
echo "ARM主频设置为'$arm_freq'Mhz，默认1500Mhz，推荐范围<=2147Mhz"
check_and_append_string "$config_file" "$arm_freq"
echo "核心电压偏移设置为'$over_voltage'*10^-2V，默认0，推荐范围<=10*10^-2V"
check_and_append_string "$config_file" "$over_voltage"
echo "核心频率设置为'$core_freq'Mhz，默认500Mhz，推荐范围<=750Mhz"
check_and_append_string "$config_file" "$core_freq"

source /etc/profile
if which llvm-config; then
    echo "LLVM已经安装"
else
    echo "下载LLVM"

    TEMP_DIR=~/temp
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    wget -q https://ghproxy.com/https://github.com/llvm/llvm-project/releases/download/llvmorg-14.0.6/clang+llvm-14.0.6-armv7a-linux-gnueabihf.tar.xz
    tar xf ./clang+llvm-14.0.6-armv7a-linux-gnueabihf.tar.xz
    sudo mkdir -p $LLVM_DIR
    sudo mv clang+llvm-14.0.6-armv7a-linux-gnueabihf/* $LLVM_DIR
    rm -rf clang+llvm-14.0.6-armv7a-linux-gnueabihf

    LLVM_DIR=/opt/llvm
    echo "安装LLVM到$LLVM_DIR"

    if echo "$PATH" | grep -q "$LLVM_DIR"; then
      echo "路径 $LLVM_DIR 已存在于 PATH 环境变量中"
    else
      echo '路径 $LLVM_DIR 不存在于 PATH 环境变量中'
      sudo sh -c "echo 'export PATH=$PATH:$LLVM_DIR/bin' >> /etc/profile"
      #sudo sh -c "echo 'export secure_path=$secure_path:$LLVM_DIR/bin' >> /etc/sudoers"
      #source /etc/sudoers
      source /etc/profile
    fi
    echo "已在/etc/profile中添加PATH"
fi

sudo apt-get install -y libtinfo-dev #llvmlite deps
sudo apt install -y raspberrypi-kernel-headers #ch34x driver deps
