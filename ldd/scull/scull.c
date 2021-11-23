#include <linux/init.h>
#include <linux/module.h>
#include <linux/device.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/slab.h>
#include <linux/uaccess.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/sched.h>

#include "scull.h"

MODULE_LICENSE("Dual BSD/GPL");

struct scull_qset
{
    void **data_;
    struct scull_qset *next_;
};

struct scull_dev
{
    struct scull_qset *data_;
    int quantum_;
    int qset_;
    unsigned long size_;
    unsigned int access_key_;
    struct semaphore sem_;
    struct cdev cdev_;
};

static loff_t scull_llseek(struct file* _filp, loff_t _offset, int _whence);
static ssize_t scull_read(struct file *_filp, char __user *_buf, size_t _count, loff_t *_fpos);
static ssize_t scull_write(struct file *_filp, const char __user *_buf, size_t _count, loff_t *_fpos);
static long scull_unlocked_ioctl(struct file *_filp, unsigned int _cmd, unsigned long _arg);
static int scull_open(struct inode *_inode, struct file *_filp);
static int scull_release(struct inode *_inode, struct file *_filp);
static int scull_setup_cdev(struct scull_dev *_dev, int _index);
static int scull_trim(struct scull_dev *_dev);
static struct scull_qset* scull_follow(struct scull_dev *_dev, int _item);

/* The seq_file interfaces */
static void *scull_seq_start(struct seq_file *_s, loff_t *_pos);
static void *scull_seq_next(struct seq_file *_s, void *_v, loff_t *_pos);
static void scull_seq_stop(struct seq_file *_s, void *_v);
static int scull_seq_show(struct seq_file *_s, void *_v);
static int scull_proc_open(struct inode *_inode, struct file *_file);

static int g_scull_major = SCULL_MAJOR;
static int g_scull_nr_devs = SCULL_DEV_COUNT;
static int g_scull_quantum = SCULL_QUANTUM;
static int g_scull_qset = SCULL_QSET;
static struct scull_dev *g_scull_devs = NULL;

static struct file_operations g_scull_fops = 
{
    .owner          = THIS_MODULE,
    .llseek         = scull_llseek,
    .read           = scull_read,
    .write          = scull_write,
    .unlocked_ioctl = scull_unlocked_ioctl,
    .open           = scull_open,
    .release        = scull_release,
};

static struct seq_operations g_scull_seq_ops =
{
    .start = scull_seq_start,
    .next  = scull_seq_next,
    .stop  = scull_seq_stop,
    .show  = scull_seq_show 
};

static struct file_operations g_scull_proc_ops =
{
    .owner   = THIS_MODULE,
    .open    = scull_proc_open,
    .read    = seq_read,
    .llseek  = seq_lseek,
    .release = seq_release
};

module_param(g_scull_major, int, S_IRUGO);
module_param(g_scull_nr_devs, int, S_IRUGO);
module_param(g_scull_quantum, int, S_IRUGO);
module_param(g_scull_qset, int, S_IRUGO);

static int __init scull_init(void)
{
    int ret = 0, i = 0;
    dev_t dev;

    if (0 != g_scull_major)
    {
        dev = MKDEV(g_scull_major, 0);
        ret = register_chrdev_region(dev, g_scull_nr_devs, "scull");
    }
    else
    {
        ret = alloc_chrdev_region(&dev, 0, g_scull_nr_devs, "scull");
        g_scull_major = MAJOR(dev);
    }

    if (0 != ret)
    {
        printk(KERN_ERR "scull_init: can't get major %d, result is %d!\n", g_scull_major, ret);
        return ret;
    }

    printk(KERN_NOTICE "scull_init: g_scull_major = %d, g_scull_nr_devs = %d\n", g_scull_major, g_scull_nr_devs);
    g_scull_devs = kmalloc(sizeof(struct scull_dev) * g_scull_nr_devs, GFP_KERNEL);

    if (NULL == g_scull_devs)
    {
        printk(KERN_ERR "scull_init: kmalloc scull_dev failed!\n");
        return -1;
    }

    memset(g_scull_devs, 0, sizeof(struct scull_dev) * g_scull_nr_devs);

    for (i = 0; i < g_scull_nr_devs; i++)
    {
        g_scull_devs[i].quantum_ = g_scull_quantum;
        g_scull_devs[i].qset_ = g_scull_qset;
        sema_init(&g_scull_devs[i].sem_, 1);
        ret = scull_setup_cdev(g_scull_devs + i, i);

        if (0 != ret)
        {
            printk(KERN_ERR "scull_init: setup cdev(%d) failed(%d)!\n", i, ret);
            return ret;
        }
    }

    proc_create("scullseq", 0, NULL, &g_scull_proc_ops);

    return 0;
}

