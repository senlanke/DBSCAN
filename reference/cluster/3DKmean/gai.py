import os
import re
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from sklearn.cluster import KMeans


def read_txt(txt_path):
    xyz_data = []
    pattern = r"\s*\[([-+]?\d*\.\d+),\s*([-+]?\d*\.\d+),\s*([-+]?\d*\.\d+)\]"
    try:
        with open(txt_path, 'r') as f:
            for line in f.readlines():
                if line == "\n":
                    continue
                match = re.search(pattern, line)
                if match:
                    x = match.group(1)
                    y = match.group(2)
                    z = match.group(3)
                    xyz_data.append([float(x), float(y), float(z)])
    except FileNotFoundError:
        print(f"文件 {txt_path} 未找到。")
    return xyz_data


def is_point_in_box(point, x_min, x_max, y_min, y_max, z_min, z_max):
    return (x_min <= point[0] <= x_max
            and y_min <= point[1] <= y_max
            and z_min <= point[2] <= z_max)


def process(xyz_data):
    xyz_data = np.array(xyz_data)
    x = xyz_data[:, 0]
    y = xyz_data[:, 1]
    z = xyz_data[:, 2]

    ax1.scatter(x, y, z, c='b')

    # 初始 聚类中心点 k
    kmeans = KMeans(n_clusters=K, random_state=42).fit(xyz_data)
    # 聚类中心点
    centers = kmeans.cluster_centers_

    isInBoxNum = 0

    points = []
    # 遍历每个中心
    for center in centers:
        # 读取以该点为框中心的边界框
        x_min = center[0] - BOUNDING_BOXES_W / 2
        x_max = center[0] + BOUNDING_BOXES_W / 2
        y_min = center[1] - BOUNDING_BOXES_L / 2
        y_max = center[1] + BOUNDING_BOXES_L / 2
        z_min = center[2] - BOUNDING_BOXES_H / 2
        z_max = center[2] + BOUNDING_BOXES_H / 2

        ax1.scatter(center[0], center[1], center[2], c='r', marker='x')
        # 绘制矩形框
        # 定义矩形框的边
        edges = [[[x_min, x_min], [y_min, y_min], [z_min, z_max]],
                 [[x_max, x_max], [y_min, y_min], [z_min, z_max]],
                 [[x_min, x_min], [y_max, y_max], [z_min, z_max]],
                 [[x_max, x_max], [y_max, y_max], [z_min, z_max]],
                 [[x_min, x_max], [y_max, y_max], [z_min, z_min]],
                 [[x_min, x_max], [y_max, y_max], [z_max, z_max]],
                 [[x_min, x_max], [y_min, y_min], [z_max, z_max]],
                 [[x_min, x_max], [y_min, y_min], [z_min, z_min]],
                 [[x_min, x_min], [y_min, y_max], [z_min, z_min]],
                 [[x_min, x_min], [y_min, y_max], [z_max, z_max]],
                 [[x_max, x_max], [y_min, y_max], [z_min, z_min]],
                 [[x_max, x_max], [y_min, y_max], [z_max, z_max]]]
        for edge in edges:
            ax1.plot3D(edge[0], edge[1], edge[2], color='r')

        color = 'black'

        for point in xyz_data:
            if (is_point_in_box(point, x_min, x_max, y_min, y_max, z_min, z_max) and point.tolist() not in points):
                points.append(point.tolist())
                isInBoxNum += 1
                # ax1.scatter(point[0], point[1], point[2], c=color, marker='o')
                ax1.scatter(point[0], point[1], point[2], c=color, marker='x')

    print(isInBoxNum)
    rate = isInBoxNum * 1. / len(xyz_data)
    print(rate)

    ax1.set_xlabel("X label")
    ax1.set_ylabel("Y label")
    ax1.set_zlabel("Z label")
    ax1.set_title("Rate: {}".format(rate))
    print("采收率: {} / {} = {}".format(isInBoxNum, len(xyz_data), rate))
    return rate


if "__main__" == __name__:
    # 配置原先设定
    K = 6  # 设置采收次数
    BOUNDING_BOXES_H = 0.65  # 设定作业范围 高
    BOUNDING_BOXES_W = 0.40  # 设定作业范围 宽
    BOUNDING_BOXES_L = 0.12  # 设定作业范围 长

    # 图片路径
    txt_root_path = '/media/cs/e9882685-3ce8-4a58-9e3f-df00ff7ea22d/3DKmean/Data/29438.txt'
    data = read_txt(txt_root_path)
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1, projection="3d")
    rate = process(data)
    plt.show()
    