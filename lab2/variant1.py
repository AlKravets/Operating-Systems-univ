import socket
from enum import Enum,IntFlag
import multiprocessing as mp
import os
import time
import signal
import select
import logging


logging.basicConfig(level=logging.INFO)

class Status(IntFlag):
    Pause = 0
    Cont = 1
    End = 2
    Cont_no_Ques = 3 # продолжить без вопросов



def foo(arg):
    """

    """
    for i in range(1):
        logging.debug(f"function working with arg: {arg}")
        time.sleep(1)
    return arg

def foo_long(arg):
    n=10
    for i in range(n):
        logging.debug(f"function long it {i} of {n} working with arg: {arg}")
        time.sleep(1)
    return arg


# def decor_add_queue(function_to_decorate):
#     def wrapper(f_arg, queue):
#         queue.put(function_to_decorate(f_arg))
#     return wrapper



def decor_add_pipe(function_to_decorate):
    def wrapper(f_arg, pipe_connect):
        pipe_connect.send(function_to_decorate(f_arg))
    return wrapper


def client_function(pair, func, f_arg):
    """
    Функция клиента, она будет передавать по адресу pair результат вычисления func(f_arg)
    """
    logging.debug('Start client')
    parent_connect , child_connect = mp.Pipe() # создаем Pipe для синхронизации процессов

    p = mp.Process(target=decor_add_pipe(func), args=(f_arg, child_connect)) # процесс для вычисления функции

    s = socket.socket()
    s.settimeout(0.1)
    s.connect(pair) # соединяемся с сервером

    logging.debug('Client connected')
    
    p.start() 

    
    kill_flag = False # флаг для экстренного завершения процесса вычисления
    
    while p.is_alive() and not kill_flag:
        
        try:
            command = int(s.recv(1024))
            logging.debug(f'Client recv command {command}')

            if command == Status.Pause:
                os.kill(p.pid, signal.SIGTSTP) 
            elif command == Status.Cont:
                os.kill(p.pid, signal.SIGCONT)
            elif command == Status.End:
                p.kill()
                
                kill_flag = True
                child_connect.close()
                parent_connect.close()
                del child_connect
                del parent_connect
            else:
                pass          
            
        except socket.timeout:
            pass
    
    
    if not kill_flag and parent_connect is not None:
        res = parent_connect.recv()
        logging.debug(f'Client has result: {res}')
        s.send(str(res).encode())
        
    s.close()

    logging.debug('Client before end')




if __name__ == "__main__":


    sock = socket.socket()

    pair = ('127.0.0.1', 3000) # адрес сервера

    sock.bind(pair)
    sock.listen()

    # Запуск процессов, что будут считать функции
    p_f = mp.Process(target=client_function, args=(pair, foo, True))
    p_g = mp.Process(target=client_function, args=(pair, foo_long, False))

    p_list = [p_f,p_g]

    connections = []
    for proc in p_list:
        proc.start() # Начинаем вычисления
        connections.append(sock.accept()[0]) # подключаем клиента для передачи данных

    for conn in connections:
        conn.setblocking(0) # необходимо для неблокирующей передачи данных


    epoll = select.epoll()

    for conn in connections:
        epoll.register(conn.fileno(), select.EPOLLIN) # Регистрируем событие возможности чтения из сокета

    conn_map = {conn.fileno(): conn for conn in connections}

    timer = 3 # таймер вызова меню
    result = [] # будущий результат

    quest_flag = False # флаг продолжения без вопросов

    start_time = time.time() # отметка времени для таймера

    while len(connections)>0:
        events = epoll.poll(1) # проверка на возможность чтения из сокетов
        
        for fileno, event in events: # читаем из всех возможных сокетов
            
            data = (conn_map[fileno].recv(1024)).decode() # чтение
            logging.debug(f'Fileno {fileno} recv result {data}')
            result.append(data)
            
            # Далее убираем сокет из которого прочитали
            connections.pop(connections.index(conn_map[fileno])) 
            epoll.unregister(fileno) # убираем отслеживание сокета
            conn_map[fileno].close()
            logging.debug(f'Close fileno {fileno}')

        
        if time.time()- start_time > timer and len(connections)>0 and not quest_flag: # вызов меню
            for conn in connections:    # ставим вычисления на паузу
                conn.send(str(int(Status.Pause)).encode())  
            comm = input('Write 1 to continue, 2 to stop, 3 to continue without questions: ')
            if int(comm) == Status.Cont_no_Ques:
                # если выбрана команда продолжать без вопросов, то ставим флаг и отправляем команду
                # продолжать
                quest_flag = True
                comm = str(int(Status.Cont)) 
            
            for conn in connections: # отправляем команду сокетам
                conn.send(comm.encode("utf8"))
            if int(comm) == Status.End:
                for conn in connections:
                    conn.close()
                connections = []
                conn_map = {}

            start_time = time.time()
    
    for proc in p_list:
        proc.join()
    sock.close()

    if len(result)< 2:
        print('Cant give answer')
    else:
        print('Answer:', result[0] or result[1])