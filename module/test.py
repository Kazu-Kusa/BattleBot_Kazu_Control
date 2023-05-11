import unittest
from testRoot import test
from ctypes import cdll


class MyTestCase(unittest.TestCase):
    def test_something(self):

        self.assertEqual(1, 1)  # add assertion here

    def test_primes(self):
        nb_primes = 1000
        p = [0] * nb_primes
        if nb_primes > 1000:
            nb_primes = 1000

        len_p = 0  # The current number of elements in p.
        n = 2
        while len_p < nb_primes:
            # Is n prime?
            for i in p[:len_p]:
                if n % i == 0:
                    break

            # If no break occurred in the loop, we have a prime.
            else:
                p[len_p] = n
                len_p += 1
            n += 1

        # Let's return the result in a python list:
        result_as_list = [prime for prime in p[:len_p]]
        print(result_as_list)
        return result_as_list

    def test_k(self):
        a = cdll.LoadLibrary('testRoot/build/test.cpython-310-arm-linux-gnueabihf.so')
        a.bench()


if __name__ == '__main__':
    unittest.main()
