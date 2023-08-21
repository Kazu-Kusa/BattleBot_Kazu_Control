from repo.uptechStar.module.actions import new_ActionFrame, ActionFrame
from repo.uptechStar.module.algrithm_tools import FLOAT_SET_UPPER, FLOAT_SET_LOWER, FLOAT_SET_MIDDLE, SHRINK_SET_LLL, \
    SHRINK_SET_LL, SHRINK_SET_L, ENLARGE_SET_LLL, ENLARGE_SET_LL, ENLARGE_SET_L

multiplier_group = [FLOAT_SET_UPPER, FLOAT_SET_LOWER, FLOAT_SET_MIDDLE,
                    SHRINK_SET_LLL, SHRINK_SET_LL, SHRINK_SET_L,
                    ENLARGE_SET_LLL, ENLARGE_SET_LL, ENLARGE_SET_L]

a = []


def action_down(speed=3000, duration=210):
    # 前进 后退
    for x1 in multiplier_group:
        for x in x1:
            for y1 in multiplier_group:
                for y in y1:
                    for z in (-1, 1):
                        a.append(new_ActionFrame(action_speed=z * speed,
                                                 action_speed_multiplier=x,
                                                 action_duration=duration,
                                                 action_duration_multiplier=y))
    # 左转 右转
    for x1 in multiplier_group:
        for x in x1:
            for y1 in multiplier_group:
                for y in y1:
                    for z in (-1, 1):
                        a.append(new_ActionFrame(action_speed=(z * speed, -z * speed),
                                                 action_speed_multiplier=x,
                                                 action_duration=duration,
                                                 action_duration_multiplier=y))
    # 前左轮锁定，前进,后退
    for x1 in multiplier_group:
        for x in x1:
            for y1 in multiplier_group:
                for y in y1:
                    for z in (-1, 1):
                        a.append(new_ActionFrame(action_speed=(0, z * speed, z * speed, z * speed),
                                                 action_speed_multiplier=x,
                                                 action_duration=duration,
                                                 action_duration_multiplier=y))
    # 后左轮锁定，前进,后退
    for x1 in multiplier_group:
        for x in x1:
            for y1 in multiplier_group:
                for y in y1:
                    for z in (-1, 1):
                        a.append(new_ActionFrame(action_speed=(z * speed, 0, z * speed, z * speed),
                                                 action_speed_multiplier=x,
                                                 action_duration=duration,
                                                 action_duration_multiplier=y))
    # 后右轮锁定，前进，后退
    for x1 in multiplier_group:
        for x in x1:
            for y1 in multiplier_group:
                for y in y1:
                    for z in (-1, 1):
                        a.append(new_ActionFrame(action_speed=(z * speed, z * speed, 0, z * speed),
                                                 action_speed_multiplier=x,
                                                 action_duration=duration,
                                                 action_duration_multiplier=y))
    # 前右轮锁定，前进，后退
    for x1 in multiplier_group:
        for x in x1:
            for y1 in multiplier_group:
                for y in y1:
                    for z in (-1, 1):
                        a.append(new_ActionFrame(action_speed=(z * speed, z * speed, z * speed, 0),
                                                 action_speed_multiplier=x,
                                                 action_duration=duration,
                                                 action_duration_multiplier=y))


action_down()
print(len(a))
ActionFrame.save_cache()
