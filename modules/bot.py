import json
from abc import ABCMeta, abstractmethod

from repo.uptechStar.module.camera import Camera
from repo.uptechStar.module.screen import Screen


class Bot(metaclass=ABCMeta):
    screen = Screen(init_screen=False)

    camera = Camera(open_camera=False)

    def __init__(self, config_path: str = './config.json'):
        """
        :param config_path: the path to the config,but it hasn't been put into use
        """
        # load the config.json file to memory
        with open(config_path, 'r') as f:
            self._config: dict = json.load(fp=f)
            f.close()

    # region utilities
    @abstractmethod
    def load_config(self):
        """
        analyze configuration form _config
        :return:
        """

        pass

    # endregion

    @abstractmethod
    def Battle(self, normal_spead):
        """
        the main function
        :param normal_spead:
        :return:
        """
        pass