import pymysql
import time
from utils.trajectory import Trajectory
from rtree import index

days = ['20221201','20221202','20221203','20221204','20221205','20221206','20221207']
# 在为用户添加轨迹的时候，同步添加轨迹的MBR索引
idx_scan = index.Index(interleaved=False)
idx_act = index.Index(interleaved=False)
"""
scan_data, columns=['date', 'uid', 'phone', 'vlon','vlat', 'day','stime', 'type','special']
act_data, columns=['date', 'uid', 'phone', 'vlon','vlat', 'day','stime','etime', 'type','special']
covid_data, columns=['date', 'uid', 'phone', 'res',  'time']
"""

# 获取原始数据库中所有数据
class DataLoader:

    def __init__(self):
        self.conn = self.connect()

    def connect(self):
        conn=pymysql.connect(host = '127.0.0.1' # 连接名称，默认127.0.0.1
        ,user = 'root' # 用户名
        ,passwd='1212' # 密码
        ,port= 3306 # 端口，默认为3306
        ,db='yqfk' # 数据库名称
        ,charset='utf8' # 字符编码
        )
        print("connect successful!!")
        return conn

    def query(self, command):
        cur = self.conn.cursor() # 生成游标对象
        cur.execute(command) # 执行SQL语句
        data = cur.fetchall() # 通过fetchall方法获得数据
        cur.close() # 关闭游标
        return data

    def getStaticData(self):
        userData = self.query("select * from USER_BASE_INFO")
        # userData = pd.DataFrame(userData, columns=['uid', 'uname', 'phone', 'cid', 'clon', 'clat', 'hid', 'hlon', 'hlat'])
        homeData = self.query("select * from RESIDENTIAL_BASE_INFO")
        # homeData = pd.DataFrame(homeData, columns=['hid', 'hname', 'hlon', 'hlat'])
        companyData = self.query("select * from COMPANY_BASE_INFO")
        # companyData = pd.DataFrame(companyData, columns=['cid', 'cname', 'hlon', 'hlat'])
        return userData, homeData, companyData,

    def getVaryData(self, date):
        scan_data = self.query("select * from USER_SCAN_VENUE_CODE_RECORDS where STAT_DATE='%s'"%date)
        # scan_data = pd.DataFrame(scan_data, columns=['date', 'uid', 'phone', 'vlon','vlat', 'day','stime', 'type','special'])
        covid_data = self.query("select * from USER_COVID19_TEST_RECORDS where STAT_DATE='%s'"%date)
        # covid_data = pd.DataFrame(covid_data, columns=['date', 'uid', 'phone', 'res',  'time'])
        act_data = self.query("select * from USER_ACTIVITY_TRACE_RECORDS where STAT_DATE='%s'"%date)
        # act_data = pd.DataFrame(act_data, columns=['date', 'uid', 'phone', 'vlon','vlat', 'day','stime','etime', 'type','special'])
        return  scan_data, covid_data, act_data

    def getDataByUser(self):
        scan_data = []
        for ii in range(1, 10001):
            data = self.query("select * from USER_SCAN_VENUE_CODE_RECORDS where USER_ID='%d'"%ii)
        scan_data.append(data)
        return scan_data

    def close(self):
        self.conn.close()  # 关闭连接


class User:

    def __init__(self):
        self.uid = None
        self.uname = None
        self.phone = None
        self.cid = None
        self.clon = None
        self.clat = None
        self.hid = None
        self.hlon = None
        self.hlat = None

        # 缓存天数
        max_cache_days = 7
        self.covid_records_order_by_day = []
        self.scan_trips_order_by_day = []
        self.act_trips_order_by_day = []

    def init_user_info(self, user_info):
        self.uid = user_info.uid
        self.uname = user_info.uname
        self.phone = user_info.phone
        self.cid = user_info.cid
        self.clon = user_info.clon
        self.clat = user_info.clat
        self.hid = user_info.hid
        self.hlon = user_info.hlon
        self.hlat = user_info.hlat

    def add_covid_record(self, covid_record):
        covid_record = [covid_record.time, covid_record.res]
        self.covid_records_order_by_day.append(covid_record)

    def __str__(self):
        return str([self.uid,self.uname,self.cid,self.hid])


