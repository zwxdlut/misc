#ifndef __SOCK_CLIENT_H__
#define __SOCK_CLIENT_H__

#include <thread>

#include <stdint.h>
#include <stdbool.h>

#include <sys/types.h>
#include <time.h>
#include <signal.h>

namespace sock
{
    /**
     * Socket connect state.
     */
    enum connect_state
    {
        closed = 0,
        connected = 1, 
        lost = 2,
    };

    typedef void (*connect_state_callback)(const connect_state _state, void *_param);
    
    /**
     * Socket client.
     */
    class client
    {
    public:
        ~client();

        void set_connect_state_callback(connect_state_callback _callback, void *_param);

        int32_t open(const char _addr[], const uint32_t _port, const bool _block = true);

        ssize_t recv(void *_buf, size_t _size);

        ssize_t send(const void *_buf, size_t _size);

        int32_t close();

    private:
        void listen();

        static constexpr const char *TAG = "sock::client";

        int sockfd_;
        connect_state state_ = closed;
        // bool done_ = true;
        // std::thread thread_;
        timer_t timer_;
        connect_state_callback callback_ = nullptr;
        void *param_ = nullptr;
    };
}

#endif // __SOCK_CLIENT_H__