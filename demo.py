import apriltag
import cv2
import threading
import time

from up_controller import UpController
from uptech import UpTech


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

    # blue
    enemy_tag = 1

    friendly_tag = 2

    # # yellow
    # enemy_tag = 2
    #
    # friendly_tag = 1

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

        self.tag_monitor_switch = False

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

        if ad1 <= 2580:
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
        # print(f"the edge case is{bin(judge_bin)}||{judge_bin}")
        return judge_dict.get(judge_bin, 606)

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
            time.sleep(0.05)
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
            time.sleep(0.05)
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
            time.sleep(0.05)
            self.move_cmd(3500, 3500)
            time.sleep(0.03)
            # 右侧两个检测到边缘
        if edge1 == 8:
            # self.move_cmd(0, 0)
            # time.sleep(0.01)
            self.move_cmd(-3500, 5000)
            time.sleep(0.05)
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

    # 主函数直接运行
    def start_match(self):

        # '''
        while True:
            # 底部左侧红外光电
            ad4 = self.adc_data[4]
            if ad4 < 1000:
                self.move_cmd(-7200, -7200)
                time.sleep(0.5)
                break
        # '''
        while 1:
            # xxy=xxy+1
            # if  xxy > 100:
            # print("xxxxxxxxxxxxxxxx")
            # break
            stage = self.paltform_detect()
            # time.sleep(0.001)
            # print(stage)
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
                    self.move_cmd(3000, 3000)
                    time.sleep(0.05)
                    io_4 = self.io_data[5]
                    if io_4 == 0:
                        self.move_cmd(0, 0)
                        time.sleep(0.3)
                        init_time = time.time()
                        basic_speed = 3140
                        while self.tag_id == self.enemy_tag or self.tag_id == -1:
                            self.move_cmd(basic_speed, basic_speed)
                            time.sleep(0.02)
                            # 左前检测到边缘
                            edge = self.edge_detect()
                            if time.time() - init_time > 4.5:
                                basic_speed = 6500
                            if edge == 1:
                                # print("xxxxyxtxjytyjygkhskgihbdihids")
                                # self.move_cmd(0, 0)
                                # time.sleep(0.01)
                                nd = 0
                                while 1:
                                    ad0 = self.adc_data[0]
                                    if ad0 > 500:
                                        nd += 1
                                        if nd > 55:
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
                                        if nd > 55:
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
                                        if nd > 55:
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
                        if self.tag_id == self.friendly_tag:
                            self.move_cmd(0, 0)
                            time.sleep(0.5)
                            self.move_cmd(-3500, -2000)
                            time.sleep(0.08)
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
                # 右前检测到边缘
                if edge == 2:
                    # self.move_cmd(0, 0)
                    # time.sleep(0.01)
                    self.move_cmd(-3500, -3500)
                    time.sleep(0.05)
                    self.move_cmd(-3500, 3500)
                    time.sleep(0.03)
                # 右后检测到边缘
                if edge == 3:
                    # self.move_cmd(0, 0)
                    # time.sleep(0.01)
                    self.move_cmd(3500, 3500)
                    time.sleep(0.1)
                    self.move_cmd(3500, -3500)
                    time.sleep(0.03)
                # 左后检测到边缘
                if edge == 4:
                    # self.move_cmd(0, 0)
                    # time.sleep(0.01)
                    self.move_cmd(3500, 3500)
                    time.sleep(0.1)
                    self.move_cmd(-3500, 3500)
                    time.sleep(0.03)
                # 前方两个检测到边缘
                if edge == 5:
                    # self.move_cmd(0, 0)
                    # time.sleep(0.01)
                    self.move_cmd(-3500, -3500)
                    time.sleep(0.05)
                    self.move_cmd(3500, -3500)
                    time.sleep(0.03)
                # 后面两个检测到边缘
                if edge == 6:
                    self.move_cmd(3800, 3800)
                    time.sleep(0.05)
                # 左侧两个检测到边缘
                if edge == 7:
                    # self.move_cmd(0, 0)
                    # time.sleep(0.01)
                    self.move_cmd(5000, -3500)
                    time.sleep(0.05)
                    self.move_cmd(3500, 3500)
                    time.sleep(0.03)
                # 右侧两个检测到边缘
                if edge == 8:
                    # self.move_cmd(0, 0)
                    # time.sleep(0.01)
                    self.move_cmd(-3500, 5000)
                    time.sleep(0.05)
                    self.move_cmd(3500, 3500)
                    time.sleep(0.03)
            if stage == 0:
                self.tag_monitor_switch = False
                print("taixia")
                fence = self.fence_detect()
                # 在台下后方对擂台
                # print("fence")
                print(fence)
                if fence == 1:
                    self.move_cmd(0, 0)
                    time.sleep(0.02)
                    self.move_cmd(2500, 2500)
                    time.sleep(0.2)
                    self.move_cmd(-7200, -7200)
                    time.sleep(0.5)
                # 左侧对擂台
                if (2 <= fence <= 8) or (15 <= fence <= 18):
                    self.move_cmd(0, 0)
                    time.sleep(0.02)
                    while 1:
                        print(3)

                        io_4 = self.io_data[5]
                        ad4 = self.adc_data[4]
                        ad0 = self.adc_data[0]
                        ad6 = self.adc_data[6]
                        ad7 = self.adc_data[7]
                        if io_4 == 0 and ad6 < self.RD and ad4 > 1000 and ad0 > self.FD and ad7 < self.BD:
                            # time.sleep(0.5)
                            self.move_cmd(2000, 2000)
                            time.sleep(0.2)
                            self.move_cmd(-7200, -7200)
                            time.sleep(0.4)
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
                            self.move_cmd(-7200, -7200)
                            time.sleep(0.5)
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
                            time.sleep(0.5)
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
    match_demo.start_match()
