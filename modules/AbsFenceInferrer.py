from abc import ABCMeta, abstractmethod
from typing import final, Dict, List, Callable, Tuple, Optional

from repo.uptechStar.module.actions import ActionPlayer


class AbstractFenceInferrer(metaclass=ABCMeta):
    KEY_FRONT_TO_FENCE = 0
    KEY_LEFT_TO_FENCE = 1
    KEY_RIGHT_TO_FENCE = 2
    KEY_BEHIND_TO_FENCE = 3
    KEY_FRONT_LEFT_TO_FENCE = 4
    KEY_FRONT_RIGHT_TO_FENCE = 5
    KEY_BEHIND_LEFT_TO_FENCE = 6
    KEY_BEHIND_RIGHT_TO_FENCE = 7

    def __init__(self, basic_duration: int, player: ActionPlayer):
        self._basic_duration = basic_duration
        self._player = player

    @abstractmethod
    def on_front_to_fence(self, basic_speed, multiplier):
        """
        the action that will be executed on the event when encountering fence at front
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_left_to_fence(self, basic_speed, multiplier):
        """
        the action that will be executed on the event when encountering fence at left
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_right_to_fence(self, basic_speed, multiplier):
        """
        the action that will be executed on the event when encountering fence at right
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_behind_to_fence(self, basic_speed, multiplier):
        """
        the action that will be executed on the event when encountering fence at behind
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_front_left_to_fence(self, basic_speed, multiplier):
        """
        the action that will be executed on the event when encountering fence at front left
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_front_right_to_fence(self, basic_speed, multiplier):
        """
        the action that will be executed on the event when encountering fence at front right
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_behind_left_to_fence(self, basic_speed, multiplier):
        """
        the action that will be executed on the event when encountering fence at behind left
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_behind_right_to_fence(self, basic_speed, multiplier):
        """
        the action that will be executed on the event when encountering fence at behind right
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    __method_table: Dict[int, Callable] = {
        KEY_FRONT_TO_FENCE: on_front_to_fence,
        KEY_LEFT_TO_FENCE: on_left_to_fence,
        KEY_RIGHT_TO_FENCE: on_right_to_fence,
        KEY_BEHIND_TO_FENCE: on_behind_to_fence,
        KEY_FRONT_LEFT_TO_FENCE: on_front_left_to_fence,
        KEY_FRONT_RIGHT_TO_FENCE: on_front_right_to_fence,
        KEY_BEHIND_LEFT_TO_FENCE: on_behind_left_to_fence,
        KEY_BEHIND_RIGHT_TO_FENCE: on_behind_right_to_fence
    }

    @abstractmethod
    def evaluate_fence_status(self, adc_list) -> int:
        pass

    @final
    def react_to_fence(self, adc_list, basic_speed, multiplier) -> int:
        status_code = self.evaluate_fence_status(adc_list)
        method: Callable = self.__method_table.get(status_code)
        method(basic_speed, multiplier)
        return status_code
