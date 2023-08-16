import re
import unittest
import warnings
from typing import List, Dict

from modules.EdgeInferrers import StandardEdgeInferrer
from modules.FenceInferrers import StandardFenceInferrer
from modules.SurroundInferrers import StandardSurroundInferrer
from repo.uptechStar.module.actions import ActionPlayer
from repo.uptechStar.module.close_loop_controller import motor_speed_test
from repo.uptechStar.module.sensors import SensorHub
from repo.uptechStar.module.serial_helper import find_serial_ports

EMPTY_JSON = 'config/empty.json'
import time
import json

from repo.uptechStar.module.onboardsensors import OnBoardSensors
from repo.uptechStar.module.sensors import record_updater
from repo.uptechStar.module.screen import Screen
import numpy as np

# 原始列表
try:
    a = OnBoardSensors()
    screen = Screen()
except:
    pass


def test_decode_recorded_data(json_path='./recorded.json', dedup: bool = False):
    import pandas as pd
    import json

    with open(json_path, mode='r') as f:
        data: dict = json.load(f)
    df = pd.concat({k: pd.Series(v) for k, v in data.items()}, axis=1, sort=False)

    df.to_csv(json_path.replace('.json', '.csv'), index=False)
    if dedup:
        def remove_duplicates(data_f):
            data_f = data_f.apply(lambda x: x.ne(x.shift()))
            data_f = data_f.cumsum()
            data_f = data_f[data_f.duplicated(keep='last')]
            data_f = data_f.apply(lambda x: x.ne(x.shift())).dropna()
            return data_f

        # remove duplicated values
        df = remove_duplicates(df)
        df.to_csv(json_path.replace('.json', '_dedup.csv'), index=False)


class SerialTest(unittest.TestCase):

    def test_port_serial(self):
        ports = find_serial_ports()
        print(ports)


class InferrerTests(unittest.TestCase):

    def test_StandardEdgeInferrer_create(self):
        a = StandardEdgeInferrer(action_player=ActionPlayer(), sensor_hub=SensorHub(updaters=[]),
                                 config_path=EMPTY_JSON)
        a.save_config('config/std_edge_inferrer_config.json')
        print(a)

    def test_StandardFenceInferrer_create(self):
        a = StandardFenceInferrer(action_player=ActionPlayer(), sensor_hub=SensorHub(updaters=[]),
                                  config_path=EMPTY_JSON)
        a.save_config('config/std_fence_inferrer_config.json')
        print(a)

    def test_StandardSurroundInferrer_create(self):
        a = StandardSurroundInferrer(action_player=ActionPlayer(), sensor_hub=SensorHub(updaters=[]),
                                     config_path=EMPTY_JSON)
        a.save_config('config/std_surround_inferrer_config.json')
        print(a)


class motor_test(unittest.TestCase):
    def test_motor_speed_test(self):
        motor_speed_test('COM4')


def test_sensor_record(duration=10000, interval=0):
    time.sleep(3)
    updaters = [a.atti_all, a.acc_all, a.gyro_all, a.adc_all_channels]
    result_dict = {}

    def record(updater) -> Dict[str, List]:
        screen.set_led_color(1, Screen.COLOR_RED)
        recoded = record_updater(updater=updater, duration=duration, interval=interval)
        screen.set_led_color(1, Screen.COLOR_GREEN)
        return recoded

    def formatted_save(data_chunk: Dict[str, List], save_path: str):
        temp_dict = {}
        for key, value in data_chunk.items():
            transposed: List = np.transpose(value).tolist()
            for i, row in enumerate(transposed):
                temp_dict[f'{key}-{i}'] = row
        print('saving')
        with open(save_path, mode='w+') as f:
            json.dump(temp_dict, f, indent=4)

    for updater in updaters:
        a.adc_io_open()
        result_dict.update(record(updater))
        a.adc_io_close()
        time.sleep(2)
    formatted_save(data_chunk=result_dict, save_path=f'./recorded_{duration}_{interval}.json')


