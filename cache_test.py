import random
import time
from matplotlib import pyplot as plt

from repo.uptechStar.module.db_tools import persistent_lru_cache
from repo.uptechStar.module.algrithm_tools import bake_to_cache, performance_evaluate


@persistent_lru_cache('cache')
def my_function(x):
    print("Calculating...")
    time.sleep(0.01)
    return x + 1


def learning_curve(function=my_function, multiplier: int = 2, laps: int = 20):
    op_durations_list = []

    for _ in range(laps):
        start_time = time.time()
        for i in range(256):
            # 第一次调用会计算并缓存结果
            print(function(random.randint(0, 256 * multiplier)))
        op_durations_list.append(time.time() - start_time)
    plt.plot(range(laps), op_durations_list)
    plt.show()
    # 输出: Calculating... \n 6


# learning_curve(multiplier=10)
# bake_to_cache()
performance_evaluate()
