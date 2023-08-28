from repo.uptechStar.module.hotConfigure.valueTest import read_sensors

adc_labels = {
    6: 'EDGE_FL',
    7: "EDGE_RL",
    2: 'EDGE_FR',
    1: 'EDGE_RR',
    8: 'L1',
    0: 'R1',
    3: 'FB', 5: 'RB',
    4: 'GRAY'
}

io_labels = {
    3: "gray l",
    2: "gray r",

    7: 'ftl',
    6: 'ftr',
    5: 'rtr'
}

read_sensors(adc_labels=adc_labels, io_labels=io_labels)
