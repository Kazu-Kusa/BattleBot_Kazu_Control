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


if __name__ == '__main__':
    unittest.main()
