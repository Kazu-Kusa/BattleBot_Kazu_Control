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

TEMP_DIR="/home/pi/temp"
mkdir $TEMP_DIR
sudo apt install -y -q git gcc cmake

python_version="3.11.0"  # 要判断的Python版本

function installPython() {
    # install python compile dep
    sudo apt install -y build-essential libffi-dev libssl-dev openssl
    # install python
    cd $TEMP_DIR || exit
    wget https://mirrors.huaweicloud.com/python/$python_version/Python-$python_version.tar.xz
    tar -xf Python-$python_version.tar.xz
    cd Python-$python_version || exit
    ./configure --enable-optimizations
    make -j4
    sudo make install
    # update pip
    pip3 install --upgrade pip
}

function apply_autoenv(){
    PROJECT_DIR_PATH=$1
    VENV_DIR_PATH=$2
    INSTALL_URL=https://ghproxy.com/https://raw.githubusercontent.com/hyperupcall/autoenv/master/scripts/install.sh
    wget --show-progress -o /dev/null -O- $INSTALL_URL | sh
    if test -e "$PROJECT_DIR_PATH"; then
        echo "Found exists $PROJECT_DIR_PATH "
    else
        echo "creating $PROJECT_DIR_PATH"
        mkdir "$PROJECT_DIR_PATH"
    fi
    echo "source $VENV_DIR_PATH/bin/activate&&dos2unix $PROJECT_DIR_PATH/*.sh" > "$PROJECT_DIR_PATH/.env"
    echo "find /home/pi/battleBot -name "*.sh" -exec dos2unix {} \;" >> "$PROJECT_DIR_PATH/.env"
}
function create_venv(){
    BASE_PATH=/home/pi/.virtualenvs
    PROJECT_NAME=$1
    PROJECT_PATH=/home/pi/$PROJECT_NAME
    # 创建虚拟环境
    if test -e "$BASE_PATH/$PROJECT_NAME"; then
        echo "虚拟环境已创建"
    else
        echo "在$BASE_PATH/$PROJECT_NAME创建虚拟环境"
        python3 -m venv "$BASE_PATH/$PROJECT_NAME"
        source "$BASE_PATH/$PROJECT_NAME/bin/activate"
        pip3 config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple
        pip3 config list
        pip3 install --upgrade pip setuptools wheel pyserial pytest
        deactivate
        apply_autoenv "$PROJECT_PATH" "$BASE_PATH/$PROJECT_NAME"
    fi
}

pip3 config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple


# 函数：检查模块是否存在
# 参数：模块名
# 返回值：0表示模块已安装，1表示模块未安装
check_module() {
    python3 -c "import $1" 2>/dev/null
    return $?
}
function check_python_modules() {
    if python3 --version 2>&1 | grep -qF "$python_version"; then
        echo "Python $python_version 已安装."



        # 调用示例
        if check_module "ssl"; then
            echo "ssl模块已安装"
        else
            echo "ssl模块未安装"
            installPython
        fi

        if check_module "ctypes"; then
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
create_venv "BattleBot_Kazu_Control"


if command -v gpio; then
    echo "wiringpi 已经安装"
else
    echo "下载并安装wiringpi中"
    cd $TEMP_DIR || exit
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

echo "检查LLVM"
source /etc/profile
LLVM_URL=https://ghproxy.com/https://github.com/llvm/llvm-project/releases/download/llvmorg-14.0.6/clang+llvm-14.0.6-armv7a-linux-gnueabihf.tar.xz
FILE_NAME=$(basename $LLVM_URL)
UNZIPPED_FOLDER_NAME=$(basename "$FILE_NAME" .tar.xz)
LLVM_DIR=/opt/llvm
echo "target package name: $FILE_NAME"
echo "unzipped name: $UNZIPPED_FOLDER_NAME"
echo "install destination: $LLVM_DIR"
if which llvm-config; then
    echo "LLVM已经安装"
else
    echo "下载LLVM"
    cd $TEMP_DIR || exit
    if test -e "./$FILE_NAME"; then
        echo "llvm-project已经存在"
    else
        wget $LLVM_URL
    fi
    sudo apt install pv -y
    sudo chmod 777 "$FILE_NAME"
    pv "./$FILE_NAME" | tar -xJ
    sudo mkdir -p $LLVM_DIR
    sudo mv "$UNZIPPED_FOLDER_NAME/*" $LLVM_DIR
    rm -rf "$UNZIPPED_FOLDER_NAME"


    echo "安装LLVM到$LLVM_DIR"

    if echo "$PATH" | grep -q "$LLVM_DIR"; then
      echo "路径 $LLVM_DIR 已存在于 PATH 环境变量中"
    else
      echo "路径 $LLVM_DIR 不存在于 PATH 环境变量中"
      sudo sh -c "echo 'export PATH=$PATH:$LLVM_DIR/bin' >> /etc/profile"
      #sudo sh -c "echo 'export secure_path=$secure_path:$LLVM_DIR/bin' >> /etc/sudoers"
      #source /etc/sudoers
      source /etc/profile
    fi
    echo "已在/etc/profile中添加PATH"
fi
#llvmlite deps  #ch34x driver deps
sudo apt-get install -y -q libtinfo-dev raspberrypi-kernel-headers libpigpiod-if2-1 pigpiod
#sudo apt-get install -y i2c-tools
#sudo apt-get install --reinstall raspberrypi-bootloader raspberrypi-kernel raspberrypi-kernel-headers

if ! systemctl is-enabled pigpiod >/dev/null 2>&1; then
  # 设置pigpiod开机自启
  sudo systemctl enable pigpiod
  sudo pigpiod
  echo "已设置pigpiod开机自启"
else
  echo "pigpiod已设置开机自启"
fi





