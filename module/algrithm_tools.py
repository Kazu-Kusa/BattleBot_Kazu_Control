def compute_error(current_angle, target_angle):
    # 计算目标偏差，注意角度转换为[-180, 180]范围
    error = (current_angle - target_angle + 180) % 360 - 180
    return error