static void __exit scull_exit(void)
{
    int i = 0;

    printk(KERN_NOTICE "scull_exit: g_scull_major = %d, g_scull_nr_devs = %d\n", g_scull_major, g_scull_nr_devs);
    remove_proc_entry("scullseq", NULL);

    for (i = 0; i < g_scull_nr_devs; i++)
    {
        scull_trim(g_scull_devs + i);
        cdev_del(&g_scull_devs[i].cdev_);
    }

    kfree(g_scull_devs);
    g_scull_devs = NULL; 
    unregister_chrdev_region(MKDEV(g_scull_major, 0), g_scull_nr_devs);
}

static loff_t scull_llseek(struct file* _filp, loff_t _offset, int _whence)
{
    struct scull_dev *dev = _filp->private_data;
	loff_t newpos = 0;

    printk(KERN_NOTICE "scull_llseek: _filp->f_pos = %lld, _offset = %lld, _whence = %d, dev->size_ = %ld\n", _filp->f_pos, _offset, _whence, dev->size_);

	switch (_whence)
    {
		case SEEK_SET:
			newpos = _offset;
			break;

		case SEEK_CUR:
			newpos = _filp->f_pos + _offset;
			break;

		case SEEK_END:
            // TODO: kmalloc memory?
			newpos = dev->size_ + _offset;
			break;
        
		default:
			return -EINVAL;
	}
	
	if(newpos < 0)
    {
		return -EINVAL;
	}

	_filp->f_pos = newpos;

	return newpos;
}

static ssize_t scull_read(struct file *_filp, char __user *_buf, size_t _count, loff_t *_fpos)
{
    struct scull_dev *dev = _filp->private_data;
    struct scull_qset *dptr = NULL;
    int quantum = dev->quantum_, qset = dev->qset_;
    int itemsize = quantum * qset; /* byte size of the link table item */
    int item = 0, s_pos = 0, q_pos = 0, rest = 0;
    ssize_t ret = 0;

    printk(KERN_NOTICE "scull_read: _count = %ld, _fpos = %lld, dev->size_ = %ld\n", _count, *_fpos, dev->size_);

    if (down_interruptible(&dev->sem_))
    {
        return -ERESTARTSYS;
    }
    
    if (*_fpos >= dev->size_)
    {
        goto out;
    }

    if (*_fpos + _count > dev->size_)
    {
        _count = dev->size_ - *_fpos;
    }
        
    /* serach the link table item, qset index and offset in the quantum set */
    item = (long)*_fpos / itemsize;
    rest = (long)*_fpos % itemsize;
    s_pos = rest / quantum;
    q_pos = rest % quantum;

    /* walk forward the link table until the correct location */
    dptr = scull_follow(dev, item);

    if (NULL == dptr || !dptr->data_ || !dptr->data_[s_pos])
    {
        goto out;
    }

    /* read the data from the quantum until the end */
    if (_count > quantum - q_pos)
    {
       _count = quantum - q_pos;
    }
    
    if (copy_to_user(_buf, dptr->data_[s_pos] + q_pos, _count))
    {
        ret = -EFAULT;
        goto out;
    }
    
    *_fpos += _count;
    ret = _count;

out:
    up(&dev->sem_);

    return ret;
}