class SensorTest(unittest.TestCase):

    def test_multiple_record(self, duration=10000, interval_list=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)):
        warnings.warn('###############################')
        for interval in interval_list:
            print(f'doing with {interval}')
            test_sensor_record(duration=duration, interval=interval)

    def test_decode_all_data(self):
        import os

        def find_files_with_string(search_string):
            files_with_string = []
            current_dir = os.getcwd()
            files = os.listdir(current_dir)
            for file in files:
                if search_string in file and os.path.isfile(file):
                    files_with_string.append(file)
            return files_with_string

        files_list = find_files_with_string('.json')
        print(files_list)
        for file in files_list:
            test_decode_recorded_data(json_path=file)

    def test_adc_sensor_runtime(self):
        from repo.uptechStar.module.hotConfigure.valueTest import read_sensors
        read_sensors()

    def test_io_flipping_freq(self):
        from repo.uptechStar.module.onboardsensors import OnBoardSensors
        from time import perf_counter_ns
        a = OnBoardSensors()
        ct = 0
        test_duration = 10000
        end_time = perf_counter_ns() + test_duration * 10e6
        while perf_counter_ns() < end_time:
            ct += 1
            a.set_all_io_level(ct)
        print(f'Flip counter: {ct}')


class ScreenTest(unittest.TestCase):

    def test_screen_sync(self):
        from repo.uptechStar.module.hotConfigure.sync_test import count_adds_per_second
        count_adds_per_second()

    def test_led(self):
        from repo.uptechStar.module.screen import Screen
        pad = Screen()
        pad.set_led_color(1, pad.COLOR_RED)
        # pad.set_font_size(pad.FONT_12X16)
        # pad.put_string(0, 0, "Screen Test")


class MiscTest(unittest.TestCase):
    @staticmethod
    def test_indexing_performance():
        from time import perf_counter_ns
        class Test():

            def get(self, data):
                return 0

        def get(data):
            return 0

        # 创建一个包含大量元素的列表和字典
        num_elements = 1000000
        my_list = list(range(num_elements))
        my_dict = {i: i for i in range(num_elements)}

        # 测试列表索引的性能
        start_time = perf_counter_ns()
        for i in range(num_elements):
            value = my_list[i]
        end_time = perf_counter_ns()
        list_time = end_time - start_time

        # 测试字典get方法的性能
        start_time = perf_counter_ns()
        for i in range(num_elements):
            value = my_dict.get(i)
        end_time = perf_counter_ns()
        dict_time = end_time - start_time

        a = Test()
        start_time = perf_counter_ns()
        for i in range(num_elements):
            value = a.get(i)
        end_time = perf_counter_ns()
        class_time = end_time - start_time

        start_time = perf_counter_ns()
        for i in range(num_elements):
            value = get(i)
        end_time = perf_counter_ns()
        method_time = end_time - start_time
        # 输出性能结果
        print(f"列表索引耗时: {list_time}秒")
        print(f"字典get方法耗时: {dict_time}秒")
        print(f"类方法耗时: {class_time}秒")
        print(f"方法耗时: {method_time}秒")
        print(f'比例: {dict_time / list_time}')
        print(f'比例: {class_time / list_time}')
        print(f'比例: {method_time / list_time}')

    def test_perf_counter_ns(self):
        from time import perf_counter_ns
        ct = 1000
        res = []
        for _ in range(ct):
            start = perf_counter_ns()
            ns_start = perf_counter_ns() - start
            res.append(ns_start)
            print(ns_start)
        print(sum(res) / ct)

    def test_delay_us(self):
        from time import perf_counter_ns
        from repo.uptechStar.module.timer import delay_us
        ct = 100
        res = []
        for _ in range(ct):
            start = perf_counter_ns()
            delay_us(2)
            ns_start = perf_counter_ns() - start
            res.append(ns_start)
            print(ns_start)
        print(sum(res) / ct)

    def test_calc_hang_time(self):
        from repo.uptechStar.module.timer import calc_hang_time
        b = calc_hang_time(5000, 4000)
        print(b)  # must 1.0

    def test_shadow_copy(self):
        from copy import copy
        a = [1, 2, 3]
        b = copy(a)
        b[0] = 4
        print(a, b)

    def test_list_op(self):
        a = [1, 2, 3]
        b = []
        b = a
        print(b is a)  # 输出：True，b 和 a 引用了同一个列表对象
        a.append(4)
        print(b)  # 输出：[1, 2, 3, 4]

        a = [1, 2, 3]
        b = []
        b[:] = a
        print(b is a)  # 输出：False，b 是一个新创建的列表对象
        a.append(4)
        print(b)  # 输出：[1, 2, 3]


