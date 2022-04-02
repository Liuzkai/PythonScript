import tushare as ts
import pandas as pd
# ts.set_token('7dc39867da616d1570e708a70325d4f51836fdec52cd8c3fc92885b6')
# 初始化pro接口
pro = ts.pro_api('7dc39867da616d1570e708a70325d4f51836fdec52cd8c3fc92885b6')

df = pro.trade_cal(exchange='', start_date='20190901', end_date='20191231', fields='exchange,cal_date,is_open,pretrade_date', is_open='0')
print(df)