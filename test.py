from repo.uptechStar.up_controller import motor_speed_test

if __name__ == '__main__':
    motor_speed_test(laps=1)
    motor_speed_test(laps=1, using_id=False)
