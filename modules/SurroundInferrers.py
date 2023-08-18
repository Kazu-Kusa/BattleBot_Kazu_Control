from typing import final

from modules.AbsSurroundInferrer import AbstractSurroundInferrer
from repo.uptechStar.module.actions import new_ActionFrame, ActionPlayer
from repo.uptechStar.module.algrithm_tools import random_sign, enlarge_multiplier_ll, float_multiplier_middle, \
    enlarge_multiplier_l, float_multiplier_upper
from repo.uptechStar.module.inferrer_base import ComplexAction
from repo.uptechStar.module.sensors import SensorHub
from repo.uptechStar.module.watcher import default_edge_rear_watcher, default_edge_front_watcher, Watcher


# TODO: use the newly developed action frame insert play to imp this class
class StandardSurroundInferrer(AbstractSurroundInferrer):
    def on_objects_encountered_at_left_behind(self, basic_speed) -> ComplexAction:
        """
        will turn right and move forward, then turn back to observe the objects,
        will exit the chain action on encountering the edge when moving forward
        :param basic_speed:
        """

        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=float_multiplier_upper(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration_multiplier=enlarge_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher,
                                break_action=(new_ActionFrame(),)),
                # in the default, break action overrides frames below
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration_multiplier=enlarge_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_objects_encountered_at_left_right(self, basic_speed) -> ComplexAction:
        """
        this action will fall back first and then randomly turn left or right
        :param basic_speed: The basic speed of the robot.
        """
        sign = random_sign()
        return [new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher,
                                break_action=(new_ActionFrame(),)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=float_multiplier_upper(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_neutral_box_encountered_at_front(self, basic_speed) -> ComplexAction:
        """
        similar to enemy car reaction, but with lower speed multiplier
        """
        # TODO: use break action to improve performance
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_nothing(self, basic_speed) -> ComplexAction:
        return []

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

        self.register_config(config_registry_path=self.CONFIG_MIN_BASELINES_KEY,
                             value=1300)
        self.register_config(config_registry_path=self.CONFIG_MAX_BASELINES_KEY,
                             value=1900)

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
                                breaker_func=self._rear_watcher),
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
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
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
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
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
