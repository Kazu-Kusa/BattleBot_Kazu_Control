from typing import Tuple, Sequence, Union, Hashable, Any

from modules.AbsFenceInferrer import AbstractFenceInferrer
from repo.uptechStar.module.actions import ActionPlayer, new_ActionFrame
from repo.uptechStar.module.algrithm_tools import random_sign, enlarge_multiplier_ll, float_multiplier_middle
from repo.uptechStar.module.inferrer_base import ComplexAction
from repo.uptechStar.module.sensors import SensorHub
from repo.uptechStar.module.watcher import default_edge_rear_watcher, Watcher


class StandardFenceInferrer(AbstractFenceInferrer):
    def react(self, *args, **kwargs) -> Any:
        pass

    CONFIG_MOTION_KEY = 'MotionSection'
    CONFIG_BASIC_DURATION_KEY = f'{CONFIG_MOTION_KEY}/BasicDuration'
    CONFIG_OFF_STAGE_DASH_DURATION_KEY = f'{CONFIG_MOTION_KEY}/OffStageDashDuration'
    CONFIG_OFF_STAGE_DASH_SPEED_KEY = f'{CONFIG_MOTION_KEY}/OffStageDashSpeed'
    CONFIG_FENCE_INFER_KEY = 'InferSection'
    CONFIG_FENCE_MAX_BASE_LINE_KEY = f"{CONFIG_FENCE_INFER_KEY}/FenceMaxBaseline"
    CONFIG_FENCE_MIN_BASE_LINE_KEY = f'{CONFIG_FENCE_INFER_KEY}/FenceMinBaseline'

    def register_all_config(self):
        self.register_config(config_registry_path=self.CONFIG_BASIC_DURATION_KEY,
                             value=200)
        self.register_config(config_registry_path=self.CONFIG_OFF_STAGE_DASH_DURATION_KEY,
                             value=600)
        self.register_config(config_registry_path=self.CONFIG_OFF_STAGE_DASH_SPEED_KEY,
                             value=-8000)

        self.register_config(config_registry_path=self.CONFIG_FENCE_MAX_BASE_LINE_KEY,
                             value=1900)
        self.register_config(config_registry_path=self.CONFIG_FENCE_MIN_BASE_LINE_KEY,
                             value=1500)

    def __init__(self, sensor_hub: SensorHub, action_player: ActionPlayer, config_path: str):
        super().__init__(sensor_hub=sensor_hub, player=action_player, config_path=config_path)

        self._rear_watcher: Watcher = default_edge_rear_watcher

    def infer(self, sensors_data: Sequence[Union[float, int]]) -> Tuple[Hashable, ...]:
        raise NotImplementedError

    # region methods

    def on_front_to_fence(self, basic_speed) -> ComplexAction:
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY), ),
                new_ActionFrame(action_speed=getattr(self, self.CONFIG_OFF_STAGE_DASH_SPEED_KEY),
                                action_duration=getattr(self, self.CONFIG_OFF_STAGE_DASH_DURATION_KEY)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_left_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_right_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_behind_to_fence(self, basic_speed) -> ComplexAction:
        sign = random_sign()
        return [new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_front_left_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_front_right_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_behind_left_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_behind_right_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    # endregion
