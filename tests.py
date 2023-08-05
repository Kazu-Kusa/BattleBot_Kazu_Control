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

if __name__ == '__main__':
    unittest.main()
