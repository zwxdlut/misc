import os
import glob
import json
import numpy as np
import cv2

from typing import Tuple, List, Optional, Dict
from scipy.optimize import minimize

IMAGE_DIR = "/mnt/data/lecheng/images/20251124100530547"
OUTPUT_DIR = "/mnt/data/lecheng/keypoints/20251124100530547"

IMAGE_DIR_2 = "/mnt/data/lecheng/images/20251124100530547_nonkey"
OUTPUT_DIR_2 = "/mnt/data/lecheng/keypoints/20251124100530547_nonkey"

# 最佳实践建议

# 特征点分布：
# 每张图像至少15-20个特征点
# 点应覆盖整个图像区域（特别是边缘）
# 避免所有点共面
# 近景：1-3米处的特征点（20%）
# 中景：3-10米特征点（60%）
# 远景：>10米特征点（20%）

# 重叠要求：
# 相邻图像应有30-50%的特征点重叠
# 整个场景应有足够多的"连接点"（建议≥100个3D点）
# 关键点应被多个视角观测（建议≥3个视角）

# 运动模式：
# 相机应绕场景做充分旋转
# 包含不同深度（近/远）的观测
# 避免纯旋转或纯平移运动
# 旋转角度：每10°-30°取一帧
# 旋转范围：至少覆盖180°（全景更佳）
# 俯仰角度：±30°以上

