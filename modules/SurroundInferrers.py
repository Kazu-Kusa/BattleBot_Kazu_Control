from modules.AbsSurroundInferrer import AbstractSurroundInferrer
from repo.uptechStar.module.actions import ActionPlayer, ActionFrame, new_ActionFrame
from typing import final, Dict, List, Callable, Tuple, Optional


class StandardSurroundInferrer(AbstractSurroundInferrer):
    @final
    def on_allay_box_at_front(self, basic_speed, multiplier):
        pass

    @final
    def on_enemy_box_at_front(self, basic_speed, multiplier):
        pass

    @final
    def on_enemy_car_at_front(self, basic_speed, multiplier):
        pass

    @final
    def on_object_encountered_at_left(self, basic_speed, multiplier):
        pass

    @final
    def on_object_encountered_at_right(self, basic_speed, multiplier):
        pass

    @final
    def on_object_encountered_at_behind(self, basic_speed, multiplier):
        pass

    @final
    def evaluate_surrounding_status(self, adc_list) -> int:
        pass
