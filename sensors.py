from repo.uptechStar.module.hotConfigure.valueTest import read_sensors
from ctypes import cdll

if __name__ == '__main__':
    # read_sensors(2)
    # sen = cdll.LoadLibrary(
    #     '/home/pi/BattleBot/repo/uptechStar/build/uptechStar/hotConfigure/valueTest.cpython-310-arm-linux-gnueabihf.so')
    read_sensors(1, interval=0.001)
    # read_sensors(1)
