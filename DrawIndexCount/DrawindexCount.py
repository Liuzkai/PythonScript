""" 
Create by zhongkailiu
date: 2020.08.09

Processing the txt from renderdoc to excel.Count the mesh and the triangle in the scene.
Note: only for the mobile render in the ue4!

处理renderdoc导出的txt文件，统计Mesh的使用数量和总面数。
注意： 只能处理UE4的手机渲染模式下的捕获数据。
"""
import re
import pandas as pd

# the txt path, you must change it to your file path.
path = '/Users/liuzhongkai/Documents/DOC/'
txt = 'ccc.txt'
f = open(path+txt)
line = f.readline()
start = 0
drawcall = {}

# read the txt file
while line:
    # we only processing the "MobileBasePass"
    if line.find('DynamicEd') > -1:
        start = 0
    
    # processing the data
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

# Creating the data frame from dictionary
data = pd.DataFrame(drawcall)
# transform data column and row
data = data.T
data.rename(columns={0:'material',1:'triangle',2:'instance'},inplace=True)
xlsx = 'output.xlsx'
excel_path = path + xlsx
writer = pd.ExcelWriter(excel_path)
data.to_excel(writer,sheet_name='drawcall')
writer.save()
print(data)