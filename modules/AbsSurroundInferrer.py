from abc import ABCMeta, abstractmethod
from typing import final, Dict, List, Callable, Tuple, Optional

from repo.uptechStar.module.actions import ActionPlayer

KEY_BEHIND_OBJECT = 5

KEY_RIGHT_OBJECT = 4

KET_LEFT_OBJECT = 3

KEY_FRONT_ENEMY_CAR = 2

KEY_FRONT_ENEMY_BOX = 1

KEY_FRONT_ALLY_BOX = 0


class AbstractSurroundInferrer(metaclass=ABCMeta):

    def __init__(self, basic_duration: int, player: ActionPlayer):
        self._basic_duration = basic_duration
        self._player = player

    @abstractmethod
    def on_allay_box_at_front(self, basic_speed, multiplier):
        """
        the action that will be executed on the event when encountering allay box
        :param basic_speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_enemy_box_at_front(self, basic_speed, multiplier):
        """
        the action that will be executed on the event when encountering enemy box
        :param basic_speed:
        :param multiplier:
        :return:
        """
        pass

    @abstractmethod
    def on_enemy_car_at_front(self, basic_speed, multiplier):
        """
        the action that will be executed on the event when encountering enemy car
        :param basic_speed:
        :param multiplier:
        :return:
        """
        pass

    @abstractmethod
    def on_object_encountered_at_left(self, basic_speed, multiplier):
        """
        the action that will be executed on the event when encountering object at left
        :param basic_speed:
        :param multiplier:
        :return:
        """
        pass

    @abstractmethod
    def on_object_encountered_at_right(self, basic_speed, multiplier):
        """
        the action that will be executed on the event when encountering object at right
        :param basic_speed:
        :param multiplier:
        :return:
        """
        pass

    @abstractmethod
    def on_object_encountered_at_behind(self, basic_speed, multiplier):
        """
        the action that will be executed on the event when encountering object at behind
        :param basic_speed:
        :param multiplier:
        :return:
        """
        pass

    @abstractmethod
    def evaluate_surrounding_status(self, adc_list) -> int:
        """
        checks sensors to get surrounding status code
        :param adc_list:
        :return: if it has encountered anything
        """
        pass

    __method_table: Dict[int, Callable] = {
        KEY_FRONT_ALLY_BOX: on_allay_box_at_front,
        KEY_FRONT_ENEMY_BOX: on_enemy_box_at_front,
        KEY_FRONT_ENEMY_CAR: on_enemy_car_at_front,
        KET_LEFT_OBJECT: on_object_encountered_at_left,
        KEY_RIGHT_OBJECT: on_object_encountered_at_right,
        KEY_BEHIND_OBJECT: on_object_encountered_at_behind
    }

    @final
    def react_to_surroundings(self, adc_list, speed, multiplier) -> int:
        status_code = self.evaluate_surrounding_status(adc_list)
        method: Callable = self.__method_table.get(status_code)
        method(speed, multiplier)
        return status_code
