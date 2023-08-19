from repo.uptechStar.module.actions import ActionPlayer, new_ActionFrame
from repo.uptechStar.module.algrithm_tools import random_sign
from repo.uptechStar.module.inferrer_base import InferrerBase
from repo.uptechStar.module.sensors import SensorHub, FU_INDEX
from repo.uptechStar.module.watcher import Watcher, build_watcher_simple
import random

ACTION_REVOLVE = (100, 100, 0, 100)

ACTION_SPEED = (-7000, -7000, 0, -7000)


class NormalActions(InferrerBase):
    def _action_table_init(self):
        self.register_action()

    CONFIG_MOTION_KEY = "MotionSection"
    # TODO 未进行测试的界限值
    CONFIG_MOTION_MIN_LINE_KEY = f"{CONFIG_MOTION_KEY}/MinLine"
    # TODO 未进行测试的超时时间界限值
    CONFIG_MOTION_REVOLVE_TIME_KEY = f"{CONFIG_MOTION_KEY}/Revolve"
    CONFIG_MOTION_SPEED_TIME_KEY = f"{CONFIG_MOTION_KEY}/Speed"
    # TODO 某个未测定的数字
    random_factor_speed = random.randint(2000, 4000)

    def register_all_config(self):
        self.register_config(config_registry_path=self.CONFIG_MOTION_MIN_LINE_KEY, value=200)
        self.register_config(config_registry_path=self.CONFIG_MOTION_REVOLVE_TIME_KEY, value=200)
        self.register_config(config_registry_path=self.CONFIG_MOTION_SPEED_TIME_KEY, value=200)

    def __init__(self, player: ActionPlayer, sensor_hub: SensorHub, config_path: str):
        super().__init__(sensor_hub, player, config_path)
        self.view: Watcher = build_watcher_simple(sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
                                                  sensor_id=(8, 0, 5, 3),
                                                  min_line=getattr(self, self.CONFIG_MOTION_MIN_LINE_KEY))
        self.surrounding_watcher: Watcher = None

    def random_action(self):
        return [new_ActionFrame(action_speed=self.random_factor_speed,
                                action_duration=getattr(self, self.CONFIG_MOTION_REVOLVE_TIME_KEY),
                                break_func=self.surrounding_watcher),
                new_ActionFrame()]

    def random_revolve_action(self):
        single = random_sign()
        return [new_ActionFrame(action_speed=(self.random_factor_speed * single, -single * self.random_factor_speed),
                                action_duration=getattr(self, self.CONFIG_MOTION_REVOLVE_TIME_KEY),
                                break_func=self.surrounding_watcher),
                new_ActionFrame()]

    def revolve_action(self):
        # TODO 该函数未测试
        # 旋转动作
        self._player.append(new_ActionFrame(action_speed=ACTION_REVOLVE,
                                            action_duration=getattr(self, self.CONFIG_MOTION_REVOLVE_TIME_KEY),
                                            breaker_func=self.view,
                                            break_action=(new_ActionFrame(),)))
        self._player.append(new_ActionFrame(action_speed=ACTION_SPEED,
                                            action_duration=getattr(self, self.CONFIG_MOTION_SPEED_TIME_KEY),
                                            breaker_func=self.view,
                                            break_action=(new_ActionFrame(),)))
