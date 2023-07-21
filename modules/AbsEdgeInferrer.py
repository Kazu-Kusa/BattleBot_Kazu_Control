import json
from abc import ABCMeta, abstractmethod
from typing import final, Tuple, Dict


class AbstractEdgeInferrer(metaclass=ABCMeta):

    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self._config: Dict = json.load(f)
        self.load_config(self._config)
        # TODO: the coupling still needs to be further decremented,but currently i 've got no idea --

    @abstractmethod
    def load_config(self, config: Dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def floating_inferrer(self, edge_sensors: Tuple[int, int, int, int]) -> Tuple[bool, bool, bool, bool]:
        pass

    @final
    def get_away_from_edge(self,
                           edge_sensors: Tuple[int, int, int, int],
                           grays: Tuple[int, int]) -> bool:
        """
        handles the normal edge case using both adc_list and io_list.
        but well do not do anything if no edge case
        :param edge_sensors: the tuple of edge sensors adc returns
        :param grays:the tuple of grays devices returns
        :return: if encounter the edge
        """

        # TODO: add back the edge speed decreasing,added but untested
        # TODO: the speed varying rule can be really annoying. How can we implement it with a low coupling level but
        #       high performance?
        return self.exec_method(edge_sensor_b=self.floating_inferrer(edge_sensors=edge_sensors),
                                grays=grays,
                                basic_speed=sum(edge_sensors))

    # region methods
    @abstractmethod
    def stop(self, basic_speed: int) -> bool:
        pass

    @abstractmethod
    def do_nothing(self, basic_speed: int) -> bool:
        pass

    # TODO: add the basic speed param convey,untested
    @abstractmethod
    def do_fl_n_n_n(self, basic_speed: int) -> bool:
        """
        [fl]         fr
            O-----O
               |
            O-----O
        rl           rr

        front-left encounters the edge, turn right,turn type is 1
        :param basic_speed:
        """
        pass

    @abstractmethod
    def do_n_n_n_fr(self, basic_speed: int) -> bool:
        """
       fl          [fr]
           O-----O
              |
           O-----O
       rl           rr

       front-right encounters the edge, turn left,turn type is 0
        :param basic_speed:
        """
        pass

    @abstractmethod
    def do_n_rl_n_n(self, basic_speed: int) -> bool:
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
    def do_n_n_rr_n(self, basic_speed: int) -> bool:
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
    def do_fl_rl_n_n(self, basic_speed: int) -> bool:
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
    def do_n_n_rr_fr(self, basic_speed: int) -> bool:
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
    def do_n_rl_rr_n(self, basic_speed: int) -> bool:
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
    def do_fl_n_n_fr(self, basic_speed: int) -> bool:
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
    def do_n_rl_rr_fr(self, basic_speed: int) -> bool:
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
    def do_fl_rl_rr_n(self, basic_speed: int) -> bool:
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
    def do_fl_n_rr_fr(self, basic_speed: int) -> bool:
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
    def do_fl_rl_n_fr(self, basic_speed: int) -> bool:
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
    __method_table = {(True, True, True, True): do_nothing,
                      (False, False, False, False): stop,
                      # region one edge sensor only
                      (False, True, True, True): do_fl_n_n_n,
                      (True, False, True, True): do_n_rl_n_n,
                      (True, True, False, True): do_n_n_rr_n,
                      (True, True, True, False): do_n_n_n_fr,
                      # endregion

                      # region double edge sensor only
                      (False, False, True, True): do_fl_rl_n_n,  # normal
                      (True, True, False, False): do_n_n_rr_fr,
                      (True, False, False, True): do_n_rl_rr_n,
                      (False, True, True, False): do_fl_n_n_fr,

                      # region abnormal case
                      (True, False, True, False): do_nothing,  # such case are hard to be classified
                      (False, True, False, True): do_nothing,
                      # endregion
                      # endregion

                      # region triple edge sensor
                      (True, False, False, False): do_n_rl_rr_fr,  # specified in conner
                      (False, False, False, True): do_fl_rl_rr_n,
                      (False, True, False, False): do_fl_n_rr_fr,
                      (False, False, True, False): do_fl_rl_n_fr,
                      # endregion

                      # region grays
                      (1, 1): do_nothing,
                      (0, 1): do_fl_n_n_n,
                      (1, 0): do_n_n_n_fr,
                      (0, 0): do_fl_n_n_fr
                      # endregion
                      }

    @final
    def exec_method(self,
                    edge_sensor_b: Tuple[bool, bool, bool, bool],
                    grays: Tuple[int, int],
                    basic_speed: int) -> bool:
        """
        check the edge_sensor and check the grays
        :param basic_speed:
        :param edge_sensor_b:
        :param grays:
        :return:
        """
        status: bool = self.__method_table.get(edge_sensor_b)(basic_speed=basic_speed)
        if status:
            return True
        return self.__method_table.get(grays)(basic_speed=basic_speed)