static ssize_t scull_write(struct file *_filp, const char __user *_buf, size_t _count, loff_t *_fpos)
{
    struct scull_dev *dev = _filp->private_data;
    struct scull_qset *dptr = NULL;
    int quantum = dev->quantum_, qset = dev->qset_;
    int itemsize = quantum * qset;
    int item = 0, s_pos = 0, q_pos = 0, rest = 0;
    ssize_t ret = -ENOMEM;

    printk(KERN_NOTICE "scull_write: _count = %ld, _fpos = %lld, dev->size_ = %ld\n", _count, *_fpos, dev->size_);

    if (down_interruptible(&dev->sem_))
    {
        return -ERESTARTSYS;
    }

    /* serach the link table item, qset index and offset in the quantum set */
    item = (long)*_fpos / itemsize;
    rest = (long)*_fpos % itemsize;
    s_pos = rest / quantum;
    q_pos = rest % quantum;

    /* walk forward the link table until the correct location */
    dptr = scull_follow(dev, item);

    if (NULL == dptr)
    {
        goto out;
    }

    if (!dptr->data_)
    {
        dptr->data_ = kmalloc(qset * sizeof(char *), GFP_KERNEL);

        if (!dptr->data_)
        {
            printk(KERN_NOTICE "scull_write: kmalloc qset failed!\n");
            goto out;
        }
        
        memset(dptr->data_, 0, qset * sizeof(char *));
    }
    
    if (!dptr->data_[s_pos])
    {
        dptr->data_[s_pos] = kmalloc(quantum, GFP_KERNEL);

        if (!dptr->data_[s_pos])
        {
            printk(KERN_NOTICE "scull_write: kmalloc quantum failed!\n");
            goto out;
        }        
    }

    /* write the data to the quantum until the end */
    if (_count > quantum - q_pos)
    {
       _count = quantum - q_pos;
    }

    if (copy_from_user(dptr->data_[s_pos] + q_pos, _buf, _count))
    {
        ret = - EFAULT;
        goto out;
    }

    *_fpos += _count;
    ret = _count;

    /* update file size */
    if (dev->size_  < *_fpos)
    {
        dev->size_ = *_fpos;
    }

out:
    up(&dev->sem_);

    return ret;
}

static long scull_unlocked_ioctl(struct file *_filp, unsigned int _cmd, unsigned long _arg)
{
    int err = 0, tmp = 0;
    int ret = 0;

    printk(KERN_NOTICE "scull_ioctl: _filp->f_pos = %lld, _cmd = %d, _arg = %ld\n", _filp->f_pos, _cmd, _arg);

    /* Extract the type and number field, and reject the fault command. 
       Before call access_ok() return ENOTTY(invalid ioctl). */
    if (SCULL_IOC_MAGIC != _IOC_TYPE(_cmd)) return -ENOTTY;    
    if (SCULL_IOC_MAXNR < _IOC_NR(_cmd)) return -ENOTTY;

    /* "Type" is at the point of user space, but "access_ok" is kernel oriented.
       Thus the concepts of "read" and "write" is opposite. */
    if (_IOC_READ & _IOC_DIR(_cmd))
    {
        err = !access_ok(VERIFY_WRITE, (void __user *)_arg, _IOC_SIZE(_cmd));
    }
    else if (_IOC_WRITE & _IOC_DIR(_cmd))
    {
        err = !access_ok(VERIFY_READ, (void __user *)_arg, _IOC_SIZE(_cmd));
    }
    
    if (0 != err) return -EFAULT;

    switch (_cmd)
    {
    case SCULL_IOCRESET:
        g_scull_quantum = SCULL_QUANTUM;
        g_scull_qset = SCULL_QSET;
        break;

    case SCULL_IOCSQUANTUM:
        if (!capable(CAP_SYS_ADMIN))
        {
            return -EPERM;
        }

        ret = __get_user(g_scull_quantum, (int __user *)_arg);
        break;

    case SCULL_IOCTQUANTUM:
        if (!capable(CAP_SYS_ADMIN))
        {
            return -EPERM;
        }

        g_scull_quantum = _arg;
        break;

    case SCULL_IOCGQUANTUM:
        ret = __put_user(g_scull_quantum, (int __user *)_arg);
        break;

    case SCULL_IOCQQUANTUM:
        return g_scull_quantum;

    case SCULL_IOCXQUANTUM:
        if (!capable(CAP_SYS_ADMIN))
        {
            return -EPERM;
        }

        tmp = g_scull_quantum;
        ret = __get_user(g_scull_quantum, (int __user *)_arg);

        if (0 == ret)
        {
            ret = __put_user(tmp, (int __user *)_arg);
        }
        
        break;

    case SCULL_IOCHQUANTUM:
        if (!capable(CAP_SYS_ADMIN))
        {
            return -EPERM;
        }

        tmp = g_scull_quantum;
        g_scull_quantum = _arg;
        return tmp;

    case SCULL_IOCSQSET:
        if (!capable(CAP_SYS_ADMIN))
        {
            return -EPERM;
        }

        ret = __get_user(g_scull_qset, (int __user *)_arg);
        break;

    case SCULL_IOCTQSET:
        if (!capable(CAP_SYS_ADMIN))
        {
            return -EPERM;
        }

        g_scull_qset = _arg;
        break;

    case SCULL_IOCGQSET:
        ret = __put_user(g_scull_qset, (int __user *)_arg);
        break;

    case SCULL_IOCQQSET:
        return g_scull_qset;

    case SCULL_IOCXQSET:
        if (!capable(CAP_SYS_ADMIN))
        {
            return -EPERM;
        }

        tmp = g_scull_qset;
        ret = __get_user(g_scull_qset, (int __user *)_arg);

        if (0 == ret)
        {
            ret = __put_user(tmp, (int __user *)_arg);
        }
        
        break;

    case SCULL_IOCHQSET:
        if (!capable(CAP_SYS_ADMIN))
        {
            return -EPERM;
        }

        tmp = g_scull_qset;
        g_scull_qset = _arg;
        return tmp;
            
    default:
        return -ENOTTY;
    }

    return ret;
}