class FeatureMatcher:
    def __init__(self, watermark_height: int = 150):
        """
        初始化特征匹配器
        """
        self.detector = cv2.SIFT_create(nfeatures=2000)  # 使用SIFT获得更好的特征
        self.matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
        self.watermark_height = watermark_height

        # 存储数据
        self.image_paths = []
        self.keypoints_list = []
        self.descriptors_list = []
        self.matches_list = []

    def load_features(self, image_dir: str, feature_dir) -> bool:
        """
        加载特征
        """
        self.image_paths = []
        self.keypoints_list = []
        self.descriptors_list = []

        image_pattern = os.path.join(image_dir, "*.jpg")
        image_paths = glob.glob(image_pattern)
        image_paths.sort()
        
        # 特征目录
        if not os.path.exists(feature_dir):
            print(f"特征目录 {feature_dir} 不存在")
            return False
        self.output_dir = feature_dir
       
        print(f"\n加载特征 {len(image_paths)} 张重叠图像...")
        
        for i, path in enumerate(image_paths):
            filename = os.path.basename(path) + ".txt"
            fpath = os.path.join(feature_dir, filename)
            if not os.path.exists(fpath):
                print(f"特征文件 {fpath} 不存在")
                return False

            with open(fpath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                m, n = lines[0].split()
                m, n = int(m), int(n)

                if len(lines) != m + 1:
                    print(f"特征文件 {fpath} 关键点个数 {m} 不匹配")
                    return False

                keypoints = []
                descriptors = []

                for values in lines[1:]:
                    values = values.split()
                    values = np.array(values, dtype=np.float32)

                    if (n + 4) != len(values):
                        print(f"特征文件 {fpath} 描述子维度 {n} 不匹配")
                        return False

                    # 关键点
                    kpt = cv2.KeyPoint(
                        x=values[0],        # x 坐标
                        y=values[1],        # y 坐标
                        size=values[2],     # 直径
                        angle=values[3],    # 方向角度（度）
                        response=1,         # 响应强度 (0-1)
                        octave=0,           # 金字塔层级
                        class_id=-1         # 对象 ID
                    )
                    keypoints.append(kpt)

                    # 描述子
                    descriptors.append(values[4:])

                print(f"  图像 {os.path.basename(path)}: 载入 {len(keypoints)} 个特征点")
                self.keypoints_list.append(keypoints)
                self.descriptors_list.append(np.array(descriptors, dtype=np.float32))
                self.image_paths.append(path)
    
        print(f"成功加载 {len(self.keypoints_list)} 张图像的特征")

        return True

    def extract_features(self, image_dir: str, output_dir: str = "output"):
        """
        提取特征(排除水印区域）
        """
        self.image_paths = []
        self.keypoints_list = []
        self.descriptors_list = []

        image_pattern = os.path.join(image_dir, "*.jpg")
        image_paths = glob.glob(image_pattern)
        image_paths.sort()
        
        # 输出目录
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"\n提取特征（排除水印区域） {len(image_paths)} 张重叠图像...")
        
        for i, path in enumerate(image_paths):
            img = cv2.imread(path)
            if img is None:
                continue

            h, w = img.shape[:2]

            # 创建掩码排除水印区域
            mask = np.ones((h, w), dtype=np.uint8)
            mask[0:self.watermark_height, :] = 0
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            keypoints, descriptors = self.detector.detectAndCompute(gray, mask)               

            if keypoints is not None and descriptors is not None:
                print(f"  图像 {os.path.basename(path)}: 提取到 {len(keypoints)} 个特征点")
                self.keypoints_list.append(keypoints)
                self.descriptors_list.append(descriptors)
                self.image_paths.append(path)

                # 保存结果
                filename = os.path.basename(path)
                with open(os.path.join(self.output_dir, f"{filename}.txt"), 'w', encoding='utf-8') as f:
                    f.write(f"{descriptors.shape[0]} {descriptors.shape[1]}\n")
                    for i, kpt in enumerate(keypoints):
                        f.write(f"{kpt.pt[0]} {kpt.pt[1]} {kpt.size} {kpt.angle}")
                        for desc in descriptors[i]:
                            f.write(f" {desc}")
                        f.write("\n")
                # 可视化
                img_keypoints = cv2.drawKeypoints(
                    img, 
                    keypoints, 
                    outImage=None, 
                    color=(0, 255, 0),   # BGR格式，绿色
                    flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS  # 显示方向与大小
                )
                cv2.imwrite(os.path.join(self.output_dir, f"{os.path.splitext(filename)[0]}_keypoints.png"), img_keypoints)
        
        if len(self.keypoints_list) < 2:
            print("有效特征图像不足")
            return
        
        print(f"成功提取 {len(self.keypoints_list)} 张图像的特征")

    def match_features(self):
        """
        匹配特征 
        """
        print("\n匹配特征, 收集对应点对...")

        file = open(os.path.join(self.output_dir, "pairs_matches.txt"), 'w', encoding='utf-8')

        # 错误匹配的图像（人工）
        # # 20251113094659633
        # match_filter = {0: [5, 10, 29, 30, 37, 51, 52], 1: [10, 12, 37, 47], 2: [10, 51], 3: [17, 19],
        #                 5: [29, 30, 42, 43], 7: [11, 12, 23, 31, 53], 9: [47], 16: [22, 25], 17: [25, 47], 
        #                 18: [22, 23, 24, 30, 31, 44, 47, 51], 19: [23, 30, 35, 45, 47, 52, 53, 57], 
        #                 20: [24, 25, 30, 31, 33, 36, 46, 47], 21: [29, 30, 47, 51, 53], 22: [29, 30, 60], 
        #                 24: [29, 32, 49, 58], 25: [29], 26: [29, 30], 36: [40], 38: [51, 53], 39: [51, 52],
        #                 40: [47, 57], 41: [47], 42: [51, 59], 44: [51], 45: [51, 62]}

        # # 20251113094659633-180
        # match_filter = {0: [5], 5: [10, 21]}

        # # 20251113094659633-90
        # match_filter = {0: [5], 5: [6, 13]}

        for i in range(len(self.keypoints_list) - 1):
            for j in range(i + 1, len(self.keypoints_list)):
                # if i in match_filter and j in match_filter[i]:
                #     continue
                    
                kp1 = self.keypoints_list[i]
                desc1 = self.descriptors_list[i]
                kp2 = self.keypoints_list[j]
                desc2 = self.descriptors_list[j]
                
                if desc1 is None or desc2 is None or len(desc1) < 2 or len(desc2) < 2:
                    continue

                try:
                    matches12 = self.matcher.knnMatch(desc1, desc2, k=2)
                    matches21 = self.matcher.knnMatch(desc2, desc1, k=2)
                except:
                    continue

                # 对称性过滤
                good_matches = []
                for m12 in matches12:
                    # for m in m12:
                    if len(m12) == 2:
                        m, n = m12
                        # 检查对称性
                        for m21 in matches21[m.trainIdx]:
                            if m21.trainIdx == m.queryIdx:
                                # 低比率测试
                                if m.distance < 0.7 * n.distance:
                                    good_matches.append(m)
                                    break
                
                # # Lowe's ratio test (更严格的阈值)
                # good_matches = []
                # for match_pair in matches:
                #     if len(match_pair) == 2:
                #         m, n = match_pair
                #         if m.distance < 0.7 * n.distance:  # 更严格的匹配阈值
                #             good_matches.append(m)

                if len(good_matches) < 40:  # 需要足够多的匹配点
                    continue

                pts1 = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                pts2 = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                H, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 4.0)
                inlier_matches = [m for i, m in enumerate(good_matches) if mask[i]]

                filename1 = os.path.basename(self.image_paths[i])
                filename2 = os.path.basename(self.image_paths[j])
                print(f"  图像对 {filename1}({i}) - {filename2}({j}): {len(inlier_matches)} 个匹配点")
                
                #  保存结果
                # i-j
                file.write(f"{filename1} {filename2}\n")
                for match in inlier_matches:
                    file.write(f"{match.queryIdx} {match.trainIdx}\n")
                file.write("\n")
                # j-i
                file.write(f"{filename2} {filename1}\n")
                for match in inlier_matches:
                    file.write(f"{match.trainIdx} {match.queryIdx}\n")
                file.write("\n")

                # 可视化
                img1 = cv2.imread(self.image_paths[i])
                img2 = cv2.imread(self.image_paths[j])
                img_match = cv2.drawMatches(
                    img1, kp1, img2, kp2, inlier_matches, None,
                    flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
                    matchColor=(0,255,0), singlePointColor=(255,0,0)
                )
                cv2.imwrite(os.path.join(self.output_dir, f"{filename1}({i})-{filename2}({j})_match.png"), img_match)
                # cv2.imshow('Feature Matching', img_match)
                # cv2.waitKey(0)
        
        file.close()
        
    def visualization(self):
        pass


