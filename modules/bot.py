from abc import ABCMeta, abstractmethod

from repo.uptechStar.module.actions import ActionPlayer
from repo.uptechStar.module.camra import Camera
from repo.uptechStar.module.db_tools import Configurable
from repo.uptechStar.module.tagdetector import TagDetector
from repo.uptechStar.module.screen import Screen
from repo.uptechStar.module.uptech import UpTech
from repo.uptechStar.module.i2c import SensorsExpansion, DEFAULT_I2C_SERIAL_KWARGS


class Bot(Configurable, metaclass=ABCMeta):
    screen = Screen(init_screen=False)
    camera = Camera(device_id=0)
    # TODO constant must be defined as named constants or something in the config file
    tag_detector = TagDetector(camera=camera, start_detect_tag=False)
    on_board_sensors = UpTech(debug=False, fan_control=False)
    i2c_expansion_sensors = SensorsExpansion(port='/dev/i2c-1', serial_config=DEFAULT_I2C_SERIAL_KWARGS)
    # TODO: do remember add the port to the config file
    player = ActionPlayer()

    def __init__(self, config_path: str = './config.json'):
        """
        :param config_path: the path to the config
        """
        super().__init__(config_path=config_path)

    @abstractmethod
    def Battle(self, normal_spead: int, team_color: str) -> None:
        """
        the main function
        :param team_color:
        :param normal_spead:
        :return:
        """
        pass
