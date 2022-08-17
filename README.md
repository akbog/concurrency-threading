Concurrency & Concensus Making
-

Prompt
-

Imagine you have 2 tasks, a receiver and a sender. Initially, the sender needs to be able to send the receiver a message (e.g. a random integer value from 0 to 1000) & log the action of sending the message, and the receiver needs to be able to accept that message and acknowledge it by Logging the message itself.

- Part 1
    - Implement a solution utilizing python's threading module to ensure that a message can be passed from the sender to the receiver and that no messages get lost in the process.

- Part 2
    - Implement a solution where N **voting** threads each choose an integer at random between 0 and 1000 and propagate their choice to all other threads. The threads must each arrive at a consensus solution (e.g. the same integer value) at each iteration.
    
Files
-
This repository contains the following files:
    
    threading-intro.py -> The initial attempt at solving both Part 1 and Part 2 (i.e. during intro conversation)
    
    threading-single.py -> A second attempt at tackling Part 1 with a better understanding of threads + thread locking
    
    threading-queue.py -> A second attempt at tackling Part 2 with a better understanding of Queues (which implement thread locking etc.)

Looking Back At the initial attempt:
1. When first approaching the problem, I assumed the Sender and Receiver would have greater interaction (e.g. Sender Sends using its extended Send Method, and Reader Reads etc.)
    - In reality, the Sender just extends the threading part of the MessagingThread, and wraps the Receiver
    - Changed the Sender to simply extend the threading module
2. Need to pay attention to the handoff between the threads (e.g. the moment where one thread drops and the other is picked up) - Locking helped with this
3. My initial Solution for Part 1. used a list acting as a queue
    - Since we're only really sending a value back and forth, just changed that to a read/write on a value and it was a good opportunity to use locks and tackle the classic Producer-Consumer Problem
4. For Part 2. Understanding that a Queue implements *most* of the lock handling would have been useful, but I'm glad I implemented it with a list / value anyway to start
    
Remaining Issues:
1. The queue solution works great when `QUEUE_SIZE` and `THREAD_SIZE` are both `3`, but it encounters a deadlock occasionally at `10`
    - This is due to the fact that there is a chance that the thread sends out all of the values to all of its peers but does not neccesarily have a queue to read from once it's finished (e.g. it's own queue could still be empty)
    - I think I can solve this with some more clever Event handling, but I'll need a little bit more time for that!


HW:
1. Take a look at Paxos / Raft protocols for solving consensus
2. Improve Part 2. to handle edge cases of thread failure etc. and resolve queue deadlock issue
