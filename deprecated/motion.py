from random import randint
from typing import Callable

from repo.uptechStar.module.algrithm_tools import calculate_relative_angle, compute_inferior_arc
from repo.uptechStar.module.pid import PID_control, PD_control
from repo.uptechStar.module.timer import delay_ms


class Motion:

    def action_BT(self, back_speed: int = 5000, back_time: int = 120,
                  turn_speed: int = 6000, turn_time: int = 120,
                  b_multiplier: float = 0, t_multiplier: float = 0,
                  turn_type: int = randint(0, 1),
                  hind_watcher_func: Callable[[], bool] = None):
        """
        function that execute the action of  backwards and turns
        open loop,actualized by delaying functions
        :param back_speed: the desired back speed,absolute value
        :param back_time:the desired duration of fall backing motion
        :param turn_speed:the desired turn speed,absolute value
        :param turn_time:the desired duration of turning motion
        :param b_multiplier: the multiplier that will be applied to the back_speed
        :param t_multiplier:the multiplier that will be applied to the turn_speed
        if no multiplier is provided ,then the actual speed will be same as the entered params
        :param turn_type: 0 for left,1 for right,default random
        :param hind_watcher_func:watcher function returning boolean value,when true,stops the robot
        :return:
        """
        if b_multiplier:
            back_speed = int(back_speed * b_multiplier)
        self.controller.move_cmd(-back_speed, -back_speed)
        delay_ms(back_time, breaker_func=hind_watcher_func)

        self.action_T(turn_type=turn_type, turn_speed=turn_speed, turn_time=turn_time,
                      multiplier=t_multiplier)

    def action_T_PID(self, offset_angle: float = 90, step: int = 2):
        """

        :param step:
        :param offset_angle: positive for wise, negative for counter-wise
        :return:
        """

        def control(left: int, right: int) -> None:
            self.controller.move_cmd(left, right)
            # print(left)

        def evaluate() -> float:
            temp = self.sensors.atti_all[2]

            return temp

        step_len = offset_angle / step
        for _ in range(step):
            current_angle = evaluate()
            target_angle = calculate_relative_angle(current_angle=current_angle, offset_angle=step_len)

            print(f'current_angle: {current_angle},target_angle: {target_angle}')

            PID_control(controller_func=control,
                        evaluator_func=evaluate,
                        error_func=compute_inferior_arc,
                        target=target_angle,
                        Kp=14, Kd=16e08, Ki=5e-09,
                        cs_limit=4000, target_tolerance=40,
                        smooth_window_size=3, end_pause=False, rip_round=6)
        self.controller.move_cmd(0, 0)

    def action_T_PD(self, offset_angle: float = 90):
        """

        :param offset_angle: positive for wise, negative for counter-wise
        :return:
        """

        def control(left: int, right: int) -> None:
            self.controller.move_cmd(left, right)

        def evaluate() -> float:
            return self.sensors.atti_all[2]

        current_angle = evaluate()
        target_angle = calculate_relative_angle(current_angle=current_angle, offset_angle=offset_angle)

        print(f'current_angle: {current_angle},target_angle: {target_angle}')

        PD_control(controller_func=control,
                   evaluator_func=evaluate,
                   error_func=compute_inferior_arc,
                   target=target_angle,
                   Kp=3, Kd=500,
                   cs_limit=1500, target_tolerance=13)

    def action_T(self, turn_type: int = randint(0, 1), turn_speed: int = 5000, turn_time: int = 130,
                 multiplier: float = 0,
                 breaker_func: Callable[[], bool] = None,
                 break_action_func: Callable[[], None] = None):
        """

        :param break_action_func:
        :param breaker_func:
        :param turn_type: <- turn_type == 0  or turn_type == 1 ->
        :param turn_speed:
        :param turn_time:
        :param multiplier:
        :return:
        """
        if multiplier:
            turn_speed = int(turn_speed * multiplier)

        if turn_type:
            self.controller.move_cmd(turn_speed, -turn_speed)
        else:
            self.controller.move_cmd(-turn_speed, turn_speed)

        if delay_ms(turn_time, breaker_func=breaker_func, break_action_func=break_action_func):
            return

        self.controller.move_cmd(0, 0)

    def action_D(self, dash_speed: int = -13000, dash_time: int = 500,
                 with_turn: bool = False, multiplier: float = 0,
                 breaker_func: Callable[[], bool] = None,
                 break_action_func: Callable[[], None] = None,
                 with_ready: bool = False, ready_time: int = 280):
        if multiplier:
            dash_speed = int(dash_speed * multiplier)
        if with_ready:
            self.controller.move_cmd(-dash_speed, -dash_speed)
            delay_ms(ready_time)
        self.controller.move_cmd(dash_speed, dash_speed)
        if delay_ms(dash_time, breaker_func=breaker_func, break_action_func=break_action_func):
            return
        self.controller.move_cmd(0, 0)
        if with_turn:
            # TODO:reset to default state may trigger bug
            self.action_T()

    def action_TF(self, fixed_wheel_id: int = 1, speed: int = 8000, tf_time=300, multiplier: float = 0) -> None:
        """
        w4[fl]       [fr]w2
              O-----O
                 |
              O-----O
        w3[rl]       [rr]w1


        :param fixed_wheel_id: the id fo the wheel that will be set to fixed in the tail flicking
        :param speed: the tail flicking speed
        :param tf_time: the duration of the tail flicking
        :param multiplier: the multiplier of the tail flicking
        :return: None
        """
        if multiplier:
            speed = multiplier * speed
        speed_list: list[int] = [speed, speed, -speed, -speed]
        speed_list[fixed_wheel_id - 1] = 0
        self.controller.set_motors_speed(speed_list=speed_list)
        delay_ms(tf_time)
        self.controller.move_cmd(0, 0)

    def action_LS(self, start_speed: int, end_speed: int, duration: int, resolution: int = 30):
        """
        liner speed
        :param start_speed:
        :param end_speed:
        :param duration:
        :param resolution:
        :return:
        """
        # TODO: add a breaker function option
        acc = int((end_speed - start_speed) / duration) * resolution
        control_counts = int(duration / resolution)
        for _ in range(control_counts):
            self.controller.move_cmd(start_speed, start_speed)
            start_speed += acc
            delay_ms(resolution)

    def action_DS(self, outer_speed: int, inner_speed_multiplier: float, turn_type: int, duration: int):
        if turn_type:
            self.controller.move_cmd(outer_speed * inner_speed_multiplier, outer_speed)
        else:
            self.controller.move_cmd(outer_speed, outer_speed * inner_speed_multiplier)
        delay_ms(duration)
