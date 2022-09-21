import math
from uptench_star.uptech import UpTech

class BattleBot(UpTech):
    def __init__(self):
        super().__init__()
        self.current_player = None
        self.current_player_name = None

    def