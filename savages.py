"""
This module contains an implementation of Savages problem.
"""

__authors__ = "Daniel Nošík, Mgr. Ing. Matúš Jókay, PhD."
__email__ = "xnosik@stuba.sk"
__license__ = "MIT"

from random import randint
from fei.ppds import Mutex, Semaphore, Thread, print
from time import sleep


class Shared:
    """
        Class with synchronization tools, variables and init variable. Used for init.
    """

    def __init__(self, n):
        self.servings = n  # initial portions in pot
        self.mutex = Mutex()  # protects integrity of data - savages
        self.mutex2 = Mutex()  # protects integrity of data - cooks
        self.barrier = SimpleBarrier(SAVAGES_COUNT)  # used for savages synchronization
        self.barrier2 = SimpleBarrier(SAVAGES_COUNT)  # used for savages synchronization
        self.full_pot = Semaphore(0)  # signalise full pot
        self.empty_pot = Semaphore(0)  # signalise empty pot


class SimpleBarrier:
    """
    Class with simple barrier implementation
    """

    def __init__(self, n):
        self.n = n  # number of threads (savages)
        self.counter = 0  # thread (savages) counter
        self.mutex = Mutex()  # protects counter integrity
        self.barrier = Semaphore(0)  # used as barrier

    def wait(self):
        """
        Implementation  of waiting at barrier. All threads must wait for the last one at barrier,
        the last thread make signal and all then all can pass.
        """
        self.mutex.lock()  # protec integrity of counter
        self.counter += 1  # when thread arrives +1
        if self.counter == self.n:  # if all threads arrived signal (the last one do it)
            self.counter = 0  # reset counter
            self.barrier.signal(self.n)
            print("Savages met")
        self.mutex.unlock()
        self.barrier.wait()  # thread(s) wait(s) for the last thread


def savage(savage_index, shared):
    """
    Simulates savage behaviour.

    Arguments:
         savage_index - id of savage
         shared - object with synchronization tools, variables and init variable
    """

    sleep(randint(10, 1000) / 1000)  # randomize order of savages
    while True:
        shared.barrier.wait()  # wait until all savages have arrived, all start taking portion together
        shared.barrier2.wait()  #
        shared.mutex.lock()  # protects integrity of data
        if shared.servings == 0:  # if po empty alert cooks to cook and wait for that
            print(f"savage {savage_index}: empty pot")
            shared.empty_pot.signal(POT_SIZE)
            shared.full_pot.wait()
        print(f"savage {savage_index}: taking from pot")
        shared.servings -= 1  # tak portion
        shared.mutex.unlock()  # unlock lock, next savage can try to take portion
        eat(savage_index)  # eats


def eat(savage_index):
    """
    Simulates eating of savage.

    Arguments:
         savage_index - id of savage
    """
    print(f"savage {savage_index} eating")
    sleep(randint(1, 3) / 100)


def cook(cook_index, shared):
    """
    Simulates cooks behaviour.

    Arguments:
         cook_index - id of cook
         shared - object with synchronization tools, variables and init variable
    """
    while True:
        shared.empty_pot.wait()  # wait for empty pot
        shared.mutex2.lock()  # protect integrity of counter for servings
        if shared.servings < POT_SIZE:  # cook if pot is not full
            print(f'cook {cook_index}: cooking')
            sleep(randint(5, 10) / 10)  # cooking
            shared.servings += 1  # add portion
            if shared.servings == POT_SIZE:  # if pot full
                print(f"cook {cook_index}: the pot is full")
                shared.full_pot.signal()  # signal full pot
        shared.mutex2.unlock()


SAVAGES_COUNT = 4  # COUNT OF SAVAGES
COOKS_COUNT = 3  # COOKS COUNT
POT_SIZE = 3  # POT IS INITIALLY FILLED UP

if __name__ == "__main__":
    shared = Shared(POT_SIZE)
    savages = []
    cooks = []
    for s in range(SAVAGES_COUNT):
        savages.append(Thread(savage, s, shared))
    for c in range(COOKS_COUNT):
        cooks.append(Thread(cook, c, shared))

    for t in savages + cooks:
        t.join()
