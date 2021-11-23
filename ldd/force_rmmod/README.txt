#  通过 `modname` 制定待卸载驱动的信息
sudo insmod force_rmmod.ko modname=createoops
#  查看是否加载成功, `exit` 函数是否正常替换
dmesg | tail -l
#  卸载 `createoops` 驱动
sudo rmmod createoops
#  卸载 `force_rmmod` 驱动
sudo rmmod force_rmmod