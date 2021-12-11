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

/*******************************************************************************
 * Definitions
 ******************************************************************************/

/*******************************************************************************
 * Local function prototypes
 ******************************************************************************/

/*******************************************************************************
 * Functions
 ******************************************************************************/
int32_t can_init(const char _name[], const uint32_t _filter[], const uint8_t _count)
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

	if (NULL != _filter && 0 != _count)
	{
		size_t size = sizeof(struct can_filter) * _count;

		rfilter = malloc(size);

		for (uint8_t i = 0; i < _count; i++)
		{
			rfilter[i].can_id = _filter[i];
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