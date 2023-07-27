from modules.AbsFenceInferrer import AbstractFenceInferrer
from repo.uptechStar.module.actions import ActionPlayer, ActionFrame, new_ActionFrame
from repo.uptechStar.module.inferrer_base import ComplexAction
from repo.uptechStar.module.sensors import SensorHub
from repo.uptechStar.module.watcher import default_edge_rear_watcher, default_edge_front_watcher, Watcher
from repo.uptechStar.module.algrithm_tools import random_sign, random_enlarge_multiplier, random_float_multiplier
from typing import final, Dict, List, Callable, Tuple, Optional, Sequence, Union, Hashable, Any

BASIC_DURATION = 200

OFF_STAGE_DASH_DURATION = 600

OFF_STAGE_DASH_SPEED = -8000


class StandardFenceInferrer(AbstractFenceInferrer):
    def react(self, *args, **kwargs) -> Any:
        pass

    CONFIG_BASIC_DURATION_KEY = 'BasicDuration'
    CONFIG_OFF_STAGE_DASH_DURATION_KEY = 'OffStageDashDuration'
    CONFIG_OFF_STAGE_DASH_SPEED_KEY = 'OffStageDashSpeed'

    def register_all_config(self):
        self.register_config(config_registry_path=self.CONFIG_BASIC_DURATION_KEY,
                             value=BASIC_DURATION)
        self.register_config(config_registry_path=self.CONFIG_OFF_STAGE_DASH_DURATION_KEY,
                             value=OFF_STAGE_DASH_DURATION)
        self.register_config(config_registry_path=self.CONFIG_OFF_STAGE_DASH_SPEED_KEY,
                             value=OFF_STAGE_DASH_SPEED)

    def __init__(self, sensor_hub: SensorHub, action_player: ActionPlayer, config_path: str):
        super().__init__(sensor_hub=sensor_hub, player=action_player, config_path=config_path)

        self._rear_watcher: Watcher = default_edge_rear_watcher

    def infer(self, sensors_data: Sequence[Union[float, int]]) -> Tuple[Hashable, ...]:
        raise NotImplementedError

    # region methods
    @final
    def on_front_to_fence(self, basic_speed) -> ComplexAction:
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY), ),
                new_ActionFrame(action_speed=OFF_STAGE_DASH_SPEED,
                                action_duration=OFF_STAGE_DASH_DURATION),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_left_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_right_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_behind_to_fence(self, basic_speed) -> ComplexAction:
        sign = random_sign()
        return [new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_front_left_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=random_float_multiplier(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_front_right_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=random_float_multiplier(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_behind_left_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=random_float_multiplier(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_behind_right_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=random_float_multiplier(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    # endregion
