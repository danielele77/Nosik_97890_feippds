# Dinning philosophers problem

This module contains implenentation of Dinning philosophers problem in Python (version 3.10) using`fei.ppds`
module (`pip install --user fei.ppds`). The implementation is part of an assignment from the Parallel Programming and
Distributed Systems course taught at the Slovak University of Technology. The code in this model is modification of code
preseted at lecture from the PPDS
course [[1]](https://github.com/tj314/ppds-2023-cvicenia/blob/master/seminar4/04_philosophers.py). The terms process and
thread are loosely substitutable and are represtend as philosopher'silos in the context of this module.

## The problem

The dining philosopher's problem is the classical problem of synchronization which says that Five philosophers are
sitting around a circular table and their job is to think and eat alternatively. A bowl of noodles is placed at the
center of the table along with five chopsticks for each of the philosophers. The followed rules applied are applied:

1. To eat a philosopher needs both their right and a left chopstick,

2. A philosopher can only eat if both immediate left and right chopsticks of the philosopher is available,

3. In case if both immediate left and right chopsticks of the philosopher are not available then the philosopher puts
   down their (either left or right) chopstick and starts thinking
   again [[2]](https://www.javatpoint.com/os-dining-philosophers-problem).

From the rules above it can be assumed, that coordiantion between philosophers must be provided, because there may be a
situation where they all want to eat at the same time, pick up one fork and thus block each other (deadlock).

## The solution(s)

There are several solutions to this problem like:

- solution with waiter,

- solution left-handed and right-handed philosophers,

- solution with token.

Each with its own advantages and disadvantages. Therefore, it is important to consider the use of a particular solution
with a view to the problem to be solved. This section compares two of the above solutions, the waiter
solution [[1]](https://github.com/tj314/ppds-2023-cvicenia/blob/master/seminar4/04_philosophers.py) and the token
solution. However before comparision, let's describe our solution with token.

The solution consits of **shared** class, which conisits of synchronization tools and variable. There is used one mutex
for protection of data integrity, **token_index**  variable, this variable is used to determinate whom turn is to eat.
In this soltution can eat concurrently only one philosopher, others must wait. The forks are represtented as Mutex, each
fork is one **mutex**. There are five tokens, represented as Sempathors. The first one is at init set to value of 1.
This configuration enables the first philosopher to eat (**eat(i: int)**) after think (**think(i: int)**).

```python
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

```

There is **philosopher** function which simulates beahaviour of philosopher.

```python
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
```

The flow is as follow, philosopher think, after that he attempts to take forks (the right one and then the left one) by
calling take_forks() fucntion. In this function philosopher until his turn (tokens[i] is 1). Let's consider, philosopher
0, we can take foorks (lock mutexes) due to value of his semaphore (at init set to 1) and then eat.

```python
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

```

After he eats, he puts forks back by calling **put_down_forks()** fucntion, in this function are mutexes unlocked (forks
are put back) and then variable shared variable **token_index** incremented. The **signal()** is called on the semaphore
with index **token_index % 5**, the token si passed to next philosopher, who is waiting in **take_forks**() function at
semaphore. And so on...

```python
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
```

This is repated **NUM_RUNS** times.

#### The waiter solution[[1]](https://github.com/tj314/ppds-2023-cvicenia/blob/master/seminar4/04_philosophers.py)

In waiter solutions are forks represented as **5 Mutex** and there is one **waiter**, which is represented as
Semaphore() with value of  **4**.

```python
class Shared:
    """Represent shared data for all threads."""

    def __init__(self):
        """Initialize an instance of Shared."""
        self.forks = [Mutex() for _ in range(NUM_PHILOSOPHERS)]
        self.waiter: Semaphore = Semaphore(NUM_PHILOSOPHERS - 1)
```

This semaphore, waiter, enables to 4 philosophers try to take forks, the last one must wait. After one the philosophers
finish eating and put the forks the waiting philosopher has a chance to get to eat.

```python
def philosopher(i: int, shared: Shared):
    """Run philosopher's code.
    Args:
        i -- philosopher's id
        shared -- shared data
    """
    for _ in range(NUM_RUNS):
        think(i)
        # get forks
        shared.waiter.wait()
        shared.forks[i].lock()
        sleep(0.5)
        shared.forks[(i + 1) % NUM_PHILOSOPHERS].lock()
        eat(i)
        shared.forks[i].unlock()
        shared.forks[(i + 1) % NUM_PHILOSOPHERS].unlock()
        shared.waiter.signal()

```

### The comparation

As we can see, both solutions provide a solution to the Dinning philosophers' problem. In the token solution, each
philosopher is guaranteed to eat with a fixed order. This can lead to starvation of the philosopher, in case it will
wait long for the philosophers ahead of us in the queue (waiting for the token). In the waiter solution, the order of
eating is not guaranteed. This behavior, too, may lead to starvation of the philosopher if it waits too long for the
waiter (waiting longer than other philosophers - scheduler-dependent). However, it theoretically provides the
possibility of two philosophers eating simultaneously. In the case of the token solution, only one philosopher can eat
concurrently. The properties of these solutions can be understood as advantages/disadvantages in the context of solving
a specific problem and not in general.

# Execution

The program can be run it on device supporting Python 3.10 and with installed all neccsary packages. To customize number
of runs use global variable **NUM_RUNS**.

```python
NUM_RUNS: int = 10  # number of repetitions of think-eat cycle of philosophers
```
