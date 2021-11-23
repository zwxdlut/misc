#include <linux/init.h>
#include <linux/module.h>

MODULE_LICENSE("Dual BSD/GPL");

static char *whom = "world";
static int howmany = 1;

module_param(whom, charp, S_IRUGO);
module_param(howmany, int, S_IRUGO);

static int __init hello_init(void)
{
    printk(KERN_ALERT "hello_init: %s %d times\n", whom, howmany);
    return 0;
}

static void __exit hello_exit(void)
{
    printk(KERN_ALERT "hello_exit\n");
}

module_init(hello_init);
module_exit(hello_exit);
