from typing import final, Optional

from modules.AbsSurroundInferrer import AbstractSurroundInferrer
from repo.uptechStar.module.actions import new_ActionFrame, ActionPlayer
from repo.uptechStar.module.algrithm_tools import random_sign, enlarge_multiplier_ll, float_multiplier_middle, \
    enlarge_multiplier_l, float_multiplier_upper, shrink_multiplier_ll
from repo.uptechStar.module.inferrer_base import ComplexAction
from repo.uptechStar.module.sensors import SensorHub
from repo.uptechStar.module.tagdetector import TagDetector
from repo.uptechStar.module.watcher import default_edge_rear_watcher, default_edge_front_watcher, Watcher


# TODO: use the newly developed action frame insert play to imp this class
class StandardSurroundInferrer(AbstractSurroundInferrer):

    # region Methods
    def on_objects_encountered_at_left_right_behind(self, basic_speed) -> ComplexAction:
        # 在左右后方遇到物体，我希望更快的前进
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_upper(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame()
                ]

    def on_objects_encountered_at_right_behind(self, basic_speed) -> ComplexAction:
        # 在右方后方遇到物体，我希望差速左前进（有中断）
        return [new_ActionFrame(action_speed=(basic_speed, basic_speed * enlarge_multiplier_l()),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                ]

    def on_neutral_box_encountered_at_front_with_left_object(self, basic_speed) -> ComplexAction:
        # 在前遇到中立箱子，左方有物体，希望更快地前进,有中断
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_upper(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame()
                ]

    def on_neutral_box_encountered_at_front_with_right_object(self, basic_speed) -> ComplexAction:
        # 在前遇到中立箱子，右方有物体，希望更快地前进,有中断
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_upper(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame()
                ]

    def on_neutral_box_encountered_at_front_with_behind_object(self, basic_speed) -> ComplexAction:
        # 在前遇到中立箱子，后方有物品，我希望先左转或右转后,后退（有中断）
        single = random_sign()
        return [new_ActionFrame(action_speed=(single * basic_speed, -single * basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame()
                ]

    def on_neutral_box_encountered_at_front_with_left_right_objects(self, basic_speed) -> ComplexAction:
        # 在前遇到中立箱子，左右方有物体，希望更快地前进,有中断
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_upper(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame()
                ]

    def on_neutral_box_encountered_at_front_with_left_behind_objects(self, basic_speed) -> ComplexAction:
        # 在前遇到中立箱子，左方后方有物体，希望左转后进行后退(有中断)
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY), ),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame()
                ]

    def on_neutral_box_encountered_at_front_with_right_behind_objects(self, basic_speed) -> ComplexAction:
        # 在前遇到中立箱子，右方后方有物体，希望右转后进行后退(有中断)
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame()
                ]

    def on_neutral_box_encountered_at_front_with_left_right_behind_objects(self, basic_speed) -> ComplexAction:
        # 在前遇到中立箱子，左右方后方有物体，希望前进(有中断)后，左或右转后，进行后退(有中断)
        single = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-single * basic_speed, single * basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame()
                ]

    def on_ally_box_encountered_at_front_with_left_object(self, basic_speed) -> ComplexAction:
        # 在前遇到友方箱子，左方有物体，希望进行差速左后退（有中断）（防止长时间检测到友方的箱子）
        return [new_ActionFrame(action_speed=(-basic_speed * enlarge_multiplier_l(), -basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                ]

    def on_ally_box_encountered_at_front_with_right_object(self, basic_speed) -> ComplexAction:
        # 在前遇到友方箱子，右方有物体，希望进行差速右后退（有中断）
        return [new_ActionFrame(action_speed=(-basic_speed, -basic_speed * enlarge_multiplier_l()),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                ]

    def on_ally_box_encountered_at_front_with_behind_object(self, basic_speed) -> ComplexAction:
        # 在前遇到友方箱子，后方有物品，我希望前右轮锁死，其余轮子后退（有中断）
        return [new_ActionFrame(action_speed=(-basic_speed, -basic_speed, -basic_speed, 0),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                ]

    def on_ally_box_encountered_at_front_with_left_right_object(self, basic_speed) -> ComplexAction:
        # 在前遇到友方箱子，左右方有物体，希望更快地后退(有中断)后，进行左右转（防止长时间检测到友方的箱子）
        single = random_sign()
        return [new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-single * basic_speed, single * basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()
                ]

    def on_ally_box_encountered_at_front_with_left_behind_object(self, basic_speed) -> ComplexAction:
        # 在前遇到友方箱子，左方后方有物体，我希望前右轮锁死，其余轮子后退（有中断）
        return [new_ActionFrame(action_speed=(-basic_speed, -basic_speed, -basic_speed, 0),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                ]

    def on_ally_box_encountered_at_front_with_right_behind_object(self, basic_speed) -> ComplexAction:
        # 在前遇到友方箱子，右方后方有物体，我希望前左轮锁死，其余轮子后退（有中断）
        return [new_ActionFrame(action_speed=(0, -basic_speed, -basic_speed, -basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                ]

    def on_ally_box_encountered_at_front_with_left_right_behind_object(self, basic_speed) -> ComplexAction:
        # 在前遇到友方箱子，左方右方后方有物体，我认为后面是箱子的可能性更大，是敌方车辆的可能性很小，所有我希望直接后退
        return [new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame()
                ]

    def on_enemy_box_encountered_at_front_with_left_object(self, basic_speed) -> ComplexAction:
        # 在前遇到敌方箱子，左方有物体，希望前进(有中断)
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame()]

    def on_enemy_box_encountered_at_front_with_right_object(self, basic_speed) -> ComplexAction:
        # 在前遇到敌方箱子，右方有物体，希望前进(有中断)
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame()]

    def on_enemy_box_encountered_at_front_with_behind_object(self, basic_speed) -> ComplexAction:
        # 在前遇到敌方箱子，后方有物品，我希望左转或右转后,后退（有中断）
        single = random_sign()
        return [new_ActionFrame(action_speed=(single * basic_speed, -single * basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame()
                ]

    def on_enemy_box_encountered_at_front_with_left_right_object(self, basic_speed) -> ComplexAction:
        # 在前遇到敌方箱子，左方右方有物体，希望进行后退(有中断)
        return [new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                ]

    def on_enemy_box_encountered_at_front_with_left_behind_object(self, basic_speed) -> ComplexAction:
        # 在前遇到敌方箱子，左方后方有物体，我希望前进(有中断)后，左转后，进行后退(有中断)
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame()
                ]

    def on_enemy_box_encountered_at_front_with_right_behind_object(self, basic_speed) -> ComplexAction:
        # 在前遇到敌方箱子，右方后方有物体，我希望前进(有中断)后，右转后，进行后退(有中断)
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame()
                ]

    def on_enemy_box_encountered_at_front_with_left_right_behind_object(self, basic_speed) -> ComplexAction:
        # 在前遇到敌方箱子，左方右方后方有物体，太危险了，我们选择贪分，直接前进（有中断)，然后交给边缘，（强袭直接上它丫的啊）
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame()
                ]

    def on_objects_encountered_at_left_behind(self, basic_speed) -> ComplexAction:
        """
        will turn right and move forward, then turn back to observe the objects,
        will exit the chain action on encountering the edge when moving forward
        :param basic_speed:
        """

        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=float_multiplier_upper(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration_multiplier=enlarge_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher,
                                break_action=(new_ActionFrame(),)),
                # in the default, break action overrides frames below
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration_multiplier=enlarge_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_objects_encountered_at_left_right(self, basic_speed) -> ComplexAction:
        """
        this action will fall back first and then randomly turn left or right
        :param basic_speed: The basic speed of the robot.
        """
        sign = random_sign()
        return [new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher,
                                break_action=(new_ActionFrame(),)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=float_multiplier_upper(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_neutral_box_encountered_at_front(self, basic_speed) -> ComplexAction:
        """
        similar to enemy car reaction, but with lower speed multiplier
        """
        # TODO: use break action to improve performance
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_nothing(self, basic_speed) -> ComplexAction:
        return []

    def on_enemy_car_encountered_at_front_with_left_object(self, basic_speed) -> ComplexAction:
        # 当前面有车左边有障碍物时，撞下对面的车然后后退至安全位置
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame()]

    def on_enemy_car_encountered_at_front_with_right_object(self, basic_speed) -> ComplexAction:
        # 当前面有车右边有障碍物时，撞下对面的车然后后退至安全位置
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame()]

    def on_enemy_car_encountered_at_front_with_behind_object(self, basic_speed) -> ComplexAction:
        # 当前面有车后边有障碍物时，撞下对面的车然后随机转向至后对边缘
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()
                ]

    def on_enemy_car_encountered_at_front_with_left_right_object(self, basic_speed) -> ComplexAction:
        # 当前面有车左右有障碍物时，撞下对面的车然后后退至安全位置
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame()]

    def on_enemy_car_encountered_at_front_with_left_behind_object(self, basic_speed) -> ComplexAction:
        # 当前面有车左后有障碍物时，撞下对面的车然后右转，再前进至安全位置

        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(basic_speed, - basic_speed),
                                action_speed_multiplier=shrink_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame()]

    def on_enemy_car_encountered_at_front_with_right_behind_object(self, basic_speed) -> ComplexAction:
        # 当前面有车右后有障碍物时，撞下对面的车然后左转，再前进至安全位置

        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=shrink_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame()]

    def on_enemy_car_encountered_at_front_with_left_right_behind_object(self, basic_speed) -> ComplexAction:
        # 当前面有车左右后有障碍物时，撞下对面的车然后随机转向，再前进至安全位置
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=shrink_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame()]

    # endregion

    CONFIG_MOTION_KEY = 'MotionSection'
    CONFIG_BASIC_DURATION_KEY = f'{CONFIG_MOTION_KEY}/BasicDuration'
    CONFIG_BASIC_SPEED_KEY = f'{CONFIG_MOTION_KEY}/BasicSpeed'
    CONFIG_DASH_TIMEOUT_KEY = f'{CONFIG_MOTION_KEY}/DashTimeout'

    CONFIG_INFER_KEY = 'InferSection'
    CONFIG_FRONT_OBJECT_TABLE_KEY = f'{CONFIG_INFER_KEY}/FrontObjectTable'
    CONFIG_SENSOR_IDS_KEY = f'{CONFIG_INFER_KEY}/SensorIds'
    CONFIG_MIN_BASELINES_KEY = f'{CONFIG_INFER_KEY}/MinBaselines'
    CONFIG_MAX_BASELINES_KEY = f'{CONFIG_INFER_KEY}/MaxBaselines'

    def react(self) -> int:
        status_code = self.infer()
        self.exc_action(self.action_table.get(status_code),
                        getattr(self, self.CONFIG_BASIC_SPEED_KEY))
        # fixme deal with this status code problem
        return status_code

    def infer(self) -> int:
        """
        Infer the status code of the robot.

        Returns:

        Note:
            This function is imp by the local function
        """
        return self._status_infer()

    @final
    def register_all_config(self):
        self.register_config(config_registry_path=self.CONFIG_BASIC_DURATION_KEY,
                             value=400)
        self.register_config(config_registry_path=self.CONFIG_BASIC_SPEED_KEY,
                             value=5000)
        self.register_config(config_registry_path=self.CONFIG_DASH_TIMEOUT_KEY,
                             value=6000)

        self.register_config(config_registry_path=self.CONFIG_FRONT_OBJECT_TABLE_KEY,
                             value={[-1, True]: 400, [-1, False]: 0,
                                    [1, True]: 100, [1, False]: 100,
                                    [2, True]: 300, [2, False]: 300,
                                    [3, True]: 200, [3, False]: 200})
        # the inferring currently only support four sensors;
        # each in the list is corresponding to [front,behind,left,right]
        self.register_config(config_registry_path=self.CONFIG_SENSOR_IDS_KEY,
                             value=[3, 5, 8, 0])
        self.register_config(config_registry_path=self.CONFIG_MIN_BASELINES_KEY,
                             value=[1300] * 4)
        self.register_config(config_registry_path=self.CONFIG_MAX_BASELINES_KEY,
                             value=[1900] * 4)

    def __init__(self, sensor_hub: SensorHub, action_player: ActionPlayer, config_path: str,
                 tag_detector: Optional[TagDetector]):
        super().__init__(sensor_hub=sensor_hub, player=action_player, config_path=config_path)
        self._tag_detector = tag_detector

        self._rear_watcher: Watcher = default_edge_rear_watcher
        self._front_watcher: Watcher = default_edge_front_watcher
        self._status_infer = self._make_infer_body()

    def _make_infer_body(self):
        """
        make an infer_body with all variables bound locally, which can bring a better performance
        Returns:

        """
        tag_detector = self._tag_detector
        sensor_ids = getattr(self, self.CONFIG_SENSOR_IDS_KEY)
        behind_left_right_weights = (
            getattr(self, self.KEY_BEHIND_OBJECT),
            getattr(self, self.KEY_LEFT_OBJECT),
            getattr(self, self.KEY_RIGHT_OBJECT)
        )
        min_baselines = getattr(self, self.CONFIG_MIN_BASELINES_KEY)
        max_baselines = getattr(self, self.CONFIG_MAX_BASELINES_KEY)
        front_object_table = getattr(self, self.CONFIG_FRONT_OBJECT_TABLE_KEY)
        updater = self._sensors.on_board_adc_updater[0]

        def status_infer() -> int:
            """

            Returns: the status code of surroundings.

            """
            updated_data = updater()  # use updater to get updated sensor data
            status_bools = tuple(
                min_baseline < updated_data[sensor_id] < max_baseline for min_baseline, sensor_id, max_baseline in
                zip(min_baselines, sensor_ids, max_baselines))  # calc for the three-direction status,behind,left,right
            # calc for the surrounding status code except front
            left_right_behind_status = sum(x * y for x, y in zip(status_bools[1:], behind_left_right_weights))
            # use front sensors and tag to search the corresponding status code
            front_object_status = front_object_table.get([tag_detector.tag_id, status_bools[0]])
            # TODO: should add a tag-follow feature, because the tag may not be at the very front of the robot.
            return left_right_behind_status + front_object_status

        return status_infer

    @final
    def on_allay_box_encountered_at_front(self, basic_speed: int) -> ComplexAction:
        sign = random_sign()
        return [new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_enemy_box_encountered_at_front(self, basic_speed: int) -> ComplexAction:
        sign = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_enemy_car_encountered_at_front(self, basic_speed: int) -> ComplexAction:
        # TODO: dash til the edge, then fall back,should add a block skill(?)
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                                breaker_func=self._front_watcher),
                new_ActionFrame(),
                new_ActionFrame(action_speed=-basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                                breaker_func=self._rear_watcher),
                new_ActionFrame()]

    @final
    def on_object_encountered_at_left(self, basic_speed: int) -> ComplexAction:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_object_encountered_at_right(self, basic_speed: int) -> ComplexAction:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    @final
    def on_object_encountered_at_behind(self, basic_speed: int) -> ComplexAction:
        sign = random_sign()
        return [new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]
