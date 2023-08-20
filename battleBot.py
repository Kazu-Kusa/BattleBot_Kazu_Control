import time
import warnings
from typing import final

from modules.EdgeInferrers import StandardEdgeInferrer
from modules.FenceInferrers import StandardFenceInferrer
from modules.NormalActions import NormalActions
from modules.SurroundInferrers import StandardSurroundInferrer
from modules.bot import Bot
from repo.uptechStar.constant import SIDES_SENSOR_ID, START_MIN_LINE
from repo.uptechStar.module.actions import new_ActionFrame, ActionFrame
from repo.uptechStar.module.sensors import FU_INDEX
from repo.uptechStar.module.watcher import build_watcher_simple, build_watcher_full_ctrl


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
    # endregion

    # region OB_IO_CONFIG
    CONFIG_OB_IO_KEY = f"{CONFIG_SENSOR_KEY}/OnBoardIo"
    CONFIG_GRAY_L_KEY = f'{CONFIG_OB_IO_KEY}/GrayL'
    CONFIG_GRAY_R_KEY = f'{CONFIG_OB_IO_KEY}/GrayR'
    # endregion

    # region EXPAN_ADC_CONFIG
    CONFIG_EXPAN_ADC_KEY = f'{CONFIG_SENSOR_KEY}/ExpansionAdc'
    CONFIG_L3_KEY = f'{CONFIG_EXPAN_ADC_KEY}/L3'
    CONFIG_L4_KEY = f'{CONFIG_EXPAN_ADC_KEY}/L4'
    CONFIG_L2_KEY = f'{CONFIG_EXPAN_ADC_KEY}/L2'
    CONFIG_FTL_KEY = f'{CONFIG_EXPAN_ADC_KEY}/Ftl'
    CONFIG_R3_KEY = f'{CONFIG_EXPAN_ADC_KEY}/R3'
    CONFIG_R4_KEY = f'{CONFIG_EXPAN_ADC_KEY}/R4'
    CONFIG_R2_KEY = f'{CONFIG_EXPAN_ADC_KEY}/R2'
    CONFIG_FTR_KEY = f'{CONFIG_EXPAN_ADC_KEY}/Ftr'

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
        self.register_config(self.CONFIG_FB_KEY, 5)
        self.register_config(self.CONFIG_RB_KEY, 3)
        # endregion

        # region EXPAN_ADC
        self.register_config(self.CONFIG_L3_KEY, 0)
        self.register_config(self.CONFIG_L4_KEY, 1)
        self.register_config(self.CONFIG_L2_KEY, 2)
        self.register_config(self.CONFIG_FTL_KEY, 3)
        self.register_config(self.CONFIG_R3_KEY, 4)
        self.register_config(self.CONFIG_R4_KEY, 5)
        self.register_config(self.CONFIG_R2_KEY, 6)
        self.register_config(self.CONFIG_FTR_KEY, 7)
        # endregion

        # region IO
        self.register_config(self.CONFIG_GRAY_L_KEY, 7)
        self.register_config(self.CONFIG_GRAY_R_KEY, 6)
        # endregion

    def __init__(self, base_config: str,
                 edge_inferrer_config: str,
                 surrounding_inferrer_config: str,
                 fence_inferrer_config: str,
                 normal_actions_config: str):
        super().__init__(config_path=base_config)

        self.edge_inferrer = StandardEdgeInferrer(sensor_hub=self.sensor_hub,
                                                  action_player=self.player,
                                                  config_path=edge_inferrer_config)
        self.surrounding_inferrer = StandardSurroundInferrer(sensor_hub=self.sensor_hub,
                                                             action_player=self.player,
                                                             config_path=surrounding_inferrer_config,
                                                             tag_detector=self.tag_detector)

        self.fence_inferrer = StandardFenceInferrer(sensor_hub=self.sensor_hub,
                                                    action_player=self.player,
                                                    config_path=fence_inferrer_config)
        self.normal_actions = NormalActions(sensor_hub=self.sensor_hub,
                                            player=self.player,
                                            config_path=normal_actions_config)
        # TODO remember decouple the constant
        self._normal_alter_watcher = build_watcher_full_ctrl(
            sensor_update=self.sensor_hub.on_board_adc_updater[FU_INDEX],
            sensor_ids=(8, 0, 3),
            min_lines=(1200, 1200, 480),
            max_lines=(None, None, None))
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

        # TODO: may allow a greater speed

        def is_on_stage() -> bool:
            # TODO: do remember implement this stage check
            return True

        def on_stage() -> None:
            if self.edge_inferrer.react():
                return
            if self.surrounding_inferrer.react():
                return
            self.normal_actions.react()

        def off_stage() -> None:
            self.fence_inferrer.react()
            self.screen.set_led_color(1, self.screen.COLOR_GREEN)

        while True:
            on_stage() if is_on_stage() else off_stage()

    def Battle_debug(self, normal_spead: int, team_color: str, use_cam: bool) -> None:
        """
        the main function
        :param use_cam:
        :param team_color:
        :param normal_spead:
        :return:
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
    # bot.save_all_config()
    # bot.start_match(normal_spead=3000, team_color='blue', use_cam=False)
    try:
        bot.Battle()
        # bot.Battle_debug(100, 'red', True)
    except KeyboardInterrupt:
        bot.player.append(new_ActionFrame())
        ActionFrame.save_cache()
        time.sleep(1)
