
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <netdb.h>
#include <arpa/inet.h>

#include "socketlib.h"
#include "log.h"

namespace socketlib
{
    Client::~Client()
    {
        close();
    }

    void Client::set_connect_state_callback(connect_state_callback _callback, void *_param)
    {
        callback_ = _callback;
        param_ = _param;
    }

    int32_t Client::open(const char _addr[], const uint32_t _port, const bool _block)
    {
        // create socket fd
        if (0 > (sockfd_ = socket(AF_INET, SOCK_STREAM, 0)))
        {
            //printf("[socketlib::Client::open] create socket error(%d), %s!\n", errno, strerror(errno));
            LOGE(TAG, "open: create socket error(%d), %s!\n", errno, strerror(errno));
            return -1;
        }

        struct sockaddr_in addr;

        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_port = htons(_port);

        if (0 >= inet_pton(AF_INET, _addr, &addr.sin_addr))
        {
            //printf("[socketlib::Client::open] inet_pton error for %s:%d!\n", _addr, _port);
            LOGE(TAG, "open: inet_pton error for %s:%d!\n", _addr, _port);
            return -1;
        }

#if 0
        // keepalive
        int value = 1;
        setsockopt(sockfd_, SOL_SOCKET, SO_KEEPALIVE, &value,  sizeof(value));
        value = 10;
        setsockopt(sockfd_, SOL_TCP, TCP_KEEPIDLE, &value,  sizeof(value));
        value = 5;
        setsockopt(sockfd_, SOL_TCP, TCP_KEEPINTVL, &value,  sizeof(value));
        value = 3;
        setsockopt(sockfd_, SOL_TCP, TCP_KEEPCNT, &value,  sizeof(value));
#endif

        // connect
        if (0 != ::connect(sockfd_, (struct sockaddr*)&addr, sizeof(addr)))
        {
            //printf("[socketlib::Client::open] connect error(%d), %s!\n", errno, strerror(errno));
            LOGE(TAG, "open: connect error(%d), %s!\n", errno, strerror(errno));
            return -1;
        }

        // non-block
        if (!_block)
        {
            int flags = fcntl(sockfd_, F_GETFL, 0); 
            fcntl(sockfd_, F_SETFL, flags | O_NONBLOCK);
        }

        // listen state
        // 1 - use thread mode for listen
        // done_ = false;
        // thread_ = std::thread([this](){listen();});

        // 2 - use timer for listen
        struct sigevent evp;
        memset(&evp, 0, sizeof(struct sigevent));   
        evp.sigev_value.sival_ptr = this;
        evp.sigev_notify = SIGEV_THREAD; 
        evp.sigev_notify_function = [](union sigval _s)
        {
            ((Client*)_s.sival_ptr)->listen();
        };

        if (0 != timer_create(CLOCK_REALTIME, &evp, &timer_))  
        {  
            //printf("[socketlib::Client::open] timer_create error(%d), %s!\n", errno, strerror(errno));
            LOGE(TAG, "open: timer_create error(%d), %s!\n", errno, strerror(errno));
            return -1;  
        }  

        struct itimerspec ts;
        ts.it_interval.tv_sec = 5;
        ts.it_interval.tv_nsec = 0;  
        ts.it_value.tv_sec = 0;
        ts.it_value.tv_nsec = 1;  

        if (0 != timer_settime(timer_, 0, &ts, NULL))  
        {  
            //printf("[socketlib::Client::open] timer_create error(%d), %s!\n", errno, strerror(errno));
            LOGE(TAG, "open: timer_create error(%d), %s!\n", errno, strerror(errno));
            return -1;
        }

        return 0;
    }

    ssize_t Client::recv(void *_buf, size_t _size)
    {
        ssize_t size = 0;

        size = ::recv(sockfd_, _buf, _size, 0);

        if (0 == size)
        {
            //printf("[socketlib::Client::receive]: receive error(%d), %s!\n", errno, strerror(errno));
            LOGE(TAG, "recv: remote shutdown, error(%d), %s!\n", errno, strerror(errno));
        }
        else if(0 > size) 
        {  
            //printf("[socketlib::Client::receive]: receive error(%d), %s!\n", errno, strerror(errno));
            LOGE(TAG, "recv: receive error(%d), %s!\n", errno, strerror(errno));
        }

        return size;
    }

    ssize_t Client::send(const void *_buf, size_t _size)
    {
        ssize_t size = 0;

        size = ::send(sockfd_, _buf, _size, 0);

        if (0 > size)
        {
            //printf("[socketlib::Client::send] send error(%d), %s!\n", errno, strerror(errno));
            LOGE(TAG, "send: send error(%d), %s!\n", errno, strerror(errno));
        }  

        return size;
    }

    int32_t Client::close()
    {
        if (CLOSED == state_)
        {
            return 0;
        }
        
        if (0 != timer_delete(timer_))
        {
            //printf("[socketlib::Client::close] timer_delete error(%d), %s!\n", errno, strerror(errno));
            LOGE(TAG, "close: timer_delete error(%d), %s!\n", errno, strerror(errno));
        }

        // done_ = true;
        // thread_.join();

        if (0 != shutdown(sockfd_, SHUT_RDWR))
        {
            //printf("[socketlib::Client::close] shutdown error(%d), %s!\n", errno, strerror(errno));
            LOGE(TAG, "close: shutdown error(%d), %s!\n", errno, strerror(errno));
        }

        if (0 != ::close(sockfd_))
        {
            //printf("[socketlib::Client::close] close error(%d), %s!\n", errno, strerror(errno));
            LOGE(TAG, "close: close error(%d), %s!\n", errno, strerror(errno));
        }

        state_ = CLOSED;

        return 0;
    }

    void Client::listen()  
    {
        LOGD(TAG, "listen\n");
        // while (!done_)
        // {
            struct tcp_info info; 
            int len = sizeof(info);
            ConnectState state;

            getsockopt(sockfd_, IPPROTO_TCP, TCP_INFO, &info, (socklen_t *)&len);
            //printf("[Client::listen] tcp state %d\n", info.tcpi_state);
            //LOGD(TAG, "listen: tcp state %d\n", info.tcpi_state);

            // check valid state
            if (TCP_CLOSING >= info.tcpi_state && 0 <= info.tcpi_state)
            {
                if (TCP_ESTABLISHED == info.tcpi_state)
                {
                    state = CONNECTED;
                }
                else
                {
                    state = LOST;
                }
            }
            else
            {
                // TODO: why return invalid value?
                if (CLOSED == state_) // first time after open
                {
                    state = CONNECTED;
                }
                else
                {
                    //continue;
                    return;
                }
            }
            
            if (state != state_ && nullptr != callback_)
            {
                state_ = state;
                callback_(state_, param_);

                // std::thread t([=]()
                // {
                //     callback_(*this, state_);
                // });

                // t.detach();
            }

        //     std::this_thread::sleep_for(std::chrono::milliseconds(5000));          
        // }  
    }
}