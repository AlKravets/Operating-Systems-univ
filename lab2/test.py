import socket
from enum import Enum,IntFlag
import multiprocessing as mp
import os
import time
import signal

class Status(IntFlag):
    Pause = 0
    Cont = 1
    End = 2
    Cont_no_Ques = 3 # продолжить без вопросов






def foo(arg):
    for i in range(10):
        print('foo going')
        time.sleep(1)
    return True

def decor_add_queue(function_to_decorate):
    def wrapper(f_arg, queue):
        queue.put(function_to_decorate(f_arg))
    return wrapper

def decor_add_pipe(function_to_decorate):
    def wrapper(f_arg, pipe_connect):
        pipe_connect.send(function_to_decorate(f_arg))
    return wrapper


if __name__ == '__main__':
    # q = mp.Queue()


    # p = mp.Process(target=decor_add_queue(foo), args=(True, q))

    parent_connect , child_connect = mp.Pipe()

    p = mp.Process(target=decor_add_pipe(foo), args=(True, child_connect))
        
    s = socket.socket()
    s.settimeout(0.1)
    s.connect(('127.0.0.1',3000))

    s.send(b'Start')
    
    p.start()

    flag = False
    kill_flag = False
    
    while (not flag) and p.is_alive():
        # print(p.is_alive())
        try:
            command = int(s.recv(1024))
        
            if command == Status.Pause:
                os.kill(p.pid, signal.SIGTSTP)
            if command == Status.Cont:
                os.kill(p.pid, signal.SIGCONT)
            if command == Status.End:
                # os.kill(p.pid,signal.SIGINT)
                p.terminate()
                kill_flag = True
                child_connect.close()
                parent_connect.close()
                del child_connect
                del parent_connect
            if command == Status.Cont_no_Ques:
                os.kill(p.pid, signal.SIGCONT)
                flag = True
            
        except socket.timeout:
            pass
    # p.join()
    if not kill_flag and parent_connect is not None:
        print(parent_connect.recv())
    s.close()