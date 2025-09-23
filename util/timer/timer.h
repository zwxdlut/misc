#ifndef __TIMER_H__
#define __TIMER_H__

#include <stdint.h>
#include <stdbool.h>

#include <time.h>
#include <signal.h>

/**
 * Timer.
 */
class Timer
{
public:
    typedef void (*handler)(void *_param);

    ~Timer();

    int32_t start(const uint32_t _period, handler _handler, void *_param = nullptr, const bool _immediately = true);

    int32_t stop();
    
private:
    static constexpr const char *TAG = "Timer";

    bool stopped = true;
    timer_t timer_;
    handler handler_;
    void *param_ = nullptr;
};

#endif // __TIMER_H__