def match_features(matcher1: FeatureMatcher, matcher2: FeatureMatcher):
    """
    两个匹配器之间匹配特征
    """
    print("\n两个匹配器之间匹配特征, 收集对应点对...")

    file = open(os.path.join(matcher1.output_dir, "pairs_matches.txt"), 'w', encoding='utf-8')

    # 错误匹配的图像
    # # 20251113094659633_nonkey <-> 20251113094659633
    # match_filter = {0: [37], 8: [2, 3, 4, 5], 9: [4, 5, 13, 14, 15, 25, 27, 33, 46, 57], 12: [1], 13: [15], 
    #                 18: [2, 3, 4, 5, 13, 23, 44, 46], 19: [5, 33, 37, 53], 28: [2, 3, 46], 29: [4, 24, 26]}

    # # 20251113094659633_nonkey-180 <-> 20251113094659633-180
    # match_filter = {3: [29], 7: [1]}

    # # 20251113094659633_nonkey-90 <-> 20251113094659633-90
    # match_filter = {5: [1]}

    for i in range(len(matcher1.keypoints_list)):
        for j in range(len(matcher2.keypoints_list)):
            # if i in match_filter and j in match_filter[i]:
            #     continue
                
            kp1 = matcher1.keypoints_list[i]
            desc1 = matcher1.descriptors_list[i]
            kp2 = matcher2.keypoints_list[j]
            desc2 = matcher2.descriptors_list[j]
            
            if desc1 is None or desc2 is None or len(desc1) < 2 or len(desc2) < 2:
                continue

            try:
                matches12 = matcher1.matcher.knnMatch(desc1, desc2, k=2)
                matches21 = matcher1.matcher.knnMatch(desc2, desc1, k=2)
            except:
                continue

            # 对称性过滤
            good_matches = []
            for m12 in matches12:
                # for m in m12:
                if len(m12) == 2:
                    m, n = m12
                    # 检查对称性
                    for m21 in matches21[m.trainIdx]:
                        if m21.trainIdx == m.queryIdx:
                            # 低比率测试
                            if m.distance < 0.7 * n.distance:
                                good_matches.append(m)
                                break
            
            # # Lowe's ratio test (更严格的阈值)
            # good_matches = []
            # for match_pair in matches:
            #     if len(match_pair) == 2:
            #         m, n = match_pair
            #         if m.distance < 0.7 * n.distance:  # 更严格的匹配阈值
            #             good_matches.append(m)

            # if len(good_matches) < 40:  # 需要足够多的匹配点
            #     continue

            pts1 = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            pts2 = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            H, mask = cv2.findHomography(pts1, pts2, cv2.RANSAC, 4.0)
            inlier_matches = [m for i, m in enumerate(good_matches) if mask[i]]
            
            filename1 = os.path.basename(matcher1.image_paths[i])
            filename2 = os.path.basename(matcher2.image_paths[j])
            print(f"  图像对 {filename1}({i}) - {filename2}({j}): {len(inlier_matches)} 个匹配点")
            
            #  保存结果
            # i-j
            file.write(f"{filename1} {filename2}\n")
            for match in inlier_matches:
                file.write(f"{match.queryIdx} {match.trainIdx}\n")
            file.write("\n")
            # j-i
            file.write(f"{filename2} {filename1}\n")
            for match in inlier_matches:
                file.write(f"{match.trainIdx} {match.queryIdx}\n")
            file.write("\n")

            # 可视化
            img1 = cv2.imread(matcher1.image_paths[i])
            img2 = cv2.imread(matcher2.image_paths[j])
            img_match = cv2.drawMatches(
                img1, kp1, img2, kp2, inlier_matches, None,
                flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
                matchColor=(0,255,0), singlePointColor=(255,0,0)
            )
            cv2.imwrite(os.path.join(matcher1.output_dir, f"{filename1}({i})-{filename2}({j})_match.png"), img_match)
            # cv2.imshow('Feature Matching', img_match)
            # cv2.waitKey(0)
    
    file.close()


def main():
    matcher = FeatureMatcher(150)
    if not matcher.load_features(IMAGE_DIR, OUTPUT_DIR):
        matcher.extract_features(IMAGE_DIR, OUTPUT_DIR)
    matcher.match_features()

    matcher2 = FeatureMatcher(150)
    if not matcher2.load_features(IMAGE_DIR_2, OUTPUT_DIR_2):
        matcher2.extract_features(IMAGE_DIR_2, OUTPUT_DIR_2)
    match_features(matcher2, matcher)


if __name__ == "__main__":
    main()