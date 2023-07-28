import time
from time import perf_counter_ns
import numpy as np

from numba import njit


# Define a generic function to calculate the power of a number based on its parity
def calculate_power(num):
    if num % 2 == 0:
        return num ** 2
    else:
        return num ** 3


# Define a generic function to apply the calculate_power function to an array
def apply_function(x, func):
    result = np.empty(len(x))
    for i in range(len(x)):
        result[i] = func(x[i])
    return result


def time_it(func):
    def wrapper(*args, **kwargs):
        temp_list = []
        result = None
        for _ in range(10):
            start_time = perf_counter_ns()

            result = func(*args, **kwargs)
            elapsed_time = perf_counter_ns() - start_time
            temp_list.append(elapsed_time)
        return result, sum(temp_list) / len(temp_list)

    return wrapper


# Define the original Python function
@time_it
def python_func(x):
    return apply_function(x, calculate_power)


# Use Numba for optimization
@time_it
@njit
def numba_func(x):
    result = np.empty(len(x))
    for i in range(len(x)):
        num = x[i]
        if num % 2 == 0:
            result1 = num ** 2
        else:
            result1 = num ** 3
        result[i] = result1
    return result


# Function for performance testing
def performance_test():
    sizes = [1000, 3000, 5000, 7000, 10000, 100000, 1000000, 10000000]
    results_python = []
    results_numba = []
    INT_NDARRAY = np.arange(1, 5 + 1)
    print(f'example input shape:\n'
          f'\tSize = 5\n'
          f'\t\t{INT_NDARRAY}\n'
          f'\tOperations:\n'
          f'\t\tExecute POWER 2 on even numbers, 3 on odd numbers\n'
          f'\tResults:\n'
          f'\t\t{numba_func(INT_NDARRAY)[0].tolist()}\n\n'
          f'--------------------------------------------------------------')

    for size in sizes:
        x = np.arange(1, size + 1)

        # Original Python test
        _, elapsed_time = numba_func(x)
        results_numba.append(elapsed_time)
        _, elapsed_time = python_func(x)
        results_python.append(elapsed_time)

        # Numba test

    # Visualize the results
    print("Size\t\t\tPython T1\t\tNumba T2\t\tT1/T2")
    print("--------------------------------------------------------------")
    for i in range(len(sizes)):
        t1 = results_python[i] / 1000000  # Time taken by original Python function in microseconds
        t2 = results_numba[i] / 1000000  # Time taken by Numba optimized function in microseconds
        speedup = results_python[i] / results_numba[i]  # Speedup factor of Numba over original Python function

        print(f"{sizes[i]}\t\t\t{t1:.2f}\t\t\t{t2:.2f}\t\t\t{speedup:.2f}")
    print("--------------------------------------------------------------")
    print('time unit: ms')


# Run the performance test
performance_test()
