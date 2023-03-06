# Sleeping barber problem

This module contains implenentation of Lamport's bakery algorithm in Python (version 3.10) using`fei.ppds`
module (`pip install --user fei.ppds`). The implementation is part of an assignment from the Parallel Programming and
Distributed Systems course taught at the Slovak University of Technology. The code in this model is impleted by pseudo
code preseted at lecture from PPDS course [[1]](https://youtu.be/IOeO6RDhhac). The terms process and thread are loosely
substitutable in the context of this module.

## The problem

This problem is related to inter-process communnication and synchronization (of those proccess) and is define by analogy
to barbershop [[2]](https://en.wikipedia.org/wiki/Sleeping_barber_problem). In the barbershop are there two rooms,
waiting room (with N seats) and barbers room (with 1 steat). In the barbershop are followed rules applied:

1. If there is no customer, the barber sleeps,

2. A customer must wake the barber if he/she is sleeping,

3. Customer waits for a seat, if all seats are full,

4. If the barber is busy (doing haircut) and customers enter, but seat is

   available, the customer sit down and
   wait [[1]](https://youtu.be/IOeO6RDhhac) [[2]](https://en.wikipedia.org/wiki/Sleeping_barber_problem).

From the rules above it can be assumed, that coordiantion between customer and barber must be provided. Barber must give
haircut and customer must get haircut concurrently.

## The solution

The solution consists from 4 semaphors and 1 mutex which are part of class **Shared** (shared between all threads **
customers/barber**) .The **waiting_room** variable represents total number of available seats. Current count of
customers in the barbershop is stored in **customers**, the data integrity of this variable **must be** protected.
Customer and barber refer to the thread.

```python
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
```

Pairs of semaphores are used to create 2 **rendezvous(es)**, which are used for signalization:

1. Semaphore **customer** and **barber** create rendezous , which use customer to signalise to barber, that he/she come
   and barber, that he/she is ready to cut hair. This is used in **barber** and **customer** function.

   ```python
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
   ```

   ```python
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
   ```

With this is satisfied that "Barber must give haircut and customer must get haircut concurrently.", the cut_hair() and
get_haircut(i). The customer thread need to chcek before if is available seat in waiting room:

```python
    
shared.mutex.lock()  # lock for ensure data integrity
if shared.customers == shared.waiting_room:  # checks available seat
   shared.mutex.unlock()  # unlock counter, because its value will not be changed
   balk(i)  # wait for an available seat
   continue  # next attempt
shared.customers += 1  # get seat in the waiting room
print("CUSTOMER: {} is in the room".format(i))
shared.mutex.unlock()  # unlock after increme        
```

Due to **customers** variable could be used by another threads (customers) is there used mutex. The mutex ensures that
only one thread (customer) can access it at a time. If there is no seat, customer wait, bulk() function, otherwise enter
to waitingroom (shared.customers += 1).

2. Semaphore **customer_done** and **barber_done** create rendezous , which use customer to signalise to barber, that
   he/she stasified with cut and barber to signalise to customer, that he finished haircut. (The execution of function
   get_haircut(i) and cut_hait() is finished).

   ```python
           get_haircut(i)  # customer getting haircut
   
           shared.customer_done.signal()  # sync customer and barber after haircut (wait each other)
           shared.barber_done.wait()  # sync customer and barber after haircut (wait each other)
   
           shared.mutex.lock()  # lock for ensure data integrity
           print("CUSTOMER: {} leaves the barbershop".format(i))
           shared.customers -= 1  # customer leaves barbershop
           shared.mutex.unlock()
   
           growing_hair(i)  # customers hair grow up
   ```

The code snippet above show customer function, customer give signal to barber, that he/she is satisfied with haircut **
shared.customer_done.signal** ( get_haircut(i) finished ) and than wait for barber to finish haircut **
shared.customer_done.signal**. After that customer leaves **shared.customers -= 1** the barbershop and will comeback
afer his/her hair grows out (after growing_hair() finished). The integrity of the customer variable must be again
proteced.

The snipet code below show barber funcition code. Barber wait for customer_done signal and after give signal to
customer, that haircut is done.

```python
        cut_hair()  # barber giving haircut

shared.customer_done.wait()  # sync barber and customer after haircut (wait each other)
shared.barber_done.signal()  # sync barber and customer after haircut (wait each other)
```

## The output

The output below shows situatian with the capacity of waitingroom is **3** and **5** customers. Three customers enter (
0, 1 and 2) and two wait (3 and 4). The barber sleeps, customer 0 wakes him up, the barber cuts his/her hair.
Customers (3 and 4) are still waiting. After customer 0 finishes his/her haircut, customer 0 leaves and his/her hair
grows. The barber starts cutting customer 1's hair and so one of the waiting customers enters, customer 4. Customer 3 is
still waiting. When customer 1 is finished (leave and starts growing his/her hair), the waiting customer 3 enters...

![](https://github.com/danielele77/Nosik_97890_feippds/blob/02/output.png)

## Excution

The program can be run it on device supporting Python 3.10 and with installed all neccsary packages. To customize number
of customers and size of waitingroom, use global variables:

```python
C = 5  # set customers count
N = 3  # set max customers count in barbershop
```
