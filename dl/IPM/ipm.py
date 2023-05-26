import numpy as np
from numpy.linalg import solve
import os
import sys
import cv2

class IPM():
    def __init__(self, args):
        # 记录参数
        self.raw_H, self.raw_W, self.raw_C = args.height, args.width, args.channel
        self.vanish_line = args.vanish_line
        param = [args.intrinsic[0], 0.0, args.intrinsic[2], 0.0, args.intrinsic[1], args.intrinsic[3], 0.0, 0.0, 1.0]
        self.K = np.array(param).reshape(3,3)
        self.ipm_width_x_3d, self.ipm_height_y_3d = args.ipm_width_x_3d, args.ipm_height_y_3d
        self.ipm_step_xy = args.ipm_step_xy
        self.ipm_height_y_start = args.ipm_height_y_start
        self.R_ccs2ocs = np.array(args.R_ccs2ocs).reshape(3,3)
        self.T_ccs2ocs = np.array(args.T_ccs2ocs).reshape(3,1)
        # 读入文件夹下所有图片
        if not os.path.exists(args.image_dir):
            os.makedirs(args.image_dir)
        self.image_dir = args.image_dir
        self.images_name = sorted(os.listdir(args.image_dir))
        # self.images_list = [os.path.join(args.image_dir, f) for f in self.images_name]
        # 输出文件路径
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
        self.output_dir = args.output_dir
        self.merge_dir = os.path.join(self.output_dir, "compare")
        if not os.path.exists(self.merge_dir):
            os.makedirs(self.merge_dir)
        # 计算IPM图像大小
        self.ipm_image_width = int(self.ipm_width_x_3d / self.ipm_step_xy)
        self.ipm_image_height = int(self.ipm_height_y_3d / self.ipm_step_xy)
        self.resize = args.resize

        return

    def pair(self, ipm_image_width, ipm_image_height):
        for r in range(ipm_image_height):
            for c in range(ipm_image_width):
                yield r,c

    def calc_ccs_xy_by_uv(self, uv):
        p_uv = np.append(np.array(uv),1)
        p_cn = np.linalg.inv(self.K) @ p_uv
        # AX=b
        A00 = self.R_ccs2ocs[2,0] * p_cn[0] - self.R_ccs2ocs[0,0]
        A01 = self.R_ccs2ocs[2,1] * p_cn[0] - self.R_ccs2ocs[0,1]
        A10 = self.R_ccs2ocs[2,0] * p_cn[1] - self.R_ccs2ocs[1,0]
        A11 = self.R_ccs2ocs[2,1] * p_cn[1] - self.R_ccs2ocs[1,1]
        b0 = self.T_ccs2ocs[0] - self.T_ccs2ocs[2] * p_cn[0]
        b1 = self.T_ccs2ocs[1] - self.T_ccs2ocs[2] * p_cn[1]
        A = np.mat([[A00,A01],[A10,A11]])
        b = np.mat([b0,b1])
        X = solve(A,b)
        return X.A  # numpy.ndarray [2,1]

    def calc_uv_by_ccs_xy(self, pt_ccs):
        pt_ocs = self.R_ccs2ocs @ pt_ccs + self.T_ccs2ocs.reshape(3)
        pt_ocs = pt_ocs / pt_ocs[2]
        pt_uv = self.K @ pt_ocs
        return (pt_uv + 0.5).astype(np.int32)

    def get_ipm_rect(self):
        # 对应960x540的投影区域
        uv_lu = [0,309]
        uv_ru = [self.raw_W-1,309]
        uv_lb = [0,433]
        uv_rb = [self.raw_W-1,433]

        ccs_lb = self.calc_ccs_xy_by_uv(uv_lb)
        ccs_rb = self.calc_ccs_xy_by_uv(uv_rb)
        try:
            assert((-self.ipm_width_x_3d/2.0<ccs_lb[0,0]<ccs_rb[0,0]<self.ipm_width_x_3d/2.0) and (0<ccs_lb[1,0]<self.ipm_height_y_3d) and (0<ccs_rb[1,0]<self.ipm_height_y_3d))
        except:
            print("Error: ipm_width_x_3d is too big.")
            sys.exit(1)

        ccs_lu = self.calc_ccs_xy_by_uv(uv_lu)
        ccs_ru = self.calc_ccs_xy_by_uv(uv_ru)
        
        if ((ccs_lu[0,0]<-self.ipm_width_x_3d/2.0) or (ccs_lu[1,0]>self.ipm_height_y_3d)):
            ccs_lu = np.array([max(ccs_lu[0,0],-self.ipm_width_x_3d/2.0), min(ccs_lu[1,0],self.ipm_height_y_3d), 0])
            uv_lu = self.calc_uv_by_ccs_xy(ccs_lu).tolist()[:2]
            if (uv_lu[0]<0):
                uv_lu[0] = 0
            if (uv_lu[1]<self.vanish_line):
                uv_lu[1] = self.vanish_line
            ccs_lu = self.calc_ccs_xy_by_uv(uv_lu)

        if ((ccs_ru[0,0]>self.ipm_width_x_3d/2.0) or (ccs_ru[1,0]>self.ipm_height_y_3d)):
            ccs_ru = np.array([min(ccs_ru[0,0],self.ipm_width_x_3d/2.0), min(ccs_ru[1,0],self.ipm_height_y_3d), 0])
            uv_ru = self.calc_uv_by_ccs_xy(ccs_ru).tolist()[:2]
            if (uv_ru[0]>=self.raw_W):
                uv_ru[0] = self.raw_W-1
            if (uv_ru[1]<self.vanish_line):
                uv_ru[1] = self.vanish_line
            ccs_ru = self.calc_ccs_xy_by_uv(uv_ru)

        ipm_lu = [max(0, int((ccs_lu[0,0]+self.ipm_width_x_3d/2.0)/self.ipm_step_xy)), max(0, self.ipm_image_height-1-int(ccs_lu[1,0]/self.ipm_step_xy))]
        ipm_ru = [min(self.ipm_image_width-1, int((ccs_ru[0,0]+self.ipm_width_x_3d/2.0)/self.ipm_step_xy)), max(0, self.ipm_image_height-1-int(ccs_ru[1,0]/self.ipm_step_xy))]
        ipm_lb = [max(0, int((ccs_lb[0,0]+self.ipm_width_x_3d/2.0)/self.ipm_step_xy)), min(self.ipm_image_height-1, self.ipm_image_height-1-int(ccs_lb[1,0]/self.ipm_step_xy))]
        ipm_rb = [min(self.ipm_image_width-1, int((ccs_rb[0,0]+self.ipm_width_x_3d/2.0)/self.ipm_step_xy)), min(self.ipm_image_height-1, self.ipm_image_height-1-int(ccs_rb[1,0]/self.ipm_step_xy))]

        uv_list = [uv_lu, uv_ru, uv_lb, uv_rb]
        ipm_list = [ipm_lu, ipm_ru, ipm_lb, ipm_rb]

        uv_array = np.array(uv_list, dtype=np.float32)
        ipm_array = np.array(ipm_list, dtype=np.float32)

        return uv_array,ipm_array

    def get_ipm_map(self):
        """
        与onboard 中 c++ IPM相同
        """
        rc_array = np.zeros((self.ipm_image_height*self.ipm_image_width,2),dtype=np.int32)
        pt_ccs_array = np.zeros((self.ipm_image_height*self.ipm_image_width,3))   #[w*h, 3]
        for r, c in self.pair(self.ipm_image_width, self.ipm_image_height):
            x = -self.ipm_width_x_3d / 2.0 + self.ipm_step_xy * c
            y = self.ipm_step_xy * (self.ipm_image_height-1-r) + self.ipm_height_y_start
            z = 0
            pt_ccs = np.array([x,y,z]).reshape(1,3)
            pt_ccs_array[r*self.ipm_image_width+c,:] = pt_ccs[0,:]
            rc_array[r*self.ipm_image_width+c,0] = r
            rc_array[r*self.ipm_image_width+c,1] = c

        pt_ocs_array = pt_ccs_array @ self.R_ccs2ocs.transpose() + self.T_ccs2ocs.reshape(1,3)  #[N,3]
        pt_ocs_array = (pt_ocs_array / pt_ocs_array[:,2].reshape(-1,1))
        pt_uv_array = pt_ocs_array @ self.K.transpose()
        pt_uv_array = (pt_uv_array + 0.5).astype(np.int32)

        idx = list(np.where((pt_uv_array[:,1]>self.vanish_line) & (pt_uv_array[:,1]<self.raw_H) & (pt_uv_array[:,0]>=0) & (pt_uv_array[:,0]<self.raw_W)))[0]
        img_uvs = pt_uv_array[idx[:], :2]
        ipm_rcs = rc_array[idx[:],:]
        return ipm_rcs,img_uvs

    def undistort(self, img):
        height = img.shape[0]
        width  = img.shape[1]

        # 相机内参 fx cx fy cy
        cam_0_matrix = [[2141.9937, 0., 1724.7345],
                        [0., 2144.1709, 1106.3953],
                        [0., 0., 1.]]
        # 去畸变参数k1 k2 p1 p2 k3
        cam_0_distcoeffs = [-0.3847, 0.1769, -0.000679, -0.000386, -0.0413]

        camera_matrix = np.array(cam_0_matrix, dtype=np.float32)

        distortion = np.array(cam_0_distcoeffs, dtype=np.float32)
        map1, map2 = cv2.initUndistortRectifyMap(camera_matrix, distortion, None, camera_matrix, (width, height), cv2.CV_32FC1)
        img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_NEAREST)

        return img

    def get_ipm_images(self):
        # 1
        ipm_rcs,img_uvs = self.get_ipm_map()

        # 2
        # uv_array,ipm_array = self.get_ipm_rect()
        # M = cv2.getPerspectiveTransform(uv_array, ipm_array)

        for f in self.images_name:
            img = cv2.imread(os.path.join(self.image_dir, f), cv2.IMREAD_COLOR if 3 == self.raw_C else cv2.IMREAD_GRAYSCALE)
            img = self.undistort(img)
            
            try:    
                # 输入图片大小与默认尺寸不匹配报错！提醒：如果图片大小不匹配需要对应修改内参矩阵和消失线
                assert((img.shape[0]==self.raw_H) and (img.shape[1]==self.raw_W))
                dst_path = os.path.join(self.output_dir, f)

                # 1
                if 3 == self.raw_C:
                    img_ipm = np.zeros((self.ipm_image_height, self.ipm_image_width, 3), dtype=np.uint8)
                else:
                    img_ipm = np.zeros((self.ipm_image_height, self.ipm_image_width), dtype=np.uint8)
                img_ipm[ipm_rcs[:,0],ipm_rcs[:,1]] = img[img_uvs[:,1],img_uvs[:,0]]

                # 2
                # img_ipm = cv2.warpPerspective(img, M, (self.ipm_image_width,self.ipm_image_height))

                if self.resize is not None:
                    img_ipm = cv2.resize(img_ipm, dsize=tuple(self.resize), interpolation=cv2.INTER_NEAREST)
 
                cv2.imwrite(dst_path, img_ipm)
                print(f"write image {dst_path}")

                # # 原图与结果图对比
                # if 3 == self.raw_C:
                #     img_merge = np.zeros((img.shape[0] + img_ipm.shape[0], img.shape[1] + img_ipm.shape[1], 3), dtype=np.uint8)
                # else:
                #     img_merge = np.zeros((img.shape[0] + img_ipm.shape[0], img.shape[1] + img_ipm.shape[1]), dtype=np.uint8)
                # img_merge[0:img.shape[0], 0:img.shape[1]] = img
                # img_merge[0:img_ipm.shape[0], img.shape[1]:img_merge.shape[1]] = img_ipm
                # merge_path = os.path.join(self.merge_dir, f)
                # cv2.imwrite(merge_path, img_merge)
                # print(f"write compare image {merge_path}")
            except:
                print(f"Warning: image {os.path.join(self.image_dir, f)} size not match!")

        return


