# import math
# import random
# import threading
# import time
#
# from typing import Tuple
# import sys
# import numpy as np
#
# import cv2
# import apriltag
#
# import uptech
# from up_controller import UpController
#
#
# # version without lock
#
# class Locating:
#     # 加速度
#     # 是相对车体的坐标系 不是绝对坐标系
#     # 要建立绝对坐标系还需要做进一步运动解算
#     # x+指向左方
#     # y+指向后方
#     # z+指向下方
#
#     # 线程锁，防止线程抢占内存
#     lock = threading.RLock()
#     # yaw 90度等效值
#     yaw_90 = 90
#
#     def __init__(self):
#         print("start locating")
#         self.detector = uptech.UpTech()
#         self.detector.MPU6500_Open()
#
#         self.attitude_data = self.detector.MPU6500_GetAttitude()
#         self.acceleration_data = self.detector.MPU6500_GetAccel()
#         self.gyroscope_data = self.detector.MPU6500_GetGyro()
#
#         # 返回值单位 度 [-180,180]
#         # 0:yaw 转向
#         # 1:pitch 俯仰
#         # 2:roll 侧滚
#
#         self.update_data_switch = True
#         self.integral_switch = False
#
#         print("monitoring")
#
#     def side_away_detection(self):
#         # 双重判断 第一层是通过z轴加速度速度是否为重力加速度判定 第二层是根据俯仰角和横滚角判定
#
#         if 0.8 < self.acceleration_data[2] < 1.2:
#             if -20 < self.attitude_data[1] < 20 and -20 < self.attitude_data[2] < 20:
#                 return 2
#             return 1
#         else:
#             return 0
#
#     # x轴加速度积分得到速度 标量
#     def x_and_x_speed_integral_thread(self):
#         print("updating x")
#         while True:
#             time.sleep(0.003)
#             # 0.003*10*accel
#             # 加速度返回值1 ==> 1G
#             # self.lock.acquire()
#             self.x_speed = 0.03 * self.acceleration_data[0]
#             self.x = 0.003 * self.x_speed
#             # self.lock.release()
#
#     # 开启一个新的（守护线程），用来计算x轴速度
#     def x_and_x_speed_scaler(self):
#         x_thread = threading.Thread(target=Locating.x_and_x_speed_integral_thread, args=(self,))
#         x_thread.setDaemon(True)
#         x_thread.start()
#
#     # y轴加速度积分得到速度 标量
#     def y_and_y_speed_integral_thread(self):
#         print("updating y")
#         while True:
#             time.sleep(0.003)
#             # 0.003*10*accel
#             # 加速度返回值1 ==> 1G
#             # self.lock.acquire()
#             self.x_speed = 0.03 * self.acceleration_data[1]
#             self.y = 0.003 * self.y_speed
#             # self.lock.release()
#
#     # 开启一个新的（守护线程），用来计算y轴速度
#     def y_and_y_speed_scaler(self):
#         y_thread = threading.Thread(target=Locating.y_and_y_speed_integral_thread, args=(self,))
#         y_thread.setDaemon(True)
#         y_thread.start()
#
#     # 计算实际的速度大小 并返回实际速度大小 x轴分量 y轴分量
#     def speed_vector(self):
#         self.speed = math.sqrt(pow(self.x_speed, 2) + pow(self.y_speed, 2))
#         return [self.speed, self.x_speed, self.y_speed]
#
#     # 返回绝对坐标
#     def location(self):
#         return [self.ab_x, self.ab_y]
#
#     def yaw_angle_variation(self, init_angle, dest_angle):
#         result_list = []
#         # 0 劣弧
#         # 1 优弧
#         arc1 = abs(dest_angle - init_angle)
#         arc2 = 360 - arc1
#         if arc1 > arc2:
#             result_list.append(arc2)
#             result_list.append(arc1)
#         else:
#             result_list.append(arc1)
#             result_list.append(arc2)
#         return result_list
#
#
# # 主函数
# class MatchDemo(Locating):
#     # 基础检测值
#
#     FD = 150
#
#     RD = 150
#
#     LD = 150
#
#     BD = 150
#
#     # # 倾斜计时
#     # na = 0
#     # # 推箱子计时
#     # nb = 0
#     # # 旋转计时
#     # nc = 8
#     # # 前搁浅计时
#     # nd_front_stranded = 0
#     # # 后搁浅计时
#     # ne = 8
#     # # 倾斜
#     # qx = 0
#
#     # 引入红外线判定
#     # 红外光电判定线
#     IR_judge_line = 300
#
#     edge = 0
#     edge_detect_switch = False
#
#     # 初始化
#     def __init__(self):
#
#         super().__init__()
#         self.version = "1.0"
#         self.servo_speed = 800
#         self.controller = UpController()
#         # self.controller.lcd_display("")
#         # 设置
#         self.controller.set_chassis_mode(2)
#         motor_ids = [1, 2]
#         servo_ids = [5, 6, 7, 8]
#         self.controller.set_cds_mode(motor_ids, 1)
#         self.controller.set_cds_mode(servo_ids, 0)
#
#         self.at_detector = apriltag.Detector(apriltag.DetectorOptions(families='tag36h11 tag25h9'))
#         self.apriltag_width = 0
#         self.tag_id = -1
#
#         apriltag_detect = threading.Thread(target=self.apriltag_detect_thread)
#         apriltag_detect.setDaemon(True)
#         apriltag_detect.start()
#
#         self.edge_detect_thread_start()
#
#     # 二维码检测
#     def apriltag_detect_thread(self):
#         print("detect april tag start")
#         cap = cv2.VideoCapture(0)
#
#         w = 640
#         h = 480
#         weight = 320
#         cap.set(3, w)
#         cap.set(4, h)
#
#         cup_w = int((w - weight) / 2)
#         cup_h = int((h - weight) / 2) + 50
#
#         while True:
#             ret, frame = cap.read()
#             frame = frame[cup_h:cup_h + weight, cup_w:cup_w + weight]
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             tags = self.at_detector.detect(gray)
#
#             for tag in tags:
#                 self.tag_id = tag.tag_id
#                 print("tag_id = {}".format(tag.tag_id))
#                 cv2.circle(frame, tuple(tag.corners[0].astype(int)), 4, (255, 0, 0), 2)  # left-top
#                 cv2.circle(frame, tuple(tag.corners[1].astype(int)), 4, (255, 0, 0), 2)  # right-top
#                 cv2.circle(frame, tuple(tag.corners[2].astype(int)), 4, (255, 0, 0), 2)  # right-bottom
#                 cv2.circle(frame, tuple(tag.corners[3].astype(int)), 4, (255, 0, 0), 2)  # left-bottom
#             cv2.imshow("img", frame)
#             if cv2.waitKey(100) & 0xff == ord('q'):
#                 break
#         cap.release()
#         cv2.destroyAllWindows()
#
#     # 前上台动作
#     def go_up_ahead_platform(self):
#
#         self.controller.move_cmd(-2000, -2000)
#         time.sleep(0.05)
#         self.controller.move_cmd(4000, -4000)
#         time.sleep(0.1)
#
#     # 后上台
#     def go_up_behind_platform(self):
#
#         # self.controller.move_cmd(0, 0)
#         # time.sleep(0.1)
#         # self.controller.move_cmd(1982, 1982)
#         # time.sleep(0.2)
#         self.controller.move_cmd(-9999, -9999)
#         time.sleep(2.6)
#         self.controller.move_cmd(0, 0)
#         time.sleep(0.1)
#
#     # 检测是否在台上-返回状态_基于灰度
#     def platform_detect(self):
#
#         judge_front_line = 2900
#         judge_rear_line = 2750
#         ad5_rear_gray_scaler = self.controller.adc_data[5]
#         ad1_front_gray_scaler = self.controller.adc_data[1]
#
#         if ad5_rear_gray_scaler <= judge_rear_line and ad1_front_gray_scaler <= judge_front_line:
#             # 在台下
#             print("off platform")
#             return 0
#
#         elif ad5_rear_gray_scaler > judge_rear_line and ad1_front_gray_scaler > judge_front_line:
#             # 在台上
#             print("on platform")
#             return 3
#         elif ad5_rear_gray_scaler <= judge_rear_line:
#             print("rear stranded")
#             return 2
#         else:
#             print("front stranded")
#             return 1
#
#     # 传感器对方位敌人边缘围栏的检测以及返回值
#     def fence_detect(self):
#
#         # 底部前方红外光电
#         io_4_bottom_front_IR = self.controller.io_data[5]
#
#         # 底部右侧红外光电
#         ad2_bottom_right_IR = self.controller.adc_data[2]
#
#         # 底部后方红外光电
#         ad3_bottom_rear_IR = self.controller.adc_data[3]
#
#         # 底部左侧红外光电
#         ad4_bottom_left_IR = self.controller.adc_data[4]
#
#         # 前红外测距传感器
#         ad0_front_dst = self.controller.adc_data[0]
#
#         # 右红外测距传感器
#         ad6_right_dst = self.controller.adc_data[6]
#
#         # 后红外测距传感器
#         ad7_rear_dst = self.controller.adc_data[7]
#
#         # 左红外测距传感器
#         ad8_left_dst = self.controller.adc_data[8]
#
#         # ----------------------对擂台，一个测距检测到--------------------
#         if ad3_bottom_rear_IR < self.IR_judge_line < ad2_bottom_right_IR and ad4_bottom_left_IR > self.IR_judge_line and ad0_front_dst > self.FD and ad6_right_dst < self.RD and ad7_rear_dst < self.BD and ad8_left_dst < self.LD:
#             # 在台下，后方对擂台
#             return 1
#         if ad4_bottom_left_IR < self.IR_judge_line < ad3_bottom_rear_IR and io_4_bottom_front_IR == 1 and ad0_front_dst < self.FD and ad6_right_dst > self.RD and ad7_rear_dst < self.BD and ad8_left_dst < self.LD:
#             # 在台下，左侧对擂台
#             return 2
#         if io_4_bottom_front_IR == 0 and ad2_bottom_right_IR > self.IR_judge_line and ad4_bottom_left_IR > self.IR_judge_line and ad0_front_dst < self.FD and ad6_right_dst < self.RD and ad7_rear_dst > self.BD and ad8_left_dst < self.LD:
#             # 在台下，前方对擂台
#             return 3
#         if ad2_bottom_right_IR < self.IR_judge_line < ad3_bottom_rear_IR and io_4_bottom_front_IR == 1 and ad0_front_dst < self.FD and ad6_right_dst < self.RD and ad7_rear_dst < self.BD and ad8_left_dst > self.LD:
#             # 在台下，右侧对擂台
#             return 4
#
#         # ------------------------对围栏，两个相邻测距检测到-------------
#         if ad2_bottom_right_IR > self.IR_judge_line and ad3_bottom_rear_IR > self.IR_judge_line and ad0_front_dst > self.FD and ad6_right_dst < self.RD and ad7_rear_dst < self.BD and ad8_left_dst > self.LD:
#             # 在台下，前左检测到围栏
#             return 5
#         if ad3_bottom_rear_IR > self.IR_judge_line and ad4_bottom_left_IR > self.IR_judge_line and ad0_front_dst > self.FD and ad6_right_dst > self.RD and ad7_rear_dst < self.BD and ad8_left_dst < self.LD:
#             # 在台下，前右检测到围栏
#             return 6
#         if io_4_bottom_front_IR == 1 and ad4_bottom_left_IR > self.IR_judge_line and ad0_front_dst < self.FD and ad6_right_dst > self.RD and ad7_rear_dst > self.BD and ad8_left_dst < self.LD:
#             # 在台下，后右检测到围栏
#             return 7
#         if io_4_bottom_front_IR == 1 and ad2_bottom_right_IR > self.IR_judge_line and ad0_front_dst < self.FD and ad6_right_dst < self.RD and ad7_rear_dst > self.BD and ad8_left_dst > self.LD:
#             # 在台下，后左检测到围栏
#             return 8
#
#         # --------------------------台上有敌人，两个相对测距检测到-----------
#         if ad0_front_dst > self.FD and ad6_right_dst < self.RD and ad7_rear_dst > self.BD and ad8_left_dst < self.LD:
#             # 在台下，前方或后方有台上敌人
#             return 9
#         if ad0_front_dst < self.FD and ad6_right_dst > self.RD and ad7_rear_dst < self.BD and ad8_left_dst > self.LD:
#             # 在台下，左侧或右侧由台上敌人
#             return 10
#
#         # -------------------------三侧有障碍，三个测距检测到---------------
#         if ad0_front_dst > self.FD and ad6_right_dst > self.RD and ad7_rear_dst < self.BD and ad8_left_dst > self.LD:
#             # 在台下，前方、左侧和右侧检测到围栏
#             return 11
#         if ad0_front_dst > self.FD and ad6_right_dst > self.RD and ad7_rear_dst > self.BD and ad8_left_dst < self.LD:
#             # 在台下，前方、右侧和后方检测到围栏
#             return 12
#         if ad0_front_dst > self.FD and ad6_right_dst < self.RD and ad7_rear_dst > self.BD and ad8_left_dst > self.LD:
#             # 在台下，前方、左侧和后方检测到围栏
#             return 13
#         if ad0_front_dst < self.FD and ad6_right_dst > self.RD and ad7_rear_dst > self.BD and ad8_left_dst > self.LD:
#             # 在台下，右侧、左侧和后方检测到围栏
#             return 14
#
#         # -----------------------斜对擂台，两个红外光电检测到----------------
#         if io_4_bottom_front_IR == 0 and ad2_bottom_right_IR < self.IR_judge_line and ad0_front_dst < self.FD and ad6_right_dst < self.RD:
#             # 在台下，前方和右侧对擂台其他传感器没检测到
#             return 15
#         if io_4_bottom_front_IR == 0 and ad4_bottom_left_IR < self.IR_judge_line and ad0_front_dst < self.FD and ad8_left_dst < self.LD:
#             # 在台下，前方和左侧对擂台其他传感器没检测到
#             return 16
#         if ad2_bottom_right_IR < self.IR_judge_line and ad3_bottom_rear_IR < self.IR_judge_line and ad6_right_dst < self.FD and ad7_rear_dst < self.RD:
#             # 在台下，后方和右侧对擂台其他传感器没检测到
#             return 17
#         if ad3_bottom_rear_IR < self.IR_judge_line and ad4_bottom_left_IR < self.IR_judge_line and ad7_rear_dst < self.FD and ad8_left_dst < self.LD:
#             # 在台下，后方和左侧对擂台其他传感器没检测到
#             return 18
#         else:
#             return 101
#
#     # def fence_detect_reformed(self):
#     #
#     #     # 底部前方红外光电
#     #     io_4_bottom_front_IR = self.controller.io_data[5
#     #
#     #     # 底部右侧红外光电
#     #     ad2_bottom_right_IR = self.controller.adc_data[2]
#     #
#     #     # 底部后方红外光电
#     #     ad3_bottom_rear_IR = self.controller.adc_data[3]
#     #
#     #     # 底部左侧红外光电
#     #     ad4_bottom_left_IR = self.controller.adc_data[4]
#     #
#     #     # 前红外测距传感器
#     #     ad0_front_dst = self.controller.adc_data[0]
#     #
#     #     # 右红外测距传感器
#     #     ad6_right_dst = self.controller.adc_data[6]
#     #
#     #     # 后红外测距传感器
#     #     ad7_rear_dst = self.controller.adc_data[7]
#     #
#     #     # 左红外测距传感器
#     #     ad8_left_dst = self.controller.adc_data[8]
#
#     # 传感器信息获取以及返回值
#     def edge_detect_and_data_update(self):
#
#         # # 左前红外光电传感器
#         # io_0_front_left_IR = self.controller.io_data[0]
#         #
#         # # 右前红外光电传感器
#         # io_1_front_right_IR = self.controller.io_data[1]
#         #
#         # # 右后红外光电传感器
#         # io_2_rear_right_IR = self.controller.io_data[2]
#         #
#         # # 左后红外光电传感器
#         # io_3_rear_left_IR = self.controller.io_data[3]
#         #
#         # # 获取前方测距值
#         # ad0_front_dst = self.controller.adc_data[0]
#         #
#         # # 获取后方测距值
#         # ad7_rear_dst = self.controller.adc_data[7]
#         k = 0
#
#         while True:
#
#             if self.edge_detect_switch + self.integral_switch + self.update_data_switch == 0:
#                 time.sleep(2)
#             else:
#                 if self.edge_detect_switch:
#                     # 每0.01s扫描一次
#                     time.sleep(0.01)
#                     # self.lock.acquire()
#                     if self.controller.io_data[0] == 0 and self.controller.io_data[1] == 0 and self.controller.io_data[
#                         2] == 0 and self.controller.io_data[3] == 0:
#
#                         # 没有检测到边缘
#                         self.edge = 0
#                     elif self.controller.io_data[0] == 1 and self.controller.io_data[1] == 0 and \
#                             self.controller.io_data[
#                                 2] == 0 and self.controller.io_data[3] == 0:
#
#                         # 左前检测到边缘
#                         self.edge = 1
#                     elif self.controller.io_data[0] == 0 and self.controller.io_data[1] == 1 and \
#                             self.controller.io_data[
#                                 2] == 0 and self.controller.io_data[3] == 0:
#
#                         # 右前检测到边缘
#                         self.edge = 2
#                     elif self.controller.io_data[0] == 0 and self.controller.io_data[1] == 0 and \
#                             self.controller.io_data[
#                                 2] == 1 and self.controller.io_data[3] == 0:
#
#                         # 右后检测到边缘
#                         self.edge = 3
#                     elif self.controller.io_data[0] == 0 and self.controller.io_data[1] == 0 and \
#                             self.controller.io_data[
#                                 2] == 0 and self.controller.io_data[3] == 1:
#
#                         # 左后检测到边缘
#                         self.edge = 4
#                     elif self.controller.io_data[0] == 1 and self.controller.io_data[1] == 1 and \
#                             self.controller.io_data[
#                                 2] == 0 and self.controller.io_data[3] == 0:
#
#                         # 前方两个检测到边缘
#                         self.edge = 5
#                     elif self.controller.io_data[0] == 0 and self.controller.io_data[1] == 0 and \
#                             self.controller.io_data[
#                                 2] == 1 and self.controller.io_data[3] == 1:
#                         # 后方两个检测到边缘
#                         self.edge = 6
#                     elif self.controller.io_data[0] == 1 and self.controller.io_data[1] == 0 and \
#                             self.controller.io_data[
#                                 2] == 0 and self.controller.io_data[3] == 1:
#                         # 左侧两个检测到边缘
#                         self.edge = 7
#                     elif self.controller.io_data[0] == 0 and self.controller.io_data[1] == 1 and \
#                             self.controller.io_data[
#                                 2] == 1 and self.controller.io_data[3] == 0:
#                         # 右侧两个检测到边缘
#                         self.edge = 8
#                     # elif self.controller.io_data[0] == 1 and self.controller.io_data[1] == 1 and self.controller.io_data[
#                     #     2] == 1 and self.controller.io_data[3] == 1 and self.controller.adc_data[0] > self.FD:
#                     #     # 搁浅放在擂台下
#                     #     self.edge = 9
#                     # elif self.controller.io_data[0] == 1 and self.controller.io_data[1] == 1 and self.controller.io_data[
#                     #     2] == 1 and self.controller.io_data[3] == 1 and self.controller.adc_data[7] > self.BD:
#                     #     # 搁浅放在擂台上
#                     #     self.edge = 10
#                     else:
#                         self.edge = 102
#                     if self.edge != 0:
#                         # self.lock.release()
#                         self.controller.move_cmd(0, 0)
#                         self.react_according_detection()
#
#                     k += 1
#
#                     if k == 50:
#                         k = 0
#                         print("now edge case is ", self.edge)
#
#                 if self.update_data_switch:
#                     # self.lock.acquire()
#                     self.attitude_data = self.detector.MPU6500_GetAttitude()
#                     # self.acceleration_data = self.detector.MPU6500_GetAccel()
#                     # self.gyroscope_data = self.detector.MPU6500_GetGyro()
#                     time.sleep(0.06)
#                     # self.lock.release()
#
#                 # if self.integral_switch:
#                 #     # self.lock.acquire()
#                 #     # x 速度 路程积分
#                 #     self.x_speed = 0.03 * self.acceleration_data[0]
#                 #     self.x = 0.003 * self.x_speed
#                 #
#                 #     # y 速度 路程积分
#                 #     self.x_speed = 0.03 * self.acceleration_data[1]
#                 #     self.y = 0.003 * self.y_speed
#                 #     time.sleep(0.06)
#                 #     # self.lock.release()
#
#     # 开启边缘线程
#     def edge_detect_thread_start(self):
#         print("edge detect Online")
#         t = threading.Thread(target=MatchDemo.edge_detect_and_data_update, args=(self,))
#         t.setDaemon(True)
#         t.start()
#
#     # 根据边缘检测函数（edge_detect）检测结果（只限于case_1-case_8，即八向对边缘的情况)，给出移动指令
#     def react_according_detection(self):
#         # 生成随机因子
#         # 只能用整型值控制电机，用浮点电机驱动板会把其转为负值
#         rand_multiplier = random.randint(7, 9)
#         # 左前检测到边缘
#         if self.edge == 1:
#             # self.controller.move_cmd(0, 0)
#             # time.sleep(0.01)
#             self.controller.move_cmd(-4000, -4000)
#             rand_multiplier = random.randint(7, 9)
#             time.sleep(0.05)
#             self.controller.move_cmd(400 * rand_multiplier, -400 * rand_multiplier)
#             time.sleep(0.03)
#         # 右前检测到边缘
#         if self.edge == 2:
#             # self.controller.move_cmd(0, 0)
#             # time.sleep(0.01)
#             self.controller.move_cmd(-4000, -4000)
#             rand_multiplier = random.randint(7, 9)
#             time.sleep(0.05)
#             self.controller.move_cmd(-400 * rand_multiplier, 400 * rand_multiplier)
#             time.sleep(0.03)
#         # 右后检测到边缘
#         if self.edge == 3:
#             # self.controller.move_cmd(0, 0)
#             # time.sleep(0.01)
#             self.controller.move_cmd(4000, 4000)
#             rand_multiplier = random.randint(7, 9)
#             time.sleep(0.05)
#             self.controller.move_cmd(400 * rand_multiplier, -400 * rand_multiplier)
#             time.sleep(0.03)
#         # 左后检测到边缘
#         if self.edge == 4:
#             # self.controller.move_cmd(0, 0)
#             # time.sleep(0.01)
#             self.controller.move_cmd(4000, 4000)
#             rand_multiplier = random.randint(7, 9)
#             time.sleep(0.05)
#             self.controller.move_cmd(-400 * rand_multiplier, 400 * rand_multiplier)
#             time.sleep(0.03)
#         # 前方两个检测到边缘
#         if self.edge == 5:
#             # self.controller.move_cmd(0, 0)
#             # time.sleep(0.01)
#             # 右转左转几率相等
#             self.controller.move_cmd(-4000, -4000)
#             rand_multiplier = random.randint(7, 9)
#             time.sleep(0.05)
#             if random.random() > 0.5:
#                 self.controller.move_cmd(400 * rand_multiplier, -400 * rand_multiplier)
#                 time.sleep(0.03)
#             else:
#                 self.controller.move_cmd(-400 * rand_multiplier, 400 * rand_multiplier)
#                 time.sleep(0.03)
#
#         # 后方两个检测到边缘
#         if self.edge == 6:
#             # self.controller.move_cmd(0, 0)
#             # time.sleep(0.01)
#             self.controller.move_cmd(5000, 5000)
#             rand_multiplier = random.randint(7, 9)
#             time.sleep(0.1)
#             # 随机偏移
#             if random.random() > 0.5:
#
#                 self.controller.move_cmd(-240 * rand_multiplier, 240 * rand_multiplier)
#             else:
#                 self.controller.move_cmd(240 * rand_multiplier, -240 * rand_multiplier)
#             time.sleep(0.2)
#         # 左侧两个检测到边缘
#         if self.edge == 7:
#             # self.controller.move_cmd(0, 0)
#             # time.sleep(0.01)
#             self.controller.move_cmd(5000, -5000)
#             rand_multiplier = random.randint(7, 9)
#             time.sleep(0.05)
#             self.controller.move_cmd(400 * rand_multiplier, 400 * rand_multiplier)
#             time.sleep(0.03)
#         # 右侧两个检测到边缘
#         if self.edge == 8:
#             # self.controller.move_cmd(0, 0)
#             # time.sleep(0.01)
#             self.controller.move_cmd(-5000, 5000)
#             rand_multiplier = random.randint(7, 9)
#             time.sleep(0.06)
#             self.controller.move_cmd(400 * rand_multiplier, 400 * rand_multiplier)
#             time.sleep(0.03)
#         self.controller.move_cmd(0, 0)
#
#     # 默认在非角落的地方 调整角度，找寻合适的角度上台
#     def find_dash_angle_and_react(self):
#         # # 底部前方红外光电
#         # io_4_bottom_front_IR = self.controller.io_data[5
#         #
#         # # 底部右侧红外光电
#         # ad2_bottom_right_IR = self.controller.adc_data[2]
#         #
#         # # 底部后方红外光电
#         # ad3_bottom_rear_IR = self.controller.adc_data[3]
#         #
#         # # 底部左侧红外光电
#         # ad4_bottom_left_IR = self.controller.adc_data[4]
#         #
#         # # 前红外测距传感器
#         # ad0_front_dst = self.controller.adc_data[0]
#         #
#         # # 右红外测距传感器
#         # # ad6_right_dst = self.controller.adc_data[6]
#         #
#         # # 后红外测距传感器
#         # ad7_rear_dst = self.controller.adc_data[7]
#         #
#         # # 左红外测距传感器
#         # # ad8_left_dst = self.controller.adc_data[8]
#
#         init_yaw_angle = self.attitude_data[2]
#
#         # 逆时针旋转
#         interval = 0.01
#         max_rotate_round = 2
#         current_round = 0
#         rotate_speed = 1600
#
#         max_rotate_time = 5
#         init_time = time.time()
#         print(init_time)
#         while time.time() - init_time < max_rotate_time and current_round < max_rotate_round:
#             if self.controller.adc_data[7] < self.BD and self.controller.adc_data[0] > self.FD and \
#                     self.controller.adc_data[2] > self.IR_judge_line and self.controller.adc_data[
#                 4] > self.IR_judge_line:
#                 print("captured")
#                 # self.controller.move_cmd(-rotate_speed, rotate_speed)
#                 # time.sleep(0.2)
#                 self.controller.move_cmd(2000, 2000)
#                 time.sleep(0.1)
#                 self.controller.move_cmd(-9999, -9999)
#                 time.sleep(0.8)
#                 self.controller.move_cmd(0, 0)
#                 return
#             if self.yaw_angle_variation(init_yaw_angle, self.attitude_data[2])[0] >= 82:
#                 init_yaw_angle = self.attitude_data[2]
#                 current_round += 0.25
#
#             print("current_round", current_round)
#             print("passed_time", time.time() - init_time)
#             print("Dt", time.time() - init_time)
#             self.controller.move_cmd(rotate_speed, -rotate_speed)
#             time.sleep(interval)
#             if self.platform_detect() == 3:
#                 self.controller.move_cmd(0, 0)
#                 return
#         # failed
#         print("failed to detect and react")
#         return -1
#
#     # 敌人检测(未更改)
#     def enemy_detect(self):
#         # 灰度预备接口
#         ad1_gray_scaler = self.controller.adc_data[1]
#
#         # 底部前方红外光电
#         io_4_bottom_front_IR = self.controller.io_data[5]
#
#         # 底部右侧红外光电
#         ad2_bottom_right_IR = self.controller.adc_data[2]
#
#         # 底部后方红外光电
#         ad3_bottom_rear_IR = self.controller.adc_data[3]
#
#         # 底部左侧红外光电
#         ad4_bottom_left_IR = self.controller.adc_data[4]
#
#         # 前红外测距传感器
#         ad0_front_dst = self.controller.adc_data[0]
#
#         # print("ad1_gray_scaler = {} , ad2_bottom_right_IR = {} , ad3_bottom_rear_IR = {}, ad4_bottom_left_IR = {} , ad0_front_dst = {}".format(ad1_gray_scaler,ad2_bottom_right_IR,ad3_bottom_rear_IR,ad4_bottom_left_IR,ad0_front_dst))
#
#         if io_4_bottom_front_IR == 1 and ad2_bottom_right_IR > 1000 and ad3_bottom_rear_IR > 1000 and ad4_bottom_left_IR > 1000:
#             # 无敌人
#             return 0
#         if io_4_bottom_front_IR == 0 and ad2_bottom_right_IR > 1000 and ad3_bottom_rear_IR > 1000 and ad4_bottom_left_IR > 1000:
#             # 前方有敌人
#             if self.tag_id != 2 or self.tag_id == -1:
#                 # 前方是敌人
#                 return 1
#             else:
#                 return 5
#         if ad1_gray_scaler > 100 and ad2_bottom_right_IR < 100 and ad3_bottom_rear_IR > 100 and ad4_bottom_left_IR > 100:
#             # 右侧有敌人或棋子
#             return 2
#         if ad1_gray_scaler > 100 and ad2_bottom_right_IR > 100 and ad3_bottom_rear_IR < 100 and ad4_bottom_left_IR > 100:
#             # 后方有敌人或棋子
#             return 3
#         if ad1_gray_scaler > 100 and ad2_bottom_right_IR > 100 and ad3_bottom_rear_IR > 100 and ad4_bottom_left_IR < 100:
#             # 左侧有敌人或棋子
#             return 4
#         else:
#             return 103
#
#     # 轻量化，非严格判定 检测周围 有优先级
#     def IR_surrounding_detect(self):
#
#         # 底部前方红外光电
#         io_4_bottom_front_IR = self.controller.io_data[5]
#
#         # 底部右侧红外光电
#         ad2_bottom_right_IR = self.controller.adc_data[2]
#
#         # 底部后方红外光电
#         ad3_bottom_rear_IR = self.controller.adc_data[3]
#
#         # 底部左侧红外光电
#         ad4_bottom_left_IR = self.controller.adc_data[4]
#
#         # 前方检测到物体
#         if io_4_bottom_front_IR == 0:
#             print("front detect")
#             return 1
#         # 左方检测到物体
#         elif ad4_bottom_left_IR < self.IR_judge_line:
#             print("left detect")
#             return 3
#         # 右方检测到物体
#         elif ad2_bottom_right_IR < self.IR_judge_line:
#             print("right detect")
#             return 4
#         # 后方检测到物体
#         elif ad3_bottom_rear_IR < self.IR_judge_line:
#             print("rear detect")
#             return 2
#         print("nothing")
#         return 0
#
#     # 定时转向，途中检测到前方物体停止，并带有小幅度的方向修正
#     def fastest_turn(self, direction, mode):
#         # p控制转向
#         if direction == 0:
#             return
#         # mode1 转向并索物体
#         # mode其他 转向
#         # 配合IR_surrounding_detect()
#         init_yaw_angle_place = self.attitude_data[2]
#
#         basic_speed = 2000
#         period = 0.32
#
#         left_speed = -basic_speed
#         right_speed = basic_speed
#
#         # 计时器
#         init_time = time.time()
#
#         # 检测时间间隔
#         time_gap = 0.01
#
#         # 快速后转（逆时针）
#         if direction == 2:
#             print("fast turn back")
#
#             while time.time() - init_time < period * 2:
#
#                 # rotated_angle = self.yaw_angle_variation(init_yaw_angle_place, self.attitude_data[2])[
#                 #                     0] - init_yaw_angle_place
#                 # proportion = 1 - (rotated_angle / 180)
#                 # if proportion > 1:
#                 #     proportion = -proportion + 1
#                 # print(proportion)
#                 # # yaw角判定转向角度
#                 # if rotated_angle >= 1.85 * self.yaw_90:
#                 #     self.controller.move_cmd(0, 0)
#                 #     return
#                 # 直接拿取前红外数据进行判断
#                 if self.controller.io_data[5] == 0 and mode == 1:
#                     self.controller.move_cmd(0, 0)
#                     return
#                 self.controller.move_cmd(left_speed, right_speed)
#                 time.sleep(time_gap)
#
#         else:
#             # 原地左转
#             if direction == 3:
#                 print("fast turn left")
#                 pass
#             # 原地右转
#             if direction == 4:
#                 print("fast turn right")
#                 left_speed = basic_speed
#                 right_speed = -basic_speed
#
#             while time.time() - init_time < period:
#
#                 # rotated_angle = self.yaw_angle_variation(self.attitude_data[2], init_yaw_angle_place)[
#                 #                     0] - init_yaw_angle_place
#                 # proportion = rotated_angle / 90
#                 # if proportion > 1:
#                 #     proportion = -proportion + 1
#                 #
#                 # print(proportion)
#                 # if rotated_angle >= 0.8 * self.yaw_90:
#                 #     self.controller.move_cmd(0, 0)
#                 #     return
#                 if self.controller.io_data[5] == 0 and mode == 1:
#                     self.controller.move_cmd(0, 0)
#                     return
#                 # print("le", int(left_speed * proportion))
#                 self.controller.move_cmd(left_speed, right_speed)
#                 time.sleep(time_gap)
#         self.controller.move_cmd(0, 0)
#         return
#
#     # 判定头或者尾部是否朝向非角落的道路
#     def conner_escape_angle_judge(self):
#         # # 底部右侧红外光电
#         # ad2_bottom_right_IR = self.controller.adc_data[2]
#         # # 底部后方红外光电
#         # ad3_bottom_rear_IR = self.controller.adc_data[3]
#         # # 底部左侧红外光电
#         # ad4_bottom_left_IR = self.controller.adc_data[4]
#         # # 底部前方红外光电
#         # io_4_bottom_front_IR = self.controller.io_data[5
#
#         # # 前红外测距传感器
#         # ad0_front_dst = self.controller.adc_data[0]
#         #
#         # # 右红外测距传感器
#         # ad6_right_dst = self.controller.adc_data[6]
#         #
#         # # 后红外测距传感器
#         # ad7_rear_dst = self.controller.adc_data[7]
#         #
#         # # 左红外测距传感器
#         # ad8_left_dst = self.controller.adc_data[8]
#
#         # XOR 0⊕0=0，1⊕0=1，0⊕1=1，1⊕1=0 同为0 异为1
#
#         # 距离 光电复合判据 严格
#         # 左右判定
#         left_judge = (self.controller.adc_data[4] < self.IR_judge_line) and (self.controller.adc_data[8] > self.LD)
#         right_judge = (self.controller.adc_data[2] < self.IR_judge_line) and (self.controller.adc_data[6] > self.RD)
#
#         left_right_judge = left_judge ^ right_judge
#         print("left_judge: ", left_judge, "||", "right_judge: ", right_judge)
#         # 前后判定
#         front_judge = (self.controller.io_data[5] == 0) and (self.controller.adc_data[0] > self.FD)
#         rear_judge = (self.controller.adc_data[3] < self.IR_judge_line) and (self.controller.adc_data[7] > self.BD)
#
#         front_rear_judge = front_judge ^ rear_judge
#         print("front_judge: ", front_judge, "||", "rear_judge: ", rear_judge)
#
#         # # 光电判据 宽松
#         # left_judge = self.controller.adc_data[4] < self.IR_judge_line
#         # right_judge = self.controller.adc_data[2] < self.IR_judge_line
#         # left_right_judge = left_judge ^ right_judge
#         # print("left_judge: ", left_judge, "||", "right_judge: ", right_judge)
#         #
#         # front_judge = self.controller.io_data[5 == 0
#         # rear_judge = self.controller.adc_data[3] < self.IR_judge_line
#         # front_rear_judge = front_judge ^ rear_judge
#         # print("front_judge: ", front_judge, "||", "rear_judge: ", rear_judge)
#
#         if left_right_judge and front_rear_judge:
#             # 可向前进 ：1
#             # 可后退：2
#             # 有三面检测到了：3
#             # 无：0
#             if front_judge == 1:
#                 return 2
#             else:
#                 return 1
#         elif left_judge + right_judge + rear_judge + front_judge == 1:
#             return 3
#         else:
#             return 0
#
#     # 主函数直接运行
#     def start_match(self):
#
#         # while 1:
#         #     # 底部左侧红外光电
#         #     ad4_bottom_left_IR = self.controller.adc_data[4]
#         #     if ad4_bottom_left_IR < self.IR_judge_line:
#         #         self.controller.move_cmd(-9999, -9999)
#         #         time.sleep(1)
#         #         break
#         # 比赛循环
#         while True:
#             stage = self.platform_detect()
#             self.tag_id = -1
#             if stage == 3:
#                 print("On Stage")
#
#                 self.edge_detect_switch = True
#                 if self.edge != 0:
#
#                     pass
#                     # self.react_according_detection()
#
#                 else:
#                     # 未检测到边界 怠速前进0.03秒
#                     self.controller.move_cmd(1600, 1600)
#                     time.sleep(0.03)
#
#                     IR_surrounding = self.IR_surrounding_detect()
#                     # 当前方检测到物体
#                     if IR_surrounding == 1:
#                         # 停止0.3s， 进行进一步检测
#                         time.sleep(0.13)
#                         self.controller.move_cmd(0, 0)
#                         time.sleep(0.08)
#
#                         # 根据码类型做出反应
#                         # -1: 为默认状态，未检测到二维码
#                         # 1: 检测到能量块
#                         # 2：检测到炸弹
#
#                         while self.tag_id == 1:
#                             # 检测到边缘则破除循环
#                             if self.edge == 5 or self.edge == 1 or self.edge == 2:
#                                 self.controller.move_cmd(-4000, -4000)
#                                 time.sleep(0.18)
#                                 self.controller.move_cmd(0, 0)
#                                 break
#
#                             # 怠速前进0.02s
#
#                             # 灰度辅助判断边缘，接近边缘时降速
#                             if self.controller.adc_data[1] < 2750:
#                                 self.controller.move_cmd(400, 400)
#                             else:
#                                 self.controller.move_cmd(980, 980)
#                             time.sleep(0.01)
#
#                         if self.tag_id == 2:
#                             # 随机左转 右转 后转
#                             self.fastest_turn(random.randint(2, 4), 0)
#
#                     elif IR_surrounding != 0:
#                         self.fastest_turn(IR_surrounding, 1)
#
#             elif stage == 1:
#                 print("FrontBody Stranded")
#                 # 前搁浅
#                 self.controller.move_cmd(-4000, -4000)
#                 time.sleep(0.16)
#                 if self.platform_detect() != 3:
#                     self.controller.move_cmd(1600, 1600)
#                     time.sleep(0.1)
#                 self.controller.move_cmd(0, 0)
#
#             elif stage == 2:
#                 print("RearBody stranded")
#                 # 后搁浅
#                 self.controller.move_cmd(4000, 4000)
#                 time.sleep(0.16)
#                 if self.platform_detect() != 3:
#                     self.controller.move_cmd(1600, 1600)
#                     time.sleep(0.1)
#                 self.controller.move_cmd(0, 0)
#
#             if stage == 0:
#                 print("Off Stage")
#
#                 self.edge_detect_switch = False
#                 # fence = self.fence_detect()
#                 #
#                 # print("the fence case is ", fence)
#                 conner_judge = self.conner_escape_angle_judge()
#                 print("the conner case is", conner_judge)
#                 if conner_judge == 1:
#                     self.controller.move_cmd(3000, 3000)
#                     time.sleep(0.2)
#                     self.controller.move_cmd(1500, 1500)
#                     time.sleep(0.1)
#                     self.controller.move_cmd(0, 0)
#                 elif conner_judge == 2:
#                     self.controller.move_cmd(-3000, -3000)
#                     time.sleep(0.2)
#                     self.controller.move_cmd(-1500, -1500)
#                     time.sleep(0.1)
#                     self.controller.move_cmd(0, 0)
#                 self.find_dash_angle_and_react()
#
#     def motor_test(self):
#         self.controller.move_cmd(1900, 1900)
#         time.sleep(1)
#         self.controller.move_cmd(-1900, -1900)
#         time.sleep(1)
#         self.controller.move_cmd(1900, -1900)
#         time.sleep(1)
#         self.controller.move_cmd(-1900, 1900)
#         time.sleep(1)
#
#     def test(self):
#         # 底部右侧红外光电
#         ad2_bottom_right_IR = self.controller.adc_data[2]
#         print("right IR", ad2_bottom_right_IR)
#         # 底部后方红外光电
#         ad3_bottom_rear_IR = self.controller.adc_data[3]
#         print("rear IR", ad3_bottom_rear_IR)
#         # 底部左侧红外光电
#         ad4_bottom_left_IR = self.controller.adc_data[4]
#         print("left IR", ad4_bottom_left_IR)
#         # 底部前方红外光电
#         io_4_bottom_front_IR = self.controller.io_data[5]
#         print("front IR", io_4_bottom_front_IR)
#         # 前红外测距传感器
#         ad0_front_dst = self.controller.adc_data[0]
#         print("front dst", ad0_front_dst)
#         # 右红外测距传感器
#         ad6_right_dst = self.controller.adc_data[6]
#         print("right dst", ad6_right_dst)
#         # 后红外测距传感器
#         ad7_rear_dst = self.controller.adc_data[7]
#         print("rear dst", ad7_rear_dst)
#         # 左红外测距传感器
#         ad8_left_dst = self.controller.adc_data[8]
#         print("left dst", ad8_left_dst)
#
#         if ad3_bottom_rear_IR < self.IR_judge_line and ad7_rear_dst < self.BD and io_4_bottom_front_IR == 0 and ad0_front_dst > self.FD and ad2_bottom_right_IR > self.IR_judge_line and ad4_bottom_left_IR > self.IR_judge_line:
#             print("found")
#         else:
#             print("not found")
#         print("------------------------------------\n\n\n")
#         time.sleep(2)
#
#
# if __name__ == '__main__':
#     match_demo = MatchDemo()
#     match_demo.start_match()
