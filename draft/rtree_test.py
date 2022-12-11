from rtree import index
import random
import time
# 主要使用 rtree.index.Index 和 rtree.index.Property . 用户操纵这些类与索引交互。

# 构建 RTree 实例对象
idx = index.Index()

# 插入索引 insert(id, coordinates, obj=None):
# 其中coordinates为坐标顺序,按照 [xmin, xmax, ymin, ymax，…,……、kmin kmax]

data = []
for ii in range(1000):
    mbr = [random.randint(1,50),random.randint(1,150),random.randint(50,100),random.randint(150,300)]
    idx.insert(ii, mbr)
    data.append(mbr)

# 查询索引
# 查询索引有三种主要方法。:
# 1. 交叉  rtree.index.Index.intersection() 给定一个窗口，返回包含该窗口的ID
t1 = time.time()
for ii in range(10000):
    left, bottom, right, top = [random.randint(1,2),random.randint(1,4),random.randint(2,5),random.randint(4,6)]
    res = list(idx.intersection((left, bottom, right, top)))
    hits = list(idx.nearest((0, 3, 5, 5), 3))
    for item in hits:
        print(data[item])
    break

print(time.time()-t1) # 以上用时70s/14s
# 2. 最近邻, 给定界限最近的1个项。如果多个项目与边界的距离相等，则返回两个项目，自定义想要寻找的最近邻个数
list(idx.nearest((1.0000001, 1.0000001, 2.0, 2.0), 1))




