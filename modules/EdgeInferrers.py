from typing import Sequence, Tuple

from modules.AbsEdgeInferrer import AbstractEdgeInferrer, ActionPack
from repo.uptechStar.module.actions import ActionPlayer, new_ActionFrame
from repo.uptechStar.module.algrithm_tools import random_sign, \
    float_multiplier_upper, float_multiplier_lower, enlarge_multiplier_ll, enlarge_multiplier_l
from repo.uptechStar.module.sensors import SensorHub, LocalFullUpdaterConstructor, FU_INDEX, FullUpdater, IU_INDEX
from repo.uptechStar.module.watcher import Watcher, build_watcher_full_ctrl


class StandardEdgeInferrer(AbstractEdgeInferrer):
    CONFIG_INFER_KEY = 'InferSection'
    CONFIG_EDGE_MAX_BASELINE_KEY = f'{CONFIG_INFER_KEY}/EdgeMaxBaseline'
    CONFIG_EDGE_MIN_BASELINE_KEY = f'{CONFIG_INFER_KEY}/EdgeMinBaseline'
    CONFIG_STRAIGHT_ACTION_DURATION_KEY = f'{CONFIG_INFER_KEY}/StraightActionDuration'
    CONFIG_CURVE_ACTION_DURATION_KEY = f'{CONFIG_INFER_KEY}/CurveActionDuration'

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
        self.register_config(config_registry_path=self.CONFIG_EDGE_MAX_BASELINE_KEY,
                             value=[1900] * 4)
        self.register_config(config_registry_path=self.CONFIG_EDGE_MIN_BASELINE_KEY,
                             value=[1300] * 4)
        self.register_config(config_registry_path=self.CONFIG_STRAIGHT_ACTION_DURATION_KEY,
                             value=200)
        self.register_config(config_registry_path=self.CONFIG_CURVE_ACTION_DURATION_KEY,
                             value=170)
        self.register_config(config_registry_path=self.CONFIG_BASIC_SPEED_KEY,
                             value=4000)

    def __init__(self, sensor_hub: SensorHub, edge_sensor_ids: Tuple[int, int, int, int],
                 grays_sensor_ids: Tuple[int, int], action_player: ActionPlayer, config_path: str):
        super().__init__(sensor_hub=sensor_hub, player=action_player, config_path=config_path)
        edge_min_lines = getattr(self, self.CONFIG_EDGE_MIN_BASELINE_KEY)
        edge_max_lines = getattr(self, self.CONFIG_EDGE_MAX_BASELINE_KEY)
        self.updater: FullUpdater = LocalFullUpdaterConstructor.from_full_updater(
            sensor_hub.on_board_adc_updater[FU_INDEX],
            edge_sensor_ids
        )
        self.gray_updater: FullUpdater = LocalFullUpdaterConstructor.from_indexed_updater(
            sensor_hub.on_board_io_updater[IU_INDEX],
            grays_sensor_ids
        )

        self._full_edge_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=edge_sensor_ids,
            min_lines=edge_min_lines,
            max_lines=edge_max_lines
        )
        self._rear_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=[edge_sensor_ids[1], edge_sensor_ids[2]],
            min_lines=[edge_min_lines[1], edge_min_lines[2]],
            max_lines=[edge_max_lines[1], edge_max_lines[2]])
        self._front_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=[edge_sensor_ids[0], edge_sensor_ids[3]],
            min_lines=[edge_min_lines[0], edge_min_lines[3]],
            max_lines=[edge_max_lines[0], edge_max_lines[3]])

    # region tapes
    # region 3 sides float case
    def do_fl_rl_n_fr(self, basic_speed: int) -> ActionPack:
        sign = random_sign()
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_lower()),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_upper(),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-sign * basic_speed, sign * basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_lower()),
                new_ActionFrame()], self.DO_FL_RL_N_FR_STATUS_CODE

    def do_fl_n_rr_fr(self, basic_speed: int) -> ActionPack:
        sign = random_sign()
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_lower()),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_upper(),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(
                    action_speed=(-sign * basic_speed, sign * basic_speed),
                    action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                    action_speed_multiplier=float_multiplier_lower()),
                new_ActionFrame()], self.DO_FL_N_RR_FR_STATUS_CODE

    def do_fl_rl_rr_n(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_lower()),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_upper(),
                                breaker_func=self._front_watcher),
                new_ActionFrame()], self.DO_FL_RL_RR_N_STATUS_CODE

    def do_n_rl_rr_fr(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_lower()),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_upper(),
                                breaker_func=self._front_watcher),
                new_ActionFrame()], self.DO_N_RL_RR_FR_STATUS_CODE

    # endregion

    # region 2 sides float case
    def do_fl_n_rr_n(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_lower()),
                new_ActionFrame()], self.DO_FL_N_RR_N_STATUS_CODE

    def do_n_rl_n_fr(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_lower()),
                new_ActionFrame()], self.DO_N_RL_N_FR_STATUS_CODE

    def do_fl_n_n_fr(self, basic_speed: int) -> ActionPack:
        sign = random_sign()
        return [new_ActionFrame(action_speed=-basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_duration_multiplier=enlarge_multiplier_l(),
                                action_speed_multiplier=float_multiplier_upper(),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(
                    action_speed=(-sign * basic_speed, sign * basic_speed),
                    action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                    action_speed_multiplier=enlarge_multiplier_l(),
                    action_duration_multiplier=enlarge_multiplier_ll()),
                new_ActionFrame()], self.DO_FL_N_N_FR_STATUS_CODE

    def do_n_rl_rr_n(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_upper(),
                                breaker_func=self._front_watcher),
                new_ActionFrame()], self.DO_N_RL_RR_N_STATUS_CODE

    def do_n_n_rr_fr(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_upper()),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_upper(),
                                breaker_func=self._front_watcher),
                new_ActionFrame()], self.DO_N_N_RR_FR_STATUS_CODE

    def do_fl_rl_n_n(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_upper()),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_upper(),
                                breaker_func=self._front_watcher),
                new_ActionFrame()], self.DO_FL_RL_N_N_STATUS_CODE

    # endregion

    # region 1 side float case
    def do_n_n_rr_n(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_upper(),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_lower()),
                new_ActionFrame()], self.DO_N_N_RR_N_STATUS_CODE

    def do_n_rl_n_n(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_upper(),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=float_multiplier_lower()),
                new_ActionFrame()], self.DO_N_RL_N_N_STATUS_CODE

    def do_n_n_n_fr(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=-basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_duration_multiplier=enlarge_multiplier_l(),
                                action_speed_multiplier=float_multiplier_upper(),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=enlarge_multiplier_l()),
                new_ActionFrame()], self.DO_N_N_N_FR_STATUS_CODE

    def do_fl_n_n_n(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame(action_speed=-basic_speed,
                                action_duration=getattr(self, self.CONFIG_STRAIGHT_ACTION_DURATION_KEY),
                                action_duration_multiplier=enlarge_multiplier_l(),
                                action_speed_multiplier=float_multiplier_upper(),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_duration=getattr(self, self.CONFIG_CURVE_ACTION_DURATION_KEY),
                                action_speed_multiplier=enlarge_multiplier_l()),
                new_ActionFrame()], self.DO_FL_N_N_N_STATUS_CODE

    # endregion

    def stop(self, basic_speed: int) -> ActionPack:
        return [new_ActionFrame()], self.DO_FL_RL_RR_FR_STATUS_CODE

    def do_nothing(self, basic_speed: int) -> ActionPack:
        return [], self.DO_N_N_N_N_STATUS_CODE

    # endregion

    def infer(self, edge_sensors: Sequence[int]) -> tuple[bool, ...]:
        min_baselines = getattr(self, self.CONFIG_EDGE_MIN_BASELINE_KEY)
        max_baselines = getattr(self, self.CONFIG_EDGE_MAX_BASELINE_KEY)

        return tuple(
            map(lambda pack: pack[1] < pack[0] < pack[2], zip(edge_sensors, min_baselines, max_baselines)))

    def react(self) -> int:
        gray_status = self.exc_action(self.action_table.get(self.infer(self.gray_updater())),
                                      getattr(self, self.CONFIG_BASIC_SPEED_KEY))

        return gray_status if gray_status else self.exc_action(self.action_table.get(self.infer(self.updater())),
                                                               getattr(self, self.CONFIG_BASIC_SPEED_KEY))
