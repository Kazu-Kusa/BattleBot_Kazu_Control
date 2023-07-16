import warnings
from random import choice, random
from typing import Callable, Optional, List, Union

from modules.EdgeInferrers import StandardEdgeInferrer
from modules.bot import Bot

from time import perf_counter_ns

from repo.uptechStar.constant import EDGE_REAR_SENSOR_ID, EDGE_FRONT_SENSOR_ID, SIDES_SENSOR_ID, START_MAX_LINE, \
    EDGE_MAX_LINE
from repo.uptechStar.module.actions import new_ActionFrame, ActionPlayer, ActionFrame
from repo.uptechStar.module.uptech import UpTech
from repo.uptechStar.module.watcher import build_watcher


class AttackPolicy:
    def __init__(self, sensors: UpTech, player: ActionPlayer):
        self._sensors: UpTech = sensors
        self._player: ActionPlayer = player

    def on_attacked(self, position_type: bool, counter_back: bool = False,
                    run_away: bool = False,
                    run_speed: int = 5000, run_time: int = 240,
                    run_away_breaker_func: Optional[Callable[[], bool]] = None,
                    run_away_break_action_func: Optional[Union[ActionFrame, List[ActionFrame]]] = None,
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
        if position_type:
            if counter_back:
                speeds = (reacting_speed, reacting_speed, reacting_speed, 0)

            else:
                speeds = (-reacting_speed, -reacting_speed, 0, -reacting_speed)

        else:
            if counter_back:
                speeds = (0, reacting_speed, reacting_speed, reacting_speed)

            else:
                speeds = (-reacting_speed, 0, -reacting_speed, -reacting_speed)

        tape = [new_ActionFrame(action_speed=speeds,
                                action_duration=reacting_time),
                new_ActionFrame()]
        if not counter_back and run_away:
            action_D = [new_ActionFrame(action_speed=run_speed,
                                        action_duration=run_time,
                                        breaker_func=run_away_breaker_func,
                                        break_action=run_away_break_action_func),
                        new_ActionFrame()]
            tape.extend(action_D)
        self._player.extend(tape)


class BattleBot(Bot, AttackPolicy):

    # TODO: unbind the surrounding objects detection logic to a new class based on ActionPlayer

    def __init__(self, config_path: str):
        super().__init__(config_path=config_path)

        self.edge_inferrer = StandardEdgeInferrer(sensors=self.sensors,
                                                  action_player=self.player,
                                                  config_path='config/edge_reaction_configs/edgeInferrer.json')
        self._team_color = None
        self._use_cam = None
        self._normal_speed = None

        self._wait_start_kwargs: dict = {}
        self._check_surrounding_fence_kwargs: dict = {}
        self._on_stage_kwargs: dict = {}
        self._get_away_from_edge_kwargs: dict = {}
        self._check_surround_kwargs: dict = {}

        self.load_config()

        self._start_watcher = build_watcher(sensor_update=self.sensors.adc_all_channels,
                                            sensor_id=SIDES_SENSOR_ID,
                                            max_line=START_MAX_LINE)
        self._rear_watcher = build_watcher(sensor_update=self.sensors.adc_all_channels,
                                           sensor_id=EDGE_REAR_SENSOR_ID,
                                           max_line=EDGE_MAX_LINE)
        self._front_watcher = build_watcher(sensor_update=self.sensors.adc_all_channels,
                                            sensor_id=EDGE_FRONT_SENSOR_ID,
                                            max_line=EDGE_MAX_LINE)

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
            self.tag_detector.set_tags(self._team_color)
            self.tag_detector.apriltag_detect_start()
        self._wait_start_kwargs = self._config.get('wait_start')
        self._check_surrounding_fence_kwargs = self._config.get('check_surrounding_fence')

        self._on_stage_kwargs = self._config.get('on_stage')
        self._get_away_from_edge_kwargs = self._on_stage_kwargs.get('get_away_from_edge')
        self._check_surround_kwargs = self._on_stage_kwargs.get('check_surround')

    def wait_start(self, dash_time: int = 600, dash_speed: int = 8000) -> None:
        """
        hold still util the start signal is received
        :param dash_speed:
        :param dash_time:
        :return:
        """
        tape = [new_ActionFrame(action_speed=dash_speed, action_duration=dash_time),
                new_ActionFrame()]
        self.screen.ADC_Led_SetColor(0, self.screen.COLOR_BROWN)
        warnings.warn('##HALTING##')
        while self._start_watcher():
            """
            HALTING
            """
        warnings.warn('!!DASH-TIME!!')
        self.player.extend(tape)

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

    # endregion

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

        if self.tag_detector.tag_id == self.tag_detector.ally_tag and adc_list[4] > baseline:
            self.on_allay_box(basic_speed, 0.3)
            return True
        elif self.tag_detector.tag_id == self.tag_detector.enemy_tag and adc_list[4] > baseline:
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
            self.tag_detector.tag_monitor_switch = False
            if self.edge_inferrer.get_away_from_edge(adc_list[:4], io_list[:2]):
                return
            self.tag_detector.tag_monitor_switch = True
            if self.check_surround(adc_list, **self._check_surround_kwargs):
                # if no edge is encountered then check if there are anything surrounding
                # will check surrounding and will act according the case to deal with it
                # after turning should go to next loop checking the object
                return
                # if no edge is encountered and nothing surrounding, then just keep moving up
            self.player.append(new_ActionFrame(action_speed=self._normal_speed))
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

            def halt():
                self.player.append(new_ActionFrame())

            self.scan_surround(detector=stage_detector_strict, with_ready=True, ready_time=300, with_dash=True,
                               dash_breaker_func=self._rear_watcher,
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
            self.player.append(new_ActionFrame())
            warnings.warn('exiting')


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


if __name__ == '__main__':
    bot = BattleBot(config_path='config/Aggressive.json')
    bot.Battle()
    # bot.test_check_surround()
