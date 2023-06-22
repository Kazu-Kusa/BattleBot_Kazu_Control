from abc import ABCMeta, abstractmethod
from typing import final

from repo.uptechStar.module.up_controller import UpController


class AbstractEdgeInferrer(metaclass=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def floating_inferrer(self, edge_sensors: tuple[int, int, int, int],
                          *args, **kwargs) -> tuple[bool, bool, bool, bool]:
        pass

    @final
    def get_away_from_edge(self,
                           edge_sensors: tuple[int, int, int, int],
                           grays: tuple[int, int],
                           *args, **kwargs) -> bool:
        # TODO: before the actualize , we should make the sensors return tuple instead of list
        """
        handles the normal edge case using both adc_list and io_list.
        but well do not do anything if no edge case
        :param edge_sensors: the tuple of edge sensors adc returns
        :param grays:the tuple of grays devices returns
        :return: if encounter the edge
        """
        return self.exec_method(edge_sensor_b=self.floating_inferrer(edge_sensors=edge_sensors, *args, **kwargs),
                                grays=grays)

    # region methods
    @abstractmethod
    def stop(self) -> bool:
        pass

    @abstractmethod
    def do_nothing(self) -> bool:
        pass

    @abstractmethod
    def do_fl(self) -> bool:
        """
        [fl]         fr
            O-----O
               |
            O-----O
        rl           rr

        front-left encounters the edge, turn right,turn type is 1
        """
        pass

    @abstractmethod
    def do_fr(self) -> bool:
        """
       fl          [fr]
           O-----O
              |
           O-----O
       rl           rr

       front-right encounters the edge, turn left,turn type is 0
        """
        pass

    @abstractmethod
    def do_rl(self) -> bool:
        """
        fl           fr
            O-----O
               |
            O-----O
        [rl]         rr

        rear-left encounters the edge, turn right,turn type is 1
        """
        pass

    @abstractmethod
    def do_rr(self) -> bool:
        """
        fl           fr
            O-----O
               |
            O-----O
        rl          [rr]

        rear-right encounters the edge, turn left,turn type is 0
        """
        pass

    @abstractmethod
    def do_fl_rl(self) -> bool:
        """
         [fl]   l   r   fr
             O-----O
                |
             O-----O
        [rl]            rr
        :return:
        """
        pass

    @abstractmethod
    def do_fr_rr(self) -> bool:
        """
          fl   l   r  [fr]
             O-----O
                |
             O-----O
         rl           [rr]
        :return:
        """
        pass

    @abstractmethod
    def do_rl_rr(self) -> bool:
        """
         fl   l   r   fr
             O-----O
                |
             O-----O
        [rl]          [rr]
        :return:
        """
        pass

    @abstractmethod
    def do_fl_fr(self) -> bool:
        """
         [fl]   l   r   [fr]
             O-----O
                |
             O-----O
        rl          rr
        :return:
        """
        pass

    @abstractmethod
    def do_fr_rl_rr(self) -> bool:
        """
         fl   l   r   [fr]
             O-----O
                |
             O-----O
        [rl]          [rr]
        :return:
        """
        pass

    @abstractmethod
    def do_fl_rl_rr(self) -> bool:
        """
        [fl]   l   r   fr
             O-----O
                |
             O-----O
        [rl]          [rr]
        :return:
        """
        pass

    @abstractmethod
    def do_fl_fr_rr(self) -> bool:
        """
         [fl]   l   r   [fr]
             O-----O
                |
             O-----O
         rl           [rr]
        :return:
        """
        pass

    @abstractmethod
    def do_fl_fr_rl(self) -> bool:
        """
         [fl]   l   r   [fr]
             O-----O
                |
             O-----O
         [rl]            rr
        :return:
        """
        pass

    # endregion
    method_table = {(True, True, True, True): do_nothing,
                    (False, False, False, False): stop,
                    # region one edge sensor only
                    (False, True, True, True): do_fl,
                    (True, False, True, True): do_fr,
                    (True, True, False, True): do_rl,
                    (True, True, True, False): do_rr,
                    # endregion

                    # region double edge sensor only
                    (False, True, False, True): do_fl_rl,  # normal
                    (True, False, True, False): do_fr_rr,
                    (True, True, False, False): do_rl_rr,
                    (False, False, True, True): do_fl_fr,

                    # region abnormal case
                    (True, False, False, True): do_nothing,  # such case are hard to be classified
                    (False, True, True, False): do_nothing,
                    # endregion
                    # endregion

                    # region triple edge sensor
                    (True, False, False, False): do_fr_rl_rr,  # specified in conner
                    (False, True, False, False): do_fl_rl_rr,
                    (False, False, True, False): do_fl_fr_rr,
                    (False, False, False, True): do_fl_fr_rl,
                    # endregion

                    # region grays
                    (1, 1): do_nothing,
                    (0, 1): do_fl,
                    (1, 0): do_fr,
                    (0, 0): do_fl_fr
                    # endregion
                    }

    @final
    def exec_method(self,
                    edge_sensor_b: tuple[bool, bool, bool, bool],
                    grays: tuple[int, int]) -> bool:
        """

        :param edge_sensor_b:
        :param grays:
        :return:
        """
        if self.method_table.get(grays)():
            return True
        return self.method_table.get(edge_sensor_b)()
