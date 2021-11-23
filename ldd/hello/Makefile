MODULE_NAME := hello
#MODCFLAGS:=-O2 -Wall -DMODULE -D__KERNEL__ -DLINUX -std=c99
#EXTRA_CFLAGS  += $(MODULE_FLAGS) $(CFG_INC) $(CFG_INC)
EXTRA_CFLAGS  += -g -std=gnu99  -Wfatal-errors 

ifneq ($(KERNELRELEASE),)
	obj-m := $(MODULE_NAME).o
else
	KERNELDIR ?= /lib/modules/$(shell uname -r)/build
	PWD := $(shell pwd)

modules:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) modules

modules_install:
	make -C $(KERNELDIR) M=$(PWD) modules_install

clean:
	make -C $(KERNELDIR) M=$(PWD) clean
	rm -f modules.order Module.symvers Module.markers

.PHNOY:
	modules modules_install clean
endif