static int scull_open(struct inode *_inode, struct file *_filp)
{
    int ret = 0;
    char info[64];
    struct scull_dev *dev = container_of(_inode->i_cdev, struct scull_dev, cdev_);

    printk(KERN_NOTICE "scull_open: /dev/scull%d(%s), _filp->f_pos = %lld, dev->size_ = %ld\n", iminor(_inode), 
        format_dev_t(info, _inode->i_rdev), _filp->f_pos, dev->size_);
    _filp->private_data = dev; /* for other methods */

    /* now trim to 0 if the length of the device if open was write-only */
    if (O_WRONLY == (_filp->f_flags & O_ACCMODE))
    {
        ret = scull_trim(dev);

        if (0 != ret)
        {
            printk(KERN_ERR "scull_open: trim scull failed(%d)!\n", ret);
            return ret;
        }
    }

    return 0;
}

static int scull_release(struct inode *_inode, struct file *_filp)
{
    char info[64];
    struct scull_dev *dev = container_of(_inode->i_cdev, struct scull_dev, cdev_);
    
    printk(KERN_NOTICE "scull_release: /dev/scull%d(%s), _filp->f_pos = %lld, dev->size_ = %ld\n", iminor(_inode), 
        format_dev_t(info, _inode->i_rdev), _filp->f_pos, dev->size_);

    return 0;
}

static int scull_setup_cdev(struct scull_dev *_dev, int _index)
{
    int ret = 0;

    if (NULL == _dev)
    {
        printk(KERN_ERR "scull_setup_cdev: Device(%d) is null!\n", _index);
        return -1;
    }

    printk(KERN_NOTICE "scull_setup_cdev: _index = %d, _dev = %p\n", _index, _dev);
    cdev_init(&_dev->cdev_, &g_scull_fops);
    _dev->cdev_.owner = THIS_MODULE;
    _dev->cdev_.ops = &g_scull_fops;
    ret = cdev_add(&_dev->cdev_, MKDEV(g_scull_major, _index), 1);

    /* fail gracefully if need be */
    if (0 != ret)
    {
        printk(KERN_ERR "scull_setup_cdev: Error %d adding scull!\n", ret);
        return ret;
    }

    return 0;
}

