from abc import ABCMeta, abstractmethod
from typing import final

from repo.uptechStar.module.actions import ActionPlayer
from repo.uptechStar.module.onboardsensors import OnBoardSensors
from repo.uptechStar.module.os_tools import Configurable
from repo.uptechStar.module.screen import Screen
from repo.uptechStar.module.sensors import SensorHub

BLIND_MODE = False
try:
    from repo.uptechStar.module.camra import Camera
    from repo.uptechStar.module.tagdetector import TagDetector, BLUE_TEAM
except ModuleNotFoundError:
    BLIND_MODE = True


class Bot(Configurable, metaclass=ABCMeta):
    """
    this class provides a way to build a key-value-based robot reacting system
    """
    CONFIG_DEVICE_KEY = 'Device'
    CONFIG_DEVICE_SCREEN_KEY = f'{CONFIG_DEVICE_KEY}/Screen'
    CONFIG_DEVICE_SCREEN_INIT_KEY = f'{CONFIG_DEVICE_SCREEN_KEY}/Init'

    CONFIG_DEVICE_DETECTOR_KEY = f'{CONFIG_DEVICE_KEY}/Detector'
    CONFIG_DEVICE_DETECTOR_CAMERA_ID_KEY = f'{CONFIG_DEVICE_DETECTOR_KEY}/CameraId'
    CONFIG_DEVICE_DETECTOR_CAMERA_RESOLUTION_MULTIPLIER_KEY = f'{CONFIG_DEVICE_DETECTOR_KEY}/CameraResolutionMultiplier'
    CONFIG_DEVICE_DETECTOR_START_DETECT_TAG_KEY = f'{CONFIG_DEVICE_DETECTOR_KEY}/StartDetectTag'

    CONFIG_ONBOARD_SENSORS_KEY = f'{CONFIG_DEVICE_KEY}/OnBoardSensors'
    CONFIG_ONBOARD_SENSORS_DEBUG_KEY = f'{CONFIG_ONBOARD_SENSORS_KEY}/Debug'

    CONFIG_MOTION_KEY = 'MotionSection'
    CONFIG_MOTION_START_SPEED_KEY = f'{CONFIG_MOTION_KEY}/StartSpeed'
    CONFIG_MOTION_START_DURATION_KEY = f'{CONFIG_MOTION_KEY}/StartDuration'

    CONFIG_MISC_KEY = 'MiscSection'
    CONFIG_MISC_TEAM_COLOR_KEY = f'{CONFIG_MISC_KEY}/TeamColor'

    @final
    def register_all_config(self):
        self.register_config(self.CONFIG_DEVICE_SCREEN_INIT_KEY, False)
        self.register_config(self.CONFIG_DEVICE_DETECTOR_CAMERA_ID_KEY, 0)
        self.register_config(self.CONFIG_DEVICE_DETECTOR_CAMERA_RESOLUTION_MULTIPLIER_KEY, 0.4)
        self.register_config(self.CONFIG_DEVICE_DETECTOR_START_DETECT_TAG_KEY, False)

        self.register_config(self.CONFIG_ONBOARD_SENSORS_DEBUG_KEY, False)

        self.register_config(self.CONFIG_MOTION_START_SPEED_KEY, 7000)
        self.register_config(self.CONFIG_MOTION_START_DURATION_KEY, 600)

        self.register_config(self.CONFIG_MISC_TEAM_COLOR_KEY, BLUE_TEAM)
        self.register_all_children_config()

    def __init__(self, config_path: str):
        super().__init__(config_path=config_path)
        self.screen = Screen(init_screen=getattr(self, self.CONFIG_DEVICE_SCREEN_INIT_KEY))
        if not BLIND_MODE:
            self.tag_detector = TagDetector(cam_id=getattr(self, self.CONFIG_DEVICE_DETECTOR_CAMERA_ID_KEY),
                                            start_detect_tag=getattr(self,
                                                                     self.CONFIG_DEVICE_DETECTOR_START_DETECT_TAG_KEY),
                                            team_color=getattr(self, self.CONFIG_MISC_TEAM_COLOR_KEY))

        self.player = ActionPlayer()
        __on_board_sensors = OnBoardSensors(debug=getattr(self, self.CONFIG_ONBOARD_SENSORS_DEBUG_KEY))
        self.sensor_hub = SensorHub(on_board_adc_updater=(__on_board_sensors.adc_all_channels, None),
                                    on_board_io_updater=(
                                        __on_board_sensors.io_all_channels, __on_board_sensors.get_io_level),
                                    expansion_adc_updater=(None, None),
                                    expansion_io_updater=(None, None))

    @abstractmethod
    def register_all_children_config(self):
        """
        Register all children configs
        Returns:
        """

    @abstractmethod
    def Battle(self) -> None:
        """
        the main function
        Args:

        """
        pass

    @abstractmethod
    def wait_start(self) -> None:
        """
        hold still util the start signal is received
        Returns: None

        """

    @abstractmethod
    def interrupt_handler(self) -> None:
        """
        used to handle the KeyboardInterrupt
        Returns: None
        """

    @final
    def start_match(self) -> None:

        self.wait_start()
        try:
            self.Battle()
        except KeyboardInterrupt:
            self.interrupt_handler()
