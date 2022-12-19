from uptench_star.uptech import UpTech
from uptench_star.up_controller import UpController
from uptench_star.uptech import UpTech


class BattleBot(UpTech, UpController, apriltag_detect_improved):
    def __init__(self):
        super().__init__()
        self.current_player = None
        self.current_player_name = None

    def run(self):
        pass

    def get_enemy_position(self) -> int:
        pass

    def get_cur_position(self):
        pass
    def motion(self,motionCode:int):
        pass
    def