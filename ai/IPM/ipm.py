import os
import sys
import cv2

import numpy as np
from numpy.linalg import solve


class IPM():
    def __init__(self, cfg):
        # 参数
        self.image_height, self.image_width = cfg["image_height"], cfg["image_width"]
        self.vanish_line = cfg["vanish_line"]
        self.world_width, self.world_height = cfg["world_width"], cfg["world_height"]
        self.world_pixel = cfg["world_pixel"]
        self.world_y_start = cfg["world_y_start"]
        self.distort = np.array(cfg["distort"])
        self.K = np.array([cfg["intrinsic"][0], 0.0, cfg["intrinsic"][2], 
                           0.0, cfg["intrinsic"][1], cfg["intrinsic"][3], 
                           0.0, 0.0, 1.0]).reshape(3,3)
        self.Rcw = np.array(cfg["Rcw"]).reshape(3,3)
        self.tcw = np.array(cfg["tcw"]).reshape(3,1)
    
        # 读入文件夹下所有图片
        os.makedirs(cfg["image_dir"], exist_ok=True)
        self.image_dir = cfg["image_dir"]

        # 输出文件路径
        os.makedirs(cfg["output_dir"], exist_ok=True)
        self.output_dir = cfg["output_dir"]

        # 计算俯视图大小
        self.ipm_width = int(self.world_width / self.world_pixel)
        self.ipm_height = int(self.world_height / self.world_pixel)
        self.resize = cfg["resize"]

        # 计算去畸变映射
        self.undistort_map1, self.undistort_map2 = self.get_undistort_map()

        # 计算点云
        self.point_cloud = self.get_point_cloud()

        # 计算俯视图到透视图的像素映射
        self.ipm_map, self.ipm_mask = self.get_ipm_map()

    def pair(self, ipm_width, ipm_height):
        for r in range(ipm_height):
            for c in range(ipm_width):
                yield r,c

    def calc_ccs_xy_by_uv(self, uv):
        p_uv = np.append(np.array(uv),1)
        p_cn = np.linalg.inv(self.K) @ p_uv
        # AX=b
        A00 = self.Rcw[2,0] * p_cn[0] - self.Rcw[0,0]
        A01 = self.Rcw[2,1] * p_cn[0] - self.Rcw[0,1]
        A10 = self.Rcw[2,0] * p_cn[1] - self.Rcw[1,0]
        A11 = self.Rcw[2,1] * p_cn[1] - self.Rcw[1,1]
        b0 = self.tcw[0] - self.tcw[2] * p_cn[0]
        b1 = self.tcw[1] - self.tcw[2] * p_cn[1]
        A = np.asmatrix([[A00,A01],[A10,A11]])
        b = np.asmatrix([b0,b1])
        X = solve(A,b)

        return X.A  # numpy.ndarray [2,1]

    def calc_uv_by_ccs_xy(self, pt_ccs):
        pt_ocs = self.Rcw @ pt_ccs + self.tcw.reshape(3)
        pt_ocs = pt_ocs / pt_ocs[2]
        pt_uv = self.K @ pt_ocs

        return (pt_uv + 0.5).astype(np.int32)

    def get_ipm_rect(self):
        # 对应960x540的投影区域
        uv_lu = [0,309]
        uv_ru = [self.image_width-1,309]
        uv_lb = [0,433]
        uv_rb = [self.image_width-1,433]

        ccs_lb = self.calc_ccs_xy_by_uv(uv_lb)
        ccs_rb = self.calc_ccs_xy_by_uv(uv_rb)
        try:
            assert((-self.world_width/2.0<ccs_lb[0,0]<ccs_rb[0,0]<self.world_width/2.0) and (0<ccs_lb[1,0]<self.world_height) and (0<ccs_rb[1,0]<self.world_height))
        except:
            print("Error: world_width is too big.")
            sys.exit(1)

        ccs_lu = self.calc_ccs_xy_by_uv(uv_lu)
        ccs_ru = self.calc_ccs_xy_by_uv(uv_ru)
        
        if ((ccs_lu[0,0]<-self.world_width/2.0) or (ccs_lu[1,0]>self.world_height)):
            ccs_lu = np.array([max(ccs_lu[0,0],-self.world_width/2.0), min(ccs_lu[1,0],self.world_height), 0])
            uv_lu = self.calc_uv_by_ccs_xy(ccs_lu).tolist()[:2]
            if (uv_lu[0]<0):
                uv_lu[0] = 0
            if (uv_lu[1]<self.vanish_line):
                uv_lu[1] = self.vanish_line
            ccs_lu = self.calc_ccs_xy_by_uv(uv_lu)

        if ((ccs_ru[0,0]>self.world_width/2.0) or (ccs_ru[1,0]>self.world_height)):
            ccs_ru = np.array([min(ccs_ru[0,0],self.world_width/2.0), min(ccs_ru[1,0],self.world_height), 0])
            uv_ru = self.calc_uv_by_ccs_xy(ccs_ru).tolist()[:2]
            if (uv_ru[0]>=self.image_width):
                uv_ru[0] = self.image_width-1
            if (uv_ru[1]<self.vanish_line):
                uv_ru[1] = self.vanish_line
            ccs_ru = self.calc_ccs_xy_by_uv(uv_ru)

        ipm_lu = [max(0, int((ccs_lu[0,0]+self.world_width/2.0)/self.world_pixel)), max(0, self.ipm_height-1-int(ccs_lu[1,0]/self.world_pixel))]
        ipm_ru = [min(self.ipm_width-1, int((ccs_ru[0,0]+self.world_width/2.0)/self.world_pixel)), max(0, self.ipm_height-1-int(ccs_ru[1,0]/self.world_pixel))]
        ipm_lb = [max(0, int((ccs_lb[0,0]+self.world_width/2.0)/self.world_pixel)), min(self.ipm_height-1, self.ipm_height-1-int(ccs_lb[1,0]/self.world_pixel))]
        ipm_rb = [min(self.ipm_width-1, int((ccs_rb[0,0]+self.world_width/2.0)/self.world_pixel)), min(self.ipm_height-1, self.ipm_height-1-int(ccs_rb[1,0]/self.world_pixel))]

        uv_list = [uv_lu, uv_ru, uv_lb, uv_rb]
        ipm_list = [ipm_lu, ipm_ru, ipm_lb, ipm_rb]

        uv_array = np.array(uv_list, dtype=np.float32)
        ipm_array = np.array(ipm_list, dtype=np.float32)

        return uv_array, ipm_array

    def get_undistort_map(self):
        camera_matrix = self.K.astype(np.float32)
        dist_coeffs = self.distort.astype(np.float32)
        map1, map2 = cv2.initUndistortRectifyMap(camera_matrix, dist_coeffs, None, camera_matrix, (self.image_width, self.image_height), cv2.CV_32FC1)

        return map1, map2

    def get_point_cloud(self):
        # perspective image to camera(normalized)
        vs, us = np.indices((self.image_height, self.image_width))
        coords = np.column_stack((us.ravel(), vs.ravel(), np.ones(self.image_height * self.image_width)))
        # coords = np.linalg.inv(self.K) @ coords.transpose()
        xs = (coords[:, 0] - self.K[0, 2]) / self.K[0, 0]
        ys = (coords[:, 1] - self.K[1, 2]) / self.K[1, 1]
        zs = np.ones(self.image_height * self.image_width)
        coords = np.vstack((xs, ys, zs))
        
        # camera to world
        # coords is normalized(no depth), so can't directly calculate
        # coords = np.linalg.inv(self.Rcw) @ (coords - self.tcw)
        Rcw = self.Rcw.transpose() # the inverse of an orthogonal matrix is its transpose 
        tcw = Rcw @ (-self.tcw)
        coords = Rcw @ coords
        coef = (0 - tcw[2]) / coords[2, :] # zknown = z * coef + T[2]
        coords = coords * coef + tcw

        return coords

    def get_ipm_map(self):
        """
        与onboard中c++IPM相同
        """
        # ipm image to world
        vs, us = np.indices((self.ipm_height, self.ipm_width))
        coords = np.column_stack((us.ravel(), vs.ravel()))
        # 车道线
        xs = self.world_pixel * coords[:, 0] - self.world_width / 2.0
        ys = self.world_height - self.world_pixel * coords[:, 1] + self.world_y_start
        zs = np.zeros(self.ipm_height * self.ipm_width)
        # 云台
        # xs = self.world_pixel * coords[:, 0] - self.world_width / 2.0
        # ys = self.world_height / 2.0 -  self.world_pixel * coords[:, 1] + self.world_y_start
        # zs = np.zeros(self.ipm_height * self.ipm_width)
        coords = np.vstack((xs, ys, zs))
        
        # world to camera
        coords = self.Rcw @ coords + self.tcw

        # camera to perspective image
        coords = coords / coords[2, :]
        coords = self.K @ coords

        # filter
        coords = coords.transpose().reshape(self.ipm_height, self.ipm_width, 3).astype(np.int64)
        mask = (0 <= coords[:, :, 0]) & (self.image_width > coords[:, :, 0]) \
                & (self.vanish_line <= coords[:, :, 1]) & (self.image_height > coords[:, :, 1])

        return coords, mask

    # def transform(self):
    #     for name in sorted(os.listdir(self.image_dir)):
    #         path = os.path.join(self.image_dir, name)
    #         print(f"[transform] read perspective image {path}")

    #         img = cv2.imread(path, cv2.IMREAD_GRAYSCALE | cv2.IMREAD_COLOR)
    #         assert((img.shape[0]==self.image_height) and (img.shape[1]==self.image_width))

    #         # undistort
    #         img = cv2.remap(img, self.undistort_map1, self.undistort_map2, interpolation=cv2.INTER_NEAREST)

    #         # point cloud
    #         # point_cloud = np.hstack((self.point_cloud.transpose(), img.reshape(-1, 3).astype(np.float64)))
            
    #         # world to ipm image
    #         us = (self.point_cloud[0, :] + self.world_width / 2.0) / self.world_pixel
    #         vs = (self.world_height + self.world_y_start - self.point_cloud[1, :]) / self.world_pixel
    #         coords = np.column_stack((us, vs)).astype(np.int64)

    #         # filter
    #         coords = coords.reshape(img.shape[0], img.shape[1], 2)
    #         mask = (0 <= coords[:, :, 0]) & (self.ipm_width > coords[:, :, 0]) \
    #                 & (0 <= coords[:, :, 1]) & (self.ipm_height > coords[:, :, 1])
    #         mask[np.arange(img.shape[0]) < self.vanish_line] = False

    #         # transform 
    #         img_ipm = np.zeros((self.ipm_height, self.ipm_width, 3), dtype=np.uint8)
    #         img_ipm[coords[mask][:, 1], coords[mask][:, 0]] = img[np.argwhere(mask)[:, 0], np.argwhere(mask)[:, 1]]

    #         # save ipm image
    #         if self.resize is not None:
    #             img_ipm = cv2.resize(img_ipm, dsize=tuple(self.resize), interpolation=cv2.INTER_NEAREST)
    #         path = os.path.join(self.output_dir, name)
    #         cv2.imwrite(path, img_ipm)
    #         print(f"[transform] save ipm image {path}")

    def transform(self):
        for name in sorted(os.listdir(self.image_dir)):
            path = os.path.join(self.image_dir, name)
            print(f"[transform] read perspective image {path}")

            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE | cv2.IMREAD_COLOR)
            assert((img.shape[0]==self.image_height) and (img.shape[1]==self.image_width))

            # undistort
            img = cv2.remap(img, self.undistort_map1, self.undistort_map2, interpolation=cv2.INTER_NEAREST)

            # transform
            img_ipm = np.zeros((self.ipm_height, self.ipm_width, 3), dtype=np.uint8)
            img_ipm[np.argwhere(self.ipm_mask)[:, 0], np.argwhere(self.ipm_mask)[:, 1]] = img[self.ipm_map[self.ipm_mask][:, 1], self.ipm_map[self.ipm_mask][:, 0]]

            # save ipm image
            if self.resize is not None:
                img_ipm = cv2.resize(img_ipm, dsize=tuple(self.resize), interpolation=cv2.INTER_NEAREST)
            path = os.path.join(self.output_dir, name)
            cv2.imwrite(path, img_ipm)
            print(f"[transform] save ipm image {path}")
