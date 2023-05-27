import threading
import time

from repo.uptechStar.module.up_controller import UpController
from typing import Optional, Union
import cv2
import apriltag


class BattleBot:
    controller = UpController(debug=False, fan_control=False)

    def __init__(self, config_path: str = './config.json'):
        self.load_config(config_path=config_path)

        self.at_detector = apriltag.Detector(apriltag.DetectorOptions(families='tag36h11 tag25h9'))
        self.apriltag_width = 0
        self.tag_id = -1
        apriltag_detect = threading.Thread(target=self.apriltag_detect_thread)
        apriltag_detect.daemon = True
        apriltag_detect.start()

        self.tag_monitor_switch = True

    def apriltag_detect_thread(self):
        """
        这是一个线程函数，它从摄像头捕获视频帧，处理帧以检测 AprilTags，
        并在视频帧上显示 AprilTag 检测结果（如果有）。这是这个函数的概述：

        1.使用 cv2.VideoCapture(0) 创建视频捕获对象，从默认摄像头（通常是笔记本电脑的内置摄像头）捕获视频。
        2.使用 cap.set(3, w) 和 cap.set(4, h) 设置帧的宽度和高度为 640x480，帧的 weight 为 320。
        3.开始一个 while 循环，直到用户按下 'q' 键结束循环。
        4.在循环内，从视频捕获对象中捕获帧并将其存储在 frame 变量中。然后将帧裁剪为中心区域的 weight x weight 大小。
        5.将帧转换为灰度并存储在 gray 变量中。
        6.使用 AprilTag 检测器对象（self.at_detector）在灰度帧中检测 AprilTags。检测到的标记存储在 tags 变量中。
        7.对于每个检测到的标记，在原始帧上打印其标记 ID 并用圆圈标记其角落。
        8.使用 cv2.imshow("img", frame) 显示带有 AprilTag 检测结果（如果有）的原始帧。
        9.如果用户按下 'q' 键，则结束循环并关闭视频
        """
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

    def load_config(self, config_path: str):
        """
        load configuration form json
        :param config_path:
        :return:
        """

        pass

    def check_sensors(self):
        """
        sensors function check
        :return:
        """
        pass

    def on_stage_check(self, using_dst_assistance: bool = True):
        """
        check if the bot is on the stage
        :param using_dst_assistance:
        :return:
        """

    def load_models(self, model_path: str):
        """
        load vision model to memory
        :param model_path:
        :return:
        """
        pass

    def open_camera(self):
        """

        :return:
        """

    def Battle(self):
        """
        the main function of the BattleBot
        :return:
        """
        print('battle starts')
        """
        rr 0
        fr 1
        fl 2
        rl 3
        l2 8
        r2 7
        fr 6
        fb 4
        rb 5
        
        l_gray io 1
        r_gray io 0
        """
        try:
            while True:
                print('holding')
                time.sleep(1)
                if self.controller.adc_all[8] > 1650 and self.controller.adc_all[7]:
                    self.controller.move_cmd(-10000, -10000)
                    time.sleep(0.8)
                    break
            edge_a = 1650
            while True:
                edge_rr_sensor = self.controller.adc_all[0]
                edge_fr_sensor = self.controller.adc_all[1]
                edge_fl_sensor = self.controller.adc_all[2]
                edge_rl_sensor = self.controller.adc_all[3]
                # l_gray = self.controller.io_all[1]
                # r_gray = self.controller.io_all[0]
                if edge_fl_sensor < edge_a:
                    self.controller.move_cmd(-4000, -4000)
                    time.sleep(0.5)
                    # front left edge encounter
                    self.controller.move_cmd(4000, -4000)
                    time.sleep(1.5)
                    self.controller.move_cmd(5000, 5000)
                    time.sleep(1)
                if edge_fr_sensor < edge_a:
                    # front left edge encounter
                    self.controller.move_cmd(-4000, -4000)
                    time.sleep(0.5)
                    self.controller.move_cmd(-4000, 4000)
                    time.sleep(1.5)
                    self.controller.move_cmd(5000, 5000)
                    time.sleep(1)
                if edge_rl_sensor < edge_a:
                    # front left edge encounter
                    self.controller.move_cmd(-4000, -4000)
                    time.sleep(0.5)
                    self.controller.move_cmd(4000, -4000)
                    time.sleep(1.5)
                    self.controller.move_cmd(5000, 5000)
                    time.sleep(1)
                if edge_rr_sensor < edge_a:
                    # front left edge encounter
                    self.controller.move_cmd(-4000, -4000)
                    time.sleep(0.5)
                    self.controller.move_cmd(-4000, 4000)
                    time.sleep(1.5)
                    self.controller.move_cmd(5000, 5000)
                    time.sleep(1)
                # if not l_gray or not r_gray:
                #     self.controller.move_cmd(-4000, -4000)
                #     time.sleep(1.5)
                #     self.controller.move_cmd(5000, 5000)
                #     time.sleep(0.5)
                self.controller.move_cmd(1000, 1000)
        except KeyboardInterrupt:
            print('exiting')
            self.controller.move_cmd(0, 0)


if __name__ == '__main__':
    bot = BattleBot()
    bot.Battle()
