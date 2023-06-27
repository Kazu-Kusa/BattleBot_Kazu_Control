import warnings
from random import randint, choice, random
from typing import Callable

from modules.AbsSurroundInferrer import AbstractSurroundInferrer
from modules.motion import Motion
from modules.EdgeInferrers import StandardEdgeInferrer
from modules.bot import Bot

from time import perf_counter_ns
from repo.uptechStar.module.timer import delay_ms
from repo.uptechStar.module.actions import ActionPlayer


def check_surrounding_fence(ad_list: list, baseline: int = 5000, conner_baseline: int = 2200) -> int:
    """
    fl           fr
        O-----O
           |
        O-----O
    rl           rr

    0: on stage
    1: by stage
    2: in conner should need fallback
    3: in conner should push forward
    :param ad_list:
    :param baseline:
    :param conner_baseline:
    :return:
    """
    rb_sensor = ad_list[5]
    fb_sensor = ad_list[4]
    l3_sensor = ad_list[8]
    r3_sensor = ad_list[7]

    total = sum([rb_sensor, fb_sensor, l3_sensor, r3_sensor])
    if total > baseline:
        # off-stage

        fl_sum = fb_sensor + l3_sensor
        fr_sum = fb_sensor + r3_sensor
        rl_sum = rb_sensor + l3_sensor
        rr_sum = rb_sensor + r3_sensor
        result_dict = {
            (fl_sum, conner_baseline): 2,
            (fr_sum, conner_baseline): 2,
            (rl_sum, conner_baseline): 3,
            (rr_sum, conner_baseline): 3,
        }
        return result_dict.get((max(fl_sum, fr_sum, rl_sum, rr_sum), conner_baseline), 0)
    else:
        # on stage
        return 0


