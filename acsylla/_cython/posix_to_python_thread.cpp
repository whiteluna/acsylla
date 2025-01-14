#include <mutex>
#include <queue>
#include <unistd.h>
#include <iostream>

#include "cassandra.h"


class PosixToPython {
    public:
        PosixToPython(int write_fd);
        ~PosixToPython(void);
        int write_fd;
        std::mutex _queue_mutex;
        std::queue<void *> _queue;
};

PosixToPython::PosixToPython(int fd) {
    write_fd = fd;
};

PosixToPython::~PosixToPython(void){
    //std::cout << "### PosixToPython Destroyed ###" << "\n";
};

class CallbackContainer {
    public:
        CallbackContainer(PosixToPython* h, void* d);
        ~CallbackContainer();
        PosixToPython* handler;
        void* data;
};

CallbackContainer::CallbackContainer(PosixToPython* h, void* d) {
    handler = h;
    data = d;
};

CallbackContainer::~CallbackContainer(void) {
  //std::cout << "*** CallbackContainer Destroyed ***" << "\n";
};

void posix_to_python_callback(CassFuture* cass_future, void* data){
    CallbackContainer* container = (CallbackContainer*)data;
    container->handler->_queue_mutex.lock();
    container->handler->_queue.push(container->data);
    container->handler->_queue_mutex.unlock();
    ssize_t written;
    written = write(container->handler->write_fd, "1", strlen("1"));
    delete container;
}

void posix_to_python_logger_callback(const CassLogMessage* message, void* data){
    PosixToPython* handler = (PosixToPython*)data;
    handler->_queue_mutex.lock();
    handler->_queue.push((void*)message);
    handler->_queue_mutex.unlock();
    ssize_t written;
    written = write(handler->write_fd, "1", strlen("1"));
}
