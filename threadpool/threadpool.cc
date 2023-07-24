// TODO: 实现1
#include <iostream>
#include <thread>
#include <chrono>
#include <functional>

#include <boost/asio.hpp>

/* 互斥锁 */
std::mutex mutex_iostream;

void my_task(int i)
{
    std::lock_guard<std::mutex> lg(mutex_iostream);
    std::cout.flush();
    std::cout << "[" << std::this_thread::get_id() << "] This is my task " << i << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
    std::cout.flush();
}

int main(int argc, const char *argv[])
{
    /* 定义一个4线程的线程池 */
    boost::asio::thread_pool tp(10);

    /* 将函数投放到线程池 */
    for (int i = 0; i < 10; ++i)
    {
        boost::asio::post(tp, std::bind(&my_task, i));
    }

    /* 将语句块投放到线程池 */
    for (int i = 0; i < 10; ++i)
    {
        boost::asio::post(
            tp,
            [i]()
            {
                std::lock_guard<std::mutex> lg(mutex_iostream);
                std::cout.flush();
                std::cout << "[" << std::this_thread::get_id() << "] This is lambda task " << i << std::endl;
                std::cout.flush();
            });
    }

    /* 退出所有线程 */
    tp.join();

    system("PAUSE");

    return 0;
}

// // TODO: 实现2-post
// // asio_post_dispatch.cpp : 定义控制台应用程序的入口点。
// //
// /*
//     代码使用智能指针控制io_service，使用mutex控制各个进程间的输出互斥。work类维持io_service的生命周期, 然后使用post添加执行任务。
//     在此基础上我们再查看post与dispatch的区别：
//     post 优先将任务排进处理队列，然后返回，任务会在某个时机被完成。
//     dispatch会即时请求io_service去调用指定的任务。
// */
// #include <boost/asio.hpp>
// #include <boost/shared_ptr.hpp>
// #include <boost/thread.hpp>
// #include <boost/thread/mutex.hpp>
// #include <boost/bind.hpp>
// #include <iostream>

// boost::mutex global_stream_lock;

// void WorkerThread(boost::shared_ptr< boost::asio::io_service > io_service)
// {
//     global_stream_lock.lock();
//     std::cout << "[" << boost::this_thread::get_id()
//         << "] Thread Start" << std::endl;
//     global_stream_lock.unlock();

//     io_service->run();

//     global_stream_lock.lock();
//     std::cout << "[" << boost::this_thread::get_id()
//         << "] Thread Finish" << std::endl;
//     global_stream_lock.unlock();
// }

// size_t fib(size_t n)
// {
//     if (n <= 1)
//     {
//         return n;
//     }
//     boost::this_thread::sleep(
//         boost::posix_time::milliseconds(1000)
//         );
//     return fib(n - 1) + fib(n - 2);
// }

// void CalculateFib(size_t n)
// {
//     global_stream_lock.lock();
//     std::cout << "[" << boost::this_thread::get_id()
//         << "] Now calculating fib( " << n << " ) " << std::endl;
//     global_stream_lock.unlock();

//     size_t f = fib(n);

//     global_stream_lock.lock();
//     std::cout << "[" << boost::this_thread::get_id()
//         << "] fib( " << n << " ) = " << f << std::endl;
//     global_stream_lock.unlock();
// }

// int main(int argc, char * argv[])
// {
//     boost::shared_ptr< boost::asio::io_service > io_service(
//         new boost::asio::io_service
//         );
//     boost::shared_ptr< boost::asio::io_service::work > work(
//         new boost::asio::io_service::work(*io_service)
//         );

//     global_stream_lock.lock();
//     std::cout << "[" << boost::this_thread::get_id()
//         << "] The program will exit when all work has finished."
//         << std::endl;
//     global_stream_lock.unlock();

//     boost::thread_group worker_threads;
//     for (int x = 0; x < 2; ++x)
//     {
//         worker_threads.create_thread(
//             boost::bind(&WorkerThread, io_service)
//             );
//     }

//     io_service->post(boost::bind(CalculateFib, 3));
//     io_service->post(boost::bind(CalculateFib, 4));
//     io_service->post(boost::bind(CalculateFib, 5));

//     work.reset();

//     worker_threads.join_all();

//     system("pause");

//     return 0;
// }

// // TODO::实现2-dispatch
// // aiso_dispatch.cpp : 定义控制台应用程序的入口点。
// //
// /*
//     我们可以看到结果是先显示dispatch的结果然后才显示post结果，与预想的是一致的.
// */
// #include <boost/asio.hpp>
// #include <boost/shared_ptr.hpp>
// #include <boost/thread.hpp>
// #include <boost/thread/mutex.hpp>
// #include <boost/bind.hpp>
// #include <iostream>

// boost::mutex global_stream_lock;

// void WorkerThread(boost::shared_ptr<boost::asio::io_service> io_service)
// {
//     global_stream_lock.lock();
//     std::cout << "[" << boost::this_thread::get_id()
//               << "] Thread Start" << std::endl;
//     global_stream_lock.unlock();

//     io_service->run();

//     global_stream_lock.lock();
//     std::cout << "[" << boost::this_thread::get_id()
//               << "] Thread Finish" << std::endl;
//     global_stream_lock.unlock();
// }

// void Dispatch(int x)
// {
//     global_stream_lock.lock();
//     std::cout << "[" << boost::this_thread::get_id() << "] "
//               << __FUNCTION__ << " x = " << x << std::endl;
//     global_stream_lock.unlock();
// }

// void Post(int x)
// {
//     global_stream_lock.lock();
//     std::cout << "[" << boost::this_thread::get_id() << "] "
//               << __FUNCTION__ << " x = " << x << std::endl;
//     global_stream_lock.unlock();
// }

// void Run3(boost::shared_ptr<boost::asio::io_service> io_service)
// {
//     for (int x = 0; x < 3; ++x)
//     {
//         io_service->dispatch(boost::bind(&Dispatch, x * 2));
//         io_service->post(boost::bind(&Post, x * 2 + 1));
//         boost::this_thread::sleep(boost::posix_time::milliseconds(1000));
//     }
// }

// int main(int argc, char *argv[])
// {
//     boost::shared_ptr<boost::asio::io_service> io_service(
//         new boost::asio::io_service);
//     boost::shared_ptr<boost::asio::io_service::work> work(
//         new boost::asio::io_service::work(*io_service));

//     global_stream_lock.lock();
//     std::cout << "[" << boost::this_thread::get_id()
//               << "] The program will exit when all  work has finished." << std::endl;
//     global_stream_lock.unlock();

//     boost::thread_group worker_threads;
//     for (int x = 0; x < 1; ++x)
//     {
//         worker_threads.create_thread(boost::bind(&WorkerThread, io_service));
//     }

//     io_service->post(boost::bind(&Run3, io_service));

//     work.reset();

//     worker_threads.join_all();

//     system("pause");

//     return 0;
// }