class BattleBot(Bot, AbstractSurroundInferrer, Motion):

    # TODO: unbind the surrounding objects detection logic to a new class based on ActionPlayer
    def __init__(self, config_path: str):
        super().__init__(config_path=config_path)
        self._player = ActionPlayer()
        self.edge_inferrer = StandardEdgeInferrer(sensors=self.sensors,
                                                  action_player=self._player,
                                                  config_path='config/edge_reaction_configs/standard.json')
        self._team_color = None
        self._use_cam = None
        self._normal_speed = None

        self._wait_start_kwargs: dict = {}
        self._check_surrounding_fence_kwargs: dict = {}
        self._on_stage_kwargs: dict = {}
        self._get_away_from_edge_kwargs: dict = {}
        self._check_surround_kwargs: dict = {}

        self.load_config()

    def load_config(self):
        """
        analyze the configuration form the dict in memory
        :return:
        """
        self._normal_speed = self._config.get('normal_speed')
        self._use_cam = self._config.get('use_cam')
        if self._use_cam:
            # if use_cam is True then load the team color and init the hardware
            self._team_color = self._config.get('team_color')
            self.camera.set_tags(self._team_color)
            self.camera.apriltag_detect_start()
        self._wait_start_kwargs = self._config.get('wait_start')
        self._check_surrounding_fence_kwargs = self._config.get('check_surrounding_fence')

        self._on_stage_kwargs = self._config.get('on_stage')
        self._get_away_from_edge_kwargs = self._on_stage_kwargs.get('get_away_from_edge')
        self._check_surround_kwargs = self._on_stage_kwargs.get('check_surround')

    # region special actions
    def wait_start(self, baseline: int = 1800, check_interval: int = 50,
                   with_turn: bool = False, dash_time: int = 600, dash_speed: int = 8000) -> None:
        """
        hold still util the start signal is received
        :param dash_speed:
        :param check_interval:
        :param dash_time:
        :param baseline:
        :param with_turn:
        :return:
        """
        self.screen.ADC_Led_SetColor(0, self.screen.COLOR_BROWN)
        while True:
            print(f'\r##HALT AT {perf_counter_ns()}##', end='')
            delay_ms(check_interval)
            # TODO: shall we make this change be a local function that passed into here as param?
            temp_list = self.sensors.adc_all_channels
            if temp_list[8] > baseline and temp_list[7] > baseline:
                warnings.warn('!!DASH-TIME!!')
                self.action_D(with_turn=with_turn, dash_time=dash_time, dash_speed=dash_speed)
                return

    def scan_surround(self, detector: Callable[[], bool],
                      with_ready: bool = False,
                      ready_time: int = 300,
                      with_dash: bool = False,
                      dash_speed: int = -8000,
                      dash_time: int = 450,
                      dash_breaker_func: Callable[[], bool] = None,
                      dash_breaker_action_func: Callable[[], None] = None,
                      with_turn: bool = False,
                      spinning_type=randint(0, 1), spinning_speed: int = 2500, max_duration: int = 3000):
        """
        checking the stage direction and make the dash movement accordingly
        :param ready_time:
        :param with_ready:
        :param dash_breaker_action_func:
        :param dash_breaker_func:
        :param dash_speed:
        :param dash_time:
        :param with_turn:
        :param detector:
        :param with_dash:
        :param spinning_type:
        :param spinning_speed:
        :param max_duration:
        :return:
        """
        if with_dash:
            def dash() -> None:
                self.action_D(dash_speed=dash_speed, dash_time=dash_time, with_turn=with_turn,
                              breaker_func=dash_breaker_func,
                              break_action_func=dash_breaker_action_func,
                              with_ready=with_ready, ready_time=ready_time)
        else:
            dash = (lambda: None)
        self.action_T(turn_speed=spinning_speed, turn_time=max_duration,
                      turn_type=spinning_type,
                      breaker_func=detector, break_action_func=dash)

    # endregion

    # region events
    def util_edge(self, using_gray: bool = True, using_edge_sensor: bool = True, edge_baseline: int = 1800,
                  breaker_func: Callable[[], bool] = lambda: None, max_duration: int = 3000):
        """
        a conditioned delay function ,will delay util the condition is satisfied
        :param max_duration:
        :param breaker_func:
        :param using_gray: use the gray the judge if the condition is satisfied
        :param using_edge_sensor: use the edge sensors to judge if the condition is satisfied
        :param edge_baseline: edge sensors judge baseline
        :return:
        """
        end = perf_counter_ns() + max_duration * 1000000

        def gray_check():
            io_list = self.sensors.io_all_channels
            while io_list[6] + io_list[7] > 1 and perf_counter_ns() < end:
                io_list = self.sensors.io_all_channels
                if breaker_func():
                    return

        def edge_sensor_check():
            adc_list = self.sensors.adc_all_channels
            while (adc_list[1] > edge_baseline or adc_list[2] > edge_baseline) and perf_counter_ns() < end:
                adc_list = self.sensors.adc_all_channels
                if breaker_func():
                    return

        def mixed_check():
            io_list = self.sensors.io_all_channels
            adc_list = self.sensors.adc_all_channels
            while (adc_list[1] > edge_baseline or adc_list[2] > edge_baseline) and io_list[6] + io_list[
                7] > 1 and perf_counter_ns() < end:
                adc_list = self.sensors.adc_all_channels
                io_list = self.sensors.io_all_channels
                if breaker_func():
                    return

        if using_gray and using_edge_sensor:
            mixed_check()
        elif using_edge_sensor:
            edge_sensor_check()
        elif using_gray:
            gray_check()

    def on_allay_box(self, speed: int = 5000, multiplier: float = 0):
        """
        the action that will be executed on the event when encountering allay box
        :param speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        self.screen.ADC_Led_SetColor(1, self.screen.COLOR_GREEN)
        self.action_T(turn_speed=speed, multiplier=multiplier)

    def on_enemy_box(self, speed: int = 6000, multiplier: float = 0):
        """
        the action that will be executed on the event when encountering enemy box
        :param speed:
        :param multiplier:
        :return:
        """

        self.screen.ADC_Led_SetColor(1, self.screen.COLOR_RED)
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

        self.screen.ADC_Led_SetColor(1, self.screen.COLOR_RED)
        if multiplier:
            speed = int(multiplier * speed)
        self.controller.move_cmd(speed, speed)
        self.util_edge()
        if multiplier:
            speed = int(multiplier * speed)
        self.controller.move_cmd(-speed, -speed)
        delay_ms(160)
        self.controller.move_cmd(0, 0)

    def on_thing_surrounding(self, position_type: int = 0, rotate_time: int = 160, rotate_speed: int = 3800):
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
            self.action_T(turn_speed=rotate_speed, turn_time=rotate_time, multiplier=1.8)
        else:
            self.action_T(turn_type=position_type, turn_speed=rotate_speed, turn_time=rotate_time)

    def on_attacked(self, position_type: int, counter_back: bool = False,
                    run_away: bool = False,
                    run_speed: int = 5000, run_time: int = 240,
                    run_away_breaker_func: Callable[[], bool] = None,
                    run_away_break_action_func: Callable[[], None] = None,
                    reacting_speed: int = 6400, reacting_time: int = 350):
        """
        use action tf to evade attacks
        :param run_away_break_action_func:
        :param run_away_breaker_func:
        :param run_time:
        :param run_away: 
        :param run_speed:
        :param counter_back:
        :param position_type:
        :param reacting_speed:
        :param reacting_time:
        :return:
        """
        if position_type == 0:
            if counter_back:
                self.action_TF(fixed_wheel_id=4, speed=reacting_speed, tf_time=reacting_time)
            else:
                self.action_TF(fixed_wheel_id=3, speed=-reacting_speed, tf_time=reacting_time)
                if run_away:
                    self.action_D(dash_speed=run_speed, dash_time=run_time,
                                  breaker_func=run_away_breaker_func,
                                  break_action_func=run_away_break_action_func)
        elif position_type == 1:
            if counter_back:
                self.action_TF(fixed_wheel_id=2, speed=reacting_speed, tf_time=reacting_time)
            else:
                self.action_TF(fixed_wheel_id=1, speed=-reacting_speed, tf_time=reacting_time)
                if run_away:
                    self.action_D(dash_speed=run_speed, dash_time=run_time,
                                  breaker_func=run_away_breaker_func,
                                  break_action_func=run_away_break_action_func)
        elif position_type == 2:
            if counter_back:
                reacting_time = reacting_time * 0.9
            self.action_TF(fixed_wheel_id=choice([1, 3]), speed=reacting_speed, tf_time=reacting_time)

    # endregion

    def get_away_from_edge(self, adc_list: list[int], io_list: list[int],
                           edge_baseline: int = 1750, min_baseline: int = 1150,
                           edge_speed_multiplier: float = 3,
                           high_speed_time: int = 180, turn_time: int = 160) -> bool:
        """
        handles the normal edge case using both adc_list and io_list.
        but well do not do anything if no edge case
        :param min_baseline:
        :param high_speed_time:
        :param turn_time:
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

        # the closer to the edge ,the slower the wheels rotates
        high_spead = int(edge_speed_multiplier * min(edge_rl_sensor, edge_fl_sensor, edge_fr_sensor, edge_rr_sensor))

        def rear_watcher() -> bool:

            temp = self.sensors.adc_all_channels
            local_edge_rr_sensor = temp[0]
            local_edge_rl_sensor = temp[3]
            if local_edge_rl_sensor < edge_baseline or local_edge_rr_sensor < edge_baseline:
                # if at least one of the edge sensor is hanging over air
                return True
            else:
                return False

        def front_watcher() -> bool:
            temp = self.sensors.adc_all_channels
            local_edge_fr_sensor = temp[1]
            local_edge_fl_sensor = temp[2]
            if local_edge_fl_sensor < edge_baseline or local_edge_fr_sensor < edge_baseline:
                # if at least one of the edge sensor is hanging over air
                return True
            else:
                return False

        def halt() -> None:
            self.controller.move_cmd(0, 0)

        def stop() -> bool:
            warnings.warn('>>>>FLOATING<<<<')
            halt()
            return True

        # region methods
        def do_nothing():
            return False

        def do_fl():
            """
            [fl]         fr
                O-----O
                   |
                O-----O
            rl           rr

            front-left encounters the edge, turn right,turn type is 1
            """
            self.action_BT(back_speed=high_spead, back_time=high_speed_time,
                           turn_speed=high_spead, turn_time=turn_time,
                           b_multiplier=1.1,
                           t_multiplier=0.7, turn_type=1,
                           hind_watcher_func=rear_watcher)
            return True

        def do_fr():
            """
           fl          [fr]
               O-----O
                  |
               O-----O
           rl           rr

           front-right encounters the edge, turn left,turn type is 0
            """
            self.action_BT(back_speed=high_spead, back_time=high_speed_time,
                           turn_speed=high_spead, turn_time=turn_time,
                           b_multiplier=1.1,
                           t_multiplier=0.7, turn_type=0,
                           hind_watcher_func=rear_watcher)
            return True

        def do_rl():
            """
            fl           fr
                O-----O
                   |
                O-----O
            [rl]         rr

            rear-left encounters the edge, turn right,turn type is 1
            """
            self.action_T(turn_type=1, turn_speed=high_spead, turn_time=turn_time, multiplier=1.2)
            self.action_D(dash_speed=high_spead, dash_time=high_speed_time, multiplier=1.1,
                          breaker_func=front_watcher, break_action_func=halt)
            return True

        def do_rr():
            """
            fl           fr
                O-----O
                   |
                O-----O
            rl          [rr]

            rear-right encounters the edge, turn left,turn type is 0
            """
            self.action_T(turn_type=0, turn_speed=high_spead, turn_time=turn_time, multiplier=0.9)
            self.action_D(dash_speed=high_spead, dash_time=high_speed_time, multiplier=1.1,
                          breaker_func=front_watcher, break_action_func=halt)
            return True

        def do_fl_rl():
            """
             [fl]   l   r   fr
                 O-----O
                    |
                 O-----O
            [rl]            rr
            :return:
            """
            self.action_T(turn_type=1, turn_speed=high_spead, multiplier=1.2, turn_time=turn_time)
            self.action_D(dash_speed=high_spead, dash_time=high_speed_time, multiplier=1.1,
                          breaker_func=front_watcher, break_action_func=halt)
            return True

        def do_fr_rr():
            """
              fl   l   r  [fr]
                 O-----O
                    |
                 O-----O
             rl           [rr]
            :return:
            """
            self.action_T(turn_type=0, turn_speed=high_spead, multiplier=1.2, turn_time=turn_time)
            self.action_D(dash_speed=high_spead, dash_time=high_speed_time, multiplier=1.1,
                          breaker_func=front_watcher, break_action_func=halt)
            return True

        def do_rl_rr():
            """
             fl   l   r   fr
                 O-----O
                    |
                 O-----O
            [rl]          [rr]
            :return:
            """
            self.action_D(dash_speed=high_spead, dash_time=high_speed_time, multiplier=1.1,
                          breaker_func=front_watcher, break_action_func=halt)
            return True

        def do_fl_fr():
            """
             [fl]   l   r   [fr]
                 O-----O
                    |
                 O-----O
            rl          rr
            :return:
            """
            self.action_BT(back_speed=high_spead, back_time=high_speed_time,
                           turn_speed=high_spead, turn_time=int(turn_time * 1.3),
                           b_multiplier=1.1,
                           t_multiplier=0.7, turn_type=0,
                           hind_watcher_func=rear_watcher)
            return True

        def do_fr_rl_rr():
            """
             fl   l   r   [fr]
                 O-----O
                    |
                 O-----O
            [rl]          [rr]
            :return:
            """
            self.action_T(turn_type=0, turn_speed=high_spead, turn_time=turn_time, multiplier=0.3)
            self.action_D(dash_speed=high_spead, dash_time=high_speed_time, multiplier=1.1,
                          breaker_func=front_watcher, break_action_func=halt)
            return True

        def do_fl_rl_rr():
            """
            [fl]   l   r   fr
                 O-----O
                    |
                 O-----O
            [rl]          [rr]
            :return:
            """
            self.action_T(turn_type=1, turn_speed=high_spead, turn_time=turn_time, multiplier=0.3)
            self.action_D(dash_speed=high_spead, dash_time=high_speed_time, multiplier=1.1,
                          breaker_func=front_watcher, break_action_func=halt)
            return True

        def do_fl_fr_rr():
            """
             [fl]   l   r   [fr]
                 O-----O
                    |
                 O-----O
             rl           [rr]
            :return:
            """
            self.action_T(turn_type=1, turn_speed=high_spead, turn_time=turn_time, multiplier=0.3)
            self.action_D(dash_speed=high_spead, dash_time=high_speed_time, multiplier=1.1,
                          breaker_func=rear_watcher, break_action_func=halt,
                          with_turn=True)
            return True

        def do_fl_fr_rl():
            """
             [fl]   l   r   [fr]
                 O-----O
                    |
                 O-----O
             [rl]            rr
            :return:
            """
            self.action_T(turn_type=0, turn_speed=high_spead, turn_time=turn_time, multiplier=0.3)
            self.action_D(dash_speed=high_spead, dash_time=high_speed_time, multiplier=1.1,
                          breaker_func=rear_watcher, break_action_func=halt,
                          with_turn=True)
            return True

        # endregion

        sensor_data = (edge_fl_sensor > edge_baseline and edge_fl_sensor > min_baseline,
                       edge_fr_sensor > edge_baseline and edge_fr_sensor > min_baseline,
                       edge_rl_sensor > edge_baseline and edge_rl_sensor > min_baseline,
                       edge_rr_sensor > edge_baseline and edge_rr_sensor > min_baseline)

        method_table = {(True, True, True, True): do_nothing,
                        (False, False, False, False): stop,
                        # region one edge sensor only
                        (False, True, True, True): do_fl,
                        (True, False, True, True): do_fr,
                        (True, True, False, True): do_rl,
                        (True, True, True, False): do_rr,
                        # endregion

                        # region double edge sensor only
                        (False, True, False, True): do_fl_rl,  # normal
                        (True, False, True, False): do_fr_rr,
                        (True, True, False, False): do_rl_rr,
                        (False, False, True, True): do_fl_fr,

                        # (True, False, False, True): do_rl_rr, #abnormal such case are hard to be classified
                        # (False, True, True, False): do_rl_rr,
                        # endregion

                        # region triple edge sensor
                        (True, False, False, False): do_fr_rl_rr,  # specified in conner
                        (False, True, False, False): do_fl_rl_rr,
                        (False, False, True, False): do_fl_fr_rr,
                        (False, False, False, True): do_fl_fr_rl,
                        # endregion
                        (1, 1): do_nothing,
                        (0, 1): do_fl,
                        (1, 0): do_fr,
                        (0, 0): do_fl_fr
                        }

        method = method_table.get(sensor_data)
        if method:
            return method()
        else:
            # read the io sensors
            l_gray = io_list[6]
            r_gray = io_list[7]
            gray_sensor_data = (l_gray, r_gray)

            return method_table.get(gray_sensor_data)

    def check_surround(self, adc_list: list[int], baseline: int = 2000, basic_speed: int = 6000,
                       evade_prob: float = 0.1) -> bool:
        """
        checks sensors to get surrounding objects
        :param evade_prob:
        :param basic_speed:
        :param adc_list:
        :param baseline:
        :return: if it has encountered anything
        """

        if self.camera.tag_id == self.camera.ally_tag and adc_list[4] > baseline:
            self.on_allay_box(basic_speed, 0.3)
            return True
        elif self.camera.tag_id == self.camera.enemy_tag and adc_list[4] > baseline:
            self.on_enemy_box(basic_speed, 0.4)
            return True
        elif adc_list[4] > baseline:
            self.on_enemy_car(basic_speed, 0.5)
            return True
        elif adc_list[8] > baseline:
            if random() < evade_prob:
                self.on_attacked(0)
            self.on_thing_surrounding(0)
            return True
        elif adc_list[7] > baseline:
            if random() < evade_prob:
                self.on_attacked(1)
            self.on_thing_surrounding(1)
            return True
        elif adc_list[5] > baseline:
            if random() < evade_prob:
                self.on_attacked(2)
            self.on_thing_surrounding(2)
            return True
        else:
            return False

    def Battle(self, normal_spead: int = 3000):
        """
        the main function
        :param normal_spead:
        :return:
        """

        def stage_detector_strict(baseline: int = 1000) -> bool:

            temp = self.sensors.adc_all_channels
            if temp[6] > baseline > temp[8] and temp[7] < baseline < temp[5] and temp[4] > baseline:
                return True
            return False

        def conner_break() -> bool:
            temp = self.sensors.adc_all_channels
            rb_sensor = temp[5]
            fb_sensor = temp[4]
            l3_sensor = temp[8]
            r3_sensor = temp[7]
            base_line = 2000
            delta_front_rear = abs(rb_sensor - fb_sensor)
            ab_delta_right_left = abs(l3_sensor - r3_sensor)
            if delta_front_rear + ab_delta_right_left > base_line:
                return True
            else:
                return False

        def on_stage() -> None:
            warnings.warn('on_stage')
            if not self.tag_monitor_switch:
                self.tag_monitor_switch = True
            adc_list = self.sensors.adc_all_channels
            io_list = self.sensors.io_all_channels

            if self.edge_inferrer.get_away_from_edge(adc_list[:4], io_list[:2]):
                return

            if self.check_surround(adc_list, **self._check_surround_kwargs):
                # if no edge is encountered then check if there are anything surrounding
                # will check surrounding and will act according the case to deal with it
                # after turning should go to next loop checking the object
                return
                # if no edge is encountered and nothing surrounding, then just keep moving up
            self.controller.move_cmd(normal_spead, normal_spead)
            # loop delay,this is to prevent sending too many cmds to driver causing jam
            self.screen.ADC_Led_SetColor(1, self.screen.COLOR_YELLOW)

        def front_to_conner() -> None:
            warnings.warn('in_conner,front_to_conner')
            if self.tag_monitor_switch:
                self.tag_monitor_switch = False
            self.scan_surround(detector=conner_break, with_dash=True,
                               dash_speed=-7000, dash_time=450, spinning_speed=2000)

        def rear_to_conner() -> None:
            warnings.warn('in_conner,rear_to_conner')
            if self.tag_monitor_switch:
                self.tag_monitor_switch = False
            self.scan_surround(detector=conner_break, with_dash=True,
                               dash_speed=5000, dash_time=450, spinning_speed=2000)

        def to_stage() -> None:
            warnings.warn('by_stage')
            if self.tag_monitor_switch:
                self.tag_monitor_switch = False

            def watcher(edge_baseline=1750) -> bool:

                temp = self.sensors.adc_all_channels
                local_edge_rr_sensor = temp[0]
                local_edge_rl_sensor = temp[3]
                if local_edge_rl_sensor < edge_baseline or local_edge_rr_sensor < edge_baseline:
                    # if at least one of the edge sensor is hanging over air
                    return True
                else:
                    return False

            def halt():
                self.controller.move_cmd(0, 0)

            self.scan_surround(detector=stage_detector_strict, with_ready=True, ready_time=300, with_dash=True,
                               dash_breaker_func=watcher,
                               dash_breaker_action_func=halt, spinning_speed=1200, max_duration=4000)

        methods_table = {0: on_stage, 1: to_stage, 2: front_to_conner, 3: rear_to_conner}
        try:
            # wait for the battle starts
            self.wait_start(**self._wait_start_kwargs)
            while True:
                method: Callable[[], None] = methods_table.get(
                    check_surrounding_fence(self.sensors.adc_all_channels, **self._check_surrounding_fence_kwargs))
                method()


        except KeyboardInterrupt:
            # forced stop
            self.screen.ADC_Led_SetColor(0, self.screen.COLOR_WHITE)
            self.controller.move_cmd(0, 0)
            warnings.warn('exiting')


if __name__ == '__main__':
    bot = BattleBot(config_path='config/Aggressive.json')
    bot.Battle()
    # bot.test_check_surround()
