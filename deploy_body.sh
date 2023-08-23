#!/bin/bash
# apt source
APT_FILE_PATH=/etc/apt/sources.list
sudo sh -c "echo 'deb https://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ bullseye main non-free contrib rpi' > $APT_FILE_PATH"
sudo sh -c "echo 'deb-src https://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ bullseye main non-free contrib rpi' >> $APT_FILE_PATH"
sudo sh -c "echo 'deb http://mirrors.ustc.edu.cn/raspbian/raspbian/ bullseye main contrib non-free rpi' >> $APT_FILE_PATH"
#sudo sh -c "echo 'deb http://raspbian.raspberrypi.org/raspbian/ bullseye main contrib non-free rpi' >> $APT_FILE_PATH"
# apt update
sudo apt update
sudo apt upgrade -y

PROJECT_ROOT_PATH=$(pwd)
echo $PROJECT_ROOT_PATH

##config here
PYTHON_VERSION="3.11.0"  # 要判断的Python版本
TEMP_DIR_PATH="/home/pi/temp"





mkdir $TEMP_DIR_PATH || True
sudo chmod 777 $TEMP_DIR_PATH

sudo apt install -y -q git gcc cmake



function installPython() {
    # install python compile dep
    sudo apt install -y build-essential libffi-dev libssl-dev openssl
    # install python
    cd $TEMP_DIR_PATH || exit
    wget https://mirrors.huaweicloud.com/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tar.xz
    tar -xf Python-$PYTHON_VERSION.tar.xz
    cd Python-$PYTHON_VERSION || exit
    ./configure --enable-optimizations
    make -j4
    sudo make install
    # update pip
    pip3 config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple
    pip3 install --upgrade pip setuptools wheel
}

function apply_autoenv(){
    PROJECT_DIR_PATH=$1
    VENV_DIR_PATH=$2

    echo "Checking Autoenv installation"
    INSTALL_URL=https://ghproxy.com/https://raw.githubusercontent.com/hyperupcall/autoenv/master/scripts/install.sh
    wget --show-progress -o /dev/null -O- $INSTALL_URL | sh

    if test -e "$PROJECT_DIR_PATH"; then
        echo "Found exists $PROJECT_DIR_PATH "
    else
        echo "creating $PROJECT_DIR_PATH"
        mkdir "$PROJECT_DIR_PATH"
    fi
    echo "source $VENV_DIR_PATH/bin/activate&&dos2unix $PROJECT_DIR_PATH/*.sh" > "$PROJECT_DIR_PATH/.env"
}
function create_venv(){
    BASE_PATH=/home/pi/.virtualenvs

    PROJECT_PATH=$1
    PROJECT_NAME=$(basename $1)

    VENV_DIR_PATH=$BASE_PATH/$PROJECT_NAME
    # 创建虚拟环境
    if test -e "$VENV_DIR_PATH"; then
        echo "虚拟环境已创建"
    else
        echo "在$VENV_DIR_PATH创建虚拟环境"
        python3 -m venv "$VENV_DIR_PATH"
        sudo chmod 777 "$VENV_DIR_PATH"
        source "$VENV_DIR_PATH/bin/activate"
        pip3 config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple
        pip3 config list
        pip3 install --upgrade pip setuptools wheel
        deactivate
        apply_autoenv "$PROJECT_PATH" "$VENV_DIR_PATH"
    fi
}



# 函数：检查模块是否存在
# 参数：模块名
# 返回值：0表示模块已安装，1表示模块未安装
check_module() {
    python3 -c "import $1" 2>/dev/null
    return $?
}
function check_python_modules() {
    if python3 --version 2>&1 | grep -qF "$PYTHON_VERSION"; then
        echo "Python $PYTHON_VERSION 已安装."



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

        if  check_module "llvmlite" ; then
            echo "llvmlite 已经安装"
        else
          source /etc/profile
            cd $TEMP_DIR_PATH || exit
            PACKAGE_URL=https://ghproxy.com/https://github.com/numba/llvmlite/archive/refs/tags/v0.41.0dev0.zip
            ZIP_NAME=$(basename $PACKAGE_URL)
            if test -e ./$ZIP_NAME;then
                echo "llvmlite 已经下载"
            else
                wget $PACKAGE_URL
                unzip ./$ZIP_NAME
            fi
            cd ./llvmlite-* || exit
            cd $PROJECT_ROOT_PATH || exit
            python3 setup.py build
            python3 runtests.py
            python3 setup.py install
            deactivate
        fi
    else
        echo "Python $PYTHON_VERSION 未安装."
        installPython
    fi
}

# 调用函数
check_python_modules
create_venv $PROJECT_ROOT_PATH


if command -v gpio; then
    echo "wiringpi 已经安装"
else
    echo "下载并安装wiringpi中"
    cd $TEMP_DIR_PATH || exit
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
over_voltage="over_voltage=10"
core_freq="core_freq=750"
arm_64bit="arm_64bit=0"
echo "-超频配置参数-"
echo "ARM主频设置为'$arm_freq'Mhz，默认1500Mhz，推荐范围<=2147Mhz"
check_and_append_string "$config_file" "$arm_freq"
echo "核心电压偏移设置为'$over_voltage'*10^-2V，默认0，推荐范围<=10*10^-2V"
check_and_append_string "$config_file" "$over_voltage"
echo "核心频率设置为'$core_freq'Mhz，默认500Mhz，推荐范围<=750Mhz"
check_and_append_string "$config_file" "$core_freq"
echo "确认系统为32bit"
check_and_append_string "$config_file" "$arm_64bit"

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
    cd $TEMP_DIR_PATH || exit
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

function install_ch34x_driver() {
    DRIVER_REPO_PATH=$PROJECT_ROOT_PATH/repo/ch341par_linux
    DRIVER_SRC="driver"
    DRIVER_NAME="ch34x_pis"
    # 检查驱动是否已经安装
    if lsmod | grep "$DRIVER_NAME"; then
        echo "驱动 $DRIVER_NAME 已安装"

    else

        cd $DRIVER_REPO_PATH ||exit
        cd $DRIVER_SRC || exit
        make || exit
        sudo make install
    fi
}

function build_ch34_demo() {
    DRIVER_REPO_PATH=$PROJECT_ROOT_PATH/repo/ch341par_linux
    DEMO_SRC=$1
    BUILD_DIR='build'

    echo "building ch34x_demo_app"
    cd "$DRIVER_REPO_PATH/$DEMO_SRC" || exit
    mkdir "$DRIVER_REPO_PATH/$DEMO_SRC/$BUILD_DIR" || True
    gcc *.c -o app -l$(basename $DEMO_SRC)
}
#install_ch34x_driver
#build_ch34_demo demo/ch341
#build_ch34_demo demo/ch347

sudo chmod -R 777 $TEMP_DIR_PATH



OPENCV_LIB="export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1"
sh -c "echo $OPENCV_LIB >> /etc/profile"
