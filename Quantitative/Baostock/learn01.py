import baostock as bs
import pandas as pd
import matplotlib.pyplot as plt

#### 登陆系统 ####
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

#### 获取沪深A股估值指标(日频)数据 ####
# peTTM    滚动市盈率
# psTTM    滚动市销率
# pcfNcfTTM    滚动市现率
# pbMRQ    市净率
rs = bs.query_history_k_data_plus("sh.600000",
    "date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM",
    start_date='2020-01-01', end_date='2020-12-31',
    frequency="d", adjustflag="3")
print('query_history_k_data_plus respond error_code:'+rs.error_code)
print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)

#### 打印结果集 ####
result_list = []
while (rs.error_code == '0') & rs.next():
    # 获取一条记录，将记录合并在一起
    result_list.append(rs.get_row_data())
result = pd.DataFrame(result_list, columns=rs.fields)

#### 结果集输出到csv文件 ####
result.to_csv("history_A_stock_valuation_indicator_data.csv", encoding="gbk", index=False)
print(result)


x = result['date']
y = result['peTTM']
plt.plot(x, y)
plt.show()

#### 登出系统 ####
bs.logout()

