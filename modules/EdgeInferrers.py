from random import choice

from modules.AbsEdgeInferrer import AbstractEdgeInferrer
from repo.uptechStar.module.actions import ActionPlayer, new_ActionFrame, ActionFrame
from repo.uptechStar.module.uptech import UpTech, build_watcher

FRONT_SENSOR_ID = (1, 2)

REAR_SENSOR_ID = (0, 3)


class StandardEdgeInferrer(AbstractEdgeInferrer):

    # TODO: the params should load form the _config

    def __init__(self, sensors: UpTech, action_player: ActionPlayer, config_path: str):
        super().__init__(config_path=config_path)

        self.edge_baseline: int = self._config.get('edge_baseline')
        self.min_baseline: int = self._config.get('min_baseline')
        self.straight_action_duration: int = self._config.get('straight_action_duration')
        self.curve_action_duration: int = self._config.get('curve_action_duration')
        self._sensors: UpTech = sensors
        self._player: ActionPlayer = action_player

        self._rear_watcher = build_watcher(sensor_update=self._sensors.adc_all_channels,
                                           sensor_id=REAR_SENSOR_ID,
                                           max_line=self.edge_baseline)
        self._front_watcher = build_watcher(sensor_update=self._sensors.adc_all_channels,
                                            sensor_id=FRONT_SENSOR_ID,
                                            max_line=self.edge_baseline)

    # region tapes
    def do_fl_rl_n_fr(self, basic_speed: int) -> bool:
        sign = self.random_sign()
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
        sign = self.random_sign()
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

    def do_fl_n_n_fr(self, basic_speed: int) -> bool:
        sign = self.random_sign()
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

    def stop(self, basic_speed: int) -> bool:
        self._player.append(new_ActionFrame())
        return True

    def do_nothing(self, basic_speed: int) -> bool:
        return False

    # endregion

    def floating_inferrer(self, edge_sensors: tuple[int, int, int, int]) -> tuple[bool, bool, bool, bool]:
        edge_rr_sensor = edge_sensors[0]
        edge_fr_sensor = edge_sensors[1]
        edge_fl_sensor = edge_sensors[2]
        edge_rl_sensor = edge_sensors[3]

        return (edge_fl_sensor > self.edge_baseline and edge_fl_sensor > self.min_baseline,
                edge_fr_sensor > self.edge_baseline and edge_fr_sensor > self.min_baseline,
                edge_rl_sensor > self.edge_baseline and edge_rl_sensor > self.min_baseline,
                edge_rr_sensor > self.edge_baseline and edge_rr_sensor > self.min_baseline)

    @classmethod
    def random_sign(cls) -> int:
        return choice([-1, 1])
