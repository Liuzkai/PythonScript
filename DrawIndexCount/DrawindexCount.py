import re
import pandas as pd
path = '/Users/liuzhongkai/Documents/DOC/'
txt = 'ccc.txt'
f = open(path+txt)
line = f.readline()
start = 0
drawcall = {}
while line:
    if line.find('DynamicEd') > -1:
        start = 0
    
    if start == 1:
        s = line.split('|')[1].strip().strip(' \\- ').split(' ')
        name = s[1]
        material = [s[0]]
        line = f.readline()
        ss = line.split('|')[1].strip().strip(' \\- ')
        num = re.findall(r'\d+',ss)
        triangle = int(num[0])
        count = 0
        try: 
            count = int(num[1])
            triangle *= count
        except IndexError:
            count = 1

        k = name
        v = [material, triangle, count]
        if drawcall.get(k):
            if material[0] not in drawcall[k][0]:
                drawcall[k][0].append(material[0])
                drawcall[k][0].sort()
            drawcall[k][1] += triangle
            drawcall[k][2] += count
        else:
            drawcall[k] = v

    if line.find('MobileBasePass')>-1 :
        start = 1

    line = f.readline()

data = pd.DataFrame(drawcall)
data = data.T
data.rename(columns={0:'material',1:'triangle',2:'instance'},inplace=True)
xlsx = 'output.xlsx'
excel_path = path + xlsx
# print(excel_path)
writer = pd.ExcelWriter(excel_path)
data.to_excel(writer,sheet_name='drawcall')
writer.save()
print(data)
# print( drawcall )
# for key in drawcall:
#     pd.array(drawcall[key])
# import numpy as np
# import pandas as pd
 
# txt = np.loadtxt('/Users/liuzhongkai/Documents/DOC/ccc.txt')
# txtDF = pd.DataFrame(txt)
# txtDF.to_csv('/Users/liuzhongkai/Documents/DOC/ccc.csv',index=False)
# data = pd.read_table('/Users/liuzhongkai/Documents/DOC/ccc.txt')
# print(type(data))
# print(data.shape[1])