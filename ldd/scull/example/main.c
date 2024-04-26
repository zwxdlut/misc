#include <stdio.h>
#include <string.h>

#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>

#include "../scull.h"

#define DEV "/dev/scull0"
 
int main(int argc, char *argv[])
{
	int fd = open("/dev/scull0", O_RDWR);
	int cmd = 0, quantum = 0;
	char rbuf[100];
	char wbuf[100] = "Hello World!";

	if (fd < 0)
	{
		printf("open %s failed(%d)!\n%s\n", DEV, errno, strerror(errno));
		return -1;
	}

	printf("open %s successed! fd = %d\n", DEV, fd);

	while(1)
	{
		printf("input command(r-read, w-write, o-ioctl, l-lseek, q-quit):");
		cmd = getchar();
		getchar();

		if ('q' == cmd)
		{
			break;
		}
        
		switch (cmd)
		{
			case 'r':
				memset(rbuf, 0, 100);
				read(fd, rbuf, 100);
				printf("read: \n%s\n", rbuf);
				break;

			case 'w':
				printf("write: \n%s\n", wbuf);
				write(fd, wbuf, 100);
				break;

			case 'o':
				if (0 == ioctl(fd, SCULL_IOCGQUANTUM, &quantum))
				{
					printf("ioctl: SCULL_IOCGQUANTUM %d <==\n", quantum);
				}
				else
				{
					printf("ioctl: SCULL_IOCGQUANTUM error %d. %s\n", errno, strerror(errno));
				}
								
				quantum = 2000;
				if (0 == ioctl(fd, SCULL_IOCTQUANTUM, quantum))
				{
					printf("ioctl: SCULL_IOCTQUANTUM %d ==>\n", quantum);
				}
				else
				{
					printf("ioctl: SCULL_IOCTQUANTUM error %d. %s\n", errno, strerror(errno));
				}			

				if (0 == ioctl(fd, SCULL_IOCGQUANTUM, &quantum))
				{
					printf("ioctl: SCULL_IOCGQUANTUM %d <==\n", quantum);
				}
				else
				{
					printf("ioctl: SCULL_IOCGQUANTUM error %d. %s\n", errno, strerror(errno));
				}

				break;

			case 'l':
				lseek(fd, 0, SEEK_SET);
				break;

			default:
				break;
		}

		sleep(1);
	}
	
	close(fd);

	return 0;
}
