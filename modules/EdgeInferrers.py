from random import choice
from typing import Tuple, Sequence

from modules.AbsEdgeInferrer import AbstractEdgeInferrer, ActionPack
from repo.uptechStar.module.actions import ActionPlayer, new_ActionFrame
from repo.uptechStar.module.algrithm_tools import random_sign
from repo.uptechStar.module.sensors import SensorHub, LocalFullUpdaterConstructor, FU_INDEX, FullUpdater
from repo.uptechStar.module.watcher import Watcher, default_edge_rear_watcher, default_edge_front_watcher


class StandardEdgeInferrer(AbstractEdgeInferrer):
    CONFIG_INFER_KEY = 'InferSection'
    CONFIG_EDGE_MAX_BASELINE_KEY = f'{CONFIG_INFER_KEY}/EdgeMaxBaseline'
    CONFIG_EDGE_MIN_BASELINE_KEY = f'{CONFIG_INFER_KEY}/EdgeMinBaseline'
    CONFIG_STRAIGHT_ACTION_DURATION_KEY = f'{CONFIG_INFER_KEY}/StraightActionDuration'
    CONFIG_CURVE_ACTION_DURATION_KEY = f'{CONFIG_INFER_KEY}/CurveActionDuration'

    CONFIG_SENSOR_KEY = 'SensorSection'
    CONFIG_SENSOR_IDS_KEY = f'{CONFIG_SENSOR_KEY}/SensorIds'

    CONFIG_MOTION_KEY = 'MotionSection'

    CONFIG_BASIC_SPEED_KEY = f'{CONFIG_MOTION_KEY}/BasicSpeed'
    DO_N_N_N_N_STATUS_CODE = 0

    DO_FL_N_N_N_STATUS_CODE = 1
    DO_N_N_N_FR_STATUS_CODE = 2
    DO_N_RL_N_N_STATUS_CODE = 4
    DO_N_N_RR_N_STATUS_CODE = 8

    DO_FL_N_N_FR_STATUS_CODE = 3
    DO_FL_RL_N_N_STATUS_CODE = 5
    DO_N_RL_RR_N_STATUS_CODE = 12
    DO_N_N_RR_FR_STATUS_CODE = 10
    DO_FL_N_RR_N_STATUS_CODE = 9
    DO_N_RL_N_FR_STATUS_CODE = 6

    DO_FL_RL_RR_N_STATUS_CODE = 13
    DO_FL_RL_N_FR_STATUS_CODE = 7
    DO_FL_N_RR_FR_STATUS_CODE = 11
    DO_N_RL_RR_FR_STATUS_CODE = 14

    DO_FL_RL_RR_FR_STATUS_CODE = 15

    def register_all_config(self):
        # TODO remember decouple the constant
        self.register_config(config_registry_path=self.CONFIG_EDGE_MAX_BASELINE_KEY,
                             value=1750)
        self.register_config(config_registry_path=self.CONFIG_EDGE_MIN_BASELINE_KEY,
                             value=1150)
        self.register_config(config_registry_path=self.CONFIG_STRAIGHT_ACTION_DURATION_KEY,
                             value=200)
        self.register_config(config_registry_path=self.CONFIG_CURVE_ACTION_DURATION_KEY,
                             value=170)
        self.register_config(config_registry_path=self.CONFIG_SENSOR_IDS_KEY,
                             value=[6, 7, 1, 2])

        self.register_config(config_registry_path=self.CONFIG_BASIC_SPEED_KEY,
                             value=4000)

    def __init__(self, sensor_hub: SensorHub, action_player: ActionPlayer, config_path: str):
        super().__init__(sensor_hub=sensor_hub, player=action_player, config_path=config_path)
        self.updater: FullUpdater = LocalFullUpdaterConstructor.from_full_updater(
            sensor_hub.on_board_adc_updater[FU_INDEX],
            getattr(self, self.CONFIG_SENSOR_IDS_KEY)
        )
        self._rear_watcher: Watcher = default_edge_rear_watcher
        self._front_watcher: Watcher = default_edge_front_watcher

    # region tapes
    # region 3 sides float case
    def do_fl_rl_n_fr(self, basic_speed: int) -> ActionPack:
        sign = random_sign()
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=0.3),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=1.1,
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-sign * basic_speed, sign * basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=0.7),
                new_ActionFrame()], self.DO_FL_RL_N_FR_STATUS_CODE

    def do_fl_n_rr_fr(self, basic_speed: int) -> ActionPack:
        sign = random_sign()
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=0.3),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=1.1,
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(
                    action_speed=(-sign * basic_speed, sign * basic_speed),
                    action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                    action_speed_multiplier=0.7),
                new_ActionFrame()], self.DO_FL_N_RR_FR_STATUS_CODE

    def do_fl_rl_rr_n(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=0.3),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=1.1,
                                breaker_func=self._front_watcher),
                new_ActionFrame()], self.DO_FL_RL_RR_N_STATUS_CODE

    def do_n_rl_rr_fr(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=0.3),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=1.1,
                                breaker_func=self._front_watcher),
                new_ActionFrame()], self.DO_N_RL_RR_FR_STATUS_CODE

    # endregion

    # region 2 sides float case
    def do_fl_n_rr_n(self, basic_speed: int) -> ActionPack:
        return choice([self.do_fl_n_n_n, self.do_n_n_rr_n])(basic_speed=basic_speed)

    def do_n_rl_n_fr(self, basic_speed: int) -> ActionPack:
        return choice([self.do_n_rl_n_n, self.do_n_n_n_fr])(basic_speed=basic_speed)

    def do_fl_n_n_fr(self, basic_speed: int) -> ActionPack:
        sign = random_sign()
        return [new_ActionFrame(action_speed=-basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=1.1,
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(
                    action_speed=(-sign * basic_speed, sign * basic_speed),
                    action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                    action_speed_multiplier=0.7,
                    action_duration_multiplier=1.3),
                new_ActionFrame()], self.DO_FL_N_N_FR_STATUS_CODE

    def do_n_rl_rr_n(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=1.1,
                                breaker_func=self._front_watcher),
                new_ActionFrame()], self.DO_N_RL_RR_N_STATUS_CODE

    def do_n_n_rr_fr(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=1.2),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=1.1,
                                breaker_func=self._front_watcher),
                new_ActionFrame()], self.DO_N_N_RR_FR_STATUS_CODE

    def do_fl_rl_n_n(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=1.2),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=1.1,
                                breaker_func=self._front_watcher),
                new_ActionFrame()], self.DO_FL_RL_N_N_STATUS_CODE

    # endregion

    # region 1 side float case
    def do_n_n_rr_n(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=1.1,
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=0.7),
                new_ActionFrame()], self.DO_N_N_RR_N_STATUS_CODE

    def do_n_rl_n_n(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=1.1,
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=0.7),
                new_ActionFrame()], self.DO_N_RL_N_N_STATUS_CODE

    def do_n_n_n_fr(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=-basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=1.1,
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=0.7),
                new_ActionFrame()], self.DO_N_N_N_FR_STATUS_CODE

    def do_fl_n_n_n(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=-basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=1.1,
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=0.7),
                new_ActionFrame()], self.DO_FL_N_N_N_STATUS_CODE

    # endregion

    def stop(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame()], self.DO_FL_RL_RR_FR_STATUS_CODE

    def do_nothing(self, basic_speed: int) -> ActionPack:
        return [], self.DO_N_N_N_N_STATUS_CODE

    # endregion

    def infer(self, edge_sensors: Sequence[int]) -> Tuple[bool, bool, bool, bool]:
        edge_min_baseline = getattr(self, self.CONFIG_EDGE_MIN_BASELINE_KEY)
        edge_max_baseline = getattr(self, self.CONFIG_EDGE_MAX_BASELINE_KEY)

        return tuple(map(lambda x: edge_min_baseline < x < edge_max_baseline, edge_sensors))

    def react(self) -> int:
        action, status = self.action_table.get(self.infer(self.updater()))(getattr(self, self.CONFIG_BASIC_SPEED_KEY))
        self._player.extend(action)
        return status