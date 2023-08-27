import warnings
from random import choices, choice
from typing import Tuple, List

from AbstractNormalActions import AbstractNormalActions
from repo.uptechStar.module.actions import ActionPlayer, new_ActionFrame
from repo.uptechStar.module.algrithm_tools import float_multiplier_middle, random_sign, \
    enlarge_multiplier_ll, enlarge_multiplier_lll, float_multiplier_lower, enlarge_multiplier_l
from repo.uptechStar.module.algrithm_tools import shrink_multiplier_l
from repo.uptechStar.module.inferrer_base import ComplexAction
from repo.uptechStar.module.sensors import SensorHub, FU_INDEX, IU_INDEX
from repo.uptechStar.module.watcher import Watcher, build_watcher_full_ctrl, build_delta_watcher_full_ctrl, \
    watchers_merge, build_io_watcher_from_indexed


def full_rand_drift(speed: int) -> Tuple[int, int, int, int]:
    """
    随机漂移生成器
    Args:
        speed:

    Returns:

    """
    return choice([(speed, speed, speed, 0),
                   (speed, speed, 0, speed),
                   (speed, 0, speed, speed),
                   (0, speed, speed, speed), ])


class NormalActions(AbstractNormalActions):
    CONFIG_SCAN_KEY = "Scan"
    CONFIG_SCAN_WEIGHT_KEY = f'{CONFIG_SCAN_KEY}/Weight'
    CONFIG_SCANNING_SPEED_KEY = f'{CONFIG_SCAN_KEY}/ScanningSpeed'
    CONFIG_SCANNING_DURATION_KEY = f'{CONFIG_SCAN_KEY}/ScanningDuration'
    CONFIG_SCAN_CYCLES_KEY = f"{CONFIG_SCAN_KEY}/ScanCycles"

    CONFIG_SNAKE_KEY = "Snake"
    CONFIG_SNAKE_WEIGHT_KEY = f'{CONFIG_SNAKE_KEY}/Weight'
    CONFIG_SNAKE_CYCLES_KEY = f'{CONFIG_SNAKE_KEY}/SnakeCycles'

    CONFIG_DRIFTING_KEY = "Drifting"
    CONFIG_DRIFTING_WEIGHT_KEY = f'{CONFIG_DRIFTING_KEY}/Weight'
    CONFIG_DRIFTING_CYCLES_KEY = f'{CONFIG_DRIFTING_KEY}/DriftingCycles'

    CONFIG_TURN_KEY = "Turn"
    CONFIG_TURN_WEIGHT_KEY = f'{CONFIG_TURN_KEY}/Weight'

    CONFIG_PLAIN_MOVE_KEY = "PlainMove"
    CONFIG_PLAIN_MOVE_WEIGHT_KEY = f'{CONFIG_PLAIN_MOVE_KEY}/Weight'
    CONFIG_PLAIN_MOVE_GRAYS_MIN_LINE_KEY = f'{CONFIG_PLAIN_MOVE_KEY}/GraysMinLine'

    CONFIG_IDLE_KEY = 'Idle'
    CONFIG_IDLE_WEIGHT_KEY = f'{CONFIG_IDLE_KEY}/Weight'
    CONFIG_IDLE_IDS_KEY = f'{CONFIG_IDLE_KEY}/Ids'
    CONFIG_IDLE_MIN_BASELINE_KEY = f'{CONFIG_IDLE_KEY}/MinBaseline'
    CONFIG_IDLE_MAX_BASELINE_KEY = f'{CONFIG_IDLE_KEY}/MaxBaseline'

    CONFIG_SURROUNDING_WATCHER_KEY = "SurroundingWatcher"

    CONFIG_SURROUNDING_WATCHER_MAX_BASELINE_KEY = f'{CONFIG_SURROUNDING_WATCHER_KEY}/MaxBaseline'
    CONFIG_SURROUNDING_WATCHER_MIN_BASELINE_KEY = f'{CONFIG_SURROUNDING_WATCHER_KEY}/MinBaseline'

    CONFIG_EDGE_WATCHER_KEY = "EdgeWatcher"

    CONFIG_EDGE_WATCHER_MAX_BASELINE_KEY = f'{CONFIG_EDGE_WATCHER_KEY}/MaxBaseline'
    CONFIG_EDGE_WATCHER_MIN_BASELINE_KEY = f'{CONFIG_EDGE_WATCHER_KEY}/MinBaseline'

    KEY_SCAN = 1
    KEY_SNAKE = 2
    KEY_DRIFTING = 3
    KEY_TURN = 4
    KEY_PLAIN_MOVE = 5
    KEY_IDLE = 6

    def infer(self) -> int:
        return self._infer_body()

    def register_all_children_config(self):
        self.register_config(self.CONFIG_SCAN_WEIGHT_KEY, 2)
        self.register_config(self.CONFIG_SCANNING_SPEED_KEY, 100)
        self.register_config(self.CONFIG_SCANNING_DURATION_KEY, 4500)
        self.register_config(self.CONFIG_SCAN_CYCLES_KEY, 1)

        self.register_config(self.CONFIG_SNAKE_WEIGHT_KEY, 2)
        self.register_config(self.CONFIG_SNAKE_CYCLES_KEY, 3)

        self.register_config(self.CONFIG_DRIFTING_WEIGHT_KEY, 2)
        self.register_config(self.CONFIG_DRIFTING_CYCLES_KEY, 1)

        self.register_config(self.CONFIG_TURN_WEIGHT_KEY, 4)

        self.register_config(self.CONFIG_PLAIN_MOVE_WEIGHT_KEY, 16)
        self.register_config(self.CONFIG_PLAIN_MOVE_GRAYS_MIN_LINE_KEY, 3300)

        self.register_config(self.CONFIG_IDLE_IDS_KEY, list(range(8)))
        self.register_config(self.CONFIG_IDLE_WEIGHT_KEY, 6)
        self.register_config(self.CONFIG_IDLE_MIN_BASELINE_KEY, [150] * 8)
        self.register_config(self.CONFIG_IDLE_MAX_BASELINE_KEY, [None] * 8)

        self.register_config(self.CONFIG_SURROUNDING_WATCHER_MAX_BASELINE_KEY, [1900] * 4)
        self.register_config(self.CONFIG_SURROUNDING_WATCHER_MIN_BASELINE_KEY, [1500] * 4)

        self.register_config(self.CONFIG_EDGE_WATCHER_MAX_BASELINE_KEY, [2070, 2150, 2210, 2050])
        self.register_config(self.CONFIG_EDGE_WATCHER_MIN_BASELINE_KEY, [1550, 1550, 1550, 1550])

    def _action_table_init(self):
        self.register_action(self.KEY_SCAN, self.scan)
        self.register_action(self.KEY_SNAKE, self.snake)
        self.register_action(self.KEY_DRIFTING, self.drifting)
        self.register_action(self.KEY_TURN, self.turn)
        self.register_action(self.KEY_PLAIN_MOVE, self.plain_move)
        self.register_action(self.KEY_IDLE, self.idle)

    def __init__(self, player: ActionPlayer, sensor_hub: SensorHub, edge_sensor_ids: Tuple[int, int, int, int],
                 surrounding_sensor_ids: Tuple[int, int, int, int], config_path: str, grays_sensor_ids: Tuple[int, int],
                 extra_sensor_ids: Tuple[int, int, int], true_gray_ids: Tuple[int]):
        super().__init__(sensor_hub, player, config_path)
        self._infer_body = self._make_infer_body()
        self._surrounding_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=surrounding_sensor_ids,
            min_lines=getattr(self, self.CONFIG_SURROUNDING_WATCHER_MIN_BASELINE_KEY),
            max_lines=getattr(self, self.CONFIG_SURROUNDING_WATCHER_MAX_BASELINE_KEY),
            use_any=True)
        self._extra_sensor_watcher: Watcher = build_io_watcher_from_indexed(
            sensor_update=self._sensors.on_board_io_updater[IU_INDEX],
            sensor_ids=extra_sensor_ids,
            activate_status_describer=(0, 0, 0),
            use_any=True
        )
        self._hall_surrounding_watcher: Watcher = watchers_merge(
            [self._extra_sensor_watcher,
             self._surrounding_watcher],
            use_any=True
        )
        edge_min_lines = getattr(self, self.CONFIG_EDGE_WATCHER_MIN_BASELINE_KEY)
        edge_max_lines = getattr(self, self.CONFIG_EDGE_WATCHER_MAX_BASELINE_KEY)
        self._full_edge_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=edge_sensor_ids,
            min_lines=edge_min_lines,
            max_lines=edge_max_lines,
            use_any=True
        )
        self._rear_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=[edge_sensor_ids[1], edge_sensor_ids[2]],
            min_lines=[edge_min_lines[1], edge_min_lines[2]],
            max_lines=[edge_max_lines[1], edge_max_lines[2]],
            use_any=True)
        self._front_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=[edge_sensor_ids[0], edge_sensor_ids[3]],
            min_lines=[edge_min_lines[0], edge_min_lines[3]],
            max_lines=[edge_max_lines[0], edge_max_lines[3]],
            use_any=True)

        self._front_watcher_grays: Watcher = build_io_watcher_from_indexed(
            sensor_update=self._sensors.on_board_io_updater[IU_INDEX],
            sensor_ids=grays_sensor_ids,
            activate_status_describer=(0, 0),
            use_any=True)
        self._full_edge_watcher_merged: Watcher = watchers_merge([
            self._front_watcher_grays, self._full_edge_watcher],
            use_any=True)

        self._front_watcher_merged: Watcher = watchers_merge([self._front_watcher_grays,
                                                              self._front_watcher],
                                                             use_any=True)

        self._idle_watcher: Watcher = build_delta_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=getattr(self, self.CONFIG_IDLE_IDS_KEY),
            max_lines=getattr(self, self.CONFIG_IDLE_MAX_BASELINE_KEY),
            min_lines=getattr(self, self.CONFIG_IDLE_MIN_BASELINE_KEY),
            use_any=True
        )
        self._idle_watcher_merged: Watcher = watchers_merge([self._extra_sensor_watcher,
                                                             self._idle_watcher],
                                                            use_any=True)

        adc_updater = self._sensors.on_board_adc_updater[FU_INDEX]
        min_line = getattr(self, self.CONFIG_PLAIN_MOVE_GRAYS_MIN_LINE_KEY)
        true_gray_ids = edge_sensor_ids[0]  # current uses only one

        def _center_watcher() -> bool:
            return adc_updater()[true_gray_ids] > min_line

        self._stage_center_watcher: Watcher = _center_watcher

    def _make_infer_body(self):
        action_key: List[int, ...] = []
        action_weight: List[float, ...] = []

        scan_weight = getattr(self, self.CONFIG_SCAN_WEIGHT_KEY)
        snake_weight = getattr(self, self.CONFIG_SNAKE_WEIGHT_KEY)
        drifting_weight = getattr(self, self.CONFIG_DRIFTING_WEIGHT_KEY)
        turn_weight = getattr(self, self.CONFIG_TURN_WEIGHT_KEY)
        plain_move_weight = getattr(self, self.CONFIG_PLAIN_MOVE_WEIGHT_KEY)
        idle_weight = getattr(self, self.CONFIG_IDLE_WEIGHT_KEY)
        if scan_weight:
            action_key.append(self.KEY_SCAN)
            action_weight.append(scan_weight)

        if snake_weight:
            action_key.append(self.KEY_SNAKE)
            action_weight.append(snake_weight)

        if drifting_weight:
            action_key.append(self.KEY_DRIFTING)
            action_weight.append(drifting_weight)

        if turn_weight:
            action_key.append(self.KEY_TURN)
            action_weight.append(turn_weight)

        if plain_move_weight:
            action_key.append(self.KEY_PLAIN_MOVE)
            action_weight.append(plain_move_weight)

        if idle_weight:
            action_key.append(self.KEY_IDLE)
            action_weight.append(idle_weight)

        warnings.warn('\nBuilding Normal Action selector\n'
                      f'{action_key}\n'
                      f'{action_weight}')

        def infer_body() -> int:
            """
            weighted random choice
            Returns: the key that corresponds to the action

            """
            nonlocal action_key, action_weight
            return choices(action_key, weights=action_weight)[0]

        return infer_body

    def scan(self, basic_speed: int) -> ComplexAction:
        """
        Scan like a radar
        Args:
            basic_speed:

        Returns:

        """
        scanning_speed = getattr(self, self.CONFIG_SCANNING_SPEED_KEY)
        return [new_ActionFrame(action_speed=(-scanning_speed, scanning_speed),
                                action_duration=getattr(self, self.CONFIG_SCANNING_DURATION_KEY),
                                breaker_func=self._hall_surrounding_watcher,
                                break_action=(new_ActionFrame(),)),
                new_ActionFrame(action_duration=50,
                                breaker_func=self._full_edge_watcher_merged,
                                break_action=(new_ActionFrame(),),
                                is_override_action=True),
                new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                action_duration_multiplier=enlarge_multiplier_lll()),
                new_ActionFrame()] * getattr(self, self.CONFIG_SCAN_CYCLES_KEY)

    def snake(self, basic_speed: int) -> ComplexAction:
        """
        snake motion
        Args:
            basic_speed:

        Returns:

        """
        basic_duration = getattr(self, self.CONFIG_BASIC_DURATION_KEY)
        return [new_ActionFrame(action_speed=(basic_speed, 0, basic_speed, basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=basic_duration,
                                action_duration_multiplier=enlarge_multiplier_lll(),
                                breaker_func=self._front_watcher_merged),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(basic_speed, basic_speed, 0, basic_speed),
                                action_speed_multiplier=float_multiplier_lower(),
                                action_duration=basic_duration,
                                action_duration_multiplier=enlarge_multiplier_lll(),
                                breaker_func=self._front_watcher_merged),
                new_ActionFrame()] * getattr(self, self.CONFIG_SNAKE_CYCLES_KEY)

    def drifting(self, basic_speed: int) -> ComplexAction:
        """
        random drift, left or right
        Args:
            basic_speed:

        Returns:

        """
        duration = getattr(self, self.CONFIG_BASIC_DURATION_KEY)
        return [
            new_ActionFrame(action_speed=0,
                            action_duration=duration,
                            breaker_func=self._full_edge_watcher_merged,
                            break_action=(new_ActionFrame(),),
                            is_override_action=True),

            new_ActionFrame(action_speed=full_rand_drift(basic_speed),
                            action_speed_multiplier=enlarge_multiplier_ll(),
                            action_duration=duration,
                            action_duration_multiplier=float_multiplier_middle(),
                            breaker_func=self._front_watcher_grays,
                            break_action=(new_ActionFrame(),),
                            is_override_action=True),

            new_ActionFrame()] * getattr(self, self.CONFIG_DRIFTING_CYCLES_KEY)

    def turn(self, basic_speed: int) -> ComplexAction:
        """
        random turn left or right
        Args:
            basic_speed:

        Returns:

        """
        sign = random_sign()
        return [new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._extra_sensor_watcher),
                new_ActionFrame()]

    def plain_move(self, basic_speed: int) -> ComplexAction:
        """
        Simply moving forward with breaker, if breaker is activated, backwards a little, finally stop
        Args:
            basic_speed:

        Returns:

        """
        multiplier = enlarge_multiplier_l if self._stage_center_watcher() else shrink_multiplier_l
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=multiplier(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher,
                                break_action=(new_ActionFrame(),),
                                is_override_action=True), new_ActionFrame()]

    def idle(self, basic_speed: int) -> ComplexAction:
        """
        Idle checking all sensors
        Args:
            basic_speed:

        Returns:

        """
        sign = random_sign()
        duration = getattr(self, self.CONFIG_BASIC_DURATION_KEY)
        return [new_ActionFrame(action_speed=0,
                                action_duration=duration,
                                action_duration_multiplier=enlarge_multiplier_lll(),
                                breaker_func=self._idle_watcher_merged,
                                break_action=(new_ActionFrame(), new_ActionFrame(
                                    action_speed=(sign * basic_speed, -sign * basic_speed),
                                    action_duration=duration,
                                    action_speed_multiplier=enlarge_multiplier_lll(),

                                ), new_ActionFrame())

                                )]
