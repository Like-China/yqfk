
import matplotlib.pyplot as plt


# 给定一个人一周的轨迹，绘制七个子图
def observer(trjs):
    fig = plt.figure(num=1, figsize=(12, 20))
    for ii, trj in enumerate(trjs):
        ax1 = fig.add_subplot(8, 1, ii + 1)
        x, y = trj.lon_seq, trj.lat_seq
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        ax1.plot(x, y)
        txt = []
        for ii, point in enumerate(trj.points):
            print(point)
            txt.append(str(ii) + point[-2])
        for i in range(len(x)):
            ax1.annotate(txt[i], xy=(x[i], y[i]), xytext=(x[i], y[i]))
    plt.show()


# 给定两条认定的有关联的轨迹，绘制两者的轨迹在同一张图上
def show_two_trjs(trj1, trj2):
    plt.figure(num=1, figsize=(12, 20))
    plt.plot(trj1[0], trj1[1], linewidth=5, marker = 'p', markersize= 30)
    plt.plot(trj2[0], trj2[1], linewidth=5, marker = 'o', markersize= 30)
    plt.show()


if __name__ == "__main__":
    # 观察任意的两组找到的轨迹是否具有相似性
    import numpy as np
    import random
    day = 0  #random.randint(0,6)
    arr = np.load("../%d.npy"%day, allow_pickle=True)
    n = random.randint(0,len(arr))
    print(arr[n])
    trj1 = arr[n][3]
    trj2 = arr[n][4]
    show_two_trjs(trj1, trj2)