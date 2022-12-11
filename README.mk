编程思路
1. 加载全部静态数据
2. 按天逐步添加扫码+活动点+核酸检测记录，轨迹点用Trajectory类存储，一个轨迹包含一个人一天的3-5个记录。
   建立User类，存储个人静态信息+轨迹信息，人员关系匹配是基于User类的。
3. 空间转换和空间索引
4. 记录有联系的用户，邻居+同事+同行，建立关系图聚类
5. 记录有联系的用户记录,直接从邻居+同事挖掘，再找群体中最相似的补充

COMPANY_BASE_INFO            |
| RESIDENTIAL_BASE_INFO        |
| USER_ACTIVITY_TRACE_RECORDS  |
| USER_BASE_INFO               |
| USER_COVID19_TEST_RECORDS    |
| USER_SCAN_VENUE_CODE_RECORDS |

select count(*) from COMPANY_BASE_INFO;
select count(*) from USER_ACTIVITY_TRACE_RECORDS;
select count(*) from USER_BASE_INFO;
select count(*) from USER_COVID19_TEST_RECORDS;
select count(*) from USER_SCAN_VENUE_CODE_RECORDS;

source /home/like/yqfk/COMPANY_BASE_INFO.sql;
source /home/like/yqfk/USER_ACTIVITY_TRACE_RECORDS.sql;
source /home/like/yqfk/USER_BASE_INFO.sql;
source /home/like/yqfk/USER_COVID19_TEST_RECORDS.sql;
source /home/like/yqfk/USER_SCAN_VENUE_CODE_RECORDS.sql;
