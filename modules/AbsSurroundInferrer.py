from abc import ABCMeta, abstractmethod


class AbstractSurroundInferrer(metaclass=ABCMeta):
    @abstractmethod
    def scan_surround(self, detector, with_ready, ready_time, with_dash, dash_speed, dash_time, dash_breaker_func,
                      dash_breaker_action_func, with_turn, spinning_type, spinning_speed, max_duration):
        """
        checking the stage direction and make the dash movement accordingly
        :param ready_time:
        :param with_ready:
        :param dash_breaker_action_func:
        :param dash_breaker_func:
        :param dash_speed:
        :param dash_time:
        :param with_turn:
        :param detector:
        :param with_dash:
        :param spinning_type:
        :param spinning_speed:
        :param max_duration:
        :return:
        """
        pass

    @abstractmethod
    def on_allay_box(self, speed, multiplier):
        """
        the action that will be executed on the event when encountering allay box
        :param speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        pass

    @abstractmethod
    def on_enemy_box(self, speed, multiplier):
        """
        the action that will be executed on the event when encountering enemy box
        :param speed:
        :param multiplier:
        :return:
        """
        pass

    @abstractmethod
    def on_enemy_car(self, speed, multiplier):
        """
        the action that will be executed on the event when encountering enemy car
        :param speed:
        :param multiplier:
        :return:
        """
        pass

    @abstractmethod
    def on_thing_surrounding(self, position_type, rotate_time, rotate_speed):
        """
        0 for left
        1 for right
        2 for behind
        :param rotate_speed:
        :param rotate_time:
        :param position_type:
        :return:
        """
        pass

    @abstractmethod
    def on_attacked(self, position_type, counter_back, run_away, run_speed, run_time, run_away_breaker_func,
                    run_away_break_action_func, reacting_speed, reacting_time):
        """
        use action tf to evade attacks
        :param run_away_break_action_func:
        :param run_away_breaker_func:
        :param run_time:
        :param run_away:
        :param run_speed:
        :param counter_back:
        :param position_type:
        :param reacting_speed:
        :param reacting_time:
        :return:
        """
        pass

    @abstractmethod
    def check_surround(self, adc_list, baseline, basic_speed, evade_prob):
        """
        checks sensors to get surrounding objects
        :param evade_prob:
        :param basic_speed:
        :param adc_list:
        :param baseline:
        :return: if it has encountered anything
        """
        pass
