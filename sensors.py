from repo.uptechStar.module.hotConfigure.valueTest import read_sensors
from ctypes import cdll

if __name__ == '__main__':
    # read_sensors(2)
    adc = {0: 'edge_rr', 1: 'edge_fr', 2: 'edge_fl', 3: 'edge_rl', 4: 'fb', 5: 'rb', 6: 'fr', 7: 'r3', 8: 'l3'}

    io = {7: 'r_gray', 6: 'l_gray'}
    read_sensors(interval=0.01, adc_labels=adc, io_labels=io)
    # read_sensors(1)
