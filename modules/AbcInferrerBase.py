import json
from abc import ABCMeta, abstractmethod
from typing import Dict, Any, Hashable, final, Tuple, Optional, Callable, Union
from repo.uptechStar.module.actions import ActionFrame, ActionPlayer

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
    def infer(self, *args, **kwargs) -> Hashable:
        raise NotImplementedError

    @final
    def register_action(self, case: Hashable, complex_action: Reaction) -> None:
        self.__action_table[case] = complex_action

    @final
    def get_action(self, case: Hashable) -> ComplexAction:
        return self.__action_table.get(case, tuple())

    @final
    @property
    def action_table(self) -> Dict:
        return self.__action_table
