from repo.uptechStar.module.actions import ActionPlayer, new_ActionFrame
from repo.uptechStar.module.sensors import SensorHub, FU_INDEX, IU_INDEX
from time import perf_counter_ns


class NormalActions:

    def __init__(self, player: ActionPlayer,
                 sensor_hub: SensorHub,
                 how_time: int = 6000):
        self.player = player
        self.sensor_hub = sensor_hub
        self.how_time = how_time

    def all_actions(self):
        """
        该函数是该类的主要使用函数，根据输入的时间参数，执行相应时间，在特殊情况下弹出
        :return:
        """
        quit_1 = 0
        while self.how_time > 0 and quit_1 == 0:
            how_time_1 = perf_counter_ns()
            self.waiting_cation()
            self.infer_sensors()
            self.how_time = self.how_time - (perf_counter_ns() - how_time_1)

    def waiting_cation(self):
        # 停止动作
        self.player.append(new_ActionFrame())

    def revolve_cation(self):
        # 旋转动作
        self.player.append(new_ActionFrame((100, 100, 0, 100), action_duration=50))

    def open_sensors(self):
        """
        检测周围
        :return: 返回前后左右的传感器参数，并生成一个元组
        """
        fu_updater = self.sensor_hub.on_board_adc_updater[FU_INDEX]
        sensor_data = fu_updater()
        l1 = sensor_data[8]
        r1 = sensor_data[0]
        fb = sensor_data[5]
        rb = sensor_data[3]
        return l1, r1, fb, rb

    def infer_sensors(self) -> int:
        """
        解析传感器参数，并返回对应的动作返回值
        :return: 1 是对应未检测到任何东西，执行旋转动作
        :return: 2 是对应检测到未知数量的物品，返回停止信号，
        """
        view = self.open_sensors()
        i = 100
        #
        if view[0] <= i and view[1] <= i and view[2] <= i and view[3] <= i:
            self.revolve_cation()
        else:
            quit_1 = 1
            return quit_1
