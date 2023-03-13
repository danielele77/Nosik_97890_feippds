"""
This module implements dinning philosophers problem.
Solution using a token is implemented.
Token is represented as Semaphore for each philosopher.
"""

__author__ = "Daniel Nošík, Tomáš Vavro"
__email__ = "xnosik@stuba.sk"
__license__ = "MIT"

from fei.ppds import Thread, Mutex, Semaphore, print
from time import sleep

NUM_PHILOSOPHERS: int = 5  # number of philosophers/forks
NUM_RUNS: int = 10  # number of repetitions of think-eat cycle of philosophers


class Shared:
    """
        Class with synchronization tools and variable
    """

    def __init__(self):
        """Initialize an instance of Shared."""
        self.mutex = Mutex()  # protects integrity of data (index of token)
        self.token_index = 0  # determinate at whom philosophers eats ( using modulation by 5)
        self.forks = [Mutex() for _ in range(NUM_PHILOSOPHERS)]  # represents forks
        self.tokens = [Semaphore(0) for _ in range(NUM_PHILOSOPHERS)]  # represents "Token" for each philosopher
        self.tokens[0] = Semaphore(1)  # give token to first philosopher


def think(i: int):
    """
    Simulates thinking.

    Arguments:
        i - philosopher's id
    """

    print(f"Philosopher {i} is thinking!")
    sleep(0.1)


def eat(i: int):
    """
    Simulates eating.

    Arguments:
        i - philosopher's id
    """

    print(f"Philosopher {i} is eating!")
    sleep(0.1)


def take_forks(i: int, shared: Shared):
    """
    Simulates taking of forks with waiting for a turn

    Arguments:
        i - philosopher's id
        shared - object with synchronization tools and variable
    """

    shared.tokens[i].wait()  # philosopher waits for the token, then takes forks
    shared.forks[i].lock()  # take right fork
    sleep(0.25)
    shared.forks[(i + 1) % NUM_PHILOSOPHERS].lock()  # take left fork


def put_down_forks(i: int, shared: Shared):
    """
    Simulates putting down of forks with shift token to neighbouring philosopher

    Arguments:
        i - philosopher's id
        shared - object with synchronization tools and variable
    """

    shared.forks[i].unlock()  # put back right fork
    shared.forks[(i + 1) % NUM_PHILOSOPHERS].unlock()  # put back left fork
    shared.mutex.lock()  # protects integrity of data
    shared.token_index += 1
    shared.tokens[shared.token_index % 5].signal()  # give token to the next philosopher
    shared.mutex.unlock()


def philosopher(i: int, shared: Shared):
    """Run philosopher's code.

    Arguments:
        i - philosopher's id
        shared - object with synchronization tools and variable
    """

    for _ in range(NUM_RUNS):
        think(i)
        # get forks
        take_forks(i, shared)
        eat(i)
        put_down_forks(i, shared)


def main():
    """
    Run main.
    """

    shared: Shared = Shared()
    philosophers: list[Thread] = [
        Thread(philosopher, i, shared) for i in range(NUM_PHILOSOPHERS)
    ]
    for p in philosophers:
        p.join()


if __name__ == "__main__":
    main()
