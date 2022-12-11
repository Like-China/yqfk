
import pymysql


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


if __name__ == "__main__":
    loader = DataLoader()
    loader.query("source /home/like/yqfk/USER_BASE_INFO.sql")
