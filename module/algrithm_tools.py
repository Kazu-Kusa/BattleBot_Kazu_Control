def compute_error(current_angle: float, target_angle: float) -> float:
    """
    计算当前角度与目标角度之间的相对角度。取劣弧，顺时针为正
    :param current_angle: 当前角度，单位：度数。取值范围 [-180, 180]
    :param target_angle: 目标角度，单位：度数。取值范围 [-180, 180]
    :return: 当前角度到目标角度的相对角度，单位：度数，取值范围：[-180, 180]
    """
    angle_diff = (target_angle - current_angle) % 360

    if angle_diff > 180:
        angle_diff -= 360
    elif angle_diff <= -180:
        angle_diff += 360

    return angle_diff


def calculate_relative_angle(current_angle: float, offset_angle: float) -> float:
    """
    计算相对偏移特定角度之后的目标角度，返回值范围 [-180, 180]。
    :param current_angle: 当前角度，单位：度数。取值范围 [-180, 180]
    :param offset_angle: 偏移角度，单位：度数。
    :return: 偏移后的目标角度，单位：度数。取值范围 [-180, 180]
    """
    return (current_angle + offset_angle + 180) % 360 - 180


def determine_direction(current_angle: float, target_angle: float) -> int:
    """
    判断当前角度移动到目标角度是逆时针更近还是顺时针更近。
    :param current_angle: 当前角度，单位：度数。取值范围 [-180, 180]
    :param target_angle: 目标角度，单位：度数。取值范围 [-180, 180]
    :return: 若逆时针更近，则返回 -1；若顺时针更近，则返回 1；若两者距离相等，会返回-1。
    """
    angle_diff = (target_angle - current_angle + 180) % 360 - 180
    return int(angle_diff / abs(angle_diff))
