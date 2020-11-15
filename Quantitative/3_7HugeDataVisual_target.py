import pandas as pd
import matplotlib.pyplot as plot

filePath = ("/Users/liuzhongkai/Downloads/Python量化交易实战/code/dataTest.csv")
dataFile = pd.read_csv(filePath,header=None,prefix='V')
target = []
for i in range(0,200) :
    if dataFile.iat[i, 10] >= 7.0 :
        target.append(1.0)
    else:
        target.append(0.0)

ind = [i for i in range(0,200)]

dataRow = dataFile.iloc[0:200, 10]
plot.scatter(ind,dataRow)
plot.xlabel('index')
plot.ylabel('data')
plot.show()