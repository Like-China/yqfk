from rtree import index
import random
import time


class MyIndex():
    def __init__(self, idx):
        self.uid = idx


class Rtree():
    def __init__(self):
        self.p = index.Property()
        self.p.dimension = 4  # 设置 使用的 维度数 (对于地图)
        self.p.dat_extension = 'data'  # 设置存储的后缀名
        self.p.idx_extension = 'index'  # 设置存储的后缀名
        # interleaved=False时，bbox must be [，…,……、kmin kmax] (interleaved=False)
        # 第一个参数表示 存储到文件中，会生成case.dat 和 case.idx两个文件，overwrite表示是否覆盖之前的数据，如果为false,那么新插入的数据会追加到之前的文件中；
        self.rtree = index.Index('case', interleaved=False, property=self.p, overwrite=True)

    # objects == True 时,返回包括obj在内的数据，否则只返回目标 id
    def get_nearby_obj(self, width, num):
        res = list(self.rtree.nearest(width, num, objects=True))
        return res

    def insert(self, mbr, obj):
        self.rtree.insert(obj, mbr)

    def intersection(self, query_mbr):
        return list(self.rtree.intersection(query_mbr))
    

def test():
    idx = Rtree()
    # 随机插入
    for ii in range(10000):
        left, bottom, right, top = [random.randint(1, 50), random.randint(50, 100), random.randint(1, 150),
                                    random.randint(150, 300)]
        idx.insert((left, bottom, right, top), MyIndex(ii))
    # 1. 交叉  rtree.index.Index.intersection() 给定一个窗口，返回包含该窗口的ID
    t1 = time.time()
    for ii in range(10000):
        left, bottom, right, top = [random.randint(1, 2), random.randint(2, 5), random.randint(1, 4),
                                    random.randint(4, 6)]
        res = list(idx.intersection((left, bottom, right, top)))
    print(time.time() - t1)  # 以上用时70s/14s
    # 给定界限最近的1个项。如果多个项目与边界的距离相等，则返回两个项目，自定义想要寻找的最近邻个数
    hits = idx.get_nearby_obj((0, 0, 5, 5), 3)
    for x in hits:
        print(x.id, '\t')
    hits = idx.get_nearby_obj((0, 0, 1, 1), 2)
    for x in hits:
        print(x.id, '\t')


if  __name__ == "__main__":
    test()

