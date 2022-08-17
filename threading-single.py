import logging
import random
import threading


class MessagingThread(threading.Thread):
    id: int
    value: int

    def __init__(self, id: int) -> None:
        super().__init__(target=lambda x: self.run())
        self.id = id
        self.sender_lock = threading.Lock()
        self.receiver_lock = threading.Lock()
        self.receiver_lock.acquire()

    def send(self, x: int) -> None:
        self.sender_lock.acquire()
        self.value = x
        self.receiver_lock.release()

    def read(self) -> int:
        self.receiver_lock.acquire()
        value = self.value
        self.sender_lock.release()
        return value

    def run(self) -> None:
        #Passed into the thread
        raise NotImplemented()

class Receiver(MessagingThread):
    def run(self) -> None:
        for i in range(100):
            num = self.read()
            logging.info("Receiver read %s", num)


class Sender(threading.Thread):

    def __init__(self, id: int, receiver: Receiver) -> None:
        self.receiver: Receiver = receiver
        self.id = id
        super().__init__(target=lambda x: self.run())

    def run(self) -> None:
        for i in range(100):
            num = random.randint(0, 1000)
            self.receiver.send(num)
            logging.info("Sender sent %s", num)

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    x = Receiver(0)
    y = Sender(1, x)
    y.start() #Calls to the run method
    x.start() 
    x.join() #Prevents from exiting when main thread exits
    y.join()
