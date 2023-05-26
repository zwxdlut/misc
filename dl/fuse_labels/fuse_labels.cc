#include <stdio.h>
#include <stdint.h>

#include <vector>
#include <iostream>
#include <algorithm>
#include <string>

#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/prctl.h>

#include <opencv2/opencv.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>

#define SRC_PATH "/mnt/ext/data/traffic_all/seg/ipm/masks/train/"
#define DST_PATH "/mnt/ext/data/traffic_all/seg/ipm/masks_ll/train/"
#define LL_LABEL_VALUE 1

const std::vector<uint8_t> FUSE_LABLES = {2, 3, 4, 5, 7, 10, 21};

int main(int argc, char *argv[])
{   
    DIR *dir = NULL;
    struct dirent *st = NULL;
    struct stat sta;
    int ret = 0;
    size_t count = 0;
    char src_path[1024] = SRC_PATH;
    char dst_path[1024] = DST_PATH;

    if (1 < argc)
    {
        strcpy(src_path, argv[1]);
    }

    if (2 < argc)
    {
        strcpy(dst_path, argv[2]);
    }

    if (NULL == (dir = opendir(src_path)))
    {
        printf("open dir %s error(%d), %s!\n", src_path, errno, strerror(errno));
        return -1;
    }

    while(NULL != (st = readdir(dir)))
    {
        char src[1024] = {0};

        strcpy(src, src_path);
        if(src_path[strlen(src_path)-1] != '/') strcat(src, "/");
        strcat(src, st->d_name);

        if(0 > (ret = stat(src, &sta)))
        {
            printf("read stat %s error(%d), %s!\n", src, errno, strerror(errno));
            continue;
        }

        if (!S_ISREG(sta.st_mode) || nullptr == strstr(st->d_name, ".png")) // it is not a png file
        {
            continue;
        }

        cv::Mat img_ori = cv::imread(src, cv::IMREAD_GRAYSCALE);

        if (!img_ori.data) 
        {
            printf("image %s no data\n", src);
            continue;
        }

        cv::Mat img(img_ori.rows, img_ori.cols, CV_8UC1, cv::Scalar(0, 0, 0));

        for (size_t k = 0, HW = img.rows * img.cols; k < HW; k++)
        {
            if (FUSE_LABLES.end() != std::find(FUSE_LABLES.begin(), FUSE_LABLES.end(), img_ori.ptr<uint8_t>()[k]))
            {
                img.ptr<uint8_t>()[k] = LL_LABEL_VALUE;
            }
        }

        if (0 != mkdir(dst_path, S_IRUSR | S_IWUSR | S_IXUSR | S_IRWXG | S_IRWXO) 
            && EEXIST != errno)
        {
            printf("mkdir error(%d), %s\n", errno, strerror(errno));
        }

        char dst[1024] = {0};

        strcpy(dst, dst_path);
        if(dst_path[strlen(dst_path)-1] != '/') strcat(dst, "/");
        strcat(dst, st->d_name);
        cv::imwrite(dst, img);
        count++;
        printf("write image %s\n", dst);
    }

    closedir(dir);
    printf("write %ld images\n", count);

    return 0;
}