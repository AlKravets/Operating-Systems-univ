using System;
using System.IO;
using System.Text;
using System.Threading;


namespace Lab1{

    
    
    class MainClass{
        //Буфер обмена данными для потоков
        static string BUF;
        

        public static void Main (string[] args){
            
            string path ="./results";
            
            //Объявляем потоки
            Thread supplier_thread = new Thread(new ParameterizedThreadStart(supplier_func));
            Thread handler_thread = new Thread(new ThreadStart(handler_func));
            Thread consumer_thread = new Thread(new ParameterizedThreadStart(consumer_func));

            supplier_thread.Start(); // запуск потока создателя данных
            supplier_thread.Join(); // ожидание завершения создания данных

            handler_thread.Start(); // запуск потока обработчика данных
            handler_thread.Join(); // ожидание завершения обработчика данных

            consumer_thread.Start(path); // запуск потока читателя данных
            consumer_thread.Join();


        }
        //функция для потока поставщика
        static void supplier_func(object text_str = null){

            Console.WriteLine("Supplier-thread: start");

            if (text_str == null){
                string test_str = "Some TEST StrIng.1234#$%^";
                BUF = String.Copy(test_str);
            } else{
                string Text_str = (string)text_str;
                BUF = String.Copy(Text_str);
            }           
            Console.WriteLine("Supplier-thread: fill buffer");

            Console.WriteLine("Supplier-thread: end");
        }


        //функция для потока обработчика.
        static void handler_func (){
            Console.WriteLine("Handler-thread: start");

            BUF = BUF.ToLower();
            Console.WriteLine("Handler-thread: processed the data");

            Console.WriteLine("Handler-thread: end");
        }
        
        //функция для потока потребителя.
        static void consumer_func (object pathname){
            string Pathname = (string) pathname;
            Console.WriteLine("Consumer-thread: start");


            FileStream fstream = null;
            try
            {
                fstream = new FileStream(Pathname, FileMode.OpenOrCreate);
                byte[] input = Encoding.Default.GetBytes(BUF);
                // запись массива байтов в файл
                fstream.Write(input, 0, input.Length);
            }
            catch(Exception ex)
            {
                Console.WriteLine($"Error with file: {ex}");
            }
            finally
            {
                if (fstream != null)
                    fstream.Close();
            }
            Console.WriteLine("Consumer-thread: wrote data");

            Console.WriteLine("Consumer-thread: end");
        }


    }
}