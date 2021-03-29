using System;
using System.IO;
using System.Text;
using System.Threading;
using System.Collections.Generic;


namespace Lab1{

    class PHC_machine{

        Queue<char> buffer = new Queue<char>();
        int max_buf_size = 5;

        bool end_flag = false;

        StreamWriter sw;

        EventWaitHandle prod_handle = new AutoResetEvent(true); // Сигнальный Handle для Producer
        EventWaitHandle handl_handle = new AutoResetEvent(false);
        EventWaitHandle cons_handle = new AutoResetEvent(false);

        public PHC_machine(string filepath){
            sw = new StreamWriter(filepath, false, System.Text.Encoding.Default);
        }
    

        public void produce(object o_data){
            string data = (string) o_data;
            int data_index = 0;

            Console.WriteLine("Start Producer");
        
            while (!end_flag){

                Console.WriteLine("Producer before lock (prod_handle)");

                prod_handle.WaitOne();// Закрываем Producer

                Console.WriteLine("Producer acquired lock (prod_handle)");

                while (buffer.Count < max_buf_size && data_index != data.Length){
                    buffer.Enqueue(data[data_index]);
                    Console.WriteLine("Producer push '"+data[data_index] + "' to buffer");
                    data_index++;
                }

                if (data_index == data.Length){
                    end_flag = true;
                    Console.WriteLine("Producer created all data. Start ending.");
                }

                Console.WriteLine("Producer unlock Handler`s lock (handl_handle)"); 
                
                handl_handle.Set();

            }

            Console.WriteLine("Producer end");
        }

        public void handle(){
            Console.WriteLine("Start Handler");
            while(true){
                Console.WriteLine("Handler before lock (handl_handle)");

                handl_handle.WaitOne();// Запираем Handler

                Console.WriteLine("Handler acquired lock (handl_handle)");
                int buf_size = buffer.Count;

                for (int i=0; i< buf_size; ++i){
                    char symbol = buffer.Dequeue();
                    buffer.Enqueue(Char.ToLower(symbol));
                    Console.WriteLine("Handler transform '"+ symbol + "'  to '" + Char.ToLower(symbol) + "'");

                }

                Console.WriteLine("Handler unlock Consumer`s lock (cons_handle)");
                
                cons_handle.Set(); // Открываем Consumer

                if (end_flag){
                    Console.WriteLine("Handler processed all data. Start ending.");
                    break;
                }
            }
            Console.WriteLine("Handler end");
        }   

        public void consume(){
            Console.WriteLine("Start Consumer");
            
            while(true){
                
                Console.WriteLine("Consumer before lock (cons_handle)");

                cons_handle.WaitOne(); // Запираем Consumer
                

                Console.WriteLine("Consumer acquired lock (cons_handle)");

                int buf_size = buffer.Count;

                for (int i=0; i< buf_size; ++i){
                    char symbol = buffer.Dequeue();
                    Console.WriteLine("Consumer pop '"+ symbol+ "'");
                    if (sw==null){
                        Console.WriteLine("Error");
                    }
                    else{
                        sw.Write(symbol);
                    }
                }

                Console.WriteLine("Consumer unlock Producer`s lock (prod_handle)");
                
                prod_handle.Set(); // Открываем Producer

                if (end_flag){
                    Console.WriteLine("Consumer processed all data. Start ending.");
                    break;
                }

            }
            Console.WriteLine("Consumer end");
            sw.Close();
        }
    }
    
    class Program{
        
        

        public static void Main (string[] args){
            
            PHC_machine mh = new PHC_machine("test.txt");

            string data = "HeLLO123";

        
            // //Объявляем потоки
            Thread producer_thread = new Thread(new ParameterizedThreadStart(mh.produce));
            Thread handler_thread = new Thread(new ThreadStart(mh.handle));
            Thread consumer_thread = new Thread(new ThreadStart(mh.consume));

            producer_thread.Start(data); // запуск потока создателя данных
            handler_thread.Start(); // запуск потока обработчика данных
            consumer_thread.Start(); // запуск потока читателя данных
            
            
            producer_thread.Join(); // ожидание завершения создания данных
            handler_thread.Join(); // ожидание завершения обработчика данных
            consumer_thread.Join();
        }


    }
}