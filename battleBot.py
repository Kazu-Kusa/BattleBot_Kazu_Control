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
    # ad4未注册，暂时没有控制单元
    CONFIG_SENSOR_KEY = "Sensor"
    # region OB config
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

    # region IO
    CONFIG_OB_IO_KEY = f"{CONFIG_SENSOR_KEY}/OnBoardIo"
    CONFIG_GRAY_L_KEY = f'{CONFIG_OB_IO_KEY}/GrayL'
    CONFIG_GRAY_R_KEY = f'{CONFIG_OB_IO_KEY}/GrayR'
    # endregion

    # region EXPAN_ADC
    CONFIG_EXPAN_ADC_KEY = f'{CONFIG_SENSOR_KEY}/ExpansionAdc'
    CONFIG_F3_KEY = f'{CONFIG_EXPAN_ADC_KEY}/F3'
    CONFIG_F4_KEY = f'{CONFIG_EXPAN_ADC_KEY}/F4'
    CONFIG_F2_KEY = f'{CONFIG_EXPAN_ADC_KEY}/F2'
    CONFIG_FTL_KEY = f'{CONFIG_EXPAN_ADC_KEY}/Ftl'
    CONFIG_R3_KEY = f'{CONFIG_EXPAN_ADC_KEY}/R3'
    CONFIG_R4_KEY = f'{CONFIG_EXPAN_ADC_KEY}/R4'
    CONFIG_R2_KEY = f'{CONFIG_EXPAN_ADC_KEY}/R2'
    CONFIG_FTR_KEY = f'{CONFIG_EXPAN_ADC_KEY}/Ftr'

    # endregion

    # region Driver
    CONFIG_DRIVER_KEY = "driver"
    CONFIG_PRE_COMPILE_CMD_KEY = f'{CONFIG_DRIVER_KEY}/PreCompileCmd'
    CONFIG_DRIVER_DEBUG_MODE_KEY = f'{CONFIG_DRIVER_KEY}/DriverDebugMode'
    CONFIG_MOTOR_IDS_KEY = f'{CONFIG_DRIVER_KEY}/MotorIds'
    CONFIG_MOTOR_DIRS_KEY = f'{CONFIG_DRIVER_KEY}/MotorDirs'
    CONFIG_HANG_TIME_MAX_ERROR_KEY = f'{CONFIG_DRIVER_KEY}/HangTimeMaxError'
    CONFIG_TAG_GROUP_KEY = f'{CONFIG_DRIVER_KEY}/TagGroup'
    CONFIG_DEFAULT_EDGE_BASELINE_KEY = f'{CONFIG_DRIVER_KEY}/DefaultEdgeBaseline'
    CONFIG_DEFAULT_NORMAL_BASELINE_KEY = f'{CONFIG_DRIVER_KEY}/DefaultNormalBaseline'
    CONFIG_DEFAULT_GRAYS_BASELINE_KEY = f'{CONFIG_DRIVER_KEY}/DefaultGraysBaseline'
    CONFIG_DRIVER_SERIAL_PORT_KEY = f'{CONFIG_DRIVER_KEY}/DriverSerialPort'
    # endregion
    def register_all_config(self):
        self.register_config(self.CONFIG_EDGE_FL_KEY, 6)
        self.register_config(self.CONFIG_EDGE_FR_KEY, 2)
        self.register_config(self.CONFIG_EDGE_RL_KEY, 7)
        self.register_config(self.CONFIG_EDGE_RR_KEY, 1)
        self.register_config(self.CONFIG_L1_KEY, 8)
        self.register_config(self.CONFIG_R1_KEY, 0)
        self.register_config(self.CONFIG_FB_KEY, 5)
        self.register_config(self.CONFIG_RB_KEY, 3)
        self.register_config(self.CONFIG_F3_KEY, 0)
        self.register_config(self.CONFIG_F4_KEY, 1)
        self.register_config(self.CONFIG_F2_KEY, 2)
        self.register_config(self.CONFIG_FTL_KEY, 3)
        self.register_config(self.CONFIG_R3_KEY, 4)
        self.register_config(self.CONFIG_R4_KEY, 5)
        self.register_config(self.CONFIG_R2_KEY, 6)
        self.register_config(self.CONFIG_FTR_KEY, 7)
        self.register_config(self.CONFIG_GRAY_L_KEY, 7)
        self.register_config(self.CONFIG_GRAY_R_KEY, 6)
        self.register_config(self.CONFIG_PRE_COMPILE_CMD_KEY, True)
        self.register_config(self.CONFIG_DRIVER_DEBUG_MODE_KEY, False)
        self.register_config(self.CONFIG_MOTOR_IDS_KEY, [4, 3, 1, 2])
        self.register_config(self.CONFIG_MOTOR_DIRS_KEY, [-1, -1, 1, 1])
        self.register_config(self.CONFIG_HANG_TIME_MAX_ERROR_KEY, 50)
        self.register_config(self.CONFIG_TAG_GROUP_KEY, "tag36h11")
        self.register_config(self.CONFIG_DEFAULT_EDGE_BASELINE_KEY, 1750)
        self.register_config(self.CONFIG_DEFAULT_NORMAL_BASELINE_KEY, 1000)
        self.register_config(self.CONFIG_DEFAULT_GRAYS_BASELINE_KEY, 1)
        self.register_config(self.CONFIG_DRIVER_SERIAL_PORT_KEY, None)


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
