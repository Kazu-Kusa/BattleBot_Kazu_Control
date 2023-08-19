from typing import final

from modules.AbsSurroundInferrer import AbstractSurroundInferrer
from repo.uptechStar.module.actions import new_ActionFrame, ActionPlayer
from repo.uptechStar.module.algrithm_tools import random_sign, enlarge_multiplier_ll, float_multiplier_middle, \
    enlarge_multiplier_l, shrink_multiplier_l, shrink_multiplier_ll
from repo.uptechStar.module.inferrer_base import ComplexAction
from repo.uptechStar.module.sensors import SensorHub
from repo.uptechStar.module.watcher import default_edge_rear_watcher, default_edge_front_watcher, Watcher


class StandardSurroundInferrer(AbstractSurroundInferrer):
    def on_enemy_car_encountered_at_front_with_left_object(self, basic_speed) -> ComplexAction:
        # 当前面有车左边有障碍物时，撞下对面的车然后后退至安全位置
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame()]

    def on_enemy_car_encountered_at_front_with_right_object(self, basic_speed) -> ComplexAction:
        # 当前面有车右边有障碍物时，撞下对面的车然后后退至安全位置
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame()]

    def on_enemy_car_encountered_at_front_with_behind_object(self, basic_speed) -> ComplexAction:
        # 当前面有车后边有障碍物时，撞下对面的车然后随机转向至后对边缘
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()
                ]

    def on_enemy_car_encountered_at_front_with_left_right_object(self, basic_speed) -> ComplexAction:
        # 当前面有车左右有障碍物时，撞下对面的车然后后退至安全位置
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame()]

    def on_enemy_car_encountered_at_front_with_left_behind_object(self, basic_speed) -> ComplexAction:
        # 当前面有车左后有障碍物时，撞下对面的车然后右转，再前进至安全位置
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(basic_speed, - basic_speed),
                                action_speed_multiplier=shrink_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame()]

    def on_enemy_car_encountered_at_front_with_right_behind_object(self, basic_speed) -> ComplexAction:
        # 当前面有车右后有障碍物时，撞下对面的车然后左转，再前进至安全位置
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=default_edge_front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=shrink_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=default_edge_rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=default_edge_front_watcher),
                new_ActionFrame()]

    def on_enemy_car_encountered_at_front_with_left_right_behind_object(self, basic_speed) -> ComplexAction:
        # 当前面有车左右后有障碍物时，撞下对面的车然后随机转向，再前进至安全位置
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=default_edge_rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=shrink_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=default_edge_front_watcher),
                new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=default_edge_front_watcher),
                new_ActionFrame()]

    CONFIG_MOTION_KEY = 'MotionSection'
    CONFIG_BASIC_DURATION_KEY = f'{CONFIG_MOTION_KEY}/BasicDuration'
    CONFIG_BASIC_SPEED_KEY = f'{CONFIG_MOTION_KEY}/BasicSpeed'
    CONFIG_DASH_TIMEOUT_KEY = f'{CONFIG_MOTION_KEY}/DashTimeout'

    CONFIG_INFER_KEY = 'InferSection'
    CONFIG_MIN_BASELINES_KEY = f'{CONFIG_INFER_KEY}/MinBaselines'
    CONFIG_MAX_BASELINES_KEY = f'{CONFIG_INFER_KEY}/MaxBaselines'

    def react(self) -> int:
        status_code = self.infer()
        self.exc_action(self.action_table.get(status_code),
                        getattr(self, self.CONFIG_BASIC_SPEED_KEY))
        # fixme deal with this status code problem
        return status_code

    def infer(self) -> int:
        raise NotImplementedError

    @final
    def register_all_config(self):
        self.register_config(config_registry_path=self.CONFIG_BASIC_DURATION_KEY,
                             value=400)
        self.register_config(config_registry_path=self.CONFIG_BASIC_SPEED_KEY,
                             value=5000)
        self.register_config(config_registry_path=self.CONFIG_DASH_TIMEOUT_KEY,
                             value=6000)

    def __init__(self, sensor_hub: SensorHub, action_player: ActionPlayer, config_path: str):
        super().__init__(sensor_hub=sensor_hub, player=action_player, config_path=config_path)

        self._rear_watcher: Watcher = default_edge_rear_watcher
        self._front_watcher: Watcher = default_edge_front_watcher

    @final
    def on_allay_box_encountered_at_front(self, basic_speed: int) -> ComplexAction:
        sign = random_sign()
        return [new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=default_edge_rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_enemy_box_encountered_at_front(self, basic_speed: int) -> ComplexAction:
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=default_edge_front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=default_edge_rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_enemy_car_encountered_at_front(self, basic_speed: int) -> ComplexAction:
        # TODO: dash til the edge, then fall back,should add a block skill(?)
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=default_edge_front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=default_edge_rear_watcher),
                new_ActionFrame()]

    @final
    def on_object_encountered_at_left(self, basic_speed: int) -> ComplexAction:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_object_encountered_at_right(self, basic_speed: int) -> ComplexAction:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_object_encountered_at_behind(self, basic_speed: int) -> ComplexAction:
        sign = random_sign()
        return [new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]
