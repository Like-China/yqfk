import time
from utils.trajectory import Trajectory
from rtree import index
from utils.user import User
from loader.dataloader import DataLoader
from tqdm import tqdm

days = ['20221201','20221202','20221203','20221204','20221205','20221206','20221207']
# 在为用户添加轨迹的时候，同步添加轨迹的MBR索引
idx_scan = index.Index(interleaved=False)
idx_act = index.Index(interleaved=False)
"""
scan_data, columns=['date', 'uid', 'phone', 'vlon','vlat', 'day','stime', 'type','special']
act_data, columns=['date', 'uid', 'phone', 'vlon','vlat', 'day','stime','etime', 'type','special']
covid_data, columns=['date', 'uid', 'phone', 'res',  'time']
"""


# 用户静态数据初始化
def init_users(data_loader):
    # 读取静态的固有关系
    userData, homeData, companyData = data_loader.getStaticData()
    # 加载用户信息,0号用户无信息
    users = []
    users.append(User())
    for user_info in userData:
        u = User()
        u.init_user_info(user_info)
        users.append(u)
    return users


# 用户动态轨迹数据更新
def user_records_update(users, scan_data, covid_data, act_data):
    # idx_scan = index.Index(interleaved=False)
    # idx_act = index.Index(interleaved=False)
    # 逐个添加基于用户的扫码轨迹记录，一天一条
    uid = 1
    trj = Trajectory(uid)
    for point in scan_data:
        if point[1] == uid:
            trj.add_point(point, True)
        else:
            users[uid].scan_trips_order_by_day.append(trj)
            idx_scan.insert(uid, trj.mbr)
            uid = point[1]
            trj = Trajectory(uid)
            trj.add_point(point, True)
        # 记录最后一个用户
        if point[1] == 10000:
            users[uid].scan_trips_order_by_day.append(trj)
            uid = point[1]
            trj = Trajectory(uid)
    # 逐个添加基于用户的活动轨迹记录，一天一条
    uid = 1
    trj = Trajectory(uid)
    for point in act_data:
        if point[1] == uid:
            trj.add_point(point, False)
        else:
            users[uid].act_trips_order_by_day.append(trj)
            idx_act.insert(uid, trj.mbr)
            uid = point[1]
            trj = Trajectory(uid)
            trj.add_point(point, False)
        # 记录最后一个用户
        if point[1] == 10000:
            users[uid].act_trips_order_by_day.append(trj)
            uid = point[1]
            trj = Trajectory(uid)
    # 核酸记录
    for covid_record in covid_data:
        uid = covid_record[1]
        users[uid].add_covid_record(covid_record)
    return users


# 给定一个人一周的轨迹，绘制七个子图
def observer(trjs):
    import matplotlib.pyplot as plt
    fig = plt.figure(num=1, figsize=(12,20))
    for ii, trj in enumerate(trjs):
        ax1 = fig.add_subplot(8,1, ii+1)
        x, y = trj.lon_seq, trj.lat_seq
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        ax1.plot(x, y)
        txt = []
        for ii, point in enumerate(trj.points):
            print(point)
            txt.append(str(ii) + point[-2])
        for i in range(len(x)):
            ax1.annotate(txt[i], xy=(x[i], y[i]), xytext=(x[i] , y[i]))
    plt.show()

# 计算一天所有用户能产生LCS
def get_comovement(users, day, index):
    import numpy as np
    lcs_match_res = []
    for u in tqdm(users[1:]):
        query_trj = u.act_trips_order_by_day[day]
        query_mbr = query_trj.mbr
        intersect_users = list(idx_scan.intersection(query_mbr))
        print(len(intersect_users))
        if len(query_trj) < 3:
            continue
        for item in intersect_users:
            intersect_u = users[item]
            intersect_trj = intersect_u.act_trips_order_by_day[day]
            # 计算 最长公共子序列长度 大于等于 3的匹配
            if len(intersect_trj) < 3:
                continue
            if query_trj.LCS_to(intersect_trj) >= 3 and u.uid != item:
                lcs_match_res.append([u.uid, item])
                # print(query_trj)
                # print(intersect_trj)
                # print([u.uid, item])
                # print(query_trj.LCS_to(intersect_trj), intersect_trj.LCS_to(query_trj))
    # 存储满足条件的user对
    np.save('co-pair %d.npy'%day, np.array(lcs_match_res))


if __name__ == "__main__":
    t1 = time.time()
    data_loader = DataLoader()
    users = init_users(data_loader)
    # 读取数据库所有数据, 条目数目分别为：269469 40046 409263
    for ii, date in enumerate(days):
        # print("%s reading..."% date)
        scan_data, covid_data, act_data = data_loader.getVaryData(date)
        users = user_records_update(users, scan_data, covid_data, act_data)
        # 每一天，对每个人的轨迹MBR查找有重叠的轨迹+进一步计算LCS, 挖掘可能的co-movement并写出记录
        get_comovement(users, ii, idx_scan)
        idx_scan = index.Index(interleaved=False)
        idx_act = index.Index(interleaved=False)
    data_loader.close()
    print("reading finished, time comsuming: %d"% (time.time()-t1))


