from math import sin, asin, cos, radians, fabs, sqrt
EARTH_RADIUS = 6371  # 地球平均半径，6371km


def hav(theta):
    s = sin(theta / 2)
    return s * s


def get_distance_hav(lng0, lat0, lng1, lat1):
    """用haversine公式计算球面两点间的距离。"""
    # 经纬度转换成弧度
    lat0 = radians(lat0)
    lat1 = radians(lat1)
    lng0 = radians(lng0)
    lng1 = radians(lng1)

    dlng = fabs(lng0 - lng1)
    dlat = fabs(lat0 - lat1)
    h = hav(dlat) + cos(lat0) * cos(lat1) * hav(dlng)
    distance = 2 * EARTH_RADIUS * asin(sqrt(h))
    return distance*1000

if __name__ == "__main__":
    lng0, lat0, lng1, lat1 = 104.00131, 30.79532, 103.95213, 30.66328 # 公司到小区
    lng0, lat0, lng1, lat1 = 104.00229, 30.79380, 104.00178, 30.79407 #公司到公司
    lng0, lat0, lng1, lat1 = 104.00229, 30.79380, 103.94645, 30.66999 # 公司到附近用餐
    lng0, lat0, lng1, lat1 = 103.95689, 30.66252, 103.94645, 30.66999 # 公司附近用餐到小区
    print(get_distance_hav(lng0, lat0, lng1, lat1))

