from modules.AbsSurroundInferrer import AbstractSurroundInferrer
from repo.uptechStar.module.actions import new_ActionFrame, ActionPlayer
from repo.uptechStar.module.inferrer_base import ComplexAction
from repo.uptechStar.module.sensors import SensorHub
from repo.uptechStar.module.watcher import default_edge_rear_watcher, default_edge_front_watcher, Watcher
from repo.uptechStar.module.algrithm_tools import random_sign, enlarge_multiplier_ll, float_multiplier_middle
from typing import final, Tuple, Hashable, Any


class StandardSurroundInferrer(AbstractSurroundInferrer):
    def react(self, *args, **kwargs) -> Any:
        pass

    def infer(self, *args, **kwargs) -> Tuple[Hashable, ...]:
        raise NotImplementedError

    CONFIG_BASIC_DURATION_KEY = 'BasicDuration'

    @final
    def register_all_config(self):
        self.register_config(config_registry_path=self.CONFIG_BASIC_DURATION_KEY,
                             value=1500)

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
                                action_duration=6000,
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
                                action_duration=6000,
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