static int scull_trim(struct scull_dev *_dev)
{
    struct scull_qset *next = NULL, *dptr = NULL;
    int qset = 0;
    int i = 0;

    if (NULL == _dev)
    {
        printk(KERN_ERR "scull_trim: Device is null!\n");
        return -1;
    }

    printk(KERN_NOTICE "scull_trim: _dev = %p\n", _dev);
    qset = _dev->qset_;

    for (dptr = _dev->data_; NULL != dptr; dptr = next)
    {
        if (NULL != dptr->data_)
        {
            for (i = 0; i < qset; i++)
            {
                kfree(dptr->data_[i]);
            }

            kfree(dptr->data_);
            dptr->data_ = NULL;
        }

        next = dptr->next_;
        kfree(dptr);        
    }

    _dev->size_ = 0;
    _dev->quantum_ = g_scull_quantum;
    _dev->qset_ = g_scull_qset;
    _dev->data_ = NULL;

    return 0;        
}

static struct scull_qset* scull_follow(struct scull_dev *_dev, int _item)
{
    struct scull_qset *dptr = NULL;
    int i = 0;

    if (NULL == _dev)
    {
        printk(KERN_ERR "scull_follow: Device is null!\n");
        return NULL;
    }

    printk(KERN_NOTICE "scull_follow: _dev = %p, _item = %d\n", _dev, _item);

    if (NULL == _dev->data_)
    {
        _dev->data_ = kmalloc(sizeof(struct scull_qset), GFP_KERNEL);

        if (NULL == _dev->data_)
        {
            printk(KERN_NOTICE "scull_follow: kmalloc scull_qset failed!\n");
            return NULL;
        }
        
        _dev->data_->data_ = NULL;
        _dev->data_->next_ = NULL;
    }

    for (i = 0, dptr = _dev->data_; i < _item; i++, dptr = dptr->next_)
    {
        if (NULL == dptr->next_)
        {
            dptr->next_ = kmalloc(sizeof(struct scull_qset), GFP_KERNEL);

            if (NULL == dptr->next_)
            {
                printk(KERN_NOTICE "scull_follow: kmalloc scull_qset failed!\n");
                return NULL;
            }
            
            dptr->next_->data_ = NULL;
            dptr->next_->next_ = NULL;
        }
    }
    
    return dptr;
}

static void *scull_seq_start(struct seq_file *_s, loff_t *_pos)
{
    if (*_pos >= g_scull_nr_devs)
    {
        return NULL;
    }

    return g_scull_devs + *_pos;   
}

static void *scull_seq_next(struct seq_file *_s, void *_v, loff_t *_pos)
{
    (*_pos)++;

    if (*_pos >= g_scull_nr_devs)
    {
        return NULL;
    }
    
    return g_scull_devs + *_pos;
}

static void scull_seq_stop(struct seq_file *_s, void *_v) {}

static int scull_seq_show(struct seq_file *_s, void *_v)
{
    struct scull_dev *dev = (struct scull_dev *)_v;
    struct scull_qset *d = NULL;
    int i = 0;

    if (down_interruptible(&dev->sem_))
    {
        return -ERESTARTSYS;
    }
    
    seq_printf(_s, "\nDevice %i: qset %i, q %i, sz %li\n", (int)(dev - g_scull_devs), dev->qset_, dev->quantum_, dev->size_);

    for (d = dev->data_; NULL != d; d = d->next_) /* scan the list */
    {
        seq_printf(_s, "    item at %p, qset at %p\n", d, d->data_);

        if (NULL != d->data_ && NULL == d->next_) /* just for the last item */
        {
            for (i = 0; i < dev->qset_; i++)
            {
               if (NULL != d->data_[i])
               {
                   seq_printf(_s, "    % 4i: %8p\n", i, d->data_[i]);
               }
               
            }
        }
    }
    
    up(&dev->sem_);

    return 0;
}

static int scull_proc_open(struct inode *_inode, struct file *_file)
{
    return seq_open(_file, &g_scull_seq_ops);
}

module_init(scull_init);
module_exit(scull_exit);
