# !/bin/sh
module="scull"
device="scull"

rm -f /dev/${device}[0-3]
/sbin/rmmod ./$module.ko $* || exit 1
