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

def handler_target():
    """
    функция для потока обработчика.
    Принимает ссылку на поток-поставщик, чтобы ожидать его завершения
    """
    global BUF
    
    print("Handler-thread: start")

    BUF = BUF.lower()
    print("Handler-thread: processed the data")

    print("Handler-thread: end")

def consumer_target(pathname):
    """
    функция для потока потребителя.
    Принимает ссылку на поток-обработчик, чтобы ожидать его завершения
    Принимает название файла, куда будет записана информация
    """
    global BUF

    print("Consumer-thread: start")

    with open(pathname,'w')as f:
        f.write(BUF)
    print("Consumer-thread: wrote data")

    print("Consumer-thread: end")


if __name__ == "__main__":
    res_pathname = './results'

    # объявляем потоки
    supplier_thread = threading.Thread(target=supplier_target, args=())
    handler_thread = threading.Thread(target=handler_target, args=())
    consumer_thread = threading.Thread(target=consumer_target, args=(res_pathname,))

    
    supplier_thread.start() # запуск потока
    supplier_thread.join() # ждем завершения потока

    handler_thread.start()
    handler_thread.join()

    consumer_thread.start()
    consumer_thread.join()

    
    
    
    