import socket
from enum import Enum,IntFlag
import multiprocessing as mp
import os
import time
import signal

import asyncio

flag = True

async def client_connected(reader, writer):
    global flag
    # Communicate with the client with
    # reader/writer streams.  For example:
    
    print('Connected')

    # data = await reader.readline()
    # print(data)

    # while True:
    for _ in range(10):
        if flag:
            print('True')
        else:
            print('False')    
        await asyncio.sleep(0.1)
    
    # await asyncio.sleep(0.1)
    print('end')
    return True

# async def main(host, port):
#     global flag
#     srv = await asyncio.start_server(
#         client_connected, host, port)
#     # await srv.serve_forever()
#     await srv.start_serving()
#     for _ in range(1):
#         print(len(srv.sockets))
#         await asyncio.sleep(5)

#     loop = srv.get_loop()
#     print(loop)


#         # print(input())
#     flag = False
    
#     return 42

# res =asyncio.run(main('127.0.0.1', 3000))

# print(res)

loop = asyncio.get_event_loop()

server_gen = asyncio.start_server(client_connected,host = '127.0.0.1', port=3000)
server = loop.run_until_complete(server_gen)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass # Press Ctrl+C to stop
finally:
    server.close()
    loop.close()

