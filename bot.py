import threading
import time
from abc import ABCMeta, abstractmethod

import cv2
from apriltag import Detector, DetectorOptions

from repo.uptechStar.module.screen import Screen
from repo.uptechStar.module.timer import delay_ms
from repo.uptechStar.module.up_controller import UpController


class Bot(metaclass=ABCMeta):
    tag_detector = Detector(DetectorOptions(families='tag36h11')).detect
    screen = Screen(init_screen=False)
    controller = UpController(debug=False, fan_control=False)

    def __init__(self, config_path: str = './config.json', team_color: str = 'blue'):
        """

        :param config_path: the path to the config,but it hasn't been put into use
        :param team_color:
        """
        self.load_config(config_path=config_path)

        self._tag_id = -1
        self._tag_monitor_switch = True
        self._enemy_tag = None
        self._ally_tag = None

        self._set_tags(team_color=team_color)

        self.apriltag_detect_start()

    # region utilities
    def load_config(self, config_path: str):
        """
        load configuration form json
        :param config_path:
        :return:
        """

        pass

    # endregion

    # region tag detection
    def _set_tags(self, team_color: str = 'blue'):
        """
        set the ally/enemy tag according the team color

        blue: ally: 1 ; enemy: 2
        yellow: ally: 2 ; enemy: 1
        :param team_color: blue or yellow
        :return:
        """
        if team_color == 'blue':
            self._enemy_tag = 2
            self._ally_tag = 1
        elif team_color == 'yellow':
            self._enemy_tag = 1
            self._ally_tag = 2

    def apriltag_detect_start(self):
        """
        start the tag-detection thread and set it to daemon
        :return:
        """
        apriltag_detect = threading.Thread(target=self.apriltag_detect_thread,
                                           name="apriltag_detect_detect")
        apriltag_detect.daemon = True
        apriltag_detect.start()

    def apriltag_detect_thread(self, single_tag_mode: bool = True, print_tag_id: bool = False,
                               check_interval: int = 50):
        """
        这是一个线程函数，它从摄像头捕获视频帧，处理帧以检测 AprilTags，
        :param check_interval:
        :param single_tag_mode: if check only a single tag one time
        :param print_tag_id: if print tag id on check
        :return:
        """
        print("detect start")
        # 使用 cv2.VideoCapture(0) 创建视频捕获对象，从默认摄像头（通常是笔记本电脑的内置摄像头）捕获视频。
        cap = cv2.VideoCapture(0)

        # 使用 cap.set(3, w) 和 cap.set(4, h) 设置帧的宽度和高度为 640x480，帧的 weight 为 320。
        w = 640
        h = 480
        weight = 320
        cap.set(3, w)
        cap.set(4, h)

        cup_w = int((w - weight) / 2)
        cup_h = int((h - weight) / 2) + 50

        print_interval: float = 1.2
        start_time = time.time()
        while True:

            if self.tag_monitor_switch:  # 台上开启 台下关闭 节约性能
                # 在循环内，从视频捕获对象中捕获帧并将其存储在 frame 变量中。然后将帧裁剪为中心区域的 weight x weight 大小。
                _, frame = cap.read()
                frame = frame[cup_h:cup_h + weight, cup_w:cup_w + weight]
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 将帧转换为灰度并存储在 gray 变量中。
                # 使用 AprilTag 检测器对象（self.tag_detector）在灰度帧中检测 AprilTags。检测到的标记存储在 tags 变量中。
                tags = self.tag_detector(gray)
                if tags and single_tag_mode:
                    self.tag_id = tags[0].tag_id
                    if print_tag_id and time.time() - start_time > print_interval:
                        print(f"#DETECTED TAG: [{self.tag_id}]")
                        start_time = time.time()
                delay_ms(check_interval)
            else:
                # TODO: This delay may not be correct,since it could cause wrongly activate enemy box action
                delay_ms(1500)

    # endregion

    # region properties
    @property
    def tag_id(self):
        """

        :return:  current tag id
        """
        return self._tag_id

    @tag_id.setter
    def tag_id(self, new_tag_id: int):
        """
        setter for  current tag id
        :param new_tag_id:
        :return:
        """
        self._tag_id = new_tag_id

    @property
    def tag_monitor_switch(self):
        return self._tag_monitor_switch

    @tag_monitor_switch.setter
    def tag_monitor_switch(self, switch: bool):
        """
        setter for the switch
        :param switch:
        :return:
        """
        self._tag_monitor_switch = switch

    @property
    def ally_tag(self):
        return self._ally_tag

    @property
    def enemy_tag(self):
        return self._enemy_tag

    # endregion

    @abstractmethod
    def Battle(self, interval, normal_spead):
        """
        the main function
        :param interval:
        :param normal_spead:
        :return:
        """
        pass
