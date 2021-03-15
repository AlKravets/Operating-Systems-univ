from abc import ABC, abstractmethod
import threading
from concurrent.futures import ThreadPoolExecutor
import logging
import time



logging.basicConfig(level=logging.DEBUG)
SLEEP_TIME = 0




# генератор для создания данных
def ex_producer():
    test_str = "HELLO world12345$%^*"*5
    # test_str = "HELLo"
    data = list(test_str)
    num = 0
    while num < len(data):
        yield data[num]
        num+=1


def ex_handler(str_symbol):
    return str_symbol.lower()


class ABC_Consumer(ABC):
    @abstractmethod
    def __call__(self):
        """
        Получение символа на запись
        """
        pass

    def close(self):
        """
        при необходимости закрыть файлы
        """
        pass

class Consumer_Write_to_File(ABC_Consumer):
    def __init__(self, filepath):
        self.filepath = filepath
        self.file = open(self.filepath, 'w')

    def __call__(self, value):
        self.file.write(value)
    def close(self):
        self.file.close()

class Consumer_Write_to_Console(ABC_Consumer):
    def __call__(self, value):
        print(value,end='')

ex_consumer = Consumer_Write_to_Console()


class PHC_With_Threading_Condition:
    """
    Класс, что иллюстрирует работу Producer -> Handler -> Consumer
    Использует 3 условные переменные (threading.Condition) связанные одним RLock
    """
    def __init__(self, producer, handler, consumer, max_size_buffer = 5):
       
        self.buffer = []
        self.max_buf_size = max_size_buffer

        self._producer= producer() # генератор
        self._handler = handler
        self._consumer = consumer

        self._end_flag = False # флаг, что обозначает завершение потоков

        self._mutex = threading.RLock()

        self._prod_cond = threading.Condition(self._mutex)
        self._handl_cond = threading.Condition(self._mutex)
        self._cons_cond = threading.Condition(self._mutex)

        logging.info('Create object  PHC_With_Threading_Condition')

    def produce(self):
        logging.info('Start Producer')
        time.sleep(SLEEP_TIME)
        while not self._end_flag:
            with self._prod_cond:
                logging.info('Producer acquired lock (Producer condition)')
                time.sleep(SLEEP_TIME)


                while len(self.buffer) < self.max_buf_size:
                    try:
                        next_symbol = next(self._producer)
                        logging.debug(f"Producer created data: '{next_symbol}'")
                        time.sleep(SLEEP_TIME)
                        
                    except StopIteration:
                        self._end_flag = True
                        logging.info('Producer created all data. Start ending.')
                        time.sleep(SLEEP_TIME)
                        break                      

                    self.buffer.append(next_symbol)
                    logging.debug(f"Producer push data: '{next_symbol}' to buffer")
                    time.sleep(SLEEP_TIME)
                
                self._handl_cond.notify() # сообщаем, что можно обрабатывать данные
                
                logging.info(f'Producer filled {len(self.buffer)} cells')
                logging.info('Producer notify Handler')
                time.sleep(SLEEP_TIME)

                if not self._end_flag:
                    logging.info('Producer wait')
                    time.sleep(SLEEP_TIME)
                    self._prod_cond.wait() # ожидаем

                logging.info('Producer wait ended. Producer renewal acquired lock (Producer condition)')
                time.sleep(SLEEP_TIME)
            
            logging.info('Producer released lock (Producer condition)')
            time.sleep(SLEEP_TIME)
        
        logging.info('Producer end')
        time.sleep(SLEEP_TIME)
                  
    def handle(self):
        logging.info('Start Handler')
        time.sleep(SLEEP_TIME)
        while True:
            with self._handl_cond:
                logging.info('Handler acquired lock (Handler condition)')
                time.sleep(SLEEP_TIME)
                

                for index, item in enumerate(self.buffer):
                    self.buffer[index] = self._handler(str(item))
                    logging.debug(f"Handler change '{item}' to '{self.buffer[index]}'")
                    time.sleep(SLEEP_TIME)

                logging.info(f'Handler processed {len(self.buffer)} cells')
                
                self._cons_cond.notify() # сообщаем, что можно читать данные              
                logging.info('Handler notify Consumer')
                time.sleep(SLEEP_TIME)
                
                if self._end_flag:
                    logging.info('Handler processed all data. Start ending. Handler released lock (Handler condition)')
                    time.sleep(SLEEP_TIME)
                    break

                if not self._end_flag:
                    logging.info('Handler wait')
                    time.sleep(SLEEP_TIME)
                    self._handl_cond.wait() #ожидаем

                logging.info('Handler wait ended. Handler renewal acquired lock (Handler condition)')
                time.sleep(SLEEP_TIME)

            logging.info('Handler released lock (Handler condition)')
            time.sleep(SLEEP_TIME)
        
        logging.info('Handler end')
        time.sleep(SLEEP_TIME)

    def consume(self):
        logging.info('Start Consumer')
        time.sleep(SLEEP_TIME)
        while True:

            with self._cons_cond:
                
                logging.info('Consumer acquired lock (Consumer condition)')
                time.sleep(SLEEP_TIME)
                
                
                while len(self.buffer) >0:
                    item  =self.buffer.pop(0)
                    self._consumer(item)
                    logging.debug(f"Consumer read data: {item}")
                    time.sleep(SLEEP_TIME)
                
                logging.info(f"Consumer read all data in buffer")
                time.sleep(SLEEP_TIME)

                self._prod_cond.notify() # сообщаем, что можно добавлять данные

                logging.info('Consumer notify Producer')
                time.sleep(SLEEP_TIME)
                
                if self._end_flag:
                    logging.info('Consumer read all data. Start ending. Consumer released lock (Consumer condition)')
                    time.sleep(SLEEP_TIME)
                    break

                if not self._end_flag:
                    logging.info('Consumer wait')
                    time.sleep(SLEEP_TIME)
                    self._cons_cond.wait() #ожидаем

                logging.info('Consumer wait ended. Consumer renewal acquired lock (Consumer condition)')
                time.sleep(SLEEP_TIME)

            logging.info('Consumer released lock (Consumer condition)')
            time.sleep(SLEEP_TIME)
        if hasattr(self._consumer, "close"):
            self._consumer.close()
            logging.debug('Consumer call close')
            time.sleep(SLEEP_TIME)

        logging.debug('Consumer end')
        time.sleep(SLEEP_TIME)