class ConstructorsTest(unittest.TestCase):
    def test_delta_watcher_constructor(self):
        from repo.uptechStar.module.watcher import build_delta_watcher_simple
        def gen() -> list:
            i = 0
            while True:
                yield [i] * 10
                i += 10

        gener = gen()

        def sensor_update(*args, **kwargs) -> list:
            a = next(gener)
            print(a)
            return a

        print('test')
        # 创建一个 max_line 和 min_line 都存在的 watcher
        watcher1 = build_delta_watcher_simple(sensor_update, (0, 1), max_line=5, min_line=2, args=(1, 2))
        print(watcher1())  # False
        print(watcher1())  # False
        # 创建一个 max_line 和 min_line 都存在的 watcher

        # 创建一个只有 min_line 的 watcher
        watcher2 = build_delta_watcher_simple(sensor_update, (0, 1), min_line=2, args=(3, 4))
        print(watcher2())  # False
        print(watcher2())  # True

        # 创建一个只有 max_line 的 watcher
        watcher3 = build_delta_watcher_simple(sensor_update, (0, 1), max_line=5, args=(6, 7))
        print(watcher3())  # True
        print(watcher3())  # False


class ActionTest(unittest.TestCase):
    def test_af_compile(self):
        from repo.uptechStar.module.actions import pre_build_action_frame
        pre_build_action_frame(speed_range=(-10000, 10000, 5),
                               duration_range=(0, 5000, 10))


class Algrithm_tools(unittest.TestCase):

    def test_list_multiply(self):
        from repo.uptechStar.module.algrithm_tools import list_multiply
        import random
        a = [random.randint(0, 1000) for i in range(3)]
        b = [random.randint(0, 1000) for i in range(3)]
        c = list_multiply(a, b)
        d = tuple(int(a[i] * b[i]) for i in range(3))
        self.assertIsInstance(c, tuple)
        self.assertEqual(c, d)

    def test_factor_list_multiply(self):
        import random
        import numpy
        from repo.uptechStar.module.algrithm_tools import factor_list_multiply
        b_list = [random.randint(0, 1000) for i in range(10)]
        a = random.randint(0, 1000)
        b = factor_list_multiply(a, b_list)
        self.assertIsInstance(b, tuple)
        c = numpy.array(b_list) * a
        c = tuple(c)
        self.assertEqual(c, b)

    def test_multiply(self):
        from repo.uptechStar.module.algrithm_tools import multiply
        a = 3
        b = 6
        c = multiply(a, b)
        self.assertIsInstance(c, int)

    def test_random_sign(self):
        from repo.uptechStar.module.algrithm_tools import random_sign
        b = random_sign()
        self.assertIsInstance(b, int)

    def test_random_enlarge_multiplier(self):
        from repo.uptechStar.module.algrithm_tools import random_enlarge_multiplier
        b = random_enlarge_multiplier()
        self.assertIsInstance(b, float)

    def test_random_shrink_multiplier(self):
        from repo.uptechStar.module.algrithm_tools import random_shrink_multiplier
        b = random_shrink_multiplier()
        self.assertIsInstance(b, float)

    def test_random_float_multiplier(self):
        from repo.uptechStar.module.algrithm_tools import random_float_multiplier
        b = random_float_multiplier()
        self.assertIsInstance(b, float)

    def test_calc_p2p_dst(self):
        from repo.uptechStar.module.algrithm_tools import calc_p2p_dst
        import random
        a = calc_p2p_dst((random.uniform(0, 10), random.uniform(0, 10)), (random.uniform(0, 10), random.uniform(0, 10)))
        self.assertIsInstance(a, float)

    def test_calc_p2p_error(self):
        from repo.uptechStar.module.algrithm_tools import calc_p2p_error
        import random
        a = calc_p2p_error((random.uniform(0, 10), random.uniform(0, 10)),
                           (random.uniform(0, 10), random.uniform(0, 10)))
        self.assertIsInstance(a, tuple)


