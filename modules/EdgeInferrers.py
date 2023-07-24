from random import choice
from typing import Dict, Any

from modules.AbcInferrerBase import Reaction
from modules.AbsEdgeInferrer import AbstractEdgeInferrer
from repo.uptechStar.constant import EDGE_FRONT_SENSOR_ID, EDGE_REAR_SENSOR_ID
from repo.uptechStar.module.actions import ActionPlayer, new_ActionFrame
from repo.uptechStar.module.algrithm_tools import random_sign
from repo.uptechStar.module.sensors import SensorHub
from repo.uptechStar.module.watcher import build_watcher, Watcher, default_edge_rear_watcher, default_edge_front_watcher


class StandardEdgeInferrer(AbstractEdgeInferrer):
    CONFIG_EDGE_MAX_BASELINE_KEY = r'EdgeMaxBaseline'
    CONFIG_EDGE_MIN_BASELINE_KEY = r'EdgeMinBaseline'
    CONFIG_STRAIGHT_ACTION_DURATION_KEY = r'StraightActionDuration'
    CONFIG_CURVE_ACTION_DURATION_KEY = r'CurveActionDuration'

    def register_all_config(self):
        self.register_config(config_registry_path=self.CONFIG_EDGE_MAX_BASELINE_KEY,
                             value=1750)
        self.register_config(config_registry_path=self.CONFIG_EDGE_MIN_BASELINE_KEY,
                             value=1150)
        self.register_config(config_registry_path=self.CONFIG_STRAIGHT_ACTION_DURATION_KEY,
                             value=200)
        self.register_config(config_registry_path=self.CONFIG_CURVE_ACTION_DURATION_KEY,
                             value=170)

    def exc_action(self, reaction: Reaction, *args, **kwargs) -> Any:
        raise NotImplementedError

    def __init__(self, sensor_hub: SensorHub, action_player: ActionPlayer, config_path: str):
        super().__init__(sensor_hub=sensor_hub, player=action_player, config_path=config_path)

        self._rear_watcher: Watcher = default_edge_rear_watcher
        self._front_watcher: Watcher = default_edge_front_watcher

    # region tapes
    # region 3 sides float case
    def do_fl_rl_n_fr(self, basic_speed: int) -> bool:
        sign = random_sign()
        tape = [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=self.curve_action_duration,
                                action_speed_multiplier=0.3),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_duration=self.straight_action_duration,
                                action_speed_multiplier=1.1,
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-sign * basic_speed, sign * basic_speed),
                                action_duration=self.curve_action_duration,
                                action_speed_multiplier=0.7),
                new_ActionFrame()]

        self._player.extend(tape)
        return True

    def do_fl_n_rr_fr(self, basic_speed: int) -> bool:
        sign = random_sign()
        tape = [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=self.curve_action_duration,
                                action_speed_multiplier=0.3),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_duration=self.straight_action_duration,
                                action_speed_multiplier=1.1,
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(
                    action_speed=(-sign * basic_speed, sign * basic_speed),
                    action_duration=self.curve_action_duration,
                    action_speed_multiplier=0.7),
                new_ActionFrame()]

        self._player.extend(tape)
        return True

    def do_fl_rl_rr_n(self, basic_speed: int) -> bool:
        tape = [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=self.curve_action_duration,
                                action_speed_multiplier=0.3),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_duration=self.straight_action_duration,
                                action_speed_multiplier=1.1,
                                breaker_func=self._front_watcher),
                new_ActionFrame()]

        self._player.extend(tape)
        return True

    def do_n_rl_rr_fr(self, basic_speed: int) -> bool:
        tape = [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=self.curve_action_duration,
                                action_speed_multiplier=0.3),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_duration=self.straight_action_duration,
                                action_speed_multiplier=1.1,
                                breaker_func=self._front_watcher),
                new_ActionFrame()]

        self._player.extend(tape)
        return True

    # endregion

    # region 2 sides float case
    def do_fl_n_rr_n(self, basic_speed: int) -> bool:
        return choice([self.do_fl_n_n_n, self.do_n_n_rr_n])()

    def do_n_rl_n_fr(self, basic_speed: int) -> bool:
        return choice([self.do_n_rl_n_n, self.do_n_n_n_fr])()

    def do_fl_n_n_fr(self, basic_speed: int) -> bool:
        sign = random_sign()
        tape = [new_ActionFrame(action_speed=-basic_speed,
                                action_duration=self.straight_action_duration,
                                action_speed_multiplier=1.1,
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(
                    action_speed=(-sign * basic_speed, sign * basic_speed),
                    action_duration=self.curve_action_duration,
                    action_speed_multiplier=0.7,
                    action_duration_multiplier=1.3),
                new_ActionFrame()]

        self._player.extend(tape)
        return True

    def do_n_rl_rr_n(self, basic_speed: int) -> bool:
        tape = [new_ActionFrame(action_speed=basic_speed,
                                action_duration=self.straight_action_duration,
                                action_speed_multiplier=1.1,
                                breaker_func=self._front_watcher),
                new_ActionFrame()]
        self._player.extend(tape)
        return True

    def do_n_n_rr_fr(self, basic_speed: int) -> bool:
        tape = [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=self.curve_action_duration,
                                action_speed_multiplier=1.2),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_duration=self.straight_action_duration,
                                action_speed_multiplier=1.1,
                                breaker_func=self._front_watcher),
                new_ActionFrame()]

        self._player.extend(tape)
        return True

    def do_fl_rl_n_n(self, basic_speed: int) -> bool:
        tape = [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=self.curve_action_duration,
                                action_speed_multiplier=1.2),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_duration=self.straight_action_duration,
                                action_speed_multiplier=1.1,
                                breaker_func=self._front_watcher),
                new_ActionFrame()]

        self._player.extend(tape)
        return True

    # endregion

    # region 1 side float case
    def do_n_n_rr_n(self, basic_speed: int) -> bool:
        tape = [new_ActionFrame(action_speed=basic_speed,
                                action_duration=self.straight_action_duration,
                                action_speed_multiplier=1.1,
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=self.curve_action_duration,
                                action_speed_multiplier=0.7),
                new_ActionFrame()]

        self._player.extend(tape)
        return True

    def do_n_rl_n_n(self, basic_speed: int) -> bool:
        tape = [new_ActionFrame(action_speed=basic_speed,
                                action_duration=self.straight_action_duration,
                                action_speed_multiplier=1.1,
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=self.curve_action_duration,
                                action_speed_multiplier=0.7),
                new_ActionFrame()]

        self._player.extend(tape)
        return True

    def do_n_n_n_fr(self, basic_speed: int) -> bool:
        tape = [new_ActionFrame(action_speed=-basic_speed,
                                action_duration=self.straight_action_duration,
                                action_speed_multiplier=1.1,
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=self.curve_action_duration,
                                action_speed_multiplier=0.7),
                new_ActionFrame()]

        self._player.extend(tape)
        return True

    def do_fl_n_n_n(self, basic_speed: int) -> bool:
        tape = [new_ActionFrame(action_speed=-basic_speed,
                                action_duration=self.straight_action_duration,
                                action_speed_multiplier=1.1,
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=self.curve_action_duration,
                                action_speed_multiplier=0.7),
                new_ActionFrame()]
        self._player.extend(tape)
        return True

    # endregion

    def stop(self, basic_speed: int) -> bool:
        self._player.append(new_ActionFrame())
        return True

    def do_nothing(self, basic_speed: int) -> bool:
        return False

    # endregion

    def infer(self, edge_sensors: tuple[int, int, int, int]) -> tuple[bool, bool, bool, bool]:
        pass
        # edge_rr_sensor = edge_sensors[0]
        # edge_fr_sensor = edge_sensors[1]
        # edge_fl_sensor = edge_sensors[2]
        # edge_rl_sensor = edge_sensors[3]
        #
        # return (edge_fl_sensor > self.edge_baseline and edge_fl_sensor > self.min_baseline,
        #         edge_fr_sensor > self.edge_baseline and edge_fr_sensor > self.min_baseline,
        #         edge_rl_sensor > self.edge_baseline and edge_rl_sensor > self.min_baseline,
        #         edge_rr_sensor > self.edge_baseline and edge_rr_sensor > self.min_baseline)
