#include <stdio.h>
#include <stdint.h>

#include <vector>
#include <map>
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

#define IMG_DIR "/mnt/ext/data/traffic/traffic/masks/train/"
#define OUT_DIR "/mnt/ext/data/traffic/traffic/fixed_masks/train/"

// // bdd100k lane
// #define BACKGROUND 12
// const std::map<uint8_t, uint8_t> kLABLE_MAP = 
// {  
//     {2,   0},  // 平行双白实线 
//     {3,   1},  // 平行双黄实线
//     {4,   2},  // 路缘石
//     {6,   3},  // 平行单白实线
//     {7,   4},  // 平行单黄实线
//     {18,  5},  // 平行双白虚线
//     {19,  6},  // 平行双黄虚线
//     {22,  7},  // 平行单白虚线
//     {23,  8},  // 平行单黄虚线
//     {38,  9},  // 垂直单白实线
//     {39, 10},  // 垂直单黄实线
//     {48, 11},  // 人行横道
// };

// traffic lane
#define BACKGROUND 0
const std::map<uint8_t, uint8_t> kLABLE_MAP = 
{  
    {2,   1},  // 实线 
    {3,   2},  // 虚线
    {4,   3},  // 停止线
    {7,   4},  // 人行横道
    {10,  2},  // 纵向减速标线
    {13,  5},  // 路缘石
};

int main(int argc, char *argv[])
{   
    DIR *dir = NULL;
    struct dirent *st = NULL;
    struct stat sta;
    int ret = 0;
    size_t count = 0;
    char img_dir[1024] = IMG_DIR;
    char out_dir[1024] = OUT_DIR;

    if (1 < argc)
    {
        strcpy(img_dir, argv[1]);
    }

    if (2 < argc)
    {
        strcpy(out_dir, argv[2]);
    }

    if (NULL == (dir = opendir(img_dir)))
    {
        printf("open dir %s error(%d), %s!\n", img_dir, errno, strerror(errno));
        return -1;
    }

    while(NULL != (st = readdir(dir)))
    {
        char path[1024] = {0};

        strcpy(path, img_dir);
        if(img_dir[strlen(img_dir)-1] != '/') strcat(path, "/");
        strcat(path, st->d_name);

        if(0 > (ret = stat(path, &sta)))
        {
            printf("read stat %s error(%d), %s!\n", path, errno, strerror(errno));
            continue;
        }

        if (!S_ISREG(sta.st_mode) || nullptr == strstr(st->d_name, ".png")) // it is not a png file
        {
            continue;
        }

        cv::Mat img_ori = cv::imread(path, cv::IMREAD_GRAYSCALE);

        if (!img_ori.data) 
        {
            printf("image %s no data\n", path);
            continue;
        }

        cv::Mat img(img_ori.rows, img_ori.cols, CV_8UC1, cv::Scalar(BACKGROUND, BACKGROUND, BACKGROUND));

        for (size_t k = 0, HW = img.rows * img.cols; k < HW; k++)
        {
            auto iter = kLABLE_MAP.find(img_ori.ptr<uint8_t>()[k]);
    
            if (kLABLE_MAP.end() != iter)
            {
                img.ptr<uint8_t>()[k] = iter->second;
            }
        }

        if (0 != mkdir(out_dir, S_IRUSR | S_IWUSR | S_IXUSR | S_IRWXG | S_IRWXO) 
            && EEXIST != errno)
        {
            printf("mkdir error(%d), %s\n", errno, strerror(errno));
        }

        strcpy(path, out_dir);
        if(out_dir[strlen(out_dir)-1] != '/') strcat(path, "/");
        strcat(path, st->d_name);
        cv::imwrite(path, img);
        count++;
        printf("write image %s\n", path);
    }

    closedir(dir);
    printf("write %ld images\n", count);

    return 0;
}
