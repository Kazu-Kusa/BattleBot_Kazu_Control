from modules.AbsSurroundInferrer import AbstractSurroundInferrer
from repo.uptechStar.module.actions import new_ActionFrame
from repo.uptechStar.module.watcher import default_edge_rear_watcher, default_edge_front_watcher
from repo.uptechStar.module.algrithm_tools import random_sign, random_enlarge_multiplier, random_float_multiplier
from typing import final


class StandardSurroundInferrer(AbstractSurroundInferrer):

    @final
    def on_allay_box_at_front(self, basic_speed, multiplier):
        sign = random_sign()
        tape = [new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=random_float_multiplier(),
                                action_duration=self._basic_duration,
                                breaker_func=default_edge_rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=self._basic_duration),
                new_ActionFrame()]
        self._player.extend(tape)

    @final
    def on_enemy_box_at_front(self, basic_speed, multiplier):
        sign = random_sign()
        tape = [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=6000,
                                breaker_func=default_edge_front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=random_float_multiplier(),
                                action_duration=self._basic_duration,
                                breaker_func=default_edge_rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=self._basic_duration),
                new_ActionFrame()]
        self._player.extend(tape)

    @final
    def on_enemy_car_at_front(self, basic_speed, multiplier):
        tape = [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=6000,
                                breaker_func=default_edge_front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=random_float_multiplier(),
                                action_duration=self._basic_duration,
                                breaker_func=default_edge_rear_watcher),
                new_ActionFrame()]
        # TODO: dash til the edge, then fall back,should add a block skill(?)
        self._player.extend(tape)

    @final
    def on_object_encountered_at_left(self, basic_speed, multiplier):
        tape = [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=self._basic_duration),
                new_ActionFrame()]
        self._player.extend(tape)

    @final
    def on_object_encountered_at_right(self, basic_speed, multiplier):
        tape = [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=self._basic_duration),
                new_ActionFrame()]
        self._player.extend(tape)

    @final
    def on_object_encountered_at_behind(self, basic_speed, multiplier):
        sign = random_sign()
        tape = [new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=random_enlarge_multiplier(),
                                action_duration=self._basic_duration),
                new_ActionFrame()]
        self._player.extend(tape)

    @final
    def evaluate_surrounding_status(self, adc_list) -> int:
        pass
