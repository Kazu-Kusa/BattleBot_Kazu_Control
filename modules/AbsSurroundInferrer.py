from abc import abstractmethod
from typing import final, Callable

from repo.uptechStar.module.inferrer_base import InferrerBase, ComplexAction

FlexActionFactory = Callable[[int], ComplexAction]


class AbstractSurroundInferrer(InferrerBase):
    """
    There are
    """

    # region SURROUNDING KEYS
    KEY_LEFT_OBJECT = 1

    KEY_RIGHT_OBJECT = 2

    KEY_BEHIND_OBJECT = 4

    KEY_LEFT_RIGHT_OBJECTS = 3

    KEY_LEFT_BEHIND_OBJECTS = 5

    KEY_RIGHT_BEHIND_OBJECTS = 6

    KEY_LEFT_RIGHT_BEHIND_OBJECTS = 7
    # endregion

    # region BASIC KEYS
    KEY_FRONT_ENEMY_CAR = 400

    KEY_FRONT_ENEMY_BOX = 300

    KEY_FRONT_NEUTRAL_BOX = 200

    KEY_FRONT_ALLY_BOX = 100

    KEY_NOTHING = 0
    # endregion

    # region ALLY BOX AND SURROUNDINGS
    KEY_FRONT_ALLY_BOX_LEFT_OBJECT = KEY_FRONT_ALLY_BOX + KEY_LEFT_OBJECT

    KEY_FRONT_ALLY_BOX_RIGHT_OBJECT = KEY_FRONT_ALLY_BOX + KEY_RIGHT_OBJECT

    KEY_FRONT_ALLY_BOX_BEHIND_OBJECT = KEY_FRONT_ALLY_BOX + KEY_BEHIND_OBJECT

    KEY_FRONT_ALLY_BOX_LEFT_RIGHT_OBJECTS = KEY_FRONT_ALLY_BOX + KEY_LEFT_RIGHT_OBJECTS

    KEY_FRONT_ALLY_BOX_LEFT_BEHIND_OBJECTS = KEY_FRONT_ALLY_BOX + KEY_LEFT_BEHIND_OBJECTS

    KEY_FRONT_ALLY_BOX_RIGHT_BEHIND_OBJECTS = KEY_FRONT_ALLY_BOX + KEY_RIGHT_BEHIND_OBJECTS

    KEY_FRONT_ALLY_BOX_LEFT_RIGHT_BEHIND_OBJECTS = KEY_FRONT_ALLY_BOX + KEY_LEFT_RIGHT_BEHIND_OBJECTS
    # endregion

    # region ENEMY BOX AND SURROUNDINGS
    KEY_FRONT_ENEMY_BOX_LEFT_OBJECT = KEY_FRONT_ENEMY_BOX + KEY_LEFT_OBJECT

    KEY_FRONT_ENEMY_BOX_RIGHT_OBJECT = KEY_FRONT_ENEMY_BOX + KEY_RIGHT_OBJECT

    KEY_FRONT_ENEMY_BOX_BEHIND_OBJECT = KEY_FRONT_ENEMY_BOX + KEY_BEHIND_OBJECT

    KEY_FRONT_ENEMY_BOX_LEFT_RIGHT_OBJECTS = KEY_FRONT_ENEMY_BOX + KEY_LEFT_RIGHT_OBJECTS

    KEY_FRONT_ENEMY_BOX_LEFT_BEHIND_OBJECTS = KEY_FRONT_ENEMY_BOX + KEY_LEFT_BEHIND_OBJECTS

    KEY_FRONT_ENEMY_BOX_RIGHT_BEHIND_OBJECTS = KEY_FRONT_ENEMY_BOX + KEY_RIGHT_BEHIND_OBJECTS

    KEY_FRONT_ENEMY_BOX_LEFT_RIGHT_BEHIND_OBJECTS = KEY_FRONT_ENEMY_BOX + KEY_LEFT_RIGHT_BEHIND_OBJECTS
    # endregion

    # region NEUTRAL BOX AND SURROUNDINGS
    KEY_FRONT_NEUTRAL_BOX_LEFT_OBJECT = KEY_FRONT_NEUTRAL_BOX + KEY_LEFT_OBJECT

    KEY_FRONT_NEUTRAL_BOX_RIGHT_OBJECT = KEY_FRONT_NEUTRAL_BOX + KEY_RIGHT_OBJECT

    KEY_FRONT_NEUTRAL_BOX_BEHIND_OBJECT = KEY_FRONT_NEUTRAL_BOX + KEY_BEHIND_OBJECT

    KEY_FRONT_NEUTRAL_BOX_LEFT_RIGHT_OBJECTS = KEY_FRONT_NEUTRAL_BOX + KEY_LEFT_RIGHT_OBJECTS

    KEY_FRONT_NEUTRAL_BOX_LEFT_BEHIND_OBJECTS = KEY_FRONT_NEUTRAL_BOX + KEY_LEFT_BEHIND_OBJECTS

    KEY_FRONT_NEUTRAL_BOX_RIGHT_BEHIND_OBJECTS = KEY_FRONT_NEUTRAL_BOX + KEY_RIGHT_BEHIND_OBJECTS

    KEY_FRONT_NEUTRAL_BOX_LEFT_RIGHT_BEHIND_OBJECTS = KEY_FRONT_NEUTRAL_BOX + KEY_LEFT_RIGHT_BEHIND_OBJECTS

    # endregion

    # region ENEMY CAR AND SURROUNDINGS
    KEY_FRONT_ENEMY_CAR_LEFT_OBJECT = KEY_FRONT_ENEMY_CAR + KEY_LEFT_OBJECT

    KEY_FRONT_ENEMY_CAR_RIGHT_OBJECT = KEY_FRONT_ENEMY_CAR + KEY_RIGHT_OBJECT

    KEY_FRONT_ENEMY_CAR_BEHIND_OBJECT = KEY_FRONT_ENEMY_CAR + KEY_BEHIND_OBJECT

    KEY_FRONT_ENEMY_CAR_LEFT_RIGHT_OBJECTS = KEY_FRONT_ENEMY_CAR + KEY_LEFT_RIGHT_OBJECTS

    KEY_FRONT_ENEMY_CAR_LEFT_BEHIND_OBJECTS = KEY_FRONT_ENEMY_CAR + KEY_LEFT_BEHIND_OBJECTS

    KEY_FRONT_ENEMY_CAR_RIGHT_BEHIND_OBJECTS = KEY_FRONT_ENEMY_CAR + KEY_RIGHT_BEHIND_OBJECTS

    KEY_FRONT_ENEMY_CAR_LEFT_RIGHT_BEHIND_OBJECTS = KEY_FRONT_ENEMY_CAR + KEY_LEFT_RIGHT_BEHIND_OBJECTS

    # endregion

    @abstractmethod
    def react(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def infer(self, *args, **kwargs) -> int:
        raise NotImplementedError

    def exc_action(self, reaction: FlexActionFactory, basic_speed: int) -> None:
        self._player.override(reaction(basic_speed))
        self._player.play()

    @final
    def _action_table_init(self):
        self.register_action(case=self.KEY_NOTHING,
                             complex_action=self.on_nothing)
        self.register_action(case=self.KEY_FRONT_ENEMY_CAR,
                             complex_action=self.on_enemy_car_encountered_at_front)
        self.register_action(case=self.KEY_FRONT_ENEMY_BOX,
                             complex_action=self.on_enemy_box_encountered_at_front)
        self.register_action(case=self.KEY_FRONT_ALLY_BOX,
                             complex_action=self.on_allay_box_encountered_at_front)

        self.register_action(case=self.KEY_BEHIND_OBJECT,
                             complex_action=self.on_object_encountered_at_behind)
        self.register_action(case=self.KEY_RIGHT_OBJECT,
                             complex_action=self.on_object_encountered_at_right)
        self.register_action(case=self.KEY_LEFT_OBJECT,
                             complex_action=self.on_object_encountered_at_left)
        self.register_action(case=self.KEY_LEFT_RIGHT_OBJECTS,
                             complex_action=self.on_objects_encountered_at_left_right)

    # region methods

    # region Description
    @abstractmethod
    def on_nothing(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering nothing
        :param basic_speed: the desired speed
        :return:
        """
        pass

    @abstractmethod
    def on_neutral_box_encountered_at_front(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering neutral box
        :param basic_speed: the desired speed
        :return:
        """
        pass

    @abstractmethod
    def on_allay_box_encountered_at_front(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering allay box
        :param basic_speed: the desired speed the desired speed multiplier
        :return: the desired speed
        """
        pass

    @abstractmethod
    def on_enemy_box_encountered_at_front(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy box
        :param basic_speed: the desired speed
        :return:
        """
        pass

    @abstractmethod
    def on_enemy_car_encountered_at_front(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering an enemy car
        :param basic_speed: the desired speed
        :return:
        """
        pass

    # endregion

    # region Surroundings Methods
    @abstractmethod
    def on_object_encountered_at_left(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering an object at the left
        :param basic_speed:
        :return:
        """
        pass

    @abstractmethod
    def on_object_encountered_at_right(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering an object at right
        :param basic_speed:
        :return:
        """
        pass

    @abstractmethod
    def on_object_encountered_at_behind(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering an object at behind
        :param basic_speed:
        :return:
        """
        pass

    @abstractmethod
    def on_objects_encountered_at_left_right(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering an object at left right
        :param basic_speed:
        :return:
        """
        pass

    @abstractmethod
    def on_objects_encountered_at_left_behind(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering an object at left behind
        :param basic_speed:
        :return:
        """
        pass

    @abstractmethod
    def on_objects_encountered_at_right_behind(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering an object at right behind
        :param basic_speed:
        :return:
        """
        pass

    @abstractmethod
    def on_objects_encountered_at_left_right_behind(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering an object at left right behind
        :param basic_speed:
        :return:
        """
        pass

    # endregion

    # region Neutral Box and Surroundings Methods
    @abstractmethod
    def on_neutral_box_encountered_at_front_with_left_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering neutral box and left object
        :param basic_speed: the desired speed
        :return:
        """
        pass

    @abstractmethod
    def on_neutral_box_encountered_at_front_with_right_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering neutral box and right object
        :param basic_speed: the desired speed
        :return:
        """
        pass

    @abstractmethod
    def on_neutral_box_encountered_at_front_with_behind_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering neutral box and behind object
        :param basic_speed: the desired speed
        :return:
        """
        pass

    @abstractmethod
    def on_neutral_box_encountered_at_front_with_left_right_objects(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering neutral box and left right objects
        :param basic_speed: the desired speed
        :return:
        """
        pass

    @abstractmethod
    def on_neutral_box_encountered_at_front_with_left_behind_objects(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering neutral box and left behind objects
        :param basic_speed: the desired speed
        :return:
        """
        pass

    @abstractmethod
    def on_neutral_box_encountered_at_front_with_right_behind_objects(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering neutral box and right behind objects
        :param basic_speed: the desired speed
        :return:
        """
        pass

    @abstractmethod
    def on_neutral_box_encountered_at_front_with_left_right_behind_objects(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering neutral box and left right behind objects
        :param basic_speed: the desired speed
        :return:
        """
        pass

    # endregion

    # region Allay Box and Surroundings Methods
    @abstractmethod
    def on_ally_box_encountered_at_front_with_left_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering allay box and left object
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_ally_box_encountered_at_front_with_right_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering allay box and right object
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_ally_box_encountered_at_front_with_behind_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering allay box and behind object
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_ally_box_encountered_at_front_with_left_right_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering allay box and left right objects
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_ally_box_encountered_at_front_with_left_behind_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering allay box and left behind objects
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_ally_box_encountered_at_front_with_right_behind_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering allay box and right behind objects
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_ally_box_encountered_at_front_with_left_right_behind_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering allay box and left right behind objects
        :param basic_speed: the desired speed
        :return:

        """
        pass

    # endregion

    # region Enemy Box and Surroundings Methods
    @abstractmethod
    def on_enemy_box_encountered_at_front_with_left_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy box and left object
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_enemy_box_encountered_at_front_with_right_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy box and right object
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_enemy_box_encountered_at_front_with_behind_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy box and behind object
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_enemy_box_encountered_at_front_with_left_right_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy box and left right objects
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_enemy_box_encountered_at_front_with_left_behind_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy box and left behind objects
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_enemy_box_encountered_at_front_with_right_behind_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy box and right behind objects
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_enemy_box_encountered_at_front_with_left_right_behind_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy box and left right behind objects
        :param basic_speed: the desired speed
        :return:

        """
        pass

    # endregion

    # region Enemy Box and Surroundings Methods
    @abstractmethod
    def on_enemy_car_encountered_at_front_with_left_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy car and left object
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_enemy_car_encountered_at_front_with_right_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy car and right object
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_enemy_car_encountered_at_front_with_behind_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy car and behind object
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_enemy_car_encountered_at_front_with_left_right_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy car and left right objects
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_enemy_car_encountered_at_front_with_left_behind_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy car and left behind objects
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_enemy_car_encountered_at_front_with_right_behind_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy car and right behind objects
        :param basic_speed: the desired speed
        :return:

        """
        pass

    @abstractmethod
    def on_enemy_car_encountered_at_front_with_left_right_behind_object(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering enemy car and left right behind objects
        :param basic_speed: the desired speed
        :return:

        """
        pass
    # endregion

    # endregion
