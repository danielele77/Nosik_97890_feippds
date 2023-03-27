# Savages problem

This module contains implenentation of Savages problem in Python (version 3.10) using`fei.ppds`
module (`pip install --user fei.ppds`). The implementation is part of an assignment from the Parallel Programming and
Distributed Systems course taught at the Slovak University of Technology. The code in this module is modification of
code preseted at lecture from the PPDS course [[1]](https://www.youtube.com/watch?v=iotYZJzxKf4). The terms process and
thread are loosely substitutable and are represtend as savages and cooks in the context of this module.

## The problem

The savages of Equatorial Guinea are a very social and advanced type of savage. Not only do they eat together all the
time, but they also have among themselves cooks, who prepare a delicious zebra goulash. So they need all a reliable
system in which they report all the acts that are related to the common feast. There are severals rules:

- savages, they always start eating together. The last savage to arrive signals to everyone that they are all in and can
  start feasting,

- one by one, the savages take their portion from the pot until the pot is empty,

- asavage who discovers that the pot is already empty alerts the cooks to cook,

- the savages are waiting for the cooks to refill the full pot,

- the cook always cooks one portion and puts it in the pot,

- when the pot is full, the savages continue to feast,

- the whole process is repeated in an endless cycle.

## The solution(s)

The solution consits of severals synchronizations patterns and tools. The **Shared** class, (code snipet bellow) is used
to to initialize them. There is **servings** variable, which holds the current state of the pot (count of servings)
initialized to represent full pot in the beging. The two Mutexs, **mutex** a **mutex2**, are used for the protection
of **servings** variable. The `savage` and `cook` functions are executed concurrently by multiple threads, and they both
access the shared variable **servings**. Therefore, using a single mutex to protec **servings** would not be sufficient
to prevent race conditions and ensure thread safety. The **full_pot** and **empty_pot** are of type **Semaphore**,
initialy set to **0** and used to signalise by saveges to cooks state of the pot.

```python
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
```

In the **Shared** class are also created two **SimpleBarrier**, **barrier** and **barrier2** with parameter of **
SAVAGES_COUNT**. These barriers are used in `savage` function for ensure that there is no race condition where some
savages might access the shared data before others have had a chance to enter the critical section. With this
the `savages` can be synchronized in two stages, which helps to ensure that the problem is solved correctly. If there
was only one barrier, it would be more difficult to synchronize the `savages` in two stages, and there could be
synchronization issues that would make the solution incorrect.

```python
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
```

In the ``__init__`` function of the **SimpleBarrier** class is initialzed **n** variable, this represnts for how many
threads is going to be used. There is **mutex** for protection of

**counter**. Function ``wait`` implents logic of the barrier, when thread( **savage**) arrives lock the **mutex**
increment **counter**, check if all the threads have alredy arrived before him, if so signalise them they are all by **
signal(self.n)**, otherwise unlock **mutex** and wait with others for the last **thread.**

Nex part of solution are ``cook`` and ``savages``. The ``cook`` function represent beahaviour of cooks. Cook cooks in an
infinit loop. In the begining must wait for the **empty_pot** signal, this signal comes from **savage**, who discovers
empty pot. After signal came, the cook check if is not the pot full (filled up by another cook(s)), if not cooking and
then checks if the pot is full, if so send signal to savage waiting at the **full_pot** (the one, who send send signal
to **empty_pot**). All these under locked **mutex** for protection of **servings** variable. Then need to be **mutex**
unlocked.

```python
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
                shared.full_pot.signal()  # signal full pot
        shared.mutex2.unlock()
```

The``savege`` function represents behaviour of the savage. The ``sleep`` is used to randomize the order of savages.
After that in the infinit loop, are called ``wait`` functions at **SimpleBarrier** objects from **Shared**. This usage
was explained previously above. The **mutex** is used again. In this **mutex** thread, **savage**, cheks if the pot is
not empty. If not, he tooks the portion, unlock **mutex** and eats. In case the pot is empty is the **empty_pot** signal
is send, for which the **cooks** are waiting for. After the cooks filed up the pot he recieves the **full_pot** signal,
where waits. (This was describe before in `cook` funtion part frfrom the cooks point of view).

```python
def savage(savage_index, shared):
    """
    Simulates savage behaviour.

    Arguments:
         savage_index - id of savage
         shared - object with synchronization tools, variables and init variable
    """

    sleep(randint(10, 1000) / 1000)  # randomize order of savages
    while True:
        shared.barrier.wait()  # wait until all savages have arrived
        shared.barrier2.wait()  # all start taking portion together
        shared.mutex.lock()  # protects integrity of data
        if shared.servings == 0:  # if po empty alert cooks to cook and wait for that
            print(f"savage {savage_index}: empty pot")
            shared.empty_pot.signal(POT_SIZE)
            shared.full_pot.wait()
        print(f"savage {savage_index}: taking from pot")
        shared.servings -= 1  # tak portion
        shared.mutex.unlock()  # unlock lock, next savage can try to take portion
        eat(savage_index)  # eats
```

From the description above, it can be sated that the solution avoids the deadlock, and starvation of the **savages**.

## The output

In the image bellow is shown screenshot of terminal of the run program with initializations variable init to **POT_SIZE
= 3**, **COOKS_COUNT = 3** and **SAVAGES_COUNT = 3**. In the begging all savages wait for each other. The pot is
initialy full, so they can take from the pot, afer  **savage 3** took the portion the pot is empty, which was discovered
by **savage 0**, who noticed **cooks** and waits. The **cook 0**, **cook 1** and  **cook 2** add the portion, the pot is
full, which is discoverd by **cook 2** which signalised it ot **savage** waiting at **full_pot**. The savage can eat and
the savages can meet again. The procces is repeated in infinit lop.

![](https://github.com/danielele77/Nosik_97890_feippds/blob/02/output.png)

# Execution

The program can be run it on device supporting Python 3.10 and with installed all neccsary packages. To customize number
of **cooks**, **savages** and **pot size**, use global variables **COOKS_COUNT** , **SAVAGES_COUNT** and **POT_SIZE**.

```python
SAVAGES_COUNT = 4  # COUNT OF SAVAGES
COOKS_COUNT = 3  # COOKS COUNT
POT_SIZE = 3  # POT IS INITIALLY FILLED UP
```
