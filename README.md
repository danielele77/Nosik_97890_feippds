# Lamport's bakery algorithm

This module contains implenentation of Lamport's bakery algorithm in Python (version 3.10) using`fei.ppds`
module (`pip install --user fei.ppds`). The implementation is part of an assignment from the Parallel Programming and
Distributed Systems course taught at the Slovak University of Technology. The terms process and thread are loosely
substitutable in the context of this module.

## The mutal exluction problem

The Lamport's bakery algorithm provides software soltution to the mutal exclusion problem for the general case of N
process. Mutal exluction problem occures in the context of computer science, when one of threads enters a critical
section while a concurent thread of execution is already accessing said critical section. Critical section refers to the
section of the program where access to the common resource is
performed [[Source]([Mutual exclusion - Wikipedia](https://en.wikipedia.org/wiki/Mutual_exclusion#Problem_description))]
.

## The Solution

For an algorithm to be considered a correct solution to the mutal exluction problem, it must ensure that the specific
conditions are met:

1. **no more than one process may be carried out in a critical area at any one time,**

2. **a process that executes outside the critical area must not prevent other processes from entering it,**

3. **the decision to enter must be made at the finite time,**

4. **processes cannot assume anything of mutual timing (scheduling) when entering the critical area.**

Bakery's algorithm satisfies these conditions as follows:

- **Condition 1**

  ```python
      # thread wants its order number
      entering[process_id] = True
      # thread obtains its order number
      number[process_id] = 1 + max(number)
      entering[process_id] = False
  
      # checks another threads
      for index, _ in enumerate(number):
          # waits for another processes obtains theirs order number
          while entering[index]:
              pass
  
          # waits until it is process turn (order number), in case of equality of order numbers,
          # their ids (indexes) decide, the smaller id has priority
          while number[index] != 0 and ((number[index], index) < (number[process_id], process_id)):
              pass
  
  ```

  This condition is met by part of code of **lock** function, where the thread recieves its order number.

  First, the process sets its **entering** variable to **True**, signaling its interest in entering the critical region
  and receiving a number order (current_max_order_number + 1) . After that sets back its **entering** variable to **
  False**.

  Second, the process checks value of entering variable of all another processes and wait until all procces recive
  theirs **order number**. That means all proceses must have set theirs **entering** variable to **False**.

  As a final step, the process waits its turn. This is done by checking the order numbers of the other processes. If its
  order number is lower, it can enter the critical area. In case of equality of order numbers, the id of the process is
  taken into account (lower has priority).

- **Condtion 2**

  ```python
  def unlock(process_id: int):
      """
      Unlock lock for process
  
      Arguments:
          process_id -- id (index) of process for which is lock unlocked
      """
  
      # resetting the process order number
      number[process_id] = 0
  ```

  The procces after excution of critical area set its **number** variable, order number, to **0** by calling **unlock**
  function. This puts the process at the bottom of the queue when it re-enters the critical area. (the algorithm is
  fairly)

- **Condition 3**

  ```python
      # thread wants its order number
      entering[process_id] = True
      # thread obtains its order number
      number[process_id] = 1 + max(number)
      # rescheduling of the process
      .
      .
  ```

  The decision to enter the critical area comes at a finite time because it is based on the order number of the
  processes. Equality of order numbers can occur due to rescheduling of the process right after it receives the order
  number. Then the process id decides, the smaller one has priority.

- **Condition 4**

  Rescheduling of the process during lock creation can occur at any time without affecting the correct functioning of
  the algorithm. Since as described earlier, it waits until all processes have been assigned a order number (order
  number > 0). Only then is it evaluated which process has access to the critical area.

# Excution

The algorithm can be run it on device supporting Python 3.10 and with installed all neccsary packages. To customize
number of thread and runs, use function in main.

```python
    init_global_variables(4, 5)  # 4 threads and 5 runs
```