# 用户静态数据初始化
def init_users(data_loader):
    # 读取静态的固有关系
    userData, homeData, companyData = data_loader.getStaticData()
    # 加载用户信息,0号用户无信息
    users = []
    users.append(User())
    for ii in range(len(userData)):
        user_info = userData.iloc[ii]
        u = User()
        u.init_user_info(user_info)
        users.append(u)
    return users

# 用户数据按照每天添加，动态更新
def user_records_update(users, scan_data, covid_data, act_data):
    # 逐个添加基于用户的扫码轨迹记录，一天一条
    uid = 1
    trj = Trajectory(uid)
    for ii in range(len(scan_data)):
        point = scan_data.iloc[ii]
        if point.uid == uid:
            trj.add_point(point, True)
        else:
            users[uid].scan_trips_order_by_day.append(trj)
            idx_scan.insert(uid, trj.mbr)
            uid = point.uid
            trj = Trajectory(uid)
            trj.add_point(point, True)
        # 记录最后一个用户
        if ii == len(scan_data) - 1:
            users[uid].scan_trips_order_by_day.append(trj)
            uid = point.uid
            trj = Trajectory(uid)
    # 逐个添加基于用户的活动轨迹记录，一天一条
    uid = 1
    trj = Trajectory(uid)
    for ii in range(len(act_data)):
        point = act_data.iloc[ii]
        if point.uid == uid:
            trj.add_point(point, False)
        else:
            users[uid].act_trips_order_by_day.append(trj)
            idx_act.insert(uid, trj.mbr)
            uid = point.uid
            trj = Trajectory(uid)
            trj.add_point(point, False)
        # 记录最后一个用户
        if ii == len(act_data) - 1:
            users[uid].act_trips_order_by_day.append(trj)
            uid = point.uid
            trj = Trajectory(uid)
    # 核酸记录
    for ii in range(len(covid_data)):
        covid_record = covid_data.iloc[ii]
        uid = covid_record.uid
        users[uid].add_covid_record(covid_record)
    return users

def user_records_update1(users, scan_data, covid_data, act_data):
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
    for ii in range(len(covid_data)):
        covid_record = covid_data.iloc[ii]
        uid = covid_record.uid
        users[uid].add_covid_record(covid_record)
    return users


if __name__ == "__main__":
    t1 = time.time()
    data_loader = DataLoader()
    users = init_users(data_loader)
    # 读取数据库所有数据, 条目数目分别为：269469 40046 409263

    for ii, date in enumerate(days):
        print("%s reading..."% date)
        scan_data, covid_data, act_data = data_loader.getVaryData(date)
        scan_data = scan_data.values.tolist()
        act_data = act_data.values.tolist()
        users = user_records_update1(users, scan_data, covid_data, act_data)
    data_loader.close()
    print("reading finished, time comsuming: %d"% (time.time()-t1))


    # 每一天，对每个人的轨迹MBR查找有重叠的轨迹+进一步计算LCS
    # lcs_match_res = []
    # for u in tqdm(users[1:]):
    #     query_trj = u.scan_trips_order_by_day[0]
    #     query_mbr = query_trj.mbr
    #     intersect_users = idx_scan.intersection(query_mbr)
    #     for item in intersect_users:
    #         intersect_u = users[item]
    #         intersect_trj = intersect_u.scan_trips_order_by_day[0]
    #         # 计算 最长公共子序列长度 大于等于 2的匹配
    #         if (query_trj.LCS_to(intersect_trj)>=3) and u.uid != item:
    #             count += 1
    #             lcs_match_res.append([query_trj, intersect_trj])
    #             print(query_trj)
    #             print(intersect_trj)
    #             print(len(query_trj))
    #             continue

