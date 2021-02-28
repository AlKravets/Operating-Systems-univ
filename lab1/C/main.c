#include <pthread.h>
#include <stdio.h>
#include<stdlib.h>
#include <string.h>

// буфер обмена данными между потоками
char *BUF;

// функция, которую выполняет поток поставщик данных
// должен получать строку(ASCII), которую запишет в BUF
void *supplier_start(void *text_string){
    printf("Supplier-thread: start\n");

    if (text_string == NULL){
        // Запись тестовой строки в BUF
        char *test_str = "Some TEST StrIng.1234#$^P*";

        // printf("%ld\n", strlen(test_str));
        BUF = malloc(strlen(test_str)*sizeof(char));
        strcpy(BUF, test_str);
        

    }
    else{
        BUF = malloc(sizeof(text_string));
        strcpy(BUF, (char *)text_string);
    }
    printf("Supplier-thread: fill buffer\n");

    printf("Supplier-thread: end\n");    
}

// функция, которую выполняет поток обработчик данных
// Не должен получать ничего
void *handler_start(void *params){
    printf("Handler-thread: start\n");

    int n = strlen(BUF);

    // работает только для ASCII
    for (int i =0; i< n; ++i){
        if ((int)BUF[i] < 91 && (int)BUF[i] > 64){
            BUF[i] = (char)((int)BUF[i] + 32);
        }
    }

    printf("Handler-thread: processed the data\n");

    printf("Handler-thread: end\n");
}

// функция, которую выполняет поток потребитель данных
// Получает строку с путем к файлу, куда запишет BUF
void *consumer_start(void *pathname){
    printf("Consumer-thread: start\n");

    FILE *res;
    res = fopen((char *)pathname,"w+" );
    fprintf(res, "%s", BUF);
    fclose(res);

    printf("Consumer-thread: wrote data\n");

    printf("Consumer-thread: end\n");
}

int main(){

    char *path = "./results";

    pthread_t supplier_tid; // идентификатор потока
    pthread_attr_t supplier_attr; // атрибуты потока    
    pthread_attr_init(&supplier_attr); // получаем дефолтные значения атрибутов


    pthread_t handler_tid;
    pthread_attr_t handler_attr;
    pthread_attr_init(&handler_attr);


    pthread_t consumer_tid;
    pthread_attr_t consumer_attr;    
    pthread_attr_init(&consumer_attr);

    pthread_create(&supplier_tid,&supplier_attr,supplier_start,NULL); // создаем новый поток
    pthread_join(supplier_tid,NULL); //ждем завершения исполнения потока

    pthread_create(&handler_tid,&handler_attr,handler_start,NULL); 
    pthread_join(handler_tid,NULL);

    pthread_create(&consumer_tid,&consumer_attr,consumer_start,path);
    pthread_join(supplier_tid,NULL);
    
    
    free(BUF);
    return 0;
}