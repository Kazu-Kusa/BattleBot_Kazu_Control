from abc import abstractmethod
from typing import final

from repo.uptechStar.module.reactor_base import ReactorBase, FlexActionFactory


class AbstractSearchReactor(ReactorBase):
    CONFIG_MOTION_KEY = "MotionSection"
    CONFIG_BASIC_SPEED_KEY = f"{CONFIG_MOTION_KEY}/BasicSpeed"
    CONFIG_BASIC_DURATION_KEY = f"{CONFIG_MOTION_KEY}/BasicDuration"

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
        self.exc_action(
            self.action_table.get(self.infer()),
            getattr(self, self.CONFIG_BASIC_SPEED_KEY),
        )

    @abstractmethod
    def infer(self) -> int:
        raise NotImplementedError
