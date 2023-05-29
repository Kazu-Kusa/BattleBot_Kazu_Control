from random import randint
import threading
import time
from repo.uptechStar.module.up_controller import UpController
from repo.uptechStar.module.timer import delay_ms
# from typing import Optional, Union
import cv2
import apriltag
from repo.uptechStar.module.screen import Screen


class BattleBot:
    controller = UpController(debug=False, fan_control=False)

    def __init__(self, config_path: str = './config.json'):
        self.load_config(config_path=config_path)
        self.screen = Screen(init_screen=False)
        self.at_detector = apriltag.Detector(apriltag.DetectorOptions(families='tag36h11 tag25h9'))
        self.apriltag_width = 0

        self.apriltag_detect_start()
        self._tag_id = -1
        self._tag_monitor_switch = True
        self._enemy_tag = 2
        self._ally_tag = 1

    def apriltag_detect_start(self):
        apriltag_detect = threading.Thread(target=self.apriltag_detect_thread)
        apriltag_detect.daemon = True
        apriltag_detect.start()

        self._tag_monitor_switch = True
        self._enemy_tag = 2
        self._ally_tag = 1

    @property
    def tag_id(self):
        return self._tag_id

    @tag_id.setter
    def tag_id(self, new_tag_id: int):
        self._tag_id = new_tag_id

    @property
    def tag_monitor_switch(self):
        return self._tag_monitor_switch

    @tag_monitor_switch.setter
    def tag_monitor_switch(self, switch: bool):
        self._tag_monitor_switch = switch

    @property
    def enemy_tag(self):
        return self._enemy_tag

    @property
    def ally_tag(self):
        return self._ally_tag

    def apriltag_detect_thread(self, single_tag_mode: bool = True, print_tag_id: bool = False,
                               check_interval: int = 50):
        """
        这是一个线程函数，它从摄像头捕获视频帧，处理帧以检测 AprilTags，
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
                # 使用 AprilTag 检测器对象（self.at_detector）在灰度帧中检测 AprilTags。检测到的标记存储在 tags 变量中。
                tags = self.at_detector.detect(gray)
                if tags and single_tag_mode:
                    self.tag_id = tags[0].tag_id
                    if print_tag_id and time.time() - start_time > print_interval:
                        print(f"#DETECTED TAG: [{self.tag_id}]")
                        start_time = time.time()
                delay_ms(check_interval)
            else:
                delay_ms(1500)

    def action_BT(self, back_speed: int = 5000, back_time: int = 120,
                  turn_speed: int = 6000, turn_time: int = 120,
                  b_multiplier: float = 0, t_multiplier: float = 0,
                  turn_type: int = randint(0, 1)):
        """
        function that execute the action of  backwards and turns
        :param back_speed:
        :param back_time:
        :param turn_speed:
        :param turn_time:
        :param b_multiplier:
        :param t_multiplier:
        :param turn_type: 0 for left,1 for right,default random
        :return:
        """
        if b_multiplier:
            back_speed = int(back_speed * b_multiplier)
        self.controller.move_cmd(-back_speed, -back_speed)
        delay_ms(back_time)

        if t_multiplier:
            turn_speed = int(turn_speed)
        if turn_type:
            self.controller.move_cmd(-turn_speed, turn_speed)
        else:
            self.controller.move_cmd(turn_speed, -turn_speed)
        delay_ms(turn_time)
        self.controller.move_cmd(0, 0)

    def action_T(self, turn_type: int = randint(0, 1), turn_speed: int = 5000, turn_time: int = 130,
                 multiplier: float = 0):
        if multiplier:
            turn_speed = int(turn_speed * multiplier)

        if turn_type:
            self.controller.move_cmd(turn_speed, -turn_speed)
        else:
            self.controller.move_cmd(-turn_speed, turn_speed)
        delay_ms(turn_time)

    def normal_behave(self, adc_list: list[int], io_list: list[int], edge_a: int = 1680, edge_multiplier: float = 0):
        """
        handles the normal edge case using both adc_list and io_list.
        but well do not do anything if no edge case
        :param adc_list:
        :param io_list:
        :param edge_a:
        :return:
        """
        self.screen.ADC_Led_SetColor(0, self.screen.COLOR_BLUE)
        edge_rr_sensor = adc_list[0]
        edge_fr_sensor = adc_list[1]
        edge_fl_sensor = adc_list[2]
        edge_rl_sensor = adc_list[3]

        l_gray = io_list[6]
        r_gray = io_list[7]
        high_spead = edge_rl_sensor + edge_fl_sensor + edge_fr_sensor + edge_rr_sensor
        if edge_multiplier:
            high_spead = int(high_spead * edge_multiplier)
        backing_time = 180
        rotate_time = 130

        if l_gray + r_gray <= 1:
            self.action_BT(back_speed=high_spead, back_time=backing_time,
                           turn_speed=high_spead, turn_time=rotate_time,
                           t_multiplier=0.6)
        elif edge_fl_sensor < edge_a:
            self.action_BT(back_speed=high_spead, back_time=backing_time,
                           turn_speed=high_spead, turn_time=rotate_time,
                           t_multiplier=0.6, turn_type=1)

        elif edge_fr_sensor < edge_a:
            self.action_BT(back_speed=high_spead, back_time=backing_time,
                           turn_speed=high_spead, turn_time=rotate_time,
                           t_multiplier=0.6, turn_type=0)

        elif edge_rl_sensor < edge_a:
            self.action_T(turn_type=1)

        elif edge_rr_sensor < edge_a:
            self.action_T(turn_type=0)

    def load_config(self, config_path: str):
        """
        load configuration form json
        :param config_path:
        :return:
        """

        pass

    def on_ally_box(self, speed: int = 5000, multiplier: float = 0):
        if multiplier:
            speed = int(multiplier * speed)
        self.controller.move_cmd(-speed, speed)
        delay_ms(200)

    def check_surround(self, adc_list: list[int], baseline=2000):
        """

        :param adc_list:
        :param baseline:
        :return:
        """
        self.screen.ADC_Led_SetColor(0, self.screen.COLOR_CYAN)
        timestep = 120
        speed = 6000

        if self.tag_id == self.ally_tag and adc_list[4] > baseline:
            self.on_ally_box(speed, 0.3)
        elif self.tag_id == self.enemy_tag and adc_list[4] > baseline:
            self.on_enemy_box(speed, 0.4)
        elif adc_list[4] > baseline:
            self.on_enemy_car(speed, 0.5)
        elif adc_list[8] > baseline:
            self.on_thing_surrounding(1)
        elif adc_list[7] > baseline:
            self.on_thing_surrounding(2)
        elif adc_list[5] > baseline:
            self.on_thing_surrounding(3)

    def util_edge(self, using_gray: bool = True, using_edge_sensor: bool = False, edge_a: int = 1800):
        if using_gray:
            io_list = self.controller.ADC_IO_GetAllInputLevel(make_str_list=False)
            while int(io_list[6]) + int(io_list[7]) > 1:
                io_list = self.controller.ADC_IO_GetAllInputLevel(make_str_list=False)
        elif using_edge_sensor:
            adc_list = self.controller.ADC_Get_All_Channel()
            while adc_list[1] < edge_a or adc_list[2] < edge_a:
                adc_list = self.controller.ADC_Get_All_Channel()

    def on_enemy_box(self, speed: int = 8000, multiplier: float = 0):
        if multiplier:
            speed = int(multiplier * speed)
        self.controller.move_cmd(speed, speed)
        self.util_edge()
        self.controller.move_cmd(-speed, -speed)
        delay_ms(160)
        self.controller.move_cmd(0, 0)

    def on_enemy_car(self, speed: int = 8000, multiplier: float = 0):
        if multiplier:
            speed = int(multiplier * speed)
        self.controller.move_cmd(speed, speed)
        self.util_edge()
        if multiplier:
            speed = int(multiplier * speed)
        self.controller.move_cmd(-speed, -speed)
        delay_ms(160)
        self.controller.move_cmd(0, 0)

    def on_thing_surrounding(self, position_type: int = 0):
        """
        1 for left
        2 for right
        3 for behind
        :param position_type:
        :return:
        """
        rotate_time = 60
        rotate_speed = 5000
        if position_type == 1:
            self.controller.move_cmd(-rotate_speed, rotate_speed)
        else:
            self.controller.move_cmd(rotate_speed, -rotate_speed)
            if position_type == 3:
                rotate_time = 2 * rotate_time
        delay_ms(rotate_time)
        self.controller.move_cmd(0, 0)

    def Battle(self, interval: int = 10, normal_spead: int = 3000):
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
        [edge_rr, edge_fr, edge_fl, edge_rl, fb,rb,fr,r2,l2]
        {0:edge_rr,1:edge_fr,2:edge_fl, 3:edge_rl, 4:fb,5:rb,6:fr,7:r2,8:l2}
        
        {0:r_gray,1:l_gray}
        l_gray io 1
        r_gray io 0
        """
        try:

            while True:
                print('holding')
                delay_ms(150)
                temp_list = self.controller.ADC_Get_All_Channel()
                if temp_list[8] > 1800 and temp_list[7] > 1800:
                    print('dashing')
                    self.controller.move_cmd(-30000, -30000)
                    delay_ms(800)
                    self.controller.move_cmd(0, 0)
                    break
            while True:
                adc_list = self.controller.ADC_Get_All_Channel()
                io_list = self.controller.ADC_IO_GetAllInputLevel(make_str_list=False)
                self.normal_behave(adc_list, io_list, edge_a=1650, edge_multiplier=0.6)
                self.check_surround(adc_list, )
                self.controller.move_cmd(normal_spead, normal_spead)
                delay_ms(interval)

        except KeyboardInterrupt:
            self.controller.move_cmd(0, 0)
            print('exiting')


if __name__ == '__main__':
    bot = BattleBot()
    bot.controller.move_cmd(0, 0)
    # breakpoint()
    bot.Battle(interval=10, normal_spead=3000)
