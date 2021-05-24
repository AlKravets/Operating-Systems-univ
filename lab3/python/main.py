import sys
import threading


CRITICAL_SEGMENT = 0

def function_critical(n = 1000):
    global CRITICAL_SEGMENT
    for _ in range(n):
        CRITICAL_SEGMENT += 1

def function_non_critical(n =1000):
    a = 0

    for _ in range(n):
        a += 1

if __name__ == "__main__":

    th_list = []
    n = 1000_000
    flag = True
    if (len(sys.argv) == 2) and (int(sys.argv[1]) == 2):
        # non critical
        flag = False
        for i in range(2):
            th_list.append(threading.Thread(target=function_non_critical, args = (n,)))        
    else:
        # critical
        for i in range(2):
            th_list.append(threading.Thread(target=function_critical, args = (n,)))        

        
    for th in th_list:
        th.start()

    
    for th in th_list:
        th.join()
    if flag:
        print(CRITICAL_SEGMENT)

