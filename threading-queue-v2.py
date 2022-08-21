import logging
import queue
import random
import threading
from typing import Iterable, Tuple

QUEUE_SIZE = 100

class MessagingThread(threading.Thread):
    id: int
    fifo: list

    def __init__(self, id: int) -> None:
        super().__init__()
        self.id = id
        self.condition_lock = threading.Condition()
        self.fifo = []

    def send(self, ident, x: int) -> None:
        self.condition_lock.acquire()
        self.fifo.append((ident, x))
        self.condition_lock.notify()
        self.condition_lock.release()

    def read(self, pop = True, index = 0) -> int:
        while True:
            try:
                if pop:
                    value = self.fifo.pop(index)
                else:
                    value = self.fifo[index]
                break
            except IndexError:
                self.condition_lock.acquire()
                notified = self.condition_lock.wait(2)
                if notified:
                    self.condition_lock.release()
                    continue
                else:
                    raise TimeoutError("Timed Out: Failed to get number from Queue")
        return value

# class MessagingThread(threading.Thread):
#     id: int
#     fifo: queue.Queue

#     def __init__(self, id: int) -> None:
#         super().__init__(target=lambda x: self.run())
#         self.id = id
#         self.fifo = queue.Queue(maxsize=QUEUE_SIZE)

#     def send(self, src: int, x: int) -> None:
#         self.fifo.put((src, x))

#     def read(self) -> Tuple[int, int]:
#         return self.fifo.get()

#     def run(self) -> None:
#         #Passed into the thread
#         raise NotImplemented()

class VotingThread(MessagingThread):
    peers: Iterable[MessagingThread]

    def set_peers(self, peers: Iterable[MessagingThread]) -> None:
        self.peers = [x for x in peers if x != self]
        self.ids = set([x.id for x in self.peers])

    def run(self) -> None:
        for i in range(100):
            num = random.randint(0, 1000)
            logging.info("Round %s: Thread %s generated %s", i, self.id, num)
            mem = {self.id : num}
            for peer in self.peers:
                peer.send(self.id, num)
                #These numbers can come in any order, and it is not guaranteed that all peers will sen
                #Because of this order, Node 1 will tend to receive numbers first + can receive all numbers before everyone else
                #and therefore can begin sending out round 2 numbs before everyone else is finished receiving numbers
                #need to use a hash map to store numbers corresponding to IDs so that we can be agnostic to queue order
            index = 0
            while len(mem) <= len(self.peers):
                ident, num = self.read()
                if ident not in mem:
                    mem[ident] = num
                else:
                    self.send(ident, num)
                index += 1
            logging.info("Round %s: Thread %s picked %s", i, self.id, min(mem.values()))
    
    def __init__(self, id: int) -> None:
        self.peers = []
        super().__init__(id)

if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    threads = []
    for i in range(QUEUE_SIZE):
        threads.append(VotingThread(i))
    for th in threads:
        th.set_peers(threads)
    for th in threads:
        th.start()
    for th in threads:
        th.join()
