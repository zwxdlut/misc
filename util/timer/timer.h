#ifndef __TIMER_H__
#define __TIMER_H__

#include <stdint.h>
#include <stdbool.h>

#include <time.h>
#include <signal.h>

/**
 * Timer.
 */
class timer
{
public:
    typedef void (*handler)(void *_param);

    ~timer();

    int32_t start(const uint32_t _period, handler _handler, void *_param = nullptr);
    int32_t stop();
    
private:
    static constexpr const char *TAG = "timer";

    bool stopped = true;
    timer_t timer_;
    handler handler_;
    void *param_ = nullptr;
};

#endif // __TIMER_H__
