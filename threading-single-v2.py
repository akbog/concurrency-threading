import logging
import random
import threading


class MessagingThread(threading.Thread):
    id: int
    bucket: list

    def __init__(self, id: int) -> None:
        super().__init__()
        self.id = id
        self.condition_lock = threading.Condition()
        self.bucket = []

    def send(self, x: int) -> None:
        self.condition_lock.acquire()
        self.bucket.append(x)
        self.condition_lock.notify()
        self.condition_lock.release()

    def read(self) -> int:
        while True:
            try:
                value = self.bucket.pop()
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
        super().__init__()

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
