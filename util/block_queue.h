#ifndef __BLOCK_QUEUE_H__
#define __BLOCK_QUEUE_H__

#include <queue>
#include <mutex>
#include <condition_variable>
#include <functional>

/**
 * Block queue, thread safety.
 */
template<typename T>
class block_queue : public std::queue<T>
{
public:
    using base = std::queue<T>;

    void put(const T &_t)
    {
        std::lock_guard<std::mutex> lock(mutex_);

        base::push(_t);
        cond_.notify_all();
    }

    T take()
    {
        std::unique_lock<std::mutex> lock(mutex_);

        if (0 == base::size())
        {
            cond_.wait(lock);
        }

        auto ret = base::front();

        base::pop();

        return ret;
    }

    T pull()
    {
        std::unique_lock<std::mutex> lock(mutex_);

        auto ret = base::front();

        base::pop();

        return ret;
    }

    void notify()
    {
        std::lock_guard<std::mutex> lock(mutex_);

        cond_.notify_all();
    }

private:
    std::mutex mutex_;
    std::condition_variable cond_;
};

#endif // __BLOCK_QUEUE_H__
