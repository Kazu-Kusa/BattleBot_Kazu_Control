from random import choices, choice
from typing import Tuple

from AbstractNormalActions import AbstractNormalActions
from repo.uptechStar.module.actions import ActionPlayer, new_ActionFrame
from repo.uptechStar.module.algrithm_tools import float_multiplier_middle, float_multiplier_lower, random_sign, \
    float_multiplier_upper, enlarge_multiplier_ll, shrink_multiplier_lll, \
    enlarge_multiplier_lll
from repo.uptechStar.module.inferrer_base import ComplexAction
from repo.uptechStar.module.sensors import SensorHub, FU_INDEX
from repo.uptechStar.module.watcher import Watcher, build_watcher_full_ctrl, build_delta_watcher_full_ctrl


def rand_drift(speed: int) -> Tuple[int, int, int, int]:
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

    CONFIG_IDLE_KEY = 'Idle'
    CONFIG_IDLE_WEIGHT_KEY = f'{CONFIG_IDLE_KEY}/Weight'
    CONFIG_IDLE_IDS_KEY = f'{CONFIG_IDLE_KEY}/Ids'
    CONFIG_IDLE_MIN_BASELINE_KEY = f'{CONFIG_IDLE_KEY}/MinBaseline'
    CONFIG_IDLE_MAX_BASELINE_KEY = f'{CONFIG_IDLE_KEY}/MaxBaseline'

    CONFIG_WATCHER_KEY = "Watcher"
    CONFIG_WATCHER_IDS_KEY = f'{CONFIG_WATCHER_KEY}/Ids'
    CONFIG_WATCHER_MAX_BASELINE_KEY = f'{CONFIG_WATCHER_KEY}/MaxBaseline'
    CONFIG_WATCHER_MIN_BASELINE_KEY = f'{CONFIG_WATCHER_KEY}/MinBaseline'

    CONFIG_EDGE_WATCHER_KEY = "EdgeWatcher"
    CONFIG_EDGE_WATCHER_IDS_KEY = f'{CONFIG_EDGE_WATCHER_KEY}/Ids'
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
        self.register_config(self.CONFIG_SCAN_WEIGHT_KEY, 1)
        self.register_config(self.CONFIG_SCANNING_SPEED_KEY, 100)
        self.register_config(self.CONFIG_SCANNING_DURATION_KEY, 4500)
        self.register_config(self.CONFIG_SCAN_CYCLES_KEY, 1)

        self.register_config(self.CONFIG_SNAKE_WEIGHT_KEY, 1)
        self.register_config(self.CONFIG_SNAKE_CYCLES_KEY, 3)

        self.register_config(self.CONFIG_DRIFTING_WEIGHT_KEY, 1)
        self.register_config(self.CONFIG_DRIFTING_CYCLES_KEY, 1)

        self.register_config(self.CONFIG_TURN_WEIGHT_KEY, 1)

        self.register_config(self.CONFIG_PLAIN_MOVE_WEIGHT_KEY, 1)

        self.register_config(self.CONFIG_IDLE_IDS_KEY, list(range(8)))
        self.register_config(self.CONFIG_IDLE_WEIGHT_KEY, 1)
        self.register_config(self.CONFIG_IDLE_MIN_BASELINE_KEY, [None] * 8)
        self.register_config(self.CONFIG_IDLE_MAX_BASELINE_KEY, [150] * 8)

        self.register_config(self.CONFIG_WATCHER_IDS_KEY, [8, 0, 5, 3])
        self.register_config(self.CONFIG_WATCHER_MAX_BASELINE_KEY, [1900] * 4)
        self.register_config(self.CONFIG_WATCHER_MIN_BASELINE_KEY, [1500] * 4)

        self.register_config(self.CONFIG_EDGE_WATCHER_IDS_KEY, [6, 7, 1, 2])
        self.register_config(self.CONFIG_EDGE_WATCHER_MAX_BASELINE_KEY, [2070, 2150, 2210, 2050])
        self.register_config(self.CONFIG_EDGE_WATCHER_MIN_BASELINE_KEY, [1550, 1550, 1550, 1550])

    def _action_table_init(self):
        self.register_action(self.KEY_SCAN, self.scan)
        self.register_action(self.KEY_SNAKE, self.snake)
        self.register_action(self.KEY_DRIFTING, self.drifting)
        self.register_action(self.KEY_TURN, self.turn)
        self.register_action(self.KEY_PLAIN_MOVE, self.plain_move)
        self.register_action(self.KEY_IDLE, self.idle)

    def __init__(self, player: ActionPlayer, sensor_hub: SensorHub, config_path: str):
        super().__init__(sensor_hub, player, config_path)
        self._infer_body = self._make_infer_body()
        # TODO: consider use edge sensors to assist the judge
        self._surrounding_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=getattr(self, self.CONFIG_WATCHER_IDS_KEY),
            min_lines=getattr(self, self.CONFIG_WATCHER_MIN_BASELINE_KEY),
            max_lines=getattr(self, self.CONFIG_WATCHER_MAX_BASELINE_KEY))

        edge_sensor_ids = getattr(self, self.CONFIG_EDGE_WATCHER_IDS_KEY)
        edge_min_lines = getattr(self, self.CONFIG_EDGE_WATCHER_MIN_BASELINE_KEY)
        edge_max_lines = getattr(self, self.CONFIG_EDGE_WATCHER_MAX_BASELINE_KEY)
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

        self._idle_watcher: Watcher = build_delta_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=getattr(self, self.CONFIG_IDLE_IDS_KEY),
            max_lines=getattr(self, self.CONFIG_IDLE_MAX_BASELINE_KEY),
            min_lines=getattr(self, self.CONFIG_IDLE_MIN_BASELINE_KEY)
        )

    def _make_infer_body(self):
        action_keys = [
            self.KEY_SCAN,
            self.KEY_SNAKE,
            self.KEY_DRIFTING,
            self.KEY_TURN,
            self.KEY_PLAIN_MOVE,
            self.KEY_IDLE]
        weights = [
            getattr(self, self.CONFIG_SCAN_WEIGHT_KEY),
            getattr(self, self.CONFIG_SNAKE_WEIGHT_KEY),
            getattr(self, self.CONFIG_DRIFTING_WEIGHT_KEY),
            getattr(self, self.CONFIG_TURN_WEIGHT_KEY),
            getattr(self, self.CONFIG_PLAIN_MOVE_WEIGHT_KEY),
            getattr(self, self.CONFIG_IDLE_WEIGHT_KEY)]

        def infer_body() -> int:
            """
            weighted random choice
            Returns: the key that corresponds to the action

            """
            return choices(action_keys, weights=weights)[0]

        return infer_body

    def scan(self, basic_speed: int) -> ComplexAction:
        """
        Scan like a radar
        Args:
            basic_speed:

        Returns:

        """
        scanning_speed = getattr(self, self.CONFIG_SCANNING_SPEED_KEY)
        sign = random_sign()
        return [new_ActionFrame(action_speed=(sign * scanning_speed, -sign * scanning_speed),
                                action_duration=getattr(self, self.CONFIG_SCANNING_DURATION_KEY),
                                breaker_func=self._surrounding_watcher,
                                break_action=(new_ActionFrame(),)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-sign * basic_speed, sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
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
        return [new_ActionFrame(action_speed=(0, basic_speed, basic_speed, basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=basic_duration,
                                action_duration_multiplier=enlarge_multiplier_ll(),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(basic_speed, basic_speed, basic_speed, 0),
                                action_speed_multiplier=enlarge_multiplier_lll(),
                                action_duration=basic_duration,
                                action_duration_multiplier=enlarge_multiplier_ll(),
                                breaker_func=self._front_watcher),
                new_ActionFrame()] * getattr(self, self.CONFIG_SNAKE_CYCLES_KEY)

    def drifting(self, basic_speed: int) -> ComplexAction:
        """
        random drift, left or right
        Args:
            basic_speed:

        Returns:

        """
        return [new_ActionFrame(action_speed=rand_drift(basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                action_duration_multiplier=float_multiplier_middle(),
                                breaker_func=self._front_watcher, ),
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
                                action_speed_multiplier=float_multiplier_upper(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def plain_move(self, basic_speed: int) -> ComplexAction:
        """
        Simply moving forward with breaker, if breaker is activated, backwards a little, finally stop
        Args:
            basic_speed:

        Returns:

        """
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                action_duration_multiplier=shrink_multiplier_lll(),
                                breaker_func=self._full_edge_watcher,
                                break_action=(new_ActionFrame(action_speed=-basic_speed,
                                                              action_speed_multiplier=float_multiplier_lower(),
                                                              action_duration=getattr(self,
                                                                                      self.CONFIG_BASIC_DURATION_KEY),
                                                              breaker_func=self._rear_watcher),),
                                is_override_action=False),
                new_ActionFrame()]

    def idle(self, basic_speed: int) -> ComplexAction:
        """
        Idle checking all sensors
        Args:
            basic_speed:

        Returns:

        """
        sign = random_sign()
        return [new_ActionFrame(action_speed=0,
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                action_duration_multiplier=enlarge_multiplier_lll(),
                                breaker_func=self._idle_watcher,
                                break_action=(new_ActionFrame(
                                    action_speed=(sign * basic_speed, -sign * basic_speed),
                                    action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                    action_speed_multiplier=enlarge_multiplier_lll(),

                                ), new_ActionFrame())

                                )]
