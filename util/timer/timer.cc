#include <string.h>
#include <stdio.h>

#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/ioctl.h>

#include "timer.h"
#include "log.h"

Timer::~Timer()
{
    stop();
}

int32_t Timer::start(const uint32_t _period, handler _handler, void *_param, const bool _immediately)
{
    handler_ = _handler;
    param_ = _param;

    struct sigevent evp;
    memset(&evp, 0, sizeof(struct sigevent));   
    evp.sigev_value.sival_ptr = this;
    evp.sigev_notify = SIGEV_THREAD; 
    evp.sigev_notify_function = [](union sigval _s)
    {
        Timer *p = (Timer*)_s.sival_ptr;

        if (nullptr != p->handler_)
        {
            p->handler_(p->param_);
        } 
    };

    if (0 != timer_create(CLOCK_REALTIME, &evp, &timer_))  
    {  
        LOGE(TAG, "start: timer_create error(%d), %s!\n", errno, strerror(errno));
        return -1;  
    }  

    struct itimerspec ts;
    memset(&ts, 0, sizeof(struct itimerspec));
    ts.it_interval.tv_sec = _period / 1000;
    ts.it_interval.tv_nsec = (_period % 1000) * 1000 * 1000;  
    ts.it_value.tv_sec = _immediately ? 0 : _period / 1000;
    ts.it_value.tv_nsec = _immediately ? 1 : (_period % 1000) * 1000 * 1000; 

    if (0 != timer_settime(timer_, 0, &ts, NULL))  
    {  
        LOGE(TAG, "start: timer_settime error(%d), %s!\n", errno, strerror(errno));
        return -1;
    }

    stopped = false;

    return 0;
}

int32_t Timer::stop()
{
    if (stopped)
    {
       return 0;
    }
    
    if (0 != timer_delete(timer_))
    {
        LOGE(TAG, "stop: timer_delete error(%d), %s\n", errno, strerror(errno));
        return -1;
    }

    return 0;
}
