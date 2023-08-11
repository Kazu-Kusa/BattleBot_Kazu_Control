import time
import time
import warnings

from modules.EdgeInferrers import StandardEdgeInferrer
from modules.FenceInferrers import StandardFenceInferrer
from modules.SurroundInferrers import StandardSurroundInferrer
from modules.bot import Bot
from repo.uptechStar.constant import EDGE_REAR_SENSOR_ID, EDGE_FRONT_SENSOR_ID, SIDES_SENSOR_ID, START_MAX_LINE, \
    EDGE_MAX_LINE
from repo.uptechStar.module.actions import new_ActionFrame
from repo.uptechStar.module.watcher import build_watcher


class BattleBot(Bot):

    def register_all_config(self):
        pass

    def __init__(self, base_config: str,
                 edge_inferrer_config: str,
                 surrounding_inferrer_config: str,
                 fence_inferrer_config: str):
        super().__init__(config_path=base_config)

        self.edge_inferrer = StandardEdgeInferrer(sensor_hub=self.sensor_hub,
                                                  action_player=self.player,
                                                  config_path=edge_inferrer_config)
        self.surrounding_inferrer = StandardSurroundInferrer(sensor_hub=self.sensor_hub,
                                                             action_player=self.player,
                                                             config_path=surrounding_inferrer_config)

        self.fence_inferrer = StandardFenceInferrer(sensor_hub=self.sensor_hub,
                                                    action_player=self.player,
                                                    config_path=fence_inferrer_config)
        self._start_watcher = build_watcher(sensor_update=self.__on_board_sensors.adc_all_channels,
                                            sensor_id=SIDES_SENSOR_ID,
                                            max_line=START_MAX_LINE)
        self._rear_watcher = build_watcher(sensor_update=self.__on_board_sensors.adc_all_channels,
                                           sensor_id=EDGE_REAR_SENSOR_ID,
                                           max_line=EDGE_MAX_LINE)
        self._front_watcher = build_watcher(sensor_update=self.__on_board_sensors.adc_all_channels,
                                            sensor_id=EDGE_FRONT_SENSOR_ID,
                                            max_line=EDGE_MAX_LINE)

    def wait_start(self, dash_time: int = 600, dash_speed: int = 8000) -> None:
        """
        hold still util the start signal is received
        :param dash_speed:
        :param dash_time:
        :return:
        """
        tape = [new_ActionFrame(action_speed=dash_speed, action_duration=dash_time),
                new_ActionFrame()]
        self.screen.set_led_color(0, self.screen.COLOR_BROWN)
        warnings.warn('##HALTING##')
        while self._start_watcher():
            """
            HALTING
            """
        warnings.warn('!!DASH-TIME!!')
        self.player.extend(tape)

    # region events

    # endregion

    def Battle(self, normal_spead: int, team_color: str, use_cam: bool) -> None:
        """
        the main function
        :param use_cam:
        :param team_color:
        :param normal_spead:
        :return:
        """

        def is_on_stage() -> bool:
            # TODO: do remember implement this stage check
            return True

        def on_stage() -> None:
            self.tag_detector.tag_monitor_switch = True
            self.edge_inferrer.react()
            self.surrounding_inferrer.react()
            self.screen.set_led_color(1, self.screen.COLOR_YELLOW)

        def off_stage() -> None:
            self.tag_detector.tag_monitor_switch = False
            self.fence_inferrer.react()
            self.screen.set_led_color(1, self.screen.COLOR_GREEN)

        try:
            # wait for the battle starts
            self.wait_start()
            while True:
                on_stage() if is_on_stage() else off_stage()

        except KeyboardInterrupt:
            # forced stop
            self.screen.set_led_color(0, self.screen.COLOR_WHITE)
            self.player.append(new_ActionFrame())
            warnings.warn('exiting')
            time.sleep(1)


if __name__ == '__main__':
    bot = BattleBot(base_config='config/empty.json',
                    edge_inferrer_config='config/std_edge_inferrer_config.json',
                    surrounding_inferrer_config='config/std_surround_inferrer_config.json',
                    fence_inferrer_config='config/std_fence_inferrer_config.json')
    # bot.Battle(team_color='blue', normal_spead=3000, use_cam=True)
    bot.save_config('config/std_base.config')