''' 学习注释
    numpy.array()能将数组改变为向量，进行常量*向量的乘法
    self.assertEqual(c, b)能将两者进行比较，相同则ture
    self.assertIsInstance(c, tuple)，判断前者是否是后者的类型
    tuple(int(a[i]*b[i]) for i in range(3))生成器
    
'''


# class Pid(unittest.TestCase):
#     def a_test_def(self):
#         pass
#
#     def test_PD_control(self):
#         from repo.uptechStar.module.pid import PID_control
#         import random
#         a = PID_control()


class Uptech(unittest.TestCase):
    def test_adc_io_open(self):
        a.adc_io_open()
        print(a.adc_io_open())

    def test_adc_io_close(self):
        a.adc_io_close()
        assert a.adc_io_close() is None

    def test_adc_all_channels(self):
        a.adc_all_channels()
        print([x for x in a.adc_all_channels()])

    def test_set_io_level(self):
        a.set_io_level(1, 1)
        print(a.set_io_level(1, 1))

    def test_set_all_io_level(self):
        a.set_all_io_level(1)
        print(a.set_all_io_level(1))

    def test_get_all_io_mode(self):
        a.get_all_io_mode(1)
        print(a.get_all_io_mode(1))

    def test_io_all_channels(self):
        a.io_all_channels()
        print(a.io_all_channels())

    def test_MPU6500_Open(self):
        assert a.acc_all() == -1
        assert a.atti_all() == -1
        assert a.gyro_all() == -1
        a.MPU6500_Open(False)
        print([x for x in a.acc_all()])
        print([x for x in a.atti_all()])
        print([x for x in a.gyro_all()])
        assert len([x for x in a.acc_all()]) == 3
        assert len([x for x in a.atti_all()]) == 3
        assert len([x for x in a.gyro_all()]) == 3
        print(a.MPU6500_Open())


class Tagdetector(unittest.TestCase):
    # 未完成，当前环境不支持完成该测试，cmake
    def test_get_center_tag(self):
        from repo.uptechStar.module.tagdetector import get_center_tag
        b = get_center_tag((1, 2), [3, 4])
        print(b)


