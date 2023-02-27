"""
This module contains an implementation of Lamport's bakery algorithm.

This solution works for N process, where N is positive integer and N >=1 .
The terms process and thread are loosely substitutable in the context of this module.
"""

__authors__ = "Daniel Nošík, Tomáš Vavro"
__email__ = "xnosik@stuba.sk"
__license__ = "MIT"

from fei.ppds import Thread
from time import sleep

number_threads: int = 0  # total count of threads which is created
number_runs: int = 0  # total number of runs of each thread

entering: list[bool] = []  # set entering[i] as True if just before thread i obtains order number and then False
number: list[int] = []  # number[i] contains obtained order number of process i


def process(process_id: int):
    """
    Simulates process

    Arguments:
        process_id -- id (index) of process
    """

    global number_runs, entering, number

    # execute critical section
    for i in range(number_runs):
        # process wants to enter critical section
        lock(process_id)
        # execute of critical section
        print("Process " + str(process_id) + " runs a complicated computation!")
        sleep(1)
        # exit critical section
        unlock(process_id)


def lock(process_id: int):
    """
    Creates lock for process

    Arguments:
        process_id -- id (index) of process for which is lock created
    """

    # thread wants its order number
    entering[process_id] = True
    # thread obtains its order number
    number[process_id] = 1 + max(number)
    entering[process_id] = False

    # checks another threads
    for index, _ in enumerate(number):
        # waits for another process obtains theirs order number
        while entering[index]:
            pass

        # waits until it is process turn (order number), in case of equality of order numbers,
        # their ids (indexes) decide, the smaller id has priority
        while number[index] != 0 and ((number[index], index) < (number[process_id], process_id)):
            pass


def unlock(process_id: int):
    """
    Unlock lock for process

    Arguments:
        process_id -- id (index) of process for which is lock unlocked
    """

    # resetting the process order number
    number[process_id] = 0


def init_global_variables(thread_count: int, runs: int):
    """
    Initializes necessary and configuration global variables

    Arguments:
        thread_count - number of threads to be created
        runs - number of executions of the critical section
    """

    global number_runs, number_threads, entering, number
    number_runs = runs
    number_threads = thread_count
    entering = [False] * number_threads
    number = [0] * number_threads


if __name__ == '__main__':
    init_global_variables(4, 5)
    threads = [Thread(process, i) for i in range(0, number_threads)]
    [t.join() for t in threads]
