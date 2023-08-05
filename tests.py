import unittest
from modules.EdgeInferrers import StandardEdgeInferrer
from modules.FenceInferrers import StandardFenceInferrer
from modules.SurroundInferrers import StandardSurroundInferrer
from repo.uptechStar.module.actions import ActionFrame, ActionPlayer
from repo.uptechStar.module.sensors import SensorHub
from repo.uptechStar.module.serial_helper import find_serial_ports
from repo.uptechStar.module.close_loop_controller import motor_speed_test, CloseLoopController

EMPTY_JSON = 'config/empty.json'


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


class Sensor_test(unittest.TestCase):

    def test_sensor_record(self):
        from repo.uptechStar.module.uptech import UpTech
        from repo.uptechStar.module.sensors import record_updater
        a = UpTech()
        recoded = record_updater(updater=a.atti_all, duration=10000, interval=2)
        recoded.to_csv('test.csv')

        pad = Screen()
        pad.set_font_size(pad.FONT_12X16)
        pad.put_string(0, 0, "Screen Test")


# import ctypes
# a = ctypes.cdll.LoadLibrary('./libuptech.so')

class SensorTest(unittest.TestCase):

    def test_sensor_record(self):
        from repo.uptechStar.module.uptech import UpTech
        from repo.uptechStar.module.sensors import record_updater
        a = UpTech()

        MPU_recoded = record_updater(updater=a.atti_all, duration=10000, interval=2)
        for k, v in MPU_recoded.items():
            print(k, len(v))

        ADC_recoded = record_updater(updater=a.adc_all_channels, duration=10000, interval=2)

        for k, v in ADC_recoded.items():
            print(k, len(v))
            for i in v:
                print(i)


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


if __name__ == '__main__':
    unittest.main()
