def compute_error(current_angle: float, target_angle: float, direction=1) -> float:
    """
    计算当前角度与目标角度之间的角度偏差。
    :param current_angle: 当前角度，单位：度数。取值范围 [-180, 180]
    :param target_angle: 目标角度，单位：度数。取值范围 [-180, 180]
    :param direction: 方向，1 表示顺时针，-1 表示逆时针。
    :return: 当前角度到目标角度的角度差，单位：度数，取值范围：[-180, 180]
    """
    angle_diff = (target_angle - current_angle) % 360
    if angle_diff > 180:
        angle_diff -= 360

    return angle_diff * direction


def calculate_relative_angle(current_angle: float, offset_angle: float) -> float:
    """
    计算相对偏移特定角度之后的目标角度，返回值范围 [-180, 180]。
    :param current_angle: 当前角度，单位：度数。取值范围 [-180, 180]
    :param offset_angle: 偏移角度，单位：度数。
    :return: 偏移后的目标角度，单位：度数。取值范围 [-180, 180]
    """
    target_angle = current_angle + offset_angle  # 目标角度 = 当前角度 + 偏移角度
    target_angle = (target_angle + 180) % 360 - 180  # 确保目标角度在 [-180, 180] 的范围内
    return target_angle


def determine_direction(current_angle: float, target_angle: float) -> int:
    """
    判断当前角度移动到目标角度是逆时针更近还是顺时针更近。
    :param current_angle: 当前角度，单位：度数。取值范围 [-180, 180]
    :param target_angle: 目标角度，单位：度数。取值范围 [-180, 180]
    :return: 若逆时针更近，则返回 -1；若顺时针更近，则返回 1；若两者距离相等，则返回 -1。
    """
    angle_diff = (target_angle - current_angle + 180) % 360 - 180
    if angle_diff == 0:
        return -1  # 两者距离相等，按照题目要求返回 -1。
    else:
        return int(angle_diff / abs(angle_diff))
