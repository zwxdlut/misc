#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <iostream>
#include <ctime>
#include <iomanip>
#include <thread>
#include <chrono>

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <fcntl.h>
#include <unistd.h> 
#include <errno.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <linux/can/error.h>

#include "device.h"

/*******************************************************************************
 * Definitions
 ******************************************************************************/
#define CAN_DEV_NAME  "can0"
#define UART_DEV_NAME "/dev/ttyS7"

/*******************************************************************************
 * Local function prototypes
 ******************************************************************************/
/** 
 * @name Threads
 * @{
 */
static void can_receive_thread(int32_t _canfd);
static void uart_receive_thread(int32_t _uartfd);
/** @} */ // Threads

static void print_buf(const char *_prefix, const uint32_t _id, const uint8_t _buf[], const uint16_t _size);

/*******************************************************************************
 * Functions
 ******************************************************************************/
int main(int argc, char *argv[])
{
	auto now = std::chrono::system_clock::now();
	auto t_c = std::chrono::system_clock::to_time_t(now);
    std::cout << "local: " 
    		  << std::put_time(std::localtime(&t_c), "%F %T %Z") 
    		  << std::endl;
    std::cout << "timestamp: " 
    		  << std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count() 
    		  << std::endl;

	// initialize the devices
	uint32_t can_filter[] = {0x328, 0x118, 0x15};
	int32_t canfd = can_init(CAN_DEV_NAME, can_filter, sizeof(can_filter) / sizeof(uint32_t));
	int32_t uartfd = uart_init(UART_DEV_NAME, 115200, 8, 'N', 1);

	// create worker threads
	std::thread t1(can_receive_thread, canfd);
	std::thread t2(uart_receive_thread, uartfd);

	// infinite loop
	while (1) {}

	// de-initialize
	t1.join();
	t2.join();
	close(canfd);
	close(uartfd);

	return 0;
}

/*******************************************************************************
 * Local functions
 ******************************************************************************/
void can_receive_thread(int32_t _canfd)
{
	if (-1 == _canfd)
	{
		printf("can_receive_thread: Invalid CAN fd, exit!\n");
		return;
	}

	struct can_frame frame;
	ssize_t size = 0;

	while (1)
	{
		size = read(_canfd, &frame, sizeof(frame));

		if (0 > size)
		{
			printf("can_receive_thread: read error(%d-%s)\n", errno, strerror(errno));
			continue;
		}
		else if (0 == size)
		{
			continue;
		}

		print_buf("CAN-RX: ", frame.can_id, frame.data, frame.can_dlc);
		size = write(_canfd, &frame, sizeof(frame));

		if (size != sizeof(frame))
		{
			printf("can_receive_thread: write error(%d-%s)\n", errno, strerror(errno));
		}
	}

#if 0
	struct can_frame frame;
	frame.can_id = 0x123;//如果为扩展帧，那么 frame.can_id = CAN_EFF_FLAG | 0x123;
	frame.can_dlc = 7; //数据长度为 1
	frame.data[0] = 0xAA; //数据内容为 0xAB
	frame.data[6] = 0xBB; //数据内容为 0xAB
	int nbytes = write(_canfd, &frame, sizeof(frame)); //发送数据

	if (nbytes != sizeof(frame)) //如果 nbytes 不等于帧长度，就说明发送失败
	{
		printf("send error!\n");
	}

	printf("send %d bytes!\n", nbytes);
#endif
}

void uart_receive_thread(int32_t _uartfd)
{
	if (-1 == _uartfd)
	{
		printf("can_receive_thread: Invalid UART fd, exit!\n");
		return;
	}

	uint8_t buf[512];
	ssize_t size = 0;

	while (1)
	{
		size = read(_uartfd, buf, sizeof(buf));

		if (0 > size)
		{
			printf("uart_receive_thread: read error(%d-%s)\n", errno, strerror(errno));
			continue;
		}
		else if (0 == size)
		{
			continue;
		}

		print_buf("UART-RX: ", _uartfd, buf, size);
		ssize_t nbytes = write(_uartfd, buf, size);

		if (nbytes != size)
		{
			printf("can_receive_thread: write error(%d-%s)\n", errno, strerror(errno));
		}
	}
}

void print_buf(const char *_prefix, const uint32_t _id, const uint8_t _buf[], const uint16_t _size)
{
#if defined _UDEBUG
	char info[1000] = "";
	char s[10] = "";

	sprintf(info, "%s(0x%X,%d): ", _prefix, (unsigned int)_id, _size);

	for (uint16_t i = 0; i < _size; i++)
	{
		sprintf(s, "%02X ", _buf[i]);
		strcat(info, s);
	}

	strcat(info, "\n");
	printf("%s", info);
#endif
}