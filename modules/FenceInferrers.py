from modules.AbsFenceInferrer import AbstractFenceInferrer
from repo.uptechStar.module.actions import ActionPlayer, ActionFrame, new_ActionFrame
from typing import final, Dict, List, Callable, Tuple, Optional


class StandardFenceInferrer(AbstractFenceInferrer):

    @final
    def on_front_to_fence(self, basic_speed, multiplier):
        pass

    @final
    def on_left_to_fence(self, basic_speed, multiplier):
        pass

    @final
    def on_right_to_fence(self, basic_speed, multiplier):
        pass

    @final
    def on_behind_to_fence(self, basic_speed, multiplier):
        pass

    @final
    def on_front_left_to_fence(self, basic_speed, multiplier):
        pass

    @final
    def on_front_right_to_fence(self, basic_speed, multiplier):
        pass

    @final
    def on_behind_left_to_fence(self, basic_speed, multiplier):
        pass

    @final
    def on_behind_right_to_fence(self, basic_speed, multiplier):
        pass

    @final
    def evaluate_fence_status(self, adc_list) -> int:
        pass
