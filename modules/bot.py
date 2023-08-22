from abc import ABCMeta, abstractmethod
from typing import final

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

    CONFIG_I2C_EXPANSION_SENSORS_KEY = f'{CONFIG_DEVICE_KEY}/I2CExpansionSensors'
    CONFIG_I2C_EXPANSION_SENSORS_SCL_PIN_KEY = f'{CONFIG_I2C_EXPANSION_SENSORS_KEY}/SCLPin'
    CONFIG_I2C_EXPANSION_SENSORS_SDA_PIN_KEY = f'{CONFIG_I2C_EXPANSION_SENSORS_KEY}/SDAPin'
    CONFIG_I2C_EXPANSION_SENSORS_SPEED_KEY = f'{CONFIG_I2C_EXPANSION_SENSORS_KEY}/Speed'
    CONFIG_I2C_EXPANSION_SENSORS_TARGET_ADDR_KEY = f'{CONFIG_I2C_EXPANSION_SENSORS_KEY}/TargetAddr'
    CONFIG_I2C_EXPANSION_SENSORS_REGISTER_ADDR_KEY = f'{CONFIG_I2C_EXPANSION_SENSORS_KEY}/RegisterAddr'

    CONFIG_MOTION_KEY = 'MotionSection'
    CONFIG_MOTION_START_SPEED_KEY = f'{CONFIG_MOTION_KEY}/StartSpeed'
    CONFIG_MOTION_START_DURATION_KEY = f'{CONFIG_MOTION_KEY}/StartDuration'

    @final
    def register_all_config(self):
        self.register_config(self.CONFIG_DEVICE_SCREEN_INIT_KEY, False)
        self.register_config(self.CONFIG_DEVICE_DETECTOR_CAMERA_ID_KEY, 0)
        self.register_config(self.CONFIG_DEVICE_DETECTOR_CAMERA_RESOLUTION_MULTIPLIER_KEY, 0.4)
        self.register_config(self.CONFIG_DEVICE_DETECTOR_START_DETECT_TAG_KEY, False)

        self.register_config(self.CONFIG_ONBOARD_SENSORS_DEBUG_KEY, False)

        self.register_config(self.CONFIG_I2C_EXPANSION_SENSORS_SCL_PIN_KEY, 6)
        self.register_config(self.CONFIG_I2C_EXPANSION_SENSORS_SDA_PIN_KEY, 7)
        self.register_config(self.CONFIG_I2C_EXPANSION_SENSORS_SPEED_KEY, 100)
        self.register_config(self.CONFIG_I2C_EXPANSION_SENSORS_TARGET_ADDR_KEY, 0x24)
        self.register_config(self.CONFIG_I2C_EXPANSION_SENSORS_REGISTER_ADDR_KEY, 0x10)

        self.register_config(self.CONFIG_MOTION_START_SPEED_KEY, 7000)
        self.register_config(self.CONFIG_MOTION_START_DURATION_KEY, 600)
        self.register_all_children_config()

    def __init__(self, config_path: str):
        super().__init__(config_path=config_path)
        self.screen = Screen(init_screen=getattr(self, self.CONFIG_DEVICE_SCREEN_INIT_KEY))
        if not BLIND_MODE:
            self.camera = Camera(device_id=getattr(self, self.CONFIG_DEVICE_DETECTOR_CAMERA_ID_KEY))

            self.tag_detector = TagDetector(camera=self.camera,
                                            start_detect_tag=getattr(self,
                                                                     self.CONFIG_DEVICE_DETECTOR_START_DETECT_TAG_KEY))
            self.camera.set_cam_resolution(
                resolution_multiplier=getattr(self, self.CONFIG_DEVICE_DETECTOR_CAMERA_RESOLUTION_MULTIPLIER_KEY))
        self.player = ActionPlayer()
        __on_board_sensors = OnBoardSensors(debug=getattr(self, self.CONFIG_ONBOARD_SENSORS_DEBUG_KEY))
        __i2c_expansion_sensors = SensorI2CExpansion(
            SCL_PIN=getattr(self, self.CONFIG_I2C_EXPANSION_SENSORS_SCL_PIN_KEY),
            SDA_PIN=getattr(self, self.CONFIG_I2C_EXPANSION_SENSORS_SDA_PIN_KEY),
            speed=getattr(self, self.CONFIG_I2C_EXPANSION_SENSORS_SPEED_KEY),
            expansion_device_addr=getattr(self, self.CONFIG_I2C_EXPANSION_SENSORS_TARGET_ADDR_KEY),
            register_addr=getattr(self, self.CONFIG_I2C_EXPANSION_SENSORS_REGISTER_ADDR_KEY),
            indexed_setter=__on_board_sensors.set_io_level,
            indexed_getter=__on_board_sensors.get_io_level,
            indexed_mode_setter=__on_board_sensors.set_io_mode
        )
        self.sensor_hub = SensorHub(on_board_adc_updater=(__on_board_sensors.adc_all_channels, None),
                                    on_board_io_updater=(
                                        __on_board_sensors.io_all_channels, __on_board_sensors.get_io_level),
                                    expansion_adc_updater=(None, __i2c_expansion_sensors.get_sensor_adc),
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
