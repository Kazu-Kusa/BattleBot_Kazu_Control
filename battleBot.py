from abc import ABCMeta, abstractmethod
from random import randint
import threading
import time
from typing import Callable
from time import perf_counter_ns
from repo.uptechStar.module.up_controller import UpController
from repo.uptechStar.module.timer import delay_ms
# from typing import Optional, Union
import cv2
from apriltag import Detector, DetectorOptions
from repo.uptechStar.module.screen import Screen
from repo.uptechStar.module.algrithm_tools import compute_inferior_arc, calculate_relative_angle
from repo.uptechStar.module.pid import PD_control, PID_control


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


class BattleBot(Bot):

    # region basic actions
    def action_BT(self, back_speed: int = 5000, back_time: int = 120,
                  turn_speed: int = 6000, turn_time: int = 120,
                  b_multiplier: float = 0, t_multiplier: float = 0,
                  turn_type: int = randint(0, 1), watch_behind: bool = False,
                  watcher_func: Callable[[], bool] = None):
        """
        function that execute the action of  backwards and turns
        open loop,actualized by delaying functions
        :param back_speed: the desired back speed,absolute value
        :param back_time:the desired duration of fall backing motion
        :param turn_speed:the desired turn speed,absolute value
        :param turn_time:the desired duration of turning motion
        :param b_multiplier: the multiplier that will be applied to the back_speed
        :param t_multiplier:the multiplier that will be applied to the turn_speed
        if no multiplier is provided ,then the actual speed will be same as the entered params
        :param turn_type: 0 for left,1 for right,default random
        :param watch_behind:if backing when use watcher
        :param watcher_func:watcher function returning boolean value,when true,stops the robot
        :return:
        """
        if b_multiplier:
            back_speed = int(back_speed * b_multiplier)
        self.controller.move_cmd(-back_speed, -back_speed)
        if watch_behind:
            end = perf_counter_ns() + back_time * 1000000
            while perf_counter_ns() < end:
                if watcher_func():
                    self.controller.move_cmd(0, 0)
                    break
        else:
            delay_ms(back_time)

        if t_multiplier:
            turn_speed = int(turn_speed * t_multiplier)
        if turn_type:
            self.controller.move_cmd(turn_speed, -turn_speed)
        else:
            self.controller.move_cmd(-turn_speed, turn_speed)
        delay_ms(turn_time)
        self.controller.move_cmd(0, 0)

    def action_T_PID(self, offset_angle: float = 90, step: int = 2):
        """

        :param step:
        :param offset_angle: positive for wise, negative for counter-wise
        :return:
        """

        def control(left: int, right: int) -> None:
            self.controller.move_cmd(left, right)
            # print(left)

        def evaluate() -> float:
            temp = self.controller.atti_all[2]

            return temp

        step_len = offset_angle / step
        for _ in range(step):
            current_angle = evaluate()
            target_angle = calculate_relative_angle(current_angle=current_angle, offset_angle=step_len)

            print(f'current_angle: {current_angle},target_angle: {target_angle}')

            PID_control(controller_func=control,
                        evaluator_func=evaluate,
                        error_func=compute_inferior_arc,
                        target=target_angle,
                        Kp=14, Kd=16e08, Ki=5e-09,
                        cs_limit=4000, target_tolerance=40,
                        smooth_window_size=3, end_pause=False, rip_round=6)
        self.controller.move_cmd(0, 0)

    def action_T_PD(self, offset_angle: float = 90):
        """

        :param offset_angle: positive for wise, negative for counter-wise
        :return:
        """

        def control(left: int, right: int) -> None:
            self.controller.move_cmd(left, right)

        def evaluate() -> float:
            return self.controller.atti_all[2]

        current_angle = evaluate()
        target_angle = calculate_relative_angle(current_angle=current_angle, offset_angle=offset_angle)

        print(f'current_angle: {current_angle},target_angle: {target_angle}')

        PD_control(controller_func=control,
                   evaluator_func=evaluate,
                   error_func=compute_inferior_arc,
                   target=target_angle,
                   Kp=3, Kd=500,
                   cs_limit=1500, target_tolerance=13)

    def action_T(self, turn_type: int = randint(0, 1), turn_speed: int = 5000, turn_time: int = 130,
                 multiplier: float = 0):
        """

        :param turn_type: <- turn_type == 0  or turn_type == 1 ->
        :param turn_speed:
        :param turn_time:
        :param multiplier:
        :return:
        """
        if multiplier:
            turn_speed = int(turn_speed * multiplier)

        if turn_type:
            self.controller.move_cmd(turn_speed, -turn_speed)
        else:
            self.controller.move_cmd(-turn_speed, turn_speed)
        delay_ms(turn_time)

    def action_D(self, dash_speed: int = -13000, dash_time: int = 500,
                 with_turn: bool = False):
        self.controller.move_cmd(dash_speed, dash_speed)
        delay_ms(dash_time)
        self.controller.move_cmd(0, 0)
        if with_turn:
            self.action_T(turn_speed=7000, turn_time=140)

    # endregion

    # region special actions
    def wait_start(self, baseline: int = 1800, check_interval: int = 50,
                   with_turn: bool = False, dash_time: int = 600) -> None:
        """
        hold still util the start signal is received
        :param check_interval:
        :param dash_time:
        :param baseline:
        :param with_turn:
        :return:
        """
        self.screen.ADC_Led_SetColor(0, self.screen.COLOR_BROWN)
        while True:
            print('\r##HALT##')
            delay_ms(check_interval)
            # TODO: shall we make this change be a local function that passed into here as param?
            temp_list = self.controller.adc_all_channels
            if temp_list[8] > baseline and temp_list[7] > baseline:
                print('!!DASH-TIME!!')
                self.action_D(with_turn=with_turn, dash_time=dash_time)
                return

    # endregion

    # region events
    def util_edge(self, using_gray: bool = True, using_edge_sensor: bool = False, edge_a: int = 1800):
        """
        a conditioned delay function ,will delay util the condition is satisfied
        :param using_gray: use the gray the judge if the condition is satisfied
        :param using_edge_sensor: use the edge sensors to judge if the condition is satisfied
        :param edge_a: edge sensors judge baseline
        :return:
        """
        if using_gray:
            io_list = self.controller.io_all_channels
            while int(io_list[6]) + int(io_list[7]) > 1:
                io_list = self.controller.io_all_channels
        elif using_edge_sensor:
            adc_list = self.controller.adc_all_channels
            while adc_list[1] < edge_a or adc_list[2] < edge_a:
                adc_list = self.controller.adc_all_channels

    def on_ally_box(self, speed: int = 5000, multiplier: float = 0):
        """
        the action that will be executed on the event when encountering ally box
        :param speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        self.action_T(turn_speed=speed, multiplier=multiplier)

    def on_enemy_box(self, speed: int = 8000, multiplier: float = 0):
        """
        the action that will be executed on the event when encountering enemy box
        :param speed:
        :param multiplier:
        :return:
        """

        if multiplier:
            speed = int(multiplier * speed)
        self.controller.move_cmd(speed, speed)
        self.util_edge()
        self.controller.move_cmd(-speed, -speed)
        delay_ms(160)
        self.controller.move_cmd(0, 0)

    def on_enemy_car(self, speed: int = 8000, multiplier: float = 0):
        """
        the action that will be executed on the event when encountering enemy car
        :param speed:
        :param multiplier:
        :return:
        """
        if multiplier:
            speed = int(multiplier * speed)
        self.controller.move_cmd(speed, speed)
        self.util_edge()
        if multiplier:
            speed = int(multiplier * speed)
        self.controller.move_cmd(-speed, -speed)
        delay_ms(160)
        self.controller.move_cmd(0, 0)

    def on_thing_surrounding(self, position_type: int = 0, rotate_time: int = 60, rotate_speed: int = 5000):
        """
        0 for left
        1 for right
        2 for behind
        :param rotate_speed:
        :param rotate_time:
        :param position_type:
        :return:
        """
        if position_type == 2:
            self.action_T(turn_speed=rotate_speed, turn_time=rotate_time, multiplier=2)
        else:
            self.action_T(turn_type=position_type, turn_speed=rotate_speed, turn_time=rotate_time)

    # endregion

    def normal_behave(self, adc_list: list[int], io_list: list[int], edge_baseline: int = 1680,
                      edge_speed_multiplier: float = 0, backing_time: int = 180, rotate_time: int = 130) -> bool:
        """
        handles the normal edge case using both adc_list and io_list.
        but well do not do anything if no edge case
        :param backing_time:
        :param rotate_time:
        :param edge_speed_multiplier:
        :param adc_list:the list of adc devices returns
        :param io_list:the list of io devices returns
        :param edge_baseline: the edge_check baseline
        :return: if encounter the edge
        """
        # change the light color to represent current state, state of in normal behave
        self.screen.ADC_Led_SetColor(0, self.screen.COLOR_BLUE)

        # read the adc sensors
        edge_rr_sensor = adc_list[0]
        edge_fr_sensor = adc_list[1]
        edge_fl_sensor = adc_list[2]
        edge_rl_sensor = adc_list[3]

        # read the io sensors
        l_gray = io_list[6]
        r_gray = io_list[7]

        # use the sum of their returns to get the high_speed
        # the closer to the edge ,the slower the wheels rotates
        high_spead = 4 * min(edge_rl_sensor, edge_fl_sensor, edge_fr_sensor, edge_rr_sensor)
        if edge_speed_multiplier:
            # multiplier to adjust the high_speed
            high_spead = int(high_spead * edge_speed_multiplier)

        # fixed action duration

        if l_gray + r_gray <= 1:
            # at least one of the gray scaler is hanging over air
            self.action_BT(back_speed=high_spead, back_time=backing_time,
                           turn_speed=high_spead, turn_time=rotate_time,
                           t_multiplier=0.6)
            return True
        elif edge_fl_sensor < edge_baseline:
            """
            [fl]         fr
                O-----O
                   |
                O-----O
            rl           rr
            
            front-left encounters the edge, turn right,turn type is 1
            """
            self.action_BT(back_speed=high_spead, back_time=backing_time,
                           turn_speed=high_spead, turn_time=rotate_time,
                           t_multiplier=0.6, turn_type=1)
            return True

        elif edge_fr_sensor < edge_baseline:
            """
            fl          [fr]
                O-----O
                   |
                O-----O
            rl           rr
            
            front-right encounters the edge, turn left,turn type is 0
            """
            self.action_BT(back_speed=high_spead, back_time=backing_time,
                           turn_speed=high_spead, turn_time=rotate_time,
                           t_multiplier=0.6, turn_type=0)
            return True

        elif edge_rl_sensor < edge_baseline:
            """
            fl           fr
                O-----O
                   |
                O-----O
            [rl]         rr

            rear-left encounters the edge, turn right,turn type is 1
            """
            self.action_T(turn_type=1)
            return True
        elif edge_rr_sensor < edge_baseline:
            """
            fl           fr
                O-----O
                   |
                O-----O
            rl          [rr]

            rear-right encounters the edge, turn left,turn type is 0
            """
            self.action_T(turn_type=0)
            return True
        else:
            return False

    def check_surround(self, adc_list: list[int], baseline: int = 2000, basic_speed: int = 6000):
        """
        checks sensors to get surrounding objects
        :param basic_speed:
        :param adc_list:
        :param baseline:
        :return:
        """
        self.screen.ADC_Led_SetColor(0, self.screen.COLOR_RED)
        if self.tag_id == self.ally_tag and adc_list[4] > baseline:
            self.on_ally_box(basic_speed, 0.3)
        elif self.tag_id == self.enemy_tag and adc_list[4] > baseline:
            self.on_enemy_box(basic_speed, 0.4)
        elif adc_list[4] > baseline:
            self.on_enemy_car(basic_speed, 0.5)
        elif adc_list[8] > baseline:
            self.on_thing_surrounding(1)
        elif adc_list[7] > baseline:
            self.on_thing_surrounding(2)
        elif adc_list[5] > baseline:
            self.on_thing_surrounding(3)
        self.screen.ADC_Led_SetColor(0, self.screen.COLOR_GREEN)

    def Battle(self, interval: int = 10, normal_spead: int = 3000):
        """
        the main function
        :param interval:
        :param normal_spead:
        :return:
        """
        print('>>>>BATTLE STARTS<<<<')

        try:
            # wait for the battle starts
            self.wait_start(baseline=1800, with_turn=False)
            while True:
                # update the sensors data
                # TODO: these two functions could be combined
                adc_list = self.controller.adc_all_channels
                io_list = self.controller.io_all_channels

                # normal behave includes all edge encounter solution
                # if encounters edge,must deal with it first
                if self.normal_behave(adc_list, io_list, edge_baseline=1650, edge_speed_multiplier=0.6):
                    adc_list = self.controller.adc_all_channels

                # if no edge is encountered then check if there are anything surrounding
                # will check surrounding and will act according the case to deal with it
                self.check_surround(adc_list)

                # if no edge is encountered and nothing surrounding, then just keep moving up
                self.controller.move_cmd(normal_spead, normal_spead)

                # loop delay,this is to prevent sending too many cmds to driver causing jam
                self.screen.ADC_Led_SetColor(0, self.screen.COLOR_YELLOW)
                delay_ms(interval)

        except KeyboardInterrupt:
            # forced stop
            self.screen.ADC_Led_SetColor(0, self.screen.COLOR_WHITE)
            self.controller.move_cmd(0, 0)
            print('exiting')

    def test_run(self, offset_angle=80):
        print('test')
        self.controller.move_cmd(2000, 2000)
        delay_ms(300)
        self.controller.move_cmd(0, 0)
        while True:
            delay_ms(100)

            if self.controller.adc_all_channels[7] > 1600:
                print('rotates')
                self.action_T_PID(offset_angle)


if __name__ == '__main__':
    bot = BattleBot()
    bot.controller.move_cmd(0, 0)
    # breakpoint()
    bot.Battle(interval=3, normal_spead=3500)
    # bot.test_run()
