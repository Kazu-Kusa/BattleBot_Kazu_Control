from abc import abstractmethod
from random import choices
from typing import final

from repo.uptechStar.module.actions import ActionPlayer
from repo.uptechStar.module.inferrer_base import InferrerBase, FlexActionFactory, ComplexAction
from repo.uptechStar.module.sensors import SensorHub, FU_INDEX
from repo.uptechStar.module.watcher import Watcher, build_watcher_simple


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

    def _action_table_init(self):
        self.register_action(self.KEY_SCAN, self.scan)
        self.register_action(self.KEY_SNAKE, self.snake)
        self.register_action(self.KEY_DRIFTING, self.drifting)
        self.register_action(self.KEY_TURN, self.turn)
        self.register_action(self.KEY_PLAIN_MOVE, self.plain_move)

    def __init__(self, player: ActionPlayer, sensor_hub: SensorHub, config_path: str):
        super().__init__(sensor_hub, player, config_path)
        self._infer_body = self._make_infer_body()
        self.view: Watcher = build_watcher_simple(sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
                                                  sensor_id=(8, 0, 5, 3),
                                                  min_line=getattr(self, self.CONFIG_MOTION_MIN_LINE_KEY))
        self.surrounding_watcher: Watcher = None

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
        return []

    def snake(self, basic_speed: int) -> ComplexAction:
        return []

    def drifting(self, basic_speed: int) -> ComplexAction:
        return []

    def turn(self, basic_speed: int) -> ComplexAction:
        return []

    def plain_move(self, basic_speed: int) -> ComplexAction:
        return []
