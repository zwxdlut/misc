#ifndef __SCULL_H__
#define __SCULL_H__

#include <linux/ioctl.h>

/* Device basic information */
#define SCULL_MAJOR         0
#define SCULL_DEV_COUNT     4
#define SCULL_QUANTUM       4000
#define SCULL_QSET          1000

/* define "k" as magic number */
#define SCULL_IOC_MAGIC 'k'

#define SCULL_IOCRESET    	_IO(SCULL_IOC_MAGIC, 0)
#define SCULL_IOCSQUANTUM 	_IOW(SCULL_IOC_MAGIC, 1, int)
#define SCULL_IOCSQSET    	_IOW(SCULL_IOC_MAGIC, 2, int)
#define SCULL_IOCTQUANTUM 	_IO(SCULL_IOC_MAGIC, 3)
#define SCULL_IOCTQSET    	_IO(SCULL_IOC_MAGIC, 4)
#define SCULL_IOCGQUANTUM 	_IOR(SCULL_IOC_MAGIC, 5, int)
#define SCULL_IOCGQSET    	_IOR(SCULL_IOC_MAGIC, 6, int)
#define SCULL_IOCQQUANTUM 	_IO(SCULL_IOC_MAGIC, 7)
#define SCULL_IOCQQSET    	_IO(SCULL_IOC_MAGIC, 8)
#define SCULL_IOCXQUANTUM 	_IOWR(SCULL_IOC_MAGIC, 9, int)
#define SCULL_IOCXQSET    	_IOWR(SCULL_IOC_MAGIC, 10, int)
#define SCULL_IOCHQUANTUM 	_IO(SCULL_IOC_MAGIC, 11)
#define SCULL_IOCHQSET    	_IO(SCULL_IOC_MAGIC, 12)

#define SCULL_IOC_MAXNR 14

#endif /*__SCULL_H__*/
