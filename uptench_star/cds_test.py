#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import uptech
import time


if __name__ == '__main__':
    up=uptech.UpTech()
    up.CDS_Open()
    up.CDS_SetMode(1,0)
    while True:
        up.CDS_SetAngle(1,52,256)
        time.sleep(0.1)
        up.CDS_SetAngle(1, 256, 256)

    