class Close_loop_controller(unittest.TestCase):
    from repo.uptechStar.module.close_loop_controller import CloseLoopController

    b = CloseLoopController((0, 0, 1, 1), (1, 1, 0, 0))

    def test_motor_ids(self):
        # 测试函数motor_ids 生成元组的功能
        # 测试内容：判断生成内容是否是元组，是否为输入参数中的关键字motor_ids（b）
        print(self.b.motor_ids)
        self.assertIsInstance(self.b.motor_ids, tuple)
        self.assertEqual(self.b.motor_ids, (0, 0, 1, 1))

    def test_motor_speeds(self):
        # 测试函数motor_speeds 生成元组的功能
        # 测试内容：判断生成内容是否是元组，是否为规定的（0，0，0，0）
        print(self.b.motor_speeds)
        self.assertIsInstance(self.b.motor_speeds, tuple)
        self.assertEqual(self.b.motor_speeds, (0, 0, 0, 0))

    def test_motor_dirs(self):
        # 测试函数motor_idrs 生成元组的功能
        # 测试内容：判断生成内容是否是元组，是否为输入参数中的关键字motor_idrs（b）
        print(self.b.motor_dirs)
        self.assertIsInstance(self.b.motor_dirs, tuple)
        self.assertEqual(self.b.motor_dirs, (1, 1, 0, 0))

    def test_debug(self):
        # 测试函数debug 生成布尔值的功能
        # 测试内容：判断生成内容是否是布尔值，是否为默认参数False
        print(self.b.debug)
        self.assertIsInstance(self.b.debug, bool)
        self.assertEqual(self.b.debug, False)

    def test_stop_msg_sending(self):
        assert self.b._msg_send_thread_should_run == True
        try:
            self.b.stop_msg_sending()
        except[RuntimeError]:
            print("RuntimeError,可能是以下错误")
            print("Thread.__init__() not called")
            print("cannot join thread before it is started")
            print("cannot join current thread")
        assert self.b._msg_send_thread_should_run == False

    def test_start_msg_sending(self):
        # 包含set_motors_speed和set_all_motors_speed
        # _msg_sending_loop函数在该项测试中有体现，没有单独拿出来测试
        from repo.uptechStar.module.timer import delay_ms
        self._msg_send_thread_should_run: bool = False
        self.b.start_msg_sending()
        assert self.b._msg_send_thread_should_run == True
        for i in range(100):
            self.b.set_motors_speed((i, i, i, i), 0.1)
            delay_ms(100)
        # 10秒内小蓝灯在闪烁，则成功，通信建立成功，set_motors_speed速度传递参数成功
        for i in range(100):
            self.b.set_motors_speed((1, 1, 1, 1), 0.1)
            delay_ms(100)
        # 10秒内小蓝灯仅仅在开始时闪烁一次，则成功，set_motors_speed拦截相同指令成功
        for i in range(100):
            self.b.set_all_motors_speed(i, 0.1)
            delay_ms(100)
        # 10秒内小蓝灯在闪烁，则成功

    def test_makeCmds_dirs(self):
        # TODO: 正则表达式暂时写不出来，不用管
        c = self.b.makeCmds_dirs((2, 2, 2, 2))
        print(c)
        c = str(c)

        d = re.findall(string=c, pattern=r"\d+v\d+\\r")
        print(d)

    def test_move_cmd(self):
        self.b.move_cmd(1, 1)
        # TODO: 要开启电机才可以进行测试

    def test_open_userInput_channel(self):
        # TODO : 不好测试
        pass

    def test_is_list_all_zero(self):
        from repo.uptechStar.module.close_loop_controller import is_list_all_zero
        import random
        c = 10
        while c >= 1:
            b = [0, random.randint(0, 1), 0, random.randint(0, 1)]
            print(b)
            print(is_list_all_zero(b))
            if b[1] == 0 and b[3] == 0:
                assert is_list_all_zero(b) is True
            if b[1] == 1 and b[3] == 1:
                assert is_list_all_zero(b) is False
            c = c - 1

    def test_is_rotate_cmd(self):
        from repo.uptechStar.module.close_loop_controller import is_rotate_cmd
        import random
        c = 50
        while c >= 1:
            a1 = random.randint(-1, 1)
            a2 = random.randint(-1, 1)
            a3 = random.randint(-1, 1)
            a4 = random.randint(-1, 1)
            b = (a1, a2, a3, a4)
            print(b)
            print(is_rotate_cmd(b))
            if a1 == a2 and a3 == a4 and a1 + a3 == 0:
                assert is_rotate_cmd(b) is True
            else:
                assert is_rotate_cmd(b) is False
            c = c - 1

    def test_makeCmd_list(self):
        # TODO:  正则表达式暂时写不出来
        from repo.uptechStar.module.close_loop_controller import makeCmd_list
        a = makeCmd_list(['1', '1', '1', '1'])
        print(a)

    def test_makeCmd(self):
        # TODO: 正则表达式暂时写不出来
        from repo.uptechStar.module.close_loop_controller import makeCmd
        a = makeCmd("1")
        print(a)

    def test_motor_speed_test(self):
        from repo.uptechStar.module.close_loop_controller import motor_speed_test
        # print(find_serial_ports())
        motor_speed_test('/dev/ttyUSB0')


class I2C_test(unittest.TestCase):

    def test_bytes_to_int(self):
        from repo.uptechStar.module.i2c import join_bytes_to_uint16
        byte_array = bytearray([0b00000000, 0b01000000])
        result = join_bytes_to_uint16(byte_array)
        print(result)  # 输出 43981


if __name__ == '__main__':
    unittest.main()
