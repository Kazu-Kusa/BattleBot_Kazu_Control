import random
import threading
import time
from ctypes import cdll

import apriltag
import cv2

from up_controller import UpController
from uptech import UpTech

so_upt = cdll.LoadLibrary("libuptech.so")


# 角度偏差值计算
def yaw_angle_variation(init_angle: int, dest_angle: int) -> int:
    arc1 = abs(dest_angle - init_angle)
    arc2 = 360 - arc1
    if arc1 > arc2:
        return arc2
    return arc1


def wait(t):
    init_time = time.time()
    while time.time() - init_time <= t:
        pass
    return


class MatchDemo(UpController, UpTech):
    FD = 200
    RD = 200
    BD = 200
    LD = 200

    # 倾斜计时
    na = 0
    # 推箱子计时
    nb = 0
    # 旋转计时
    nc = 8
    # 前搁浅计时
    nd = 0
    # 后搁浅计时
    ne = 8
    # 倾斜
    qx = 0

    move_p = 100

    tag_monitor_switch = False

    def __init__(self):
        super().__init__()
        self.version = "1.0"
        self.servo_speed = 800
        self.lcd_display("OIP")

        # 设置
        self.set_chassis_mode(2)
        motor_ids = [1, 2]
        servo_ids = [5, 6, 7, 8]
        self.set_cds_mode(motor_ids, 1)
        self.set_cds_mode(servo_ids, 0)

        self.at_detector = apriltag.Detector(apriltag.DetectorOptions(families='tag36h11 tag25h9'))
        self.apriltag_width = 0
        self.tag_id = 0
        apriltag_detect = threading.Thread(target=self.apriltag_detect_thread)
        apriltag_detect.setDaemon(True)
        apriltag_detect.start()

        self.MPU6500_Open()

    def apriltag_detect_thread(self):
        print("detect start")
        cap = cv2.VideoCapture(0)

        w = 640
        h = 480
        weight = 320
        cap.set(3, w)
        cap.set(4, h)

        cup_w = int((w - weight) / 2)
        cup_h = int((h - weight) / 2) + 50

        while True:
            if self.tag_monitor_switch:  # 台上开启 台下关闭 节约性能
                ret, frame = cap.read()
                frame = frame[cup_h:cup_h + weight, cup_w:cup_w + weight]
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                tags = self.at_detector.detect(gray)

                for tag in tags:
                    self.tag_id = tag.tag_id
                    print("tag_id = {}".format(tag.tag_id))
                    cv2.circle(frame, tuple(tag.corners[0].astype(int)), 4, (255, 0, 0), 2)  # left-top
                    cv2.circle(frame, tuple(tag.corners[1].astype(int)), 4, (255, 0, 0), 2)  # right-top
                    cv2.circle(frame, tuple(tag.corners[2].astype(int)), 4, (255, 0, 0), 2)  # right-bottom
                    cv2.circle(frame, tuple(tag.corners[3].astype(int)), 4, (255, 0, 0), 2)  # left-bottom
                cv2.imshow("img", frame)
                if cv2.waitKey(100) & 0xff == ord('q'):
                    break
            else:
                time.sleep(2)
        cap.release()
        cv2.destroyAllWindows()

    # 前上台动作
    def go_up_ahead_platform(self):
        self.move_cmd(-2000, -2000)
        time.sleep(0.05)
        self.move_cmd(3500, -3500)
        time.sleep(0.1)

    # 后上台
    def go_up_behind_platform(self):
        self.move_cmd(0, 0)
        time.sleep(0.1)
        self.move_cmd(1000, 1000)
        time.sleep(0.2)
        self.move_cmd(-9999, -9999)
        time.sleep(0.5)
        self.move_cmd(0, 0)

    # 检测是否在台上-返回状态
    def platform_detect(self):
        ad1 = self.adc_data[1]

        if ad1 <= 2615:
            # 在台下
            print("OFF platform")
            return False

        else:
            # 在台上
            print("ON platform")
            return True

    def side_away_detection(self):
        # 数组长度3
        # 0位 代表pitch 这里表现的是横滚角
        # 1位 代表roll 这里表现的是俯仰角
        # 2位 代表yaw 这里表现的转向角
        if abs(self.MPU6500_GetAttitude()[0]) > 45 or abs(self.MPU6500_GetAttitude()[1]) > 45:
            return True
        else:
            return False

    def fence_detect_old(self):
        # # 底部前方红外光电
        # ad1 = self.adc_data[1]
        # ad1=grayScaler

        # real down and front
        io_4 = self.io_data[5]
        # 底部右侧红外光电
        ad2 = self.adc_data[2]
        # 底部后方红外光电
        ad3 = self.adc_data[3]
        # 底部左侧红外光电
        ad4 = self.adc_data[4]

        # 前红外测距传感器
        ad0 = self.adc_data[0]
        # 右红外测距传感器
        ad6 = self.adc_data[6]
        # 后红外测距传感器
        ad7 = self.adc_data[7]
        # 左红外测距传感器
        ad8 = self.adc_data[8]

        # ----------------------对擂台，一个测距检测到--------------------
        if ad3 < 1000 and ad2 > 1000 and ad4 > 1000 and ad0 > self.FD and ad6 < self.RD and ad7 < self.BD and ad8 < self.LD:
            # 在台下，后方对擂台
            return 1
        if ad4 < 1000 and io_4 == 1 and ad3 > 1000 and ad0 < self.FD and ad6 > self.RD and ad7 < self.BD and ad8 < self.LD:
            # 在台下，左侧对擂台
            return 2
        if io_4 == 0 and ad2 > 1000 and ad4 > 1000 and ad0 < self.FD and ad6 < self.RD and ad7 > self.BD and ad8 < self.LD:
            # 在台下，前方对擂台
            return 3
        if ad2 < 1000 and io_4 == 1 and ad3 > 1000 and ad0 < self.FD and ad6 < self.RD and ad7 < self.BD and ad8 > self.LD:
            # 在台下，右侧对擂台
            return 4

        # ------------------------对围栏，两个相邻测距检测到-------------
        if ad2 > 1000 and ad3 > 1000 and ad0 > self.FD and ad6 < self.RD and ad7 < self.BD and ad8 > self.LD:
            # 在台下，前左检测到围栏
            print("qianzuo")
            return 5

        if ad3 > 1000 and ad4 > 1000 and ad0 > self.FD and ad6 > self.RD and ad7 < self.BD and ad8 < 100:
            # 在台下，前右检测到围栏
            print("qianyouyouwenti")
            return 6
        if io_4 == 1 and ad4 > 1000 and ad0 < self.FD and ad6 > self.RD and ad7 > self.BD and ad8 < self.LD:
            # 在台下，后右检测到围栏
            return 7
        if io_4 == 1 and ad2 > 1000 and ad0 < self.FD and ad6 < self.RD and ad7 > self.BD and ad8 > self.LD:
            # 在台下，后左检测到围栏
            return 8

        # --------------------------台上有敌人，两个相对测距检测到-----------
        if ad0 > self.FD and ad6 < self.RD and ad7 > self.BD and ad8 < self.LD:
            # 在台下，前方或后方有台上敌人
            return 9
        if ad0 < self.FD and ad6 > self.RD and ad7 < self.BD and ad8 > self.LD:
            # 在台下，左侧或右侧由台上敌人
            return 10

        # -------------------------三侧有障碍，三个测距检测到---------------
        if ad0 > self.FD and ad6 > self.RD and ad7 < self.BD and ad8 > 300:
            # 在台下，前方、左侧和右侧检测到围栏
            return 11
        if ad0 > self.FD and ad6 > self.RD and ad7 > self.BD and ad8 < self.LD:
            # 在台下，前方、右侧和后方检测到围栏
            return 12
        if ad0 > self.FD and ad6 < self.RD and ad7 > self.BD and ad8 > self.LD:
            # 在台下，前方、左侧和后方检测到围栏
            return 13
        if ad0 < self.FD and ad6 > self.RD and ad7 > self.BD and ad8 > self.LD:
            # 在台下，右侧、左侧和后方检测到围栏
            return 14

        # -----------------------斜对擂台，两个红外光电检测到----------------
        if io_4 == 0 and ad2 < 1000 and ad0 < self.FD and ad6 < self.RD:
            # 在台下，前方和右侧对擂台其他传感器没检测到
            return 15
        if io_4 == 0 and ad4 < 1000 and ad0 < self.FD and ad8 < self.LD:
            # 在台下，在台下，前方和左侧对擂台其他传感器没检测到
            return 16
        if ad2 < 1000 and ad3 < 1000 and ad6 < self.FD and ad7 < self.RD:
            # 在台下，后方和右侧对擂台其他传感器没检测到
            return 17
        if ad3 < 1000 and ad4 < 1000 and ad7 < self.FD and ad8 < self.LD:
            # 在台下，后方和左侧对擂台其他传感器没检测到
            return 18
        else:
            return 101

    # 传感器对方位敌人边缘围栏的检测以及返回值
    def fence_detect(self):

        # # 底前红外光电
        # io_4 = self.io_data[5]
        # # 底部右侧红外光电
        # ad2 = self.adc_data[2]
        # # 底部后方红外光电
        # ad3 = self.adc_data[3]
        # # 底部左侧红外光电
        # ad4 = self.adc_data[4]
        #
        # # 前红外测距传感器
        # ad0 = self.adc_data[0]
        # # 右红外测距传感器
        # ad6 = self.adc_data[6]
        # # 后红外测距传感器
        # ad7 = self.adc_data[7]
        # # 左红外测距传感器
        # ad8 = self.adc_data[8]
        judge_bin = 0b00000000
        word = ""
        # 0 代表检测到了
        judge_dict = {0b01010111: 1, 0b10101011: 2, 0b01011101: 3, 0b10101110: 4,  # 非角落，单正向检测到擂台
                      0b01100110: 5, 0b00110011: 6, 0b10011001: 7, 0b11001100: 8,  # 角落情况或者斜对擂台情况
                      0b01010101: 9, 0b10101010: 10,  # 非角落，台上存在障碍物，对侧检测到
                      0b00100010: 11, 0b00010001: 12, 0b01000100: 13, 0b10001000: 14,  # 角落，3侧检测到
                      0b00111111: 15, 0b01101111: 16, 0b10011111: 17, 0b11001111: 18,  # 斜着对台，只有两个光电检测到
                      0b00000000: 19  # 全向8个传感器检测到

                      }
        try:
            # 底前红外光电
            judge_bin += self.io_data[5]
            judge_bin <<= 1
            # word = word + "f ||"
            # 底部右侧红外光电
            judge_bin += self.adc_data[2] > 1000
            judge_bin <<= 1
            # word = word + "r ||"
            # 底部后方红外光电
            judge_bin += self.adc_data[3] > 1000
            judge_bin <<= 1
            # word = word + "h ||"
            # 底部左侧红外光电
            judge_bin += self.adc_data[4] > 1000
            judge_bin <<= 1
            # word = word + "l ||"

            # -----------------------------------------------------
            # 前红外测距传感器
            judge_bin += self.adc_data[0] < self.FD
            judge_bin <<= 1
            # word = word + "F ||"
            # 右红外测距传感器
            judge_bin += self.adc_data[6] < self.RD
            judge_bin <<= 1
            # word = word + "R ||"
            # 后红外测距传感器
            judge_bin += self.adc_data[7] < self.BD
            judge_bin <<= 1
            # word = word + "H ||"
            # 左红外测距传感器
            judge_bin += self.adc_data[8] < self.LD
        except IndexError:
            print("IndexError")
            return 101
        print(f"the fence case is {bin(judge_bin)} || {judge_bin}")
        return judge_dict.get(judge_bin, 101)

    # -------------------------------------围栏应对函数-------------------------------------------------------
    def react_according_fence_detect(self):
        func_dict = {1: self.rear_to_plat, 2: self.left_to_plat,
                     3: self.front_to_plat, 4: self.right_to_plat,

                     5: self.front_left_to_fence, 6: self.front_left_to_fence,
                     7: self.rear_right_to_fence, 8: self.rear_left_to_fence,

                     9: self.front_rear_to_blockage, 10: self.right_left_to_blockage,

                     11: self.front_left_right_to_conner, 12: self.front_rear_right_to_conner,
                     13: self.front_left_rear_to_conner, 14: self.rear_left_right_to_conner,

                     15: self.front_right_side_away_to_plat, 16: self.front_left_side_away_to_plat,
                     17: self.rear_right_side_away_to_plat, 18: self.rear_left_side_away_to_plat,

                     19: self.search_fence_position,

                     101: self.search_fence_position
                     }

        return func_dict[self.fence_detect()]

    # <editor-fold desc="fence_react">
    # ----------------------------------------------
    def rear_to_plat(self):
        self.move_cmd(0, 0)
        self.move_cmd(2000, 2000)
        wait(0.1)
        self.move_cmd(-9999, -9999)
        time.sleep(0.8)
        self.move_cmd(0, 0)
        if self.side_away_detection():
            print("failed to get on platform")
            self.move_cmd(2000, 2000)
            time.sleep(0.3)
            return 505
        else:
            print("succeed to get on platform")
            self.fastest_turn(2, 0)
            return 1

    def left_to_plat(self):
        self.move_cmd(0, 0)
        self.fastest_turn(4, 0)
        return 2

    def front_to_plat(self):
        self.move_cmd(0, 0)
        self.fastest_turn(2, 0)
        return 3

    def right_to_plat(self):
        self.move_cmd(0, 0)
        self.fastest_turn(3, 0)
        return 4

    # ----------------------------------------------
    def front_left_to_fence(self):
        self.move_cmd(-3000, -3000)
        wait(0.4)
        self.fastest_turn(3, 0)
        if self.fence_detect() == 1:
            self.rear_to_plat()
        return 5

    def front_right_to_fence(self):
        self.move_cmd(-3000, -3000)
        wait(0.4)
        self.fastest_turn(4, 0)
        if self.fence_detect() == 1:
            self.rear_to_plat()
        return 6

    def rear_right_to_fence(self):
        self.move_cmd(3000, 3000)
        wait(0.4)
        self.fastest_turn(4, 0)
        if self.fence_detect() == 1:
            self.rear_to_plat()
        return 7

    def rear_left_to_fence(self):
        self.move_cmd(3000, 3000)
        wait(0.4)
        self.fastest_turn(3, 0)
        if self.fence_detect() == 1:
            self.rear_to_plat()
        return 8

    # ----------------------------------------------
    def front_rear_to_blockage(self):
        self.fastest_turn(3 + random.getrandbits(1), 0)
        self.move_cmd(4000, 4000)
        wait(0.2)
        self.move_cmd(0, 0)
        self.search_fence_position()
        return 9

    def right_left_to_blockage(self):
        if random.getrandbits(1):
            self.move_cmd(4000, 4000)
        self.move_cmd(-4000, -4000)
        wait(0.2)
        self.move_cmd(0, 0)
        self.search_fence_position()
        return 10

    # ----------------------------------------------
    def front_left_right_to_conner(self):
        self.search_fence_position()
        return 11

    def front_rear_right_to_conner(self):
        self.search_fence_position()
        return 12

    def front_left_rear_to_conner(self):
        self.search_fence_position()
        return 13

    def rear_left_right_to_conner(self):
        self.search_fence_position()
        return 14

    # ----------------------------------------------
    def front_right_side_away_to_plat(self):
        self.search_fence_position()
        return 15

    def front_left_side_away_to_plat(self):
        self.search_fence_position()
        return 16

    def rear_right_side_away_to_plat(self):
        self.search_fence_position()
        return 17

    def rear_left_side_away_to_plat(self):
        self.search_fence_position()
        return 18

    # ----------------------------------------------
    # ----------------------------------------------
    def search_fence_position(self):
        # 旋转一周以寻找fence的位置
        init_time = time.time()
        while time.time() - init_time < 2.3:
            if self.fence_detect() != 101:
                self.move_cmd(0, 0)
                print("fence found")
                return 200
            self.move_cmd(1200, -1200)
        while time.time() - init_time < 5:
            if not self.io_data[5]:
                self.move_cmd(1600, 1600)
                self.move_cmd(0, 0)
                return 300

        print("time limit exceeded")
        return 404

    def side_away_handling(self):
        self.move_cmd(-5000, 5000)

    # </editor-fold>

    # -------------------------------------围栏应对函数-------------------------------------------------------

    # ----------------------------------------------------------------------------

    def edge_detect(self):
        #     # 左前红外光电传感器
        #     io_0 = self.io_data[0]
        #     # 右前红外光电传感器
        #     io_1 = self.io_data[1]
        #     # 右后红外光电传感器
        #     io_2 = self.io_data[2]
        #     # 左后红外光电传感器
        #     io_3 = self.io_data[3]
        #     # 获取前方测距值
        #     ad0 = self.adc_data[0]
        #     # 获取后方测距值
        #     ad7 = self.adc_data[7]
        judge_bin = 0b0000
        # judge_dict = {0b0000: 0, 0b1000:1,0b0100: 2, 0b0010: 3, 0b0001: 4, 0b1100: 5, 0b0011: 6, 0b1001: 7, 0b0110: 8}
        try:
            judge_bin += self.io_data[0]
            judge_bin <<= 1
            judge_bin += self.io_data[1]
            judge_bin <<= 1
            judge_bin += self.io_data[2]
            judge_bin <<= 1
            judge_bin += self.io_data[3]
        except IndexError:
            self.move_cmd(0, 0)
        # judge_bin <<= 1
        # judge_bin += self.adc_data[0] > 480
        # judge_bin <<= 1
        # judge_bin += self.adc_data[7] > 480
        print(f"the edge case is{bin(judge_bin)}||{judge_bin}")
        return judge_bin

    # 敌人检测
    def react_according_edge_detection(self):
        # judge_dict = {0b0000: 0, 0b1000:1, 0b0100: 2, 0b0010: 3,
        # 0b0001: 4, 0b1100: 5, 0b0011: 6, 0b1001: 7, 0b0110: 8}
        judge_dict = {0b0000: self.no_edge_detected, 0b1000: self.front_left, 0b0100: self.front_right,
                      0b0010: self.rear_right, 0b0001: self.rear_left, 0b1100: self.front_double,
                      0b0011: self.rear_double, 0b1001: self.left_double, 0b0110: self.right_double}
        return judge_dict.get(self.edge_detect(), self.stop())

    # <editor-fold desc="edge_react">
    # ----------------------------------------------------------------------------
    # 边缘检测对应的响应函数
    def no_edge_detected(self):
        # print("safe")
        basic_speed = 34
        # # 底部右侧红外光电
        # ad2 = self.adc_data[2]
        # # 底部后方红外光电
        # ad3 = self.adc_data[3]
        # # 底部左侧红外光电
        # ad4 = self.adc_data[4]
        # # 底前红外光电
        # io_4 = self.io_data[5]

        surrounding_detection = self.IR_surrounding_detect()

        if surrounding_detection == 1:
            self.move_cmd(0, 0)
            init_t = time.time()
            while time.time() - init_t < 1:
                if self.tag_id:
                    break
            push_move_p = 65

            while self.tag_id == 1 or (self.tag_id == 0 and not self.io_data[5]):

                if self.edge_detect() != 0:
                    init_t = time.time()
                    self.move_cmd(-4000, -4000)
                    while time.time() - init_t < 0.3:
                        surrounding = self.IR_surrounding_detect()
                        if surrounding:
                            self.fastest_turn(surrounding, 0)
                            break

                    break
                self.move_cmd(push_move_p * basic_speed, push_move_p * basic_speed)
                if push_move_p > 40:
                    push_move_p -= 1

            if self.tag_id == 2:
                self.move_cmd(0, 0)
                # 向后转
                self.fastest_turn(2, 0)

                self.move_p = 70

        self.move_cmd(basic_speed * self.move_p, basic_speed * self.move_p)
        if self.move_p > 55:
            self.move_p -= 1
        return

    def front_left(self):
        # print("front_left")
        # case 1
        self.move_with_edge_detection(-3200, 0.1)
        self.move_cmd(3500, -3500)
        time.sleep(0.3)
        self.move_p = 80
        return

    def front_right(self):
        # print("front_right")
        # case 2
        self.move_with_edge_detection(-3400, 0.1)
        self.move_cmd(-3500, 3500)
        time.sleep(0.3)
        self.move_p = 80
        return

    def rear_right(self):
        # print("rear_right")
        # case 3
        self.move_cmd(3500, 3500)
        time.sleep(0.1)
        self.move_cmd(3500, -3500)
        time.sleep(0.3)
        self.move_p = 100
        return

    def rear_left(self):
        # print("rear_left")
        # case 4
        self.move_cmd(3500, 3500)
        time.sleep(0.1)
        self.move_cmd(-3500, 3500)
        time.sleep(0.3)
        self.move_p = 100
        return

    def front_double(self):
        # print("front_double")
        # case 5
        self.move_with_edge_detection(-5000, 0.1)
        self.move_cmd(3500, -3500)
        time.sleep(0.3)
        self.move_p = 100
        return

    def rear_double(self):
        # print("rear_double")
        # case 6
        self.move_with_edge_detection(5000, 0.15)
        self.move_p = 100
        return

    def left_double(self):
        # print("left_double")
        # case 7
        self.move_cmd(3800, -3200)
        time.sleep(0.1)
        self.move_cmd(3500, 0.1)
        self.move_p = 100
        return

    def right_double(self):
        # print("right_double")
        # case 8
        self.move_cmd(-3200, 3800)
        time.sleep(0.1)
        self.move_cmd(3500, 0.1)
        self.move_p = 100
        return

    def move_with_edge_detection(self, speed: int, mov_time: float):
        init_time = time.time()
        self.move_cmd(speed, speed)
        while time.time() - init_time < mov_time and self.edge_detect() == 0:
            pass
        self.move_cmd(0, 0)

    # 边缘检测对应的响应函数
    # -----------------------------------------------------------------------------------
    # </editor-fold>
    def enemy_detect(self):
        # 底部前方红外光电
        ad1 = self.adc_data[1]
        io_4 = self.io_data[5]
        # 底部右侧红外光电
        ad2 = self.adc_data[2]
        # 底部后方红外光电
        ad3 = self.adc_data[3]
        # 底部左侧红外光电
        ad4 = self.adc_data[4]
        # 前红外测距传感器
        ad0 = self.adc_data[0]

        # print("ad1 = {} , ad2 = {} , ad3 = {}, ad4 = {} , ad0 = {}".format(ad1,ad2,ad3,ad4,ad0))

        if io_4 == 1 and ad2 > 1000 and ad3 > 1000 and ad4 > 1000:
            # 无敌人
            return 0
        if io_4 == 0 and ad2 > 1000 and ad3 > 1000 and ad4 > 1000:
            # 前方有敌人
            if self.tag_id != 2 or self.tag_id == 0:
                # 前方是敌人
                return 1
            else:
                return 5
        if ad1 > 100 and ad2 < 100 and ad3 > 100 and ad4 > 100:
            # 右侧有敌人或棋子
            return 2
        if ad1 > 100 and ad2 > 100 and ad3 < 100 and ad4 > 100:
            # 后方有敌人或棋子
            return 3
        if ad1 > 100 and ad2 > 100 and ad3 > 100 and ad4 < 100:
            # //左侧有敌人或棋子
            return 4
        else:
            return 103

    # 快速转身
    def fastest_turn(self, direction, mode):
        # p控制转向
        # mode1 转向并索物体
        # mode其他 转向
        # 配合IR_surrounding_detect()
        if direction:
            init_yaw_angle_place = int(self.MPU6500_GetAttitude()[2])

            basic_speed = 11
            period = 3  # 最大的转动时间

            left_speed = -basic_speed
            right_speed = basic_speed

            init_time = time.time()

            # 快速后转（逆时针）
            if direction == 2:
                print("fast turn back")
                # self.move_cmd(left_speed * 200, right_speed * 200)
                while time.time() - init_time < period * 2:
                    rotated_angle = yaw_angle_variation(init_yaw_angle_place, int(self.MPU6500_GetAttitude()[2]))
                    remaining_angle = 180 - rotated_angle
                    print(f"rotated_angle {rotated_angle}")
                    try:
                        if (self.io_data[5] == 0 and mode == 1) or remaining_angle < 20:
                            self.move_cmd(0, 0)
                            return
                    except IndexError:
                        if remaining_angle < 25:
                            self.move_cmd(0, 0)
                            return
                    self.move_cmd(remaining_angle * left_speed, remaining_angle * right_speed)

            else:
                # 原地左转
                if direction == 3:
                    print("fast turn left")
                    pass
                # 原地右转
                if direction == 4:
                    print("fast turn right")
                    left_speed = basic_speed
                    right_speed = -basic_speed

                # self.move_cmd(left_speed * 200, right_speed * 200)
                while time.time() - init_time < period:
                    rotated_angle = yaw_angle_variation(init_yaw_angle_place, int(self.MPU6500_GetAttitude()[2]))
                    remaining_angle = 90 - rotated_angle
                    print(f"rotated_angle {rotated_angle}")
                    if (self.io_data[5] == 0 and mode == 1) or remaining_angle < 25:
                        self.move_cmd(0, 0)
                        return
                    self.move_cmd(remaining_angle * left_speed, remaining_angle * right_speed)

        return

    # 周围检测
    def IR_surrounding_detect(self):

        # # 底部前方红外光电
        # io_5_bottom_front_IR = self.io_data[5]
        #
        # # 底部右侧红外光电
        # ad2_bottom_right_IR = self.adc_data[2]
        #
        # # 底部后方红外光电
        # ad3_bottom_rear_IR = self.adc_data[3]
        #
        # # 底部左侧红外光电
        # ad4_bottom_left_IR = self.adc_data[4]

        IR_judge_line = 1000
        # 前方检测到物体
        try:
            if self.io_data[5] == 0:
                print("front detect")
                return 1
        except IndexError:
            pass
        # 左方检测到物体
        if self.adc_data[4] < IR_judge_line:
            print("left detect")
            return 3
        # 右方检测到物体
        elif self.adc_data[2] < IR_judge_line:
            print("right detect")
            return 4
        # 后方检测到物体
        elif self.adc_data[3] < IR_judge_line:
            print("rear detect")
            return 2
        print("nothing")
        return 0

    def start_match_reformed(self):

        while True:
            # 底部左侧红外光电
            ad4 = self.adc_data[4]
            if ad4 < 1000:
                self.move_cmd(-9999, -9999)
                time.sleep(1.2)
                break

        # infinite match loop
        while True:
            self.tag_id = 0
            if self.platform_detect():
                self.tag_monitor_switch = True  # 开启tag检测
                try:

                    self.react_according_edge_detection()()  # 检测边缘并应对
                except IndexError:
                    print("IndexError ON plat")
                    self.move_cmd(0, 0)
            else:
                self.tag_monitor_switch = False  # 关闭tag检测
                try:
                    self.react_according_fence_detect()()
                except IndexError:
                    print("IndexError OFF plat")
                    self.move_cmd(0, 0)


if __name__ == '__main__':
    match_demo = MatchDemo()

    match_demo.start_match_reformed()

    # print(match_demo.MPU6500_GetAttitude()[2])
    # time.sleep(10)
    # match_demo.MPU6500_Open()
    # print("fa")
    # print(match_demo.MPU6500_GetAttitude()[2])
    # print("done")
    # while True:
    #     match_demo.fastest_turn(match_demo.IR_surrounding_detect(), 0)

    # while True:
    #     k = match_demo.react_according_edge_detection()
    #     k()

    # while True:
    #     time.sleep(2)
    #     a = match_demo.fence_detect()
    #     b = match_demo.fence_detect_old()
    #     print(b)
    #
    #     if a == b:
    #         print("affirmative")
    #     else:
    #         print("fal")
    #
    #     print(
    #         f"f{match_demo.io_data[5]}||r{match_demo.adc_data[2]}||h{match_demo.adc_data[3]}||l{match_demo.adc_data[4]}||")
    #     print(
    #         f"F{match_demo.adc_data[0]}||R{match_demo.adc_data[6]}||H{match_demo.adc_data[7]}||L{match_demo.adc_data[8]}||")
