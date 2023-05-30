from repo.uptechStar.extension.up_controller import motor_speed_test

# from repo.uptechStar.module.up_controller import motor_speed_test_liner
# from repo.uptechStar.module.hotConfigure.sync_test import count_adds_per_second


# from repo.uptechStar.module.close_loop_controller import CloseLoopController

if __name__ == '__main__':
    # motor_speed_test_liner(detailed_info=True)
    # motor_speed_test(laps=1, interval=1)
    # motor_speed_test(laps=1, interval=0.5)
    # motor_speed_test(laps=1, interval=0.25)
    # motor_speed_test(laps=1, interval=0.125)
    # motor_speed_test(laps=1, interval=0.0625)
    # motor_speed_test(laps=1, interval=0.0375)
    # motor_speed_test(laps=1, interval=0.0185)

    # con = CloseLoopController()

    # con.open_userInput_channel(debug=True)

    from time import perf_counter_ns

    while True:
        print(perf_counter_ns())
