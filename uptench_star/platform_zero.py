import time

import cv2

import uptech

'''
init up
'''
up=uptech.UpTech()
up.LCD_Open(2)
up.ADC_IO_Open()
up.ADC_Led_Set(0,0x2F0000)
up.ADC_Led_Set(1,0x002F00)
up.CDS_Open()
up.CDS_SetMode(5,0)
up.CDS_SetMode(6,0)
up.MPU6500_Open()
up.LCD_PutString(30, 0, 'InnoStar')
up.LCD_Refresh()
up.LCD_SetFont(up.FONT_8X14)

'''
init net
'''
net = cv2.dnn.readNet('face.xml')
net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)
cv = cv2.VideoCapture(0)


while True:
    up.CDS_SetAngle(5,512,256)
    up.CDS_SetAngle(6,256,256)
    time.sleep(0.1)



