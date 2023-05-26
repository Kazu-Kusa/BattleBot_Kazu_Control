# from repo.uptechStar.up_controller import motor_speed_test
from repo.uptechStar.uptech import UpTech

if __name__ == '__main__':
    # motor_speed_test(laps=1)
    # motor_speed_test(laps=1, using_id=False)
    a = UpTech(debug=True, fan_control=False)

    print(a.get_io(0))
