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

from repo.uptechStar.module.uptech import UpTech
from repo.uptechStar.module.sensors import record_updater
from repo.uptechStar.module.screen import Screen
import numpy as np

# 原始列表
try:
    a = UpTech()
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
        from repo.uptechStar.module.uptech import UpTech
        from time import perf_counter_ns
        a = UpTech()
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
        from repo.uptechStar.module.watcher import build_delta_watcher
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
        watcher1 = build_delta_watcher(sensor_update, (0, 1), max_line=5, min_line=2, args=(1, 2))
        print(watcher1())  # False
        print(watcher1())  # False
        # 创建一个 max_line 和 min_line 都存在的 watcher

        # 创建一个只有 min_line 的 watcher
        watcher2 = build_delta_watcher(sensor_update, (0, 1), min_line=2, args=(3, 4))
        print(watcher2())  # False
        print(watcher2())  # True

        # 创建一个只有 max_line 的 watcher
        watcher3 = build_delta_watcher(sensor_update, (0, 1), max_line=5, args=(6, 7))
        print(watcher3())  # True
        print(watcher3())  # False


class ActionTest(unittest.TestCase):
    def test_af_compile(self):
        from repo.uptechStar.module.actions import pre_build_action_frame
        pre_build_action_frame(speed_range=(-10000, 10000, 5),
                               duration_range=(0, 5000, 10))


if __name__ == '__main__':
    unittest.main()
