#!/bin/bash
# https://github.com/raspberrypi/rpi-firmware/tree/oldstable
sudo apt upgrade rpi-update

temp_dir=/home/pi/temp
mkdir $temp_dir
cd $temp_dir
pwd
# 定义内核文件的URL
kernel_url=$1
wget $kernel_url
filename=$(basename $kernel_url)
echo "$filename"

unzip_file_dirname=rpi-firmware-$(basename $filename .zip)
# 解压内核文件
unzip $filename
rm $filename



sudo mkdir /root/.rpi-firmware
sudo mv $temp_dir/$unzip_file_dirname/* /root/.rpi-firmware
sudo rm -rf $temp_dir/$unzip_file_dirname

sudo rm /boot/.firmware_revision
# 执行本地更新
sudo UPDATE_SELF=0 SKIP_DOWNLOAD=1 rpi-update

