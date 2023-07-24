#include <stdio.h>
#include <string.h>
#include <stdlib.h>

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
#include <termios.h>

#include "device.h"

//Linux CAN 编程
//数据发送：
//在数据收发的内容方面，CAN总线与标准套接字通信稍有不同，每一次通信都采用can_frame结
//构体将数据封装成帧。结构体定义如下：
//struct can_frame {
//canid_t can_id;//CAN标识符
//__u8 can_dlc;//数据场的长度
//__u8 data[8];//数据
//};
//can_id为帧的标识符，如果发出的是标准帧，就使用can_id的低11位；如果为扩展帧，就使用0
//～28位。can_id的第29、30、31位是帧的标志位，用来定义帧的类型，定义如下：
//#define CAN_EFF_FLAG 0x80000000U //扩展帧的标识
//#define CAN_RTR_FLAG 0x40000000U //远程帧的标识
//#define CAN_ERR_FLAG 0x20000000U //错误帧的标识，用于错误检查
//数据发送使用write函数来实现。
//发送扩展帧：frame.can_id = CAN_EFF_FLAG | id
//发送远程帧：frame.can_id = CAN_RTR_FLAG | id;
//
//数据接收：
//数据接收使用read函数来完成。
//
//当然，套接字数据收发时常用的send、sendto、sendmsg以及对应的recv函数也都可以用于CAN
//总线数据的收发。
//
//错误处理：
//当帧接收后，可以通过判断can_id中的CAN_ERR_FLAG位来判断接收的帧是否为错误帧。如果
//为错误帧，可以通过can_id的其他符号位来判断错误的具体原因。
//错误帧的符号位在头文件linux/can/error.h中定义。
//
//过滤规则：
//接收到的数据帧的can_id & mask == can_id & mask
//通过这条规则可以在系统中过滤掉所有不符合规则的报文，使得应用程序不需要对无关的报文进行
//处理。在can_filter结构的can_id中，符号位CAN_INV_FILTER在置位时可以实现can_id在执行过
//滤前的位反转。
//用户可以为每个打开的套接字设置多条独立的过滤规则。
//在极端情况下，如果应用程序不需要接收报文，可以禁用过滤规则。这样的话，原始套接字就会忽略所有
//接收到的报文。在这种仅仅发送数据的应用中，可以在内核中省略接收队列，以此减少CPU资源的消耗。禁
//用方法如下：
//setsockopt(s, SOL_CAN_RAW, CAN_RAW_FILTER, NULL, 0); //禁用过滤规则
//通过错误掩码可以实现对错误帧的过滤，例如：
//can_err_mask_t err_mask = ( CAN_ERR_TX_TIMEOUT | CAN_ERR_BUSOFF );
//setsockopt(s, SOL_CAN_RAW, CAN_RAW_ERR_FILTER, err_mask, sizeof(err_mask));
//在默认情况下，本地回环功能是开启的，可以使用下面的方法关闭回环/开启功能：
//int loopback = 0; // 0表示关闭, 1表示开启(默认)
//setsockopt(s, SOL_CAN_RAW, CAN_RAW_LOOPBACK, &loopback, sizeof(loopback));
//在本地回环功能开启的情况下，所有的发送帧都会被回环到与CAN总线接口对应的套接字上。默认情况
//下，发送CAN报文的套接字不想接收自己发送的报文，因此发送套接字上的回环功能是关闭的。可以在
//需要的时候改变这一默认行为：
//int ro = 1; // 0表示关闭(默认), 1表示开启
//setsockopt(s, SOL_CAN_RAW, CAN_RAW_RECV_OWN_MSGS, &ro, sizeof(ro));

/*******************************************************************************
 * Definitions
 ******************************************************************************/

/*******************************************************************************
 * Local function prototypes
 ******************************************************************************/

/*******************************************************************************
 * Functions
 ******************************************************************************/
