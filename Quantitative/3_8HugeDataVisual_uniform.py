from random import uniform
import pandas as pd
import matplotlib.pyplot as plot

filePath = ("/Users/liuzhongkai/Downloads/Python量化交易实战/code/dataTest.csv")
dataFile = pd.read_csv(filePath, header=None, prefix='V')

target = []
for i in range(0,200) :
    if dataFile.iat[i, 10] >= 7.0 :
        target.append( 1.0 + uniform(-0.3, 0.3))
    else :
        target.append(uniform(-0.3,0.3))

dataRow = dataFile.iloc[0:200,10]
plot.scatter(dataRow,target)
plot.xlabel('dataRow')
plot.ylabel('target')
plot.show()