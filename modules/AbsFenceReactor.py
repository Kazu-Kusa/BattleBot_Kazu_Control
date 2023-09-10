from abc import abstractmethod
from typing import final

from repo.uptechStar.module.reactor_base import (
    ReactorBase,
    ComplexAction,
    FlexActionFactory,
)


class AbstractFenceReactor(ReactorBase):
    KEY_NO_FENCE = 0

    KEY_FRONT_TO_FENCE = 1
    KEY_LEFT_TO_FENCE = 2
    KEY_RIGHT_TO_FENCE = 4
    KEY_BEHIND_TO_FENCE = 8

    KEY_FRONT_LEFT_TO_FENCE = KEY_FRONT_TO_FENCE + KEY_LEFT_TO_FENCE  # code: 3
    KEY_FRONT_RIGHT_TO_FENCE = KEY_FRONT_TO_FENCE + KEY_RIGHT_TO_FENCE  # code: 5
    KEY_BEHIND_LEFT_TO_FENCE = KEY_BEHIND_TO_FENCE + KEY_LEFT_TO_FENCE  # code: 10
    KEY_BEHIND_RIGHT_TO_FENCE = KEY_BEHIND_TO_FENCE + KEY_RIGHT_TO_FENCE  # code: 12

    KEY_LEFT_RIGHT_TO_FENCE = KEY_LEFT_TO_FENCE + KEY_RIGHT_TO_FENCE  # code: 6

    KEY_FRONT_BEHIND_TO_FENCE = KEY_FRONT_TO_FENCE + KEY_BEHIND_TO_FENCE  # code: 9

    KEY_FRONT_LEFT_RIGHT_TO_FENCE = (
            KEY_FRONT_TO_FENCE + KEY_LEFT_TO_FENCE + KEY_RIGHT_TO_FENCE
    )  # code: 7

    KEY_FRONT_LEFT_BEHIND_TO_FENCE = (
            KEY_FRONT_TO_FENCE + KEY_LEFT_TO_FENCE + KEY_BEHIND_TO_FENCE
    )  # code: 11

    KEY_FRONT_RIGHT_BEHIND_TO_FENCE = (
            KEY_FRONT_TO_FENCE + KEY_RIGHT_TO_FENCE + KEY_BEHIND_TO_FENCE
    )  # code: 13

    KEY_LEFT_RIGHT_BEHIND_TO_FENCE = (
            KEY_LEFT_TO_FENCE + KEY_RIGHT_TO_FENCE + KEY_BEHIND_TO_FENCE
    )  # code: 14

    KEY_FRONT_LEFT_RIGHT_BEHIND_TO_FENCE = (
            KEY_LEFT_RIGHT_TO_FENCE + KEY_FRONT_BEHIND_TO_FENCE
    )  # code: 15

    def _action_table_init(self):
        self.register_action(
            case=self.KEY_FRONT_TO_FENCE, complex_action=self.on_front_to_fence
        )
        self.register_action(
            case=self.KEY_LEFT_TO_FENCE, complex_action=self.on_left_to_fence
        )
        self.register_action(
            case=self.KEY_RIGHT_TO_FENCE, complex_action=self.on_right_to_fence
        )
        self.register_action(
            case=self.KEY_BEHIND_TO_FENCE, complex_action=self.on_behind_to_fence
        )

        self.register_action(
            case=self.KEY_FRONT_LEFT_TO_FENCE,
            complex_action=self.on_front_left_to_fence,
        )
        self.register_action(
            case=self.KEY_FRONT_RIGHT_TO_FENCE,
            complex_action=self.on_front_right_to_fence,
        )
        self.register_action(
            case=self.KEY_BEHIND_LEFT_TO_FENCE,
            complex_action=self.on_behind_left_to_fence,
        )
        self.register_action(
            case=self.KEY_BEHIND_RIGHT_TO_FENCE,
            complex_action=self.on_behind_right_to_fence,
        )
        self.register_action(
            case=self.KEY_LEFT_RIGHT_TO_FENCE,
            complex_action=self.on_left_right_to_fence,
        )
        self.register_action(
            case=self.KEY_FRONT_BEHIND_TO_FENCE,
            complex_action=self.on_front_behind_to_fence,
        )

        self.register_action(
            case=self.KEY_FRONT_LEFT_RIGHT_TO_FENCE,
            complex_action=self.on_front_left_right_to_fence,
        )
        self.register_action(
            case=self.KEY_FRONT_LEFT_BEHIND_TO_FENCE,
            complex_action=self.on_front_left_behind_to_fence,
        )
        self.register_action(
            case=self.KEY_FRONT_RIGHT_BEHIND_TO_FENCE,
            complex_action=self.on_front_right_behind_to_fence,
        )
        self.register_action(
            case=self.KEY_LEFT_RIGHT_BEHIND_TO_FENCE,
            complex_action=self.on_left_right_behind_to_fence,
        )

        self.register_action(
            case=self.KEY_FRONT_LEFT_RIGHT_BEHIND_TO_FENCE,
            complex_action=self.on_front_left_right_behind_to_fence,
        )
        self.register_action(case=self.KEY_NO_FENCE, complex_action=self.on_no_fence)

        # region methods

    # region one direction to fence
    @abstractmethod
    def on_front_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fence at front
        :param basic_speed: the desired speed

        :return:
        """
        pass

    @abstractmethod
    def on_left_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering a fence at left
        :param basic_speed: the desired speed

        :return:
        """
        pass

    @abstractmethod
    def on_right_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fence at right
        :param basic_speed: the desired speed

        :return:
        """
        pass

    @abstractmethod
    def on_behind_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering a fence at behind
        :param basic_speed: the desired speed

        :return:
        """
        pass

    # endregion

    # region two directions to fence
    @abstractmethod
    def on_front_left_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fence at front left
        :param basic_speed: the desired speed

        :return:
        """
        pass

    @abstractmethod
    def on_front_right_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fence at front right
        :param basic_speed: the desired speed

        :return:
        """
        pass

    @abstractmethod
    def on_behind_left_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fence at behind left
        :param basic_speed: the desired speed

        :return:
        """
        pass

    @abstractmethod
    def on_behind_right_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fence at behind right
        :param basic_speed: the desired speed

        :return:
        """
        pass

    @abstractmethod
    def on_left_right_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fences at the left and right
        :param basic_speed: the desired speed
        """

    @abstractmethod
    def on_front_behind_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fences at the front and behind
        :param basic_speed: the desired speed
        """

    # endregion

    # region three directions to fence
    @abstractmethod
    def on_front_left_right_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fences at the front and left and right
        :param basic_speed: the desired speed
        """

    @abstractmethod
    def on_front_left_behind_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fences at the front and left and behind
        :param basic_speed: the desired speed
        """

    @abstractmethod
    def on_front_right_behind_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fences at the front and right and behind
        :param basic_speed: the desired speed
        """

    @abstractmethod
    def on_left_right_behind_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fences at the left and right and behind
        :param basic_speed: the desired speed
        """

    # endregion

    # region four directions to fence
    @abstractmethod
    def on_no_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when no fence is encountered
        :param basic_speed: the desired speed
        """

    @abstractmethod
    def on_front_left_right_behind_to_fence(self, basic_speed) -> ComplexAction:
        """
        the action that will be executed on the event when encountering fences at the front and left and right and behind
        :param basic_speed: the desired speed
        """

    # endregion

    # endregion

    @abstractmethod
    def infer(self) -> int:
        raise NotImplementedError

    @final
    def exc_action(self, reaction: FlexActionFactory, basic_speed) -> None:
        self._player.override(reaction(basic_speed))
        self._player.play()
