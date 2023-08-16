from repo.uptechStar.module.hotConfigure.valueTest import read_sensors

adc_labels = {
    6: 'EDGE_FL',
    7: "EDGE_RL",
    2: 'EDGE_FR',
    1: 'EDGE_RR',
    8: 'L1',
    0: 'R1',
    3: 'FB', 5: 'RB',

}

read_sensors(adc_labels=adc_labels)
