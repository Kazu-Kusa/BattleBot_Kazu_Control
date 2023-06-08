import warnings
from random import randint, choice
from typing import Callable
from time import perf_counter_ns

from bot import Bot
from repo.uptechStar.module.timer import delay_ms, get_end_time_ms
from repo.uptechStar.module.algrithm_tools import compute_inferior_arc, calculate_relative_angle
from repo.uptechStar.module.pid import PD_control, PID_control


class BattleBot(Bot):

    # region basic actions
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
            temp = self.controller.atti_all[2]

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
            return self.controller.atti_all[2]

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
                 multiplier: float = 0):
        """

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
        delay_ms(turn_time)
        self.controller.move_cmd(0, 0)

    def action_D(self, dash_speed: int = -13000, dash_time: int = 500,
                 with_turn: bool = False):
        self.controller.move_cmd(dash_speed, dash_speed)
        delay_ms(dash_time)
        self.controller.move_cmd(0, 0)
        if with_turn:
            self.action_T(turn_speed=7000, turn_time=140)

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
        speed_list: list[int] = [speed, speed, speed, speed]
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

    # endregion

    # region special actions
    def wait_start(self, baseline: int = 1800, check_interval: int = 50,
                   with_turn: bool = False, dash_time: int = 600, dash_speed: int = 8000) -> None:
        """
        hold still util the start signal is received
        :param check_interval:
        :param dash_time:
        :param baseline:
        :param with_turn:
        :return:
        """
        self.screen.ADC_Led_SetColor(0, self.screen.COLOR_BROWN)
        while True:
            print('\r##HALT##')
            delay_ms(check_interval)
            # TODO: shall we make this change be a local function that passed into here as param?
            temp_list = self.controller.adc_all_channels
            if temp_list[8] > baseline and temp_list[7] > baseline:
                print('!!DASH-TIME!!')
                self.action_D(with_turn=with_turn, dash_time=dash_time, dash_speed=dash_speed)
                return

    def checking_stage_direction(self, detector: Callable[[], bool], with_dash: bool = False,
                                 spinning_type=randint(0, 1), spinning_speed: int = 2500, max_duration: int = 3000):
        """
        checking the stage direction and make the dash movement accordingly
        :param detector:
        :param with_dash:
        :param spinning_type:
        :param spinning_speed:
        :param max_duration:
        :return:
        """
        warnings.warn('Checking stage direction')
        end_time = get_end_time_ms(max_duration)
        if spinning_type:
            spinning_speed = -spinning_speed
        self.controller.move_cmd(spinning_speed, -spinning_speed)
        while perf_counter_ns() < end_time:
            if detector():
                self.controller.move_cmd(0, 0)
                if with_dash:
                    # TODO: debug params,dont forget toa changewith_dash:bool=Falsewith_dash:bool=False
                    self.action_D(dash_time=700, with_turn=False, dash_speed=-6000)
                break

    # endregion

    # region events
    def util_edge(self, using_gray: bool = True, using_edge_sensor: bool = False, edge_a: int = 1800):
        """
        a conditioned delay function ,will delay util the condition is satisfied
        :param using_gray: use the gray the judge if the condition is satisfied
        :param using_edge_sensor: use the edge sensors to judge if the condition is satisfied
        :param edge_a: edge sensors judge baseline
        :return:
        """
        if using_gray:
            io_list = self.controller.io_all_channels
            while int(io_list[6]) + int(io_list[7]) > 1:
                io_list = self.controller.io_all_channels
        elif using_edge_sensor:
            adc_list = self.controller.adc_all_channels
            while adc_list[1] < edge_a or adc_list[2] < edge_a:
                adc_list = self.controller.adc_all_channels

    def on_ally_box(self, speed: int = 5000, multiplier: float = 0):
        """
        the action that will be executed on the event when encountering ally box
        :param speed: the desired speed
        :param multiplier: the desired speed multiplier
        :return:
        """
        self.action_T(turn_speed=speed, multiplier=multiplier)

    def on_enemy_box(self, speed: int = 8000, multiplier: float = 0):
        """
        the action that will be executed on the event when encountering enemy box
        :param speed:
        :param multiplier:
        :return:
        """

        if multiplier:
            speed = int(multiplier * speed)
        self.controller.move_cmd(speed, speed)
        self.util_edge()
        self.controller.move_cmd(-speed, -speed)
        delay_ms(160)
        self.controller.move_cmd(0, 0)

    def on_enemy_car(self, speed: int = 8000, multiplier: float = 0):
        """
        the action that will be executed on the event when encountering enemy car
        :param speed:
        :param multiplier:
        :return:
        """
        if multiplier:
            speed = int(multiplier * speed)
        self.controller.move_cmd(speed, speed)
        self.util_edge()
        if multiplier:
            speed = int(multiplier * speed)
        self.controller.move_cmd(-speed, -speed)
        delay_ms(160)
        self.controller.move_cmd(0, 0)

    def on_thing_surrounding(self, position_type: int = 0, rotate_time: int = 160, rotate_speed: int = 6000):
        """
        0 for left
        1 for right
        2 for behind
        :param rotate_speed:
        :param rotate_time:
        :param position_type:
        :return:
        """
        if position_type == 2:
            self.action_T(turn_speed=rotate_speed, turn_time=rotate_time, multiplier=1.8)
        else:
            self.action_T(turn_type=position_type, turn_speed=rotate_speed, turn_time=rotate_time)

    def on_attacked(self, position_type: int, counter_back: bool = False,
                    run_away: bool = False,
                    run_speed: int = 5000, run_time: int = 400,
                    action_break_func: Callable[[], bool] = None,
                    reacting_speed: int = 8000, reacting_time: int = 300):
        """
        use action tf to evade attacks
        :param run_time: 
        :param run_away: 
        :param run_speed: 
        :param action_break_func: 
        :param counter_back:
        :param position_type:
        :param reacting_speed:
        :param reacting_time:
        :return:
        """
        # TODO make all actions support action break function
        if position_type == 0:
            if counter_back:
                self.action_TF(fixed_wheel_id=4, speed=reacting_speed, tf_time=reacting_time)
            else:
                self.action_TF(fixed_wheel_id=3, speed=-reacting_speed, tf_time=reacting_time)
                if run_away:
                    self.action_D(dash_speed=run_speed, dash_time=run_time)

        elif position_type == 1:
            if counter_back:
                self.action_TF(fixed_wheel_id=2, speed=reacting_speed, tf_time=reacting_time)
            else:
                self.action_TF(fixed_wheel_id=1, speed=-reacting_speed, tf_time=reacting_time)
                if run_away:
                    self.action_D(dash_speed=run_speed, dash_time=run_time)
        elif position_type == 2:
            if counter_back:
                reacting_time = reacting_time * 1.6
            self.action_TF(fixed_wheel_id=choice([1, 3]), speed=reacting_speed, tf_time=reacting_time)

    # endregion

    def get_away_from_edge(self, adc_list: list[int], io_list: list[int], edge_baseline: int = 1680,
                           edge_speed_multiplier: float = 0, backing_time: int = 180, turn_time: int = 160) -> bool:
        """
        handles the normal edge case using both adc_list and io_list.
        but well do not do anything if no edge case
        :param backing_time:
        :param turn_time:
        :param edge_speed_multiplier:
        :param adc_list:the list of adc devices returns
        :param io_list:the list of io devices returns
        :param edge_baseline: the edge_check baseline
        :return: if encounter the edge
        """
        # change the light color to represent current state, state of in normal behave
        self.screen.ADC_Led_SetColor(0, self.screen.COLOR_BLUE)

        # read the adc sensors
        edge_rr_sensor = adc_list[0]
        edge_fr_sensor = adc_list[1]
        edge_fl_sensor = adc_list[2]
        edge_rl_sensor = adc_list[3]

        # read the io sensors
        l_gray = io_list[6]
        r_gray = io_list[7]

        # use the sum of their returns to get the high_speed
        # the closer to the edge ,the slower the wheels rotates
        high_spead = 4 * min(edge_rl_sensor, edge_fl_sensor, edge_fr_sensor, edge_rr_sensor)
        if edge_speed_multiplier:
            # multiplier to adjust the high_speed
            high_spead = int(high_spead * edge_speed_multiplier)

        # fixed action duration
        def watcher() -> bool:

            temp = self.controller.adc_all_channels
            local_edge_rr_sensor = temp[0]
            local_edge_rl_sensor = temp[3]
            if local_edge_rl_sensor < edge_baseline or local_edge_rr_sensor < edge_baseline:
                # if at least one of the edge sensor is hanging over air
                return True
            else:
                return False

        if l_gray + r_gray <= 1:
            # at least one of the gray scaler is hanging over air

            self.action_BT(back_speed=high_spead, back_time=backing_time,
                           turn_speed=high_spead, turn_time=turn_time,
                           t_multiplier=1.5, hind_watcher_func=watcher)
            return True
        elif edge_fl_sensor < edge_baseline:
            """
            [fl]         fr
                O-----O
                   |
                O-----O
            rl           rr
            
            front-left encounters the edge, turn right,turn type is 1
            """
            self.action_BT(back_speed=high_spead, back_time=backing_time,
                           turn_speed=high_spead, turn_time=turn_time,
                           t_multiplier=1.5, turn_type=1,
                           hind_watcher_func=watcher)
            return True

        elif edge_fr_sensor < edge_baseline:
            """
            fl          [fr]
                O-----O
                   |
                O-----O
            rl           rr
            
            front-right encounters the edge, turn left,turn type is 0
            """
            self.action_BT(back_speed=high_spead, back_time=backing_time,
                           turn_speed=high_spead, turn_time=turn_time,
                           t_multiplier=1.5, turn_type=0,
                           hind_watcher_func=watcher)
            return True

        elif edge_rl_sensor < edge_baseline:
            """
            fl           fr
                O-----O
                   |
                O-----O
            [rl]         rr

            rear-left encounters the edge, turn right,turn type is 1
            """
            self.action_T(turn_type=1, turn_speed=high_spead, turn_time=turn_time)
            return True
        elif edge_rr_sensor < edge_baseline:
            """
            fl           fr
                O-----O
                   |
                O-----O
            rl          [rr]

            rear-right encounters the edge, turn left,turn type is 0
            """
            self.action_T(turn_type=0, turn_speed=high_spead, turn_time=turn_time)
            return True
        else:
            return False

    def check_surround(self, adc_list: list[int], baseline: int = 2000, basic_speed: int = 6000) -> bool:
        """
        checks sensors to get surrounding objects
        :param basic_speed:
        :param adc_list:
        :param baseline:
        :return: if it has encountered anything
        """
        self.screen.ADC_Led_SetColor(0, self.screen.COLOR_RED)
        if self.tag_id == self.ally_tag and adc_list[4] > baseline:
            self.on_ally_box(basic_speed, 0.3)
            return True
        elif self.tag_id == self.enemy_tag and adc_list[4] > baseline:
            self.on_enemy_box(basic_speed, 0.4)
            return True
        elif adc_list[4] > baseline:
            self.on_enemy_car(basic_speed, 0.5)
            return True
        elif adc_list[8] > baseline:
            self.on_thing_surrounding(0)
            return True
        elif adc_list[7] > baseline:
            self.on_thing_surrounding(1)
            return True
        elif adc_list[5] > baseline:
            self.on_thing_surrounding(2)
            return True
        else:
            self.screen.ADC_Led_SetColor(0, self.screen.COLOR_GREEN)
            return False

    def Battle(self, interval: int = 10, normal_spead: int = 3000):
        """
        the main function
        :param interval:
        :param normal_spead:
        :return:
        """
        print('>>>>BATTLE STARTS<<<<')

        def detector() -> bool:
            baseline = 1000
            temp = self.controller.adc_all_channels
            ftr_sensor = temp[6]
            rb_sensor = temp[5]
            fb_sensor = temp[4]
            l2_sensor = temp[8]
            r2_sensor = temp[7]
            if ftr_sensor > baseline and l2_sensor < baseline and r2_sensor < baseline and rb_sensor > baseline and fb_sensor > baseline:
                return True
            return False

        try:
            # wait for the battle starts
            self.wait_start(baseline=1800, with_turn=False, dash_speed=-6000)
            while True:
                on_stage = True
                if on_stage:
                    # update the sensors data
                    # TODO: these two functions could be combined
                    adc_list = self.controller.adc_all_channels
                    io_list = self.controller.io_all_channels

                    if self.get_away_from_edge(adc_list, io_list, edge_baseline=1650, edge_speed_multiplier=0.6):
                        # normal behave includes all edge encounter solution
                        # if encounters edge,must deal with it first
                        # should update the sensor data too ,since much time passed out
                        adc_list = self.controller.adc_all_channels

                    if self.check_surround(adc_list):
                        # if no edge is encountered then check if there are anything surrounding
                        # will check surrounding and will act according the case to deal with it
                        # after turning should go to next loop checking the object
                        continue
                    # if no edge is encountered and nothing surrounding, then just keep moving up
                    self.controller.move_cmd(normal_spead, normal_spead)
                    # loop delay,this is to prevent sending too many cmds to driver causing jam
                    self.screen.ADC_Led_SetColor(0, self.screen.COLOR_YELLOW)
                    delay_ms(interval)
                else:
                    delay_ms(interval)
                    self.checking_stage_direction(detector=detector, with_dash=True, spinning_speed=1300)
                    delay_ms(5000)


        except KeyboardInterrupt:
            # forced stop
            self.screen.ADC_Led_SetColor(0, self.screen.COLOR_WHITE)
            self.controller.move_cmd(0, 0)
            print('exiting')

    def test_run(self):
        print('test')
        self.controller.move_cmd(2000, 2000)
        delay_ms(300)
        self.controller.move_cmd(0, 0)
        baseline = 1900
        while True:
            delay_ms(100)
            temp = self.controller.adc_all_channels
            ftr_sensor = temp[1]
            rb_sensor = temp[5]
            fb_sensor = temp[4]
            l2_sensor = temp[8]
            r2_sensor = temp[7]
            if l2_sensor > baseline:
                print('Left_encounter')
                self.on_attacked(0)
            elif r2_sensor > baseline:
                print('right_encounter')
                self.on_attacked(1)
            elif rb_sensor > baseline:
                print('rear_encounter')
                self.on_attacked(2)


if __name__ == '__main__':
    bot = BattleBot()
    bot.controller.move_cmd(0, 0)
    # breakpoint()
    bot.Battle(interval=3, normal_spead=3500)
    # bot.test_run()
