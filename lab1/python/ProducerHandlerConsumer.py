import threading
from concurrent.futures import ThreadPoolExecutor

"""
Основная идея в threading.Condition они будут отвечать за блокировку в нужный момент.
"""


def ex_producer():
    test_str = "HELLO world12345$%^*"*5
    
    # None - завершающий символ
    data = list(test_str) + [None]
    num = 0
    while num < len(data):
        yield data[num]
        num+=1


def ex_handler(str_symbol):
    return str_symbol.lower()

def ex_consumer(value):
    print(value, end='')




class PHC_machine:
    def __init__(self, producer, handler, consumer, max_size_buffer = 5):
        
        
        self.buffer = []
        self.max_buf_size = max_size_buffer

        self._producer= producer()
        self._handler = handler
        self._consumer = consumer

        self._end_flag = False # флаг, что обозначает завершение потоков

        self._mutex = threading.RLock()

        self._prod_cond = threading.Condition(self._mutex)
        self._handl_cond = threading.Condition(self._mutex)
        self._cons_cond = threading.Condition(self._mutex)

    def produce(self):
        while not self._end_flag:
            with self._prod_cond:
                while len(self.buffer) < self.max_buf_size:
                    next_symbol = next(self._producer)

                    if next_symbol is None : # закончились данные
                        self._end_flag = True
                        break
                    else:
                        self.buffer.append(next_symbol)
                
                self._handl_cond.notify() # сообщаем, что можно обрабатывать данные

                if not self._end_flag:
                    self._prod_cond.wait() # ожидаем
                
    def handle(self):
        while True:
            with self._handl_cond:
                for index, item in enumerate(self.buffer):
                    self.buffer[index] = self._handler(str(item))

                self._cons_cond.notify() # сообщаем, что можно читать данные
                
                if self._end_flag:
                    break

                if not self._end_flag:
                    self._handl_cond.wait() #ожидаем

    def consume(self):
        while True:
            with self._cons_cond:
                while len(self.buffer) >0:
                    self._consumer(self.buffer.pop(0))
                
                self._prod_cond.notify() # сообщаем, что можно добавлять данные
                
                if self._end_flag:
                    break

                if not self._end_flag:
                    self._cons_cond.wait() #ожидаем

if __name__ == "__main__":
    mh = PHC_machine(ex_producer,ex_handler,ex_consumer)

    # th1 = threading.Thread(target=mh.produce)
    # th2 = threading.Thread(target=mh.handle)
    # th3 = threading.Thread(target=mh.consume)

    # th1.start()
    # th2.start()
    # th3.start()

    # th1.join()
    # th2.join()
    # th3.join()

    with ThreadPoolExecutor(max_workers= 3) as pool:
        pool.submit(mh.produce)
        pool.submit(mh.handle)
        pool.submit(mh.consume)

    print()