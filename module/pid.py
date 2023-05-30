import time
from typing import Callable
from time import perf_counter_ns


# TODO: both PD and PID  are haven't react properly on direction change
def PD_control(controller_func: Callable[[int, int], None],
               evaluator_func: Callable[[], float],
               error_func: Callable[[float, float], float],
               target: float,
               Kp: float = 80, Kd: float = 16,
               cs_limit: float = 2000, target_tolerance: float = 15):
    """
    PD controller designed to control the action-T using MPU-6500
    :param controller_func:
    :param evaluator_func:
    :param error_func:
    :param target:
    :param Kp:
    :param Kd:
    :param cs_limit:
    :param target_tolerance:
    :return:
    """

    last_state = evaluator_func()
    last_time = perf_counter_ns()
    current_error = error_func(last_state, target)

    if current_error < target_tolerance and Kp * current_error < cs_limit:
        # control strength is small and current state is near the target
        return

    while True:
        current_state = evaluator_func()
        current_time = perf_counter_ns()

        current_error = error_func(current_state, target)

        d_target = (current_state - last_state) / (current_time - last_time)

        control_strength = int(Kp * current_error + Kd * d_target)
        if current_error < target_tolerance and control_strength < cs_limit:
            controller_func(0, 0)
            break
        controller_func(control_strength, -control_strength)

        last_state = current_state  # 更新前一个状态
        last_time = current_time  # 更新前一个时间


def PID_control(controller_func: Callable[[int, int], None],
                evaluator_func: Callable[[], float],
                error_func: Callable[[float, float], float],
                target: float,
                Kp: float = 80, Kd: float = 16, Ki: float = 2,
                cs_limit: float = 2000, target_tolerance: float = 15):
    """
    PID controller designed to control the action-T using MPU-6500

    :param controller_func:
    :param evaluator_func:
    :param error_func:
    :param target:
    :param Kp:
    :param Kd:
    :param Ki:
    :param cs_limit:
    :param target_tolerance:
    :return:
    """

    last_state = evaluator_func()
    last_time = perf_counter_ns()
    current_error = error_func(last_state, target)

    if current_error < target_tolerance and Kp * current_error < cs_limit:
        # control strength is small and current state is near the target
        return
    i_error = 0
    while True:
        current_state = evaluator_func()
        current_time = perf_counter_ns()

        current_error = error_func(current_state, target)
        delta_time = current_time - last_time

        d_target = (current_state - last_state) / delta_time
        i_error += current_error * delta_time

        control_strength = int(Kp * current_error + Kd * d_target + Ki * i_error)
        if current_error < target_tolerance and control_strength < cs_limit:
            controller_func(0, 0)
            break
        controller_func(control_strength, -control_strength)

        last_state = current_state
        last_time = current_time


class PIDController:
    """
    它包含一个 update 函数，接收所期望的目标值（setpoint）和测量的当前值（measured_value）。
    随着循环不断执行 update 函数，PID 控制器会输出对应的输出值，并根据测量的反馈指挥指令执行下一步操作。
    """

    def __init__(self, Kp: float, Ki: float, Kd: float):
        # TODO: pid的参数应该是要从config.json里面读取的才对，所以最好留一个pid默认值
        """
        用于实现PID控制算法的类

        Attributes:
            Kp (float): 比例增益
            Ki (float): 积分增益
            Kd (float): 微分增益
            total_error (float): 偏差的累积和
            last_error (float): 上一时刻的偏差
            last_time (float): 上一次更新时间，以秒为单位
            cs_limit (float): 容许误差门限值（单位与 Error 值相同）
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.total_error = 0
        self.last_error = 0
        self.last_time = time.time()
        self.state_error_tolerance: float = 5
        self.control_strength_tolerance: float = 100

    def update(self, setpoint, measured_value):
        error = setpoint - measured_value
        current_time = time.time()
        dt = current_time - self.last_time

        proportional_term = self.Kp * error
        integral_term = self.Ki * (self.total_error + error * dt)
        derivative_term = self.Kd * ((error - self.last_error) / dt)

        output = proportional_term + integral_term + derivative_term

        self.last_error = error
        self.total_error += error
        self.last_time = current_time

        return output

    def control_loop(self, state_sampler: Callable[[], float], controller: Callable[[int, int], None],
                     target_state: float,
                     print_info: bool = False) -> None:
        """
         这个函数用于控制一个单值系统,控制执行器默认为

        Args:
            state_sampler: 状态采样器，输出当前状态（例如温度，速度等）
            controller: 控制器，需要两个整型作为参数，根据测量值计算出相应的控制量
            print_info: 是否打印控制细节
            target_state: 目标状态
        Returns:
            None


        """
        min_control_strength = 50
        last_control_strength = None
        last_state = None
        while 1:
            current_state = state_sampler()

            control_strength = int(self.update(target_state, current_state))

            if last_state is not None and self.is_pid_stable(target_state, current_state, control_strength, last_state,
                                                             last_control_strength):
                if print_info:
                    print("state achieved")
                break
            controller(control_strength, -control_strength)
            last_state = current_state
            last_control_strength = control_strength

    def is_pid_stable(self, target_state: float, current_state: float, control_strength: float,
                      last_control_strength: float) -> bool:
        """
        判断PID控制器是否达到目标稳态的函数

        Args:
            target_state (float): 设定值（单位与反馈系统输出值相同）
            current_state (float): 反馈系统输出值（例如传感器测量的数值等）
            control_strength (float): PID控制器的输出值（例如电压、转速等）
            last_state (float): 上次记录的反馈系统输出值
            last_control_strength (float): 上次记录的控制反馈值


        Returns:
            如果系统已经达到目标稳态，则返回True；否则，返回False。
        """

        state_error = abs(target_state - current_state)
        control_delta = abs(control_strength - last_control_strength)

        if state_error < self.state_error_tolerance and control_delta < self.control_strength_tolerance:
            return True
        else:
            return False
