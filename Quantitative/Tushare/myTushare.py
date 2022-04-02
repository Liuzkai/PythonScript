#先引入后面分析、可视化等可能用到的库
import tushare as ts
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sqlalchemy import create_engine
import psycopg2


#正常显示画图时出现的中文和负号
from pylab import mpl
mpl.rcParams['font.sans-serif']=['SimHei']
mpl.rcParams['axes.unicode_minus']=False

#设置token
token = '7dc39867da616d1570e708a70325d4f51836fdec52cd8c3fc92885b6'
pro = ts.pro_api(token)

#数据获取函数，默认时间可以随时改动
#如果报错，把tushare升级到最新
def get_data(code,start='20190101',end='20190425'):
    df=ts.pro_bar(ts_code=code, adj='qfq', start_date=start, end_date=end)
    return df


#交易代码获取函数，获取最新交易日的代码
#获取当前交易日最新的股票代码和简称
def get_code():
    codes = pro.stock_basic(list_status='L').ts_code.values
    return codes


engine = create_engine('postgresql+psycopg2://postgres:123456@localhost:5432/postgres')
def insert_sql(data,db_name,if_exists='append'):
    #使用try...except..continue避免出现错误，运行崩溃
    try:
        data.to_sql(db_name,engine,index=False,if_exists=if_exists)
        #print(code+'写入数据库成功')
    except:
        pass


#下载20190101-20190425数据并插入数据库stock_data
#此步骤比较耗费时间，大致25-35分钟左右
for code in get_code():
    data=get_data(code)
    insert_sql(data,'stock_data')
#读取整张表数据
df=pd.read_sql('stock_data',engine)
print(len(df))