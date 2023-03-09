from repo.uptechStar.up_controller import UpController
from typing import Optional, Union


class BattleBot:
    controller = UpController()

    def __init__(self, config_path: str = './config.json'):
        self.load_config(config_path=config_path)

    def load_config(self, config_path: str):
        """
        load configuration form json
        :param config_path:
        :return:
        """

        pass

    def check_sensors(self):
        """
        sensors function check
        :return:
        """
        pass

    def on_stage_check(self, using_dst_assistance: bool = True):
        """
        check if the bot is on the stage
        :param using_dst_assistance:
        :return:
        """

    def load_models(self, model_path: str):
        """
        load vision model to memory
        :param model_path:
        :return:
        """
        pass

    def open_camera(self):
        """

        :return:
        """

    def Battle(self):
        """
        the main function of the BattleBot
        :return:
        """
        print('battle starts')
        pass


if __name__ == '__main__':
    bot = BattleBot()
    bot.Battle()
