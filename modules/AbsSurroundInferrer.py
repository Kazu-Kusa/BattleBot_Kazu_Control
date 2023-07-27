from abc import ABCMeta, abstractmethod
from typing import final, Dict, List, Callable, Tuple, Optional, Hashable, Any

from overrides import overrides

from repo.uptechStar.module.actions import ActionPlayer
from repo.uptechStar.module.inferrer_base import InferrerBase, Reaction, ComplexAction

FlexActionFactory = Callable[[int], ComplexAction]
from repo.uptechStar.module.sensors import SensorHub
from repo.uptechStar.module.watcher import Watcher, default_edge_front_watcher, default_edge_rear_watcher


class AbstractSurroundInferrer(InferrerBase):
    KEY_BEHIND_OBJECT = 5

    KEY_RIGHT_OBJECT = 4

    KEY_LEFT_OBJECT = 3

    KEY_FRONT_ENEMY_CAR = 2

    KEY_FRONT_ENEMY_BOX = 1

    KEY_FRONT_ALLY_BOX = 0

    KEY_FRONT_NEUTRAL_BOX = 6

    # TODO: currently, these cases has only covered the major ones,assuming robot was surrounded by one object at a time

    @abstractmethod
    def infer(self, *args, **kwargs) -> Tuple[Hashable, ...]:
        raise NotImplementedError

    def exc_action(self, reaction: FlexActionFactory, basic_speed: int) -> None:
        self._player.override(reaction(basic_speed))

    @final
    def _action_table_init(self):
        self.register_action(case=self.KEY_BEHIND_OBJECT,
                             complex_action=self.on_object_encountered_at_behind)
        self.register_action(case=self.KEY_RIGHT_OBJECT,
                             complex_action=self.on_object_encountered_at_right)
        self.register_action(case=self.KEY_LEFT_OBJECT,
                             complex_action=self.on_object_encountered_at_left)
        self.register_action(case=self.KEY_FRONT_ENEMY_CAR,
                             complex_action=self.on_enemy_car_encountered_at_front)
        self.register_action(case=self.KEY_FRONT_ENEMY_BOX,
                             complex_action=self.on_enemy_box_encountered_at_front)
        self.register_action(case=self.KEY_FRONT_ALLY_BOX,
                             complex_action=self.on_allay_box_encountered_at_front)

    # region methods
    @abstractmethod
    def on_allay_box_encountered_at_front(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering allay box
        :param basic_speed: the desired speed the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_enemy_box_encountered_at_front(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy box
        :param basic_speed:
        :return:
        """
        pass

    @abstractmethod
    def on_enemy_car_encountered_at_front(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy car
        :param basic_speed:
        :return:
        """
        pass

    @abstractmethod
    def on_object_encountered_at_left(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering object at left
        :param basic_speed:
        :return:
        """
        pass

    @abstractmethod
    def on_object_encountered_at_right(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering object at right
        :param basic_speed:
        :return:
        """
        pass

    @abstractmethod
    def on_object_encountered_at_behind(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering object at behind
        :param basic_speed:
        :return:
        """
        pass

    # endregion
