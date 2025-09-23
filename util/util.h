#ifndef __UTIL_H__
#define __UTIL_H__

#include <chrono>
#include <iostream>

// 获取当前UTC毫秒时间戳
inline uint64_t get_utc_timestamp_ms() 
{
    auto now = std::chrono::system_clock::now();
    return std::chrono::duration_cast<std::chrono::milliseconds>(
        now.time_since_epoch()
    ).count();
}

#endif // __UTIL_H__