from abc import abstractmethod
from typing import final, Tuple, Any, Callable, Sequence
from repo.uptechStar.module.inferrer_base import InferrerBase
from repo.uptechStar.module.actions import ActionFrame

ActionPack = Tuple[Sequence[ActionFrame], int]

ActionBuilder = Callable[[int], ActionPack]


class AbstractEdgeInferrer(InferrerBase):

    @abstractmethod
    def infer(self, edge_sensors: Tuple[int, int, int, int]) -> Tuple[bool, bool, bool, bool]:
        raise NotImplementedError

    def exc_action(self, reaction: ActionBuilder, *args, **kwargs) -> Any:
        """
        all parameters are passed to the reaction function
        :param reaction:
        :param args:
        :param kwargs:
        :return:
        """
        complex_action, status_code = reaction
        self._player.override(complex_action(*args, **kwargs))

        return status_code

    # region methods
    @abstractmethod
    def do_nothing(self, basic_speed: int) -> ActionPack:
        raise NotImplementedError

    @abstractmethod
    def stop(self, basic_speed: int) -> ActionPack:
        raise NotImplementedError

    @abstractmethod
    def do_fl_n_n_n(self, basic_speed: int) -> ActionPack:
        """
        [fl]         fr
            O-----O
               |
            O-----O
        rl           rr

        front-left encounters the edge, turn right,turn type is 1
        :param basic_speed:
        """
        raise NotImplementedError

    @abstractmethod
    def do_n_n_n_fr(self, basic_speed: int) -> ActionPack:
        """
       fl          [fr]
           O-----O
              |
           O-----O
       rl           rr

       front-right encounters the edge, turn left,turn type is 0
        :param basic_speed:
        """
        raise NotImplementedError

    @abstractmethod
    def do_n_rl_n_n(self, basic_speed: int) -> ActionPack:
        """
        fl           fr
            O-----O
               |
            O-----O
        [rl]         rr

        rear-left encounters the edge, turn right,turn type is 1
        """
        raise NotImplementedError

    @abstractmethod
    def do_n_n_rr_n(self, basic_speed: int) -> ActionPack:
        """
        fl           fr
            O-----O
               |
            O-----O
        rl          [rr]

        rear-right encounters the edge, turn left,turn type is 0
        """
        raise NotImplementedError

    @abstractmethod
    def do_fl_rl_n_n(self, basic_speed: int) -> ActionPack:
        """
         [fl]   l   r   fr
             O-----O
                |
             O-----O
        [rl]            rr
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def do_n_n_rr_fr(self, basic_speed: int) -> ActionPack:
        """
          fl   l   r  [fr]
             O-----O
                |
             O-----O
         rl           [rr]
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def do_n_rl_rr_n(self, basic_speed: int) -> ActionPack:
        """
         fl   l   r   fr
             O-----O
                |
             O-----O
        [rl]          [rr]
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def do_fl_n_n_fr(self, basic_speed: int) -> ActionPack:
        """
         [fl]   l   r   [fr]
             O-----O
                |
             O-----O
        rl          rr
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def do_n_rl_n_fr(self, basic_speed: int) -> ActionPack:
        """
         fl   l   r   [fr]
             O-----O
                |
             O-----O
        [rl]         rr
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def do_fl_n_rr_n(self, basic_speed: int) -> ActionPack:
        """
         [fl]   l   r   fr
             O-----O
                |
             O-----O
        rl           [rr]
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def do_n_rl_rr_fr(self, basic_speed: int) -> ActionPack:
        """
         fl   l   r   [fr]
             O-----O
                |
             O-----O
        [rl]          [rr]
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def do_fl_rl_rr_n(self, basic_speed: int) -> ActionPack:
        """
        [fl]   l   r   fr
             O-----O
                |
             O-----O
        [rl]          [rr]
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def do_fl_n_rr_fr(self, basic_speed: int) -> ActionPack:
        """
         [fl]   l   r   [fr]
             O-----O
                |
             O-----O
         rl           [rr]
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def do_fl_rl_n_fr(self, basic_speed: int) -> ActionPack:
        """
         [fl]   l   r   [fr]
             O-----O
                |
             O-----O
         [rl]            rr
        :return:
        """
        raise NotImplementedError

    # endregion
    @final
    def _action_table_init(self):
        # region idle case
        self.register_action(case=(True, True, True, True),
                             complex_action=self.do_nothing)
        self.register_action(case=(False, False, False, False),
                             complex_action=self.stop)
        # endregion

        # region 1 side float case
        self.register_action(case=(False, True, True, True),
                             complex_action=self.do_fl_n_n_n)
        self.register_action(case=(True, False, True, True),
                             complex_action=self.do_n_rl_n_n)
        self.register_action(case=(True, True, False, True),
                             complex_action=self.do_n_n_rr_n)
        self.register_action(case=(True, True, True, False),
                             complex_action=self.do_n_n_n_fr)
        # endregion

        # region 2 sides float case
        self.register_action(case=(False, False, True, True),
                             complex_action=self.do_fl_rl_n_n)
        self.register_action(case=(True, True, False, False),
                             complex_action=self.do_n_n_rr_fr)
        self.register_action(case=(True, False, False, True),
                             complex_action=self.do_n_rl_rr_n)
        self.register_action(case=(False, True, True, False),
                             complex_action=self.do_fl_n_n_fr)

        # region abnormal 2 sides float case
        self.register_action(case=(True, False, True, False),
                             complex_action=self.do_n_rl_n_fr)
        self.register_action(case=(False, True, False, True),
                             complex_action=self.do_fl_n_rr_n)
        # endregion
        # endregion

        # region 3 sides float case
        self.register_action(case=(True, False, False, False),
                             complex_action=self.do_n_rl_rr_fr)
        self.register_action(case=(False, True, False, False),
                             complex_action=self.do_fl_n_rr_fr)
        self.register_action(case=(False, False, True, False),
                             complex_action=self.do_fl_rl_n_fr)
        self.register_action(case=(False, False, False, True),
                             complex_action=self.do_fl_rl_rr_n)
        # endregion

        # region grays case
        self.register_action(case=(1, 1),
                             complex_action=self.do_nothing)
        self.register_action(case=(0, 1),
                             complex_action=self.do_fl_n_n_n)
        self.register_action(case=(1, 0),
                             complex_action=self.do_n_n_n_fr)
        self.register_action(case=(0, 0),
                             complex_action=self.do_fl_n_n_fr)
        # endregion
