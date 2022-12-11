import Settings
from fun.dist import get_distance_hav


class Trajectory:

    def __init__(self, uid):
        self.uid = uid
        self.lon_seq = []
        self.lat_seq = []
        self.stime_seq = []
        self.etime_seq = []
        self.points = []
        self.mbr = [1000,-1000,1000,-1000]

    """
    原dataframe使用，效果慢
    """
    def add_point1(self, point, is_scan):
        lon, lat = float(point.vlon), float(point.vlat)
        self.lon_seq.append(lon)
        self.lat_seq.append(lat)
        self.stime_seq.append(point.stime)
        if not is_scan:
            self.etime_seq.append(point.etime)
        self.points.append(point)
        self.mbr[0] = min(self.mbr[0], lon)
        self.mbr[1] = max(self.mbr[1], lon)
        self.mbr[2] = min(self.mbr[2], lat)
        self.mbr[3] = max(self.mbr[3], lat)

    def add_point(self, point, is_scan):
        lon, lat = float(point[3]), float(point[4])
        self.lon_seq.append(lon)
        self.lat_seq.append(lat)
        self.stime_seq.append(point[6])
        if not is_scan:
            self.etime_seq.append(point[7])
        self.points.append(point)
        self.mbr[0] = min(self.mbr[0], lon)
        self.mbr[1] = max(self.mbr[1], lon)
        self.mbr[2] = min(self.mbr[2], lat)
        self.mbr[3] = max(self.mbr[3], lat)

    def __len__(self):
        return len(self.lon_seq)

    def __str__(self):
        return str(self.lon_seq)+ str(self.lat_seq)
    
    def LCS_to(self, trj):
        m = len(self.lon_seq)
        n = len(trj)
        # 定义一个列表来保存最长公共子序列的长度，并初始化
        record = [[0 for i in range(n + 1)] for j in range(m + 1)]
        # lcs序列是哪几个数值,记录索引
        lcs_seq = []
        for i in range(m):
            for j in range(n):
                lon1 = self.lon_seq[i]
                lat1 = self.lat_seq[i]
                lon2 = trj.lon_seq[j]
                lat2 = trj.lat_seq[j]
                if get_distance_hav(lon1, lat1, lon2, lat2) <= Settings.dist_error:
                    record[i + 1][j + 1] = record[i][j] + 1
                    lcs_seq.append([i,j])
                elif record[i + 1][j] > record[i][j + 1]:
                    record[i + 1][j + 1] = record[i + 1][j]
                else:
                    record[i + 1][j + 1] = record[i][j + 1]
                # 提前结束条件
                # if record[i + 1][j + 1] >= Settings.min_lcs_length: return Settings.min_lcs_length
                # if Settings.min_lcs_length-record[i + 1][j + 1] > m-i-1 or Settings.min_lcs_length-record[i + 1][j + 1] > n-i-1: return record[i + 1][j + 1]
        return lcs_seq, record[-1][-1]