int32_t can_init(const char _name[], const uint32_t _filter_ids[], const size_t _filter_count)
{
	printf("can_init: %s\n", _name);
		
	int s;
	struct sockaddr_can addr;
	struct ifreq ifr;
	struct can_filter *rfilter;

	s = socket(PF_CAN, SOCK_RAW, CAN_RAW);

	if (-1 == s)
	{
		printf("can_init: create socket failed(%d-%s)!\n", errno, strerror(errno));
		return s;
	}

	printf("can_init: create socket fd %d\n", s);
	strcpy(ifr.ifr_name, _name);

	if (0 != ioctl(s, SIOCGIFINDEX, &ifr))
	{
		printf("can_init: ioctl failed(%d-%s)!\n", errno, strerror(errno));
		return -1;
	}
	
	addr.can_family = AF_CAN;
	addr.can_ifindex = ifr.ifr_ifindex;

	if (0 != bind(s, (struct sockaddr *)&addr, sizeof(addr)))
	{
		printf("can_init: bind failed(%d-%s)!\n", errno, strerror(errno));
		return -1;
	}

	if (NULL != _filter_ids && 0 != _filter_count)
	{
		size_t size = sizeof(struct can_filter) * _filter_count;

		rfilter = malloc(size);

		for (size_t i = 0; i < _filter_count; i++)
		{
			rfilter[i].can_id = _filter_ids[i];
			rfilter[i].can_mask = CAN_SFF_MASK; /* #define CAN_SFF_MASK 0x000007FFU */
		}

		setsockopt(s, SOL_CAN_RAW, CAN_RAW_FILTER, rfilter, size);
		free(rfilter);
	}

	return s;
}

int32_t uart_init(const char _name[], const uint32_t _baudrate, const uint8_t _databits, const char _parity, const uint8_t _stopbits)
{
	printf("uart_init: %s, %d, %d, %c, %d\n", _name, _baudrate, _databits, _parity, _stopbits);

	int fd;

	fd = open(_name, O_RDWR|O_NOCTTY);

	if (-1 == fd)
	{
		printf("uart_init: open failed(%d-%s)!\n", errno, strerror(errno));
		return -1;
	}

	printf("uart_init: open fd %d\n", fd);

	struct termios newtio, oldtio;

	if (0 != tcgetattr(fd, &oldtio)) 
	{ 
		printf("uart_init: get attribute failed(%d-%s)!\n", errno, strerror(errno));
		return -1;
	}

	bzero(&newtio, sizeof(newtio));
	newtio.c_cflag  |=  CLOCAL | CREAD;
	newtio.c_cflag &= ~CSIZE;
 
	switch(_databits)
	{
		case 5:
			newtio.c_cflag |= CS5;
			break;

		case 6:
			newtio.c_cflag |= CS6;
			break;

		case 7:
			newtio.c_cflag |= CS7;
			break;

		case 8:
			newtio.c_cflag |= CS8;
			break;
	}
 
	switch(_parity)
	{
	case 'O':
		newtio.c_cflag |= PARENB;
		newtio.c_cflag |= PARODD;
		newtio.c_iflag |= (INPCK | ISTRIP);
		break;

	case 'E': 
		newtio.c_iflag |= (INPCK | ISTRIP);
		newtio.c_cflag |= PARENB;
		newtio.c_cflag &= ~PARODD;
		break;

	case 'N':  
		newtio.c_cflag &= ~PARENB;
		break;
	}
 
	switch (_baudrate)
	{
		case 2400:
			cfsetispeed(&newtio, B2400);
			cfsetospeed(&newtio, B2400);
			break;

		case 4800:
			cfsetispeed(&newtio, B4800);
			cfsetospeed(&newtio, B4800);
			break;

		case 9600:
			cfsetispeed(&newtio, B9600);
			cfsetospeed(&newtio, B9600);
			break;

		case 19200:
			cfsetispeed(&newtio, B19200);
			cfsetospeed(&newtio, B19200);
			break;

		case 38400:
			cfsetispeed(&newtio, B38400);
			cfsetospeed(&newtio, B38400);
			break;

		case 57600:
			cfsetispeed(&newtio, B57600);
			cfsetospeed(&newtio, B57600);
			break;

		case 115200:
			cfsetispeed(&newtio, B115200);
			cfsetospeed(&newtio, B115200);
			break;

		case 460800:
			cfsetispeed(&newtio, B460800);
			cfsetospeed(&newtio, B460800);
			break;

		default:
			cfsetispeed(&newtio, B115200);
			cfsetospeed(&newtio, B115200);
			break;
	}

	if(1 == _stopbits)
	{
		newtio.c_cflag &=  ~CSTOPB;
	}
	else if (2 == _stopbits)
	{
		newtio.c_cflag |=  CSTOPB;
	}

	newtio.c_cc[VTIME] = 0;
	newtio.c_cc[VMIN] = 0;
	tcflush(fd, TCIFLUSH);

	if(0 != tcsetattr(fd,TCSANOW,&newtio))
	{
		printf("uart_init: set attribute failed(%d-%s)!\n", errno, strerror(errno));
		return -1;
	}
	
	return fd;
}

/*******************************************************************************
 * Local functions
 ******************************************************************************/