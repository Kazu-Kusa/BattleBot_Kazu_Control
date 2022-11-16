import threading
import time

import apriltag
import cv2

from up_controller import UpController
from uptech import UpTech


def wait(t):
    init_time = time.time()
    while time.time() - init_time <= t:
        pass
    return


def yaw_angle_variation(init_angle: int, dest_angle: int) -> int:
    arc1 = abs(dest_angle - init_angle)
    arc2 = 360 - arc1
    if arc1 > arc2:
        return arc2
    return arc1


class MatchDemo(UpController, UpTech):
    FD = 200
    RD = 500
    BD = 500
    LD = 300

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

    basic_speed = 42

    mov_p = 80

    tag_monitor_switch = True

    def __init__(self):
        super().__init__()
        self.version = "1.0"
        self.servo_speed = 800
        self.lcd_display("MatchDemo")
        # 设置
        self.set_chassis_mode(2)
        motor_ids = [1, 2]
        servo_ids = [5, 6, 7, 8]
        self.set_cds_mode(motor_ids, 1)
        self.set_cds_mode(servo_ids, 0)

        self.at_detector = apriltag.Detector(apriltag.DetectorOptions(families='tag36h11 tag25h9'))
        self.apriltag_width = 0
        self.tag_id = -1
        apriltag_detect = threading.Thread(target=self.apriltag_detect_thread)
        apriltag_detect.setDaemon(True)
        apriltag_detect.start()

        tag_monitor_switch = False

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
        time.sleep(0.5)
        self.move_cmd(-15000, -15000)
        time.sleep(0.5)
        self.move_cmd(0, 0)
        time.sleep(0.5)

    # 检测是否在台上-返回状态
    def paltform_detect(self):
        ad1 = self.adc_data[1]

        if ad1 <= 2615:
            # 在台下
            print("taixia")
            return 0

        else:
            # 在台上
            print("taishangxx")
            return 1

        # 传感器对方位敌人边缘围栏的检测以及返回值

    def fence_detect(self):
        # 底部前方红外光电
        ad1 = self.adc_data[1]
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
        # jiekou  ad0  bian  ad0
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

    # 传感器信息获取以及返回值
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
        judge_dict = {0b0000: 0, 0b1000: 1, 0b0100: 2, 0b0010: 3, 0b0001: 4, 0b1100: 5, 0b0011: 6, 0b1001: 7, 0b0110: 8}
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
        return judge_dict.get(judge_bin, 606)

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
    # zhixing bianyuan jiance，执行边缘检测
    def bianyuanjiance(self):
        edge1 = self.edge_detect()
        # 左前检测到边缘
        if edge1 == 1:
            # print("xxxxyxtxjytyjygkhskgihbdihids")
            # self.move_cmd(0, 0)
            # time.sleep(0.01)
            self.move_cmd(-3500, -3500)
            time.sleep(0.05)
            self.move_cmd(3500, -3500)
            time.sleep(0.03)
            # 右前检测到边缘
        if edge1 == 2:
            # self.move_cmd(0, 0)
            # time.sleep(0.01)
            self.move_cmd(-3500, -3500)
            time.sleep(0.1)
            self.move_cmd(-3500, 3500)
            time.sleep(0.03)
            # 右后检测到边缘
        if edge1 == 3:
            # self.move_cmd(0, 0)
            # time.sleep(0.01)
            self.move_cmd(3500, 3500)
            time.sleep(0.1)
            self.move_cmd(3500, -3500)
            time.sleep(0.03)
            # 左后检测到边缘
        if edge1 == 4:
            # self.move_cmd(0, 0)
            # time.sleep(0.01)
            self.move_cmd(3500, 3500)
            time.sleep(0.1)
            self.move_cmd(-3500, 3500)
            time.sleep(0.03)
            # 前方两个检测到边缘
        if edge1 == 5:
            # self.move_cmd(0, 0)
            # time.sleep(0.01)
            self.move_cmd(-3500, -3500)
            time.sleep(0.1)
            self.move_cmd(3500, -3500)
            time.sleep(0.03)
            # 后方两个检测到边缘
        if edge1 == 6:
            # self.move_cmd(0, 0)
            # time.sleep(0.01)
            self.move_cmd(5000, 5000)
            time.sleep(0.1)
            # 左侧两个检测到边缘
        if edge1 == 7:
            # self.move_cmd(0, 0)
            # time.sleep(0.01)
            self.move_cmd(5000, -3500)
            time.sleep(0.1)
            self.move_cmd(3500, 3500)
            time.sleep(0.03)
            # 右侧两个检测到边缘
        if edge1 == 8:
            # self.move_cmd(0, 0)
            # time.sleep(0.01)
            self.move_cmd(-3500, 5000)
            time.sleep(0.1)
            self.move_cmd(3500, 3500)
            time.sleep(0.03)

    # 敌人检测
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
            if self.tag_id != 2 or self.tag_id == -1:
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

    def side_away_detection(self):
        # 数组长度3
        # 0位 代表pitch 这里表现的是横滚角
        # 1位 代表roll 这里表现的是俯仰角
        # 2位 代表yaw 这里表现的转向角
        if abs(self.MPU6500_GetAttitude()[0]) > 45 or abs(self.MPU6500_GetAttitude()[1]) > 45:
            return True
        else:
            return False

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

    def move_with_edge_detection(self, speed: int, mov_time: float):
        init_time = time.time()
        self.move_cmd(speed, speed)
        while time.time() - init_time < mov_time and self.edge_detect() == 0:
            pass
        self.move_cmd(0, 0)

    # 主函数直接运行
    def start_match(self):

        # self.go_up_ahead_platform()
        # xxy:int = 1
        '''
        while 1:
            # 底部左侧红外光电
            ad4 = self.adc_data[4]
            if ad4 < 1000:
                self.move_cmd(-9999, -9999)
                time.sleep(1)
                break
        '''
        while 1:

            stage = self.paltform_detect()

            self.tag_id = -1

            # stage = 1
            # stage = 0
            if stage == 1:
                self.tag_monitor_switch = True
                print("taishangxx")
                edge = self.edge_detect()
                if edge == 0:
                    # 底部右侧红外光电
                    ad2 = self.adc_data[2]
                    # 底部后方红外光电
                    ad3 = self.adc_data[3]
                    # 底部左侧红外光电
                    ad4 = self.adc_data[4]
                    self.move_cmd(self.basic_speed * self.mov_p, self.basic_speed * self.mov_p)
                    time.sleep(0.01)
                    if self.mov_p > 75:
                        self.mov_p -= 1
                    io_4 = self.io_data[5]
                    if not io_4:
                        self.move_cmd(0, 0)
                        time.sleep(0.3)
                        init_time = time.time()
                        mov_speed = 3100
                        while self.tag_id == 1 or (self.tag_id == -1 and not self.io_data[5]):
                            self.move_cmd(mov_speed, mov_speed)
                            time.sleep(0.02)
                            # 左前检测到边缘
                            edge = self.edge_detect()
                            if edge == 1:
                                # print("xxxxyxtxjytyjygkhskgihbdihids")
                                # self.move_cmd(0, 0)
                                # time.sleep(0.01)
                                nd = 0
                                while 1:
                                    ad0 = self.adc_data[0]
                                    if ad0 > 500:
                                        nd += 1
                                        if nd >= 35:
                                            break
                                        self.move_cmd(1200, 1200)
                                        time.sleep(0.001)
                                        print("222")
                                    else:
                                        break
                                self.move_cmd(-3500, -3500)
                                time.sleep(0.1)
                                self.move_cmd(-3500, -3500)
                                time.sleep(0.1)
                                self.move_cmd(3500, -3500)
                                time.sleep(0.1)
                                break
                                # 右前检测到边缘
                            if edge == 2:
                                nd = 0
                                while 1:
                                    ad0 = self.adc_data[0]
                                    if ad0 > 500:
                                        nd += 1
                                        if nd >= 35:
                                            break
                                        self.move_cmd(1200, 1200)
                                        time.sleep(0.001)
                                        print("222")
                                    else:
                                        break
                                # print("xxxxyxtxjytyjygkhskgihbdihids")
                                # self.move_cmd(0, 0)
                                # time.sleep(0.01)
                                self.move_cmd(-3500, -3500)
                                time.sleep(0.1)
                                self.move_cmd(-3500, 3500)
                                time.sleep(0.03)
                                break
                            # 前方两个检测到边缘
                            if edge == 5:
                                nd = 0
                                while 1:
                                    ad0 = self.adc_data[0]
                                    if ad0 > 500:
                                        nd += 1
                                        if nd >= 35:
                                            break
                                        self.move_cmd(1200, 1200)
                                        time.sleep(0.001)
                                        print("222")
                                    else:
                                        break
                                # print("xxxxyxtxjytyjygkhskgihbdihids")
                                # self.move_cmd(0, 0)
                                # time.sleep(0.01)
                                self.move_cmd(-3000, -3000)
                                time.sleep(0.1)
                                self.move_cmd(3500, -3500)
                                time.sleep(0.03)
                                break
                            if time.time() - init_time >= 5:
                                mov_speed = 5000
                        if self.tag_id == 2:
                            self.move_cmd(0, 0)
                            time.sleep(0.8)
                            self.move_cmd(-3500, -2000)
                            time.sleep(0.13)
                            n4 = 0
                            while 1:
                                edge = self.edge_detect()
                                time.sleep(0.05)
                                n4 += 1
                                if edge != 0 or n4 >= 16:
                                    self.bianyuanjiance()
                                    break

                    else:
                        if ad2 < 1000 or ad3 < 1000:
                            n1 = 0
                            while 1:
                                self.move_cmd(2000, -2000)
                                time.sleep(0.02)
                                n1 = n1 + 1
                                io_4 = self.io_data[5]
                                if io_4 == 0 or n1 > 40:
                                    self.move_cmd(0, 0)
                                    time.sleep(0.5)
                                    break
                        if ad4 < 1000:
                            n1 = 0
                            while 1:
                                self.move_cmd(-2000, 2000)
                                time.sleep(0.02)
                                n1 = n1 + 1

                                io_4 = self.io_data[5]
                                if io_4 == 0 or n1 > 40:
                                    self.move_cmd(0, 0)
                                    time.sleep(0.5)
                                    break

                # 左前检测到边缘
                if edge == 1:
                    self.move_cmd(-3500, -3500)
                    time.sleep(0.05)
                    self.move_cmd(3500, -3500)
                    time.sleep(0.03)
                    self.mov_p = 80
                # 右前检测到边缘
                if edge == 2:
                    # self.move_cmd(0, 0)
                    # time.sleep(0.01)
                    self.move_cmd(-3500, -3500)
                    time.sleep(0.1)
                    self.move_cmd(-3500, 3500)
                    time.sleep(0.03)
                    self.mov_p = 80
                # 右后检测到边缘
                if edge == 3:
                    # self.move_cmd(0, 0)
                    # time.sleep(0.01)
                    self.move_cmd(3500, 3500)
                    time.sleep(0.1)
                    self.move_cmd(3500, -3500)
                    time.sleep(0.03)
                    self.mov_p = 80
                # 左后检测到边缘
                if edge == 4:
                    # self.move_cmd(0, 0)
                    # time.sleep(0.01)
                    self.move_cmd(3500, 3500)
                    time.sleep(0.1)
                    self.move_cmd(-3500, 3500)
                    time.sleep(0.03)
                    self.mov_p = 80
                # 前方两个检测到边缘
                if edge == 5:
                    # self.move_cmd(0, 0)
                    # time.sleep(0.01)
                    self.move_cmd(-3500, -3500)
                    time.sleep(0.1)
                    self.move_cmd(3500, -3500)
                    time.sleep(0.03)
                    self.mov_p = 80
                # 后方两个检测到
                if edge == 6:
                    self.move_cmd(3500, 3500)
                    time.sleep(0.1)
                # 左侧两个检测到边缘
                if edge == 7:
                    # self.move_cmd(0, 0)
                    # time.sleep(0.01)
                    self.move_cmd(5000, -3500)
                    time.sleep(0.1)
                    self.move_cmd(3500, 3500)
                    time.sleep(0.03)

                # 右侧两个检测到边缘
                if edge == 8:
                    # self.move_cmd(0, 0)
                    # time.sleep(0.01)
                    self.move_cmd(-3500, 5000)
                    time.sleep(0.1)
                    self.move_cmd(3500, 3500)
                    time.sleep(0.03)
            if stage == 0:
                self.tag_monitor_switch = False
                print("taixia")

                # 在台下后方对擂台
                # print("fence")

                if not self.paltform_detect():
                    fence = self.fence_detect()
                    print(fence)
                    if fence == 1:
                        self.move_cmd(0, 0)
                        self.move_cmd(2000, 2000)
                        wait(0.1)
                        self.move_cmd(-9999, -9999)
                        time.sleep(0.7)
                        self.move_cmd(0, 0)
                        if self.side_away_detection():
                            print("failed to get on platform")
                            self.move_cmd(2000, 2000)
                            time.sleep(0.3)
                        else:
                            print("succeed to get on platform")
                            # self.fastest_turn(2, 0)
                            self.move_cmd(4000, -4000)
                            time.sleep(0.1)
                    # 左侧对擂台
                    if (2 <= fence <= 8) or (15 <= fence <= 18):
                        self.move_cmd(0, 0)
                        time.sleep(0.02)
                        while 1:
                            print(3)
                            ad1 = self.adc_data[1]
                            io_4 = self.io_data[5]
                            ad4 = self.adc_data[4]
                            ad0 = self.adc_data[0]
                            ad6 = self.adc_data[6]
                            ad7 = self.adc_data[7]
                            if io_4 == 0 and ad6 < self.RD and ad4 > 1000 and ad0 > self.FD and ad7 < self.BD:
                                # time.sleep(0.5)
                                self.move_cmd(2000, 2000)
                                time.sleep(0.2)
                                self.move_cmd(-9999, -9999)
                                time.sleep(0.8)
                                break
                            else:
                                self.move_cmd(1500, -1500)
                                time.sleep(0.1)
                    """前方对擂台
                    if fence == 3:
                        while 1:
                            ad1 = self.adc_data[1]
                            ad4 = self.adc_data[4]
                            ad0 = self.adc_data[0]
                            ad6 = self.adc_data[6]
                            ad7 = self.adc_data[7]
                            if io_4 == 0 and ad6 < 500 and ad4 > 1000 and ad0 > 500 and ad7 < 500:
                                #time.sleep(0.5)
                                self.move_cmd(2000, 2000)
                                time.sleep(0.1)
                                self.move_cmd(-9999, -9999)
                                time.sleep(0.8)
                                break
                            else:
                                self.move_cmd(1000, -1000)
                                time.sleep(0.2)
                    # 右侧对擂台
                    if fence == 4:
                        self.move_cmd(0, 0)
                        time.sleep(0.02)
                        while 1:
                            ad1 = self.adc_data[1]
                            io_4 = self.io_data[4]
                            ad4 = self.adc_data[4]
                            ad0 = self.adc_data[0]
                            ad6 = self.adc_data[6]
                            ad7 = self.adc_data[7]
                            if io_4 == 0 and ad6 < 500 and ad4 > 1000 and ad0 > 500 and ad7 < 500:
                                #time.sleep(0.2)
                                self.move_cmd(2000, 2000)
                                time.sleep(0.1)
                                self.move_cmd(-15000, -15000)
                                time.sleep(0.8)
                                break
                            else:
                                self.move_cmd(-1000, 1000)
                                time.sleep(0.2)
                    # 前左检测到围栏
                    if fence == 5:
                        self.move_cmd(-3500, -3500)
                        time.sleep(0.7)
                    # 前右检测到围栏
                    if fence == 6:
                        self.move_cmd(-3500, -3500)
                        time.sleep(0.07)
                    # 后有检测到围栏
                    if fence == 7:
                        self.move_cmd(3500, 3500)
                        time.sleep(0.07)
                    # 后左检测到围栏
                    if fence == 8:
                        self.move_cmd(3500, 3500)
                        time.sleep(0.07)"""
                    # 前方或后方有台上敌人
                    if fence == 9:
                        self.move_cmd(5000, -5000)
                        time.sleep(0.1)
                        self.move_cmd(3500, 3500)
                        time.sleep(0.4)
                    # 左侧或右侧有台上敌人
                    if fence == 10:
                        self.move_cmd(3500, 3500)
                        time.sleep(0.4)
                    # 前方、左侧和右侧检测到围栏
                    if fence == 11:
                        while 1:
                            ad7 = self.adc_data[7]
                            ad6 = self.adc_data[6]
                            ad8 = self.adc_data[8]
                            io_4 = self.io_data[5]
                            ad3 = self.adc_data[3]
                            if ad7 < self.BD and ad6 < 1000 and ad3 > 1000 or ad7 < self.BD and ad8 < 500 and io_4 == 1:
                                self.move_cmd(-2000, -2000)
                                time.sleep(1.5)
                                break
                            else:
                                self.move_cmd(1000, -1000)
                                time.sleep(0.1)

                    # 前右后检测到围栏
                    if fence == 12:
                        self.move_cmd(3000, 6000)
                        time.sleep(0.1)
                    # 前左后检测到围栏
                    if fence == 13:
                        self.move_cmd(6000, 3000)
                        time.sleep(0.1)
                    # 右左后检测到围栏
                    if fence == 14:
                        self.move_cmd(-1000, 1000)
                        time.sleep(0.02)
                        self.move_cmd(3500, 3500)
                        time.sleep(0.3)
                    # 前右检测到擂台
                    '''if fence == 15:
                        self.move_cmd(0, 0)
                        time.sleep(0.2)
                        while 1:
                            ad1 = self.adc_data[1]
                            io_4 = self.io_data[4]
                            ad4 = self.adc_data[4]
                            ad8 = self.adc_data[8]
                            if io_4 == 1 and ad6 < 500 and ad8 > 500:
                                #time.sleep(0.2)
                                break
                            else:
                                self.move_cmd(1000, -1000)
                                time.sleep(0.1)
                                print(1)
                    #  前左检测到擂台
                    if fence == 16:
                        self.move_cmd(0, 0)
                        time.sleep(0.2)
                        while 1:
                            ad1 = self.adc_data[1]
                            io_4 = self.io_data[4]
                            ad4 = self.adc_data[4]
                            ad8 = self.adc_data[8]
                            if io_4 == 1 and ad6 < 500 and ad8 > 500:
                                #time.sleep(0.2)
                                break
                            else:
                                self.move_cmd(1000, -1000)
                                time.sleep(0.1)
                                print(2)
                            
                    # 在台下，后方和右侧对擂台其他传感器没检测到
                    if fence == 17:
                        self.move_cmd(0, 0)
                        time.sleep(0.2)
                        while 1:
                            ad1 = self.adc_data[1]
                            io_4 = self.io_data[4]
                            ad4 = self.adc_data[4]
                            ad6 = self.adc_data[6]
                            if io_4 == 0 and ad6 < 500 and ad4 > 1000:
                                #time.sleep(0.5)
                                self.move_cmd(3500, 3500)
                                time.sleep(0.1)
                                break
                            else:
                                self.move_cmd(3000, -3000)
                                time.sleep(0.05)
                    # 在台下，后方和左侧对擂台其他传感器没检测到
                    if fence == 18:
                        self.move_cmd(0, 0)
                        time.sleep(0.02)
                        while 1:
                            ad1 = self.adc_data[1]
                            ad4 = self.adc_data[4]
                            ad6 = self.adc_data[6]
                            io_4 = self.io_data[4]
                            if io_4 == 0 and ad6 < 500 and ad4 > 1000:
                                #time.sleep(0.05)
                                self.move_cmd(3500, 3500)
                                time.sleep(0.05)
                                break
                            else:
                                self.move_cmd(-3500, 3500)
                                time.sleep(0.1)######
    
    '''

    def mortor_test(self):
        self.move_cmd(3500, -3500)
        time.sleep(0.7)
        self.move_cmd(0, 0)

    # 停止
    def stop(self):
        self.move_cmd(0, 0)


if __name__ == '__main__':
    match_demo = MatchDemo()
    # match_demo.stop()
    match_demo.start_match()
