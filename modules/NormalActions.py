from abc import abstractmethod
from random import choices, choice
from typing import final, Tuple

from repo.uptechStar.module.actions import ActionPlayer, new_ActionFrame
from repo.uptechStar.module.algrithm_tools import float_multiplier_middle, float_multiplier_lower, random_sign, \
    float_multiplier_upper, shrink_multiplier_l, enlarge_multiplier_ll, shrink_multiplier_lll, \
    enlarge_multiplier_lll
from repo.uptechStar.module.inferrer_base import InferrerBase, FlexActionFactory, ComplexAction
from repo.uptechStar.module.sensors import SensorHub, FU_INDEX
from repo.uptechStar.module.watcher import Watcher, default_edge_front_watcher, \
    default_edge_rear_watcher, build_watcher_full_ctrl


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


class AbstractNormalActions(InferrerBase):
    CONFIG_MOTION_KEY = 'MotionSection'
    CONFIG_BASIC_SPEED_KEY = f'{CONFIG_MOTION_KEY}/BasicSpeed'
    CONFIG_BASIC_DURATION_KEY = f'{CONFIG_MOTION_KEY}/BasicDuration'

    @final
    def register_all_config(self):
        self.register_config(self.CONFIG_BASIC_SPEED_KEY, 3600)
        self.register_config(self.CONFIG_BASIC_DURATION_KEY, 500)
        self.register_all_children_config()

    @abstractmethod
    def register_all_children_config(self):
        """
        Register all children configs
        Returns:

        """

    @final
    def exc_action(self, reaction: FlexActionFactory, basic_speed: int) -> None:
        self._player.override(reaction(basic_speed))
        self._player.play()

    @final
    def react(self) -> None:
        self.exc_action(self.action_table.get(self.infer()), getattr(self, self.CONFIG_BASIC_SPEED_KEY))

    @abstractmethod
    def infer(self) -> int:
        raise NotImplementedError


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

    CONFIG_WATCHER_KEY = "Watcher"
    CONFIG_WATCHER_IDS_KEY = f'{CONFIG_WATCHER_KEY}/Ids'
    CONFIG_WATCHER_MAX_BASELINE_KEY = f'{CONFIG_WATCHER_KEY}/MaxBaseline'
    CONFIG_WATCHER_MIN_BASELINE_KEY = f'{CONFIG_WATCHER_KEY}/MinBaseline'

    KEY_SCAN = 1
    KEY_SNAKE = 2
    KEY_DRIFTING = 3
    KEY_TURN = 4
    KEY_PLAIN_MOVE = 5

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

        self.register_config(self.CONFIG_WATCHER_IDS_KEY, [8, 0, 5, 3])
        self.register_config(self.CONFIG_WATCHER_MAX_BASELINE_KEY, [1900] * 4)
        self.register_config(self.CONFIG_WATCHER_MIN_BASELINE_KEY, [1500] * 4)

    def _action_table_init(self):
        self.register_action(self.KEY_SCAN, self.scan)
        self.register_action(self.KEY_SNAKE, self.snake)
        self.register_action(self.KEY_DRIFTING, self.drifting)
        self.register_action(self.KEY_TURN, self.turn)
        self.register_action(self.KEY_PLAIN_MOVE, self.plain_move)

    def __init__(self, player: ActionPlayer, sensor_hub: SensorHub, config_path: str):
        super().__init__(sensor_hub, player, config_path)
        self._infer_body = self._make_infer_body()
        # TODO: consider use edge sensors to assist the judge
        self._surrounding_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=getattr(self, self.CONFIG_WATCHER_IDS_KEY),
            min_lines=getattr(self, self.CONFIG_WATCHER_MIN_BASELINE_KEY),
            max_lines=getattr(self, self.CONFIG_WATCHER_MAX_BASELINE_KEY))
        self._rear_watcher: Watcher = default_edge_rear_watcher
        self._front_watcher: Watcher = default_edge_front_watcher

    def _make_infer_body(self):
        action_keys = [
            self.KEY_SCAN,
            self.KEY_SNAKE,
            self.KEY_DRIFTING,
            self.KEY_TURN,
            self.KEY_PLAIN_MOVE]
        weights = [
            getattr(self, self.CONFIG_SCAN_WEIGHT_KEY),
            getattr(self, self.CONFIG_SNAKE_WEIGHT_KEY),
            getattr(self, self.CONFIG_DRIFTING_WEIGHT_KEY),
            getattr(self, self.CONFIG_TURN_WEIGHT_KEY),
            getattr(self, self.CONFIG_PLAIN_MOVE_WEIGHT_KEY)]

        def infer_body() -> int:
            """
            weighted random choice
            Returns: the key that corresponds to the action

            """
            return choices(action_keys, weights)[0]

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
                                action_speed_multiplier=enlarge_multiplier_lll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                action_duration_multiplier=shrink_multiplier_l()),
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
                                action_speed_multiplier=float_multiplier_upper(),
                                action_duration=basic_duration,
                                action_duration_multiplier=enlarge_multiplier_ll(),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(basic_speed, basic_speed, basic_speed, 0),
                                action_speed_multiplier=float_multiplier_upper(),
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
                                breaker_func=self._front_watcher,
                                break_action=(new_ActionFrame(action_speed=basic_speed,
                                                              action_speed_multiplier=float_multiplier_lower(),
                                                              action_duration=getattr(self,
                                                                                      self.CONFIG_BASIC_DURATION_KEY),
                                                              breaker_func=self._rear_watcher),),
                                is_override_action=False),
                new_ActionFrame()]
