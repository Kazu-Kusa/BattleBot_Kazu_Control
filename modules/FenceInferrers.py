from typing import Tuple, List, Callable

from modules.AbsFenceInferrer import AbstractFenceInferrer
from repo.uptechStar.module.actions import ActionPlayer, new_ActionFrame
from repo.uptechStar.module.algrithm_tools import random_sign, enlarge_multiplier_ll, float_multiplier_middle, \
    float_multiplier_lower, enlarge_multiplier_lll, shrink_multiplier_lll, shrink_multiplier_l
from repo.uptechStar.module.inferrer_base import ComplexAction
from repo.uptechStar.module.sensors import SensorHub, FU_INDEX, IU_INDEX
from repo.uptechStar.module.watcher import Watcher, build_watcher_full_ctrl, build_watcher_simple, watchers_merge

FRONT_INDEX, REAR_INDEX, LEFT_INDEX, RIGHT_INDEX = 0, 1, 2, 3


class StandardFenceInferrer(AbstractFenceInferrer):
    CONFIG_MOTION_KEY = 'MotionSection'
    CONFIG_BASIC_DURATION_KEY = f'{CONFIG_MOTION_KEY}/BasicDuration'
    CONFIG_BASIC_SPEED_KEY = f'{CONFIG_MOTION_KEY}/BasicSpeed'
    CONFIG_OFF_STAGE_DASH_DURATION_KEY = f'{CONFIG_MOTION_KEY}/OffStageDashDuration'
    CONFIG_OFF_STAGE_DASH_SPEED_KEY = f'{CONFIG_MOTION_KEY}/OffStageDashSpeed'
    CONFIG_FENCE_INFER_KEY = 'InferSection'
    CONFIG_FENCE_MIN_BASE_LINE_KEY = f'{CONFIG_FENCE_INFER_KEY}/FenceMinBaseline'

    CONFIG_FENCE_LR_MAX_Deviation_KEY = f'{CONFIG_FENCE_INFER_KEY}/LRMaxDeviation'

    CONFIG_EDGE_WATCHER_KEY = "EdgeWatcher"
    CONFIG_EDGE_WATCHER_MAX_BASELINE_KEY = f'{CONFIG_EDGE_WATCHER_KEY}/MaxBaseline'
    CONFIG_EDGE_WATCHER_MIN_BASELINE_KEY = f'{CONFIG_EDGE_WATCHER_KEY}/MinBaseline'

    def on_left_right_to_fence(self, basic_speed) -> ComplexAction:
        # 在左方和右方向上遇到围栏，我希望随机转向
        single = random_sign()
        return [new_ActionFrame(action_speed=(single * basic_speed, -single * basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()
                ]

    def on_front_behind_to_fence(self, basic_speed) -> ComplexAction:
        # 在前方和后方向上遇到围栏，我希望前进一段距离
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_lower(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()
                ]

    def on_front_left_right_to_fence(self, basic_speed) -> ComplexAction:
        # 在前方和左右方向上遇到围栏，我希望随机向某一个方向转向
        single = random_sign()
        return [new_ActionFrame(action_speed=(single * basic_speed, -single * basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()
                ]

    def on_front_left_behind_to_fence(self, basic_speed) -> ComplexAction:
        # 在前后方和左方向上遇到围栏，我希望向右转向
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=float_multiplier_lower(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_front_right_behind_to_fence(self, basic_speed) -> ComplexAction:
        # 在前后方和右方向上遇到围栏，我希望向左转向
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=float_multiplier_lower(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_left_right_behind_to_fence(self, basic_speed) -> ComplexAction:
        # 在左右方和后方向上遇到围栏，我希望前进一段距离后随机转向
        single = random_sign()
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_lower(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame,
                new_ActionFrame(action_speed=(single * basic_speed, -single * basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()
                ]

    def on_no_fence(self, basic_speed) -> ComplexAction:
        # 在没有围栏的情况下，我希望随机前进或者后退一段距离
        single = random_sign()
        return [new_ActionFrame(action_speed=single * basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_front_left_right_behind_to_fence(self, basic_speed) -> ComplexAction:
        # 在前后方和左右方向上遇到围栏，我希望随机转向
        single = random_sign()
        return [new_ActionFrame(action_speed=(single * basic_speed, -single * basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()
                ]

    def react(self) -> int:
        status_code = self.infer()

        self.exc_action(self.action_table.get(status_code),
                        getattr(self, self.CONFIG_BASIC_SPEED_KEY))
        return status_code

    def register_all_config(self):
        self.register_config(config_registry_path=self.CONFIG_BASIC_DURATION_KEY,
                             value=200)
        self.register_config(config_registry_path=self.CONFIG_BASIC_SPEED_KEY,
                             value=2500)
        self.register_config(config_registry_path=self.CONFIG_OFF_STAGE_DASH_DURATION_KEY,
                             value=600)
        self.register_config(config_registry_path=self.CONFIG_OFF_STAGE_DASH_SPEED_KEY,
                             value=-8000)

        self.register_config(config_registry_path=self.CONFIG_FENCE_MIN_BASE_LINE_KEY,
                             value=[800] * 4)
        self.register_config(self.CONFIG_FENCE_LR_MAX_Deviation_KEY,
                             200)

        self.register_config(self.CONFIG_EDGE_WATCHER_MAX_BASELINE_KEY, [2070, 2150, 2210, 2050])
        self.register_config(self.CONFIG_EDGE_WATCHER_MIN_BASELINE_KEY, [1550, 1550, 1550, 1550])

    def __init__(self, sensor_hub: SensorHub, action_player: ActionPlayer, config_path: str,
                 edge_sensor_ids: Tuple[int, int, int, int], surrounding_sensor_ids: Tuple[int, int, int, int],
                 grays_sensor_ids: Tuple[int, int],
                 extra_sensor_ids: Tuple[int, int, int]):
        super().__init__(sensor_hub=sensor_hub, player=action_player, config_path=config_path)

        self._front_object_watcher: Watcher = build_watcher_simple(
            sensor_update=self._sensors.on_board_io_updater[FU_INDEX],
            sensor_id=extra_sensor_ids[0:2],
            max_line=1,
            use_any=True
        )
        indexed_io_updater = self._sensors.on_board_io_updater[IU_INDEX]
        rear_sensor_id = extra_sensor_ids[-1]
        self._rear_object_watcher: Watcher = lambda: not bool(indexed_io_updater(rear_sensor_id))

        sensor_updater = self._sensors.on_board_adc_updater[FU_INDEX]
        left_sensor_id = surrounding_sensor_ids[LEFT_INDEX]
        right_sensor_id = surrounding_sensor_ids[RIGHT_INDEX]
        fence_min_baselines: List[int] = getattr(self, self.CONFIG_FENCE_MIN_BASE_LINE_KEY)
        left_sensor_fence_min_baseline = fence_min_baselines[LEFT_INDEX]
        right_sensor_fence_min_baseline = fence_min_baselines[RIGHT_INDEX]

        lr_max_deviation = getattr(self, self.CONFIG_FENCE_LR_MAX_Deviation_KEY)

        def left_right_objects_watcher() -> Tuple[bool, bool]:
            """
            a customized Watcher-liked func,judge fence existence in two directions
            Returns: a tuple, represents left is the fence and right is the fence in order

            """
            sensor_data = sensor_updater()

            left_is_fence, right_is_fence = False, False
            left_data = sensor_data[left_sensor_id]
            right_data = sensor_data[right_sensor_id]
            if left_data < left_sensor_fence_min_baseline and right_data < right_sensor_fence_min_baseline:
                # this checks the no activation case
                return left_is_fence, right_is_fence

            if left_data > right_data:
                # this checks the single direction to fence case
                left_is_fence = True
            else:
                right_is_fence = True

            if abs(left_data - right_data) < lr_max_deviation:
                # this checks the front to fence, parallel to the fence
                return False, False
            else:
                return left_is_fence, right_is_fence

        self._left_right_objects_watcher: Callable[[], Tuple[bool, bool]] = left_right_objects_watcher

        edge_min_lines = getattr(self, self.CONFIG_EDGE_WATCHER_MIN_BASELINE_KEY)
        edge_max_lines = getattr(self, self.CONFIG_EDGE_WATCHER_MAX_BASELINE_KEY)
        self._full_edge_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=edge_sensor_ids,
            min_lines=edge_min_lines,
            max_lines=edge_max_lines,
            use_any=True
        )
        self._rear_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=[edge_sensor_ids[1], edge_sensor_ids[2]],
            min_lines=[edge_min_lines[1], edge_min_lines[2]],
            max_lines=[edge_max_lines[1], edge_max_lines[2]],
            use_any=True)
        self._front_watcher: Watcher = build_watcher_full_ctrl(
            sensor_update=self._sensors.on_board_adc_updater[FU_INDEX],
            sensor_ids=[edge_sensor_ids[0], edge_sensor_ids[3]],
            min_lines=[edge_min_lines[0], edge_min_lines[3]],
            max_lines=[edge_max_lines[0], edge_max_lines[3]],
            use_any=True)
        self._front_watcher_grays: Watcher = build_watcher_simple(
            sensor_update=self._sensors.on_board_io_updater[FU_INDEX],
            sensor_id=grays_sensor_ids,
            max_line=1,
            use_any=True)

        self._front_watcher_merged: Watcher = watchers_merge([self._front_watcher_grays,
                                                              self._front_watcher],
                                                             use_any=True)

        weights = (
            self.KEY_FRONT_TO_FENCE,
            self.KEY_BEHIND_TO_FENCE,
            self.KEY_LEFT_TO_FENCE,
            self.KEY_RIGHT_TO_FENCE
        )

        fence_watchers: Tuple[Watcher, ...] = (
            self._front_object_watcher,
            self._rear_object_watcher,

        )

        def infer_body() -> int:
            """
            infer the fence in four-direction
            Returns: status code that represents the fence surrounded

            """
            nonlocal fence_watchers, weights

            status_code = 0
            all_status = [fence_watcher() for fence_watcher in fence_watchers]
            all_status.extend(left_right_objects_watcher())
            for status, weight in zip(all_status, weights):
                status_code += status * weight

            return status_code

        self._infer_body = infer_body

    def infer(self) -> int:
        return self._infer_body()

    # region methods

    def on_front_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=basic_speed,
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=getattr(self.CONFIG_OFF_STAGE_DASH_SPEED_KEY),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()
                ]

    def on_left_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=shrink_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_right_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=shrink_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_behind_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=shrink_multiplier_l(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_front_left_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_front_right_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_behind_left_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_behind_right_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=float_multiplier_middle(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    # endregion
