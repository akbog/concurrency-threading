import logging
import queue
import random
import threading
from typing import Iterable, Tuple

QUEUE_SIZE = 10

class MessagingThread(threading.Thread):
    id: int
    fifo: queue.Queue

    def __init__(self, id: int) -> None:
        super().__init__(target=lambda x: self.run())
        self.id = id
        self.fifo = queue.Queue(maxsize=QUEUE_SIZE)

    def send(self, src: int, x: int) -> None:
        self.fifo.put((src, x))

    def read(self) -> Tuple[int, int]:
        value = self.fifo.get()
        return value

    def run(self) -> None:
        #Passed into the thread
        raise NotImplemented()

class Receiver(MessagingThread):
    def run(self) -> None:
        for i in range(100):
            sender, num = self.read()
            logging.info("Receiver read %s", num)


class Sender(threading.Thread):

    def __init__(self, id: int, receiver: Receiver) -> None:
        self.receiver: Receiver = receiver
        self.id = id
        super().__init__(target=lambda x: self.run())

    def run(self) -> None:
        for _ in range(100):
            num = random.randint(0, 1000)
            self.receiver.send(self.id, num)
            logging.info("Sender sent %s", num)

class VotingThread(MessagingThread):
    peers: Iterable[MessagingThread]

    def set_peers(self, peers: Iterable[MessagingThread]) -> None:
        self.peers = [x for x in peers if x != self]

    def run(self) -> None:
        for i in range(100):
            num = random.randint(0, 1000)
            logging.info("Round %s: Thread %s generated %s", i, self.id, num)
            mem = [num]
            for peer in self.peers:
                peer.send(self.id, num)
            for peer in self.peers:
                mem.append(self.read()[1])
            logging.info("Round %s: Thread %s picked %s", i, self.id, min(mem))
    
    def __init__(self, id: int) -> None:
        self.peers = []
        super().__init__(id)

#This still suffers from the queue getting stuck (e.g. get is blocked because a queue has been dequeued but has not had any items put into it)
#How to prevent this from happening?
#Requirement 1: Propagate the value to all peers
#Requirement 2: Wait for all peers to add their value to your queue
#Requirement 3: Pick the minimum value from the queue

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
