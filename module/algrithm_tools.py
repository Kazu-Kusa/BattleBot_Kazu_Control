def compute_error(current_angle, target_angle, direction=1):
    """
    计算当前角度与目标角度之间的角度偏差。
    :param current_angle: 当前角度，单位：度数。取值范围 [-180, 180]
    :param target_angle: 目标角度，单位：度数。取值范围 [-180, 180]
    :param direction: 方向，1 表示顺时针，-1 表示逆时针。
    :return: 当前角度到目标角度的角度差，单位：度数，取值范围：[-180, 180]

    :document:
        可以将当前角度和目标角度以及方向作为参数传入该函数，函数会先计算出绝对角度差，
        然后根据方向参数来判断应该返回顺时针方向的角度差还是逆时针方向的角度差。
        如果 direction=1，则表示需要计算顺时针方向的角度差，所以就将绝对角度差取相反数；
        如果 direction=-1，则表示需要计算逆时针方向的角度差，同样也将绝对角度差取相反数即可。
    """
    error = (target_angle - current_angle) % 360  # 先计算出绝对角度差

    if error > 180:  # 如果绝对角度差大于 180 度，则表示需要改变方向
        error = 360 - error

        if direction == 1:
            error = -error  # 若要计算顺时针方向的角度差，则取相反数
    elif direction == -1:
        error = -error  # 若要计算逆时针方向的角度差，则取相反数

    return error


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
    :return: 若逆时针更近，则返回 -1；若顺时针更近，则返回 1；若两者距离相等，则返回 0。
    """
    # 将角度都转为正值
    current_angle = (current_angle + 360) % 360
    target_angle = (target_angle + 360) % 360

    # 计算逆时针距离和顺时针距离
    counterclockwise_distance = min((360 - target_angle + current_angle) % 360,
                                    (360 - current_angle + target_angle) % 360)
    clockwise_distance = min((360 - current_angle + target_angle) % 360, (360 - target_angle + current_angle) % 360)

    # 判断两者距离哪个更短
    if counterclockwise_distance < clockwise_distance:
        return -1  # 逆时针更近
    elif counterclockwise_distance > clockwise_distance:
        return 1  # 顺时针更近
    else:
        return 0  # 两者距离相等
