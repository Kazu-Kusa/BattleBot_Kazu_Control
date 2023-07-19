from modules.AbsFenceInferrer import AbstractFenceInferrer
from repo.uptechStar.module.actions import ActionPlayer, ActionFrame, new_ActionFrame
from repo.uptechStar.module.watcher import default_edge_rear_watcher, default_edge_front_watcher
from repo.uptechStar.module.algrithm_tools import random_sign, random_enlarge_multiplier, random_float_multiplier
from typing import final, Dict, List, Callable, Tuple, Optional

OFF_STAGE_DASH_DURATION = 600

OFF_STAGE_DASH_SPEED = -8000


class StandardFenceInferrer(AbstractFenceInferrer):

    @final
    def on_front_to_fence(self, basic_speed, multiplier):
        sign = random_sign()
        tape = [new_ActionFrame(action_speed=basic_speed,
                                action_duration=self._basic_duration),
                new_ActionFrame(action_speed=OFF_STAGE_DASH_SPEED,
                                action_duration=OFF_STAGE_DASH_DURATION),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=self._basic_duration),
                new_ActionFrame()]
        self._player.extend(tape)

    @final
    def on_left_to_fence(self, basic_speed, multiplier):
        tape = [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=self._basic_duration),
                new_ActionFrame()]

        self._player.extend(tape)

    @final
    def on_right_to_fence(self, basic_speed, multiplier):
        tape = [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=self._basic_duration),
                new_ActionFrame()]

        self._player.extend(tape)

    @final
    def on_behind_to_fence(self, basic_speed, multiplier):
        sign = random_sign()
        tape = [new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=self._basic_duration),
                new_ActionFrame()]

        self._player.extend(tape)

    @final
    def on_front_left_to_fence(self, basic_speed, multiplier):
        tape = [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=random_float_multiplier(),
                                action_duration=self._basic_duration),
                new_ActionFrame()]

        self._player.extend(tape)

    @final
    def on_front_right_to_fence(self, basic_speed, multiplier):
        tape = [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=random_float_multiplier(),
                                action_duration=self._basic_duration),
                new_ActionFrame()]

        self._player.extend(tape)

    @final
    def on_behind_left_to_fence(self, basic_speed, multiplier):
        tape = [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=random_float_multiplier(),
                                action_duration=self._basic_duration),
                new_ActionFrame()]

        self._player.extend(tape)

    @final
    def on_behind_right_to_fence(self, basic_speed, multiplier):
        tape = [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=random_float_multiplier(),
                                action_duration=self._basic_duration),
                new_ActionFrame()]

        self._player.extend(tape)

    @final
    def evaluate_fence_status(self, adc_list) -> int:
        pass