class PHC_With_Three_Locks:
    """
    Класс, что иллюстрирует работу Producer -> Handler -> Consumer
    Использует 3 Lock (threading.Lock). Потоки будут сами себя блокировать после каждой итерации цикла.
    Другие потоки будут открывать заблокированные.
    """    
    def __init__(self, producer, handler, consumer, max_size_buffer = 5):
                
        self.buffer = []
        self.max_buf_size = max_size_buffer

        self._producer= producer() # генератор
        self._handler = handler
        self._consumer = consumer

        self._end_flag = False # флаг, что обозначает завершение потоков

        self._prod_lock = threading.Lock()
        self._handl_lock = threading.Lock()
        self._cons_lock = threading.Lock()

        logging.info('Create object PHC_With_Three_Locks')

        self._handl_lock.acquire()

        logging.info('Handler acquired lock (handl_lock)')
        time.sleep(SLEEP_TIME)

        self._cons_lock.acquire()

        logging.info('Consumer acquired lock (cons_lock)')
        time.sleep(SLEEP_TIME)

    def produce(self):
        logging.info('Start Producer')
        time.sleep(SLEEP_TIME)
        while not self._end_flag:
            logging.info('Producer before lock (prod_lock)')
            time.sleep(SLEEP_TIME)

            self._prod_lock.acquire()   # запираем Producer
            
            logging.info('Producer acquired lock (prod_lock)')
            time.sleep(SLEEP_TIME)

            while len(self.buffer) < self.max_buf_size:
                try:
                    next_symbol = next(self._producer)
                    logging.debug(f"Producer created data: '{next_symbol}'")
                    time.sleep(SLEEP_TIME)
                    
                except StopIteration:
                    self._end_flag = True
                    logging.info('Producer created all data. Start ending.')
                    time.sleep(SLEEP_TIME)
                    break                      

                self.buffer.append(next_symbol)
                logging.debug(f"Producer push data: '{next_symbol}' to buffer")
                time.sleep(SLEEP_TIME)
                       
            logging.info(f'Producer filled {len(self.buffer)} cells')



            self._handl_lock.release() # Открываем Handler
            
            logging.info('Producer released Handler`s lock (handl_lock)')
            time.sleep(SLEEP_TIME)
        
        logging.info('Producer end')
        time.sleep(SLEEP_TIME)

    def handle(self):
        logging.info('Start Handler')
        time.sleep(SLEEP_TIME)
        while True:
            
            logging.info('Handler before lock (handl_lock)')
            time.sleep(SLEEP_TIME)

            self._handl_lock.acquire() # запираем Handler
            
            logging.info('Handler acquired lock (handl_lock)')
            time.sleep(SLEEP_TIME)

            for index, item in enumerate(self.buffer):
                self.buffer[index] = self._handler(str(item))
                logging.debug(f"Handler change '{item}' to '{self.buffer[index]}'")
                time.sleep(SLEEP_TIME)

            logging.info(f'Handler processed {len(self.buffer)} cells')
            
            
            self._cons_lock.release() # открываем Consumer

            logging.info('Handler released Consumer`s lock (cons_lock)')
            time.sleep(SLEEP_TIME)
            
            if self._end_flag:
                logging.info('Handler processed all data. Start ending.')
                time.sleep(SLEEP_TIME)
                break

        
        logging.info('Handler end')
        time.sleep(SLEEP_TIME)

    def consume(self):
        logging.info('Start Consumer')
        time.sleep(SLEEP_TIME)
        while True:

            logging.info('Consumer before lock (cons_lock)')
            time.sleep(SLEEP_TIME)

            self._cons_lock.acquire() # запираем Consumer

            logging.info('Consumer acquired lock (cons_lock)')
            time.sleep(SLEEP_TIME)
            
            
            while len(self.buffer) >0:
                item  =self.buffer.pop(0)
                self._consumer(item)
                logging.debug(f"Consumer read data: {item}")
                time.sleep(SLEEP_TIME)
            
            logging.info(f"Consumer read all data in buffer")
            time.sleep(SLEEP_TIME)

            self._prod_lock.release() # Открываем Producer

            logging.info('Consumer released Producer`s lock (prod_lock)')
            time.sleep(SLEEP_TIME)

            if self._end_flag:
                logging.info('Consumer read all data. Start ending.')
                time.sleep(SLEEP_TIME)
                break

            
            
        if hasattr(self._consumer, "close"):
            self._consumer.close()
            logging.debug('Consumer call close')
            time.sleep(SLEEP_TIME)

        logging.debug('Consumer end')
        time.sleep(SLEEP_TIME)





if __name__ == "__main__":
    test_cons = Consumer_Write_to_File('results')
    
    # mh = PHC_With_Threading_Condition(ex_producer,ex_handler,ex_consumer, max_size_buffer=2)
    mh = PHC_With_Three_Locks(ex_producer,ex_handler,ex_consumer, max_size_buffer=2)

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