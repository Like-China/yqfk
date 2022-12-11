import time

import Settings
from utils.trajectory import Trajectory
from rtree import index
from utils.user import User
from loader.dataloader import DataLoader
from tqdm import tqdm
from index.scan import get_communities
import numpy as np

days = ['20221201','20221202','20221203','20221204','20221205','20221206','20221207']
# 在为用户添加轨迹的时候，同步添加轨迹的MBR索引
idx_scan = index.Index(interleaved=False)
idx_act = index.Index(interleaved=False)
# 用户住宅集合
home_dict = {}
company_dict = {}
for ii in range(1,1001):
    home_dict[ii] = []
    company_dict[ii] = []
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
        # 记录家字典和公司字典
        home_dict[u.hid].append(u.uid)
        company_dict[u.cid].append(u.uid)
        users.append(u)
    return users


# 用户动态轨迹数据更新
def user_records_update(users, scan_data, covid_data, act_data):
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


# 计算一天所有用户能产生LCS
def get_comovement(users, day, communities):
    import numpy as np
    lcs_match_res = []
    for u in tqdm(users[1:]):
        query_trj = u.act_trips_order_by_day[day]
        # query_mbr = query_trj.mbr
        # intersect_users = list(idx_act.intersection(query_mbr)) # MBR交集
        # intersect_users = list(set(home_dict[u.hid]).union(company_dict[u.cid])) # 邻居或同事交集
        if u.community_id == -1:
            intersect_users = list(set(home_dict[u.hid]).union(company_dict[u.cid]))
        else:
            intersect_users = communities[u.community_id]
        if len(query_trj) < Settings.min_lcs_length:
            continue
        for item in intersect_users[intersect_users.index(u.uid)+1:]:
            intersect_u = users[item]
            intersect_trj = intersect_u.act_trips_order_by_day[day]
            # 计算 最长公共子序列长度 大于等于 的匹配
            if len(intersect_trj) < Settings.min_lcs_length:
                continue
            lcs_seq, lcs_length = query_trj.LCS_to(intersect_trj)
            if lcs_length >= Settings.min_lcs_length and u.uid != item:
                lcs_match_res.append([u.uid, item, lcs_length, [query_trj.lon_seq, query_trj.lat_seq], [intersect_trj.lon_seq, intersect_trj.lat_seq]])
    # 存储满足条件的user对
    print("find %d pairs with lcs_min_length=%d"%(len(lcs_match_res), Settings.min_lcs_length))
    np.save('%d.npy'%day, np.array(lcs_match_res))
    return lcs_match_res


if __name__ == "__main__":
    t1 = time.time()
    data_loader = DataLoader()
    users = init_users(data_loader)
    # 构建社区
    import itertools
    pairs = []
    for ii in range(1,1001):
        home_pair = list(itertools.combinations(home_dict[ii], 2))
        company_pair = list(itertools.combinations(company_dict[ii], 2))
        pairs.extend(home_pair)
        pairs.extend(company_pair)
    communities, hubs, outliers = get_communities(pairs, Settings.mu)
    communities = [sorted(item) for item in communities]
    print("共探测到静态社区数目: %d"%len(communities))
    # 记录每个用户属于哪个社区
    for ii, comm in enumerate(communities):
        for item in comm:
            users[item].community_id = ii
    # 分天读取数据库所有数据, 条目数目分别为：269469 40046 409263, 获取有关联的co-movement pair
    for ii, date in enumerate(days[0:Settings.process_days]):
        scan_data, covid_data, act_data = data_loader.getVaryData(date)
        users = user_records_update(users, scan_data, covid_data, act_data)
        get_comovement(users, ii, communities)
        idx_scan = index.Index(interleaved=False)
        idx_act = index.Index(interleaved=False)
    data_loader.close()
    print("reading finished, time cost: %d"% (time.time()-t1))

    # 读取co-movement pair, 建立社区网络并尝试补全轨迹
    for day in range(Settings.process_days):
        pairs = np.load("%d.npy" % day, allow_pickle=True)
        communities, hubs, outliers = get_communities(pairs,5)
        print(len(communities))
        # 初始化每个人的comovement id
        for user in users:
            user.co_movement_id = -1
        # 记录每个用户属于哪个co-movement 聚类
        for ii, comm in enumerate(communities):
            for item in comm:
                users[item].co_movement_id = ii
        # 对每个用户，尝试使用其co-movement组内的其他成员轨迹对其进行填充
        valid_count = 0
        invalid_count = 0
        for u in users[1:]:
            query_trj = u.act_trips_order_by_day[day]
            if u.co_movement_id == -1:
                intersect_users = list(set(home_dict[u.hid]).union(company_dict[u.cid]))
            else:
                intersect_users = communities[u.co_movement_id]
            for item in intersect_users[intersect_users.index(u.uid) + 1:]:
                intersect_u = users[item]
                intersect_trj = intersect_u.act_trips_order_by_day[day]
                lcs_seq, lcs_length = query_trj.LCS_to(intersect_trj)
                if lcs_length >= 2:
                    print(lcs_seq, lcs_length)

