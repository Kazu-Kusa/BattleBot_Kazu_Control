from abc import ABCMeta, abstractmethod

from repo.uptechStar.module.actions import ActionPlayer
from repo.uptechStar.module.camra import Camera
from repo.uptechStar.module.db_tools import Configurable
from repo.uptechStar.module.i2c import SensorsExpansion, DEFAULT_I2C_SERIAL_KWARGS
from repo.uptechStar.module.screen import Screen
from repo.uptechStar.module.sensors import SensorHub
from repo.uptechStar.module.tagdetector import TagDetector
from repo.uptechStar.module.uptech import UpTech


class Bot(Configurable, metaclass=ABCMeta):
    screen = Screen(init_screen=False)
    camera = Camera(device_id=0)
    # TODO constant must be defined as named constants or something in the config file
    tag_detector = TagDetector(camera=camera, start_detect_tag=False)
    on_board_sensors = UpTech(debug=False, fan_control=False)
    i2c_expansion_sensors = SensorsExpansion(port='/dev/i2c-1', serial_config=DEFAULT_I2C_SERIAL_KWARGS)
    # TODO: do remember add the port to the config file
    player = ActionPlayer()

    sensor_hub = SensorHub(updaters=[on_board_sensors.adc_all_channels,
                                     on_board_sensors.io_all_channels,
                                     i2c_expansion_sensors.get_all_adc_data])

    @abstractmethod
    def Battle(self, normal_spead: int, use_cam: bool, team_color: str) -> None:
        """
        the main function
        Args:

            normal_spead: the base speed during the battle
            team_color: the team color of own team
            use_cam: if you use the camera during the battle
        """
        pass
