#ifndef __LOG_H__
#define __LOG_H__

#ifdef ANDROID
    #include <config.h>
    #include <android/log.h>

    #define LOGI(TAG, format, ...) __android_log_print(ANDROID_LOG_INFO, TAG, format, ##__VA_ARGS__);
    #define LOGW(TAG, format, ...) __android_log_print(ANDROID_LOG_WARN, TAG, format, ##__VA_ARGS__);
    #define LOGE(TAG, format, ...) __android_log_print(ANDROID_LOG_ERROR, TAG, format, ##__VA_ARGS__);
    #define LOGD(TAG, format, ...) __android_log_print(ANDROID_LOG_DEBUG, TAG, format, ##__VA_ARGS__);
#else
    #define NONE         "\033[m"
    #define RED          "\033[0;32;31m"
    #define LIGHT_RED    "\033[1;31m"
    #define GREEN        "\033[0;32;32m"
    #define LIGHT_GREEN  "\033[1;32m"
    #define BLUE         "\033[0;32;34m"
    #define LIGHT_BLUE   "\033[1;34m"
    #define DARY_GRAY    "\033[1;30m"
    #define CYAN         "\033[0;36m"
    #define LIGHT_CYAN   "\033[1;36m"
    #define PURPLE       "\033[0;35m"
    #define LIGHT_PURPLE "\033[1;35m"
    #define BROWN        "\033[0;33m"
    #define YELLOW       "\033[1;33m"
    #define LIGHT_GRAY   "\033[0;37m"
    #define WHITE        "\033[1;37m"

    #define LOGI(TAG, format, ...) do {printf(LIGHT_GRAY "[%s] " format NONE, TAG, ##__VA_ARGS__);} while(0)
    #define LOGW(TAG, format, ...) do {printf(YELLOW "[%s] " format NONE, TAG, ##__VA_ARGS__);} while(0)
    #define LOGE(TAG, format, ...) do {printf(LIGHT_RED "[%s] " format NONE, TAG, ##__VA_ARGS__);} while(0)
    #define LOGD(TAG, format, ...) do {printf(LIGHT_CYAN "[%s] " format NONE, TAG, ##__VA_ARGS__);} while(0)
#endif

#endif // __LOG_H__