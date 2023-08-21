import copy
import time
import warnings

from repo.uptechStar.module.onboardsensors import OnBoardSensors

a = OnBoardSensors()
print(a.adc_all_channels()[0])
result = []
warnings.warn('ascasv')
time.sleep(10)
end = time.time() + 5
while time.time() < end:
    result.append(copy.deepcopy(a.adc_all_channels()))
print('a')

for i in result:
    print(list(i))
print('asc')
print(len(result))
