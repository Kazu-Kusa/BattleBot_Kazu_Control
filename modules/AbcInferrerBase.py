import json
from abc import ABCMeta, abstractmethod
from typing import Dict, Any, Hashable, final, Tuple, Optional, Callable, Union
from repo.uptechStar.module.actions import ActionFrame, ActionPlayer

DEFAULT_REACTION = tuple()

ComplexAction = Tuple[Optional[ActionFrame], ...]
ActionFactory = Callable[[Any, ...], ComplexAction]
Reaction = Union[ComplexAction, ActionFactory, Any]


class InferrerBase(metaclass=ABCMeta):
    __action_table: Dict[Hashable, Reaction] = {}

    def __init__(self, player: ActionPlayer, config_path: str):
        self._player: ActionPlayer = player
        with open(config_path, mode='r') as f:
            self._config: Dict = json.load(f)
        self._action_table_init()

    @abstractmethod
    def load_config(self, config: Dict) -> None:
        """
        used to load the important configurations. may not be mandatory
        :param config:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def _action_table_init(self):
        """
        init the method table
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def exc_action(self, reaction: Reaction, *args, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    def infer(self, *args, **kwargs) -> Tuple[Hashable, ...]:
        raise NotImplementedError

    def react(self, *args, **kwargs) -> Any:
        """

        :param args:
        :param kwargs:
        :return:
        """
        reaction = self.get_action(self.infer(*args, **kwargs))
        return self.exc_action(reaction[0])

    @final
    def register_action(self, case: Hashable, complex_action: Reaction) -> None:
        self.__action_table[case] = complex_action

    @final
    def get_action(self, case: Hashable) -> Reaction:
        return self.__action_table.get(case, DEFAULT_REACTION)

    @final
    @property
    def action_table(self) -> Dict:
        return self.__action_table
