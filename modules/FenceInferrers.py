from typing import Tuple

from modules.AbsFenceInferrer import AbstractFenceInferrer
from repo.uptechStar.module.actions import ActionPlayer, new_ActionFrame
from repo.uptechStar.module.algrithm_tools import random_sign, enlarge_multiplier_ll, float_multiplier_middle, \
    float_multiplier_lower
from repo.uptechStar.module.inferrer_base import ComplexAction
from repo.uptechStar.module.sensors import SensorHub, FU_INDEX
from repo.uptechStar.module.watcher import Watcher, build_watcher_full_ctrl, build_watcher_simple, watchers_merge


class StandardFenceInferrer(AbstractFenceInferrer):
    CONFIG_MOTION_KEY = 'MotionSection'
    CONFIG_BASIC_DURATION_KEY = f'{CONFIG_MOTION_KEY}/BasicDuration'
    CONFIG_BASIC_SPEED_KEY = f'{CONFIG_MOTION_KEY}/BasicSpeed'
    CONFIG_OFF_STAGE_DASH_DURATION_KEY = f'{CONFIG_MOTION_KEY}/OffStageDashDuration'
    CONFIG_OFF_STAGE_DASH_SPEED_KEY = f'{CONFIG_MOTION_KEY}/OffStageDashSpeed'
    CONFIG_FENCE_INFER_KEY = 'InferSection'
    CONFIG_FENCE_MAX_BASE_LINE_KEY = f"{CONFIG_FENCE_INFER_KEY}/FenceMaxBaseline"
    CONFIG_FENCE_MIN_BASE_LINE_KEY = f'{CONFIG_FENCE_INFER_KEY}/FenceMinBaseline'

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
                new_ActionFrame
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

        self.register_config(config_registry_path=self.CONFIG_FENCE_MAX_BASE_LINE_KEY,
                             value=[1900] * 4)
        self.register_config(config_registry_path=self.CONFIG_FENCE_MIN_BASE_LINE_KEY,
                             value=[1500] * 4)

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
        self._rear_object_watcher: Watcher = build_watcher_simple(
            sensor_update=self._sensors.on_board_io_updater[FU_INDEX],
            sensor_id=extra_sensor_ids[2:],  # actually, this watcher uses only one sensor ()
            max_line=1
        )

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

        def infer_body() -> int:
            # TODO imp this method
            return 0

        self._infer_body = infer_body

    def infer(self) -> int:
        return self._infer_body()

    # region methods

    def on_front_to_fence(self, basic_speed) -> ComplexAction:
        sign = random_sign()
        return [new_ActionFrame(action_speed=getattr(self, self.CONFIG_OFF_STAGE_DASH_SPEED_KEY),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY), ),
                new_ActionFrame(action_speed=getattr(self, self.CONFIG_OFF_STAGE_DASH_SPEED_KEY),
                                action_duration=getattr(self, self.CONFIG_OFF_STAGE_DASH_DURATION_KEY)),
                new_ActionFrame(),
                new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_left_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(-basic_speed, basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_right_to_fence(self, basic_speed) -> ComplexAction:
        return [new_ActionFrame(action_speed=(basic_speed, -basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
                                action_duration=getattr(self, self.CONFIG_BASIC_DURATION_KEY)),
                new_ActionFrame()]

    def on_behind_to_fence(self, basic_speed) -> ComplexAction:
        sign = random_sign()
        return [new_ActionFrame(action_speed=(sign * basic_speed, -sign * basic_speed),
                                action_speed_multiplier=enlarge_multiplier_ll(),
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
