import warnings
from random import choice, random
from typing import Callable, Optional, List, Union

from modules.EdgeInferrers import StandardEdgeInferrer
from modules.bot import Bot
from functools import lru_cache
from time import perf_counter_ns

from repo.uptechStar.constant import EDGE_REAR_SENSOR_ID, EDGE_FRONT_SENSOR_ID, SIDES_SENSOR_ID, START_MAX_LINE, \
    EDGE_MAX_LINE
from repo.uptechStar.module.actions import new_ActionFrame, ActionPlayer, ActionFrame
from repo.uptechStar.module.uptech import UpTech
from repo.uptechStar.module.watcher import build_watcher


class BattleBot(Bot):

    # TODO: unbind the surrounding objects detection logic to a new class based on ActionPlayer

    def __init__(self, config_path: str):
        super().__init__(config_path=config_path)

        self.edge_inferrer = StandardEdgeInferrer(sensor_hub=self.sensors,
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

    # endregion

    def Battle(self, normal_spead: int = 3000):
        """
        the main function
        :param normal_spead:
        :return:
        """

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

        try:
            # wait for the battle starts
            self.wait_start(**self._wait_start_kwargs)
            while True:
                pass


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
