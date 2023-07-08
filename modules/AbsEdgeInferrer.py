import json
from abc import ABCMeta, abstractmethod
from typing import final, Tuple


class AbstractEdgeInferrer(metaclass=ABCMeta):

    def __init__(self, config_path: str):
        self._config: dict = self.load_config(config_path)
        self.edge_multiplier: float = self._config.get('edge_multiplier')

    @classmethod
    def load_config(cls, config_path: str) -> dict:
        with open(config_path, 'r') as f:
            return json.load(f)

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

        return self.exec_method(edge_sensor_b=self.floating_inferrer(edge_sensors=edge_sensors),
                                grays=grays,
                                basic_speed=int(self.edge_multiplier * sum(edge_sensors)))

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
    method_table = {(True, True, True, True): do_nothing,
                    (False, False, False, False): stop,
                    # region one edge sensor only
                    (False, True, True, True): do_fl_n_n_n,
                    (True, False, True, True): do_n_n_n_fr,
                    (True, True, False, True): do_n_rl_n_n,
                    (True, True, True, False): do_n_n_rr_n,
                    # endregion

                    # region double edge sensor only
                    (False, True, False, True): do_fl_rl_n_n,  # normal
                    (True, False, True, False): do_n_n_rr_fr,
                    (True, True, False, False): do_n_rl_rr_n,
                    (False, False, True, True): do_fl_n_n_fr,

                    # region abnormal case
                    (True, False, False, True): do_nothing,  # such case are hard to be classified
                    (False, True, True, False): do_nothing,
                    # endregion
                    # endregion

                    # region triple edge sensor
                    (True, False, False, False): do_n_rl_rr_fr,  # specified in conner
                    (False, True, False, False): do_fl_rl_rr_n,
                    (False, False, True, False): do_fl_n_rr_fr,
                    (False, False, False, True): do_fl_rl_n_fr,
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
        status: bool = self.method_table.get(edge_sensor_b)(basic_speed=basic_speed)
        if status:
            return True
        return self.method_table.get(grays)(basic_speed=basic_speed)
