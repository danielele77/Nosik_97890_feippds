"""
This module contains an implementation of Sleeping Barber problem.
"""

__authors__ = "Daniel Nošík, Bc. Marian Šebeňa, Mgr. Ing. Matúš Jókay, PhD."
__email__ = "xnosik@stuba.sk"
__license__ = "MIT"

from fei.ppds import Mutex, Thread, Semaphore, print
from time import sleep
from random import randint


class Shared(object):
    """
        Class with synchronization tools, variables and init variable. Used for init.
    """

    def __init__(self):
        self.mutex = Mutex()  # protects integrity of data
        self.waiting_room = 0  # total number available seats in waiting room (include barbers seat)
        self.customers = 0  # current number of customers in barbershop
        self.customer = Semaphore(0)  # semaphore, which indicates to barber enter of customer
        self.barber = Semaphore(0)  # semaphore, which indicates barber readiness to customer after his enter
        self.customer_done = Semaphore(0)  # semaphore, which indicates to barber satisfaction of customer with haircut
        self.barber_done = Semaphore(0)  # semaphore, which indicates to customer, that the barber finished haircut


def get_haircut(i):
    """
    Simulates getting haircut.

    Arguments:
        i - id of customer
    """

    print("CUSTOMER: {} gets cut".format(i))
    sleep(randint(5, 10) / 10)


def cut_hair():
    """
    Simulates cutting customers hair by barber.
    """

    print()
    print("BARBER: cuts hair.")
    sleep(randint(5, 10) / 10)


def balk(i):
    """
    Simulates waiting of customer, when no seats are available.

    Arguments:
         i - id of customer, who waits for available seat
    """

    print("CUSTOMER: {} is waiting for a seat in waiting room.".format(i))
    sleep(randint(1, 3) / 10)


def growing_hair(i):
    """
    Simulates growing customers hair.

    Arguments:
         i - id of customer
    """

    print()
    print("CUSTOMER: {} hair grows".format(i))
    sleep(randint(10, 15) / 10)


def customer(i, shared):
    """
    Represents customers behavior.

    Arguments:
        i - id of customer
        shared - object with synchronization tools, variables and init variable
    """

    while True:
        shared.mutex.lock()  # lock for ensure data integrity
        if shared.customers == shared.waiting_room:  # checks available seat
            shared.mutex.unlock()  # unlock counter, because its value will not be changed
            balk(i)  # wait for an available seat
            continue  # next attempt
        shared.customers += 1  # get seat in the waiting room
        print("CUSTOMER: {} is in the room".format(i))
        shared.mutex.unlock()  # unlock after increment customer count

        shared.customer.signal()  # sync customer and barber before haircut (wait each other)
        shared.barber.wait()  # sync customer and barber before haircut (wait each other)

        get_haircut(i)  # customer getting haircut

        shared.customer_done.signal()  # sync customer and barber after haircut (wait each other)
        shared.barber_done.wait()  # sync customer and barber after haircut (wait each other)

        shared.mutex.lock()  # lock for ensure data integrity
        print("CUSTOMER: {} leaves the barbershop".format(i))
        shared.customers -= 1  # customer leaves barbershop
        shared.mutex.unlock()

        growing_hair(i)  # customers hair grow up


def barber(shared):
    """
    Represents barbers activity .

    Arguments:
        shared - object with synchronization tools, variables and init variable
    """

    while True:
        shared.customer.wait()  # sync barber and customer before haircut (wait each other)
        shared.barber.signal()  # sync barber and customer before haircut (wait each other)

        cut_hair()  # barber giving haircut

        shared.customer_done.wait()  # sync barber and customer after haircut (wait each other)
        shared.barber_done.signal()  # sync barber and customer after haircut (wait each other)


def main():
    """
    Function initializes object with synchronization tools and creates barbers and customers thread(s)
    """

    shared = Shared()
    shared.waiting_room = N  # set max customers count in barbershop
    customers = []  # threads represent customers

    for i in range(C):
        customers.append(Thread(customer, i, shared))
    hair_stylist = Thread(barber, shared)  # thread represents barber

    for t in customers + [hair_stylist]:
        t.join()


C = 5  # set customers count
N = 3  # set max customers count in barbershop

if __name__ == "__main__":
    main()
