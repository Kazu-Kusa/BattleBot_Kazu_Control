#!/bin/bash
dos2unix *.sh
sudo bash ./deploy_body.sh 
if [ "$1" == "reboot" ]; then
   sudo reboot
else
   echo "如果更改了超频选项，则需要重启"
fi
