
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
        self.uid = user_info[0]
        self.uname = user_info[1]
        self.phone = user_info[2]
        self.cid = user_info[3]
        self.clon = user_info[4]
        self.clat = user_info[5]
        self.hid = user_info[6]
        self.hlon = user_info[7]
        self.hlat = user_info[8]

    def add_covid_record(self, covid_record):
        record = [covid_record[4], covid_record[3]]
        self.covid_records_order_by_day.append(record)

    def __str__(self):
        return str([self.uid,self.uname,self.cid,self.hid])

