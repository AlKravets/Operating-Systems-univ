import threading


# Буфер обмена данными для потоков
BUF = ""

def supplier_target (string_with_text = ''):
    """
    функция для потока поставщика
    """
    global BUF

    print('Supplier-thread: start')

    if not string_with_text:
        string_with_text = "Some TEST StrIng.1234#$%^"

    
    BUF = string_with_text
    print('Supplier-thread: fill buffer')

    print('Supplier-thread: end')

def handler_target(supplier_thread):
    """
    функция для потока обработчика.
    Принимает ссылку на поток-поставщик, чтобы ожидать его завершения
    """
    global BUF
    
    supplier_thread.join() # ожидаем завершения создания данных
    print("Handler-thread: start")

    BUF = BUF.lower()
    print("Handler-thread: processed the data")

    print("Handler-thread: end")

def consumer_target(handler_thread, pathname):
    """
    функция для потока потребителя.
    Принимает ссылку на поток-обработчик, чтобы ожидать его завершения
    Принимает название файла, куда будет записана информация
    """
    global BUF

    handler_thread.join() # ожидаем заверения обработки данных
    print("Consumer-thread: start")

    with open(pathname,'w')as f:
        f.write(BUF)
    print("Consumer-thread: wrote data")

    print("Consumer-thread: end")


if __name__ == "__main__":
    res_pathname = './results'

    # объявляем потоки
    supplier_thread = threading.Thread(target=supplier_target, args=())
    handler_thread = threading.Thread(target=handler_target, args=(supplier_thread,))
    consumer_thread = threading.Thread(target=consumer_target, args=(handler_thread,res_pathname))

    # запуск потоков
    supplier_thread.start() 
    handler_thread.start()
    consumer_thread.start()

    # ждем завершения потоков
    supplier_thread.join() 
    handler_thread.join()
    consumer_thread.join()

    
    
    
    