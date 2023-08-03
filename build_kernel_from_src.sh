#!/bin/bash

TEMP_DIR=/home/pi/temp
mkdir $TEMP_DIR
cd $TEMP_DIR

SOURCE_URL=https://ghproxy.com/https://github.com/raspberrypi/linux/archive/refs/heads/rpi-5.15.y.zip

wget $SOURCE_URL

zip_name=$(basename $SOURCE_URL)

unzip $zip_name
rm $zip_name

unziped_folder_name=$(basename $zip_name .zip)
cd $unziped_folder_name

KERNEL=kernel7l
make bcm2711_defconfig

CONFIG_LOCALVERSION="-v7l-MY_CUSTOM_KERNEL"

make -j4 zImage modules dtbs
sudo make modules_install
sudo cp arch/arm/boot/dts/*.dtb /boot/
sudo cp arch/arm/boot/dts/overlays/*.dtb* /boot/overlays/
sudo cp arch/arm/boot/dts/overlays/README /boot/overlays/
sudo cp arch/arm/boot/zImage /boot/$KERNEL.img

sudo apt install raspberrypi-kernel-headers