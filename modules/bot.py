from abc import ABCMeta, abstractmethod

from repo.uptechStar.module.actions import ActionPlayer
from repo.uptechStar.module.i2c import SensorI2CExpansion
from repo.uptechStar.module.onboardsensors import OnBoardSensors
from repo.uptechStar.module.os_tools import Configurable
from repo.uptechStar.module.screen import Screen
from repo.uptechStar.module.sensors import SensorHub

BLIND_MODE = False
try:
    from repo.uptechStar.module.camra import Camera
    from repo.uptechStar.module.tagdetector import TagDetector
except ModuleNotFoundError:
    BLIND_MODE = True


class Bot(Configurable, metaclass=ABCMeta):
    screen = Screen(init_screen=False)
    if not BLIND_MODE:
        camera = Camera(device_id=0)
        # TODO constant must be defined as named constants or something in the config file
        tag_detector = TagDetector(camera=camera, start_detect_tag=False)
    # TODO: do remember add the port to the config file
    player = ActionPlayer()
    __on_board_sensors = OnBoardSensors(debug=False)
    __i2c_expansion_sensors = SensorI2CExpansion(
        SCL_PIN=6, SDA_PIN=7, speed=100,
        indexed_setter=__on_board_sensors.set_io_level,
        indexed_getter=__on_board_sensors.get_io_level,
        indexed_mode_setter=__on_board_sensors.set_io_mode
    )
    sensor_hub = SensorHub(on_board_adc_updater=__on_board_sensors.adc_all_channels,
                           on_board_io_updater=__on_board_sensors.io_all_channels,
                           expansion_adc_updater=__i2c_expansion_sensors.get_all_sensor)

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
