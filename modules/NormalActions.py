from repo.uptechStar.module.actions import ActionPlayer, new_ActionFrame
from repo.uptechStar.module.sensors import SensorHub, FU_INDEX
from repo.uptechStar.module.watcher import Watcher, build_watcher

ACTION_REVOLVE = (100, 100, 0, 100)

ACTION_SPEED = (-7000, -7000, 0, -7000)


class NormalActions:
    # TODO 未进行测试的界限值
    i = 100
    # TODO 未进行测试的超时时间界限值
    t = 100
    t_2 = 10

    def __init__(self, player: ActionPlayer,
                 sensor_hub: SensorHub,
                 how_time: int = 6000):
        self.player = player
        self.sensor_hub = sensor_hub
        self.how_time = how_time
        self.view: Watcher = build_watcher(sensor_update=self.sensor_hub.on_board_adc_updater[FU_INDEX],
                                           sensor_id=(8, 0, 5, 3), min_line=self.i)

    def revolve_action(self):
        # TODO 该函数未测试
        # 旋转动作
        self.player.append(new_ActionFrame(action_speed=ACTION_REVOLVE, action_duration=self.t,
                                           breaker_func=self.view,
                                           break_action=(new_ActionFrame(),)))
        self.player.append(new_ActionFrame(action_speed=ACTION_SPEED, action_duration=self.t_2,
                                           breaker_func=self.view,
                                           break_action=(new_ActionFrame(),)))
