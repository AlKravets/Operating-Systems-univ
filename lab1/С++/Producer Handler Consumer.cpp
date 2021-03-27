#include<iostream>
#include<string>
#include<deque>
#include<thread>
#include<mutex>
#include<unistd.h>
#include<locale>
#include<fstream>

#define BASE_PAUSE 0

using namespace std;

void info(const string & str, int pause = BASE_PAUSE){
    cout << str<< endl;
    sleep(pause);
}


class PHC_machine{
    const int max_buf_size= 5;
    deque<char> buffer;

    bool end_flag = false;

    fstream fs;

    mutex prod_mutex;
    mutex handl_mutex;
    mutex cons_mutex;
public:
    

    PHC_machine(const string & filepath){
        
        fs.open(filepath, fstream::out);
        if (!fs.is_open()){
            cout << "Error"<< endl;
            
        }
        handl_mutex.lock(); // Запираем Handler
        cons_mutex.lock();  // Запираем Consumer
    }

    ~PHC_machine(){
        if (fs.is_open()){
            fs.close();
        }
    }

    void produce(const string & data){
        auto iter = begin(data);
        info("Start Producer");

        while (!end_flag){
            info("Producer before lock (prod_mutex)");
            
            prod_mutex.lock(); // запираем Producer

            info("Producer acquired lock (prod_mutex)");

            while (buffer.size() < max_buf_size && iter != end(data)){
                buffer.push_back(*iter);
                // cout << "Push '" << *iter <<"'\n";
                info("Producer push symbol '" + string(1,*iter) + "' to buffer");
                iter++;
            }

            

            if (iter == end(data)){
                end_flag = true;
                info("Producer created all data. Start ending.");
            }

            handl_mutex.unlock();
            info("Producer unlock Handler`s lock (handl_mutex)"); // Открываем Handler

        }
        info("Producer end");
    }


    void handle(){
        info("Start Handler");

        while (true){
            info("Handler before lock (handl_mutex)");

            handl_mutex.lock(); // Запираем Handler

            info("Handler acquired lock (handl_mutex)");

            const size_t buf_len = buffer.size();
            
            for (int i=0; i< buf_len; ++i){

                char symbol = buffer.front();
                buffer.pop_front();
                
                info("Handler change symbol '" + string(1,symbol) + "' to '" + string(1,tolower(symbol)) + "'");
                buffer.push_back(tolower(symbol));
            }

            // info("Handler ");

            cons_mutex.unlock(); // открываем Consumer

            info("Handler unlock Consumer`s lock (cons_mutex)");

            if (end_flag){
                info("Handler processed all data. Start ending.");
                break;
            }
        }

        info("Handler end");
    }

    void consume(){
       info("Start Consumer");

        while (true){
            info("Consumer before lock (cons_mutex)");

            cons_mutex.lock(); // Запираем Consumer

            info("Consumer acquired lock (cons_mutex)");

            while(!buffer.empty()){
                char symbol = buffer.front();
                buffer.pop_front();
                info("Consumer pop symbol '" + string(1,symbol) + "' from buffer");
                fs << symbol;
            }

            // info("Consumer ");

            prod_mutex.unlock(); // открываем Producer

            info("Consumer unlock Producer`s lock (prod_mutex)");

            if (end_flag){
                info("Consumer read all data. Start ending.");
                break;
            }
        }

        info("Consumer end");

    }

};

// void produce(const string & data){
//     auto iter = begin(data);
//     bool end_flag = false;
//     int buf_size = 5;
//     deque<char> buffer;
//     while (!end_flag){
//         cout << "start\n";

//         while (buffer.size() < buf_size && iter != end(data)){
//             buffer.push_back(*iter);
//             cout << "Push '" << *iter <<"'\n";
//             iter++;
//         }

//         buffer.clear();

//         if (iter == end(data)){
//             end_flag = true;
//         }
//     }

// }

// void handle(){
//     cout << "Hello"<< endl;
//     int buf_size = 5;
//     deque<char> buffer = {'H', 'e', 'L', 'l', 'O'};

//     const size_t buf_len = buffer.size();
//     for (int i=0; i< buf_len; ++i){

//         char symbol = buffer.front();
//         buffer.pop_front();
//         cout << symbol << endl;
//         buffer.push_back(tolower(symbol));
//     }

//     for (const auto item: buffer){
//         cout<< item;
//     }
//     cout << endl;
// }

// void consume(string filepath){
//     deque<char> buffer = {'H', 'e', 'L', 'l', 'O'};
//     fstream fs;
//     fs.open(filepath, fstream::out);
//     if (!fs.is_open()){
//         cout << "Error"<< endl;
//         return;
//     }
//     fs << "Hello world" << endl;

//     for (const auto item: buffer){
//         fs<< item;
//     }

//     fs.close();
// }   




int main(){
    string data = "HelLoWorD";

    // PHC_machine mh = PHC_machine("test.txt");
    PHC_machine * mh = new PHC_machine("test.txt");

    
    thread Producer (&PHC_machine::produce, mh, data);
    thread Handler (&PHC_machine::handle,mh);
    thread Consumer (&PHC_machine::consume,mh);

    Producer.join();
    Handler.join();
    Consumer.join();

    delete mh;
    return 0;
}