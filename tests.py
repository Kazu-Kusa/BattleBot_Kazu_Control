import unittest
from modules.EdgeInferrers import StandardEdgeInferrer
from repo.uptechStar.module.actions import ActionFrame, ActionPlayer
from repo.uptechStar.module.sensors import SensorHub


class MyTestCase(unittest.TestCase):

    def test_something(self):
        a = StandardEdgeInferrer(action_player=ActionPlayer(), sensor_hub=SensorHub(updaters=[]),
                                 config_path='config/empty.json')
        print(a)


if __name__ == '__main__':
    unittest.main()
