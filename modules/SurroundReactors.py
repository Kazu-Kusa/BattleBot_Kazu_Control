import warnings
from typing import final, Optional, Tuple, Dict

from modules.AbsSurroundReactor import AbstractSurroundReactor
from repo.uptechStar.module.actions import new_ActionFrame, ActionPlayer
from repo.uptechStar.module.algrithm_tools import (
    random_sign,
    enlarge_multiplier_ll,
    float_multiplier_middle,
    enlarge_multiplier_l,
    float_multiplier_upper,
    shrink_multiplier_ll,
    shrink_multiplier_l,
    float_multiplier_lower,
)
from repo.uptechStar.module.reactor_base import ComplexAction
from repo.uptechStar.module.sensors import SensorHub, FU_INDEX, IU_INDEX
from repo.uptechStar.module.tagdetector import TagDetector, BLUE_TEAM, YELLOW_TEAM
from repo.uptechStar.module.watcher import (
    Watcher,
    build_watcher_full_ctrl,
    watchers_merge,
    build_io_watcher_from_indexed,
)


class StandardSurroundReactor(AbstractSurroundReactor):

    # region Methods
    def on_objects_encountered_at_left_right_behind(self, basic_speed) -> ComplexAction:
        # 在左右后方遇到物体，我希望更快的前进
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=float_multiplier_upper(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
        ]

    def on_objects_encountered_at_right_behind(self, basic_speed) -> ComplexAction:
        # 在右方后方遇到物体，我希望差速左前进（有中断）
        return [
            new_ActionFrame(
                action_speed=(basic_speed, int(basic_speed * enlarge_multiplier_l())),
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
        ]

    def on_neutral_box_encountered_at_front_with_left_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到中立箱子，左方有物体，希望更快地前进,有中断
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=float_multiplier_upper(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(action_duration=10),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=float_multiplier_lower(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
        ]

    def on_neutral_box_encountered_at_front_with_right_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到中立箱子，右方有物体，希望更快地前进,有中断
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=float_multiplier_upper(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(action_duration=10),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=float_multiplier_lower(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
        ]

    def on_neutral_box_encountered_at_front_with_behind_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到中立箱子，后方有物品，我希望先左转或右转后,后退（有中断）
        single = random_sign()
        return [
            new_ActionFrame(
                action_speed=(single * basic_speed, -single * basic_speed),
                action_speed_multiplier=float_multiplier_lower(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_neutral_box_encountered_at_front_with_left_right_objects(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到中立箱子，左右方有物体，希望更快地前进,有中断
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=float_multiplier_upper(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
        ]

    def on_neutral_box_encountered_at_front_with_left_behind_objects(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到中立箱子，左方后方有物体，希望左转后进行后退(有中断)
        return [
            new_ActionFrame(
                action_speed=(-basic_speed, basic_speed),
                action_speed_multiplier=float_multiplier_lower(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_neutral_box_encountered_at_front_with_right_behind_objects(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到中立箱子，右方后方有物体，希望右转后进行后退(有中断)
        return [
            new_ActionFrame(
                action_speed=(basic_speed, -basic_speed),
                action_speed_multiplier=float_multiplier_lower(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_neutral_box_encountered_at_front_with_left_right_behind_objects(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到中立箱子，左右方后方有物体，希望前进(有中断)后，左或右转后，进行后退(有中断)
        single = random_sign()
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=(-single * basic_speed, single * basic_speed),
                action_speed_multiplier=float_multiplier_lower(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_ally_box_encountered_at_front_with_left_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到友方箱子，左方有物体，希望进行差速左后退（有中断）（防止长时间检测到友方的箱子）
        return [
            new_ActionFrame(
                action_speed=(int(-basic_speed * enlarge_multiplier_l()), -basic_speed),
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
        ]

    def on_ally_box_encountered_at_front_with_right_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到友方箱子，右方有物体，希望进行差速右后退（有中断）
        return [
            new_ActionFrame(
                action_speed=(-basic_speed, int(-basic_speed * enlarge_multiplier_l())),
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
        ]

    def on_ally_box_encountered_at_front_with_behind_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到友方箱子，后方有物品，我希望前右轮锁死，其余轮子后退（有中断）
        return [
            new_ActionFrame(
                action_speed=(-basic_speed, -basic_speed, -basic_speed, 0),
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
        ]

    def on_ally_box_encountered_at_front_with_left_right_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到友方箱子，左右方有物体，希望更快地后退(有中断)后，进行左右转（防止长时间检测到友方的箱子）
        single = random_sign()
        return [
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=(-single * basic_speed, single * basic_speed),
                action_speed_multiplier=float_multiplier_lower(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
        ]

    def on_ally_box_encountered_at_front_with_left_behind_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到友方箱子，左方后方有物体，我希望前右轮锁死，其余轮子后退（有中断）
        return [
            new_ActionFrame(
                action_speed=(-basic_speed, -basic_speed, -basic_speed, 0),
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
        ]

    def on_ally_box_encountered_at_front_with_right_behind_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到友方箱子，右方后方有物体，我希望前左轮锁死，其余轮子后退（有中断）
        return [
            new_ActionFrame(
                action_speed=(0, -basic_speed, -basic_speed, -basic_speed),
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
        ]

    def on_ally_box_encountered_at_front_with_left_right_behind_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到友方箱子，左方右方后方有物体，我认为后面是箱子的可能性更大，是敌方车辆的可能性很小，所有我希望直接后退
        return [
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_enemy_box_encountered_at_front_with_left_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到敌方箱子，左方有物体，希望前进(有中断)
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
        ]

    def on_enemy_box_encountered_at_front_with_right_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到敌方箱子，右方有物体，希望前进(有中断)
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(action_duration=10),
        ]

    def on_enemy_box_encountered_at_front_with_behind_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到敌方箱子，后方有物品，我希望左转或右转后,后退（有中断）
        single = random_sign()
        return [
            new_ActionFrame(
                action_speed=(single * basic_speed, -single * basic_speed),
                action_speed_multiplier=float_multiplier_lower(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_enemy_box_encountered_at_front_with_left_right_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到敌方箱子，左方右方有物体，希望进行后退(有中断)
        return [
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_enemy_box_encountered_at_front_with_left_behind_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到敌方箱子，左方后方有物体，我希望前进(有中断)后，左转后，进行后退(有中断)
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=(-basic_speed, basic_speed),
                action_speed_multiplier=float_multiplier_lower(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_enemy_box_encountered_at_front_with_right_behind_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到敌方箱子，右方后方有物体，我希望前进(有中断)后，右转后，进行后退(有中断)
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=(basic_speed, -basic_speed),
                action_speed_multiplier=float_multiplier_lower(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_enemy_box_encountered_at_front_with_left_right_behind_object(
        self, basic_speed
    ) -> ComplexAction:
        # 在前遇到敌方箱子，左方右方后方有物体，太危险了，我们选择贪分，直接前进（有中断)，然后交给边缘，（强袭直接上它丫的啊）
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
        ]

    def on_objects_encountered_at_left_behind(self, basic_speed) -> ComplexAction:
        """
        will turn right and move forward, then turn back to observe the objects,
        will exit the chain action on encountering the edge when moving forward
        :param basic_speed:
        """

        return [
            new_ActionFrame(
                action_speed=(basic_speed, -basic_speed),
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=enlarge_multiplier_l(),
                action_duration_multiplier=enlarge_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
                break_action=(new_ActionFrame(),),
            ),
            # in the default, break action overrides frames below
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=(-basic_speed, basic_speed),
                action_speed_multiplier=float_multiplier_upper(),
                action_duration_multiplier=enlarge_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
        ]

    def on_objects_encountered_at_left_right(self, basic_speed) -> ComplexAction:
        """
        this action will fall back first and then randomly turn left or right
        :param basic_speed: The basic speed of the robot.
        """
        sign = random_sign()
        return [
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
                break_action=(new_ActionFrame(),),
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=(sign * basic_speed, -sign * basic_speed),
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
        ]

    def on_neutral_box_encountered_at_front(self, basic_speed) -> ComplexAction:
        """
        similar to enemy car reaction, but with lower speed multiplier
        """
        # TODO: use break action to improve performance
        sign = random_sign()
        duration = getattr(self, self.CONFIG_BASIC_DURATION_KEY)
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=enlarge_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(action_duration=10),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=duration,
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=(sign * basic_speed, -sign * basic_speed),
                action_speed_multiplier=enlarge_multiplier_l(),
                action_duration=duration,
            ),
            new_ActionFrame(),
        ]

    def on_nothing(self, basic_speed) -> ComplexAction:
        return []

    def on_enemy_car_encountered_at_front_with_left_object(
        self, basic_speed
    ) -> ComplexAction:
        # 当前面有车左边有障碍物时，撞下对面的车然后后退至安全位置
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=enlarge_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(action_duration=10),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_enemy_car_encountered_at_front_with_right_object(
        self, basic_speed
    ) -> ComplexAction:
        # 当前面有车右边有障碍物时，撞下对面的车然后后退至安全位置
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=enlarge_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(action_duration=10),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_enemy_car_encountered_at_front_with_behind_object(
        self, basic_speed
    ) -> ComplexAction:
        # 当前面有车后边有障碍物时，撞下对面的车然后随机转向至后对边缘
        sign = random_sign()
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=enlarge_multiplier_ll(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(action_duration=10),
            new_ActionFrame(
                action_speed=(sign * basic_speed, -sign * basic_speed),
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
        ]

    def on_enemy_car_encountered_at_front_with_left_right_object(
        self, basic_speed
    ) -> ComplexAction:
        # 当前面有车左右有障碍物时，撞下对面的车然后后退至安全位置
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=enlarge_multiplier_ll(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(action_duration=10),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=shrink_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_enemy_car_encountered_at_front_with_left_behind_object(
        self, basic_speed
    ) -> ComplexAction:
        # 当前面有车左后有障碍物时，撞下对面的车然后右转，再前进至安全位置

        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=enlarge_multiplier_ll(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(action_duration=10),
            new_ActionFrame(
                action_speed=(basic_speed, -basic_speed),
                action_speed_multiplier=shrink_multiplier_ll(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
        ]

    def on_enemy_car_encountered_at_front_with_right_behind_object(
        self, basic_speed
    ) -> ComplexAction:
        # 当前面有车右后有障碍物时，撞下对面的车然后左转，再前进至安全位置

        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=enlarge_multiplier_ll(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(action_duration=10),
            new_ActionFrame(
                action_speed=(-basic_speed, basic_speed),
                action_speed_multiplier=shrink_multiplier_ll(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
        ]

    def on_enemy_car_encountered_at_front_with_left_right_behind_object(
        self, basic_speed
    ) -> ComplexAction:
        # 当前面有车左右后有障碍物时，撞下对面的车然后随机转向，再前进至安全位置
        sign = random_sign()
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=enlarge_multiplier_ll(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(action_duration=10),
            new_ActionFrame(
                action_speed=(sign * basic_speed, -sign * basic_speed),
                action_speed_multiplier=shrink_multiplier_ll(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(),
        ]

    def on_allay_box_encountered_at_front(self, basic_speed: int) -> ComplexAction:
        sign = random_sign()
        return [
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=(sign * basic_speed, -sign * basic_speed),
                action_speed_multiplier=enlarge_multiplier_ll(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
        ]

    def on_enemy_box_encountered_at_front(self, basic_speed: int) -> ComplexAction:
        sign = random_sign()
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=enlarge_multiplier_ll(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(action_duration=10),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
            new_ActionFrame(
                action_speed=(sign * basic_speed, -sign * basic_speed),
                action_speed_multiplier=enlarge_multiplier_ll(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
            ),
            new_ActionFrame(),
        ]

    def on_enemy_car_encountered_at_front(self, basic_speed: int) -> ComplexAction:
        # TODO: dash til the edge, then fall back,should add a block skill(?)
        return [
            new_ActionFrame(
                action_speed=basic_speed,
                action_speed_multiplier=enlarge_multiplier_ll(),
                action_duration=getattr(self, self.CONFIG_DASH_TIMEOUT_KEY),
                breaker_func=self._front_watcher_merged,
            ),
            new_ActionFrame(action_duration=10),
            new_ActionFrame(
                action_speed=-basic_speed,
                action_speed_multiplier=float_multiplier_middle(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._rear_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_object_encountered_at_left(self, basic_speed: int) -> ComplexAction:
        return [
            new_ActionFrame(
                action_speed=(-basic_speed, basic_speed),
                action_speed_multiplier=enlarge_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_object_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_object_encountered_at_right(self, basic_speed: int) -> ComplexAction:
        return [
            new_ActionFrame(
                action_speed=(basic_speed, -basic_speed),
                action_speed_multiplier=enlarge_multiplier_l(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_object_watcher,
            ),
            new_ActionFrame(),
        ]

    def on_object_encountered_at_behind(self, basic_speed: int) -> ComplexAction:
        sign = random_sign()
        return [
            new_ActionFrame(
                action_speed=(sign * basic_speed, -sign * basic_speed),
                action_speed_multiplier=enlarge_multiplier_ll(),
                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY),
                breaker_func=self._front_object_watcher,
            ),
            new_ActionFrame(),
        ]

    # endregion
    # TODO unbind these tag id constants
    __TAG_STATUS_CODE_TABLE: Dict[str, Dict[str, int]] = {
        BLUE_TEAM: {
            f"{-1}/{True}": 400,
            f"{-1}/{False}": 0,
            f"{0}/{True}": 100,
            f"{0}/{False}": 100,
            f"{2}/{True}": 300,
            f"{2}/{False}": 300,
            f"{1}/{True}": 200,
            f"{1}/{False}": 200,
        },
        YELLOW_TEAM: {
            f"{-1}/{True}": 400,
            f"{-1}/{False}": 0,
            f"{0}/{True}": 100,
            f"{0}/{False}": 100,
            f"{1}/{True}": 300,
            f"{1}/{False}": 300,
            f"{2}/{True}": 200,
            f"{2}/{False}": 200,
        },
    }

    CONFIG_MOTION_KEY = "MotionSection"
    CONFIG_BASIC_DURATION_KEY = f"{CONFIG_MOTION_KEY}/BasicDuration"
    CONFIG_BASIC_SPEED_KEY = f"{CONFIG_MOTION_KEY}/BasicSpeed"

    CONFIG_DASH_TIMEOUT_KEY = f"{CONFIG_MOTION_KEY}/DashTimeout"
    CONFIG_INFER_KEY = "InferSection"

    CONFIG_MIN_BASELINES_KEY = f"{CONFIG_INFER_KEY}/MinBaselines"

    CONFIG_EDGE_WATCHER_KEY = "EdgeWatcher"
    CONFIG_EDGE_WATCHER_MAX_BASELINE_KEY = f"{CONFIG_EDGE_WATCHER_KEY}/MaxBaseline"

    CONFIG_EDGE_WATCHER_MIN_BASELINE_KEY = f"{CONFIG_EDGE_WATCHER_KEY}/MinBaseline"

    def react(self) -> int:
        status_code = self.infer()
        if status_code not in self.action_table:
            warnings.warn(
                f"\nUnknown status code: {status_code},please check the infer(), status code will reset to 0",
                stacklevel=2,
            )
            status_code = 0
        self.exc_action(
            self.action_table.get(status_code),
            getattr(self, self.CONFIG_BASIC_SPEED_KEY),
        )
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
        self.register_config(
            config_registry_path=self.CONFIG_BASIC_DURATION_KEY, value=400
        )
        self.register_config(
            config_registry_path=self.CONFIG_BASIC_SPEED_KEY, value=5000
        )
        self.register_config(
            config_registry_path=self.CONFIG_DASH_TIMEOUT_KEY, value=6000
        )

        # the inferring currently only support four sensors;
        # each in the list is corresponding to [front,behind,left,right]
        self.register_config(
            config_registry_path=self.CONFIG_MIN_BASELINES_KEY, value=[1300] * 4
        )

        self.register_config(
            self.CONFIG_EDGE_WATCHER_MAX_BASELINE_KEY, [2070, 2150, 2210, 2050]
        )
        self.register_config(
            self.CONFIG_EDGE_WATCHER_MIN_BASELINE_KEY, [1550, 1550, 1550, 1550]
        )

    def __init__(
        self,
        sensor_hub: SensorHub,
        action_player: ActionPlayer,
        config_path: str,
        tag_detector: Optional[TagDetector],
        surrounding_sensor_ids: Tuple[int, int, int, int],
        edge_sensor_ids: Tuple[int, int, int, int],
        grays_sensor_ids: Tuple[int, int],
        extra_sensor_ids: Tuple[int, int, int],
    ):
        super().__init__(
            sensor_hub=sensor_hub, player=action_player, config_path=config_path
        )
        self._tag_detector = tag_detector
        edge_min_lines = getattr(self, self.CONFIG_EDGE_WATCHER_MIN_BASELINE_KEY)
        edge_max_lines = getattr(self, self.CONFIG_EDGE_WATCHER_MAX_BASELINE_KEY)
        self._front_object_watcher: Watcher = build_io_watcher_from_indexed(
            sensor_update=self._sensors.on_board_io_updater[IU_INDEX],
            sensor_ids=extra_sensor_ids[0:2],
            activate_status_describer=(0, 0),
            use_any=True,
        )
        indexed_io_updater = self._sensors.on_board_io_updater[IU_INDEX]
        rear_sensor_id = extra_sensor_ids[-1]
        self._rear_object_watcher: Watcher = lambda: not bool(
            indexed_io_updater(rear_sensor_id)
        )

        self._full_edge_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=edge_sensor_ids,
            min_lines=edge_min_lines,
            max_lines=edge_max_lines,
            use_any=True,
        )
        self._rear_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=[edge_sensor_ids[1], edge_sensor_ids[2]],
            min_lines=[edge_min_lines[1], edge_min_lines[2]],
            max_lines=[edge_max_lines[1], edge_max_lines[2]],
            use_any=True,
        )
        self._front_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=[edge_sensor_ids[0], edge_sensor_ids[3]],
            min_lines=[edge_min_lines[0], edge_min_lines[3]],
            max_lines=[edge_max_lines[0], edge_max_lines[3]],
            use_any=True,
        )
        self._front_watcher_grays: Watcher = build_io_watcher_from_indexed(
            sensor_update=self._sensors.on_board_io_updater[IU_INDEX],
            sensor_ids=grays_sensor_ids,
            activate_status_describer=(0, 0),
            use_any=True,
        )

        self._front_watcher_merged: Watcher = watchers_merge(
            [self._front_watcher_grays, self._front_watcher], use_any=True
        )

        self._status_infer = self._make_infer_body(
            surrounding_sensor_ids, extra_sensor_ids
        )

    def _make_infer_body(
        self,
        sensor_ids: Tuple[int, int, int, int],
        extra_sensor_ids: Tuple[int, int, int],
    ):
        """
        make an infer_body with all variables bound locally, which can bring a better performance
        Args:
            extra_sensor_ids ():

        Returns:

        """
        tag_detector = self._tag_detector

        behind_left_right_weights = (
            self.KEY_BEHIND_OBJECT,
            self.KEY_LEFT_OBJECT,
            self.KEY_RIGHT_OBJECT,
        )
        min_baselines = getattr(self, self.CONFIG_MIN_BASELINES_KEY)
        front_object_table = self.__TAG_STATUS_CODE_TABLE.get(tag_detector.team_color)
        adc_updater = self._sensors.on_board_adc_updater[FU_INDEX]
        io_updater = self._sensors.on_board_io_updater[IU_INDEX]
        fb_id, rb_id, l1_id, r1_id = sensor_ids
        fb_min_line, rb_min_line, l1_min_line, r1_min_line = min_baselines
        ftl_id, ftr_id, rtr_id = extra_sensor_ids

        (
            behind_status_weight,
            left_status_weight,
            right_status_weight,
        ) = behind_left_right_weights

        def status_infer() -> int:
            """

            Returns: the status code of surroundings.

            """
            # use updater to get updated sensor data
            adc_updated_data = adc_updater()

            # calc for the front status
            status_bools = (
                any(
                    [
                        not bool(io_updater(ftl_id)),
                        not bool(io_updater(ftr_id)),
                        adc_updated_data[fb_id] > fb_min_line,
                    ]
                ),
                any(
                    [
                        not bool(io_updater(rtr_id)),
                        adc_updated_data[rb_id] > rb_min_line,
                    ]
                ),
                adc_updated_data[l1_id] > l1_min_line,
                adc_updated_data[r1_id] > r1_min_line,
            )
            # calc for the three-direction status, behind, left, right
            # calc for the surrounding status code except front
            left_right_behind_status = (
                status_bools[1] * behind_status_weight
                + status_bools[2] * left_status_weight
                + status_bools[3] * right_status_weight
            )
            # use front sensors and tag to search the corresponding status code
            front_object_status = front_object_table.get(
                f"{tag_detector.tag_id}/{status_bools[0]}"
            )
            # fixme: here seems is a status calc bug, it generate a code that can't be found in the table.
            # TODO: should add a tag-follow feature, because the tag may not be at the very front of the robot.

            code = left_right_behind_status + front_object_status
            # warnings.warn(f'\rStatusCode: {code}')
            return code

        return status_infer
