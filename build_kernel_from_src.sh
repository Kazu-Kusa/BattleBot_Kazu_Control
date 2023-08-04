#!/bin/bash

TEMP_DIR=/home/pi/temp
mkdir $TEMP_DIR
cd $TEMP_DIR

if [ -z "$1" ]
then
    version=5.5 #default
else
    version=$1
fi

SOURCE_URL=https://ghproxy.com/https://github.com/raspberrypi/linux/archive/refs/heads/rpi-$version.y.zip
zip_name=$(basename $SOURCE_URL)
unziped_folder_name=linux-$(basename $zip_name .zip)

if test -e $unziped_folder_name; then
    cd $unziped_folder_name
else
    wget $SOURCE_URL
    unzip $zip_name
    rm $zip_name
    cd $unziped_folder_name
fi

echo "WORK DIR: $(pwd)"
KERNEL=kernel7l
sudo make bcm2711_defconfig


make -j4 zImage modules dtbs
sudo make modules_install
sudo cp arch/arm/boot/dts/*.dtb /boot/
sudo cp arch/arm/boot/dts/overlays/*.dtb* /boot/overlays/
sudo cp arch/arm/boot/dts/overlays/README /boot/overlays/
sudo cp arch/arm/boot/zImage /boot/$KERNEL.img


<<COMMENT
headers_dir=/usr/src/linux-headers-$(uname -r)
sudo mkdir $headers_dir
sudo cp * $headers_dir -r
sudo ln -s $headers_dir /lib/modules/$(uname -r)/build
COMMENT