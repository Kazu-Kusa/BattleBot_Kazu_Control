import warnings
from time import sleep, perf_counter_ns
from typing import final

from modules.EdgeInferrers import StandardEdgeInferrer
from modules.FenceInferrers import StandardFenceInferrer
from modules.NormalActions import NormalActions
from modules.SurroundInferrers import StandardSurroundInferrer
from modules.bot import Bot
from repo.uptechStar.constant import SIDES_SENSOR_ID, START_MIN_LINE
from repo.uptechStar.module.actions import new_ActionFrame
from repo.uptechStar.module.sensors import FU_INDEX
from repo.uptechStar.module.watcher import build_watcher_simple


class BattleBot(Bot):
    # ad4未注册，暂时没有控制单元
    CONFIG_SENSOR_KEY = "Sensor"
    # region OB_ADC_CONFIG
    CONFIG_OB_ADC_KEY = f"{CONFIG_SENSOR_KEY}/OnBoardAdc"
    CONFIG_EDGE_FL_KEY = f"{CONFIG_OB_ADC_KEY}/Fl"
    CONFIG_EDGE_FR_KEY = f'{CONFIG_OB_ADC_KEY}/Fr'
    CONFIG_EDGE_RL_KEY = f'{CONFIG_OB_ADC_KEY}/Rl'
    CONFIG_EDGE_RR_KEY = f'{CONFIG_OB_ADC_KEY}/Rr'
    CONFIG_L1_KEY = f'{CONFIG_OB_ADC_KEY}/L1'
    CONFIG_R1_KEY = f'{CONFIG_OB_ADC_KEY}/R1'
    CONFIG_FB_KEY = f'{CONFIG_OB_ADC_KEY}/Fb'
    CONFIG_RB_KEY = f'{CONFIG_OB_ADC_KEY}/Rb'

    CONFIG_TRUE_GRAYS_KEY = f'{CONFIG_OB_ADC_KEY}/TrueGrays'
    # endregion

    # region OB_IO_CONFIG
    CONFIG_OB_IO_KEY = f"{CONFIG_SENSOR_KEY}/OnBoardIo"
    CONFIG_GRAY_L_KEY = f'{CONFIG_OB_IO_KEY}/GrayL'
    CONFIG_GRAY_R_KEY = f'{CONFIG_OB_IO_KEY}/GrayR'

    CONFIG_FTL_KEY = f'{CONFIG_OB_IO_KEY}/Ftl'
    CONFIG_FTR_KEY = f'{CONFIG_OB_IO_KEY}/Ftr'
    CONFIG_RTR_KEY = f'{CONFIG_OB_IO_KEY}/Rtr'

    # endregion

    # endregion
    def register_all_children_config(self):
        # region OB config
        self.register_config(self.CONFIG_EDGE_FL_KEY, 6)
        self.register_config(self.CONFIG_EDGE_FR_KEY, 2)
        self.register_config(self.CONFIG_EDGE_RL_KEY, 7)
        self.register_config(self.CONFIG_EDGE_RR_KEY, 1)
        self.register_config(self.CONFIG_L1_KEY, 8)
        self.register_config(self.CONFIG_R1_KEY, 0)
        self.register_config(self.CONFIG_FB_KEY, 3)
        self.register_config(self.CONFIG_RB_KEY, 5)

        self.register_config(self.CONFIG_TRUE_GRAYS_KEY, 4)
        # endregion

        # region EXPAN_ADC

        # endregion

        # region IO
        self.register_config(self.CONFIG_GRAY_L_KEY, 7)
        self.register_config(self.CONFIG_GRAY_R_KEY, 6)

        self.register_config(self.CONFIG_FTL_KEY, 7)
        self.register_config(self.CONFIG_FTR_KEY, 6)
        self.register_config(self.CONFIG_RTR_KEY, 5)
        # endregion

    def __init__(self, base_config: str,
                 edge_inferrer_config: str,
                 surrounding_inferrer_config: str,
                 fence_inferrer_config: str,
                 normal_actions_config: str):
        super().__init__(config_path=base_config)
        edge_sensor_ids = (
            getattr(self, self.CONFIG_EDGE_FL_KEY),
            getattr(self, self.CONFIG_EDGE_RL_KEY),
            getattr(self, self.CONFIG_EDGE_RR_KEY),
            getattr(self, self.CONFIG_EDGE_FR_KEY)

        )

        grays_sensor_ids = (
            getattr(self, self.CONFIG_GRAY_L_KEY),
            getattr(self, self.CONFIG_GRAY_R_KEY)
        )
        surrounding_sensor_ids = (
            getattr(self, self.CONFIG_FB_KEY),
            getattr(self, self.CONFIG_RB_KEY),
            getattr(self, self.CONFIG_L1_KEY),
            getattr(self, self.CONFIG_R1_KEY)
        )

        extra_io_sensor_ids = (
            getattr(self, self.CONFIG_FTL_KEY),
            getattr(self, self.CONFIG_FTR_KEY),
            getattr(self, self.CONFIG_RTR_KEY)
        )
        self.edge_inferrer = StandardEdgeInferrer(sensor_hub=self.sensor_hub,
                                                  edge_sensor_ids=edge_sensor_ids,
                                                  grays_sensor_ids=grays_sensor_ids,
                                                  action_player=self.player,
                                                  config_path=edge_inferrer_config)
        self.surrounding_inferrer = StandardSurroundInferrer(sensor_hub=self.sensor_hub, action_player=self.player,
                                                             config_path=surrounding_inferrer_config,
                                                             tag_detector=self.tag_detector,
                                                             surrounding_sensor_ids=surrounding_sensor_ids,
                                                             edge_sensor_ids=edge_sensor_ids,
                                                             grays_sensor_ids=grays_sensor_ids)

        self.fence_inferrer = StandardFenceInferrer(sensor_hub=self.sensor_hub, action_player=self.player,
                                                    config_path=fence_inferrer_config, edge_sensor_ids=edge_sensor_ids,
                                                    surrounding_sensor_ids=surrounding_sensor_ids,
                                                    grays_sensor_ids=grays_sensor_ids)
        self.normal_actions = NormalActions(player=self.player, sensor_hub=self.sensor_hub,
                                            edge_sensor_ids=edge_sensor_ids,
                                            surrounding_sensor_ids=surrounding_sensor_ids,
                                            config_path=normal_actions_config, grays_sensor_ids=grays_sensor_ids,
                                            extra_sensor_ids=extra_io_sensor_ids)

        self._start_watcher = build_watcher_simple(sensor_update=self.sensor_hub.on_board_adc_updater[FU_INDEX],
                                                   sensor_id=SIDES_SENSOR_ID,
                                                   min_line=START_MIN_LINE)

    def wait_start(self) -> None:
        """
        Wait for start
        Returns:

        """
        tape = [
            new_ActionFrame(breaker_func=self._start_watcher,
                            action_duration=99999999),
            new_ActionFrame(action_speed=getattr(self, self.CONFIG_MOTION_START_SPEED_KEY),
                            action_duration=getattr(self, self.CONFIG_MOTION_START_DURATION_KEY)),
            new_ActionFrame()]
        warnings.warn('\n>>>>>>>>>>Waiting for start<<<<<<<', stacklevel=4)
        self.player.extend(tape)
        warnings.warn("\n>>>>>>>>>Start<<<<<<<<", stacklevel=4)

    # region events

    # endregion

    def Battle(self) -> None:

        def _is_on_stage() -> bool:
            # TODO: do remember implement this stage check
            return True

        def _on_stage() -> None:
            if self.edge_inferrer.react():
                return
            if self.surrounding_inferrer.react():
                self.edge_inferrer.react()
                return
            self.normal_actions.react()

        def _off_stage() -> None:
            self.fence_inferrer.react()
            self.screen.set_led_color(1, self.screen.COLOR_GREEN)

        while True:
            _on_stage() if _is_on_stage() else _off_stage()

    def Battle_debug(self) -> None:
        """
        the main function

        """
        self.screen.open()
        self.screen.set_font_size(self.screen.FONT_12X16)

        def is_on_stage() -> bool:
            # TODO: do remember implement this stage check
            return True

        def on_stage() -> None:
            status_code = self.edge_inferrer.react()
            self.screen.fill_screen(self.screen.COLOR_BLACK)
            self.screen.put_string(0, 0, f'{status_code}')
            self.screen.put_string(0, 12, f'{perf_counter_ns()}')
            self.screen.refresh()
            if status_code:
                return
            if self.surrounding_inferrer.react():
                return
            self.normal_actions.react()

        def off_stage() -> None:
            self.fence_inferrer.react()
            self.screen.set_led_color(1, self.screen.COLOR_GREEN)

        while True:
            on_stage() if is_on_stage() else off_stage()

    def interrupt_handler(self):
        self.player.append(new_ActionFrame())
        self.screen.set_led_color(0, self.screen.COLOR_WHITE)

        warnings.warn('\nexiting', stacklevel=4)

    @final
    def save_all_config(self):
        """
        save all config to disk in json format
        Returns:

        """
        self.save_config()
        self.edge_inferrer.save_config()
        self.fence_inferrer.save_config()
        self.surrounding_inferrer.save_config()
        self.normal_actions.save_config()


if __name__ == '__main__':
    bot = BattleBot(base_config='config/std_base_config.json',
                    edge_inferrer_config='config/std_edge_inferrer_config.json',
                    surrounding_inferrer_config='config/std_surround_inferrer_config.json',
                    fence_inferrer_config='config/std_fence_inferrer_config.json',
                    normal_actions_config='config/std_normal_actions_config.json')

    bot.save_all_config()
    # bot.start_match(normal_spead=3000, team_color='blue', use_cam=False)

    try:
        bot.Battle()
        # bot.Battle_debug()
    except KeyboardInterrupt:
        print('end')
        bot.player.append(new_ActionFrame())

        sleep(1)
