import logging
import random
import threading
from typing import Iterable, Tuple

# Hello, World!

class MessagingThread(threading.Thread):
    id: int
    buffer: list

    def send(self, src: int, x: int) -> None:
        self.buffer.append((src, x))

    def read(self) -> Tuple[int, int]:
        while (len(self.buffer) < 1):
            continue
        return self.buffer.pop(0)

    def run(self) -> None:
        #Passed into the thread
        raise NotImplemented()

    def __init__(self, id: int) -> None:
        self.id = id
        self.buffer = []
        super().__init__(group=None, name=None, target=lambda x: self.run())

class Receiver(MessagingThread):
    def run(self) -> None:
        for i in range(100):
            sender, num = self.read()
            logging.info("Receiver read %s", num)


class Sender(MessagingThread):
    receiver: Receiver

    def run(self) -> None:
        for i in range(100):
            num = random.randint(0, 1000)
            self.receiver.send(self.id, num)
            logging.info("Sender sent %s", num)

    def __init__(self, id: int, receiver: Receiver) -> None:
        self.receiver = receiver
        super().__init__(id)

# 01:31:43: Sender sent 565
# 01:31:43: Receiver read 565
# 01:31:43: Sender sent 342
# 01:31:43: Receiver read 342
# 01:31:43: Receiver read 424
# 01:31:43: Sender sent 424
# 01:31:43: Sender sent 189
# 01:31:43: Sender sent 947
# 01:31:43: Sender sent 168
# 01:31:43: Receiver read 189
# 01:31:43: Receiver read 947
# 01:31:43: Receiver read 168


class VotingThread(MessagingThread):
    peers: Iterable[MessagingThread]

    def set_peers(self, peers: Iterable[MessagingThread]) -> None:
        self.peers = [x for x in peers if x != self]

    def run(self) -> None:
        for i in range(100):
            num = random.randint(0, 1000)
            logging.info("Round %s: Thread %s generated %s", i, self.id, num)
            mem = []
            for peer in self.peers:
                peer.send(self.id, num)
            for peer in self.peers:
                mem.append(peer.read()[1])
            logging.info("Round %s: Thread %s picked %s", i, self.id, min(mem))
    
    def __init__(self, id: int) -> None:
        self.peers = []
        super().__init__(id)


threads = []
for i in range(3):
    threads.append(VotingThread(i))
for th in threads:
    th.set_peers(threads)
for th in threads:
    th.start()
for th in threads:
    th.join()

if __name__ == "__main__":
    x = Receiver(0)
    y = Sender(1, x)
    y.start()
    x.start()
    x.join()
    y.join()
