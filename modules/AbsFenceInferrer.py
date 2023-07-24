from abc import ABCMeta, abstractmethod
from typing import final, Dict, List, Callable, Tuple, Optional, Hashable, Sequence, Union, Any

from repo.uptechStar.module.actions import ActionPlayer
from repo.uptechStar.module.inferrer_base import InferrerBase, Reaction, ComplexAction


class AbstractFenceInferrer(InferrerBase):
    KEY_FRONT_TO_FENCE = 1
    KEY_LEFT_TO_FENCE = 2
    KEY_RIGHT_TO_FENCE = 4
    KEY_BEHIND_TO_FENCE = 8
    KEY_FRONT_LEFT_TO_FENCE = KEY_FRONT_TO_FENCE + KEY_LEFT_TO_FENCE  # code: 3
    KEY_FRONT_RIGHT_TO_FENCE = KEY_FRONT_TO_FENCE + KEY_RIGHT_TO_FENCE  # code: 5
    KEY_BEHIND_LEFT_TO_FENCE = KEY_BEHIND_TO_FENCE + KEY_LEFT_TO_FENCE  # code: 7
    KEY_BEHIND_RIGHT_TO_FENCE = KEY_BEHIND_TO_FENCE + KEY_RIGHT_TO_FENCE  # code: 9

    def _action_table_init(self):
        self.register_action(case=self.KEY_FRONT_TO_FENCE, complex_action=self.on_front_to_fence)
        self.register_action(case=self.KEY_LEFT_TO_FENCE, complex_action=self.on_left_to_fence)
        self.register_action(case=self.KEY_RIGHT_TO_FENCE, complex_action=self.on_right_to_fence)
        self.register_action(case=self.KEY_BEHIND_TO_FENCE, complex_action=self.on_behind_to_fence)
        self.register_action(case=self.KEY_FRONT_LEFT_TO_FENCE, complex_action=self.on_front_left_to_fence)
        self.register_action(case=self.KEY_FRONT_RIGHT_TO_FENCE, complex_action=self.on_front_right_to_fence)
        self.register_action(case=self.KEY_BEHIND_LEFT_TO_FENCE, complex_action=self.on_behind_left_to_fence)
        self.register_action(case=self.KEY_BEHIND_RIGHT_TO_FENCE, complex_action=self.on_behind_right_to_fence)

    # region methods
    @abstractmethod
    def on_front_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fence at front
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_left_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fence at left
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_right_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fence at right
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_behind_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fence at behind
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_front_left_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fence at front left
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_front_right_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fence at front right
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_behind_left_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fence at behind left
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_behind_right_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fence at behind right
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    # endregion

    @abstractmethod
    def infer(self, sensors_data: Sequence[Union[float, int]]) -> Tuple[Hashable, ...]:
        raise NotImplementedError

    def exc_action(self, reaction: Reaction, *args, **kwargs) -> Any:
        self._player.override(reaction(*args, **kwargs))
